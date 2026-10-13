"""
Answers for the questions collected in online_question.py
(Confluent / IBM live-coding + HackerRank style problems).

Run:  python3 online_question_answers.py
Every section has its own tests (plain asserts) at the bottom of the file.

Index
  1.  Best price with value meals (<= 3 unique wanted items)   -> best_price
  2.  Warehouse Loading: Target Reach                           -> can_reach_target
  3.  Tail -N (streaming + seek-from-end)                       -> tail_stream / tail_seek
  4.  Random Queue ADT (equality, thread safety, RLE)           -> RandomQueue / rle_equal
  5.  Text search: word / phrase, + doc-id search engine        -> TextIndex / SearchEngine
  6.  Silent Sensor Detector                                    -> SensorHealth
  7.  Retrieve Token List                                       -> TokenStore
  8.  Message Logger                                            -> MessageLogger
  9.  Min start value for positive step-by-step sum             -> min_start_value
  10. Function overloading with variadic args                   -> FunctionRegistry
  11. KV store with Get / GetAverage / GetMax                   -> StatsKV
  12. Sliding-window store (put / get / average)                -> WindowStore
  13. Sudoku: validate + solve                                  -> is_valid_board / solve_sudoku
  14. Pod logs with global increment + pop-min                  -> PodLogs
  15. Time based key-value store                                -> TimeMap
  16. Max concurrent processes                                  -> max_concurrent
  17. Combination sum + memoization follow-ups                  -> combination_sum*

Not implemented: "monster cost" (statement has no cost definition / I/O).
"""

from __future__ import annotations

import bisect
import heapq
import os
import random
import re
import tempfile
import threading
from collections import Counter, defaultdict, deque
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any, Dict, Hashable, Iterable, List, Optional, Sequence, Tuple


# ---------------------------------------------------------------------------
# 1. Best price with value meals
# ---------------------------------------------------------------------------
# Problem: Restaurant ordering app that finds minimum cost to get all desired items
# using individual items and discounted value meal bundles.
#
# Input: List of menu items [(price, "item1, item2, ...")], list of wanted items
# Constraint: User wants maximum of 3 unique items
#
# Example: 
#   menu = [(5.00, "pizza"), (8.00, "sandwich, coke"), (4.00, "pasta"), 
#           (2.00, "coke"), (6.00, "pasta, coke, pizza"), 
#           (8.00, "burger, coke, pizza"), (5.00, "sandwich")]
#   wanted = ["burger", "pasta"]
#   Output: 12 ("burger, coke, pizza" for 8 + "pasta" for 4)
#
# Algorithm: Bitmask DP over wanted items (<= 3 -> only 8 states)
#   dp[mask] = min cost to cover AT LEAST the items in mask
#   dp[mask] = min(dp[mask & ~meal_mask] + price) for meals touching mask
# Prices converted to integer cents to avoid float error.
# Time O(2^k * M), space O(2^k). Returns None if some item can't be bought.
def get_best_price(menu: list[tuple[float, str]], wanted: list[str]) -> float | None:
    """
    Finds the minimum total cost to acquire all desired items using individual 
    menu items and/or bundle value meals.
    
    Args:
        menu: List of tuples (price, "item1, item2, ...")
        wanted: List of requested items (max 3 items)
        
    Returns:
        Minimum total price (float), or None if coverage is impossible.
    """
    if not wanted:
        return 0.0

    k = len(wanted)
    item_to_bit = {item: i for i, item in enumerate(wanted)}
    
    # Process menu items into (price_in_cents, meal_bitmask)
    processed_menu = []
    for price, item_str in menu:
        price_cents = round(price * 100)
        items = [i.strip() for i in item_str.split(",") if i.strip()]
        
        meal_mask = 0
        for item in items:
            if item in item_to_bit:
                meal_mask |= (1 << item_to_bit[item])
                
        # Only keep menu entries that contribute at least 1 wanted item
        if meal_mask > 0:
            processed_menu.append((price_cents, meal_mask))
            
    num_states = 1 << k
    dp = [float('inf')] * num_states
    dp[0] = 0

    # DP State Transition: Fill masks from 0 up to (2^k - 1)
    for mask in range(num_states):
        if dp[mask] == float('inf'):
            continue
            
        for price_cents, meal_mask in processed_menu:
            next_mask = mask | meal_mask
            if dp[mask] + price_cents < dp[next_mask]:
                dp[next_mask] = dp[mask] + price_cents

    full_mask = num_states - 1
    min_cents = dp[full_mask]
    
    return min_cents / 100.0 if min_cents != float('inf') else None


# ---------------------------------------------------------------------------
# Test Execution
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    menu_data = [
        (5.00, "pizza"),
        (8.00, "sandwich, coke"),
        (4.00, "pasta"),
        (2.00, "coke"),
        (6.00, "pasta, coke, pizza"),
        (8.00, "burger, coke, pizza"),
        (5.00, "sandwich")
    ]
    wanted_items = ["burger", "pasta"]
    
    result = min_cost_for_items(menu_data, wanted_items)
    print(f"Minimum Cost: {result}")  # Output: 12.0


# ---------------------------------------------------------------------------
# Example Usage / Test Case
# ---------------------------------------------------------------------------
menu = [
    (8.00, "burger, coke, pizza"),
    (4.00, "pasta"),
    (5.00, "burger, coke"),
    (6.00, "pizza"),
    (3.00, "coke")
]

wanted = ["burger", "coke", "pizza", "pasta"]

best_price = get_best_price(menu, wanted)
print(f"Minimum cost: ${best_price:.2f}")  # Output: Minimum cost: $12.00


# ---------------------------------------------------------------------------
# 2. Warehouse Loading: Target Reach
# ---------------------------------------------------------------------------
# Problem: Automated loading dock robot with N operations (load/unload weights)
# Determine if there exists an ordering where some prefix sum equals target weight
#
# Input: Sequence of weights W (positive = load, negative = unload), target weight
# Key question: Are negative running totals allowed during execution?
#
# Examples:
#   W = [2, -1, 4], target = 1 -> True (order [-1, 2, 4]: -1, then 1)
#   W = [-3, 5], target = 2 -> True if negatives allowed, False if not
#
# Algorithm: Subset sum problem - track reachable sums
#   If negatives allowed: plain subset sum
#   If negatives not allowed: same but target must be >= 0, positives first
# include_empty: whether the empty prefix (total 0 before any op) counts.
# DP over reachable sums: O(N * range) time/space.
def can_reach_target(W: Sequence[int], target: int, allow_negative: bool = True,
                     include_empty: bool = True) -> bool:
    if not allow_negative and target < 0:
        return False
    sums = {0} if include_empty else set()
    for w in W:
        sums |= {s + w for s in sums} | {w}
        if target in sums:
            return True
    return target in sums


# ---------------------------------------------------------------------------
# 3. Tail -N
# ---------------------------------------------------------------------------
# Problem: Implement Unix tail command that returns last N lines from a file/stream
# Requirements: Bounded memory usage (O(N)), handle large files efficiently
#
# Two implementations:
# (a) streaming: bounded deque, O(file) time, O(N) memory. Works on stdin/pipes.
# (b) seek-from-end: read fixed size blocks backwards until n+1 newlines found
#     Only touches tail of file -> O(bytes in last n lines). Works on bytes.
#
# Edge cases: N=0, total lines < N, non-newline terminated final lines,
# trailing newline at EOF not treated as extra empty line.
def tail_stream(lines: Iterable[str], n: int) -> List[str]:
    if n <= 0:
        return []
    buf: deque = deque(maxlen=n)
    for line in lines:
        buf.append(line.rstrip("\r\n"))
    return list(buf)


# (b) seek-from-end: read fixed size blocks backwards until we've seen n+1
# newlines. Touches only ~the tail of the file -> O(bytes in last n lines).
# Works on bytes, so a multi-byte UTF-8 char is never split (b"\n" can't occur
# inside a multi-byte sequence); decoding happens per whole line.
def tail_seek(path: str, n: int, block: int = 8192) -> List[str]:
    if n <= 0:
        return []
    with open(path, "rb") as f:
        pos = f.seek(0, os.SEEK_END)
        data = b""
        newlines = 0
        while pos > 0 and newlines <= n:
            step = min(block, pos)
            pos -= step
            f.seek(pos)
            chunk = f.read(step)
            newlines += chunk.count(b"\n")
            data = chunk + data
    lines = data.split(b"\n")
    if lines and lines[-1] == b"":  # trailing newline is not an extra empty line
        lines.pop()
    return [l.rstrip(b"\r").decode("utf-8", "replace") for l in lines[-n:]]


# ---------------------------------------------------------------------------
# 4. Random Queue ADT
# ---------------------------------------------------------------------------
# Problem: Queue that removes elements uniformly at random rather than FIFO
# Core operations: enqueue(x), dequeue() (random removal), peek(), size()
#
# Implementation: Dynamic array; dequeue swaps random slot with last, pops last -> O(1)
# Thread safety: RLock guards all operations atomically
# Equality: Multiset equality via Counter (same elements, same frequencies)
#
# Part D: RLE-backed equality - compare multisets from run-length encoded
# representations without expanding repeated elements
# Time O(R + V) where R = total runs, V = distinct values
class RandomQueue:
    def __init__(self, items: Iterable[Hashable] = (), rng: Optional[random.Random] = None):
        self._items: List[Hashable] = list(items)
        self._rng = rng or random.Random()
        self._lock = threading.RLock()

    def enqueue(self, x: Hashable) -> None:
        with self._lock:
            self._items.append(x)

    def dequeue(self) -> Hashable:
        with self._lock:
            if not self._items:
                raise IndexError("dequeue from empty RandomQueue")
            i = self._rng.randrange(len(self._items))
            self._items[i], self._items[-1] = self._items[-1], self._items[i]
            return self._items.pop()

    def peek(self) -> Hashable:
        with self._lock:
            if not self._items:
                raise IndexError("peek from empty RandomQueue")
            return self._items[self._rng.randrange(len(self._items))]

    def size(self) -> int:
        with self._lock:
            return len(self._items)

    __len__ = size

    def counts(self) -> Counter:
        with self._lock:
            return Counter(self._items)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RandomQueue):
            return NotImplemented
        if self is other:
            return True
        return self.counts() == other.counts()

    __hash__ = None  # mutable -> unhashable


# Part D: equality of two run-length encoded queues without expanding runs.
# runs = [(value, run_length), ...]; same value may appear in several runs.
def rle_equal(runs_a: Iterable[Tuple[Hashable, int]],
              runs_b: Iterable[Tuple[Hashable, int]]) -> bool:
    def agg(runs):
        c: Counter = Counter()
        for v, k in runs:
            if k < 0:
                raise ValueError("negative run length")
            if k:
                c[v] += k
        return c
    return agg(runs_a) == agg(runs_b)  # O(R + V)


# ---------------------------------------------------------------------------
# 5. Text search
# ---------------------------------------------------------------------------
_TOKEN = re.compile(r"[^\W_]+")  # runs of letters/digits (unicode aware)


def tokenize(text: str) -> List[str]:
    return _TOKEN.findall(text.lower())


class TextIndex:
    """Text search engine for word and phrase matching in multi-line text.
    
    Tokenization: Split on non-alphanumeric chars, case-insensitive matching
    Tokens continue across line breaks.
    
    Query types:
      WORD <word>: Count occurrences of individual token
      PHRASE <phrase>: Count consecutive token sequences matching phrase
    """

    def __init__(self, lines: Iterable[str]):
        self.tokens: List[str] = []
        for line in lines:
            self.tokens.extend(tokenize(line))
        self.pos: Dict[str, List[int]] = defaultdict(list)  # word -> sorted positions
        for i, t in enumerate(self.tokens):
            self.pos[t].append(i)

    def count_word(self, word: str) -> int:  # O(1)
        t = tokenize(word)
        return len(self.pos.get(t[0], ())) if len(t) == 1 else 0

    def count_phrase(self, phrase: str) -> int:
        ph = tokenize(phrase)
        if not ph:
            return 0
        if len(ph) == 1:
            return len(self.pos.get(ph[0], ()))
        # Walk the rarest word's positions, check the rest via binary search.
        offs = min(range(len(ph)), key=lambda i: len(self.pos.get(ph[i], ())))
        total = 0
        for p in self.pos.get(ph[offs], ()):
            start = p - offs
            if start < 0 or start + len(ph) > len(self.tokens):
                continue
            if all(self._has(ph[i], start + i) for i in range(len(ph))):
                total += 1
        return total

    def _has(self, word: str, position: int) -> bool:
        lst = self.pos.get(word)
        if not lst:
            return False
        j = bisect.bisect_left(lst, position)
        return j < len(lst) and lst[j] == position


"""Inverted index returning DOCUMENT IDS. Phrase must be inside one doc.
index: word -> {doc_id: [positions]} [ NEED TO PRACTICE]"""

import re
from collections import defaultdict


class SearchEngine:

    def __init__(self):
        # Index structure:
        # { word: { doc_id: [position_1, position_2, ...] } }
        self.index = defaultdict(lambda: defaultdict(list))

    def _tokenize(self, text: str) -> list[str]:
        """Tokenizes text into lowercase word tokens, removing punctuation."""
        return re.findall(r"\b\w+\b", text.lower())

    # text = "Hello, world! Cloud-computing is 100% awesome."
    # Output: ['hello', 'world', 'cloud', 'computing', 'is', '100', 'awesome']

    def add_document(self, doc_id: int, text: str) -> None:
        """Indexes a single document with token positions."""
        tokens = self._tokenize(text)
        for pos, token in enumerate(tokens):
            self.index[token][doc_id].append(pos)

    def search(self, phrase: str) -> list[int]:
        """Searches for an exact phrase across all indexed documents."""
        tokens = self._tokenize(phrase)
        if not tokens:
            return []

        # Step 1: Single-word query direct lookup
        if len(tokens) == 1:
            return sorted(self.index[tokens[0]].keys())

        # Step 2: Find document IDs containing ALL words in the query phrase
        # Optimization: Sort query tokens by document frequency to intersect smallest set first
        unique_tokens = list(set(tokens))
        unique_tokens.sort(key=lambda t: len(self.index[t]))

        matching_doc_ids = set(self.index[unique_tokens[0]].keys())
        for token in unique_tokens[1:]:
            matching_doc_ids &= set(self.index[token].keys())
            if not matching_doc_ids:
                return []

        # Step 3: Positional continuity check for remaining candidate documents
        result = []
        first_token = tokens[0]

        for doc_id in matching_doc_ids:
            # Check every occurrence position of the first word in the document
            first_word_positions = self.index[first_token][doc_id]

            for start_pos in first_word_positions:
                is_phrase_match = True

                # Subsequent tokens must exist at pos + offset
                for offset, token in enumerate(tokens[1:], start=1):
                    target_pos = start_pos + offset
                    if target_pos not in self.index[token][doc_id]:
                        is_phrase_match = False
                        break

                if is_phrase_match:
                    result.append(doc_id)
                    break  # Found match in this doc, move to next doc

        return sorted(result)


# --- Example Usage ---

docs = [
    (
        1,
        "Cloud computing is the on-demand availability of computer system"
        " resources.",
    ),
    (
        2,
        "One integrated service for metrics uptime cloud monitoring dashboards"
        " and alerts reduces time spent navigating between systems.",
    ),
    (
        3,
        "Monitor entire cloud infrastructure, whether in the cloud computing"
        " is or in virtualized data centers.",
    ),
]

engine = SearchEngine()
for doc_id, text in docs:
    engine.add_document(doc_id, text)

print(engine.search("cloud"))  # Output: [1, 2, 3]
print(engine.search("cloud monitoring"))  # Output: [2]
print(engine.search("Cloud computing is"))  # Output: [1, 3]



# ---------------------------------------------------------------------------
# 6. Silent Sensor Detector  (statement is incomplete -> assumptions stated)
# ---------------------------------------------------------------------------
# Assumed rule: sensor is STABLE at time T iff it has a ping in [T-K, T]
# (inclusive). Unknown sensor / no pings -> UNSTABLE. Pings may arrive out of
# order and T may be historical -> keep a sorted list per sensor + bisect.
# ping O(log n + n) worst case for insort, query O(log n).
class SensorHealth:
    def __init__(self, k: int):
        self.k = k
        self.pings: Dict[str, List[int]] = defaultdict(list)

    def ping(self, sensor: str, ts: int) -> None:
        bisect.insort(self.pings[sensor], ts)

    def status(self, sensor: str, t: int) -> str:
        ts = self.pings.get(sensor)
        if not ts:
            return "UNSTABLE"
        i = bisect.bisect_right(ts, t) - 1  # latest ping <= t
        return "STABLE" if i >= 0 and ts[i] >= t - self.k else "UNSTABLE"

#     Sorted array:

# a = [1, 2, 2, 2, 4]

#                  ↓
#              2 2 2
#              ↑   ↑
#            left right

# bisect_left(a, 2)  -> 1
# bisect_right(a, 2) -> 4

# bisect = bisect_right
# insort = insort_right



# ---------------------------------------------------------------------------
# 7. Retrieve Token List  (statement is vague -> assumptions stated)
# ---------------------------------------------------------------------------
# Assumptions: each token has a create_time and a TTL; get(token, now) returns
# the token record if it exists and has not expired (else None);
# list_tokens(now) returns the active tokens ordered by create_time.

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
            self.active_tokens.discard(record)

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


# ---------------------------------------------------------------------------
# 8. Message Logger (LeetCode 359)
# ---------------------------------------------------------------------------
# message -> last printed timestamp. O(1) average. A FIFO of printed messages
# optionally reclaims memory (timestamps arrive non-decreasing).
class MessageLogger:
    def __init__(self, cooldown: int = 10):
        self.cooldown = cooldown
        self.last: Dict[str, int] = {}
        self.fifo: deque = deque()  # (timestamp, message) of prints

    def should_print_message(self, timestamp: int, message: str) -> bool:
        while self.fifo and timestamp - self.fifo[0][0] >= self.cooldown:
            ts, msg = self.fifo.popleft()
            if self.last.get(msg) == ts:
                del self.last[msg]
        if message in self.last:
            return False
        self.last[message] = timestamp
        self.fifo.append((timestamp, message))
        return True


# ---------------------------------------------------------------------------
# 9. Minimum value to get positive step-by-step sum (LeetCode 1413)
# ---------------------------------------------------------------------------
# x + minPrefix >= 1 -> x = 1 - minPrefix. minPrefix starts at 0 (empty prefix),
# so the result is always >= 1 already. O(n) time, O(1) space.
def min_start_value(nums: Sequence[int]) -> int:
    cur = low = 0
    for v in nums:
        cur += v
        low = min(low, cur)
    return 1 - low


# ---------------------------------------------------------------------------
# 10. Function overloading with variadic arguments
# ---------------------------------------------------------------------------
# Decision taken for the ambiguity in the prompt: the variadic (last) parameter
# matches ZERO or more args (so {"Integer"}+isCard matches []). Set
# allow_zero_variadic=False to require at least one.
@dataclass
class Function:
    name: str
    params: List[str]
    is_card: bool = False


class FunctionRegistry:
    def __init__(self, allow_zero_variadic: bool = True):
        self.funcs: List[Function] = []
        self.allow_zero = allow_zero_variadic

    def register(self, fn: Function) -> None:
        if fn.is_card and not fn.params:
            raise ValueError("variadic function needs a final parameter type")
        self.funcs.append(fn)

    def _matches(self, fn: Function, args: Sequence[str]) -> bool:
        if not fn.is_card:
            return list(args) == fn.params
        fixed, var = fn.params[:-1], fn.params[-1]
        min_args = len(fixed) if self.allow_zero else len(fixed) + 1
        if len(args) < min_args:
            return False
        return list(args[: len(fixed)]) == fixed and all(a == var for a in args[len(fixed):])

    def find(self, args: Sequence[str]) -> List[Function]:  # O(N * M)
        return [f for f in self.funcs if self._matches(f, args)]


# ---------------------------------------------------------------------------
# 11. KV store with Put / Get / GetAverage / GetMax
# ---------------------------------------------------------------------------
# dict for Get/Put, running sum for average (O(1)), max-heap with LAZY DELETION
# for max: an entry (-value, key) is stale if dict[key] != value. Put O(log n),
# GetMax amortized O(log n). (Strict worst-case O(1) max under arbitrary
# overwrites is not possible with comparison-based structures.)
class StatsKV:
    def __init__(self):
        self.d: Dict[Hashable, float] = {}
        self.total = 0
        self.heap: List[Tuple[float, Any]] = []

    def put(self, key: Hashable, value: float) -> None:
        self.total += value - self.d.get(key, 0)
        self.d[key] = value
        heapq.heappush(self.heap, (-value, _Key(key)))
        if len(self.heap) > 2 * len(self.d) + 16:  # compact stale entries
            self.heap = [(-v, _Key(k)) for k, v in self.d.items()]
            heapq.heapify(self.heap)

    def get(self, key: Hashable) -> Optional[float]:
        return self.d.get(key)

    def get_average(self) -> Optional[float]:
        return self.total / len(self.d) if self.d else None

    def get_max(self) -> Optional[float]:
        while self.heap:
            neg, wrapped = self.heap[0]
            if self.d.get(wrapped.key) == -neg:
                return -neg
            heapq.heappop(self.heap)  # stale
        return None


class _Key:
    """Wrapper so heap tuples never compare keys (keys may be unorderable)."""
    __slots__ = ("key",)

    def __init__(self, key):
        self.key = key

    def __lt__(self, other):
        return False


# ---------------------------------------------------------------------------
# 12. Sliding-window store: put / get / average   (window e.g. 1 hour)
# ---------------------------------------------------------------------------
# An entry written at time t is alive while now - t < window (boundary is an
# assumption: exactly `window` old counts as expired).
# map key -> (value, ts); deque of (ts, key) in insertion order for expiry;
# running sum / count. Re-putting a key leaves a stale deque entry; it is
# recognised on expiry because map[key].ts != ts (or key is gone).
class WindowStore:
    def __init__(self, window: int):
        self.window = window
        self.data: Dict[Hashable, Tuple[float, int]] = {}
        self.fifo: deque = deque()
        self.total = 0
        self.lock = threading.Lock()

    def _expire(self, now: int) -> None:
        while self.fifo and now - self.fifo[0][0] >= self.window:
            ts, key = self.fifo.popleft()
            cur = self.data.get(key)
            if cur is not None and cur[1] == ts:
                self.total -= cur[0]
                del self.data[key]

    def put(self, now: int, key: Hashable, value: float) -> None:
        with self.lock:
            self._expire(now)
            if key in self.data:
                self.total -= self.data[key][0]
            self.data[key] = (value, now)
            self.total += value
            self.fifo.append((now, key))

    def get(self, now: int, key: Hashable) -> Optional[float]:
        with self.lock:
            self._expire(now)
            cur = self.data.get(key)
            return cur[0] if cur else None

    def average(self, now: int) -> Optional[float]:
        with self.lock:
            self._expire(now)
            return self.total / len(self.data) if self.data else None


# ---------------------------------------------------------------------------
# 13. Sudoku
# ---------------------------------------------------------------------------
# Board: 9x9 list of str, "." or "" = empty.
def _empty(c: str) -> bool:
    return c in (".", "", "0")


def is_valid_board(board: List[List[str]]) -> bool:
    rows = [set() for _ in range(9)]
    cols = [set() for _ in range(9)]
    boxes = [set() for _ in range(9)]
    for r in range(9):
        for c in range(9):
            v = board[r][c]
            if _empty(v):
                continue
            if v not in "123456789" or len(v) != 1:
                return False
            b = (r // 3) * 3 + c // 3
            if v in rows[r] or v in cols[c] or v in boxes[b]:
                return False
            rows[r].add(v); cols[c].add(v); boxes[b].add(v)
    return True


# Backtracking with bitmasks 
class Solution:
    def solveSudoku(self, board: list[list[str]]) -> None:
        """
        Do not return anything, modify board in-place instead.
        """
        rows = [0] * 9
        cols = [0] * 9
        boxes = [0] * 9
        empty_cells = []

        # 1. Initialize bitmasks and track empty cells
        for r in range(9):
            for c in range(9):
                if board[r][c] == '.':
                    empty_cells.append((r, c))
                else:
                    digit = int(board[r][c])
                    mask = 1 << digit
                    rows[r] |= mask
                    cols[c] |= mask
                    box_idx = (r // 3) * 3 + (c // 3)
                    boxes[box_idx] |= mask

        # 2. Backtracking using bitwise operations
        def backtrack(index: int) -> bool:
            if index == len(empty_cells):
                return True  # All empty cells filled successfully

            r, c = empty_cells[index]
            box_idx = (r // 3) * 3 + (c // 3)

            # Mask representing digits 1-9 currently taken across row, col, box
            used_mask = rows[r] | cols[c] | boxes[box_idx]

            for d in range(1, 10):
                bit = 1 << d
                if not (used_mask & bit):
                    # Place digit
                    board[r][c] = str(d)
                    rows[r] |= bit
                    cols[c] |= bit
                    boxes[box_idx] |= bit

                    if backtrack(index + 1):
                        return True

                    # Backtrack (remove digit)
                    board[r][c] = '.'
                    rows[r] ^= bit
                    cols[c] ^= bit
                    boxes[box_idx] ^= bit

            return False

        backtrack(0)


# ---------------------------------------------------------------------------
# 14. Pod logs with global increments and pop-min
# ---------------------------------------------------------------------------
# (Original statement unavailable; standard formulation.)
# Keep one global `offset`. Store value - offset in a min-heap. increment_all(d)
# is O(1) (offset += d); pop_min is O(log n).  Real value = stored + offset.
class PodLogs:
    def __init__(self):
        self.heap: List[Tuple[int, int, str]] = []
        self.offset = 0
        self.seq = 0  # tie-break so pod names are never compared

    def add(self, pod: str, value: int) -> None:
        self.seq += 1
        heapq.heappush(self.heap, (value - self.offset, self.seq, pod))

    def increment_all(self, delta: int) -> None:
        self.offset += delta

    def pop_min(self) -> Optional[Tuple[str, int]]:
        if not self.heap:
            return None
        stored, _, pod = heapq.heappop(self.heap)
        return pod, stored + self.offset

    def __len__(self) -> int:
        return len(self.heap)


# ---------------------------------------------------------------------------
# 15. Time based key-value store (LeetCode 981)
# ---------------------------------------------------------------------------
# set() timestamps are increasing per key -> append; get() = bisect for the
# latest timestamp <= t. set O(1), get O(log n).
class TimeMap:
    def __init__(self):
        self.times: Dict[str, List[int]] = defaultdict(list)
        self.vals: Dict[str, List[Any]] = defaultdict(list)

    def set(self, key: str, value: Any, ts: int) -> None:
        ts_list = self.times[key]
        if ts_list and ts < ts_list[-1]:  # tolerate out-of-order writes
            i = bisect.bisect_right(ts_list, ts)
            ts_list.insert(i, ts)
            self.vals[key].insert(i, value)
        else:
            ts_list.append(ts)
            self.vals[key].append(value)

    def get(self, key: str, ts: int) -> Optional[Any]:
        ts_list = self.times.get(key)
        if not ts_list:
            return None
        i = bisect.bisect_right(ts_list, ts) - 1
        return self.vals[key][i] if i >= 0 else None


# ---------------------------------------------------------------------------
# 16. Max concurrent processes
# ---------------------------------------------------------------------------
# Sweep line over events. Intervals are [start, end): a process ending at t does
# not overlap one starting at t, so end events sort before start events.
# O(n log n).
def max_concurrent(intervals: Sequence[Tuple[int, int]]) -> int:
    events = []
    for s, e in intervals:
        events.append((s, 1))
        events.append((e, -1))
    events.sort()  # (-1) < (+1) at equal time -> ends first
    cur = best = 0
    for _, d in events:
        cur += d
        best = max(best, cur)
    return best


# ---------------------------------------------------------------------------
# 17. Combination sum + memoization follow-ups
# ---------------------------------------------------------------------------
# (a) all unique combinations, each number reusable (LC 39): backtracking.
def combination_sum(candidates: Sequence[int], target: int) -> List[List[int]]:
    cands = sorted(set(candidates))
    out: List[List[int]] = []

    def go(start: int, remain: int, path: List[int]) -> None:
        if remain == 0:
            out.append(path[:])
            return
        for i in range(start, len(cands)):
            if cands[i] > remain:
                break
            path.append(cands[i])
            go(i, remain - cands[i], path)
            path.pop()

    go(0, target, [])
    return out


# (b) memoized COUNT of combinations (order ignored): O(target * len).
def combination_sum_count(candidates: Sequence[int], target: int) -> int:
    cands = sorted(set(c for c in candidates if c > 0))

    @lru_cache(maxsize=None)
    def go(i: int, remain: int) -> int:
        if remain == 0:
            return 1
        if i == len(cands) or remain < 0:
            return 0
        return go(i, remain - cands[i]) + go(i + 1, remain)

    return go(0, target)


# (c) memoized COUNT of ordered sequences (LC 377).
def combination_sum_perm_count(candidates: Sequence[int], target: int) -> int:
    cands = [c for c in set(candidates) if c > 0]

    @lru_cache(maxsize=None)
    def go(remain: int) -> int:
        if remain == 0:
            return 1
        return sum(go(remain - c) for c in cands if c <= remain)

    return go(target)


# you're given k v pairs

# funA: ['int','bool']
# funB: ['int','int']

# and queries like ['int','int']
# return all functions that match the description

# follow-up

# you're also given a flag is variadic

# funA: ['int','bool'] , isVariadic: true
# funC: ['int','int'] , isVariadic: false
# funB: ['int','int','int'] isVariadic: true

# and queries like ['int','int']
# return all functions that match the description

# e.g
# ['int','int'] = funC
# ['int','int','int', 'int'] = funB

# ===========================================================================
# Tests
# ===========================================================================
def test_best_price():
    menu = [(5.00, "pizza"), (8.00, "sandwich, coke"), (4.00, "pasta"), (2.00, "coke"),
            (6.00, "pasta, coke, pizza"), (8.00, "burger, coke, pizza"), (5.00, "sandwich")]
    assert get_best_price(menu, ["burger", "pasta"]) == 12
    assert get_best_price(menu, ["pizza"]) == 5
    assert get_best_price(menu, ["coke", "pizza", "pasta"]) == 6
    assert get_best_price(menu, ["salad"]) is None
    assert get_best_price(menu, []) == 0


def test_warehouse():
    assert can_reach_target([2, -1, 4], 1)
    assert can_reach_target([-3, 5], 2, allow_negative=True)
    assert can_reach_target([-3, 5], 2, allow_negative=False)  # order [5, -3]
    assert can_reach_target([1, 1, 1], 2)
    assert can_reach_target([-1, -2, -3], -3)
    assert not can_reach_target([-1, -2, -3], -3, allow_negative=False)
    assert not can_reach_target([2, 4], 3)
    # brute-force cross-check
    from itertools import permutations
    def brute(W, T, nonneg):
        for p in permutations(W):
            s = 0
            if T == 0:
                return True
            for x in p:
                s += x
                if nonneg and s < 0:
                    break
                if s == T:
                    return True
        return False
    rng = random.Random(1)
    for _ in range(300):
        W = [rng.randint(-5, 5) for _ in range(rng.randint(1, 5))]
        T = rng.randint(-6, 6)
        for nn in (False, True):
            assert can_reach_target(W, T, allow_negative=not nn) == brute(W, T, nn), (W, T, nn)


def test_tail():
    assert tail_stream(["a\n", "b\n", "c"], 2) == ["b", "c"]
    assert tail_stream(["a\n"], 0) == []
    assert tail_stream(["a\n", "b\n"], 5) == ["a", "b"]
    cases = ["", "a", "a\n", "a\nb\nc", "a\nb\nc\n", "\n\n", "x\r\ny\r\n", "héllo\n世界\nend\n"]
    big = "".join(f"line {i} é世\n" for i in range(2000))
    cases.append(big)
    cases.append(big.rstrip("\n"))
    for text in cases:
        with tempfile.NamedTemporaryFile("wb", delete=False) as tf:
            tf.write(text.encode("utf-8"))
        try:
            for n in (0, 1, 2, 3, 10, 5000):
                for block in (1, 7, 8192):
                    got = tail_seek(tf.name, n, block)
                    want = tail_stream(text.splitlines(True), n)
                    assert got == want, (text[:20], n, block, got[-2:], want[-2:])
        finally:
            os.unlink(tf.name)


def test_random_queue():
    q = RandomQueue([1, 2, 2, 3], rng=random.Random(0))
    assert q.size() == 4
    seen = sorted(q.dequeue() for _ in range(4))
    assert seen == [1, 2, 2, 3] and q.size() == 0
    try:
        q.dequeue(); assert False
    except IndexError:
        pass
    assert RandomQueue("aab") == RandomQueue("baa")
    assert RandomQueue("aab") != RandomQueue("abb")
    assert rle_equal([("a", 2), ("b", 1)], [("b", 1), ("a", 1), ("a", 1)])
    assert not rle_equal([("a", 2), ("b", 1)], [("a", 1), ("b", 2)])
    # concurrency: no item lost or duplicated
    q = RandomQueue()
    out: List[int] = []
    out_lock = threading.Lock()
    def prod(base):
        for i in range(500):
            q.enqueue(base + i)
    def cons():
        got = 0
        while got < 500:
            try:
                x = q.dequeue()
            except IndexError:
                continue
            with out_lock:
                out.append(x)
            got += 1
    ts = [threading.Thread(target=prod, args=(b,)) for b in (0, 1000)]
    ts += [threading.Thread(target=cons) for _ in range(2)]
    for t in ts: t.start()
    for t in ts: t.join()
    assert sorted(out) == sorted(list(range(500)) + list(range(1000, 1500)))


def test_text_search():
    idx = TextIndex(["Hello, world!", "world: hello. Hello hello"])
    assert idx.count_word("hello") == 4
    assert idx.count_word("WORLD") == 2
    assert idx.count_phrase("hello world") == 1
    assert idx.count_phrase("world hello") == 1
    assert idx.count_phrase("hello hello") == 2   # overlapping matches both count
    assert idx.count_phrase("hello x world") == 0
    assert idx.count_phrase("") == 0
    eng = SearchEngine()
    eng.add_document(1, "the quick brown fox")
    eng.add_document(2, "brown quick fox")
    eng.add_document(3, "A quick, brown fox jumps. Quick brown")
    assert eng.search_word("quick") == [1, 2, 3]
    assert eng.search_word("jumps") == [3]
    assert eng.search_phrase("quick brown") == [1, 3]
    assert eng.search_phrase("brown fox") == [1, 3]
    assert eng.search_phrase("fox brown") == []
    assert eng.search_phrase("nothing here") == []


def test_sensor():
    s = SensorHealth(k=10)
    s.ping("a", 100); s.ping("a", 50)
    assert s.status("a", 105) == "STABLE"
    assert s.status("a", 110) == "STABLE"   # inclusive boundary
    assert s.status("a", 111) == "UNSTABLE"
    assert s.status("a", 55) == "STABLE"    # historical query
    assert s.status("a", 40) == "UNSTABLE"
    assert s.status("zzz", 1) == "UNSTABLE"


def test_tokens():
    ts = TokenStore(ttl=10)
    ts.add("t1", 0); ts.add("t2", 5); ts.add("t3", 5)
    assert ts.get("t1", 9) == ("t1", 0)
    assert ts.get("t1", 10) is None
    assert ts.list_tokens(12) == [("t2", 5), ("t3", 5)]
    ts.add("t2", 20)
    assert ts.list_tokens(21) == [("t2", 20)]
    assert ts.get("nope", 0) is None


def test_message_logger():
    lg = MessageLogger(10)
    assert lg.should_print_message(0, "order received") is True
    assert lg.should_print_message(1, "order received") is False
    assert lg.should_print_message(2, "shipment sent") is True
    assert lg.should_print_message(11, "order received") is True
    assert lg.should_print_message(12, "shipment sent") is True  # 12-2 = 10 >= 10
    assert lg.should_print_message(13, "shipment sent") is False


def test_min_start_value():
    assert min_start_value([-3, 2, -3, 4, 2]) == 5
    assert min_start_value([1, 2]) == 1
    assert min_start_value([1, -2, -3]) == 5
    assert min_start_value([]) == 1


def test_function_registry():
    r = FunctionRegistry()
    r.register(Function("f", ["Integer", "Boolean"]))
    r.register(Function("g", ["Integer"], True))
    r.register(Function("h", ["Integer"], True))
    r.register(Function("k", ["String", "Integer"], True))
    names = lambda a: sorted(f.name for f in r.find(a))
    assert names(["Integer", "Boolean"]) == ["f"]
    assert names(["Integer"]) == ["g", "h"]       # both variadics; duplicates returned
    assert names(["Integer"] * 3) == ["g", "h"]
    assert names([]) == ["g", "h"]                # zero variadic args allowed
    assert names(["String"]) == ["k"]
    assert names(["Integer", "String"]) == []
    assert names(["String", "Integer", "Integer"]) == ["k"]
    strict = FunctionRegistry(allow_zero_variadic=False)
    strict.register(Function("g", ["Integer"], True))
    assert strict.find([]) == []
    try:
        r.register(Function("bad", [], True)); assert False
    except ValueError:
        pass


def test_stats_kv():
    kv = StatsKV()
    assert kv.get_max() is None and kv.get_average() is None
    kv.put("a", 8); kv.put("b", 5)
    assert kv.get_max() == 8 and kv.get_average() == 6.5
    kv.put("a", 2)  # overwrites the current max
    assert kv.get_max() == 5 and kv.get_average() == 3.5 and kv.get("a") == 2
    kv.put("a", 5)
    assert kv.get_max() == 5
    # randomized check vs brute force (also exercises heap compaction)
    rng = random.Random(7)
    kv, ref = StatsKV(), {}
    for _ in range(3000):
        k, v = rng.randint(0, 20), rng.randint(-50, 50)
        kv.put(k, v); ref[k] = v
        assert kv.get_max() == max(ref.values())
        assert abs(kv.get_average() - sum(ref.values()) / len(ref)) < 1e-9


def test_window_store():
    w = WindowStore(60)  # minutes
    w.put(0, "A", 10)
    w.put(10, "B", 20)
    assert w.average(30) == 15
    assert w.average(65) == 20
    assert w.get(68, "B") == 20
    assert w.get(68, "A") is None
    w.put(75, "A", 30)
    assert w.average(110) == 30
    # overwrite keeps sum/count right and the stale deque entry is harmless
    w = WindowStore(60)
    w.put(0, "A", 10); w.put(30, "A", 50)
    assert w.average(31) == 50
    assert w.get(61, "A") == 50      # old entry expired, new one must survive
    assert w.get(90, "A") is None


def test_sudoku():
    puzzle = ["53..7....", "6..195...", ".98....6.", "8...6...3", "4..8.3..1",
              "7...2...6", ".6....28.", "...419..5", "....8..79"]
    board = [list(r) for r in puzzle]
    assert is_valid_board(board)
    sol = solve_sudoku(board)
    assert sol is not None and is_valid_board(sol)
    assert all(len(set(row)) == 9 and "." not in row for row in sol)
    assert all(len({sol[r][c] for r in range(9)}) == 9 for c in range(9))
    assert all(len({sol[br + i][bc + j] for i in range(3) for j in range(3)}) == 9
               for br in (0, 3, 6) for bc in (0, 3, 6))
    assert [list(r) for r in puzzle] == board          # input untouched
    assert sol[0] == list("534678912")
    bad = [list(r) for r in puzzle]; bad[0][2] = "5"   # duplicate 5 in row 0
    assert not is_valid_board(bad) and solve_sudoku(bad) is None
    # valid but unsolvable: cell (0,8) needs a 9 but column 8 already has one
    unsolv = [["."] * 9 for _ in range(9)]
    unsolv[0] = list("12345678.")
    unsolv[1][8] = "9"
    assert is_valid_board(unsolv) and solve_sudoku(unsolv) is None
    assert solve_sudoku([["."] * 9 for _ in range(9)]) is not None  # empty board


def test_pod_logs():
    p = PodLogs()
    assert p.pop_min() is None
    p.add("a", 5); p.add("b", 3)
    p.increment_all(10)
    p.add("c", 1)             # real value 1; older ones are 15 and 13
    assert p.pop_min() == ("c", 1)
    p.increment_all(2)
    assert p.pop_min() == ("b", 15)
    assert p.pop_min() == ("a", 17)
    assert len(p) == 0


def test_time_map():
    tm = TimeMap()
    tm.set("foo", "bar", 1)
    assert tm.get("foo", 1) == "bar"
    assert tm.get("foo", 3) == "bar"
    tm.set("foo", "bar2", 4)
    assert tm.get("foo", 4) == "bar2" and tm.get("foo", 5) == "bar2"
    assert tm.get("foo", 0) is None and tm.get("nope", 1) is None
    tm.set("foo", "mid", 2)   # out of order
    assert tm.get("foo", 3) == "mid"


def test_max_concurrent():
    assert max_concurrent([(1, 4), (2, 5), (7, 9)]) == 2
    assert max_concurrent([(1, 2), (2, 3)]) == 1   # touching intervals don't overlap
    assert max_concurrent([(0, 10), (1, 9), (2, 8)]) == 3
    assert max_concurrent([]) == 0


def test_combination_sum():
    assert combination_sum([2, 3, 6, 7], 7) == [[2, 2, 3], [7]]
    assert combination_sum([2], 1) == []
    assert combination_sum_count([2, 3, 6, 7], 7) == 2
    assert combination_sum_count([1, 2, 5], 11) == 11
    assert combination_sum_perm_count([1, 2, 3], 4) == 7   # LC 377
    assert combination_sum_perm_count([9], 3) == 0


def main():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for t in tests:
        t()
        print(f"ok  {t.__name__}")
    print(f"{len(tests)} test groups passed")


if __name__ == "__main__":
    main()
