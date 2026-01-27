from bisect import bisect_right
from typing import List, Set, Dict

# =======================
a = [['z', 1, 3], ['t', 9, 9], ['a', 10, 10]]
a.sort(key=lambda x: x[0])

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

# =======================
from collections import defaultdict
monthly_card_payments = defaultdict(lambda: {'count': 0, 'total': 0})
monthly_card_payments = defaultdict(dict)

'''
defaultdict(dict) creates an empty dictionary {} for any missing key.
defaultdict(lambda: {'count': 0, 'total': 0}) creates a dictionary with specific initial values: 
{'count': 0, 'total': 0} for any missing key.
'''
