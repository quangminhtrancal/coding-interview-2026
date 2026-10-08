# Confluent problems https://interviewsolver.com/interview-questions/confluent
# https://prachub.com/companies/confluent/categories/coding-and-algorithms
# https://www.1point3acres.com/interview/search?q=confluent
# https://www.1point3acres.com/interview/problems/company/confluent
# https://www.interviewdb.io/question/confluent?page=1&name=buying-chairs
# https://www.interviewdb.io/question/confluent
# https://share.gemini.google/ibEK0sY2cqQN
# https://www.1point3acres.com/interview/problems/company/confluent [ consolidated questions]
# IBM https://interviewsolver.com/interview-questions/ibm
# https://www.aced.io/questions?company=confluent&role=swe&type=coding
# https://www.hack2hire.com/question-bank/companies/confluent/coding-questions
# https://www.showoffer.io/practice/confluent
# https://www.hack2hire.com/question-bank/companies/confluent/interview-resources/68e6a799605ab8e9546847e8
# https://crackmlinterview.com/company/confluent

Clarify -> Plan -> Execute -> Test

'''
bisect.insort run time is O(n) 
bisect_left; bisect_right is O(logn)
'''

# // You are building an App that lets the users determine the most cost-effective order that they can place in a restaurant for the food items that they want to have. You have the menu of the restaurant that contains item name, and it's price. The restaurant can also offer Value Meals, which are groups of several items, at a discounted price. Write a program that accepts a list of menu items, and a list of items that the user wants to eat, and outputs the best price at which they can get all of their desired items.
# // [Constraint: The user can order a maximum of 3 unique items.]
# https://leetcode.com/discuss/post/4999712/confluent-coding-round-by-weirdohere-0w5f/

# input
# [5.00, "pizza"],
# [8.00, "sandwich, coke"],
# [4.00, "pasta"],
# [2.00, "coke"],
# [6.00, "pasta, coke, pizza"],
# [8.00, "burger, coke, pizza"],
# [5.00, "sandwich"]

# user_wants: ["burger", "pasta"]

# output
# 12




###################################
# https://leetcode.com/discuss/post/8545763/confluent-uk-remote-interview-experience-68jv/
# I had total of 5 rounds.

# Phone Screen
# Similar to Time Based Key-Value Store and maintaining a sum and finding average
# Coding Round 1
# Inverted Index question already shared on leetcode.
# Coding Round 2
# Similar to combination sum, with memoization follow ups
# System Design
# Building a podcast service, focus on feed generation.
# Behavioural
# Project deep dives, day to day routine, work ethics.


###################################
# https://leetcode.com/discuss/post/8501506/confluent-ibm-software-engineer-l2-25-yo-d5qa/

# Round 1 : Online Assesment
# 60 min Hackerrank test with 3 questions was able to solve all the questions.
# Verdict : Positive

# Round 2 : Peer To Peer Virtual DSA Round
# Q1 : Verify Sudoko
# Q2 : Solve Sudoko
# Result : Both Question Solved

# Time : 60 mins

# Verdict : Positive

# Round 3 : Peer To Peer Virtual Machine Coding Round
# Q1 : Find word in a list of documents
# Q2 : Find Phrase in the same sequence they appear in list of documents
# Result : Both Question Solved

# Time : 60 mins

# Verdict : Positive

# Round 4 : Peer To Peer Virtual Values Alignment Round
# Focus area of this round was on my work in previous company. And Some scenarios based behavioural questions.

# Now the EM/HM asked me

# Q1 : You've mentioned that you wanna work in a Distributed System kinda environment, but this is a DevProd role we don't work in Distributed System Environment.

# Ans : I'm Open to work in services that don't involve distributed systems environment as well. Since I've worked in Distributed Systems in past company I've mentioned but it's not a mandatory job requiremnent for me. I look forward to join the team and take ownership of projects you assign me.

# Q2 : You have never worked in a DevProd Role, You have always worked for customer facing teams. I'm concerned will you be able to work here?

# Ans : Yes I don't think it's a blocker anyway. I haven't got chance in my previous companies for a DevProd role. Since now I have one. I would really like to contribute.

# Time : 45 mins

# Verdict : Negative


###################################
# https://leetcode.com/discuss/post/7529937/topics-priority-for-interviews-by-diliie-bhwq/

# Dynamic Programming (1d , 2d , with bit manipulation)
# Graph. bfs /dfs (imp but sometimes ignored - topological sort , union-find)
# Binary Search
# Backtracking /Recursion
# Trie
# Segment trees
# Sliding window
# Bit Manipulation


###################################
# https://leetcode.com/discuss/post/5047273/confluent-onsite-interview-experience-re-2swo/
# Phone Screen:
# Implement a data structure to store key-value entries within a time-based interval.
# Slight variation to LRU Cache.

# Round 1:
# Implement a Word Search Engine, given a list of documents with text, return the document ids that the given word belongs in. Followup: Search a phrase

# Round 2:
# Design TinyURL

# Round 3:
# Implement the Unix Tail -N Command

# Round 4:
# Talk about a project you had the most impact on, what was the biggest challenge, etc.


###################################

# convert these into list of questions


#         {
#             "company": "Confluent",
#             "content": "You are given a `9 x 9` Sudoku puzzle in which some cells are filled with digits and the rest are empty. Fill every empty cell so that the completed board is a valid Sudoku solution, and return the completed board.\n\n### Function Signature\n\n```python\ndef solve_sudoku(board: list[list[str]]) -> list[l",
#             "content_enhanced": "You are given a `9 x 9` Sudoku puzzle in which some cells are filled with digits and the rest are empty. Fill every empty cell so that the completed board is a valid Sudoku solution, and return the completed board.\n\n### Function Signature\n\n```python\ndef solve_sudoku(board: list[list[str]]) -> list[l",
#         },
#         {
#             "company": "Confluent",
#             "content": "You are given a `9 x 9` Sudoku board in which some cells are filled with digits and the rest are empty. Determine whether the filled cells are consistent with the rules of Sudoku.\n\n### Function Signature\n\n```python\ndef is_valid_board(board: list[list[str]]) -> bool:\n```\n\n### Rules\n\n- Return `True` i",
#             "content_enhanced": "You are given a `9 x 9` Sudoku board in which some cells are filled with digits and the rest are empty. Determine whether the filled cells are consistent with the rules of Sudoku.\n\n### Function Signature\n\n```python\ndef is_valid_board(board: list[list[str]]) -> bool:\n```\n\n### Rules\n\n- Return `True` i",
#         },
#         {
#             "company": "Confluent",
#             "content": "VO1. coding\uff0c\u5730\u91cc\u7ecf\u5178\u9898\uff1atail -n\uff0c \u8fd9\u91cc\u63d0\u9192\u4e00\u4e0b\uff0c\u56e0\u4e3a\u9762\u8bd5\u5b98\u4e00\u5b9a\u8981\u5148save\u4e00\u4e2atxt file\u8981\u4ece\u8fd9\u4e2atxt file \u91ccread string/char\u4f5c\u4e3atestcase\u6240\u4ee5\u5982\u679c\u7528java\u7684\u5c0f\u4f19\u4f34\u8bf7\u52a1\u5fc5\u719f\u6089 writebuffer/readBuffer. \u56e0\u4e3a\u8fd9\u91cc\u662f\u65e0\u6cd5\u63d0\u4f9b/\u5f53\u573a\u8ba9\u4f60\u67e5api\u7684\uff0c\u6700\u597d\u8fd8\u662f\u7528python\u6bd4\u8f83\u597d\uff08\u56e0\u4e3a\u6784\u5efatestcase\u8fd9\u91cc\u7528\u4e86\u5927\u91cf\u7684\u65f6\u95f4\uff0c\u5bfc\u81f4followup\u6ca1\u5199\u5b8c\uff09\nVO2. coding\u4e5f\u662f\u5730\u7406\u7ecf\u5178\u9898\uff0c\u5c0f\u602a\u517dcost,\u8fd9\u91cc\u57fa\u672c\u4e0adfs/bfs\u90fd\u80fd\u505a\u5f97\u51fa\u6765\u5730\u7406\u539f\u9898follow up\u4e5f\u662f\u539f\u9898\u3002\nVO3. SD\u662fRSS news feed,\u8fd9\u91cc",
#             "content_enhanced": "This entry contains two coding tasks from the same interview category.\n\n### 
# Task A: Implement a file tail operation\nImplement a function `tail(filePath, n)` that returns the last `n` lines of a text file in their original order.
# \n\nRequirements:\n- The input is a real file path, not an in-memory string",
#             "seo_summary": "This question evaluates competency in efficient file I/O and streaming techniques for implementing tail, 
# and in graph search and shortest-path algorithms with path reconstruction for computing minimum monster cost in a grid.",
#
#             "company": "Confluent",
#             "content": "\u6280\u672f\u7b5b\u9009\u8fd9\u4e00\u8f6e\u6574\u4f53\u8fd8\u662f\u6bd4\u8f83\u7b80\u5355\u7684. \u7ed9\u4f60\u4e00\u4e2a\u51fd\u6570\u67e5\u8be2\u7684 signature, \u8ba9\u4f60\u5224\u65ad\u662f\u5426\u5b58\u5728\u4e00\u4e2a\u5df2\u7ecf\u6ce8\u518c\u7684\u51fd\u6570\u53ef\u4ee5\u5339\u914d. \u540e\u9762\u4f1a\u6d89\u53ca optional arguments \u4ee5\u53ca variable number of arguments \u8fd9\u79cd\u60c5\u51b5.\nOnsite \u4e00\u5171\u6709\u56db\u8f6e.\n\u7b2c\u4e00\u8f6e coding \u662f\u5b9e\u73b0\u7c7b\u4f3c\u6253\u5370\u6587\u4ef6\u6700\u540e N \u884c\u7684\u529f\u80fd, \u540c\u65f6\u8ba8\u8bba\u4e00\u4e9b tradeoff \u548c\u4f18\u5316, \u6bd4\u5982\u7528 buffer \u8fd8\u662f\u7528 file pointer offset \u6765\u505a. \u540e\u534a\u90e8\u5206\u504f\u7406\u8bba, \u7ed9\u4f60\u4e00\u5957 file API, \u7c7b\u4f3c\u53ef\u4ee5 read N bytes, \u79fb\u52a8 file pointer +N \u6216 -N, \u4ee5\u53ca",
#             "content_enhanced": "Solve the following interview-style problems:\n\n1. **Function signature matching**\n   
# You are given a registry of function definitions. Each function has an ordered parameter list where parameters may be **required**,
#  **optional**, or a trailing **variadic** parameter. Given a candidate call signatur",
# 
#             "seo_summary": "This multi-part prompt evaluates skills in function signature and type matching, 
# resource-constrained file I/O and streaming for large files, and data-structure design for randomized queues including multiset equality, 
# synchronization, and compact run-length encodings.",
#            
#             "seo_summary": "This question evaluates understanding of data structures\u2014particularly priority queues/heaps\u2014and techniques 
# for efficiently handling global/bulk updates and minimum extraction under changing offsets.",
#             
#                     "name": "Heaps & Priority Queues",
#                     "slug": "heaps"


###################################
# https://leetcode.com/discuss/post/5166350/confluent-senior-software-engineer-offer-87jb/
# My experience regarding recent SSE interview rounds with Confluent -
# I took a referral.
# After 20 days, recruiter called me and asked to schedule a Qualifer round.

# Qualifier Round:
# I was asked a DSA+LLD question and was supposed to implement and run it on coderpad. There were followup question on time complexity and 
# Concurrency(Locking especially).
# Recruiter mailed after 3 days after followup and scheduled full onsite loop.

# Onsite 1
# Was asked a DSA question in 2 parts first being easy-medium and second being medium-hard. Again working code was required with good coding practice.
#  Wrote it nicely and interviewer was impressed.

# Onsite 2
# Was Asked a LLD question particularly on optimizing memory while reading a huge file as part of the problem. 
# Awareness of low level language memory constucts was key. Was able to solve it and run. Working code was important again.
#  Discussed further optimization on memory access when asked but could not code as we were out of time. 
# Struggled a little with API knowledge but was able to get through. Interviewer seemed fine in the end.

# Onsite 3
# Was Asked a HLD question and was the easist round as HLD being my favourite and forte. 
# Had to draw and explain the thought process with tradeoffs being made. Interviewer seemed happy.

# Onsite 4
# This was a deep dive+cultural fit round. Usual question around the project and different phases and situations in project and how did i handle them. 
# This went really well.

# After one week, followed up with recruiter and they said its a hire call. They setup a role sell call post that.



'''
Qualifier Round:
Given a window size,
perform get, put, and average operation
items that were added before the window size should be removed while taking average as well, and also during get operation, return null if item expired.
window size 1hr
00:00 put("A",10)
00:10 put("B",20)
00:30 average() -> 15
01:05 average () -> 20
01:08 get("B") -> 20
01:15 put("A",30)
01:50 average -> 30

Here is a clean Python solution using a doubly-linked list with a hash map (similar to an LRU Cache layout) 
alongside running sums to handle all operations in $O(1)$ time complexity.
'''



class Node:
    def __init__(self, key: str, val: float, timestamp: int):
        self.key = key
        self.val = val
        self.timestamp = timestamp
        self.prev = None
        self.next = None

class SlidingWindowCache:
    def __init__(self, window_seconds: int = 3600):
        self.window = window_seconds
        self.cache = {}  # key -> Node
        
        # Doubly Linked List to track insertion order / timestamps
        self.head = Node("", 0, 0)  # Dummy head (oldest)
        self.tail = Node("", 0, 0)  # Dummy tail (newest)
        self.head.next = self.tail
        self.tail.prev = self.head
        
        self.running_sum = 0.0
        self.running_count = 0

    def _add_to_tail(self, node: Node):
        """Insert a node at the end of the doubly linked list."""
        node.prev = self.tail.prev
        node.next = self.tail
        self.tail.prev.next = node
        self.tail.prev = node

    def _remove_node(self, node: Node):
        """Remove a node from the doubly linked list."""
        node.prev.next = node.next
        node.next.prev = node.prev

    def _evict_expired(self, current_time: int):
        """Remove all nodes outside the sliding time window."""
        while self.head.next != self.tail:
            oldest = self.head.next
            if current_time - oldest.timestamp >= self.window:
                self._remove_node(oldest)
                del self.cache[oldest.key]
                self.running_sum -= oldest.val
                self.running_count -= 1
            else:
                break

    def put(self, key: str, value: float, current_time: int):
        self._evict_expired(current_time)
        
        # If key already exists, remove old record first
        if key in self.cache:
            old_node = self.cache[key]
            self._remove_node(old_node)
            self.running_sum -= old_node.val
            self.running_count -= 1
        
        new_node = Node(key, value, current_time)
        self.cache[key] = new_node
        self._add_to_tail(new_node)
        self.running_sum += value
        self.running_count += 1

    def get(self, key: str, current_time: int):
        self._evict_expired(current_time)
        
        if key not in self.cache:
            return None
        return self.cache[key].val

    def average(self, current_time: int) -> float:
        self._evict_expired(current_time)
        
        if self.running_count == 0:
            return 0.0
        return self.running_sum / self.running_count

# Onsite 1: Implement a Word Search Engine, given a list of documents with text, return the document ids that the given word belongs in. Followup: Search a phrase
# Onsite 2: Implement the Unix Tail -N Command

# I guessed questions after reading other confluent interview experiences.

###################################
"""

Warehouse Loading: Reach

You manage a loading dock robot. You are given

N: operations represented by an integer array `

W:  W[i] > 0  : load an item ofW[i]
(The total load increases). W[i] < 0 unload/remove weight|W[i]|
(the total load The robot starts with total load 0

{
  "title": "Warehouse Loading: Target Reach",
  "description": "You are managing an automated loading dock robot. You are given an array W containing N operations, 
  where W[i] > 0 represents loading an item of weight W[i] and W[i] < 0 represents unloading weight |W[i]|. 
  The robot begins with an initial total load of 0. You can execute the N operations in any arbitrary order. 
  Determine whether there exists at least one permutation of the operations such that at some point 
  during execution (i.e., after executing some prefix of the chosen ordering), the running total load equals exactly TargetWeight.",
  "input_format": {
    "N": "An integer representing the number of operations.",
    "W": "An integer array of length N containing the weight operations.",
    "TargetWeight": "An integer representing the desired target total load."
  },
  "output_format": "Boolean (true if there exists an ordering where a prefix sum equals TargetWeight; otherwise false).",
  "constraints_and_notes": [
    "Negative Running Totals: Clarify whether the total load is allowed to drop below 0 at intermediate steps.",
    "Value Ranges: Constraints on N, W[i], and TargetWeight determine whether to use Subset Sum / Dynamic Programming or DFS / Backtracking."
  ],
  "sample_tests": [
    {
      "input": {
        "N": 3,
        "W": [2, -1, 4],
        "TargetWeight": 1
      },
      "output": true,
      "explanation": "Execute in order [-1, 2, 4]. After the first operation (-1), total is -1. After the second (+2), total becomes 1, matching TargetWeight."
    },
    {
      "input": {
        "N": 2,
        "W": [-3, 5],
        "TargetWeight": 2
      },
      "output": {
        "negative_totals_allowed": true,
        "negative_totals_disallowed": false
      },
      "explanation": "If negative total loads are permitted, order [-3, 5] yields running totals -3, then 2 (reaches target). 
      If non-negative prefix constraint is enforced, valid sequences may vary."
    },
    {
      "input": {
        "N": 3,
        "W": [1, 1, 1],
        "TargetWeight": 2
      },
      "output": true,
      "explanation": "Execute in order [1, 1, 1]. After 2 steps, total load is 2."
    },
    {
      "input": {
        "N": 3,
        "W": [-1, -2, -3],
        "TargetWeight": -3
      },
      "output": true,
      "explanation": "Execute in order [-3, -1, -2]. Reaches total load -3 on the first step."
    }
  ]
}
"""
class Solution:
    def canReachTarget(weights: list[int], target: int) -> bool:
        n = len(weights)

        if target == 0:
            return True

        if n == 0:
            return target == 0        

        memo = {}
        def canLoad(current_load: int, used_mask: int):
            if current_load == target:
                return True

            key = (current_load, used_mask)
            if  key in memo:
                return memo[key]

            for i, w in enumerate(weights):
                new_item_mask = 1 << i
                if not (used_mask & new_item_mask):
                    new_mask = used_mask | new_item_mask
                    new_load = current_load + w

                    if new_load > 0:
                      if canLoad(new_load, new_mask):
                        memo[key] = True

                        return memo[key]    
                      
            
            memo[key] = False
            return False
                
        return canLoad(0, 0)
# Complexity AnalysisTime Complexity: $O(N * S)
# where N is the number of elements in W and 
# S is the number of distinct reachable sums (bounded by 2^N in the worst case, or $\text{range of possible sums}$ when using DP).Space Complexity: $O(S)$ to store the set of reachable intermediate totals.


"""
Given bank transactions, positive for credits and negative for debits, determine whether any subset sums to a target balance. Each transaction can be used once. How would you improve on checking every subset?
For example, [7, -3, 5, -2] with 4 returns true because 7 + (-3) = 4. 

=> subset sum
"""
def getTarget(transactions: list[int], target: int) -> bool:
    if not transactions:
        return False

    reachable = {0}

    for tx in transactions:
        # Create new sums without mutating reachable during iteration
        new_sums = {current + tx for current in reachable}
        
        # Check early exit condition
        if target in new_sums:
            return True
            
        reachable.update(new_sums)

    return False

# ANOTHER WAY
def canReachTarget(weights: list[int], target: int) -> bool:
    memo = {}

    def dfs(index: int, current_load: int) -> bool:
        if current_load == target:
            return True
        if index == len(weights):
            return False

        key = (index, current_load)
        if key in memo:
            return memo[key]

        # Option 1: Include current weight
        if dfs(index + 1, current_load + weights[index]):
            memo[key] = True
            return True

        # Option 2: Exclude current weight
        if dfs(index + 1, current_load):
            memo[key] = True
            return True

        memo[key] = False
        return False

    return dfs(0, 0)
###################################
# * Given sorted event timestamps, count events in (t - W, t] for each event. For [1, 2, 4, 7] and W = 3, return [1, 2, 2, 1]. Can you do it in O(n)?

"""
Sample TestsTest 1Input: timestamps = [1, 2, 4, 7], W = 3
Output: [1, 2, 2, 1]

Explanation:For $t = 1$: Window is $(1 - 3, 1] = (-2, 1]$.  Events in window: [1] $\rightarrow$ count = 1.

For $t = 2$: 
Window is $(2 - 3, 2] = (-1, 2]$. Events in window: [1, 2] $\rightarrow$ count = 2.

For $t = 4$: Window is $(4 - 3, 4] = (1, 4]$. Events in window: [2, 4] $\rightarrow$ 
count = 2 (event at 1 is excluded because $1 \le 1$ is false for strictly greater than $t - W$).

For $t = 7$: Window is $(7 - 3, 7] = (4, 7]$. Events in window: [7] $\rightarrow$ count = 1.


Test 2 (Duplicate Timestamps)Input: timestamps = [1, 1, 2, 3], W = 1
output: [2, 2, 3, 2]

Explanation:For $t = 1$: Window $(0, 1]$. Events: [1, 1] $\rightarrow$ count = 2.
For $t = 1$: Window $(0, 1]$. Events: [1, 1] $\rightarrow$ count = 2.
For $t = 2$: Window $(1, 2]$. Events: [2] $\rightarrow$ count = 1 (or [1, 1, 2] depending on condition; 
here $(1, 2]$ excludes timestamps $\le 1$, so count = 1).$O(N)$ 

Solution Approach: Two Pointers / Sliding WindowSince timestamps is already sorted, we can maintain a left pointer left that points to the first event currently inside the valid window $(t_i - W, t_i]$.As the right pointer right moves from $0$ to $N-1$:We advance left while timestamps[right] - timestamps[left] >= W.The number of events in the window for timestamps[right] is simply:$$\text{count} = \text{right} - \text{left} + 1$$Because both left and right pointers move forward at most $N$ times, the overall time
"""
class Solution:
  def countEvent(time_stamp: list[int], window: int) -> list[int]:
    n = len(time_stamp)

    if n == 0 or window <= 0:
      return []

    if n == 1:
        return [1]

    left, right = 0, 0
    result = [1] * n
    while right < n:
        while time_stamp[right] - time_stamp[left] >= window:
            left += 1

        if time_stamp[right] == time_stamp[left]:
            result[left] += 1
        result[right] = right - left + 1

        right += 1

    return result


###################################


###################################
# https://www.1point3acres.com/interview/problems/company/ibm/maximum-concurrent-processes

###################################
"""
{
  "title": "Print Last N Lines (Tail Utility)",
  "description": "Read an integer N, then process the remaining stream or file input to print the final N lines in 
   their original order while maintaining bounded memory usage.",
  "algorithm_strategy": {
    "name": "Streaming Queue / Ring Buffer",
    "steps": [
      "Read the input line by line.",
      "Maintain a FIFO queue holding at most N lines.",
      "If pushing a new line causes queue size to exceed N, pop the oldest line.",
      "At end-of-file (EOF), print all lines remaining in the queue in chronological order."
    ]
  },
  "edge_cases": [
    "If N = 0, print nothing.",
    "If total lines < N, print all available lines.",
    "Handle non-newline terminated final lines (ensure the final string segment counts as a line).",
    "Avoid treating a trailing newline at EOF as an additional empty line.",
    "Avoid loading the entire file into memory; memory usage should be strictly bounded by N lines."
  ]
}

===========
Why threads don't help

The work is a sequential scan of a stream, and the result depends on line order. You can't know which lines 
are "last" until you've seen the end.
It's I/O-bound, and the per-line work (one deque.append) is trivial. In CPython the GIL also prevents CPU-parallel speedup.

If you need thread safety (say, one thread reads while another polls the current tail), deque.append is atomic in CPython, 
but a lock makes the intent explicit and makes snapshots consistent:
"""
import threading
from collections import deque


class TailBuffer:
    """Thread-safe bounded buffer holding the last n lines."""

    def __init__(self, n):
        self._buf = deque(maxlen=n) if n > 0 else None
        self._lock = threading.Lock()

    def add(self, line):
        if self._buf is None:
            return
        with self._lock:
            self._buf.append(line)

    def snapshot(self):
        if self._buf is None:
            return []
        with self._lock:
            return list(self._buf)

###################################

"""
Insufficient details: only mentions a 'monster cost' problem solvable via DFS/BFS with a follow-up identical to the original; 
missing concrete I/O, cost definition, and constraints, so it is omitted.

"This question evaluates competency in efficient file I/O and streaming techniques for implementing tail, 
# and in graph search and shortest-path algorithms with path reconstruction for computing minimum monster cost in a grid.",
"""

# The example text matches Confluent interview questions listed on PracHub, which are titled "Implement Tail and Find Monster Cost" 
# and "Solve constrained monster traversal". The tail half is well documented. 
# The monster half is only a vague summary, so the grid version below is a reasonable reconstruction.

# Part 1: Implement tail -n (streaming)

# The version I found gives you a huge newline-delimited file and a limited API (read(k), movePointer(pos), getSize()). 
# You must print the last N lines without reading the whole file, and discuss buffer scanning versus moving the pointer often. 
# prachub

# Approach: start at the end of the file and read fixed-size blocks backwards, prepending each block. Stop once you have seen more than N newlines, 
# then keep the last N lines.

# python
def tail(path: str, n: int, block: int = 8192) -> list[str]:
    if n <= 0:
        return []
    
    with open(path, "rb") as f:
        f.seek(0, 2)
        pos = f.tell()                      # getSize()
        data = b""

        while pos > 0 and data.count(b"\n") <= n:
            step = min(block, pos)
            pos -= step
            f.seek(pos)                     # movePointer(pos)
            data = f.read(step) + data      # read(k)
        lines = data.split(b"\n")
        if lines and lines[-1] == b"":      # trailing newline
            lines.pop()
        return [l.decode("utf-8", "replace") for l in lines[-n:]]
    
# Time and space: you read roughly the size of the last N lines plus one block, so the cost is O(size of the tail), not O(file size).
# Bytes, not characters: \n never appears inside a multi-byte UTF-8 sequence, so splitting on bytes and decoding each line afterwards is safe.
# Trailing newline: this is the main edge case. Require more than N newlines so the first line you keep is complete.
# Tradeoff (large buffer vs frequent seeks): a bigger block means fewer syscalls and seeks but more wasted bytes read. 
# A tiny block, such as one byte at a time, means many seeks, which is slow. Something like 4–64 KB matches the disk page size.
# Stream variant (stdin or pipe, no seeking): keep a collections.deque(maxlen=n) and iterate lines. This is O(n) memory and one pass.
# python

from collections import deque
def tail_stream(lines, n):
    return list(deque(lines, maxlen=n)) if n > 0 else []

# Part 2: "Monster minimum cost"

# The grid wording ("graph search and shortest-path with path reconstruction") 
# suggests this: you move from the start to the goal, entering a cell costs the monster there, 
# and you want the minimum total cost plus the path. Dijkstra handles this. 
# BFS or DFS only works if every cell costs the same.
# Dijkstra algorithm

import heapq

def min_monster_cost(grid, start, goal):
    R, C = len(grid), len(grid[0])
    INF = float("inf")
    dist = [[INF] * C for _ in range(R)]

    parent = {}
    sr, sc = start
    dist[sr][sc] = grid[sr][sc]

    pq = [(grid[sr][sc], sr, sc)]

    while pq:
        d, r, c = heapq.heappop(pq)
        if d > dist[r][c]:
            continue
        if (r, c) == goal:
            break
        for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < R and 0 <= nc < C and grid[nr][nc] >= 0:  # -1 = wall
                nd = d + grid[nr][nc]
                if nd < dist[nr][nc]:
                    dist[nr][nc] = nd
                    parent[(nr, nc)] = (r, c)
                    heapq.heappush(pq, (nd, nr, nc))

    if dist[goal[0]][goal[1]] == INF:
        return -1, []
    path, cur = [goal], goal
    while cur != start:
        cur = parent[cur]
        path.append(cur)
    return dist[goal[0]][goal[1]], path[::-1]


### Dijistra implementation
import heapq

def dijkstra(graph: dict, start_node: str | int) -> tuple[dict, dict]:
    """
    Computes shortest path distances from a start node to all other nodes.
    
    :param graph: Adjacency list representation {node: [(neighbor, weight), ...]}
    :param start_node: The starting node
    :return: A tuple of (distances, previous_nodes)
    """
    # Initialize distances with infinity
    distances = {node: float('inf') for node in graph}
    distances[start_node] = 0
    
    # Store shortest path tree for reconstructing paths
    previous_nodes = {node: None for node in graph}
    
    # Priority Queue stores tuples of: (current_distance, node)
    pq = [(0, start_node)]
    
    while pq:
        current_distance, current_node = heapq.heappop(pq)
        
        # If we found a longer path than already recorded, skip
        if current_distance > distances[current_node]:
            continue
            
        for neighbor, weight in graph[current_node]:
            distance = current_distance + weight
            
            # Found a shorter path to neighbor
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous_nodes[neighbor] = current_node
                heapq.heappush(pq, (distance, neighbor))
                
    return distances, previous_nodes


def reconstruct_path(previous_nodes: dict, target_node: str | int) -> list:
    """Helper function to reconstruct the path from start to target."""
    path = []
    curr = target_node
    while curr is not None:
        path.append(curr)
        curr = previous_nodes[curr]
    return path[::-1] # Reverse path so it goes start -> target

# Complexity: O(RC log(RC)) time and O(RC) space.
# Path reconstruction: store a parent pointer whenever you relax a cell, then walk back from the goal.
# Simplification: if you can only move right or down, plain DP is enough (dp[r][c] = cost + min(dp[r-1][c], dp[r][c-1])).
# The other variant: "constrained monster traversal"

# The PracHub listing describes this one as a directed graph of n rooms, labeled 0..n-1, where each room i has a monster with health hp[i] ≥ 0. The snippet cuts off before the constraint, so I can't say exactly what it is. It is probably a "minimum starting strength" or "cheapest route" question. If it turns out to be a state-dependent search, the usual move is to add the constraint to the Dijkstra state, as in (cost, room, extra_state). 
# prachub



###################################

"""
The Random Queue ADT on this page behaves like a queue in how items are added, but unlike a FIFO queue, 
each removal chooses uniformly at random from the items currently present.

Part A: Core behavior

enqueue(x): addx
.
dequeue(): choose one current item uniformly, remove it, and return it.

peek()(optional): return a random item without removing it.
size(): return the number of items.
A common design is to store items in a dynamic array. To dequeue, choose a random index, save that item, 
replace its slot with the last item, and remove the last slot. This avoids shifting elements. Under the usual assumption that 
random-index generation is constant time, enqueue and dequeue are expected O(1); storage is O(n).

dequeue

on an empty queue needs a defined behavior, such as throwing an exception or returning an optional value.Part B: Equality

First decide what equality means. A natural choice is multiset equality: two queues are equal if they contain the same values with the same multiplicities, regardless of storage order. For example,

[a, a, b] equals[b, a, a] , but not[a, b, b]

.If elements are hashable, compare sizes and frequency maps. If you sort copies instead, comparison takes O(n log n). Avoid mutating the queues while checking equality.

Part C: Thread safety

The random choice and removal must be one atomic operation. Otherwise, another thread could change the queue between reading its size, choosing an index, and removing the item. Protect related operations with a lock, or use a carefully designed concurrent structure. Decide whether

size() and  peek()

need a consistent snapshot, and document the guarantee. A basic lock around each operation provides simple linearizable behavior.Part D: RLE-backed equality

For run-length encoding, compare the represented multisets without expanding all repeated elements. 
Aggregate counts per value across runs, since the same value may appear in multiple runs—even in different positions or 
split into different run lengths. Then compare the aggregated counts for both queues. 

This takes time proportional to the number of runs plus the number of distinct values, 
with space proportional to the number of distinct values.

The exact comparison method depends on the element types and whether hashing or ordering is available. 
I couldn’t find a separate Confluent question-bank entry for this prompt; 
the available Confluent interview experiences may provide related context. 


{
  "title": "Random Queue ADT",
  "description": "A Random Queue Abstract Data Type behaves like a standard queue when adding items, 
  but removes elements uniformly at random rather than following First-In, First-Out (FIFO) ordering.",
  "sections": {
    "part_a_core_behavior": {
      "title": "Core Behavior & Operations",
      "operations": [
        {
          "method": "enqueue(x)",
          "description": "Add item x to the queue."
        },
        {
          "method": "dequeue()",
          "description": "Choose one current item uniformly at random, remove it, and return it."
        },
        {
          "method": "peek()",
          "description": "Return a randomly chosen item without removing it (optional operation)."
        },
        {
          "method": "size()",
          "description": "Return the current number of items in the queue."
        }
      ],
      "implementation_details": {
        "underlying_structure": "Dynamic Array",
        "removal_strategy": "Select a random index, store its value, overwrite the slot with the last element in the array, 
        and pop the last slot. This eliminates array shifting.",
        "time_complexity": "O(1) expected for enqueue and dequeue (assuming O(1) random index generation).",
        "space_complexity": "O(n) space.",
        "edge_cases": "Calling dequeue() on an empty queue must have defined error handling (e.g., 
        throwing an exception or returning an optional/null value)."
      }
    },
    "part_b_equality": {
      "title": "Equality Logic",
      "definition": "Multiset Equality: Two random queues are equal if they contain the exact same elements 
      with identical frequencies/multiplicities, regardless of internal storage order.",
      "examples": {
        "equal": ["[a, a, b]", "[b, a, a]"],
        "not_equal": ["[a, a, b]", "[a, b, b]"]
      },
      "approaches": [
        {
          "type": "Hash Map Frequency Counter",
          "time_complexity": "O(n)",
          "requirements": "Elements must be hashable. Compare size and element frequency maps."
        },
        {
          "type": "Sorting Copies",
          "time_complexity": "O(n log n)",
          "requirements": "Elements must be comparable/sortable."
        }
      ],
      "constraints": "Equality checks must non-destructively inspect the queues without mutating their contents."
    },
    "part_c_thread_safety": {
      "title": "Thread Safety & Concurrency",
      "atomic_operations": "Random index selection and item removal must occur as a single atomic operation 
      to prevent race conditions where queue size or content changes mid-operation.",
      "concurrency_strategies": [
        "Reentrant/Mutex Locks: Wrap each public method (enqueue, dequeue, peek, size) in a lock to 
        guarantee simple linearizable behavior.",
        "Snapshot Guarantees: Decide and document whether size() and peek() reflect a consistent 
        point-in-time snapshot of the queue."
      ]
    },
    "part_d_rle_backed_equality": {
      "title": "Run-Length Encoding (RLE) Equality",
      "description": "Compare multisets directly from run-length encoded representations without expanding 
      repeated elements into memory.",
      "algorithm": "Aggregate total counts per distinct value across all runs (since identical values 
      can appear in separate runs or vary in run lengths), then compare aggregated counts between queues.",
      "time_complexity": "O(R + V), where R is total runs and V is total distinct values.",
      "space_complexity": "O(V) to store aggregated frequency counts."
    }
  }
}

===> **************** answer:
https://share.gemini.google/oQtR9RD6RsNZ 
"""
import random
import threading
from typing import TypeVar, Generic, Optional

T = TypeVar('T')

"""
threading.RLock() is a reentrant lock: the thread that already holds it can acquire it again without blocking itself. 
A plain threading.Lock() would deadlock in that situation.
"""   

class RandomQueue(Generic[T]):
    def __init__(self) -> None:
        self._items: list[T] = []
        self._lock = threading.RLock()     

    def enqueue(self, item: T) -> None:
        """Appends an item in O(1) amortized time."""
        with self._lock:
            self._items.append(item)

    def dequeue(self) -> T:
        """
        Removes and returns a uniformly random item in O(1) time.
        Throws IndexError if queue is empty.
        """
        with self._lock:
            if not self._items:
                raise IndexError("dequeue from an empty RandomQueue")
            
            # Select random index
            rand_idx = random.randint(0, len(self._items) - 1)
            last_idx = len(self._items) - 1
            
            # Swap target element with last element
            self._items[rand_idx], self._items[last_idx] = (
                self._items[last_idx],
                self._items[rand_idx],
            )
            
            # Pop last element in O(1)
            return self._items.pop()

    def peek(self) -> T:
        """
        Returns a uniformly random item without removing it.
        Throws IndexError if queue is empty.
        """
        with self._lock:
            if not self._items:
                raise IndexError("peek from an empty RandomQueue")
            rand_idx = random.randint(0, len(self._items) - 1)
            return self._items[rand_idx]

    def size(self) -> int:
        """Returns the current number of elements."""
        with self._lock:
            return len(self._items)

    def is_empty(self) -> bool:
        with self._lock:
            return len(self._items) == 0

    def __iter__(self):
        """Allows non-destructive snapshots of elements for equality checks."""
        with self._lock:
            return iter(list(self._items))

###################################
"""
Minimum Health Required for Gaming
A person wants to play a game with the goal of defeating opponents at each level. 
Initially, there are 'n' opponents at the first level, with initial_players[i] 
corresponding to each opponent's strength. 

Then, a list named next_players is provided, representing the strength of players added with each new level. 
The goal is to defeat the player ranked at 'rank' in terms of strength at each level (as new players are added, 
the positions of existing players do not change). Each time an opponent is defeated, 
the player's health decreases by that opponent's strength. 
To ensure survival till the end, the task is to find the minimum initial health required 
so that the player's health is greater than or equal to zero at the end. 
For this question, I maintained a min heap of size 'rank'.

=====> $$$$$$$$$$$$$$$$$$$$$$$$

use min heap with size of rank ==> if more than rank size, then heap just pop
"""



###################################



"""
The problem on your current page is “Text Search: search a word, then search a phrase (follow-up).” It asks you to tokenize a multi-line text and answer two kinds of queries:

WORD <word>
: count tokens equal to that word.
PHRASE <phrase>
: count occurrences where the phrase’s tokens appear consecutively and in order.
Tokenization and matching

Split on any non-alphanumeric character, then compare case-insensitively. For example,

Hello, world!

becomes the tokenshello

,world

. A phrase match is based on adjacent tokens—not on raw characters—so punctuation between words does not prevent a match.For the sample text,

PHRASE hello world

matchesHello, world!

, whilePHRASE world hello

matchesworld: hello.

. The phrase does not match if another token lies between its words.A straightforward approach

Read all text lines and tokenize them into one sequence of normalized words.
For eachWORD
query, count matching tokens.
For eachPHRASE
query, tokenize the phrase and scan the text tokens for matching consecutive sequences.
If there are

T

text tokens andP

tokens in a phrase, a direct scan takesO(T × P)

in the worst case for that phrase. With many queries, reuse preprocessing: build a frequency map for word queries, and consider a more efficient phrase-matching method if performance constraints require it. The page’s stated limits allow a large text and many queries, so discuss the tradeoff between a simple scan and indexing/preprocessing.One subtlety: keep token order across line boundaries unless the prompt explicitly says each line is separate; the given description defines the text as multi-line but does not specify that lines break phrase matching. The searchable Confluent materials don’t include this question, but you can browse the Confluent interview experiences. 


{
  "title": "Text Search: Single Word & Consecutive Phrase Matching",
  "description": "Tokenize a multi-line text input and efficiently answer search queries 
  for individual words and multi-word phrases.",
  "tokenization_rules": {
    "delimiter": "Split on any non-alphanumeric character (e.g., spaces, punctuation, symbols).",
    "case_sensitivity": "Case-insensitive (convert all tokens to lowercase during normalization).",
    "punctuation_handling": "Punctuation acts purely as a delimiter and is discarded during tokenization.",
    "line_boundary_behavior": "Token stream is continuous across line breaks unless explicitly constrained.",
    "example": {
      "raw_text": "Hello, world!",
      "normalized_tokens": ["hello", "world"]
    }
  },
  "query_types": [
    {
      "type": "WORD <word>",
      "description": "Count total occurrences of the target token within the normalized text stream.",
      "time_complexity": "O(1) lookup using a pre-computed frequency hash map."
    },
    {
      "type": "PHRASE <phrase>",
      "description": "Count occurrences where the phrase's normalized tokens appear consecutively and in exact order.",
      "matching_rule": "Matches adjacent tokens regardless of intervening original punctuation. Fails if another token lies between phrase words.",
      "examples": [
        {
          "query": "PHRASE hello world",
          "matches": "Hello, world!",
          "matched": true
        },
        {
          "query": "PHRASE world hello",
          "matches": "world: hello.",
          "matched": true
        }
      ]
    }
  ],
  "implementation_approaches": [
    {
      "approach": "Direct Linear Scan",
      "steps": [
        "Tokenize and normalize all lines into a flat list of text tokens.",
        "For WORD queries, count exact token matches in the list.",
        "For PHRASE queries, tokenize the phrase and run a sliding-window scan across the text tokens."
      ],
      "time_complexity": "O(T * P) per phrase query (where T = total text tokens, P = phrase tokens).",
      "space_complexity": "O(T) space to store the token sequence."
    },
    {
      "approach": "Indexed Preprocessing (Optimized for High Query Volume)",
      "steps": [
        "Build a frequency hash map for WORD queries to enable O(1) lookups.",
        "Build an inverted index mapping each word to a list of its token positions in the text.",
        "For PHRASE queries, intersect position lists of constituent tokens to find adjacent index sequences."
      ],
      "time_complexity": "O(1) for WORD queries; significantly faster than O(T * P) for PHRASE queries.",
      "space_complexity": "O(T) space for inverted index positional postings."
    }
  ]
}
"""

# Solution 1: Preprocessed Frequency Map + Sliding Window (Direct Approach)This approach tokenizes 
# the multi-line text into a flat stream of normalized tokens, builds a frequency map for $O(1)$ WORD lookups, 
# and uses a sliding window for PHRASE lookups.

import re
from collections import Counter

class TextSearchEngine:
    def __init__(self, raw_text: str):
        # Tokenize on non-alphanumeric characters and convert to lowercase
        self.tokens: list[str] = [token.lower() for token in re.split(r'[^a-zA-Z0-9]+', raw_text) if token]
        
        # Precompute frequencies for O(1) WORD queries
        self.word_freq: Counter[str] = Counter(self.tokens)

    def search_word(self, word: str) -> int:
        """O(1) lookup for single word counts."""
        normalized_word = word.lower()
        return self.word_freq.get(normalized_word, 0)

    def search_phrase(self, phrase: str) -> int:
        """
        O(T * P) scanning approach.
        T = len(self.tokens), P = len(phrase_tokens)
        """
        phrase_tokens = [t.lower() for t in re.split(r'[^a-zA-Z0-9]+', phrase) if t]
        
        if not phrase_tokens:
            return 0
        
        P = len(phrase_tokens)
        T = len(self.tokens)
        
        if P > T:
            return 0

        match_count = 0
        
        # Slide a window of length P across the text tokens
        for i in range(T - P + 1):
            if self.tokens[i:i + P] == phrase_tokens:
                match_count += 1
                
        return match_count


# Solution 2: Inverted Index with Positional Postings (Optimized Approach)When query volume is high, 
# scanning the entire token stream for every phrase takes $\mathcal{O}(T \times P)$.
# Instead, we can construct an Inverted Index mapping each word to its list of occurrences (positions). 
# To evaluate PHRASE w1 w2 ... wK, we intersect position lists to check where $pos(w_{i+1}) = pos(w_i) + 1$.

import re
from collections import defaultdict

class IndexedTextSearchEngine:
    def __init__(self, raw_text: str):
        # Tokenize text
        self.tokens: list[str] = [token.lower() for token in re.split(r'[^a-zA-Z0-9]+', raw_text) if token]
        
        # Positional Inverted Index: word -> list of positions in text
        self.index: dict[str, list[int]] = defaultdict(list)
        for pos, token in enumerate(self.tokens):
            self.index[token].append(pos)

    def search_word(self, word: str) -> int:
        """O(1) lookup returning total frequency."""
        normalized_word = word.lower()
        return len(self.index.get(normalized_word, []))

    def search_phrase(self, phrase: str) -> int:
        """
        Intersects position lists of constituent phrase words.
        Time Complexity: O(min(L1, L2, ...)) where L_i is the posting list length of word_i.
        """
        phrase_tokens = [t.lower() for t in re.split(r'[^a-zA-Z0-9]+', phrase) if t]
        if not phrase_tokens:
            return 0

        # If any word in phrase doesn't exist in text, count is 0
        for token in phrase_tokens:
            if token not in self.index:
                return 0

        # Start candidate starting positions with occurrences of the first word
        candidate_positions = set(self.index[phrase_tokens[0]])

        # Intersect expected next positions for each remaining word
        for offset, token in enumerate(phrase_tokens[1:], start=1):
            valid_next_positions = set()
            for pos in self.index[token]:
                # If pos matches (start_pos + offset), start_pos remains a candidate
                start_pos = pos - offset
                if start_pos in candidate_positions:
                    valid_next_positions.add(start_pos)
            
            candidate_positions = valid_next_positions
            if not candidate_positions:
                return 0

        return len(candidate_positions)

    # Performance ComparisonApproachSpaceWORD TimePHRASE TimeBest ForDirect Scan$\mathcal{O}(T)$$\mathcal{O}(1)$$\mathcal{O}(T \cdot P)$Small text / Few phrase queriesInverted Index$\mathcal{O}(T)$$\mathcal{O}(1)$$\mathcal{O}(K \log K)$Large text / High query volume
###################################

"""
Silent Sensor Detector (

SensorHealth

) asks you to track ping timestamps per sensor and answer whether a sensor is"STABLE" or "UNSTABLE"

at query timeT. The prompt available on your current page is incomplete: 
it does not define the rule for deciding stability. For example, stability might mean 
“received a ping within the last K seconds,” but the interviewer needs to specifyK

, whether the boundary counts, and how to handle a sensor with no pings. 
Don’t assume a rule until it’s clarified.Once the rule is defined, 
a reasonable starting design is to store each sensor’s ping timestamps. 
If pings arrive in timestamp order, you may only need the latest timestamp for a “recent ping” rule. 

If they can arrive out of order or queries concern historical times, you’ll need more history, 
typically sorted per sensor.

Clarify these details with the interviewer:

What exactly makes a sensor stable?
Can pings arrive out of timestamp order?
Can query times move backward?
What should happen for an unknown sensor?
What are the expected scale and memory limits? 

{
  "title": "Silent Sensor Detector (SensorHealth)",
  "description": "Track ping timestamps for each sensor and determine whether a given sensor is 
  'STABLE' or 'UNSTABLE' at a specific query time T.",
  "status": "Incomplete Problem Definition — System requires clarification on the exact stability rule 
  and operating parameters before final implementation.",
  "core_functionality": {
    "primary_task": "Ingest sensor ping events and answer stability health checks at arbitrary time points.",
    "output_states": [
      "STABLE",
      "UNSTABLE"
    ]
  },
  "implementation_design": {
    "latest_ping_only": {
      "use_case": "Pings arrive strictly in chronological order and query targets current time.",
      "data_structure": "Hash Map mapping SensorID to its single latest timestamp.",
      "space_complexity": "O(1) space per sensor."
    },
    "historical_timeseries": {
      "use_case": "Pings arrive out of order or queries check historical timestamps.",
      "data_structure": "Hash Map mapping SensorID to a sorted list/deque of timestamps.",
      "query_method": "Binary search (e.g., lower_bound / bisect) to find the most recent ping prior to query time T.",
      "space_complexity": "O(P) where P is total retained ping history."
    }
  },
  "clarification_checklist": [
    "Stability Criteria: What exact mathematical condition defines 'STABLE'? (e.g., receiving at least 1 ping in the window [T - K, T], or a minimum frequency within window K?)",
    "Boundary Conditions: Is the threshold window inclusive or exclusive of boundaries? How should sensors with zero recorded pings be categorized?",
    "Event Ordering: Can ping events arrive out of chronological order?",
    "Query Patterns: Are queries strictly real-time and monotonic, or can query time T jump backwards to check historical health?",
    "Unknown Entities: How should the system respond to queries for an unrecognized SensorID?",
    "Scale & Constraints: What are the expected bounds on number of sensors, total pings, query throughput, and available memory?"
  ]
}
"""

import bisect
from collections import defaultdict
from typing import Dict, List, Literal

Status = Literal["STABLE", "UNSTABLE"]


class SensorHealth:
    """Tracks ping timestamps per sensor and determines stability health.

    Assumptions (configurable based on interviewer feedback):
    - Default stability rule: Sensor is STABLE if it received at least 1 ping in [T - K, T].
    - Window K default: 10 seconds.
    - Inclusive boundaries: [T - K, T].
    - Unknown/Unseen sensors: Return 'UNSTABLE'.
    - Handles out-of-order pings by maintaining sorted ping histories per sensor.
    """

    def __init__(self, window_k: float = 10.0):
        self.window_k = window_k
        # Maps sensor_id -> sorted list of ping timestamps
        self.pings: Dict[str, List[float]] = defaultdict(list)

    def record_ping(self, sensor_id: str, timestamp: float) -> None:
        """Records a ping timestamp for a sensor.

        Handles both in-order and out-of-order ping arrivals in O(log P) time.
        """
        history = self.pings[sensor_id]
        # Maintain sorted order using binary search insertion
        bisect.insort(history, timestamp)

    def is_stable(self, sensor_id: str, query_time: float) -> Status:
        """Determines if a sensor is STABLE or UNSTABLE at a given query time T.

        Calculates whether a ping exists in the range [query_time - K, query_time].

        Time Complexity: O(log P) where P is the number of pings for the sensor.
        Space Complexity: O(P) total stored pings.
        """
        if sensor_id not in self.pings or not self.pings[sensor_id]:
            return "UNSTABLE"

        history = self.pings[sensor_id]

        # Find the rightmost ping that occurred at or before query_time
        # bisect_right returns the insertion index for query_time
        idx = bisect.bisect_right(history, query_time)

        # If idx == 0, there are no pings at or before query_time
        if idx == 0:
            return "UNSTABLE"

        # The latest ping at or before query_time
        latest_ping_before_t = history[idx - 1]

        # Check if the latest ping falls within the inclusive window [T - K, T]
        if query_time - self.window_k <= latest_ping_before_t <= query_time:
            return "STABLE"

        return "UNSTABLE"


# Example Usage & Verification
if __name__ == "__main__":
    detector = SensorHealth(window_k=10.0)

    # Ingesting out-of-order pings for sensor "S1"
    detector.record_ping("S1", 100.0)
    detector.record_ping("S1", 115.0)
    detector.record_ping("S1", 105.0)  # Arrived out of order

    # Queries
    print(detector.is_stable("S1", 108.0))  # "STABLE"   (Ping at 105.0 is in range [98, 108])
    print(detector.is_stable("S1", 120.0))  # "STABLE"   (Ping at 115.0 is in range [110, 120])
    print(detector.is_stable("S1", 130.0))  # "UNSTABLE" (Latest ping was 115.0, outside [120, 130])
    print(detector.is_stable("S1", 90.0))   # "UNSTABLE" (No pings prior to T=90)
    print(detector.is_stable("UNKNOWN", 100.0))  # "UNSTABLE" (Unknown sensor)

    # Alternative: O(1) Space Optimization (Strict In-Order Pings)
    # If the interviewer clarifies that pings strictly arrive in chronological order and 
    # queries only check the current time $T$, you can optimize memory to $O(1)$ per sensor:

###################################

"""
The problem shown on your current page is “Retrieve Token List.” Its description is brief: given a
create_time
and a token, implement a function that retrieves the corresponding token and the current token list.

That description doesn’t explain the data model or rules, so the exact expected behavior isn’t clear. Before designing the implementation, clarify:

Is
create_time
a timestamp, a unique ID, or a sort key?
Can multiple tokens have the same
create_time
?
Does “current token list” mean all tokens, or only active/unexpired ones?
What should happen if the requested token or timestamp does not exist?
Do updates or deletions need to be supported?
A likely starting point is a collection of token records, with a lookup structure keyed by whatever uniquely identifies a record. If the list must be ordered by
create_time
, maintain that ordering explicitly; don’t assume timestamps are unique unless the prompt says so.

================================
"""

import bisect
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass(frozen=True)
class TokenRecord:
    token: str
    create_time: float
    ttl: Optional[float] = None  # Optional Time-To-Live in seconds

    def is_active(self, current_time: float) -> bool:
        if self.ttl is None:
            return True
        return (self.create_time + self.ttl) > current_time


class TokenManager:
    """Manages token records with fast lookup by token ID and ordered retrieval by create_time.

    Assumptions (configurable based on interviewer feedback):
    - create_time is a numerical timestamp (e.g., epoch time).
    - Multiple tokens CAN share the same create_time (handled via tuple sorting: (create_time, token)).
    - 'Current token list' returns active tokens sorted by create_time.
    - Non-existent token lookups return None.
    - Soft-deletions are supported via explicit revoking.
    """

    def __init__(self, default_ttl: Optional[float] = None):
        self.default_ttl = default_ttl
        # Fast lookup by token string -> TokenRecord
        self.tokens_by_id: Dict[str, TokenRecord] = {}
        # Revoked token set for soft deletion support
        self.revoked_tokens: set[str] = set()
        # Sorted list of tuples: (create_time, token_id) to handle non-unique timestamps
        self.ordered_tokens: List[Tuple[float, str]] = []

    def create_token(
        self,
        token: str,
        create_time: float,
        ttl: Optional[float] = None,
    ) -> TokenRecord:
        """Creates and stores a new token record.

        Time Complexity: O(N) due to insertion into sorted list (or O(log N) + O(1) if amortized).
        """
        ttl_to_use = ttl if ttl is not None else self.default_ttl
        record = TokenRecord(token=token, create_time=create_time, ttl=ttl_to_use)

        self.tokens_by_id[token] = record

        # Maintain sorted order by (create_time, token) to handle identical timestamps deterministically
        item = (create_time, token)
        bisect.insort(self.ordered_tokens, item)

        return record

    def get_token(self, token: str) -> Optional[TokenRecord]:
        """Retrieves a single token record by its token string.

        Returns None if not found or if the token was revoked.
        """
        if token in self.revoked_tokens:
            return None
        return self.tokens_by_id.get(token)

    def get_current_token_list(
        self,
        current_time: float,
        include_expired: bool = False,
    ) -> List[TokenRecord]:
        """Retrieves the list of tokens ordered by create_time.

        Parameters:
        - current_time: Timestamp used to calculate active/unexpired state.
        - include_expired: If True, returns all historical non-revoked tokens.
        """
        result: List[TokenRecord] = []

        for _, token_id in self.ordered_tokens:
            if token_id in self.revoked_tokens:
                continue

            record = self.tokens_by_id[token_id]
            if include_expired or record.is_active(current_time):
                result.append(record)

        return result

    def revoke_token(self, token: str) -> bool:
        """Revokes (deletes) a token from active use.

        Returns True if successful, False if token did not exist.
        """
        if token in self.tokens_by_id:
            self.revoked_tokens.add(token)
            return True
        return False


# Example Usage & Verification
if __name__ == "__main__":
    manager = TokenManager(default_ttl=3600.0)  # 1 hour default TTL

    # 1. Create tokens (including duplicate create_time)
    manager.create_token("token_a", create_time=1000.0, ttl=300.0)
    manager.create_token("token_b", create_time=1000.0, ttl=100.0)  # Same timestamp
    manager.create_token("token_c", create_time=1200.0, ttl=600.0)

    # 2. Retrieve single token O(1)
    record_a = manager.get_token("token_a")
    print(f"Retrieved token_a: {record_a}")

    # 3. Retrieve active token list at current_time = 1150.0
    # token_b created at 1000 with TTL 100 expired at 1100 -> Should be excluded
    active_tokens = manager.get_current_token_list(current_time=1150.0)
    print("\nActive tokens at t=1150:")
    for t in active_tokens:
        print(f"  - {t.token} (created at {t.create_time})")

    # 4. Revoke a token and check list again
    manager.revoke_token("token_a")
    active_after_revoke = manager.get_current_token_list(current_time=1150.0)
    print("\nActive tokens after revoking token_a:")
    for t in active_after_revoke:
        print(f"  - {t.token} (created at {t.create_time})")

'''
{
  "key_design_tradeoffs_and_clarifications": [
    {
      "scenario_or_aspect": "Duplicate Timestamps",
      "recommendation": "Treat (create_time, token_id) as a composite key.",
      "solution_approach": "bisect.insort on tuples maintains deterministic order."
    },
    {
      "scenario_or_aspect": "Lookup Performance",
      "recommendation": "Hash table lookup by token ID.",
      "solution_approach": "self.tokens_by_id provides O(1) retrieval."
    },
    {
      "scenario_or_aspect": "Expiration (TTL)",
      "recommendation": "Filter dynamically at query time based on current_time.",
      "solution_approach": "TokenRecord.is_active(current_time) condition."
    },
    {
      "scenario_or_aspect": "Deletions / Revocations",
      "recommendation": "Soft-deletion using a revoked lookup set.",
      "solution_approach": "self.revoked_tokens keeps historical list clean without expensive array re-indexing."
    }
  ]
}
'''



"""
===============================================================================
PROBLEM STATEMENT: TOKEN MANAGEMENT SYSTEM (Confluent)
===============================================================================

Design a token management system that supports generating, validating, and 
retrieving API or authentication tokens based on creation timestamps and 
expiration rules.

-------------------------------------------------------------------------------
DATA MODEL & SPECIFICATIONS
-------------------------------------------------------------------------------
Each token record consists of:
  • token (str)       : Unique identifier for the token.
  • create_time (int) : Creation timestamp in seconds or milliseconds.
  • ttl (int)         : Time duration (time-to-live) in seconds for which 
                        the token remains valid.

-------------------------------------------------------------------------------
KEY REQUIREMENTS & API SPECIFICATIONS
-------------------------------------------------------------------------------
1. generate(tokenId, createTime)
   - Registers a new token into the system associated with its creation timestamp.

2. renew(tokenId, currentTime)
   - Renews an existing token's expiration window if it has not already expired.

3. retrieveTokenList(currentTime)  OR  retrieve(createTime, tokenId)
   - Returns all currently active (unexpired) tokens at currentTime.
   - Returns the list ordered chronologically by create_time 
     (lexicographically by tokenId as a tie-breaker).
   - Automatically ignores/prunes expired tokens (where create_time + ttl <= currentTime).

-------------------------------------------------------------------------------
STANDARD CLARIFICATIONS
-------------------------------------------------------------------------------
• Is create_time unique?
  No. Multiple tokens can share the exact same timestamp. Order is maintained 
  by composite key (create_time, tokenId).

• What constitutes an active token?
  A token is active if: currentTime < create_time + ttl

• Optimal Data Structures:
  - HashMap / Dictionary for O(1) token lookup by tokenId.
  - SortedSet / Red-Black Tree / Doubly-Linked List to maintain ordering by 
    timestamp for efficient range queries and cleanup.
===============================================================================
"""

from sortedcontainers import SortedSet


class TokenRecord:
    def __init__(self, token_id: str, create_time: int, ttl: int):
        self.token_id = token_id
        self.create_time = create_time
        self.expiry_time = create_time + ttl

    def __lt__(self, other: "TokenRecord") -> bool:
        # Ordering: primary key = create_time, tie-breaker = token_id
        if self.create_time == other.create_time:
            return self.token_id < other.token_id
        return self.create_time < other.create_time

    def __repr__(self) -> str:
        return f"Token('{self.token_id}', create={self.create_time}, expiry={self.expiry_time})"


class TokenManager:
    def __init__(self, default_ttl: int):
        self.default_ttl = default_ttl
        self.tokens: dict[str, TokenRecord] = {}
        self.active_tokens: SortedSet[TokenRecord] = SortedSet()

    def _cleanup_expired(self, current_time: int) -> None:
        """Removes all expired tokens up to current_time."""
        expired_ids = [
            record.token_id
            for record in self.tokens.values()
            if record.expiry_time <= current_time
        ]

        for tid in expired_ids:
            record = self.tokens.pop(tid)
            self.active_tokens.discard(record) # method of sorted set to remove

    def generate(self, token_id: str, create_time: int) -> bool:
        """Registers a new token. Returns False if token_id already exists."""
        if token_id in self.tokens:
            return False

        record = TokenRecord(token_id, create_time, self.default_ttl)
        self.tokens[token_id] = record

        self.active_tokens.add(record)
        return True

    def renew(self, token_id: str, current_time: int) -> bool:
        """
        Renews an unexpired token by resetting its expiry window.
        Returns False if token does not exist or has expired.
        """
        self._cleanup_expired(current_time)

        if token_id not in self.tokens:
            return False

        record = self.tokens[token_id]
        if record.expiry_time <= current_time:
            return False

        self.active_tokens.remove(record)
        record.expiry_time = current_time + self.default_ttl
        self.active_tokens.add(record)
        return True

    def retrieve_token_list(self, current_time: int) -> list[str]:
        """Returns active token IDs ordered chronologically by create_time."""
        self._cleanup_expired(current_time)
        return [record.token_id for record in self.active_tokens]

    def retrieve(self, token_id: str, current_time: int) -> TokenRecord | None:
        """Retrieves a single active token record, or None if expired/nonexistent."""
        self._cleanup_expired(current_time)
        return self.tokens.get(token_id)


# =============================================================================
# DEMO & TESTING
# =============================================================================
if __name__ == "__main__":
    tm = TokenManager(default_ttl=10)

    # 1. Generate tokens
    tm.generate("token_A", create_time=100)
    tm.generate("token_B", create_time=105)
    tm.generate("token_C", create_time=100)  # Same create_time as A

    print("Active at t=108:", tm.retrieve_token_list(current_time=108))
    # Output: ['token_A', 'token_C', 'token_B']

    # 2. Renew token_A at t=108 (expiry shifts to 108 + 10 = 118)
    tm.renew("token_A", current_time=108)

    # 3. Check active list at t=112 (B and C expired at t=110 & t=115, A active until 118)
    print("Active at t=112:", tm.retrieve_token_list(current_time=112))
    # Output: ['token_A']


###################################

"""

Message Logger asks you to implement

In this Confluent interview question, you are tasked with designing an 
efficient notification filtering utility that prevents duplicate log entries 
from appearing within a specific temporal window. 
The exercise tests your ability to manage state and apply appropriate time-based thresholds 
using optimal data structures. 
Review the complete problem walkthrough and expert reference solution by subscribing to our platform.

shouldPrintMessage(timestamp, message)

. It should return true when the message may be printed, 
and false when that same message was printed too recently.
The rule is per message: printing one message does not affect whether a different message can print.

Example with a 10-second window

(0, "order received")
→true
; it has not been printed before.
(1, "order received")
→false
; only 1 second has passed.
(2, "shipment sent")
→true
; this is a different message.
(11, "order received")
→true
; 11 seconds have passed since its previous print.
Efficient approach

Keep a hash map from each message to the timestamp when it was last printed. When a request arrives:

If the message isn’t in the map, allow it and record the timestamp.
Otherwise, compare the new timestamp with its recorded timestamp.
If at least 10 seconds have passed, allow it and update the recorded timestamp.
Otherwise, reject it and leave the recorded timestamp unchanged.
For example, if a message was printed at time

0

, a request at time10

is allowed under the usual interpretation of a 10-second cooldown:10 - 0 >= 10

.Each request takes O(1) average time; the map uses space proportional to the number of distinct messages seen. Because timestamps arrive chronologically, you can optionally remove old map entries to reclaim memory, but that cleanup isn’t needed for correctness. 
{
  "title": "Message Logger (Rate Limiter / Cooldown)",
  "description": "Implement a method `shouldPrintMessage(timestamp, message)` that determines whether a given message should be printed '
  based on a rate-limiting cooldown window (e.g., 10 seconds). The limit applies independently per distinct message.",
  "interface": {
    "method": "shouldPrintMessage(timestamp, message)",
    "inputs": {
      "timestamp": "An integer representing the current time in seconds.",
      "message": "A string representing the log message content."
    },
    "output": "Boolean (true if the message is permitted to print; false otherwise)."
  },
  "rules": {
    "cooldown_window": 10,
    "scope": "Per-message (printing one message does not affect the rate limit or availability of a different message).",
    "timestamp_ordering": "Timestamps arrive in strictly non-decreasing / chronological order."
  },
  "example_trace": [
    {
      "timestamp": 0,
      "message": "order received",
      "allowed": true,
      "reason": "First time encountering this message."
    },
    {
      "timestamp": 1,
      "message": "order received",
      "allowed": false,
      "reason": "Only 1 second has elapsed since last print (1 - 0 < 10)."
    },
    {
      "timestamp": 2,
      "message": "shipment sent",
      "allowed": true,
      "reason": "Different message; tracked independently."
    },
    {
      "timestamp": 11,
      "message": "order received",
      "allowed": true,
      "reason": "11 seconds have elapsed since last print (11 - 0 >= 10); timestamp updated to 11."
    }
  ],
  "implementation_details": {
    "algorithm_steps": [
      "Maintain a Hash Map mapping each `message` string to its last printed `timestamp`.",
      "Upon receiving `(timestamp, message)` check if `message` exists in the map.",
      "If not present: record `map[message] = timestamp` and return `true`.",
      "If present: compare `timestamp - map[message]`.",
      "If elapsed time >= 10: update `map[message] = timestamp` and return `true`.",
      "Otherwise: leave `map[message]` unchanged and return `false`."
    ],
    "complexity": {
      "time_complexity": "O(1) average time per request.",
      "space_complexity": "O(M) space, where M is the number of distinct messages seen."
    },
    "memory_optimization": "Since timestamps arrive chronologically, stale entries (where `current_timestamp - recorded_timestamp >= 10`) can be periodically purged using a FIFO queue to prevent unbounded memory growth."
  }
}
"""
class Logger:

    def __init__(self):
        self.msg_dict = {}

    def shouldPrintMessage(self, timestamp: int, message: str) -> bool:
        if message not in self.msg_dict:
            self.msg_dict[message] = timestamp
            return True
        
        if timestamp - self.msg_dict[message] >= 10:
            self.msg_dict[message] = timestamp
            return True
        
        return False

#     2. Memory-Optimized Approach (Queue + Set)
# In system design and higher-level coding interviews (like Confluent), follow-up questions often ask how to prevent memory leaks 
# when messages arrive infinitely. Since entries older than 10 seconds become irrelevant, 
# you can clean them up using a Queue (FIFO) paired with a Set.

from collections import deque

class Logger:

    def __init__(self):
        # Stores tuples of (timestamp, message)
        self.queue = deque()
        # Stores unique messages within the current 10-second window
        self.msg_set = set()

    def shouldPrintMessage(self, timestamp: int, message: str) -> bool:
        # 1. Clean up stale messages outside the 10-second window
        while self.queue and timestamp - self.queue[0][0] >= 10:
            old_timestamp, old_msg = self.queue.popleft()
            self.msg_set.remove(old_msg)

        # 2. Check if message was printed within the last 10 seconds
        if message in self.msg_set:
            return False

        # 3. Add message to tracking structures
        self.queue.append((timestamp, message))
        self.msg_set.add(message)
        return True
    
# Key Follow-Up Interview Questions
# If asked this in an interview, be prepared for these common extensions:

# Concurrent / Thread-Safe Logger: How would you handle multiple worker threads submitting log messages at once? 
# (Use a mutex/lock around the map, or use thread-safe ConcurrentHashMap structures).

# Distributed Rate Limiting: What if logs come from multiple servers where timestamps might arrive slightly out of order? 
# (Use Redis with sliding window logs or token buckets).

import threading
from collections import deque

class ThreadSafeLogger:
    def __init__(self, time_limit: int = 10):
        self.time_limit = time_limit
        self.lock = threading.Lock()
        
        # State tracked inside the locked critical section
        self.queue = deque()      # Keeps (timestamp, message) order
        self.msg_set = set()      # Quick O(1) lookup for active window

    def shouldPrintMessage(self, timestamp: int, message: str) -> bool:
        with self.lock:
            # 1. Evict messages outside the window
            while self.queue and timestamp - self.queue[0][0] >= self.time_limit:
                _, old_msg = self.queue.popleft()
                self.msg_set.remove(old_msg)

            # 2. Check presence
            if message in self.msg_set:
                return False

            # 3. Insert and permit
            self.queue.append((timestamp, message))
            self.msg_set.add(message)
            return True
###################################
"""
For “Minimum Value to Get Positive Step by Step Sum,” find the smallest positive starting value
x
such that every running total stays strictly greater than zero as you add the array values from left to right.

For
nums = [-3, 2, -3, 4, 2]
, the running totals starting from
x = 5
are: 5 → 2 → 4 → 1 → 5 → 7

They are all positive. Starting with
x = 4
would eventually produce 0, which is not positive, so
5 is the minimum.

Key observation
Let prefix be the sum of the array values seen so far, and track the smallest prefix sum, including the initial empty prefix 0
. Every running total is  x + prefix , so the condition is:  x + minPrefix > 0

Therefore:  x = max(1, 1 - minPrefix)

For the example, the minimum prefix sum is
-4, so x = max(1, 1 - (-4)) = 5
.

Scan the array once, updating the cumulative sum and its minimum. 
This takes O(n) time and O(1) extra space. The example explanation on your page appears inconsistent: 
the running totals for x = 5 are 2, 4, 1, 5, 7 , not 5, 2, -1, 3, 5. The stated answer 5 is still correct.

{
  "title": "Minimum Value to Get Positive Step by Step Sum",
  "description": "Find the smallest positive starting integer `x` (where x ≥ 1) 
  such that the cumulative running total stays strictly positive (greater than 0) after adding each element 
  of the array sequentially from left to right.",

  "formula": "x = max(1, 1 - minPrefix)",
  "key_observation": "For any step i, the running sum equals `x + prefix[i]`. To ensure `x + prefix[i] >= 1` for all i, 
  `x` must be at least `1 - minPrefix`, bounded below by 1 because `x` must be a positive starting value.",
  "algorithm": {
    "steps": [
      "Initialize `current_prefix = 0` and `min_prefix = 0`.",
      "Iterate through the array, updating `current_prefix += num`.",
      "At each step, track `min_prefix = min(min_prefix, current_prefix)`.",
      "Return `max(1, 1 - min_prefix)`."
    ],
    "time_complexity": "O(n) — single linear pass through the array.",
    "space_complexity": "O(1) — constant extra space."
  },
  "example_trace": {
    "input": {
      "nums": [-3, 2, -3, 4, 2]
    },
    "prefix_sums": [-3, -1, -4, 0, 2],
    "min_prefix": -4,
    "calculated_x": 5,
    "running_totals_with_x_equals_5": [
      {
        "step": 1,
        "num": -3,
        "running_total": 2
      },
      {
        "step": 2,
        "num": 2,
        "running_total": 4
      },
      {
        "step": 3,
        "num": -3,
        "running_total": 1
      },
      {
        "step": 4,
        "num": 4,
        "running_total": 5
      },
      {
        "step": 5,
        "num": 2,
        "running_total": 7
      }
    ]
  },
  "notes_and_corrections": "If x = 4 were chosen, step 3 (-3) would produce a running total of 0 (which is not strictly positive). 
  Thus, x = 5 is the minimal valid positive starting value."
}
"""
from typing import List

def minStartValue(nums: List[int]) -> int:
    prefix = 0
    min_prefix = 0              # include the empty prefix
    for num in nums:
        prefix += num
        min_prefix = min(min_prefix, prefix)
    return max(1, 1 - min_prefix)


print(minStartValue([-3, 2, -3, 4, 2]))   # 5
print(minStartValue([1, 2]))              # 1
print(minStartValue([1, -2, -3]))         # 5


###################################

"""
Get best price
Find the minimum total price to get all requested menu items using single items and discounted value meals.
Input: menu items with prices, value meal bundles with prices, and a desired item list; 
Output: best total price; Constraint: up to 3 unique items.

Real-world context: restaurant ordering app optimizing cost for a user’s meal.
From Confluent interviews; a coding interview problem and common interview question on bundle pricing.
"""

from functools import lru_cache

def get_best_price(menu: dict[str, float], meals: list[tuple[dict[str, int], float]], order: dict[str, int]) -> float:
    """
    Finds the minimum price to fulfill the order using menu items and meal bundles.
    
    :param menu: Dict mapping item names to single item prices.
                 e.g., {"burger": 5.0, "fries": 2.0, "soda": 1.5}
    :param meals: List of tuples (bundle_items_dict, bundle_price).
                  e.g., [({"burger": 1, "fries": 1}, 6.0)]
    :param order: Dict mapping requested item names to requested quantities.
                  e.g., {"burger": 2, "fries": 1}
    :return: Minimum total price.
    """
    # Filter out order items with 0 quantity
    requested_items = [item for item, qty in order.items() if qty > 0]
    if not requested_items:
        return 0.0
    
    item_to_idx = {item: i for i, item in enumerate(requested_items)}
    num_items = len(requested_items)
    
    target_tuple = tuple(order[item] for item in requested_items)
    
    # Standardize options into (quantity_vector_tuple, price)
    options = []
    
    # 1. Add single item options
    for item, idx in item_to_idx.items():
        if item in menu:
            vec = [0] * num_items
            vec[idx] = 1
            options.append((tuple(vec), menu[item]))
            
    # 2. Add value meal bundle options
    for meal_items, price in meals:
        vec = [0] * num_items
        is_relevant = False

        for item, qty in meal_items.items():
            if item in item_to_idx:
                vec[item_to_idx[item]] = qty
                if qty > 0:
                    is_relevant = True

        if is_relevant:
            options.append((tuple(vec), price))
            
    @lru_cache(maxsize=None)
    def min_cost(current_target: tuple[int, ...]) -> float:
        # If all requested item counts are met or exceeded
        if all(qty <= 0 for qty in current_target):
            return 0.0
        
        best = float('inf')
        
        for bundle_vec, price in options:
            # Create next state by subtracting bundle quantities
            next_target = tuple(max(0, current_target[i] - bundle_vec[i]) for i in range(num_items))
            
            # Avoid infinite loops if bundle contributes nothing to current target
            if next_target == current_target:
                continue
                
            cost = price + min_cost(next_target)
            best = min(best, cost)
            
        return best

    return min_cost(target_tuple)


# --- Example Usage ---
if __name__ == "__main__":
    single_menu = {
        "burger": 5.0,
        "fries": 2.5,
        "soda": 1.5
    }

    value_meals = [
        ({"burger": 1, "fries": 1}, 6.0),          # Combo A: Burger + Fries = $6.00
        ({"burger": 1, "fries": 1, "soda": 1}, 7.5) # Combo B: Full meal = $7.50
    ]

    requested_order = {
        "burger": 2,
        "fries": 1,
        "soda": 1
    }

    # Best strategy: 
    # 1x Combo B (Burger, Fries, Soda) = $7.50
    # 1x Single Burger = $5.00
    # Total = $12.50
    result = get_best_price(single_menu, value_meals, requested_order)
    print(f"Minimum Price: ${result:.2f}")


    # Answer without lru cache
    def get_best_price(menu: dict[str, float], meals: list[tuple[dict[str, int], float]], order: dict[str, int]) -> float:
    """
    Finds the minimum price to fulfill the order using menu items and meal bundles.
    Memoization is handled explicitly using a Python dictionary.
    
    :param menu: Dict mapping item names to single item prices.
                 e.g., {"burger": 5.0, "fries": 2.5, "soda": 1.5}
    :param meals: List of tuples (bundle_items_dict, bundle_price).
                  e.g., [({"burger": 1, "fries": 1}, 6.0)]
    :param order: Dict mapping requested item names to requested quantities.
                  e.g., {"burger": 2, "fries": 1, "soda": 1}
    :return: Minimum total price.
    """
    # Filter out requested items with 0 quantity
    requested_items = [item for item, qty in order.items() if qty > 0]
    if not requested_items:
        return 0.0
    
    item_to_idx = {item: i for i, item in enumerate(requested_items)}
    num_items = len(requested_items)
    
    target_tuple = tuple(order[item] for item in requested_items)
    
    # Standardize options into (quantity_vector_tuple, price)
    options = []
    
    # 1. Add single item options
    for item, idx in item_to_idx.items():
        if item in menu:
            vec = [0] * num_items
            vec[idx] = 1
            options.append((tuple(vec), menu[item]))
            
    # 2. Add value meal bundle options
    for meal_items, price in meals:
        vec = [0] * num_items
        is_relevant = False
        for item, qty in meal_items.items():
            if item in item_to_idx:
                vec[item_to_idx[item]] = qty
                if qty > 0:
                    is_relevant = True
        if is_relevant:
            options.append((tuple(vec), price))
            
    # Dictionary to store cached state results: target_tuple -> min_cost
    memo = {}

    def min_cost(current_target: tuple[int, ...]) -> float:
        # Base case: All item demands are satisfied
        if all(qty <= 0 for qty in current_target):
            return 0.0
        
        # Check memo dictionary before computing
        if current_target in memo:
            return memo[current_target]
        
        best = float('inf')
        
        for bundle_vec, price in options:
            # Create next state by subtracting bundle quantities
            next_target = tuple(max(0, current_target[i] - bundle_vec[i]) for i in range(num_items))
            
            # Avoid infinite recursion if bundle adds no useful items
            if next_target == current_target:
                continue
                
            cost = price + min_cost(next_target)
            best = min(best, cost)
            
        # Cache result in memo dictionary
        memo[current_target] = best
        return best

    return min_cost(target_tuple)


# --- Example Usage ---
if __name__ == "__main__":
    single_menu = {
        "burger": 5.0,
        "fries": 2.5,
        "soda": 1.5
    }

    value_meals = [
        ({"burger": 1, "fries": 1}, 6.0),          # Combo A: Burger + Fries = $6.00
        ({"burger": 1, "fries": 1, "soda": 1}, 7.5) # Combo B: Full meal = $7.50
    ]

    requested_order = {
        "burger": 2,
        "fries": 1,
        "soda": 1
    }

    result = get_best_price(single_menu, value_meals, requested_order)
    print(f"Minimum Price: ${result:.2f}")  # Output: Minimum Price: $12.50
###################################

"""
Function Overloading Matching with Variable Arguments Support

The Function Overloading Matching with Variable Arguments Support prompt asks you to register function signatures, 
then return every function whose signature matches a supplied list of argument types.

A function is represented by its name, a vector of parameter types, and an isCard flag. 
In Part 1, isCard is false: a function matches only when its parameter list has the same length as the input 
and every type matches in the same position. So a function with {"Integer", "Boolean"} matches that exact argument list, but not
{"Integer"}
.

In Part 2, isCard == true means the final parameter is variadic: it can match zero or more additional arguments of that type. 
For example, {"Integer"} with isCard == true can match {"Integer"} and {"Integer", "Integer", "Integer"}. 
The fixed parameters must still match exactly; each extra argument must match the variadic parameter’s type. 
Return all matches, since distinct functions may have identical signatures.

A straightforward implementation checks each registered function against the input: verify the fixed argument positions, 
then validate any extra arguments if it is variadic. With n functions and at most m arguments, 
this costs O(n · m) per lookup and uses O(n · m) storage for the registrations.

One detail to confirm from the full prompt: whether a variadic function with an empty parameter list is valid, 
since there would be no final parameter type to repeat. 
I couldn’t find this exact question in Confluent’s searchable materials; 
the available Confluent interview experiences may offer related context.

{
  "title": "Function Overloading Matching with Variable Arguments Support",
  "description": "Register function signatures and evaluate queries to return all registered functions 
  whose signature matches a supplied sequence of argument types.",

  "data_structures": {
    "Function": {
      "name": "String — Name of the function.",
      "parameter_types": "List<String> — Ordered vector/list of expected parameter type names.",
      "is_card": "Boolean — Indicates whether the final parameter is a variadic (wildcard) parameter."
    }
  },
  "matching_rules": {
    "part_1_exact_matching": {
      "condition": "is_card == false",
      "rules": [
        "Argument count must equal parameter count exactly (len(args) == len(params)).",
        "Every argument type must match the parameter type at the corresponding position."
      ],
      "example": {
        "parameters": ["Integer", "Boolean"],
        "matches": [["Integer", "Boolean"]],
        "non_matches": [["Integer"], ["Integer", "Boolean", "String"]]
      }
    },
    "part_2_variadic_matching": {
      "condition": "is_card == true",
      "rules": [
        "The first (len(params) - 1) arguments must match the corresponding non-variadic fixed parameters.",
        "The final parameter type can match zero or more additional trailing arguments.",
        "Every trailing argument beyond the fixed parameters must match the final variadic parameter's type."
      ],
      "example": {
        "parameters": ["Integer"],
        "is_card": true,
        "matches": [
          [],
          ["Integer"],
          ["Integer", "Integer", "Integer"]
        ],
        "non_matches": [["String"], ["Integer", "String"]]
      }
    }
  },
  "matching_behavior": {
    "return_type": "List of all matching functions (multiple distinct registered functions may match the same call signature)."
  },
  "complexity_analysis": {
    "per_lookup_time": "O(N * M), where N is the number of registered functions and M is the number of input argument types.",
    "space_complexity": "O(N * M) to store registered function parameter lists."
  },
  "clarification_notes": [
    "Verify whether a function with is_card == true and an empty parameter list (len(params) == 0) is valid, as there is no final parameter type specified for variadic matching."
  ]
}

################# Concise version

Build a registry of function signatures, then answer queries: given a list of argument types, 
return all registered functions that could be called with those arguments.

Each function has a name, parameter_types (list of strings), and is_card (variadic flag).

Matching rules

Exact (is_card = False): len(args) == len(params) and args[i] == params[i] for every i.
Variadic (is_card = True): the last parameter type T can repeat zero or more times.
Fixed part = params[:-1], must match the first len(params)-1 args exactly.
Every remaining arg must equal T.
Needs len(args) >= len(params) - 1.
Return every match (different functions may share a signature, so don't dedupe or stop at the first).

Edge case to clarify: variadic with empty params has no type to repeat. 
The safest reading is "invalid", or it matches only an empty arg list. I treat it as matching only [].
"""

# Semantics
# Non-variadic: the argument count must equal the parameter count, and the types must match position by position.
# Variadic: the last parameter is the repeatable type and the ones before it are fixed. 
# So ["Integer"] with is_card=True means 0 fixed parameters plus Integer*. The call needs at least len(params) - 1 arguments,
#  the fixed ones must match exactly, and every remaining argument must equal the last parameter type.
# Variadic with empty params: the spec leaves this open. I reject it at registration, because there is no type to repeat.
# Straightforward version: O(n·m) per lookup

from dataclasses import dataclass


@dataclass(frozen=True)
class Function:
    name: str
    params: tuple
    is_card: bool = False


class FunctionRegistry:
    def __init__(self):
        self.functions = []

    def register(self, name, params, is_card=False):
        if is_card and not params:
            raise ValueError("variadic function needs at least one parameter type")
        self.functions.append(Function(name, tuple(params), is_card))

    def match(self, args):
        return [f for f in self.functions if self._matches(f, args)]

    @staticmethod
    def _matches(f, args):
        if not f.is_card:
            return list(f.params) == list(args)

        fixed, var_type = f.params[:-1], f.params[-1]
        if len(args) < len(fixed):
            return False
        if tuple(args[:len(fixed)]) != fixed:
            return False
        return all(a == var_type for a in args[len(fixed):])
# Faster version: lookups independent of n

# Hash the signatures, so a query never scans all registered functions.

# Exact functions go in exact[tuple(params)].
# Variadic functions go in var_typed[(fixed_prefix, var_type)] and in var_any[fixed_prefix], 
# which handles the zero-extra-arguments case.

# For a query with m args, the trailing run of identical types starting at position s is the only place a variadic tail can begin. 
# So only the split points k in [s, m] need to be checked.

from collections import defaultdict


class FastFunctionRegistry:
    def __init__(self):
        self._count = 0
        self.exact = defaultdict(list)       # params -> [(order, Function)]
        self.var_typed = defaultdict(list)   # (fixed, type) -> [(order, Function)]
        self.var_any = defaultdict(list)     # fixed -> [(order, Function)]

    def register(self, name, params, is_card=False):
        if is_card and not params:
            raise ValueError("variadic function needs at least one parameter type")
        f = Function(name, tuple(params), is_card)

        entry = (self._count, f)
        self._count += 1

        if not is_card:
            self.exact[f.params].append(entry)
        else:
            fixed, var_type = f.params[:-1], f.params[-1]
            self.var_typed[(fixed, var_type)].append(entry)
            self.var_any[fixed].append(entry)

    def match(self, args):
        args = tuple(args)
        m = len(args)
        found = list(self.exact.get(args, []))

        # Start of the trailing run of identical types
        s = m
        while s > 0 and args[s - 1] == args[m - 1]:
            s -= 1

        # Variadic with at least one extra argument: split at k, tail = args[k:]
        for k in range(s, m):
            found += self.var_typed.get((args[:k], args[k]), [])

        # Variadic with zero extra arguments: all args are fixed parameters
        found += self.var_any.get(args, [])

        found.sort(key=lambda e: e[0])       # keep registration order
        return [f for _, f in found]

# Per lookup this costs O(m²) worst case, because it builds tuple slices, and it does not depend on n. If you replace the dicts with a trie over the parameter types, it becomes O(m).

# Complexity
# 	Straightforward	Indexed
# Lookup	O(n·m)	about O(m²) (O(m) with a trie), independent of n
# Space	O(n·m)	O(n·m)                        

###################################

"""
The problem asks for a key-value store supporting:

Put(key, value)
: insert a key or update its value.
Get(key)
: return the value for a key.
GetAverage()
: return the average of all stored values.
GetMax()
: return the largest stored value.
The important complication is that updating a key can remove the current maximum. For example, if the values are
8
and
5
, then updating the key holding
8
to
2
means the new maximum is
5
. A simple variable holding the previous maximum cannot determine that efficiently by itself.

What’s straightforward
Use a hash map
key → value
for
Get
and key lookup in
Put
. Keep a running
sum
and the number of keys; on insert or update, adjust the sum by the change in value. This makes
GetAverage()
constant time.

The max requirement needs clarification
For arbitrary values and unrestricted updates, maintaining the exact maximum in worst-case O(1) is not generally achieved by just a hash map and a running maximum. You need to account for removing a value from the set of candidates when it is overwritten. A balanced search tree or heap with suitable bookkeeping can support updates and max retrieval efficiently, but typically not all in worst-case O(1).

So ask whether values are bounded (for example, integers in a small known range), whether updates are restricted, and whether “O(1)” means average/expected time. Those constraints determine a valid design. The exact question wasn’t found in Confluent’s searchable materials; 

"""
# Python Solution (Balanced BST approach using SortedDict)This provides deterministic $O(1)$ GetAverage and GetMax, with $O(\log N)$ Put.

from sortedcontainers import SortedDict

class MaxAverageKVStore:
    def __init__(self):
        self.key_to_val = {}
        self.val_counts = SortedDict()  # value -> count of keys having this value
        self.total_sum = 0.0
        self.count = 0

    def put(self, key: str, value: float) -> None:
        if key in self.key_to_val:
            old_val = self.key_to_val[key]
            # Adjust running sum
            self.total_sum += (value - old_val)
            
            # Decrement old value frequency
            self.val_counts[old_val] -= 1
            if self.val_counts[old_val] == 0:
                del self.val_counts[old_val]
        else:
            # New key insertion
            self.total_sum += value
            self.count += 1

        # Store new value
        self.key_to_val[key] = value
        self.val_counts[value] = self.val_counts.get(value, 0) + 1

    def get(self, key: str) -> float:
        if key not in self.key_to_val:
            raise KeyError("Key not found")
        return self.key_to_val[key]

    def get_average(self) -> float:
        if self.count == 0:
            raise ValueError("Store is empty")
        return self.total_sum / self.count

    def get_max(self) -> float:
        if not self.val_counts:
            raise ValueError("Store is empty")
        # peekitem(-1) gets the highest key in SortedDict in O(1) time
        max_val, _ = self.val_counts.peekitem(-1)
        return max_val


# Python Solution (Lazy Deletion Heap — Pure Standard Library)
# If external libraries like sortedcontainers aren't allowed in an interview, use a Max-Heap with Lazy Cleanup:

import heapq

class MaxAverageKVStoreHeap:
    def __init__(self):
        self.key_to_val = {}
        self.max_heap = []  # Stores (-value, key)
        self.total_sum = 0.0
        self.count = 0

    def put(self, key: str, value: float) -> None:
        if key in self.key_to_val:
            old_val = self.key_to_val[key]
            self.total_sum += (value - old_val)
        else:
            self.total_sum += value
            self.count += 1

        self.key_to_val[key] = value
        # Push to heap (using negative value for max-heap behavior)
        heapq.heappush(self.max_heap, (-value, key))

    def get(self, key: str) -> float:
        return self.key_to_val[key]

    def get_average(self) -> float:
        if self.count == 0:
            raise ValueError("Store is empty")
        return self.total_sum / self.count

    def get_max(self) -> float:
        # Lazy eviction: discard stale entries at top of heap
        while self.max_heap:
            neg_val, key = self.max_heap[0]
            curr_val = -neg_val
            # Check if this heap entry matches current state in hash map
            if key in self.key_to_val and self.key_to_val[key] == curr_val:
                return curr_val
            heapq.heappop(self.max_heap)
            
        raise ValueError("Store is empty")

'''
Here is the $O(1)$ solution using a Hash Map, a Doubly Linked List (DLL) ordered by value, and a Node Lookup Map.
By keeping nodes sorted by value in the DLL, GetMax() is strictly $O(1)$ (reading the tail node). 
Updating a key involves unlinking its node and inserting it into its new sorted position.
Data Structure Architecturekey_map: Maps key $\rightarrow$ DLLNode for $O(1)$ node lookups.head / tail: 
Sentinel nodes maintaining the list in ascending value order (head = minimum value, tail = maximum value).total_sum & count: 
Maintain running aggregates for $O(1)$ GetAverage().
'''

class Node:
    def __init__(self, key: str = "", val: float = 0.0):
        self.key = key
        self.val = val
        self.prev = None
        self.next = None


class MaxAverageKVStoreDLL:
    def __init__(self):
        self.key_map = {}  # key -> Node
        self.total_sum = 0.0
        self.count = 0

        # Dummy sentinel nodes for sorted DLL (head: min, tail: max)
        self.head = Node()
        self.tail = Node()
        self.head.next = self.tail
        self.tail.prev = self.head

    def _unlink(self, node: Node) -> None:
        """Removes a node from its current position in O(1) time."""
        node.prev.next = node.next
        node.next.prev = node.prev

    def _insert_sorted(self, node: Node) -> None:
        """Inserts node into its correct position to maintain ascending value order."""
        # Search backward from tail since updates/new entries tend to be near the top
        curr = self.tail.prev
        while curr != self.head and curr.val > node.val:
            curr = curr.prev

        # Insert 'node' right after 'curr'
        node.next = curr.next
        node.prev = curr
        curr.next.prev = node
        curr.next = node

    def put(self, key: str, value: float) -> None:
        if key in self.key_map:
            # Update existing key
            node = self.key_map[key]
            self.total_sum += (value - node.val)
            node.val = value
            
            # Reposition node in DLL
            self._unlink(node)
            self._insert_sorted(node)
        else:
            # Insert new key
            node = Node(key, value)
            self.key_map[key] = node
            self.total_sum += value
            self.count += 1
            
            self._insert_sorted(node)

    def get(self, key: str) -> float:
        if key not in self.key_map:
            raise KeyError(f"Key '{key}' not found.")
        return self.key_map[key].val

    def get_average(self) -> float:
        if self.count == 0:
            raise ValueError("Store is empty.")
        return self.total_sum / self.count

    def get_max(self) -> float:
        if self.count == 0:
            raise ValueError("Store is empty.")
        # The maximum node is always immediately before the tail sentinel
        return self.tail.prev.val


# --- Example Usage ---
if __name__ == "__main__":
    kv = MaxAverageKVStoreDLL()
    
    kv.put("A", 5.0)
    kv.put("B", 8.0)
    print("Max:", kv.get_max())       # Output: 8.0
    print("Avg:", kv.get_average())   # Output: 6.5

    # Updating key "B" (holding 8.0) down to 2.0
    kv.put("B", 2.0)
    print("New Max:", kv.get_max())   # Output: 5.0 (A becomes the new max)
    print("New Avg:", kv.get_average()) # Output: 3.5    

'''
Get(key): $O(1)$ direct hash map lookup.GetAverage(): $O(1)$ scalar arithmetic (total_sum / count).GetMax(): $O(1)$ 
accessing tail.prev.val.Put(key, val):Unlinking node: $O(1)$.
Linear search for insertion position: $O(N)$ worst-case (if values are arbitrary), 
$O(1)$ best-case (if inserted values are sequentially near existing values).
'''


'''
To achieve strict $O(1)$ time complexity across ALL operations (Put, Get, GetAverage, and GetMax), 
we combine a Hash Map with a Bucket-based Doubly Linked List (similar to the All O(1) Data Structure / LFU Cache).
Key Insight & AssumptionsFor arbitrary floating-point numbers or unbound values, maintaining a sorted order in $O(1)$ worst-case 
is theoretically impossible (it would violate the $O(N \log N)$ sorting lower bound).
However, in real-world systems (and standard coding interviews targeting $O(1)$), 
values are either integers bounded within a range or discrete quantities/frequencies.
By grouping keys that share the exact same value into Value Buckets, we can organize the buckets in a Doubly Linked List and maintain direct pointer mapping for $O(1)$ bucket jumps.Data Structure Designkey_map (key -> (val, node_ptr)):Maps each key to its current value and its location inside a ValueBucket.bucket_map (val -> ValueBucket):Maps each distinct value directly to its ValueBucket node in $O(1)$ time.ValueBucket (Doubly Linked List Node):Holds value: The numerical value shared by all keys in this bucket.Holds keys: A hash set of keys that currently have this value.Holds prev / next: Pointers linking to smaller/larger value buckets.head & tail Sentinels:head: Lowest value bucket.tail: Highest value bucket. tail.prev.value gives GetMax() in $O(1)$ time.
'''


###################################

"""
https://www.glassdoor.ca/Interview/Confluent-Software-Engineer-Interview-Questions-EI_IE1048428.0,9_KO10,27_IP4.htm

Interview

1. Regex pattern matching 
2. Java concurrency using threads type problem 
3.Matrix path finding problem with weigths in each cells 
4. Behaviour style round with hiring manager Be well prepared with leetcode medium and hard problems. 
Interviewers were very friendly overall. Looks like a good company.

Interview questions [1]

Question 1

Regex pattern matching along with java concurrenty

====
Interview questions [1]

Question 1

1. Create a data structure that can perform CRUD operations on data coming in a time period.


==============
Interview questions [1]

Question 1

Similar to wildcard pattern matching using Dynamic Programming.



"""


###################################


"""
https://leetcode.com/discuss/post/1878821/confluent-onsite-search-phrase-in-docume-1yn1/

You are given a list of documents with id and text.
Eg :-
DocId, Text
1, "Cloud computing is the on-demand availability of computer system resources."
2, "One integrated service for metrics uptime cloud monitoring dashboards and alerts reduces time spent navigating between systems."
3, "Monitor entire cloud infrastructure, whether in the cloud computing is or in virtualized data centers."

Search a given phrase in all the documents in a efficient manner. Assume that you have more than 1 million docs.
Eg :-
search("cloud") >> This should output [1,2,3]
search("cloud monitoring") >> This should output [2]
search("Cloud computing is") >> This should output [1,3]
"""

import re
from collections import defaultdict


class PhraseSearchIndex:
    def __init__(self):
        # term -> {doc_id -> [positions]}
        self.index = defaultdict(lambda: defaultdict(list))

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        return re.findall(r"\w+", text.lower())

    def add_document(self, doc_id: int, text: str) -> None:
        for pos, term in enumerate(self._tokenize(text)):
            self.index[term][doc_id].append(pos)  # positions come out sorted

    def search(self, phrase: str) -> list[int]:
        terms = self._tokenize(phrase)
        if not terms:
            return []

        # Any missing term means no document can match
        postings = []
        for t in terms:
            if t not in self.index:
                return []
            postings.append(self.index[t])

        # Candidate docs: intersect starting from the rarest term (smallest list)
        smallest = min(postings, key=len)
        candidates = set(smallest)
        for p in postings:
            candidates &= p.keys()
            if not candidates:
                return []

        # Verify the words appear consecutively in each candidate doc
        result = []
        for doc_id in candidates:
            later = [set(p[doc_id]) for p in postings[1:]]  # O(1) lookups
            for start in postings[0][doc_id]:
                if all((start + i + 1) in later[i] for i in range(len(later))):
                    result.append(doc_id)
                    break
        return sorted(result)


# ---- Demo ----
docs = {
    1: "Cloud computing is the on-demand availability of computer system resources.",
    2: "One integrated service for metrics uptime cloud monitoring dashboards and alerts reduces time spent navigating between systems.",
    3: "Monitor entire cloud infrastructure, whether in the cloud computing is or in virtualized data centers.",
}

idx = PhraseSearchIndex()
for d_id, text in docs.items():
    idx.add_document(d_id, text)

print(idx.search("cloud"))               # [1, 2, 3]
print(idx.search("cloud monitoring"))    # [2]
print(idx.search("Cloud computing is"))  # [1, 3]
###################################

"""
"""

###################################

"""
"""


###################################
