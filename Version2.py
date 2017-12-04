#!/usr/bin/python3

#Version 2: implementes persistence between runs.  Also trying to use a more
#modular approach to this maddness!

import praw
import argparse
import json
import sys
import subprocess
import random
import re
import traceback #This is used for debugging if an exception is raised
from statistics import mean, median, mode
from random import shuffle
from credentials import reddit

#our argument parser
argumentParser = argparse.ArgumentParser()
args = None

#create a group so they can specify "--new or --existing or --report or --recommend"
actionGroup = argumentParser.add_mutually_exclusive_group(required=True)
actionGroup.add_argument("-n", "--new", action="store_true", help="Search for new users in random subreddits")
actionGroup.add_argument("-e", "--existing", action="store_true", help="Search for more comments for users that we've already found")
actionGroup.add_argument("-r", "--report", action="store_true", help="Display a report at the end of the run showing min, max, avg, etc.")
actionGroup.add_argument("--recommend", metavar="USER", help="Recommend a subreddit to a user")

#we want a flag to determine whether or not we are trying to evaluate our performance
argumentParser.add_argument("--evaluate", action="store_true", help="When recommending a subreddit to a user, this will determine if it was a good recommendation")
argumentParser.add_argument("--tolerance", default=50, type=int, help="When recommending a subreddit to a user, this will determine the tolerance for finding similar users. Defaults to 50")
argumentParser.add_argument("--count", default=10, type=int, help="When recommending a subreddit to a user, this will determine how many will be shown. Defaults to 10")

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

#this is a matcher that will locate the output of the subprocess call
#the output will look like: RECOMMEND 15520 x 1
recommendationMatcher = re.compile(r"RECOMMEND (\d+) x (\d+)")

def main():
    print("*** Main function")

    #see if all we want is a report
    if args.report:
        print_report()
        return None #End of report

    if args.recommend:
        recommend_subreddit()
        return None #End of recommend

    #we will have a list of users here, we will keep track of them before putting them in the global
    #this way, we know they at least have one comment!
    userList = set()

    if args.new:
        verbose_print(1, "Searching for new users...")
        #finds random subredits then gathers users in said subreddit
        for _ in range(NUM_RANDOM_SUBREDDITS):
            subreddit = reddit.subreddit('random')
            for comment in subreddit.comments(limit = NUM_COMMENTS_PER_SUBREDDIT):
                userList.add(str(comment.author))
        
        verbose_print(1, "Found {} random users from {} random subreddits".format(len(userList), NUM_RANDOM_SUBREDDITS))
    elif args.existing:
        if(len(usernameToIdMap) == 0):
            verbose_print(0, "There aren't any existing users.")
            return None

        #shuffle the list of usernames
        potentialUsers = list(usernameToIdMap.keys())
        shuffle(potentialUsers)
        
        verbose_print(1, "Using {} existing users".format(min(NUM_RANDOM_EXISTING_USERS, len(potentialUsers))))
        
        #and fill userList with a slice from the list
        userList = set(potentialUsers[:NUM_RANDOM_EXISTING_USERS])


    #once we have a list of users, we will see which subreddits they have commented on
    for user in userList:
        get_comments_for_user(user)


def get_comments_for_user(user):
    #since we may be modifying these globals, make sure we are using the globals
    global nextUsernameID, nextSubredditID

    #grab some comments for this user
    try:
        comments = list(reddit.redditor(user).comments.new(limit=NUM_COMMENTS_PER_USER))
    except:
        verbose_print(0, "Username '{}' does not exist".format(user))
        return None

    commentsLen = len(comments)

    verbose_print(0, "Found {} comments for user '{}'".format(commentsLen, user))

    for i, comment in enumerate(comments):
        commentUser = str(comment.author)
        if user != commentUser:
            verbose_print(0, "Using username '{}' instead of '{}'".format(commentUser, user))

        subredditName = str(comment.subreddit.display_name)
        verbose_print(2, "Processing comment #{}/{} in subreddit '{}'".format(i+1, commentsLen, subredditName))

        #since this user commented in this subreddit...
        #1) make sure that the user is added to its mapping tool
        if commentUser not in usernameToIdMap:
            verbose_print(1, "New user '{}' recieves id {}".format(commentUser, nextUsernameID))

            usernameToIdMap[commentUser] = nextUsernameID
            nextUsernameID += 1

            #and we will need to create an empty list for them in subredditsForUser
            subredditsForUser[commentUser] = []

        #2) make sure that the subreddit is added to its mapping tool
        if subredditName not in subredditToIdMap:
            verbose_print(1, "New subreddit '{}' recieves id {}".format(subredditName, nextSubredditID))

            subredditToIdMap[subredditName] = nextSubredditID
            nextSubredditID += 1

        #3) make sure that this subreddit is stored within the subredditsForUser
        if subredditName not in subredditsForUser[commentUser]:
            verbose_print(0, "Subreddit '{}' added to user '{}'".format(subredditName, commentUser))
            subredditsForUser[commentUser].append(subredditName)

    #basically, since we got here, that means user existed
    return (commentUser, usernameToIdMap[commentUser])


def print_report():
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


def recommend_subreddit():
    #search for the id of this user
    recommendUsername = args.recommend
    recommendUsernameLower = recommendUsername.lower()
    recommendId = None

    print("Recommending a subreddit to username '{}'".format(recommendUsername))

    #simple case, the username is already in our dict, so we can access directly
    if recommendUsername in subredditsForUser:
        recommendId = usernameToIdMap[recommendUsername]
        print("User '{}' is already in our matrix with the id of {}".format(recommendUsername, recommendId))
    
    #more difficult case, we need to search the keys to find a case insensite match
    if recommendId is None:
        for existingUsername, existingId in usernameToIdMap.items():
            if recommendUsernameLower == existingUsername.lower():
                print("Found matching username '{}' for '{}' with the id of {}".format(existingUsername, recommendUsername, existingId))
                recommendUsername = existingUsername
                recommendUsernameLower = recommendUsername.lower()
                recommendId = existingId
                break

    if recommendId is None:
        print("No existing data for user '{}'".format(recommendUsername))

    #We need to get some comments for this user to make sure we know what they've been up to.
    print("Getting new comments for user '{}'".format(recommendUsername))
    recommendUsername, recommendId = get_comments_for_user(recommendUsername)
    recommendUsernameLower = recommendUsername.lower()

    if recommendId is None:
        #Basically, the user didn't exist
        print("Exiting program")
        return None

    #and then see if we are trying to evaluate
    if args.evaluate:
        #if we are evaluating, we need to 'flip a bit' and then recommend to see if we get the flipped one back
        print("Evaluate: Coming soon to theaters near you!") #TODO: flip the bit!

    #now that we have everything we need, we need to prepare to call the c++ executable
    generate_output_files(verbose=False)

    #call the executable
    print("Running the c++ executable")
    executable = subprocess.run(["./redditRecommender.out", "data.txt", str(recommendId), str(args.tolerance)], stdout=subprocess.PIPE)

    #read output from executable
    result = executable.stdout.decode("utf-8").split("\n")

    #output the recommended subreddit(s) based on the recommended id
    recommendationMatches = [recommendationMatcher.match(line) for line in result if recommendationMatcher.match(line)]
    recommendations = [[int(x) for x in match.group(1, 2)] for match in recommendationMatches]
    
    #shuffle it before sorting so we see more of a variety before runs
    random.shuffle(recommendations)
    recommendations.sort(key=lambda x: x[1], reverse=True)

    allRecommendations = [x[0] for x in recommendations]

    print("Recommendations for '{}':".format(recommendUsername))
    print("{:<16} {:<2}".format("Subreddit", "Confidence"))

    idToSubredditMap = {v: k for k, v in subredditToIdMap.items()}

    for rec in recommendations[:args.count]:
        subredditName = idToSubredditMap[rec[0]]
        print("{:<16} {:<2}".format(subredditName, rec[1]))

    #make sure we 'flip the bit' back if we previously did
    if args.evaluate:
        pass #TODO: flip the bit back


def generate_output_files(verbose=True):
    if verbose: 
        print("*** Generate output files function")

    #generate usernameMap.txt
    if verbose: 
        verbose_print(0, "Writing {} entries to usernameMap.txt".format(len(usernameToIdMap)))
    with open("usernameMap.txt", "w") as file:
        data = sorted(usernameToIdMap.items(), key=lambda x: x[1]) #sort by second elment, the id
        for username, ID in data:
            file.write("{} {}\n".format(username, ID))

    #generate subredditMap.txt
    if verbose: 
        verbose_print(0, "Writing {} entries to subredditMap.txt".format(len(subredditToIdMap)))
    with open("subredditMap.txt", "w") as file:
        data = sorted(subredditToIdMap.items(), key=lambda x: x[1]) #sort by second elment, the id
        for subredditName, ID in data:
            file.write("{} {}\n".format(subredditName, ID))
    
    #generate data.txt
    if verbose: 
        verbose_print(0, "Writing {} entries to data.txt".format(sum(len(x) for x in subredditsForUser.values())))
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

    verbose_print(1, "Successfully loaded globals!")


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

    verbose_print(1, "Successfully saved globals!")


def verbose_print(level, msg):
    if not args.quiet and args.verbose >= level: 
        print(msg)


if __name__ == "__main__":
    global args
    args = argumentParser.parse_args()

    #ensure they are not evaluating anything other than recommend
    if args.evaluate and not args.recommend:
        argumentParser.error("Cannot use flag --evaluate without --recommend")

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