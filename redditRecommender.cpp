//To compile: g++ -O3 -w redditRecommender.cpp -o redditRecommender.out
//To run: ./redditRecommender.out <filename>

#include <stdio.h>
#include <stdlib.h>
#include <utility> // std::pair
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

//method headers
int main(int argc, char* argv[]);
int convertUserSubToIndex(int x, int y);
void printGlobalMatrix();

int main(int argc, char* argv[])
{
    //validate command line args
    if(argc < 2)
    {
        printf("Usage: ./redditRecommender.out <filename>\n");
        exit(-1);
    }
    //read command line args
    char* fileName = argv[1];

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

    //so now we have our global matrix, so print it
    printGlobalMatrix();
}

int convertUserSubToIndex(int userID, int subredditID)
{
    return numberOfSubs * userID + subredditID;
}

void printGlobalMatrix()
{
    printf("Graph: (%d users) x (%d subreddits):\n", numberOfUsers, numberOfSubs);

    int columnWidth = 5;
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