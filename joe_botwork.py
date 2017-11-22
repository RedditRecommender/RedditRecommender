#!/usr/bin/python3
import praw
from credentials import reddit

'''
subreddit = reddit.subreddit('ShowerThoughts');

hot_posts = subreddit.hot(limit=15)

for submission in hot_posts:
   if not submission.stickied:
      print(submission.title)
'''
# Waddup nerds here's how to grab some user info
username = 'spez' # set whatever username you want here

myRedditor = reddit.redditor(username) # Create a 'Redditor' object from that username
for comment in myRedditor.comments.new(limit=10): # Get that user's comments
   print(comment.body.split('\n', 1)[0][:79]) # The comment
   print('Subreddit: ', comment.subreddit.display_name) # The subreddit the comment is on

userSubsDict = {}
subList = []

for user in users:
   for comment in user.comments(limit=10):
      subList.append(comment.subreddit.display_name)
   userSubDict[user] = subList

