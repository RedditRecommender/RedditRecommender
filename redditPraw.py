#!/usr/bin/python3
import praw
from credentials import reddit

<<<<<<< HEAD
userList = []
for subreddit in range(3):
    sub = (reddit.subreddit('random'))
    for comments in sub.comments(limit = 1):
        userList.append(comments.author)
=======
'''
subreddit = reddit.subreddit('ShowerThoughts');
>>>>>>> 4578a12b266a356f031f61d9404211a62512eacf

userSubsDict = {}
for user in userList:
    redditor = str(user)
    subList = {}
    for comment in reddit.redditor(redditor).comments.new(limit=5):
        subRedditName = str(comment.subreddit.display_name)
        if(subRedditName in subList):
            pass
        else:
            subList[subRedditName] = 0
    userSubsDict[user] = subList

<<<<<<< HEAD



# redditor = reddit.redditor('TrustMeIKnowThisOne')

# print(dir(redditor))

# for upvoted in reddit.redditor('TrustMeIKnowThisOne').upvoted():
#   print(upvoted)
=======
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
>>>>>>> 4578a12b266a356f031f61d9404211a62512eacf
