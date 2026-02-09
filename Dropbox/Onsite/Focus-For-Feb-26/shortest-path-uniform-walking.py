'''
https://www.1point3acres.com/interview/problems/374ea0b3-6ad5-4d15-a6a4-bfd7a92db739

Given a grid with a starting point at (0, 0) and an endpoint at (n-1, m-1). 
There are four types of walking methods A, B, C, D, each with a fixed time and cost per cell. 
Find the shortest time path from the start to the end using only one walking method throughout. 
If there are multiple paths with the same time, choose the one with the least cost.

Input:

An integer n and an integer m representing the grid size.
Four arrays costsA, costsB, costsC, costsD representing the costs per cell of each method on the grid.
Four integers timeA, timeB, timeC, timeD representing the time per cell for each method.
Output:

An integer representing the shortest time taken from start to end, with the least cost if multiple solutions exist.
Example:

Input:
n = 3, m = 3
costsA = [1, 3, 1]
costsB = [2, 2, 2]
costsC = [3, 1, 2]
costsD = [1, 2, 3]
timeA = 1
timeB = 2
timeC = 1
timeD = 3
Output:
3 (using method A)
Constraints:

1 <= n, m <= 100
1 <= costs*, time* <= 1000
'''