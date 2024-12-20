#!/usr/bin/env python3
import os
import praw
import time
import requests
import json
import datetime
import logging

from logging.handlers import TimedRotatingFileHandler
from dotenv import load_dotenv

log_handler = TimedRotatingFileHandler('r4rbot.log', encoding="utf8", when="d", interval=7, backupCount=4)
log_handler.setFormatter(logging.Formatter('[%(asctime)s][%(name)s][%(levelname)s] %(message)s'))

logger = logging.getLogger()
logger.addHandler(log_handler)
logger.setLevel(logging.DEBUG)
logger.info("Application Started")

load_dotenv()

reddit = praw.Reddit(
    client_id=os.getenv("CLIENT"),
    client_secret=os.getenv("SECRET"),
    user_agent="r/r4rmontreal bot by /u/gahmatar",
)

TODAY_FILE = "r4rbot.today"

webhook = os.getenv("WEBHOOK")
# We maintain a lookback that is at least 24h long
yesterday_ads = set()
today = datetime.date.today()

if os.path.exists(TODAY_FILE):
    with open(TODAY_FILE, "r") as in_fp:
        today_ads = set(json.load(in_fp))
else:
    today_ads = set()

while True:
    seen_ads = today_ads | yesterday_ads
    submissions = list(reddit.subreddit("r4rmontreal").new(limit=25))
    submissions.reverse()
    ads_this_turn = set()
    logger.info(f"Got {len(submissions)} comments in the listing")
    for submission in submissions:       
        logger.debug(submission.__dict__)
        name = submission.name

        if name not in seen_ads:
            text = submission.selftext
            title = submission.title
            url = submission.url
            author = submission.author
            author_icon = 'https://www.redditstatic.com/shreddit/assets/snoovatar-back-64x64px.png'
            author_name = '[deleted?]'
            try:
                author_icon = author.icon_img
                author_name = author.name
                author_flair = submission.author_flair_text
                if author_flair is not None:
                    author_name = f"{author_name} ({author_flair})"
            except AttributeError:
                pass

            message = {
                'embeds': [
                    {
                        'author': {
                            'name': author_name,
                            'icon_url': author_icon,
                        },
                        'title': title,
                        'url': url,
                        'description': text,
                    }
                ]
            }
            logger.info(json.dumps(message))
            requests.post(webhook, json=message)
        ads_this_turn.add(name)

    if datetime.date.today() > today:
        yesterday_ads = today_ads
        today_ads = set()
        today = datetime.date.today()
    
    today_ads |= ads_this_turn
    with open(TODAY_FILE, "w") as out_fp:
        json.dump(list(today_ads), out_fp)
    time.sleep(150)