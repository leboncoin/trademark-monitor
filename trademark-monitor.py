#!/usr/bin/env python3
'''
Trademark Monitor

A tool to monitor specific keywords on social networks about trademarks.

MIT License
Copyright (c) 2021-2022 Leboncoin
Written by Yann Faure (yann.faure@adevinta.com)
'''

import json
import smtplib
import ssl
import configparser
import logging

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from requests import Session
from tweepy import Stream

from classes.database import Database

database = Database('database.db')
database.init_databases()

config = configparser.ConfigParser()
config.read('config.ini')

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger('trademark-monitor')

SESSION = Session()

CONSUMER_KEY=config.get('DEFAULT', 'CONSUMER_KEY')
CONSUMER_SECRET=config.get('DEFAULT', 'CONSUMER_SECRET')
ACCESS_TOKEN=config.get('DEFAULT', 'ACCESS_TOKEN')
ACCESS_TOKEN_SECRET=config.get('DEFAULT', 'ACCESS_TOKEN_SECRET')

TWEETS_ID_LIST = []

SLACK_COLOR_MAPPING = {
    'info': '#b4c2bf',
    'low': '#4287f5',
    'medium': '#f5a742',
    'high': '#b32b2b',
}

def safe_url(text):
    '''Returns a safe unclickable link'''
    return text.replace('http:', 'hxxp:').replace('https:', 'hxxps:')

def slack_alert_twitter(id_tweet, author, content, criticity='high', test_only=False):
    '''Post report on Slack'''
    try:
        payload = dict()
        payload['channel'] = config.get('SLACK', 'CHANNEL')
        payload['link_names'] = 1
        payload['username'] = config.get('SLACK', 'USERNAME')
        payload['icon_emoji'] = config.get('SLACK', 'EMOJI')
        attachments = dict()
        attachments['color'] = SLACK_COLOR_MAPPING[criticity]
        attachments['blocks'] = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{safe_url(content)}"
                    }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "emoji": True,
                            "text": "Tweet Link"
                        },
                        "style": "primary",
                        "url": f'https://twitter.com/{author}/status/{id_tweet}'
                    }
                ]
            }
        ]
        payload['attachments'] = [attachments]
        if test_only:
            LOGGER.warning('[TEST-ONLY] Slack alert.')
            LOGGER.warning(payload)
            return True
        response = SESSION.post(config.get('SLACK', 'WEBHOOK'), data=json.dumps(payload))
        return response
    except Exception as ex:
        LOGGER.debug(ex)

def send_mail(to_email, content):
    '''Send a mail'''
    try:
        message = MIMEMultipart("alternative")
        message["Subject"] = config.get('MAIL', 'SUBJECT_EMAIL')
        message["From"] = config.get('MAIL', 'SMTP_EMAIL')
        message["To"] = to_email

        message.attach(MIMEText(content, "plain"))

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(
                config.get('MAIL', 'SMTP_SERVER'), config.get('MAIL', 'SMTP_PORT'),
                context=context
            ) as server:
            server.login(config.get('MAIL', 'SMTP_EMAIL'), config.get('MAIL', 'SMTP_PASSWORD'))
            server.sendmail(
                config.get('MAIL', 'SMTP_EMAIL'), to_email, message.as_string()
            )
    except Exception as ex:
        LOGGER.debug(ex)

def twitter_send_mail(json_data):
    '''Send mail if enabled in the config file'''
    if config.getboolean('MAIL', 'IS_ENABLED'):
        content = json_data['extended_tweet']['full_text'] if 'extended_tweet' \
                        in json_data else json_data['text']
        verified_or_not = 'YES' if json_data['user']['verified'] else 'NO'
        send_mail(config.get('MAIL', 'DEST_EMAIL'),
            f"FROM: @{json_data['user']['screen_name']}\r\n" \
            f"TEXT: {safe_url(content)}\r\n" \
            f"TWEET DATE: {json_data['created_at']}\r\n" \
            f"LINK: https://twitter.com/{json_data['user']['screen_name']}/status/{json_data['id']}\r\n" \
            f"VERIFIED ACCOUNT: {verified_or_not}\r\n" \
            f"FOLLOWERS: {json_data['user']['followers_count']}")

def twitter_send_slack_notif(json_data):
    '''Send slack notifications if enabled in the config file'''
    if config.getboolean('TWITTER', 'SLACK_NOTIFICATIONS_ENABLED'):
        content = json_data['extended_tweet']['full_text'] if 'extended_tweet' \
                        in json_data else json_data['text']
        verified_or_not = ' :twitter_verified:' if json_data['user']['verified'] else ''
        criticity = 'high' if json_data['user']['verified'] else 'medium'
        slack_alert_twitter(json_data['id'], json_data['user']['screen_name'],
            f"*FROM*: @{json_data['user']['screen_name']}{verified_or_not}\r\n" \
            f"*TEXT*: {content}\r\n" \
            f"*TWEET DATE*: {json_data['created_at']}\r\n" \
            f"*FOLLOWERS*: {json_data['user']['followers_count']}",
            criticity)

def insert_tweet_to_database(json_data):
    '''Insert found tweet in database'''
    content = json_data['extended_tweet']['full_text'] if 'extended_tweet' \
                        in json_data else json_data['text']
    verified_or_not = 1 if json_data['user']['verified'] else 0
    link = f"https://twitter.com/{json_data['user']['screen_name']}/status/{json_data['id']}"
    database.insert_twitter_logs(
        json_data['user']['screen_name'], safe_url(content),
        json_data['created_at'], link, verified_or_not, json_data['user']['followers_count']
    )
    LOGGER.warning(f"============= FROM: @{json_data['user']['screen_name']} =============")
    LOGGER.warning(json_data['text'])
    LOGGER.warning(f"TWEET DATE: {json_data['created_at']}")
    LOGGER.warning(f"LINK: https://twitter.com/{json_data['user']['screen_name']}/status/{json_data['id']}")

class TwitterListener(Stream):
    '''Class listening the data of the Twitter Stream'''
    def on_data(self, data):
        '''Receiving data'''
        obj = json.loads(data)
        if not obj['text'].startswith('RT'):
            if not config.getboolean('STANDALONE', 'IS_ENABLED'):
                keywords = database.get_keywords()
                for keyword in keywords:
                    if keyword[2].lower() in obj['text'].lower() and obj['id'] not in TWEETS_ID_LIST:
                        twitter_send_mail(obj)
                        twitter_send_slack_notif(obj)
                        insert_tweet_to_database(obj)
                        TWEETS_ID_LIST.append(obj['id'])
            else:
                keywords = config.get('STANDALONE', 'KEYWORDS').split()
                for keyword in keywords:
                    if keyword.lower() in obj['text'].lower() and obj['id'] not in TWEETS_ID_LIST:
                        twitter_send_mail(obj)
                        twitter_send_slack_notif(obj)
                        insert_tweet_to_database(obj)
                        TWEETS_ID_LIST.append(obj['id'])
            if len(TWEETS_ID_LIST) > 1000:
                TWEETS_ID_LIST.clear()

def main():
    '''Main, pass the exception if the streamer has failed to start due to network issues'''
    while True:
        trademarks = ''
        if not config.getboolean('STANDALONE', 'IS_ENABLED'):
            for trademark in database.get_trademarks():
                trademarks += f"{trademark[1]}, "
            trademarks = trademarks[:-2]
        else:
            trademarks = config.get('STANDALONE', 'TRADEMARKS')
        LOGGER.warning(f"Twitter stream started with the trademarks: {trademarks} ...")
        try:
            stream = TwitterListener(
                CONSUMER_KEY, CONSUMER_SECRET,
                ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
            stream.filter(track=[trademarks], stall_warnings=True)
        except Exception as ex:
            LOGGER.debug(ex)

if __name__ == '__main__':
    main()
