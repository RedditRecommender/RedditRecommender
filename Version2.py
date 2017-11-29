#!/usr/bin/python3

#Version 2: implementes persistence between runs.  Also trying to use a more
#modular approach to this maddness!

import praw
import json
import sys
import traceback #This is used for debugging if an exception is raised
from credentials import reddit

#Put some globals up top, this way it is easy to configure how much work is to be done at a time
NUM_RANDOM_SUBREDDITS = 3
NUM_COMMENTS_PER_SUBREDDIT = 10
NUM_COMMENTS_PER_USER = 10

#These two dicts will serve as a lookup to go from a string name to a unique id
usernameToIdMap  = {}
subredditToIdMap = {}

#These two fields will serve as the next available id for either category
nextUsernameID  = 0
nextSubredditID = 0

#Here we will store which subreddits each user has a comment in the key will be the username, the value will be a list of subreddits
subredditsForUser = {}

def main():
    print("*** Main function")

    #since we will be modifying these globals, make sure we are using the globals
    global nextUsernameID, nextSubredditID

    #we will have a list of users here, we will keep track of them before putting them in the global
    #this way, we know they at least have one comment!
    userList = set()

    #finds random subredits then gathers users in said subreddit
    for _ in range(NUM_RANDOM_SUBREDDITS):
        subreddit = reddit.subreddit('random')
        for comment in subreddit.comments(limit = NUM_COMMENTS_PER_SUBREDDIT):
            userList.add(str(comment.author))
    
    print("Found {} random users from {} random subreddits".format(len(userList), NUM_RANDOM_SUBREDDITS))

    #once we have a list of users, we will see which subreddits they have commented on
    for user in userList:
        comments = reddit.redditor(user).comments.new(limit=NUM_COMMENTS_PER_USER)
        commentsLen = sum(1 for _ in comments)
        print("Found {} comment{} for user {}".format(commentsLen, "s" if commentsLen != 1 else "", user))

        i = 0
        for comment in comments:
            subredditName = str(comment.subreddit.display_name)
            print("Comment {}/{}: {}".format(i+1, commentsLen, subredditName))

            #since this user commented in this subreddit...
            #1) make sure that the user is added to our mapping tool
            if user not in usernameToIdMap:
                usernameToIdMap[user] = nextUsernameID
                nextUsernameID += 1

                #and we will need to create an empty list for them in subredditsForUser
                subredditsForUser[user] = []

            #2) make sure that the subreddit is added to its mapping tool
            if subredditName not in subredditToIdMap:
                subredditToIdMap[subredditName] = nextSubredditID
                nextSubredditID += 1

            #3) make sure that this subreddit is stored within the subredditsForUser
            if subredditName not in subredditsForUser[user]:
                subredditsForUser[user].append(subredditName)

            #increase our loop counter
            i += 1

def generate_output_files():
    print("*** Generate output files function")

    #generate usernameMap.txt
    print("Writing {} entries to usernameMap.txt".format(len(usernameToIdMap)))
    with open("usernameMap.txt", "w") as file:
        data = sorted(usernameToIdMap.items(), key=lambda x: x[1]) #sort by second elment, the id
        for username, ID in data:
            file.write("{} {}\n".format(username, ID))

    #generate subredditMap.txt
    print("Writing {} entries to subredditMap.txt".format(len(subredditToIdMap)))
    with open("subredditMap.txt", "w") as file:
        data = sorted(subredditToIdMap.items(), key=lambda x: x[1]) #sort by second elment, the id
        for subredditName, ID in data:
            file.write("{} {}\n".format(subredditName, ID))
    
    #generate data.txt
    print("Writing {} entries to data.txt".format(sum(len(x) for x in subredditsForUser.values())))
    with open("data.txt", "w") as file:
        data = sorted(subredditsForUser.items(), key=lambda x: usernameToIdMap[x[0]]) #sort by the id of the username, which is the first element
        for username, subredditList in data:
            for subreddit in sorted(subredditList, key=lambda x: subredditToIdMap[x]): #and then sort by the id of the subreddit
                file.write("{} {}\n".format(usernameToIdMap[username], subredditToIdMap[subreddit]))


def load_globals():
    print("*** Load function")

    #we will be writing to the globals, so make sure we use the global variables
    global subredditsForUser
    global usernameToIdMap, subredditToIdMap
    global nextUsernameID, nextSubredditID

    #read the file as a string
    with open("save_data.txt", "r") as file:
        content = "".join(file.readlines())
    
    #load the json file contents into a dictionary
    save_state = json.loads(content)

    #now use the json to store the dictionaries back into the global variables
    usernameToIdMap = save_state["usernameToIdMap"]
    subredditToIdMap = save_state["subredditToIdMap"]
    subredditsForUser = save_state["subredditsForUser"]
    
    #and calcualte the max ids so we don't have duplicates
    nextUsernameID = max(usernameToIdMap.values() or [-1]) + 1
    nextSubredditID = max(subredditToIdMap.values() or [-1]) + 1

    print("Loaded globals!")


def save_globals():
    print("*** Save function")

    #We really only need to write the dictionarys since we can simply calculate the max ids when loading.
    save_state = {
        "usernameToIdMap": usernameToIdMap,
        "subredditToIdMap": subredditToIdMap,
        "subredditsForUser": subredditsForUser
    }

    #finally dump the json string into the file
    with open("save_data.txt", "w") as file:
        file.write(json.dumps(save_state))

    print("Saved globals!")


if __name__ == "__main__":
    try: 
        load_globals()
    except Exception as e:
        print("ERROR loading globals from file")
        traceback.print_exc(file=sys.stdout)

    print("")

    try: 
        main()
    except Exception as e:
        print("ERROR in main function")
        traceback.print_exc(file=sys.stdout)

    print("")

    try: 
        generate_output_files()
    except Exception as e:
        print("ERROR generating output files")
        traceback.print_exc(file=sys.stdout)

    print("")

    try: 
        save_globals()
    except Exception as e:
        print("ERROR saving globals to file")
        traceback.print_exc(file=sys.stdout)
    
    
    

