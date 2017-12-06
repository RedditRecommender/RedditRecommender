//To compile: g++ -O3 -w redditRecommender.cpp -o redditRecommender.out
//To run: ./redditRecommender.out <filename>

#include <stdio.h>
#include <stdlib.h>
#include <cstdlib> // atoi
#include <utility> // std::pair
#include <algorithm> // std::stable_sort
#include <vector>
#include <map>
#include <iostream>
#include <fstream>

using namespace std;

//constants
#define MAX_COLS_TO_PRINT 16
#define MAX_ROWS_TO_PRINT 16

//global variables
int* globalMatrix = NULL; //1 dimensional.  Access index with [convertUserSubToIndex(userID, subID)]
int* userTotal = NULL;
int* subTotal = NULL;
int grandTotal = 0;

int numberOfUsers;
int numberOfSubs;

long thread_count = 4; 

int recommendId = -1;

//entire matrix recommendation
map<int, map< int, int > > entireMatrixRecommendation; 

//method headers
int main(int argc, char* argv[]);
float sim(int x, int y);
int convertUserSubToIndex(int x, int y);
bool similarPairCompare(pair<int, float> i, pair<int, float> j);
void printGlobalMatrix();
void* fullMatrixRecommend(void* thread_id);

int main(int argc, char* argv[])
{
	if(argc < 2)
	{
		printf("Usage: ./redditThread.out fileName [recommendId] \n");
		exit(-1);
	}
    //validate command line args 
    char* fileName = argv[1];
    
    // if you wish to recommend to single user
    if(argc > 2)
    {       
	    //read command line args
	    recommendId = atoi(argv[2]);
	}
	
    //keep track of the largest ids that we've seen in the file
    int maxUserID = -1;
    int maxSubID = -1;

    //and keep track of the current row we're on
    int userID;
    int subID;

    //create a vector of pairs that we've read so we don't need to re-read the file
    vector<pair<int, int> > allPairs;

    //open and read the file
    printf("Reading the file: %s\n", fileName);
    fstream dataFile(fileName, ios_base::in);

    while(dataFile >> userID >> subID)
    {
        //see if either value exceeds the largest we've seen yet
        if(userID > maxUserID)
        {
            maxUserID = userID;
        }
        if(subID > maxSubID)
        {
            maxSubID = subID;
        }

        //make a pair for this line and append it to allPairs
        pair<int, int> currentPair = make_pair(userID, subID);
        allPairs.push_back(currentPair);
    }

    // if you wish to recommend a single to a single user
    if(recommendId > -1)
    {
	    //validate our recommendId is in our matrix
	    if(recommendId > maxUserID)
	    {
	        printf("Could not recommend a subreddit for userId %d since the file only has %d usernames.\n", recommendId, maxUserID + 1);
	        exit(-1);
	    }
	    if(recommendId < 0)
	    {
	        printf("ID cannot be negative\n");
	        exit(-1);
	    }
	}

    //once we are done reading the file, we need to fill in our global matrix
    //start by writing the global numbers of users/subs
    numberOfUsers = maxUserID + 1;
    numberOfSubs = maxSubID + 1;

    //then we need to allocate the memory for the matrix (1 dimensional)
    globalMatrix = (int*) calloc(numberOfUsers * numberOfSubs, sizeof(int));
    userTotal = (int*) calloc(numberOfUsers, sizeof(int));
    subTotal = (int*) calloc(numberOfSubs, sizeof(int));

    printf("File has %d usernames and %d subreddits.\n", numberOfUsers, numberOfSubs);
    printf("Allocated %d cells\n", numberOfUsers * numberOfSubs);

    //we will iterate through all of the pairs and populate our matrix
    for(vector<pair<int, int> >::iterator it = allPairs.begin(); it != allPairs.end(); it++){
        pair<int, int> thisPair = *it;
        userID = thisPair.first;
        subID = thisPair.second;

        globalMatrix[convertUserSubToIndex(userID, subID)] = 1;
        userTotal[userID] += 1;
        subTotal[subID] += 1;
        grandTotal += 1;
    }

    //now we have our global matrix, so print it
    printGlobalMatrix();

    //call recommend function for single specified user
    if(recommendId > -1)
    {
    //start the recommendation process
    	printf("Recommending a subreddit to user #%d\n", recommendId);
    	fullMatrixRecommend(0);
    }

    // if the user does not set recommendId run the entire data.txt through recommend funciton
    if(recommendId == -1)
    {
	    //create threads
	    long thread;
	    pthread_t* thread_handles;
	    thread_handles = (pthread_t*) malloc (thread_count * sizeof(pthread_t));

	    for(thread = 0; thread < thread_count; thread++)
	    {
	    	pthread_create(&thread_handles[thread], NULL, fullMatrixRecommend, (void*) thread);
	    }

	    //joining of threads
	    for(thread = 0; thread < thread_count; thread++)
	    {
	    	pthread_join(thread_handles[thread], NULL);
	    }
    }

    for(map<int,map<int,int> >::iterator it1 = entireMatrixRecommendation.begin(); it1 != entireMatrixRecommendation.end(); it1++)
    {
    	int userID = (*it1).first;
    	map<int, int> recommendations = (*it1).second;

    	for(map<int, int>::iterator it2 = recommendations.begin(); it2 != recommendations.end(); it2++)
    	{
    		int subreddit = (*it2).first;
    		int confidence = (*it2).second;

    		if(recommendId > -1)
			{
				printf("RECOMMEND %d x %d\n", subreddit, confidence);
			}
			else
			{
				printf("User ID: %d is recommended subreddit: %d with confidence: %d \n", userID, subreddit, confidence);
			}
    	}
    }
}

void* fullMatrixRecommend(void* thread_id)
{
	long rank = (long) thread_id;

    // creates start and end points for each thread
	int start = rank * (numberOfUsers / thread_count) + min(rank, numberOfUsers % thread_count);
	int end = start + (numberOfUsers / thread_count) + (rank < (numberOfUsers % thread_count));

	// if there the args specify recommending for one user only itterate once
	if(recommendId > -1)
	{
		start = recommendId;
		end = recommendId + 1;
	}

	printf("Thread: %d, Start: %d, End: %d\n", rank, start, end);

	// iterates over every user
	for(int user=start; user<end; user++)
	{
		vector<pair<int,float> > similarityVector;
		// iterates over every other user to dicscern similarity 
		for(int other=0; other<numberOfUsers; other++)
		{
			if(user == other)
			{
				continue;
			}

		    //otherwise calculate similarity and add to vector  
			float similarity = sim(user, other);
			similarityVector.push_back(make_pair(other, similarity));
		}
		
		// sorts vector
		stable_sort(similarityVector.begin(), similarityVector.end(),similarPairCompare);

		// keep track of candidate recommendations
		map<int, int> recommendations;
		float lastSimilarity = 0; 
   
	    //we will need to traverse this vector to find our candidates
	    for(vector<pair<int, float> >::iterator it=similarityVector.begin(); it != similarityVector.end(); it++)
	    {
	        pair<int, float> p = *it;
	        int otherId = p.first;
	        float otherSimilarity = p.second;

	        // see if we are no longer on the same level of similarity
	        // if we are on the same level, we should not break out yet.
	        if(lastSimilarity - otherSimilarity > .0001f)
	        {
	            //we should only break out if we actually have some recommendations
	            if(recommendations.size() > 0)
	            {
	                break;
	            }
	        }

	        //we need to find the subs in otherId's row that arent in the user's row
	        for(int i=0; i<numberOfSubs; i++)
	        {
	            if(globalMatrix[convertUserSubToIndex(otherId, i)] == 1 && globalMatrix[convertUserSubToIndex(user, i)] != 1)
	            {
	                recommendations[i] += 1;
	            }
	        }
	        // printf("finished the recommendations for user %i \n", user);

	        //finally, update our last similarity
	        lastSimilarity = otherSimilarity;
	    }


	    entireMatrixRecommendation[user] = recommendations;

	    //add the recommened users to global map
		// for(map<int, int>::iterator it=recommendations.begin(); it!=recommendations.end(); it++)
	 //    {
	 //        int key = it->first;
	 //        int value = it->second;


	 //        entireMatrixRecommendation[user][key] = value;
	 //    }
	}

	printf("Thread %d Finished.\n", rank);
}

float sim(int x, int y)
{
    //this method uses Jaccard Similarity: sim(x, y) => |intersection(x, y)| / |union(x, y)|

    //validate x and y are in bounds
    if(x < 0 || x >= numberOfUsers || y < 0 || y >= numberOfUsers)
    {
        printf("ERROR: sim(x, y) has out of bounds param: x=%d, y=%d\n", x, y);
        exit(-1);
    }

    int unionSize = 0;
    int intersectionSize = 0;

    //iterate every subreddit
    for(int i=0; i<numberOfSubs; i++)
    {
        //union
        if(globalMatrix[convertUserSubToIndex(x, i)] == 1 || globalMatrix[convertUserSubToIndex(y, i)] == 1)
        {
            unionSize += 1;
        }

        //intersection
        if(globalMatrix[convertUserSubToIndex(x, i)] == 1 && globalMatrix[convertUserSubToIndex(y, i)] == 1)
        {
            intersectionSize += 1;
        }
    }

    //because we are dividing by |union(x, y)|, make sure we don't divide by 0
    if(unionSize == 0)
    {
        return 0;
    }

    return (float) intersectionSize / unionSize;
}

int convertUserSubToIndex(int userID, int subredditID)
{
    return numberOfSubs * userID + subredditID;
}

bool similarPairCompare(pair<int, float> i, pair<int, float> j)
{
    //sort in descending order.
    return i.second > j.second;
}

void printGlobalMatrix()
{
    printf("Graph: (%d users) x (%d subreddits):\n", numberOfUsers, numberOfSubs);

    int columnWidth = 6;
    //print spacing before top row
    printf("%*s|", columnWidth, "");

    //print top row ids
    for(int x=0;x<numberOfSubs;x++)
    {
        printf("%*d|", columnWidth, x);
        if(x == MAX_COLS_TO_PRINT)
        {
            printf("%*s|", columnWidth, ".. ");
            break;
        }
    }
    printf("%*s|", columnWidth, "TOT");
    printf("\n");

    //print table
    for(int y=0;y<numberOfUsers;y++)
    {
        //print ids of this row
        printf("%*d|", columnWidth, y);
        
        //and print the rest of this row
        for(int x=0;x<numberOfSubs;x++)
        {
            printf("%*d|", columnWidth, globalMatrix[convertUserSubToIndex(y, x)]);
            if(x == MAX_COLS_TO_PRINT)
            {
                printf("%*s|", columnWidth, ".. ");
                break;
            }
        }

        printf("%*d|", columnWidth, userTotal[y]);
        printf("\n");

        if(y == MAX_ROWS_TO_PRINT)
        {
            printf("%*s|", columnWidth, ". ");
            for(int x=0;x<numberOfSubs;x++)
            {
                printf("%*s|", columnWidth, ". ");
                if(x == MAX_COLS_TO_PRINT)
                {
                    printf("%*s|", columnWidth, ".. ");
                    printf("%*s|", columnWidth, ". ");
                    break;
                }
            }
            printf("\n");
            break;
        }
    }

    printf("%*s|", columnWidth, "TOT");
    for(int x=0;x<numberOfSubs;x++)
    {
        printf("%*d|", columnWidth, subTotal[x]);
        if(x == MAX_COLS_TO_PRINT)
        {
            printf("%*s|", columnWidth, ".. ");
            break;
        }
    }
    printf("%*d|", columnWidth, grandTotal);

    printf("\n\n");
}