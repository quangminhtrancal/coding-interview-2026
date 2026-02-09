'''
https://leetcode.com/problems/making-a-large-island/description/

Data scientist interview question
"Given an n×n binary grid G where 1=land and 0=water with 4-directional connectivity, 
return the size of the largest island achievable by flipping at most one 0 to 1. n can be up to 10^3. 

Provide an O(n^2) time, O(n^2) or better space solution and justify correctness. Follow-ups: 

(a) If you must flip exactly one 1 to 0, what is the minimum number of islands you can achieve? Give an algorithm and complexity. 

(b) If you may perform one 0→1 flip and one 1→0 flip on distinct cells (in any order), 
compute the maximum possible largest-island size and prove optimality or provide a counterexample. 
Discuss edge cases (all 0s, all 1s), recursion-depth limits, and how you’d adapt for very large grids (e.g., chunking/streaming or union-find labeling).",

https://prachub.com/interview-questions/compute-max-island-with-constrained-flips
Given an n×n binary grid G where 1=land and 0=water with 4-directional connectivity, 
return the size of the largest island achievable by flipping at most one 0 to 1. n can be up to 10^3. 

Provide an O(n^2) time, O(n^2) or better space solution and justify correctness. 

Follow-ups: (a) If you must flip exactly one 1 to 0, what is the minimum number of islands you can achieve? 
Give an algorithm and complexity. (b) If you may perform one 0→1 flip and one 1→0 flip on distinct cells (in any order), 
compute the maximum possible largest-island size and prove optimality or provide a counterexample. 
Discuss edge cases (all 0s, all 1s), recursion-depth limits, and how you’d adapt for very large grids (e.g., chunking/streaming or union-find labeling).

'''