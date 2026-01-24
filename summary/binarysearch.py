'''
8. Using bisect for Binary Search (First Occurrence >= or <= Target)
-------------------------------------------------------------------
Python's `bisect` module provides convenient functions for binary search:
- `bisect_left(arr, target)`: returns the first index where `arr[index] >= target`.
- `bisect_right(arr, target)`: returns the first index where `arr[index] > target`.

To find the first occurrence where value is >= target:
'''
from bisect import bisect_left, bisect_right

# Find first index where arr[index] >= target
def first_ge(arr, target):
	return bisect_left(arr, target)

# Find first index where arr[index] > target
def first_gt(arr, target):
	return bisect_right(arr, target)

# Find last index where arr[index] <= target
def last_le(arr, target):
	idx = bisect_right(arr, target)
	return idx - 1 if idx > 0 else -1

# Find last index where arr[index] < target
def last_lt(arr, target):
	idx = bisect_left(arr, target)
	return idx - 1 if idx > 0 else -1

'''
Example usage:
arr = [1, 2, 4, 4, 5, 7]
target = 4
print(first_ge(arr, target))  # Output: 2 (first index where arr[index] >= 4)
print(first_gt(arr, target))  # Output: 4 (first index where arr[index] > 4)
print(last_le(arr, target))   # Output: 3 (last index where arr[index] <= 4)
print(last_lt(arr, target))   # Output: 1 (last index where arr[index] < 4)
'''
# Binary Search Coding Question Patterns and Answers
'''
1. Classic Binary Search (Find Target in Sorted Array)
-----------------------------------------------------
Given a sorted array, find the index of a target value.

Approach:
- Use two pointers (`left`, `right`), repeatedly halve the search space.
- If `mid` equals target, return `mid`.
- If `mid` < target, search right half; else, search left half.
- If not found, return -1.

'''

def binary_search(arr, target):
	left, right = 0, len(arr) - 1
	while left <= right:
		mid = (left + right) // 2
		if arr[mid] == target:
			return mid
		elif arr[mid] < target:
			left = mid + 1
		else:
			right = mid - 1
	return -1

'''
2. First/Last Occurrence in Sorted Array
----------------------------------------
Find the first or last occurrence of a target in a sorted array with duplicates.

Approach:
- Modify binary search to continue searching after finding the target.
- For first occurrence, move `right = mid - 1` when found.
- For last occurrence, move `left = mid + 1` when found.

Example (First Occurrence):

'''
def first_occurrence(arr, target):
	left, right = 0, len(arr) - 1
	result = -1
	while left <= right:
		mid = (left + right) // 2
		if arr[mid] == target:
			result = mid
			right = mid - 1
		elif arr[mid] < target:
			left = mid + 1
		else:
			right = mid - 1
	return result

'''
3. Search Insert Position
------------------------
Find the index where a target should be inserted in a sorted array.

Approach:
- Standard binary search; when not found, `left` is the insert position.

'''
def search_insert(arr, target):
	left, right = 0, len(arr) - 1
	while left <= right:
		mid = (left + right) // 2
		if arr[mid] == target:
			return mid
		elif arr[mid] < target:
			left = mid + 1
		else:
			right = mid - 1
	return left

'''
4. Find Minimum/Maximum in Rotated Sorted Array
-----------------------------------------------
Given a rotated sorted array, find the minimum (or maximum) element.

Approach:
- Use binary search to compare `mid` with `right` (or `left`).
- If `arr[mid] > arr[right]`, min is in right half; else, left half.

'''

def find_min_rotated(arr):
	left, right = 0, len(arr) - 1
	while left < right:
		mid = (left + right) // 2
		if arr[mid] > arr[right]:
			left = mid + 1
		else:
			right = mid
	return arr[left]

'''
5. Binary Search on Answer (Search Space)
----------------------------------------
Find the minimum/maximum value that satisfies a condition (e.g., minimum capacity to ship packages in D days).

Approach:
- Define a function `can_satisfy(x)` to check if a value is valid.
- Binary search over the value range, not the array indices.

'''

def binary_search_answer(low, high, can_satisfy):
	while low < high:
		mid = (low + high) // 2
		if can_satisfy(mid):
			high = mid
		else:
			low = mid + 1
	return low

'''
6. Find Peak Element
--------------------
Find a peak element (greater than neighbors) in an array.

Approach:
- Use binary search; if `arr[mid] < arr[mid+1]`, peak is right; else, left.

'''
def find_peak(arr):
	left, right = 0, len(arr) - 1
	while left < right:
		mid = (left + right) // 2
		if arr[mid] < arr[mid + 1]:
			left = mid + 1
		else:
			right = mid
	return left

'''
7. Search in 2D Matrix
----------------------
Given a 2D matrix sorted row-wise and column-wise, search for a target.

Approach:
- Treat as 1D array, or start from top-right and move left/down.

'''

def search_matrix(matrix, target):
	if not matrix or not matrix[0]:
		return False
	m, n = len(matrix), len(matrix[0])
	left, right = 0, m * n - 1
	while left <= right:
		mid = (left + right) // 2
		val = matrix[mid // n][mid % n]
		if val == target:
			return True
		elif val < target:
			left = mid + 1
		else:
			right = mid - 1
	return False


def find_lastest_value_less_equal_time_stamp(arr, timestamp):
	"""
	This function finds the value of the rightmost tuple (timestamp, value) in a sorted array where timestamp <= target.
    
	:param arr: List[Tuple[int, Any]] - A sorted list of (timestamp, value) tuples, sorted by timestamp
	:param timestamp: int - The target timestamp
	:return: value or None - The value of the latest tuple with timestamp <= target, or None if no such tuple exists
	"""
	from bisect import bisect_right
	# Extract timestamps for bisect
	timestamps = [t for t, v in arr]
	idx = bisect_right(timestamps, timestamp)
	if idx == 0:
		return None  # No timestamp less than or equal to target
	return arr[idx - 1][1]


def find_latest_value_le_timestamp_manual(arr, timestamp):
	"""
	Manual binary search: finds the value of the rightmost tuple (timestamp, value) in a sorted array where timestamp <= target.
	:param arr: List[Tuple[int, Any]] - A sorted list of (timestamp, value) tuples, sorted by timestamp
	:param timestamp: int - The target timestamp
	:return: value or None - The value of the latest tuple with timestamp <= target, or None if no such tuple exists
	"""
	left, right = 0, len(arr) - 1
	result = None
	while left <= right:
		mid = (left + right) // 2
		if arr[mid][0] <= timestamp:
			result = arr[mid][1]
			left = mid + 1
		else:
			right = mid - 1
	return result