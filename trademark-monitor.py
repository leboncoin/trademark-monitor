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

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import tweepy
from tweepy import Stream
from tweepy.streaming import StreamListener

config = configparser.ConfigParser()
config.read('config.ini')

CONSUMER_KEY=config['DEFAULT']['CONSUMER_KEY']
CONSUMER_SECRET=config['DEFAULT']['CONSUMER_SECRET']
ACCESS_TOKEN=config['DEFAULT']['ACCESS_TOKEN']
ACCESS_TOKEN_SECRET=config['DEFAULT']['ACCESS_TOKEN_SECRET']

TRADEMARKS = config['DETECTION']['TRADEMARKS']
WORDLIST = config['DETECTION']['WORDLIST']

TWEETS_ID_LIST = []

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

class TwitterListener(StreamListener):
    '''Class listening the data of the Twitter Stream'''
    def on_data(self, data):
        '''Receiving data'''
        obj = json.loads(data)
        words = WORDLIST.split()
        if not obj['text'].startswith('RT'):
            print(obj['text'])
            for word in words:
                if word in obj['text'] and obj['id'] not in TWEETS_ID_LIST:
                    print('============= FROM: @{} ============='
                            .format(obj['user']['screen_name']))
                    print(obj['text'])
                    print('TWEET DATE: {}'.format(obj['created_at']))
                    print('LINK: https://twitter.com/{}/status/{}'.format(obj['user']['screen_name'], obj['id']))
                    TWEETS_ID_LIST.append(obj['id'])
                    if config['MAIL']['IS_ENABLED']:
                        send_mail(config['MAIL']['DEST_EMAIL'], "FROM: @{}\r\n" \
                            "TEXT: {}\r\n" \
                            "TWEET DATE: {}\r\n" \
                            "LINK: https://twitter.com/{}/status/{}"
                                .format(obj['user']['screen_name'], obj['text'],
                                obj['created_at'], obj['user']['screen_name'], obj['id']))
            if len(TWEETS_ID_LIST) > 1000:
                TWEETS_ID_LIST.clear()

def main():
    '''Main, pass the exception if the streamer has failed to start due to network issues'''
    try:
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

        while True:
            print('Twitter stream started...')
            stream = Stream(auth, TwitterListener())
            stream.filter(track=[TRADEMARKS])
    except Exception:
        pass

if __name__ == '__main__':
    main()
