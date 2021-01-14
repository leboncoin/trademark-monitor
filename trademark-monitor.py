#!/usr/bin/env python3
'''
Trademark Monitor

A tool to monitor specific keywords on social networks about trademarks.

MIT License
Copyright (c) 2021 Leboncoin
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
import tweepy
from tweepy import Stream
from tweepy.streaming import StreamListener

config = configparser.ConfigParser()
config.read('config.ini')

logging.basicConfig()
LOGGER = logging.getLogger('trademark-monitor')

SESSION = Session()

CONSUMER_KEY=config['DEFAULT']['CONSUMER_KEY']
CONSUMER_SECRET=config['DEFAULT']['CONSUMER_SECRET']
ACCESS_TOKEN=config['DEFAULT']['ACCESS_TOKEN']
ACCESS_TOKEN_SECRET=config['DEFAULT']['ACCESS_TOKEN_SECRET']

TRADEMARKS = config['DETECTION']['TRADEMARKS']
WORDLIST = config['DETECTION']['WORDLIST']

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
    payload = dict()
    payload['channel'] = config['SLACK']['CHANNEL']
    payload['link_names'] = 1
    payload['username'] = config['SLACK']['USERNAME']
    payload['icon_emoji'] = config['SLACK']['EMOJI']
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
    response = SESSION.post(config['SLACK']['WEBHOOK'], data=json.dumps(payload))
    return response.ok

def send_mail(to_email, content):
    '''Send a mail'''
    message = MIMEMultipart("alternative")
    message["Subject"] = config['MAIL']['SUBJECT_EMAIL']
    message["From"] = config['MAIL']['SMTP_EMAIL']
    message["To"] = to_email

    message.attach(MIMEText(content, "plain"))

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(
            config['MAIL']['SMTP_SERVER'], config['MAIL']['SMTP_PORT'],
            context=context
        ) as server:
        server.login(config['MAIL']['SMTP_EMAIL'], config['MAIL']['SMTP_PASSWORD'])
        server.sendmail(
            config['MAIL']['SMTP_EMAIL'], to_email, message.as_string()
        )

def twitter_send_mail(json_data):
    '''Send mail if enabled in the config file'''
    if config['MAIL']['IS_ENABLED'] == 'True':
        content = json_data['extended_tweet']['full_text'] if 'extended_tweet' in json_data else json_data['text']
        verified_or_not = 'YES' if json_data['user']['verified'] else 'NO'
        send_mail(config['MAIL']['DEST_EMAIL'], f"FROM: @{json_data['user']['screen_name']}\r\n" \
            f"TEXT: {safe_url(content)}\r\n" \
            f"TWEET DATE: {json_data['created_at']}\r\n" \
            f"LINK: https://twitter.com/{json_data['user']['screen_name']}/status/{json_data['id']}\r\n" \
            f"VERIFIED ACCOUNT: {verified_or_not}\r\n" \
            f"FOLLOWERS: {json_data['user']['followers_count']}")

def twitter_send_slack_notif(json_data):
    '''Send slack notifications if enabled in the config file'''
    if config['TWITTER']['SLACK_NOTIFICATIONS_ENABLED'] == 'True':
        content = json_data['extended_tweet']['full_text'] if 'extended_tweet' in json_data else json_data['text']
        verified_or_not = ' :twitter_verified:' if json_data['user']['verified'] else ''
        criticity = 'high' if json_data['user']['verified'] else 'medium'
        slack_alert_twitter(json_data['id'], json_data['user']['screen_name'],
            f"*FROM*: @{json_data['user']['screen_name']}{verified_or_not}\r\n" \
            f"*TEXT*: {content}\r\n" \
            f"*TWEET DATE*: {json_data['created_at']}\r\n" \
            f"*FOLLOWERS*: {json_data['user']['followers_count']}",
            criticity)

class TwitterListener(StreamListener):
    '''Class listening the data of the Twitter Stream'''
    def on_data(self, data):
        '''Receiving data'''
        obj = json.loads(data)
        words = WORDLIST.split()
        if not obj['text'].startswith('RT'):
            for word in words:
                if word in obj['text'] and obj['id'] not in TWEETS_ID_LIST:
                    LOGGER.warning(f"============= FROM: @{obj['user']['screen_name']} =============")
                    LOGGER.warning(obj['text'])
                    LOGGER.warning(f"TWEET DATE: {obj['created_at']}")
                    LOGGER.warning(f"LINK: https://twitter.com/{obj['user']['screen_name']}/status/{obj['id']}")
                    # Alerting
                    twitter_send_mail(obj)
                    twitter_send_slack_notif(obj)

                    TWEETS_ID_LIST.append(obj['id'])
            if len(TWEETS_ID_LIST) > 1000:
                TWEETS_ID_LIST.clear()

def main():
    '''Main, pass the exception if the streamer has failed to start due to network issues'''
    try:
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        while True:
            LOGGER.warning('Twitter stream started...')
            stream = Stream(auth, TwitterListener())
            stream.filter(track=[TRADEMARKS])
    except Exception:
        pass

if __name__ == '__main__':
    main()
