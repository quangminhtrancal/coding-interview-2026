"""
COMPREHENSIVE CODING INTERVIEW PATTERNS
========================================
All major patterns with explanations and Python solutions
"""

# ============================================================================
# 1. SLIDING WINDOW PATTERN
# ============================================================================
# Use when: dealing with contiguous subarrays/substrings, finding optimal windows

def max_sum_subarray_size_k(arr, k):
    """Fixed-size sliding window: Maximum sum of subarray of size k"""
    max_sum = window_sum = sum(arr[:k])

    for i in range(len(arr) - k):
        window_sum = window_sum - arr[i] + arr[i + k]
        max_sum = max(max_sum, window_sum)

    return max_sum


def longest_substring_k_distinct(s, k):
    """Variable-size sliding window: Longest substring with at most k distinct chars"""
    if k == 0:
        return 0

    char_count = {}
    left = max_len = 0

    for right in range(len(s)):
        char_count[s[right]] = char_count.get(s[right], 0) + 1

        while len(char_count) > k:
            char_count[s[left]] -= 1
            if char_count[s[left]] == 0:
                del char_count[s[left]]
            left += 1

        max_len = max(max_len, right - left + 1)

    return max_len


def min_window_substring(s, t):
    """Minimum window substring containing all characters of t"""
    from collections import Counter

    if not s or not t:
        return ""

    target_count = Counter(t)
    required = len(target_count)
    window_count = {}
    formed = 0
    left = 0
    min_len = float('inf')
    min_window = (0, 0)

    for right in range(len(s)):
        char = s[right]
        window_count[char] = window_count.get(char, 0) + 1

        if char in target_count and window_count[char] == target_count[char]:
            formed += 1

        while left <= right and formed == required:
            if right - left + 1 < min_len:
                min_len = right - left + 1
                min_window = (left, right)

            char = s[left]
            window_count[char] -= 1
            if char in target_count and window_count[char] < target_count[char]:
                formed -= 1
            left += 1

    return "" if min_len == float('inf') else s[min_window[0]:min_window[1] + 1]


# ============================================================================
# 2. TWO POINTERS PATTERN
# ============================================================================
# Use when: dealing with sorted arrays, finding pairs, removing duplicates

def two_sum_sorted(arr, target):
    """Two pointers: Find pair that sums to target in sorted array"""
    left, right = 0, len(arr) - 1

    while left < right:
        current_sum = arr[left] + arr[right]
        if current_sum == target:
            return [left, right]
        elif current_sum < target:
            left += 1
        else:
            right -= 1

    return [-1, -1]


def remove_duplicates_sorted(arr):
    """Two pointers: Remove duplicates from sorted array in-place"""
    if not arr:
        return 0

    write_idx = 1
    for i in range(1, len(arr)):
        if arr[i] != arr[i - 1]:
            arr[write_idx] = arr[i]
            write_idx += 1

    return write_idx


def three_sum(arr):
    """Three pointers: Find all unique triplets that sum to zero"""
    arr.sort()
    result = []

    for i in range(len(arr) - 2):
        if i > 0 and arr[i] == arr[i - 1]:
            continue

        left, right = i + 1, len(arr) - 1
        while left < right:
            current_sum = arr[i] + arr[left] + arr[right]
            if current_sum == 0:
                result.append([arr[i], arr[left], arr[right]])
                while left < right and arr[left] == arr[left + 1]:
                    left += 1
                while left < right and arr[right] == arr[right - 1]:
                    right -= 1
                left += 1
                right -= 1
            elif current_sum < 0:
                left += 1
            else:
                right -= 1

    return result


def container_with_most_water(heights):
    """Two pointers: Maximum area container"""
    left, right = 0, len(heights) - 1
    max_area = 0

    while left < right:
        width = right - left
        max_area = max(max_area, min(heights[left], heights[right]) * width)

        if heights[left] < heights[right]:
            left += 1
        else:
            right -= 1

    return max_area


# ============================================================================
# 3. FAST & SLOW POINTERS (Floyd's Cycle Detection)
# ============================================================================
# Use when: detecting cycles in linked lists, finding middle element

class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def has_cycle(head):
    """Detect cycle in linked list"""
    slow = fast = head

    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow == fast:
            return True

    return False


def find_cycle_start(head):
    """Find the start of cycle in linked list"""
    slow = fast = head

    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow == fast:
            break

    if not fast or not fast.next:
        return None

    slow = head
    while slow != fast:
        slow = slow.next
        fast = fast.next

    return slow


def middle_of_linked_list(head):
    """Find middle node of linked list"""
    slow = fast = head

    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next

    return slow


def is_happy_number(n):
    """Determine if a number is happy using fast & slow pointers"""
    def get_next(num):
        total = 0
        while num > 0:
            digit = num % 10
            total += digit * digit
            num //= 10
        return total

    slow = fast = n
    while True:
        slow = get_next(slow)
        fast = get_next(get_next(fast))
        if fast == 1:
            return True
        if slow == fast:
            return False


# ============================================================================
# 4. MERGE INTERVALS PATTERN
# ============================================================================
# Use when: dealing with overlapping intervals, scheduling problems

def merge_intervals(intervals):
    """Merge overlapping intervals"""
    if not intervals:
        return []

    intervals.sort(key=lambda x: x[0])
    merged = [intervals[0]]

    for interval in intervals[1:]:
        if interval[0] <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], interval[1])
        else:
            merged.append(interval)

    return merged


def insert_interval(intervals, new_interval):
    """Insert interval and merge if necessary"""
    result = []
    i = 0

    # Add all intervals before new_interval
    while i < len(intervals) and intervals[i][1] < new_interval[0]:
        result.append(intervals[i])
        i += 1

    # Merge overlapping intervals
    while i < len(intervals) and intervals[i][0] <= new_interval[1]:
        new_interval[0] = min(new_interval[0], intervals[i][0])
        new_interval[1] = max(new_interval[1], intervals[i][1])
        i += 1
    result.append(new_interval)

    # Add remaining intervals
    while i < len(intervals):
        result.append(intervals[i])
        i += 1

    return result


def interval_intersection(list1, list2):
    """Find intersection of two interval lists"""
    result = []
    i = j = 0

    while i < len(list1) and j < len(list2):
        start = max(list1[i][0], list2[j][0])
        end = min(list1[i][1], list2[j][1])

        if start <= end:
            result.append([start, end])

        if list1[i][1] < list2[j][1]:
            i += 1
        else:
            j += 1

    return result


# ============================================================================
# 5. CYCLIC SORT PATTERN
# ============================================================================
# Use when: array contains numbers in given range, find missing/duplicate numbers

def cyclic_sort(nums):
    """Sort array containing numbers from 1 to n"""
    i = 0
    while i < len(nums):
        correct_idx = nums[i] - 1
        if nums[i] != nums[correct_idx]:
            nums[i], nums[correct_idx] = nums[correct_idx], nums[i]
        else:
            i += 1
    return nums


def find_missing_number(nums):
    """Find missing number in array containing 0 to n"""
    i = 0
    n = len(nums)

    while i < n:
        correct_idx = nums[i]
        if nums[i] < n and nums[i] != nums[correct_idx]:
            nums[i], nums[correct_idx] = nums[correct_idx], nums[i]
        else:
            i += 1

    for i in range(n):
        if nums[i] != i:
            return i

    return n


def find_all_duplicates(nums):
    """Find all duplicates in array of 1 to n"""
    i = 0
    while i < len(nums):
        correct_idx = nums[i] - 1
        if nums[i] != nums[correct_idx]:
            nums[i], nums[correct_idx] = nums[correct_idx], nums[i]
        else:
            i += 1

    duplicates = []
    for i in range(len(nums)):
        if nums[i] != i + 1:
            duplicates.append(nums[i])

    return duplicates


# ============================================================================
# 6. IN-PLACE REVERSAL OF LINKED LIST
# ============================================================================
# Use when: reversing linked lists without extra space

def reverse_linked_list(head):
    """Reverse entire linked list"""
    prev = None
    current = head

    while current:
        next_node = current.next
        current.next = prev
        prev = current
        current = next_node

    return prev


def reverse_sublist(head, left, right):
    """Reverse sublist from position left to right"""
    if left == right:
        return head

    dummy = ListNode(0)
    dummy.next = head
    prev = dummy

    for _ in range(left - 1):
        prev = prev.next

    current = prev.next
    for _ in range(right - left):
        next_node = current.next
        current.next = next_node.next
        next_node.next = prev.next
        prev.next = next_node

    return dummy.next


def reverse_k_group(head, k):
    """Reverse nodes in k-group"""
    def reverse_group(start, end):
        prev = None
        current = start
        while current != end:
            next_node = current.next
            current.next = prev
            prev = current
            current = next_node
        return prev

    dummy = ListNode(0)
    dummy.next = head
    prev_group = dummy

    while True:
        kth = prev_group
        for _ in range(k):
            kth = kth.next
            if not kth:
                return dummy.next

        next_group = kth.next
        first = prev_group.next

        prev_group.next = reverse_group(first, next_group)
        first.next = next_group
        prev_group = first

    return dummy.next


# ============================================================================
# 7. TREE BFS (Breadth-First Search)
# ============================================================================
# Use when: level-order traversal, finding shortest path in tree

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def level_order_traversal(root):
    """Level-order traversal of binary tree"""
    if not root:
        return []

    from collections import deque
    result = []
    queue = deque([root])

    while queue:
        level_size = len(queue)
        current_level = []

        for _ in range(level_size):
            node = queue.popleft()
            current_level.append(node.val)

            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)

        result.append(current_level)

    return result


def zigzag_traversal(root):
    """Zigzag level-order traversal"""
    if not root:
        return []

    from collections import deque
    result = []
    queue = deque([root])
    left_to_right = True

    while queue:
        level_size = len(queue)
        current_level = deque()

        for _ in range(level_size):
            node = queue.popleft()

            if left_to_right:
                current_level.append(node.val)
            else:
                current_level.appendleft(node.val)

            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)

        result.append(list(current_level))
        left_to_right = not left_to_right

    return result


def right_side_view(root):
    """Right side view of binary tree"""
    if not root:
        return []

    from collections import deque
    result = []
    queue = deque([root])

    while queue:
        level_size = len(queue)

        for i in range(level_size):
            node = queue.popleft()
            if i == level_size - 1:
                result.append(node.val)

            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)

    return result


# ============================================================================
# 8. TREE DFS (Depth-First Search)
# ============================================================================
# Use when: exploring all paths, finding sum paths, serialization

def max_depth(root):
    """Maximum depth of binary tree"""
    if not root:
        return 0
    return 1 + max(max_depth(root.left), max_depth(root.right))


def has_path_sum(root, target_sum):
    """Check if tree has root-to-leaf path with given sum"""
    if not root:
        return False

    if not root.left and not root.right:
        return root.val == target_sum

    return (has_path_sum(root.left, target_sum - root.val) or
            has_path_sum(root.right, target_sum - root.val))


def all_paths_sum(root, target_sum):
    """Find all root-to-leaf paths with given sum"""
    def dfs(node, current_sum, path, result):
        if not node:
            return

        path.append(node.val)

        if not node.left and not node.right and current_sum == node.val:
            result.append(list(path))
        else:
            dfs(node.left, current_sum - node.val, path, result)
            dfs(node.right, current_sum - node.val, path, result)

        path.pop()

    result = []
    dfs(root, target_sum, [], result)
    return result


def diameter_of_tree(root):
    """Find diameter (longest path between any two nodes)"""
    def dfs(node):
        if not node:
            return 0

        left_height = dfs(node.left)
        right_height = dfs(node.right)

        # Update diameter
        diameter[0] = max(diameter[0], left_height + right_height)

        return 1 + max(left_height, right_height)

    diameter = [0]
    dfs(root)
    return diameter[0]


# ============================================================================
# 9. TWO HEAPS PATTERN
# ============================================================================
# Use when: finding median, scheduling problems

import heapq

def find_median_from_stream():
    """Find median from data stream using two heaps"""
    class MedianFinder:
        def __init__(self):
            self.max_heap = []  # left half (negated for max heap)
            self.min_heap = []  # right half

        def add_num(self, num):
            if not self.max_heap or num <= -self.max_heap[0]:
                heapq.heappush(self.max_heap, -num)
            else:
                heapq.heappush(self.min_heap, num)

            # Balance heaps
            if len(self.max_heap) > len(self.min_heap) + 1:
                heapq.heappush(self.min_heap, -heapq.heappop(self.max_heap))
            elif len(self.min_heap) > len(self.max_heap):
                heapq.heappush(self.max_heap, -heapq.heappop(self.min_heap))

        def find_median(self):
            if len(self.max_heap) == len(self.min_heap):
                return (-self.max_heap[0] + self.min_heap[0]) / 2
            return -self.max_heap[0]

    return MedianFinder()


def sliding_window_median(nums, k):
    """Find median in sliding window"""
    from sortedcontainers import SortedList

    window = SortedList(nums[:k])
    medians = []

    for i in range(len(nums)):
        if i >= k:
            window.remove(nums[i - k])
        if i < len(nums):
            window.add(nums[i])

        if i >= k - 1:
            if k % 2 == 0:
                medians.append((window[k // 2 - 1] + window[k // 2]) / 2)
            else:
                medians.append(window[k // 2])

    return medians


# ============================================================================
# 10. SUBSETS PATTERN (Backtracking)
# ============================================================================
# Use when: generating combinations, permutations, subsets

def subsets(nums):
    """Generate all subsets"""
    result = []

    def backtrack(start, path):
        result.append(list(path))

        for i in range(start, len(nums)):
            path.append(nums[i])
            backtrack(i + 1, path)
            path.pop()

    backtrack(0, [])
    return result


def subsets_with_duplicates(nums):
    """Generate all subsets with duplicates"""
    nums.sort()
    result = []

    def backtrack(start, path):
        result.append(list(path))

        for i in range(start, len(nums)):
            if i > start and nums[i] == nums[i - 1]:
                continue
            path.append(nums[i])
            backtrack(i + 1, path)
            path.pop()

    backtrack(0, [])
    return result


def permutations(nums):
    """Generate all permutations"""
    result = []

    def backtrack(path, remaining):
        if not remaining:
            result.append(list(path))
            return

        for i in range(len(remaining)):
            backtrack(path + [remaining[i]], remaining[:i] + remaining[i+1:])

    backtrack([], nums)
    return result


def combinations(n, k):
    """Generate all combinations of k numbers from 1 to n"""
    result = []

    def backtrack(start, path):
        if len(path) == k:
            result.append(list(path))
            return

        for i in range(start, n + 1):
            path.append(i)
            backtrack(i + 1, path)
            path.pop()

    backtrack(1, [])
    return result


def letter_combinations(digits):
    """Letter combinations of phone number"""
    if not digits:
        return []

    phone = {
        '2': 'abc', '3': 'def', '4': 'ghi', '5': 'jkl',
        '6': 'mno', '7': 'pqrs', '8': 'tuv', '9': 'wxyz'
    }

    result = []

    def backtrack(index, path):
        if index == len(digits):
            result.append(''.join(path))
            return

        for letter in phone[digits[index]]:
            path.append(letter)
            backtrack(index + 1, path)
            path.pop()

    backtrack(0, [])
    return result


# ============================================================================
# 11. MODIFIED BINARY SEARCH
# ============================================================================
# Use when: searching in sorted/rotated arrays, finding boundaries

def binary_search(arr, target):
    """Standard binary search"""
    left, right = 0, len(arr) - 1

    while left <= right:
        mid = left + (right - left) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return -1


def search_rotated_array(arr, target):
    """Search in rotated sorted array"""
    left, right = 0, len(arr) - 1

    while left <= right:
        mid = left + (right - left) // 2

        if arr[mid] == target:
            return mid

        # Left half is sorted
        if arr[left] <= arr[mid]:
            if arr[left] <= target < arr[mid]:
                right = mid - 1
            else:
                left = mid + 1
        # Right half is sorted
        else:
            if arr[mid] < target <= arr[right]:
                left = mid + 1
            else:
                right = mid - 1

    return -1


def find_first_occurrence(arr, target):
    """Find first occurrence of target"""
    left, right = 0, len(arr) - 1
    result = -1

    while left <= right:
        mid = left + (right - left) // 2
        if arr[mid] == target:
            result = mid
            right = mid - 1  # Continue searching left
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return result


def find_peak_element(arr):
    """Find peak element in array"""
    left, right = 0, len(arr) - 1

    while left < right:
        mid = left + (right - left) // 2
        if arr[mid] > arr[mid + 1]:
            right = mid
        else:
            left = mid + 1

    return left


# ============================================================================
# 12. TOP K ELEMENTS PATTERN
# ============================================================================
# Use when: finding k largest/smallest elements

def k_largest_elements(nums, k):
    """Find k largest elements using min heap"""
    min_heap = []

    for num in nums:
        if len(min_heap) < k:
            heapq.heappush(min_heap, num)
        elif num > min_heap[0]:
            heapq.heapreplace(min_heap, num)

    return min_heap


def k_closest_points(points, k):
    """Find k closest points to origin"""
    max_heap = []

    for x, y in points:
        dist = -(x * x + y * y)  # Negative for max heap

        if len(max_heap) < k:
            heapq.heappush(max_heap, (dist, [x, y]))
        elif dist > max_heap[0][0]:
            heapq.heapreplace(max_heap, (dist, [x, y]))

    return [point for _, point in max_heap]


def top_k_frequent(nums, k):
    """Find k most frequent elements"""
    from collections import Counter

    count = Counter(nums)
    return heapq.nlargest(k, count.keys(), key=count.get)


def kth_largest_element(nums, k):
    """Find kth largest element using quickselect"""
    def partition(left, right, pivot_idx):
        pivot = nums[pivot_idx]
        nums[pivot_idx], nums[right] = nums[right], nums[pivot_idx]
        store_idx = left

        for i in range(left, right):
            if nums[i] < pivot:
                nums[i], nums[store_idx] = nums[store_idx], nums[i]
                store_idx += 1

        nums[store_idx], nums[right] = nums[right], nums[store_idx]
        return store_idx

    def select(left, right, k_smallest):
        if left == right:
            return nums[left]

        pivot_idx = left + (right - left) // 2
        pivot_idx = partition(left, right, pivot_idx)

        if k_smallest == pivot_idx:
            return nums[k_smallest]
        elif k_smallest < pivot_idx:
            return select(left, pivot_idx - 1, k_smallest)
        else:
            return select(pivot_idx + 1, right, k_smallest)

    return select(0, len(nums) - 1, len(nums) - k)


# ============================================================================
# 13. K-WAY MERGE PATTERN
# ============================================================================
# Use when: merging k sorted arrays/lists

def merge_k_sorted_lists(lists):
    """Merge k sorted linked lists"""
    min_heap = []

    for i, lst in enumerate(lists):
        if lst:
            heapq.heappush(min_heap, (lst.val, i, lst))

    dummy = ListNode(0)
    current = dummy

    while min_heap:
        val, i, node = heapq.heappop(min_heap)
        current.next = node
        current = current.next

        if node.next:
            heapq.heappush(min_heap, (node.next.val, i, node.next))

    return dummy.next


def merge_k_sorted_arrays(arrays):
    """Merge k sorted arrays"""
    min_heap = []

    for i, arr in enumerate(arrays):
        if arr:
            heapq.heappush(min_heap, (arr[0], i, 0))

    result = []

    while min_heap:
        val, array_idx, element_idx = heapq.heappop(min_heap)
        result.append(val)

        if element_idx + 1 < len(arrays[array_idx]):
            heapq.heappush(min_heap,
                          (arrays[array_idx][element_idx + 1],
                           array_idx,
                           element_idx + 1))

    return result


# ============================================================================
# 14. DYNAMIC PROGRAMMING PATTERNS
# ============================================================================
# Use when: optimization problems, counting problems with overlapping subproblems

# 0/1 Knapsack Pattern
def knapsack_01(weights, values, capacity):
    """0/1 Knapsack problem"""
    n = len(weights)
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        for w in range(1, capacity + 1):
            if weights[i - 1] <= w:
                dp[i][w] = max(
                    values[i - 1] + dp[i - 1][w - weights[i - 1]],
                    dp[i - 1][w]
                )
            else:
                dp[i][w] = dp[i - 1][w]

    return dp[n][capacity]


# Unbounded Knapsack Pattern
def coin_change_min(coins, amount):
    """Minimum coins to make amount"""
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0

    for i in range(1, amount + 1):
        for coin in coins:
            if coin <= i:
                dp[i] = min(dp[i], dp[i - coin] + 1)

    return dp[amount] if dp[amount] != float('inf') else -1


def coin_change_ways(coins, amount):
    """Number of ways to make amount"""
    dp = [0] * (amount + 1)
    dp[0] = 1

    for coin in coins:
        for i in range(coin, amount + 1):
            dp[i] += dp[i - coin]

    return dp[amount]


# Fibonacci Pattern
def fibonacci(n):
    """Fibonacci with DP"""
    if n <= 1:
        return n

    dp = [0] * (n + 1)
    dp[1] = 1

    for i in range(2, n + 1):
        dp[i] = dp[i - 1] + dp[i - 2]

    return dp[n]


def climb_stairs(n):
    """Climbing stairs (1 or 2 steps at a time)"""
    if n <= 2:
        return n

    dp = [0] * (n + 1)
    dp[1] = 1
    dp[2] = 2

    for i in range(3, n + 1):
        dp[i] = dp[i - 1] + dp[i - 2]

    return dp[n]


# Palindrome Pattern
def longest_palindromic_substring(s):
    """Find longest palindromic substring"""
    n = len(s)
    if n == 0:
        return ""

    dp = [[False] * n for _ in range(n)]
    start = max_len = 0

    # All single characters are palindromes
    for i in range(n):
        dp[i][i] = True
        max_len = 1

    # Check for 2-character palindromes
    for i in range(n - 1):
        if s[i] == s[i + 1]:
            dp[i][i + 1] = True
            start = i
            max_len = 2

    # Check for longer palindromes
    for length in range(3, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            if s[i] == s[j] and dp[i + 1][j - 1]:
                dp[i][j] = True
                start = i
                max_len = length

    return s[start:start + max_len]


# LCS Pattern
def longest_common_subsequence(s1, s2):
    """Longest common subsequence"""
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = 1 + dp[i - 1][j - 1]
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    return dp[m][n]


# LIS Pattern
def longest_increasing_subsequence(nums):
    """Longest increasing subsequence"""
    if not nums:
        return 0

    dp = [1] * len(nums)

    for i in range(1, len(nums)):
        for j in range(i):
            if nums[i] > nums[j]:
                dp[i] = max(dp[i], dp[j] + 1)

    return max(dp)


# ============================================================================
# 15. TOPOLOGICAL SORT (Graph Pattern)
# ============================================================================
# Use when: ordering tasks with dependencies, course scheduling

def topological_sort_kahn(vertices, edges):
    """Topological sort using Kahn's algorithm (BFS)"""
    from collections import defaultdict, deque

    graph = defaultdict(list)
    in_degree = {i: 0 for i in range(vertices)}

    for parent, child in edges:
        graph[parent].append(child)
        in_degree[child] += 1

    queue = deque([v for v in in_degree if in_degree[v] == 0])
    result = []

    while queue:
        vertex = queue.popleft()
        result.append(vertex)

        for neighbor in graph[vertex]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    return result if len(result) == vertices else []


def can_finish_courses(num_courses, prerequisites):
    """Check if all courses can be finished (detect cycle)"""
    from collections import defaultdict, deque

    graph = defaultdict(list)
    in_degree = [0] * num_courses

    for course, prereq in prerequisites:
        graph[prereq].append(course)
        in_degree[course] += 1

    queue = deque([i for i in range(num_courses) if in_degree[i] == 0])
    count = 0

    while queue:
        course = queue.popleft()
        count += 1

        for neighbor in graph[course]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    return count == num_courses


# ============================================================================
# 16. UNION FIND (Disjoint Set)
# ============================================================================
# Use when: detecting cycles in undirected graphs, connected components

class UnionFind:
    def __init__(self, size):
        self.parent = list(range(size))
        self.rank = [0] * size

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # Path compression
        return self.parent[x]

    def union(self, x, y):
        root_x = self.find(x)
        root_y = self.find(y)

        if root_x == root_y:
            return False

        # Union by rank
        if self.rank[root_x] < self.rank[root_y]:
            self.parent[root_x] = root_y
        elif self.rank[root_x] > self.rank[root_y]:
            self.parent[root_y] = root_x
        else:
            self.parent[root_y] = root_x
            self.rank[root_x] += 1

        return True


def count_connected_components(n, edges):
    """Count number of connected components"""
    uf = UnionFind(n)

    for u, v in edges:
        uf.union(u, v)

    return len(set(uf.find(i) for i in range(n)))


def has_cycle_undirected(n, edges):
    """Detect cycle in undirected graph"""
    uf = UnionFind(n)

    for u, v in edges:
        if not uf.union(u, v):
            return True

    return False


# ============================================================================
# 17. MONOTONIC STACK PATTERN
# ============================================================================
# Use when: finding next greater/smaller element, histogram problems

def next_greater_element(nums):
    """Find next greater element for each element"""
    result = [-1] * len(nums)
    stack = []

    for i in range(len(nums)):
        while stack and nums[i] > nums[stack[-1]]:
            idx = stack.pop()
            result[idx] = nums[i]
        stack.append(i)

    return result


def daily_temperatures(temperatures):
    """Days until warmer temperature"""
    result = [0] * len(temperatures)
    stack = []

    for i in range(len(temperatures)):
        while stack and temperatures[i] > temperatures[stack[-1]]:
            idx = stack.pop()
            result[idx] = i - idx
        stack.append(i)

    return result


def largest_rectangle_histogram(heights):
    """Largest rectangle in histogram"""
    stack = []
    max_area = 0

    for i, h in enumerate(heights + [0]):
        while stack and h < heights[stack[-1]]:
            height = heights[stack.pop()]
            width = i if not stack else i - stack[-1] - 1
            max_area = max(max_area, height * width)
        stack.append(i)

    return max_area


# ============================================================================
# 18. BITWISE XOR PATTERN
# ============================================================================
# Use when: finding missing/duplicate numbers without extra space

def single_number(nums):
    """Find single number where every other appears twice"""
    result = 0
    for num in nums:
        result ^= num
    return result


def two_single_numbers(nums):
    """Find two single numbers where every other appears twice"""
    xor = 0
    for num in nums:
        xor ^= num

    # Find rightmost set bit
    rightmost_bit = xor & -xor

    num1 = num2 = 0
    for num in nums:
        if num & rightmost_bit:
            num1 ^= num
        else:
            num2 ^= num

    return [num1, num2]


def missing_number_xor(nums):
    """Find missing number using XOR"""
    n = len(nums)
    result = n

    for i in range(n):
        result ^= i ^ nums[i]

    return result


if __name__ == "__main__":
    print("=== Coding Interview Patterns Reference ===")
    print("\n18 major patterns implemented with explanations")
    print("\nPattern categories:")
    print("1. Sliding Window")
    print("2. Two Pointers")
    print("3. Fast & Slow Pointers")
    print("4. Merge Intervals")
    print("5. Cyclic Sort")
    print("6. In-place Reversal of Linked List")
    print("7. Tree BFS")
    print("8. Tree DFS")
    print("9. Two Heaps")
    print("10. Subsets (Backtracking)")
    print("11. Modified Binary Search")
    print("12. Top K Elements")
    print("13. K-way Merge")
    print("14. Dynamic Programming")
    print("15. Topological Sort")
    print("16. Union Find")
    print("17. Monotonic Stack")
    print("18. Bitwise XOR")
