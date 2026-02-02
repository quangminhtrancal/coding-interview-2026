'''
https://www.1point3acres.com/interview/problems/ea7d38db-f5ac-4619-b82f-c7d0228d01ca

API Design for Long Running Requests

Design an API to handle a list of files. Part 1: Implement a function to accept a list of files and process each file simply. The file processing steps are as follows:

Accept a list of strings representing files.
Simulate processing each file and return the result.
Part 2: For the follow-up question, design a method to handle long-running requests.

Each file's processing time can be long, so requests need to be handled asynchronously.
Implement a function to store requests in a queue, support querying request status, and retrieving results.
Input Format:

The first line receives the number of files.
The following lines each represent a file name.
Output Format:

Part 1 returns the simulated processing result of each file.
Part 2 supports querying the request status and retrieving processing results.
Sample Input:

3
data1.txt
data2.txt
data3.txt
Sample Output:

['data1_processed', 'data2_processed', 'data3_processed']
Asynchronous Processing:

Upon submission, return a request id.
Query processing progress and retrieve results based on the request id.
'''