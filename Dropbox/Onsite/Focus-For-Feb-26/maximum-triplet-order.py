'''
https://leetcode.com/discuss/post/6611648/2874-maximum-value-of-an-ordered-triplet-5fsn/
https://leetcode.com/problems/maximum-value-of-an-ordered-triplet-ii/description/
Maximum Value of an Ordered Triplet II

Approach & Explanation:

Precompute min_j & max_k:
min_j[j]: Stores the minimum value from index 0 to j.
max_k[j]: Stores the maximum value from index j+1 to n-1.
Iterate over j (middle element) and compute max value of (nums[i] nums[j]) * nums[k]:
Ensure nums[i] > nums[j] to get a positive difference.
Use max_k[j+1] (precomputed) to get the best k.
Update max_i dynamically to keep track of the best i.
1. Time Complexity:
O(n) → One pass for min_j, one pass for max_k, and one final pass to compute the result.

Python Code
class Solution(object):
def maximumTripletValue(self, nums):
"""
:type nums: List[int]
:rtype: int
"""
n = len(nums)
if n < 3:
return 0

'''



# Step 1: Precompute prefix and suffix max arrays
from pyparsing import nums


prefix_max = [0] * n
suffix_max = [0] * n

prefix_max[0] = nums[0]
for i in range(1, n):
    prefix_max[i] = max(prefix_max[i - 1], nums[i])

suffix_max[n - 1] = nums[n - 1]
for i in range(n - 2, -1, -1):
    suffix_max[i] = max(suffix_max[i + 1], nums[i])

# Step 2: Iterate over j and compute max triplet value
max_val = 0
for j in range(1, n - 1):
    if prefix_max[j - 1] > nums[j]:  # Ensure (nums[i] - nums[j]) > 0
        max_val = max(max_val, (prefix_max[j - 1] - nums[j]) * suffix_max[j + 1])

answer = max_val