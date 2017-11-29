#!/usr/bin/python3
import praw
from credentials import reddit

#dictionary for map of Users to ID
userMap = {}

#dictionary for map of subreddit to ID
subredditMap = {}

#ID for users and subreddits to be used in Map dicitonaries
userNumber = 0
subNumber = 0

#list of users
userList = set()

#dictionary for users and subreddits
userSubsDict = {}

#finds the redditors subreddits through their comments
subList = set()

#finds random subredits then gathers users in said subreddit
for subreddit in range(1):
    sub = (reddit.subreddit('random'))
    for comments in sub.comments(limit = 10):
        userList.add(comments.author)

#finds subreddits the users have commented on
for user in userList:
    redditor = str(user)
    #number of comments for specific user
    numberOfComments = 0
    #finds the subreddit each comment resides in
    for comment in reddit.redditor(redditor).comments.new(limit=3):
        subRedditName = str(comment.subreddit.display_name)
        #checks if subreddit is in list or not
        if subRedditName not in subList:
            numberOfComments += 1
            subList.add(subRedditName)
            #assigns subreddit to subredditMap dictionary with ID
            subredditMap[subRedditName] = subNumber
            subNumber += 1
    #adds redditor only if they have comments
    if numberOfComments > 0:
        #assigns user to userMap dictionary with ID
        userMap[redditor] = userNumber
        userSubsDict[redditor] = subList
        userNumber += 1

#writes mapped values to file
file = open("data.txt", "w")
for user,subredditList in userSubsDict.items():
    #loops through subredditList
    for item in subredditList:
        userID = userMap[user]
        subRedditID = subredditMap[item]
        line = "{} {}".format(userID, subRedditID)
        file.write(line + '\n')
file.close();

#writes userMap to file
file = open("userMap.txt", "w")
for user,ID in userMap.items():
    file.write("{} {}\n".format(user, ID))
file.close()

#writes subredditMap to file
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