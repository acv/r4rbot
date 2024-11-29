import os
import praw
import time
import datetime
import requests
import json
import pytz
from dotenv import load_dotenv

load_dotenv()

reddit = praw.Reddit(
    client_id=os.getenv("CLIENT"),
    client_secret=os.getenv("SECRET"),
    user_agent="r/r4rmontreal bot by /u/gahmatar",
)

webhook = os.getenv("WEBHOOK")
most_recent_time = None
most_recent_seen = None

while True:
    opts = {}
    if most_recent_seen is not None:
        opts['before'] = most_recent_seen
    submissions = list(reddit.subreddit("r4rmontreal").new(limit=5, params=opts))
    submissions.reverse()
    for submission in submissions:
        name = submission.name
        text = submission.selftext
        title = submission.title
        url = submission.url
        author = submission.author
        author_icon = author.icon_img
        author_name = author.name
        author_flair = submission.author_flair_text
        if author_flair is not None:
            author_name = f"{author_name} ({author_flair})"

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
        print(json.dumps(message))
        requests.post(webhook, json=message)

        post_time = datetime.datetime.fromtimestamp(timestamp=submission.created_utc, tz=pytz.utc)

        if most_recent_seen is None:
            most_recent_seen = name
            most_recent_time = post_time
        else:
            if post_time > most_recent_time:
                most_recent_seen = name
                most_recent_time = post_time


    time.sleep(300)
