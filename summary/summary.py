from bisect import bisect_right
from typing import List, Set, Dict

# =======================
a = [['z', 1, 3], ['t', 9, 9], ['a', 10, 10]]
a.sort(key=lambda x: x[0])

# ========= find and rfind return -1 if not find ||| and index raise ValueError ==========
>>> a = '/a/b/c'
>>> a.find('/')
0
>>> a.rfind('/')
4
>>> a.index('/')
0
>>> a.rindex('/')
4
>>> a.index('-')
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
ValueError: substring not found


values.sort(reverse=True)

# Sort by size (desc), then by name (asc)
matching_files.sort(key=lambda x: (-x[1], x[0]))

# Result: [['a', 10, 10], ['t', 9, 9], ['z', 1, 3]]

import heapq


# Min heap by default (first element)
heap = [(2, 'task2'), (1, 'task1'), (5, 'task5'), (3, 'task3')]
heapq.heapify(heap)
print(heapq.heappop(heap))  # Returns (1, 'task1')
print(heap[0])  # Peek at the smallest item

# Max heap by second element
data = [(2, 'task2'), (1, 'task1'), (5, 'task5'), (3, 'task3')]
# Use negative of the second element for max heap
max_heap = [(-ord(t[1][-1]), t) for t in data]  # Example: sort by last char of task name
heapq.heapify(max_heap)
print(heapq.heappop(max_heap)[1])  # Returns tuple with largest second element (by sort key)

a = [['z', 1, 3], ['t', 9, 9], ['a', 10, 10]]

n_items = heapq.nlargest(2, a, key=lambda x: (x[1]))
n_smaller_items = heapq.nsmallest(2, a, key=lambda x: (x[1]))

# >>> n_items
# [['a', 10, 10], ['t', 9, 9]]
# >>> n_smaller_items
# [['z', 1, 3], ['t', 9, 9]]


def get_balance_at(self, time_at):
    """Binary search to find the balance at a specific point in time."""
    target_t = int(time_at)
    # Find the last entry where entry.timestamp <= target_t
    idx = bisect_right(self.history, target_t, key=lambda x: x.timestamp) - 1 # need to minus 1 because bisect_right returns insertion point
    return self.history[idx].balance if idx >= 0 else 0


    # or if history is a tuple of 3 elements (timestamp, value, expiry):

    idx = bisect.bisect_right(history, (int(query_ts), float('inf'), float('inf')))

# ==============

spender_data = []
for acc in self.accounts.values():
    if acc.parent == acc: # Only roots hold the combined 'outgoing' total
        spender_data.append((acc.account_id, acc.outgoing))

top = heapq.nlargest(
    n, 
    spender_data, 
    key=lambda x: (x[1], [ord(c)*-1 for c in x[0]])
)
# =======================
# FileItem class and max heap example
import heapq



class FileItem:
    def __init__(self, file_size, expiry):
        self.file_size = file_size  # e.g., file size
        self.expiry = expiry

    def __lt__(self, other):
        # For max heap, reverse comparison (largest file_size first)
        return self.file_size > other.file_size

    def __repr__(self):
        return f"FileItem(file_size={self.file_size}, expiry={self.expiry})"

def get_top_n_files(file_items, n):
    """
    Returns the top N FileItem objects with the largest file_size.
    """
    # Use heapq.nlargest for efficiency
    return heapq.nlargest(n, file_items)

# Example usage:
if __name__ == "__main__":
    files = [FileItem(100, 10), FileItem(300, 20), FileItem(200, 15), FileItem(400, 5)]
    top_files = get_top_n_files(files, 2)
    print("Top 2 files by size:", top_files)

# ======================= SORTED DICT for timestamped balance history ============
from sortedcontainers import SortedDict

# Initialize the map
ts_map = SortedDict()

# Insert data
ts_map[10] = "Value A"
ts_map[20] = "Value B"
ts_map[30] = "Value C"

# Binary Search: Find the value at or before T=25
# bisect_right returns the index where 25 would be inserted
idx = ts_map.bisect_right(25) - 1

if idx >= 0:
    # Get the key at that index
    key = ts_map.iloc[idx]
    print(f"Value at T=25: {ts_map[key]}") # Output: Value B


# To get the key <= target = 25
idx = ts_map.bisect_right(25) - 1
if idx >= 0:
    key = ts_map.keys()[idx] # Returns 20


# =======================
from collections import defaultdict
monthly_card_payments = defaultdict(lambda: {'count': 0, 'total': 0})
monthly_card_payments = defaultdict(dict)
defaultdict(int); defaultdict(list); defaultdict(set)

'''
defaultdict(dict) creates an empty dictionary {} for any missing key.
defaultdict(lambda: {'count': 0, 'total': 0}) creates a dictionary with specific initial values: 
{'count': 0, 'total': 0} for any missing key.
'''

# using match, case

def http_error(status):
    match status:
        case 400:
            return "Bad request"
        case 404:
            return "Not found"
        case 418:
            return "I'm a teapot"
        case _: # Default case
            return "Something's wrong with the internet"

# example try except

try:
    a = 1/ 0
except Error:
    raise Error('wrong dividision')


# using enum
from enum import Enum
class MachineStatus(Enum):
    START = 0
    STOP = 1
    RUNNING = 2

MachineStatus.START

# reverse string
>>> s = '12345'
>>> a = s[::-1]
>>> type(a)
<class 'str'>
>>> a = '54321'


left_max = [0] * n # will create [0, 0, ..., 0] (n times)  => not 0 * [n]


from copy import deepcopy

###                                Queue thread safe
import threading
import queue

# 1. Initialize the thread-safe Queue
# maxsize=0 means infinite; setting a limit helps prevent memory overflow
task_queue = queue.Queue(maxsize=50)
task_queue.qsize()  # Check current size of the queue
task_queue.put((101, ["apple", "apply", "banas"], "a"))  # Add a task to the queue
task_queue.get()  # Retrieve a task from the queue (blocking if empty)
task_queue.task_done()  # Signal that a retrieved task is complete

def evil_partition_worker():
    """Worker thread logic that processes guessing tasks."""
    while True:
        # get() is thread-safe and blocking by default
        task = task_queue.get()
        
        if task is None: # The "Poison Pill" to shut down threads
            task_queue.task_done()
            break
            
        user_id, word_list, guess = task
        print(f"[Worker] Processing guess '{guess}' for User {user_id}")
        
        # --- Insert your Evil Hangman partitioning logic here ---
        # (The logic we wrote in the previous step)
        
        # Signal that the job is finished
        task_queue.task_done()

# 2. Spawning a pool of workers
for i in range(3):
    t = threading.Thread(target=evil_partition_worker, daemon=True)
    t.start()

# 3. Simulating incoming API requests
mock_requests = [
    (101, ["apple", "apply", "banas"], "a"),
    (102, ["deer", "beer", "dish"], "e")
]

for req in mock_requests:
    task_queue.put(req)

# Block until all tasks are processed
task_queue.join()
print("All partitions calculated.")


import re

text = "1.txt(abcd)"
pattern = r"(.+)\((.*)\)"

match = re.search(pattern, text)

if match:
    filename = match.group(1) # Everything before the first "("
    content = match.group(2)  # Everything inside the "()"
    
    print(f"Filename: {filename}")
    print(f"Content:  {content}")


# in 2D matrix
# Anti-diagonal row + col = constant
# Diagonal: row - col = constant