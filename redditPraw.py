#! /usr/local/bin/python3.5
import praw
from credentials import reddit

userList = []
for subreddit in range(3):
    sub = (reddit.subreddit('random'))
    for comments in sub.comments(limit = 1):
        userList.append(comments.author)

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


# redditor = reddit.redditor('TrustMeIKnowThisOne')

# print(dir(redditor))

# for upvoted in reddit.redditor('TrustMeIKnowThisOne').upvoted():
#   print(upvoted)

