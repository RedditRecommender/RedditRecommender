#!/usr/bin/python3
import praw
from credentials import reddit

#dictionary for map of Users to ID
userMap = {}
#dictionary for map of subreddit to ID
subredditMap = {}
#ID for users and subreddits 
userNumber = 0
subNumber = 0

#list of users
userList = set()
#finds random subredits then gathers users in said subreddit
for subreddit in range(1):
    sub = (reddit.subreddit('random'))
    for comments in sub.comments(limit = 10):
        userList.add(comments.author)

#dictionary for users and subreddits
userSubsDict = {}

#finds the redditors subreddits through their comments
subList = set()
for user in userList:
    redditor = str(user)
    numberOfComments = 0
    for comment in reddit.redditor(redditor).comments.new(limit=3):
        subRedditName = str(comment.subreddit.display_name)
        if subRedditName not in subList:
            numberOfComments += 1
            subList.add(subRedditName)
            subredditMap[subRedditName] = subNumber
            subNumber += 1
    #adds redditor only if they have comments
    if numberOfComments > 0:
        userMap[redditor] = userNumber
        userSubsDict[redditor] = subList
        userNumber += 1

#opens a file and adds mapped values
file = open("data.txt", "w")
for user,subRedditList in userSubsDict.items():
    for item in subRedditList:
        userID = userMap[user]
        subRedditID = subredditMap[item]
        line = "{} {}".format(userID, subRedditID)
        file.write(line + '\n')
file.close();

file = open("userMap.txt", "w")
for user,ID in userMap.items():
    file.write("{} {}\n".format(user, ID))
file.close()

file = open("subRedditMap.txt", "w")
for subReddit,ID in subredditMap.items():
    file.write("{} {}\n".format(subReddit, ID))
file.close()



print(userSubsDict)
print(userMap)
print(subredditMap)

# redditor = reddit.redditor('TrustMeIKnowThisOne')

# print(dir(redditor))

# for upvoted in reddit.redditor('TrustMeIKnowThisOne').upvoted():
#   print(upvoted)