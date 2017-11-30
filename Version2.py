#!/usr/bin/python3

#Version 2: implementes persistence between runs.  Also trying to use a more
#modular approach to this maddness!

import praw
import argparse
import json
import sys
import traceback #This is used for debugging if an exception is raised
from statistics import mean, median, mode
from random import shuffle
from credentials import reddit

#our argument parser
argumentParser = argparse.ArgumentParser()

#create a group so they can specify "--new or --existing"
actionGroup = argumentParser.add_mutually_exclusive_group(required=True)
actionGroup.add_argument("-n", "--new", action="store_true", help="Search for new users in random subreddits")
actionGroup.add_argument("-e", "--existing", action="store_true", help="Search for more comments for users that we've already found")

#an option to specify a report
argumentParser.add_argument("-r", "--report", action="store_true", help="Display a report at the end of the run showing min, max, avg, etc.")

#create a group so they can specify "--verbose or --quiet"
verboseQuietGroup = argumentParser.add_mutually_exclusive_group()
verboseQuietGroup.add_argument("-v", "--verbose", action="count", default=0, help="Specify how verbose the program is")
verboseQuietGroup.add_argument("-q", "--quiet", action="store_true", help="Don't show any progress within the methods")

#Put some globals up top, this way it is easy to configure how much work is to be done at a time
NUM_RANDOM_SUBREDDITS = 3       #this is used to find random users
NUM_COMMENTS_PER_SUBREDDIT = 10 #this is how many random users to find
NUM_RANDOM_EXISTING_USERS = 100 #this is how many existing users to use
NUM_COMMENTS_PER_USER = 250     #this is how many comments to look at per user

#These two dicts will serve as a lookup to go from a string name to a unique id
usernameToIdMap  = {}
subredditToIdMap = {}

#These two fields will serve as the next available id for either category
nextUsernameID  = 0
nextSubredditID = 0

#Here we will store which subreddits each user has a comment in the key will be the username, the value will be a list of subreddits
subredditsForUser = {}

def main(args):
    print("*** Main function")

    #since we will be modifying these globals, make sure we are using the globals
    global nextUsernameID, nextSubredditID

    #we will have a list of users here, we will keep track of them before putting them in the global
    #this way, we know they at least have one comment!
    userList = set()

    if args.new:
        verbose_print(1, args, "Searching for new users...")
        #finds random subredits then gathers users in said subreddit
        for _ in range(NUM_RANDOM_SUBREDDITS):
            subreddit = reddit.subreddit('random')
            for comment in subreddit.comments(limit = NUM_COMMENTS_PER_SUBREDDIT):
                userList.add(str(comment.author))
        
        verbose_print(0, args, "Found {} random users from {} random subreddits".format(len(userList), NUM_RANDOM_SUBREDDITS))
    elif args.existing:
        #shuffle the list of usernames
        potentialUsers = list(usernameToIdMap.keys())
        shuffle(potentialUsers)
        
        verbose_print(0, args, "Using {} existing users".format(min(NUM_RANDOM_EXISTING_USERS, len(potentialUsers))))
        
        #and fill userList with a slice from the list
        userList = set(potentialUsers[:min(NUM_RANDOM_EXISTING_USERS, len(potentialUsers))])


    #once we have a list of users, we will see which subreddits they have commented on
    for user in userList:
        comments = list(reddit.redditor(user).comments.new(limit=NUM_COMMENTS_PER_USER))
        commentsLen = len(comments)
        
        verbose_print(0, args, "Found {} comments for user '{}'".format(commentsLen, user))

        for i, comment in enumerate(comments):
            subredditName = str(comment.subreddit.display_name)
            verbose_print(1, args, "Processing comment #{}/{} in subreddit '{}'".format(i+1, commentsLen, subredditName))

            #since this user commented in this subreddit...
            #1) make sure that the user is added to our mapping tool
            if user not in usernameToIdMap:
                verbose_print(0, args, "New user '{}' recieves id {}".format(user, nextUsernameID))

                usernameToIdMap[user] = nextUsernameID
                nextUsernameID += 1

                #and we will need to create an empty list for them in subredditsForUser
                subredditsForUser[user] = []

            #2) make sure that the subreddit is added to its mapping tool
            if subredditName not in subredditToIdMap:
                verbose_print(0, args, "New subreddit '{}' recieves id {}".format(subredditName, nextSubredditID))

                subredditToIdMap[subredditName] = nextSubredditID
                nextSubredditID += 1

            #3) make sure that this subreddit is stored within the subredditsForUser
            if subredditName not in subredditsForUser[user]:
                verbose_print(0, args, "Subreddit '{}' added to user '{}'".format(subredditName, user))
                subredditsForUser[user].append(subredditName)


def generate_output_files(args):
    print("*** Generate output files function")

    #generate usernameMap.txt
    verbose_print(0, args, "Writing {} entries to usernameMap.txt".format(len(usernameToIdMap)))
    with open("usernameMap.txt", "w") as file:
        data = sorted(usernameToIdMap.items(), key=lambda x: x[1]) #sort by second elment, the id
        for username, ID in data:
            file.write("{} {}\n".format(username, ID))

    #generate subredditMap.txt
    verbose_print(0, args, "Writing {} entries to subredditMap.txt".format(len(subredditToIdMap)))
    with open("subredditMap.txt", "w") as file:
        data = sorted(subredditToIdMap.items(), key=lambda x: x[1]) #sort by second elment, the id
        for subredditName, ID in data:
            file.write("{} {}\n".format(subredditName, ID))
    
    #generate data.txt
    verbose_print(0, args, "Writing {} entries to data.txt".format(sum(len(x) for x in subredditsForUser.values())))
    with open("data.txt", "w") as file:
        data = sorted(subredditsForUser.items(), key=lambda x: usernameToIdMap[x[0]]) #sort by the id of the username, which is the first element
        for username, subredditList in data:
            for subreddit in sorted(subredditList, key=lambda x: subredditToIdMap[x]): #and then sort by the id of the subreddit
                file.write("{} {}\n".format(usernameToIdMap[username], subredditToIdMap[subreddit]))

    if args.report:
        print("Generating report")
        subredditCountPerUser = [len(subs) for subs in subredditsForUser.values()]
        userCountPerSubreddit = [sum(1 if sub in subredditsForUser[user] else 0 for user in usernameToIdMap.keys()) for sub in subredditToIdMap.keys()]

        print("Statistics:")
        print("  Subreddit count per user:")
        print("    min: {}".format(min(subredditCountPerUser)))
        print("    max: {}".format(max(subredditCountPerUser)))
        print("    mean: {}".format(mean(subredditCountPerUser)))
        print("    median: {}".format(median(subredditCountPerUser)))
        print("    mode: {}".format(mode(subredditCountPerUser)))
        print("    sum: {}".format(sum(subredditCountPerUser)))

        print("  User count per subreddit:")
        print("    min: {}".format(min(userCountPerSubreddit)))
        print("    max: {}".format(max(userCountPerSubreddit)))
        print("    mean: {}".format(mean(userCountPerSubreddit)))
        print("    median: {}".format(median(userCountPerSubreddit)))
        print("    mode: {}".format(mode(userCountPerSubreddit)))
        print("    sum: {}".format(sum(userCountPerSubreddit)))



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

    verbose_print(1, args, "Successfully loaded globals!")


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

    verbose_print(1, args, "Successfully saved globals!")


def verbose_print(level, args, msg):
    if not args.quiet and args.verbose >= level: 
        print(msg)


if __name__ == "__main__":
    args = argumentParser.parse_args()

    try: 
        load_globals()
    except Exception as e:
        print("ERROR loading globals from file")
        traceback.print_exc(file=sys.stdout)

    print("")

    try: 
        main(args)
    except Exception as e:
        print("ERROR in main function")
        traceback.print_exc(file=sys.stdout)

    print("")

    try: 
        generate_output_files(args)
    except Exception as e:
        print("ERROR generating output files")
        traceback.print_exc(file=sys.stdout)

    print("")

    try: 
        save_globals()
    except Exception as e:
        print("ERROR saving globals to file")
        traceback.print_exc(file=sys.stdout)
    
    
    

