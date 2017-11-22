#!/usr/bin/python3
import praw
from credentials import reddit

subreddit = reddit.subreddit('ShowerThoughts');

hot_posts = subreddit.hot(limit=15)

for submission in hot_posts:
   if not submission.stickied:
      print(submission.title)
