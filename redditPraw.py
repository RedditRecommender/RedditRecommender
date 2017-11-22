#!/usr/bin/python3
import praw
from credentials import reddit

subreddit = reddit.subreddit('ShowerThoughts');

hot_posts = subreddit.hot(limit=15)

for i, submission in enumerate(hot_posts):
	#stuff
   print(submission.title, i) #test
#   if i == post_number:
#      print(submission.url)

#for submission in hot_python:
#   if not submission.stickied:
#      print(submission.title)


#sast#sast
for submission in hot_posts:
   if not submission.stickied:
