#!/usr/bin/python3
import praw
from credentials import reddit

#dictionary for map of Users to ID
userMap = {}
#dictionary for map of subreddit to ID
subredditMap = {}

#list of users
userList = []
#finds random subredits then gathers users in said subreddit
for subreddit in range(5):
    sub = (reddit.subreddit('random'))
    for comments in sub.comments(limit = 10):
        if comments.author not in userList:
            userList.append(comments.author)

#dictionary for users and subreddits
userSubsDict = {}
#ID for users and subreddits 
userNumber = 0
subNumber = 0
#finds the redditors subreddits through their comments
for user in userList:
    redditor = str(user)
    numberOfComments = 0
    subList = []
    for comment in reddit.redditor(redditor).comments.new(limit=50):
        subRedditName = str(comment.subreddit.display_name)
        if(subRedditName in subList):
            pass
        else:
            numberOfComments += 1
            subList.append(subRedditName)
            subredditMap[subRedditName] = subNumber
            subNumber += 1
    if numberOfComments > 0:
        userMap[redditor] = userNumber
        userSubsDict[redditor] = subList
        userNumber += 1

file = open("data.txt", "w")
for user,subRedditList in userSubsDict.items():
    for item in subRedditList:
        userID = userMap[user]
        subRedditID = subredditMap[item]
        line = "{} {}".format(userID, subRedditID)
        file.write(line + '\n')

print(userSubsDict)
print(userMap)
print(subredditMap)
file.close();
# redditor = reddit.redditor('TrustMeIKnowThisOne')

# print(dir(redditor))

# for upvoted in reddit.redditor('TrustMeIKnowThisOne').upvoted():
#   print(upvoted)