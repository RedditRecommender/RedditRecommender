//To compile: g++ -O3 -w redditRecommender.cpp -o redditRecommender.out
//To run: ./redditRecommender.out <filename>

#include <stdio.h>
#include <stdlib.h>
#include <cstdlib> // atoi
#include <utility> // std::pair
#include <algorithm> // std::stable_sort
#include <vector>
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

int recommendId = -1;

//method headers
int main(int argc, char* argv[]);
void* recommend(void* rank);
float sim(int x, int y);
int convertUserSubToIndex(int x, int y);
bool similarPairCompare(pair<int, float> i, pair<int, float> j);
void printGlobalMatrix();

int main(int argc, char* argv[])
{
    //validate command line args
    if(argc < 3)
    {
        printf("Usage: ./redditRecommender.out <filename> <usernameID>\n");
        exit(-1);
    }
    //read command line args
    char* fileName = argv[1];
    recommendId = atoi(argv[2]);

    //keep track of the largest ids that we've seen in the file
    int maxUserID = -1;
    int maxSubID = -1;

    //and keep track of the current row we're on
    int userID;
    int subID;

    //create a list of pairs that we've read so we don't need to re-read the file
    vector<pair<int, int> > allPairs;

    //open and read the file
    printf("\nReading the file: %s\n", fileName);
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

    //validate our recommendId is in our matrix
    if(recommendId > maxUserID)
    {
        printf("Could not recommend a subreddit for userId %d since the file only has %d usernames.\n", recommendId, maxUserID + 1);
        exit(-1);
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

    //start the recommendation process
    printf("Recommending a subreddit to user #%d\n", recommendId);
    recommend(0);
}

void* recommend(void* rank)
{
    long id = (long) rank;
    printf("Thread started with id of %d\n", id);

    //this vector will be a container of (id, similarity) that we can sort
    vector<pair<int, float> > similarityVector;

    for(int other=0; other<numberOfUsers; other++)
    {
        //make sure we ignore similarity to ourselves
        if(other == recommendId)
        {
            continue;
        }

        //otherwise calculate similarity and add it to our list
        float similarity = sim(recommendId, other);
        similarityVector.push_back(make_pair(other, similarity));
    }

    //sort the list based on the second value of each pair based on the method below
    stable_sort(similarityVector.begin(), similarityVector.end(), similarPairCompare);

    //output some tasty info
    printf("Contents after sorting:\n");
    for(vector<pair<int, float> >::iterator it=similarityVector.begin(); it != similarityVector.end(); it++)
    {
        printf("sim(%5d, %5d) => %5.4f\n", recommendId, (*it).first, (*it).second);
    }
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