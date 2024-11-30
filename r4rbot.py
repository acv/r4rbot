import os
import praw
import time
import requests
import json
from dotenv import load_dotenv

load_dotenv()

reddit = praw.Reddit(
    client_id=os.getenv("CLIENT"),
    client_secret=os.getenv("SECRET"),
    user_agent="r/r4rmontreal bot by /u/gahmatar",
)

webhook = os.getenv("WEBHOOK")
seen_ads = set()

while True:
    submissions = list(reddit.subreddit("r4rmontreal").new(limit=25))
    submissions.reverse()
    ads_this_turn = set()
    print(f"Got {len(submissions)} comments in the listing")
    for submission in submissions:       
        print(submission.__dict__)
        name = submission.name
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

        if name not in seen_ads:
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
        ads_this_turn.add(name)

    seen_ads = ads_this_turn
    time.sleep(150)