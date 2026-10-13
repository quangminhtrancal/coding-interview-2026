# LeetCode Concise Solutions (Python)

Problem statements are short paraphrases, not the original LeetCode text. Each entry has: **Problem**, **Example**, **Idea**, **Python**, **Complexity**.

## Pattern index

| Pattern | Problems |
|---|---|
| Hash set / hash map | 36, 380, 981, 1797 |
| Backtracking | 37, 79, 39, 40, 216 |
| Trie | 211, 212 |
| Design / cache | 146, 460, 380, 981, 1797, 2622 |
| Heap | 253, 2402, 23, 215, 295 |
| Intervals / scheduling | 253, 2402, 1229 |
| Greedy + sort | 1921 |
| Binary search on answer | 4008, 2604 |
| DP / memo | 1553, 139, 377 |
| Graph / topological sort | 207, 210 |
| Async / timing (JS-only on LeetCode) | 2627, 2622, 2637 |

---

## 36. Valid Sudoku (Medium)

**Problem:** Given a 9x9 board with digits `1-9` or `.`, check that no filled cell repeats a digit in its row, column, or 3x3 box. The board does not need to be solvable.

**Example:** A board with two `5`s in the first row returns `False`. A board with no repeats returns `True`.

**Idea:** Keep a set per row, column, and box. Box index is `(r // 3) * 3 + c // 3`.

```python
def isValidSudoku(board):
    rows = [set() for _ in range(9)]
    cols = [set() for _ in range(9)]
    boxes = [set() for _ in range(9)]
    for r in range(9):
        for c in range(9):
            v = board[r][c]
            if v == '.':
                continue
            b = (r // 3) * 3 + c // 3
            if v in rows[r] or v in cols[c] or v in boxes[b]:
                return False
            rows[r].add(v); cols[c].add(v); boxes[b].add(v)
    return True
```
**Complexity:** O(81) time, which is O(1), and O(81) space.

---

## 37. Sudoku Solver (Hard)

**Problem:** Fill the empty cells (`.`) of a 9x9 board in place so that every row, column, and 3x3 box contains `1-9` exactly once. A unique solution is guaranteed.

**Example:** A standard puzzle gets completed in place, nothing is returned.

**Idea:** Backtracking over the empty cells with row, column, and box sets for fast validity checks. Optional speedup: always pick the empty cell with the fewest candidates.

```python
def solveSudoku(board):
    rows = [set() for _ in range(9)]
    cols = [set() for _ in range(9)]
    boxes = [set() for _ in range(9)]
    empties = []
    for r in range(9):
        for c in range(9):
            v = board[r][c]
            if v == '.':
                empties.append((r, c))
            else:
                rows[r].add(v); cols[c].add(v); boxes[(r // 3) * 3 + c // 3].add(v)

    def backtrack(i):
        if i == len(empties):
            return True
        r, c = empties[i]
        b = (r // 3) * 3 + c // 3
        for d in "123456789":
            if d in rows[r] or d in cols[c] or d in boxes[b]:
                continue
            board[r][c] = d
            rows[r].add(d); cols[c].add(d); boxes[b].add(d)
            if backtrack(i + 1):
                return True
            board[r][c] = '.'
            rows[r].remove(d); cols[c].remove(d); boxes[b].remove(d)
        return False

    backtrack(0)
```
**Complexity:** Exponential worst case, but fast in practice thanks to pruning. Space is O(81).

---

## 4008. Minimum Initial Strength to Defeat All Monsters (Medium)

**Problem (reconstructed):** `monsters[i]` is the strength of the i-th monster. `boosts[j] = [l, r, v]` adds `v` to the bonus of every monster index in `[l, r]`, and overlapping boosts add up. You start with some non-negative strength and fight left to right. For monster `i`, you win if `strength + bonus[i] >= monsters[i]`. After the fight, `strength = max(0, strength - monsters[i])`. The bonus is temporary. Return the minimum initial strength that defeats every monster.

> Caveat: the LeetCode page wasn't readable, so I rebuilt the rules from a third-party mirror whose text was partly garbled. I checked the rules against both examples below. Check them against the official statement before relying on this.

**Example 1:** `monsters=[5,10,15], boosts=[[1,1,10]]` gives `30`.
**Example 2:** `monsters=[5,10,15], boosts=[[1,2,10],[1,2,5]]` gives `5`.

**Idea:** More starting strength never hurts, so the answer is monotonic. Binary search on the start value. Build `bonus[]` with a difference array, then simulate. Starting with `sum(monsters)` always works, so it is the upper bound.

```python
def minimumInitialStrength(monsters, boosts):
    n = len(monsters)
    diff = [0] * (n + 1)
    for l, r, v in boosts:
        diff[l] += v
        diff[r + 1] -= v
    bonus, cur = [0] * n, 0
    for i in range(n):
        cur += diff[i]
        bonus[i] = cur

    def can(s):
        for i in range(n):
            if s + bonus[i] < monsters[i]:
                return False
            s = max(0, s - monsters[i])
        return True

    lo, hi = 0, sum(monsters)
    while lo < hi:
        mid = (lo + hi) // 2
        if can(mid):
            hi = mid
        else:
            lo = mid + 1
    return lo
```
**Complexity:** O(n + b + n log S), where `S = sum(monsters)`.

---

## 1921. Eliminate Maximum Number of Monsters (Medium)

**Problem:** `dist[i]` is the distance of monster `i` from the city and `speed[i]` its speed per minute. You have a weapon that kills one monster, then needs one minute to recharge (it starts charged). You lose if a monster reaches the city. Return the maximum number of monsters you can kill before losing.

**Example:** `dist=[1,3,4], speed=[1,1,1]` gives `3`. `dist=[1,1,2,3], speed=[1,1,1,1]` gives `1`.

**Idea:** Arrival time is `ceil(dist / speed)`. Kill in order of arrival. The i-th shot (0-indexed) happens at minute `i`, so you lose if `arrival <= i`.

```python
def eliminateMaximum(dist, speed):
    times = sorted((d + s - 1) // s for d, s in zip(dist, speed))
    for i, t in enumerate(times):
        if t <= i:
            return i
    return len(times)
```
**Complexity:** O(n log n) time, O(n) space.

---

## 380. Insert Delete GetRandom O(1) (Medium)

**Problem:** Design a set with `insert(val)`, `remove(val)`, and `getRandom()` (uniform over current elements), each in average O(1).

**Example:** `insert(1)` is True, `remove(2)` is False, `insert(2)` is True, `getRandom()` returns 1 or 2, `remove(1)` is True, `insert(2)` is False.

**Idea:** A list for random access plus a dict from value to index. To remove, swap the element with the last one, then pop.

```python
import random

class RandomizedSet:
    def __init__(self):
        self.a = []
        self.pos = {}

    def insert(self, val):
        if val in self.pos:
            return False
        self.pos[val] = len(self.a)
        self.a.append(val)
        return True

    def remove(self, val):
        if val not in self.pos:
            return False
        i, last = self.pos[val], self.a[-1]
        self.a[i] = last
        self.pos[last] = i
        self.a.pop()
        del self.pos[val]
        return True

    def getRandom(self):
        return random.choice(self.a)
```
**Complexity:** O(1) average per operation, O(n) space.

---

## 79. Word Search (Medium)

**Problem:** Given a grid of letters and a word, return whether the word can be built from sequentially adjacent cells (up, down, left, right) without reusing a cell.

**Example:** `board=[["A","B","C","E"],["S","F","C","S"],["A","D","E","E"]]`. `"ABCCED"` is True, `"SEE"` is True, `"ABCB"` is False.

**Idea:** DFS from every cell, marking the current cell as visited (`'#'`) and restoring it on backtrack.

```python
def exist(board, word):
    R, C = len(board), len(board[0])

    def dfs(r, c, i):
        if i == len(word):
            return True
        if r < 0 or c < 0 or r >= R or c >= C or board[r][c] != word[i]:
            return False
        tmp, board[r][c] = board[r][c], '#'
        ok = (dfs(r + 1, c, i + 1) or dfs(r - 1, c, i + 1) or
              dfs(r, c + 1, i + 1) or dfs(r, c - 1, i + 1))
        board[r][c] = tmp
        return ok

    return any(dfs(r, c, 0) for r in range(R) for c in range(C))
```
**Complexity:** O(R * C * 3^L) time, O(L) recursion space.

---

## 211. Design Add and Search Words Data Structure (Medium)

**Problem:** Support `addWord(word)` and `search(word)`, where `search` may contain `.` that matches any single letter.

**Example:** Add `bad`, `dad`, `mad`. `search("pad")` is False, `search("bad")` is True, `search(".ad")` is True, `search("b..")` is True.

**Idea:** A trie. On `.`, try every child with DFS.

```python
class WordDictionary:
    def __init__(self):
        self.root = {}

    def addWord(self, word):
        node = self.root
        for ch in word:
            node = node.setdefault(ch, {})
        node['$'] = True

    def search(self, word):
        def dfs(i, node):
            if i == len(word):
                return '$' in node
            ch = word[i]
            if ch == '.':
                return any(dfs(i + 1, child) for k, child in node.items() if k != '$')
            return ch in node and dfs(i + 1, node[ch])
        return dfs(0, self.root)
```
**Complexity:** `addWord` is O(L). `search` is O(L) without dots and up to O(26^L) worst case with dots.

---

## 212. Word Search II (Hard)

**Problem:** Given a grid of letters and a list of words, return all words that can be formed in the grid (same adjacency rules as Word Search, no cell reuse within a word).

**Example:** `board=[["o","a","a","n"],["e","t","a","e"],["i","h","k","r"],["i","f","l","v"]]`, `words=["oath","pea","eat","rain"]` gives `["eat","oath"]`.

**Idea:** Build a trie of all words and run one DFS per start cell, walking the trie at the same time. Store the full word at its end node, and prune exhausted branches to avoid repeated work.

```python
def findWords(board, words):
    root = {}
    for w in words:
        node = root
        for ch in w:
            node = node.setdefault(ch, {})
        node['$'] = w

    R, C = len(board), len(board[0])
    res = []

    def dfs(r, c, parent):
        ch = board[r][c]
        node = parent[ch]
        if '$' in node:
            res.append(node.pop('$'))        # pop avoids duplicates
        board[r][c] = '#'
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < R and 0 <= nc < C and board[nr][nc] in node:
                dfs(nr, nc, node)
        board[r][c] = ch
        if not node:
            parent.pop(ch)                   # prune empty branch

    for r in range(R):
        for c in range(C):
            if board[r][c] in root:
                dfs(r, c, root)
    return res
```
**Complexity:** O(R * C * 3^L) worst case, but the trie pruning makes it far faster in practice. Space is O(total word length).

---

## 146. LRU Cache (Medium)

**Problem:** Design a cache with capacity `capacity`. `get(key)` returns the value or `-1`. `put(key, value)` inserts or updates, and evicts the least recently used key when over capacity. Both must be O(1).

**Example:** capacity 2: `put(1,1)`, `put(2,2)`, `get(1)` is 1, `put(3,3)` evicts 2, `get(2)` is -1.

**Idea (short):** `OrderedDict` keeps order for you.

```python
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity):
        self.cap, self.d = capacity, OrderedDict()

    def get(self, key):
        if key not in self.d:
            return -1
        self.d.move_to_end(key)
        return self.d[key]

    def put(self, key, value):
        if key in self.d:
            self.d.move_to_end(key)
        self.d[key] = value
        if len(self.d) > self.cap:
            self.d.popitem(last=False)
```

**Idea (interview version):** hash map + doubly linked list with dummy head and tail. Most recent goes next to the head, evict from before the tail.

```python
class Node:
    __slots__ = ("k", "v", "prev", "next")
    def __init__(self, k=0, v=0):
        self.k, self.v, self.prev, self.next = k, v, None, None

class LRUCache:
    def __init__(self, capacity):
        self.cap, self.map = capacity, {}
        self.head, self.tail = Node(), Node()
        self.head.next, self.tail.prev = self.tail, self.head

    def _remove(self, n):
        n.prev.next, n.next.prev = n.next, n.prev

    def _add_front(self, n):
        n.prev, n.next = self.head, self.head.next
        self.head.next.prev = n
        self.head.next = n

    def get(self, key):
        if key not in self.map:
            return -1
        n = self.map[key]
        self._remove(n); self._add_front(n)
        return n.v

    def put(self, key, value):
        if key in self.map:
            n = self.map[key]
            n.v = value
            self._remove(n); self._add_front(n)
            return
        if len(self.map) == self.cap:
            lru = self.tail.prev
            self._remove(lru)
            del self.map[lru.k]
        n = Node(key, value)
        self.map[key] = n
        self._add_front(n)
```
**Complexity:** O(1) per operation, O(capacity) space.

---

## 253. Meeting Rooms II (Medium, Premium)

**Problem:** Given meeting intervals `[start, end]`, return the minimum number of rooms needed. A meeting ending at `t` and another starting at `t` can share a room.

**Example:** `[[0,30],[5,10],[15,20]]` gives `2`. `[[7,10],[2,4]]` gives `1`.

**Idea:** Sort by start. A min-heap holds the end times of rooms in use. If the earliest end is `<= start`, reuse that room.

```python
import heapq

def minMeetingRooms(intervals):
    intervals.sort(key=lambda x: x[0])
    heap = []
    for start, end in intervals:
        if heap and heap[0] <= start:
            heapq.heappop(heap)
        heapq.heappush(heap, end)
    return len(heap)
```
**Complexity:** O(n log n) time, O(n) space.

---

## 2402. Meeting Rooms III (Hard)

**Problem:** There are `n` rooms numbered `0..n-1` and meetings `[start, end]` with unique start times. Each meeting takes the lowest-numbered free room. If none is free, it waits for the first room to free up and keeps its original duration. Earlier original start times get priority. Return the room that hosted the most meetings (lowest number on ties).

**Example:** `n=2, meetings=[[0,10],[1,5],[2,7],[3,4]]` gives `0`.

**Idea:** Two heaps: free rooms (by id) and busy rooms (by `(end_time, room)`). Before each meeting, release rooms that have finished. If none is free, take the room with the earliest end and push its end time forward by the meeting's duration.

```python
import heapq

def mostBooked(n, meetings):
    meetings.sort()
    free = list(range(n))
    heapq.heapify(free)
    busy = []                       # (end_time, room)
    cnt = [0] * n

    for s, e in meetings:
        while busy and busy[0][0] <= s:
            _, r = heapq.heappop(busy)
            heapq.heappush(free, r)
        if free:
            r = heapq.heappop(free)
            heapq.heappush(busy, (e, r))
        else:
            end, r = heapq.heappop(busy)
            heapq.heappush(busy, (end + (e - s), r))   # delayed start
        cnt[r] += 1

    return cnt.index(max(cnt))      # index() returns the lowest room on ties
```
**Complexity:** O(m log m + m log n), where `m` is the number of meetings.

---

## 1229. Meeting Scheduler (Medium, Premium)

**Problem:** Given two people's availability slots and a `duration`, return the earliest `[start, start + duration]` that fits in a slot free for both, or `[]` if none exists.

**Example:** `slots1=[[10,50],[60,120],[140,210]]`, `slots2=[[0,15],[60,70]]`, `duration=8` gives `[60,68]`. With `duration=12` it gives `[]`.

**Idea:** Sort both lists and use two pointers. The overlap is `[max(starts), min(ends)]`. If it fits, return it. Otherwise advance the pointer whose slot ends first.

```python
def minAvailableDuration(slots1, slots2, duration):
    slots1.sort(); slots2.sort()
    i = j = 0
    while i < len(slots1) and j < len(slots2):
        start = max(slots1[i][0], slots2[j][0])
        end = min(slots1[i][1], slots2[j][1])
        if end - start >= duration:
            return [start, start + duration]
        if slots1[i][1] < slots2[j][1]:
            i += 1
        else:
            j += 1
    return []
```
**Complexity:** O(n log n + m log m) time, O(1) extra space.

---

## 981. Time Based Key-Value Store (Medium)

**Problem:** `set(key, value, timestamp)` stores a value. `get(key, timestamp)` returns the value stored with the largest timestamp `<= timestamp`, or `""` if none exists. Timestamps passed to `set` are strictly increasing.

**Example:** `set("foo","bar",1)`, `get("foo",1)` is `"bar"`, `get("foo",3)` is `"bar"`, `set("foo","bar2",4)`, `get("foo",4)` is `"bar2"`, `get("foo",5)` is `"bar2"`.

**Idea:** Per key, keep parallel sorted lists of timestamps and values. Use binary search (`bisect_right`) for `get`.

```python
from collections import defaultdict
import bisect

class TimeMap:
    def __init__(self):
        self.ts = defaultdict(list)
        self.vals = defaultdict(list)

    def set(self, key, value, timestamp):
        self.ts[key].append(timestamp)
        self.vals[key].append(value)

    def get(self, key, timestamp):
        if key not in self.ts:
            return ""
        i = bisect.bisect_right(self.ts[key], timestamp)
        return self.vals[key][i - 1] if i else ""
```
**Complexity:** `set` is O(1). `get` is O(log n).

---

## 2604. Minimum Time to Eat All Grains (Hard, Premium)

**Problem:** Hens and grains sit on a number line. A hen moves 1 unit per second and eats a grain instantly on arrival. All hens move at the same time. Return the minimum time to eat all grains.

**Example:** `hens=[3,6,7], grains=[2,4,7,9]` gives `2`. `hens=[4,6,109,111,213,215], grains=[5,110,214]` gives `1`.

**Idea:** Binary search on time `t`. For feasibility, sort both arrays and sweep hens left to right with a pointer `j` at the leftmost uneaten grain. If it is left of the hen at distance `d`, the hen must reach it (`d <= t`). Its remaining reach to the right is `max(t - 2d, (t - d) // 2)`. Otherwise the hen reaches `h + t`. Advance `j` past everything covered.

```python
def minimumTime(hens, grains):
    hens.sort(); grains.sort()
    m = len(grains)

    def can(t):
        j = 0
        for h in hens:
            if j == m:
                return True
            if grains[j] < h:
                d = h - grains[j]
                if d > t:
                    return False
                reach = h + max(t - 2 * d, (t - d) // 2)
            else:
                reach = h + t
            while j < m and grains[j] <= reach:
                j += 1
        return j == m

    lo, hi = 0, 2 * (max(hens[-1], grains[-1]) - min(hens[0], grains[0]))
    while lo < hi:
        mid = (lo + hi) // 2
        if can(mid):
            hi = mid
        else:
            lo = mid + 1
    return lo
```
**Complexity:** O(n log n + m log m + (n + m) log T).

---

## 1553. Minimum Number of Days to Eat N Oranges (Hard)

**Problem:** Each day you may eat 1 orange, or `n/2` oranges if `n` is divisible by 2, or `2n/3` oranges if `n` is divisible by 3. Return the minimum days to eat all `n` oranges.

**Example:** `n=10` gives `4` (10 → 9 → 3 → 1 → 0). `n=6` gives `3`.

**Idea:** Only two useful moves: halve, or take two thirds. Use single "eat 1" days to reach a divisible number. So `f(n) = 1 + min(n % 2 + f(n // 2), n % 3 + f(n // 3))`, memoized.

```python
from functools import lru_cache

def minDays(n):
    @lru_cache(None)
    def f(n):
        if n <= 1:
            return n
        return 1 + min(n % 2 + f(n // 2), n % 3 + f(n // 3))
    return f(n)
```
**Complexity:** O(log^2 n) states.

---

## 1797. Design Authentication Manager (Medium)

**Problem:** Tokens live `timeToLive` seconds. `generate(id, t)` creates a token expiring at `t + ttl`. `renew(id, t)` extends it only if still unexpired. `countUnexpiredTokens(t)` returns how many are alive. A token expiring at time `t` counts as expired at `t`.

**Example:** ttl=5: `generate("aaa",2)`, `count(6)` is 1, `generate("bbb",7)`, `renew("aaa",8)` ignored since it expired at 7, `renew("bbb",10)`, `count(15)` is 0.

**Idea:** Map token to expiry time. Alive means `expiry > currentTime`.

```python
class AuthenticationManager:
    def __init__(self, timeToLive):
        self.ttl = timeToLive
        self.exp = {}

    def generate(self, tokenId, currentTime):
        self.exp[tokenId] = currentTime + self.ttl

    def renew(self, tokenId, currentTime):
        if self.exp.get(tokenId, 0) > currentTime:
            self.exp[tokenId] = currentTime + self.ttl

    def countUnexpiredTokens(self, currentTime):
        return sum(e > currentTime for e in self.exp.values())
```
**Complexity:** O(1) for `generate` and `renew`, O(n) for `count`. For amortized O(1), use an `OrderedDict` ordered by expiry and pop expired entries from the front.

---

## 39. Combination Sum (Medium)

**Problem:** Given distinct integers `candidates` and a `target`, return all unique combinations that sum to `target`. Each number can be reused any number of times.

**Example:** `[2,3,6,7], target=7` gives `[[2,2,3],[7]]`.

**Idea:** Backtracking. Recurse with the same index `i` to allow reuse. Moving only forward avoids duplicate orderings.

```python
def combinationSum(candidates, target):
    candidates.sort()
    res, path = [], []

    def dfs(start, remain):
        if remain == 0:
            res.append(path[:])
            return
        for i in range(start, len(candidates)):
            c = candidates[i]
            if c > remain:
                break
            path.append(c)
            dfs(i, remain - c)          # i, not i + 1: reuse allowed
            path.pop()

    dfs(0, target)
    return res
```
**Complexity:** Exponential, bounded by the number of valid combinations times their length.

---

## 40. Combination Sum II (Medium)

**Problem:** `candidates` may contain duplicates, and each element can be used at most once. Return all unique combinations summing to `target`.

**Example:** `[10,1,2,7,6,1,5], target=8` gives `[[1,1,6],[1,2,5],[1,7],[2,6]]`.

**Idea:** Sort, recurse with `i + 1`, and skip duplicates at the same depth (`i > start and c[i] == c[i-1]`).

```python
def combinationSum2(candidates, target):
    candidates.sort()
    res, path = [], []

    def dfs(start, remain):
        if remain == 0:
            res.append(path[:])
            return
        for i in range(start, len(candidates)):
            if i > start and candidates[i] == candidates[i - 1]:
                continue                # skip duplicate at this level
            if candidates[i] > remain:
                break
            path.append(candidates[i])
            dfs(i + 1, remain - candidates[i])
            path.pop()

    dfs(0, target)
    return res
```
**Complexity:** Exponential, bounded by the number of valid combinations.

---

## 216. Combination Sum III (Medium)

**Problem:** Find all combinations of exactly `k` distinct numbers from `1-9` that sum to `n`.

**Example:** `k=3, n=7` gives `[[1,2,4]]`. `k=3, n=9` gives `[[1,2,6],[1,3,5],[2,3,4]]`.

**Idea:** Backtracking over digits 1 to 9, stopping once `k` numbers are chosen.

```python
def combinationSum3(k, n):
    res, path = [], []

    def dfs(start, remain):
        if len(path) == k:
            if remain == 0:
                res.append(path[:])
            return
        for d in range(start, 10):
            if d > remain:
                break
            path.append(d)
            dfs(d + 1, remain - d)
            path.pop()

    dfs(1, n)
    return res
```
**Complexity:** At most C(9, k) combinations.

---

## 377. Combination Sum IV (Medium)

**Problem:** Given distinct positive integers `nums` and a `target`, return the number of **ordered** sequences that sum to `target`. Different orderings count separately.

**Example:** `nums=[1,2,3], target=4` gives `7`.

**Idea:** `dp[t] = sum(dp[t - x] for x in nums if x <= t)`, with `dp[0] = 1`. Keep the **target loop outside** so orderings are counted. Putting `nums` outside would count combinations instead (the Coin Change II pattern).

```python
def combinationSum4(nums, target):
    dp = [0] * (target + 1)
    dp[0] = 1
    for t in range(1, target + 1):
        for x in nums:
            if x <= t:
                dp[t] += dp[t - x]
    return dp[target]
```
**Complexity:** O(target * len(nums)) time, O(target) space.

---

## 2627. Debounce (Medium, JavaScript only)

**Problem:** Return a debounced version of `fn`. Each call delays execution by `t` ms, and a new call before the delay ends cancels the pending one.

**Example:** `t=50`, calls at 50 ms with `[1]` and 75 ms with `[2]`. Only `fn(2)` runs, at 125 ms.

**JavaScript (the LeetCode answer):**
```javascript
var debounce = function(fn, t) {
    let timer;
    return function(...args) {
        clearTimeout(timer);
        timer = setTimeout(() => fn(...args), t);
    };
};
```

**Python equivalent:**
```python
import threading

def debounce(fn, t_seconds):
    timer = None
    lock = threading.Lock()

    def wrapper(*args, **kwargs):
        nonlocal timer
        with lock:
            if timer is not None:
                timer.cancel()
            timer = threading.Timer(t_seconds, fn, args, kwargs)
            timer.start()
    return wrapper
```
**Complexity:** O(1) per call.

---

## 2622. Cache With Time Limit (Medium, JavaScript only)

**Problem:** Build a cache where each key expires after a duration. `set(key, value, duration)` returns `true` if an unexpired key already existed (and overwrites value and duration). `get(key)` returns the value or `-1`. `count()` returns the number of unexpired keys.

**Example:** `set(1,42,100)` is false, `get(1)` at 50 ms is 42, `count()` at 50 ms is 1, `get(1)` at 150 ms is -1.

**JavaScript:**
```javascript
var TimeLimitedCache = function() { this.map = new Map(); };

TimeLimitedCache.prototype.set = function(key, value, duration) {
    const existed = this.map.has(key);
    if (existed) clearTimeout(this.map.get(key).timer);
    const timer = setTimeout(() => this.map.delete(key), duration);
    this.map.set(key, { value, timer });
    return existed;
};

TimeLimitedCache.prototype.get = function(key) {
    return this.map.has(key) ? this.map.get(key).value : -1;
};

TimeLimitedCache.prototype.count = function() { return this.map.size; };
```

**Python equivalent (lazy expiry, no timers):**
```python
import time

class TimeLimitedCache:
    def __init__(self):
        self.d = {}                                   # key -> (value, expiry)

    def set(self, key, value, duration_ms):
        now = time.monotonic()
        existed = key in self.d and self.d[key][1] > now
        self.d[key] = (value, now + duration_ms / 1000)
        return existed

    def get(self, key):
        item = self.d.get(key)
        if item and item[1] > time.monotonic():
            return item[0]
        self.d.pop(key, None)
        return -1

    def count(self):
        now = time.monotonic()
        self.d = {k: v for k, v in self.d.items() if v[1] > now}
        return len(self.d)
```
**Complexity:** `set` and `get` are O(1). `count` is O(1) in JS and O(n) in the Python version.

---

## 2637. Promise Time Limit (Medium, JavaScript only)

**Problem:** Given an async function `fn` and a time limit `t` ms, return a new function that resolves with `fn`'s result if it finishes within `t` ms. Otherwise it rejects with `"Time Limit Exceeded"`. If `fn` rejects first, reject with that error.

**Example:** `fn` takes 100 ms, `t=50`, so it rejects with `"Time Limit Exceeded"`. With `t=150` it resolves normally.

**JavaScript:**
```javascript
var timeLimit = function(fn, t) {
    return async function(...args) {
        return new Promise((resolve, reject) => {
            const timer = setTimeout(() => reject("Time Limit Exceeded"), t);
            fn(...args).then(resolve, reject).finally(() => clearTimeout(timer));
        });
    };
};
```

**Python equivalent:**
```python
import asyncio

def time_limit(fn, t_ms):
    async def wrapper(*args, **kwargs):
        try:
            return await asyncio.wait_for(fn(*args, **kwargs), timeout=t_ms / 1000)
        except asyncio.TimeoutError:
            raise Exception("Time Limit Exceeded")
    return wrapper
```
**Complexity:** O(1) overhead per call.

---

## 460. LFU Cache (Hard)

**Problem:** Design a cache with `get` and `put`, both O(1). When full, evict the **least frequently used** key. Break ties by evicting the **least recently used** among them. Every `get` or `put` on a key counts as a use.

**Example:** capacity 2: `put(1,1)`, `put(2,2)`, `get(1)` is 1, `put(3,3)` evicts 2, `get(2)` is -1, `get(3)` is 3, `put(4,4)` evicts 1 (tied frequency, older), `get(1)` is -1.

**Idea:** Map key to value, map key to frequency, and map frequency to an `OrderedDict` of keys (oldest first). Track `min_freq`.

```python
from collections import defaultdict, OrderedDict

class LFUCache:
    def __init__(self, capacity):
        self.cap = capacity
        self.min_freq = 0
        self.kv = {}                          # key -> value
        self.kf = {}                          # key -> frequency
        self.fk = defaultdict(OrderedDict)    # freq -> keys, LRU first

    def _touch(self, key):
        f = self.kf[key]
        del self.fk[f][key]
        if not self.fk[f]:
            del self.fk[f]
            if self.min_freq == f:
                self.min_freq += 1
        self.kf[key] = f + 1
        self.fk[f + 1][key] = None

    def get(self, key):
        if key not in self.kv:
            return -1
        self._touch(key)
        return self.kv[key]

    def put(self, key, value):
        if self.cap == 0:
            return
        if key in self.kv:
            self.kv[key] = value
            self._touch(key)
            return
        if len(self.kv) == self.cap:
            old, _ = self.fk[self.min_freq].popitem(last=False)
            if not self.fk[self.min_freq]:
                del self.fk[self.min_freq]
            del self.kv[old]
            del self.kf[old]
        self.kv[key] = value
        self.kf[key] = 1
        self.fk[1][key] = None
        self.min_freq = 1
```
**Complexity:** O(1) per operation, O(capacity) space.

---

## 23. Merge k Sorted Lists (Hard)

**Problem:** Merge `k` sorted linked lists into one sorted linked list.

**Example:** `[[1,4,5],[1,3,4],[2,6]]` gives `[1,1,2,3,4,4,5,6]`.

**Idea:** A min-heap holds the current head of each list. The index in the tuple breaks ties so nodes are never compared.

```python
import heapq

def mergeKLists(lists):
    heap = [(node.val, i, node) for i, node in enumerate(lists) if node]
    heapq.heapify(heap)
    dummy = tail = ListNode()
    while heap:
        _, i, node = heapq.heappop(heap)
        tail.next = node
        tail = node
        if node.next:
            heapq.heappush(heap, (node.next.val, i, node.next))
    return dummy.next
```
**Complexity:** O(N log k) time, O(k) space, where `N` is the total node count.

---

## 207. Course Schedule (Medium)

**Problem:** There are `numCourses` courses and prerequisite pairs `[a, b]` meaning you must take `b` before `a`. Return whether all courses can be finished, which means the graph has no cycle.

**Example:** `n=2, [[1,0]]` is True. `n=2, [[1,0],[0,1]]` is False.

**Idea:** Kahn's algorithm (BFS topological sort). If every course gets processed, there is no cycle.

```python
from collections import deque

def canFinish(numCourses, prerequisites):
    g = [[] for _ in range(numCourses)]
    indeg = [0] * numCourses
    for a, b in prerequisites:
        g[b].append(a)
        indeg[a] += 1
    q = deque(i for i in range(numCourses) if indeg[i] == 0)
    done = 0
    while q:
        u = q.popleft()
        done += 1
        for v in g[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    return done == numCourses
```
**Complexity:** O(V + E).

---

## 210. Course Schedule II (Medium)

**Problem:** Same setup as 207, but return a valid order to take all courses, or `[]` if impossible.

**Example:** `n=4, [[1,0],[2,0],[3,1],[3,2]]` gives `[0,1,2,3]` or `[0,2,1,3]`.

**Idea:** Kahn's algorithm again, recording the processing order.

```python
from collections import deque

def findOrder(numCourses, prerequisites):
    g = [[] for _ in range(numCourses)]
    indeg = [0] * numCourses
    for a, b in prerequisites:
        g[b].append(a)
        indeg[a] += 1
    q = deque(i for i in range(numCourses) if indeg[i] == 0)
    order = []
    while q:
        u = q.popleft()
        order.append(u)
        for v in g[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    return order if len(order) == numCourses else []
```
**Complexity:** O(V + E).

---

## 139. Word Break (Medium)

**Problem:** Given a string `s` and a dictionary `wordDict`, return whether `s` can be split into a sequence of dictionary words (words may be reused).

**Example:** `s="leetcode", ["leet","code"]` is True. `s="catsandog", ["cats","dog","sand","and","cat"]` is False.

**Idea:** `dp[i]` means the prefix `s[:i]` can be segmented. `dp[i]` is True if some `j < i` has `dp[j]` and `s[j:i]` is a word. Only check `j` within the longest word length.

```python
def wordBreak(s, wordDict):
    words = set(wordDict)
    maxlen = max(map(len, words))
    dp = [False] * (len(s) + 1)
    dp[0] = True
    for i in range(1, len(s) + 1):
        for j in range(max(0, i - maxlen), i):
            if dp[j] and s[j:i] in words:
                dp[i] = True
                break
    return dp[-1]
```
**Complexity:** O(n * L) substring checks, where `L` is the max word length.

---

## 215. Kth Largest Element in an Array (Medium)

**Problem:** Return the k-th largest element of `nums` (by sorted order, not distinct values).

**Example:** `[3,2,1,5,6,4], k=2` gives `5`.

**Idea:** Keep a min-heap of the `k` largest values seen. Its root is the answer. (Quickselect gives O(n) average.)

```python
import heapq

def findKthLargest(nums, k):
    heap = nums[:k]
    heapq.heapify(heap)
    for x in nums[k:]:
        if x > heap[0]:
            heapq.heapreplace(heap, x)
    return heap[0]
```
**Complexity:** O(n log k) time, O(k) space.

---

## 347. Top K Frequent Elements (Medium)

**Problem:** Return the `k` most frequent elements of `nums`, in any order.

**Example:** `[1,1,1,2,2,3], k=2` gives `[1,2]`.

**Idea:** Count with `Counter`, then bucket by frequency and read from the highest bucket down. This is O(n) and beats a heap.

```python
from collections import Counter

def topKFrequent(nums, k):
    cnt = Counter(nums)
    buckets = [[] for _ in range(len(nums) + 1)]
    for x, c in cnt.items():
        buckets[c].append(x)
    res = []
    for c in range(len(buckets) - 1, 0, -1):
        for x in buckets[c]:
            res.append(x)
            if len(res) == k:
                return res
```
One-liner alternative: `[x for x, _ in Counter(nums).most_common(k)]` (O(n log k)).

**Complexity:** O(n) time, O(n) space.

---

## 295. Find Median from Data Stream (Hard)

**Problem:** Design a structure with `addNum(num)` and `findMedian()` for a stream of integers.

**Example:** `addNum(1)`, `addNum(2)`, `findMedian()` is `1.5`, `addNum(3)`, `findMedian()` is `2.0`.

**Idea:** Two heaps. `lo` is a max-heap (stored negated) with the smaller half, and `hi` is a min-heap with the larger half. Keep `len(lo)` equal to `len(hi)` or one greater.

```python
import heapq

class MedianFinder:
    def __init__(self):
        self.lo = []    # max-heap via negation
        self.hi = []    # min-heap

    def addNum(self, num):
        heapq.heappush(self.lo, -num)
        heapq.heappush(self.hi, -heapq.heappop(self.lo))
        if len(self.hi) > len(self.lo):
            heapq.heappush(self.lo, -heapq.heappop(self.hi))

    def findMedian(self):
        if len(self.lo) > len(self.hi):
            return float(-self.lo[0])
        return (-self.lo[0] + self.hi[0]) / 2
```
**Complexity:** `addNum` is O(log n), `findMedian` is O(1).
