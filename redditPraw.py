#! /usr/local/bin/python3.5
import praw
import random
from credentials import reddit

subreddit = reddit.subreddit('ShowerThoughts');

hot_posts = subreddit.hot(limit=15)
post_number = random.randint(0, 14)

for i, submission in enumerate(hot_posts):
   print(submission.title, i)
#   if i == post_number:
#      print(submission.url)

#for submission in hot_python:
#   if not submission.stickied:
#      print(submission.title)
