#!/usr/bin/python3
import praw
from credentials import reddit

#ID for users and subreddits to be used in Map dicitonaries
userIDCounter = 0
subredditIDCounter = 0

#dictionary for map of Users to ID
userMap = {}

#dictionary for map of subreddit to ID
subredditMap = {}

#dictionary for users and subreddits
userSubsDict = {}

#list of users
userList = set()

#list of subreddits that have commented on
subredditListMaster = set()

#finds random subredits then gathers users in said subreddit
for subreddit in range(2):
    sub = (reddit.subreddit('random'))
    for comments in sub.comments(limit = 5):
        userList.add(comments.author)

#finds subreddits the users have commented on
for user in userList:
    redditor = str(user)
    #list of subreddits specific to user
    subredditRedditorList = set()
    #number of comments for specific user
    numberOfComments = 0
    #finds the subreddit each comment resides in
    for comment in reddit.redditor(redditor).comments.new(limit=4):
        subredditName = str(comment.subreddit.display_name)
        #checks if subreddit is in Master list or not
        if subredditName not in subredditListMaster:
            numberOfComments += 1
            subredditListMaster.add(subredditName)
            #assigns subreddit to subredditMap dictionary with ID
            subredditMap[subredditName] = subredditIDCounter
            subredditIDCounter += 1
        #checks if subreddit is in user specific list or not
        if subredditName not in subredditRedditorList:
            subredditRedditorList.add(subredditName)
    #adds redditor only if they have comments
    if numberOfComments > 0:
        #assigns user to userMap dictionary with ID
        userMap[redditor] = userIDCounter
        userSubsDict[redditor] = subredditRedditorList
        userIDCounter += 1

#writes mapped values to file
file = open("data.txt", "w")
for user,subredditList in userSubsDict.items():
    #loops through subredditList
    for item in subredditList:
        userID = userMap[user]
        subredditID = subredditMap[item]
        line = "{} {}".format(userID, subredditID)
        file.write(line + '\n')
file.close();

#writes userMap to file
file = open("userMap.txt", "w")
for user,ID in userMap.items():
    file.write("{} {}\n".format(user, ID))
file.close()

#writes subredditMap to file
file = open("subredditMap.txt", "w")
for subreddit,ID in subredditMap.items():
    file.write("{} {}\n".format(subreddit, ID))
file.close()

print(userSubsDict)
print(userMap)
print(subredditMap)

# redditor = reddit.redditor('TrustMeIKnowThisOne')

# print(dir(redditor))

# for upvoted in reddit.redditor('TrustMeIKnowThisOne').upvoted():
#   print(upvoted)