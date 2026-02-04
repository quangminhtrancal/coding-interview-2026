'''
https://leetcode.com/discuss/post/6603702/2140-solving-questions-with-brainpower-b-7zm3/
Explanation:

Define dp[i] as the maximum points we can get starting from question i.
Iterate in reverse (from last question to first) because each decision depends on future questions.
Compute take and skip:
Take: Solve question i, earn points[i], and jump to i + brainpower + 1.
Skip: Ignore question i and move to i + 1.
Transition Formula:
dp[i]=max(take,skip)
Return dp[0] as the answer.
. Time & Space Complexity:
Time Complexity:
O(n) → We process each question once.
Space Complexity:
O(n) → Uses a DP array.
Python Code
class Solution(object):
def mostPoints(self, questions):
"""
:type questions: List[List[int]]
:rtype: int
"""
n = len(questions)
dp = [0] * (n + 1)
'''

for i in range(n - 1, -1, -1):
    points, brainpower = questions[i]
    next_question = i + brainpower + 1
    take = points + (dp[next_question] if next_question < n else 0)
    skip = dp[i + 1]
    dp[i] = max(take, skip)

return dp[0]