# Confluent Interview Solutions

Thorough solutions with detailed reasoning for **why** each approach was chosen — trade-offs,
alternatives considered, and complexity analysis. Built from the question frequency data in
`confluent_interview_questions.md` (LeetCode Discuss, Confluent tag, 75 posts).

> **How to use this in the interview:** For each problem, say the approach out loud *before*
> coding ("I'm going to use X because..."). Interviewers at Confluent reward explicit
> trade-off discussion — especially around concurrency, which comes up in nearly every
> coding round. Fully running code is expected on-site; don't leave stubs.

---

# PART 1 — CODING

---

## 1. Key-Value Store with TTL + `get_average()` (WindowedMap)

**Frequency:** 8 posts — the single most-asked Confluent coding question.

### Problem restatement (as Confluent asks it)

> Implement a key-value store where each entry expires `EXPIRY_TIME` milliseconds after it is
> written. Data arrives with monotonically increasing timestamps.
>
> - `put(key, value, timestamp)` — store the value.
> - `get(key, timestamp)` — return the value if it exists and has not expired, else `None`.
> - `get_average(timestamp)` — return the average of all **non-expired** values.
>
> Follow-ups: make it thread-safe; discuss strong vs. eventual consistency; handle out-of-order
> timestamps.

### Solution approach and WHY

**Core data structure: hash map + min-heap (or deque) for expirations + running sum.**

- **Why a hash map for storage:** `put`/`get` must be O(1) average. A hash map keyed by `key`
  storing `(value, expiry_time)` is the natural choice. Alternative: balanced BST — O(log n)
  per op with no benefit, since we never need ordering by key.
- **Why a min-heap (or queue) for expirations instead of scanning:** `get_average()` needs the
  set of *live* entries. Naively scanning all entries on every call is O(n). Because timestamps
  arrive in **increasing order**, expirations also leave in increasing order — so a FIFO
  structure works. A min-heap keyed by expiry time gives O(log n) eviction and handles the
  general case (including out-of-order timestamps in the follow-up). If the interviewer
  guarantees increasing timestamps, a **deque is strictly better**: O(1) amortized eviction,
  since expiries pop from the left in order. Say this out loud — it shows you read the
  constraints.
- **Why a running sum + count instead of recomputing:** `get_average()` in O(1) requires
  maintaining `live_sum` and `live_count` incrementally: on `put`, add; on eviction, subtract.
  Recomputing over all entries is O(n) per call — unacceptable if `get_average` is called
  frequently (it is, in the streaming-metrics framing).
- **Overwrite handling:** if `put` overwrites an existing live key, subtract the old value from
  `live_sum` first, and mark the old heap entry stale (lazy deletion) or remove it. Lazy
  deletion via a version/validity check in the map is simplest and O(1).
- **Why lazy eviction on read (not a background thread):** A background sweeper thread adds
  concurrency complexity and doesn't guarantee freshness anyway. Evicting expired entries at
  the start of every public method ("evict-then-operate") keeps the code single-threaded
  simple and is correct as long as every method evicts first. Mention the alternative
  (dedicated cleaner thread with a condition variable) and why you'd avoid it unless
  `get_average` latency is critical.

### Complexity

| Operation | Time | Space |
|---|---|---|
| `put` | O(log n) with heap; O(1) amortized with deque + increasing timestamps | O(n) |
| `get` | O(log n) amortized (eviction) / O(1) | O(n) |
| `get_average` | O(1) after O(k log n) eviction of k expired entries | O(n) |

Reasoning: each entry is pushed and popped from the expiry structure at most once, so total
eviction work across the lifetime is O(n log n) (heap) — amortized O(log n) per op. The
running sum makes the average itself O(1).

### Reference implementation

```python
import heapq
import threading

class WindowedMap:
    """
    Key-value store with per-entry TTL and O(1) average over live values.

    Design choices:
    - dict for O(1) key lookup
    - min-heap of (expiry, key, value, version) for eviction; a deque would also
      work if timestamps are guaranteed increasing (O(1) amortized eviction)
    - running live_sum / live_count so get_average() is O(1)
    - lazy deletion: heap entries carry a version; stale entries are skipped
    - single RLock around public methods for thread safety (see follow-ups)
    """

    def __init__(self, expiry_ms: int):
        self.expiry_ms = expiry_ms
        self.store = {}            # key -> (value, expiry, version)
        self.expiry_heap = []      # (expiry, version, key)
        self.live_sum = 0
        self.live_count = 0
        self._version = 0
        self._lock = threading.RLock()

    def _evict_expired(self, now: int) -> None:
        """Remove all entries with expiry <= now. Must hold the lock."""
        while self.expiry_heap and self.expiry_heap[0][0] <= now:
            expiry, version, key = heapq.heappop(self.expiry_heap)
            cur = self.store.get(key)
            # Skip stale heap entries (key overwritten since this entry was pushed)
            if cur is None or cur[2] != version:
                continue
            value, _, _ = cur
            del self.store[key]
            self.live_sum -= value
            self.live_count -= 1

    def put(self, key, value, timestamp: int) -> None:
        with self._lock:
            self._evict_expired(timestamp)
            old = self.store.get(key)
            if old is not None:          # overwrite: remove old contribution
                self.live_sum -= old[0]
                self.live_count -= 1
            self._version += 1
            expiry = timestamp + self.expiry_ms
            self.store[key] = (value, expiry, self._version)
            heapq.heappush(self.expiry_heap, (expiry, self._version, key))
            self.live_sum += value
            self.live_count += 1

    def get(self, key, timestamp: int):
        with self._lock:
            self._evict_expired(timestamp)
            cur = self.store.get(key)
            return cur[0] if cur is not None else None

    def get_average(self, timestamp: int):
        with self._lock:
            self._evict_expired(timestamp)
            if self.live_count == 0:
                return 0  # or None; clarify with interviewer
            return self.live_sum / self.live_count


# Quick sanity check
if __name__ == "__main__":
    wm = WindowedMap(expiry_ms=10)
    wm.put("a", 10, timestamp=0)   # expires at 10
    wm.put("b", 20, timestamp=5)    # expires at 15
    assert wm.get_average(timestamp=6) == 15.0
    assert wm.get("a", timestamp=6) == 10
    assert wm.get("a", timestamp=11) is None   # expired
    assert wm.get_average(timestamp=11) == 20.0
    wm.put("b", 30, timestamp=12)  # overwrite live key
    assert wm.get_average(timestamp=13) == 30.0
    print("WindowedMap OK")
```

### Confluent follow-ups — how to handle them

1. **"Make it thread-safe."** The `RLock` above serializes all public methods. Say why a single
   coarse lock is the right *starting* answer: eviction + mutation must be atomic, and
   fine-grained locking (per-key locks + a lock for the heap + a lock for the sum) invites
   deadlocks and subtle races for marginal gain at interview scale. Then discuss the
   escalation: read-write lock (many concurrent `get`s), lock striping/sharding by key hash
   for write throughput, lock-free via atomic counters if the language supports it.
2. **"Strong vs. eventual consistency?"** With one lock, every read sees all prior writes:
   strong consistency. If you shard or replicate, you trade it away. For a metrics-averaging
   use case, eventual consistency is usually acceptable (a slightly stale average is fine);
   for a correctness-critical cache, it is not. Name the trade-off explicitly — Confluent
   interviewers ask this to see systems thinking, not a "right" answer.
3. **"Timestamps arrive out of order."** The heap already handles this (expiry order ≠ arrival
   order). The deque optimization breaks — say so. Also note `get_average(t)` with `t` going
   *backwards* in time is ill-defined with eager eviction; you'd need versioned snapshots.
4. **"Memory grows unboundedly if `get_average` is never called."** True with lazy eviction.
   Mitigations: periodic background sweep, or cap size with an LRU-ish policy on top
   (leads naturally into question 4).

### What to say out loud / pitfalls

- Say: "Because timestamps are increasing, expirations leave in FIFO order — I could use a
  deque for O(1) eviction, but I'll use a heap so the code also handles out-of-order input."
- Pitfall: forgetting to subtract the overwritten value from the running sum (double counting).
- Pitfall: evicting only in `get_average` but not in `put`/`get` — stale reads.
- Pitfall: `get_average` on empty store — clarify return value (0 vs. None vs. exception).

---

## 2. Word / Phrase Search in Documents (Inverted Index)

**Frequency:** 8 posts — tied for the most-asked.

### Problem restatement (as Confluent asks it)

> Given a list of documents, each with an `id` and `text`, implement:
>
> - `search(word)` → list of document IDs containing the word.
> - Follow-up: `search_phrase(phrase)` → document IDs where the words appear **consecutively
>   in order** ("phrase search").
> - Further follow-ups: AND/OR queries, a single data store serving both word and phrase search.

### Solution approach and WHY

**Core data structure: inverted index — `word → {doc_id → [positions]}`.**

- **Why an inverted index instead of scanning documents per query:** Scanning is O(total words)
  per query. An inverted index pays O(total words) once at build time, then answers word
  queries in O(1) map lookup + O(matches). This is the standard IR trade-off (build cost
  amortized over many queries) — say it explicitly.
- **Why store positions, not just doc IDs:** Positions are what make phrase search possible
  without re-scanning text. `word → doc_id → sorted position list` lets you check phrase
  "w1 w2 w3" in doc D by verifying positions of w2 = positions of w1 + 1, etc. Storing only
  doc IDs forces a second pass over document text — defeating the purpose of the index.
- **Why positions stay sorted for free:** documents are tokenized left to right, so appending
  positions during the build keeps each list sorted with no extra sort step.
- **Why phrase matching via offset intersection, not regex:** For phrase w1..wk in doc D, take
  P1 = positions(w1, D); a phrase occurrence starts at p in P1 iff p+1 ∈ P2, p+2 ∈ P3, ….
  Checking via set lookups on the other words' position sets is O(|P1| · k). Alternative:
  build a positional index over the whole corpus and intersect — same thing. Avoid regex on
  raw text: it reintroduces the per-query scan you built the index to avoid.
- **Single store for both:** the same `word → doc_id → positions` structure answers word
  queries (keys of the inner map) and phrase queries (position arithmetic). One index, two
  query types — this is the answer to the "single data store" follow-up.
- **AND/OR queries:** AND = intersection of doc-ID sets across words; OR = union. Do the
  smallest posting list first for AND (standard optimization — say it).

### Complexity

| Operation | Time | Space |
|---|---|---|
| Build index | O(W), W = total words | O(W) |
| `search(word)` | O(1) lookup + O(d) to emit d doc IDs | O(W) |
| `search_phrase` (k words) | O(P · k), P = occurrences of first word | O(W) |
| AND over m words | O(Σ posting-list sizes), smallest-first | — |

### Reference implementation

```python
from collections import defaultdict

class DocumentStore:
    """
    Inverted index: word -> {doc_id -> [sorted positions]}.

    WHY this shape:
    - word -> doc set answers single-word queries in O(1)
    - per-doc position lists answer phrase queries without rescanning text
    - one structure serves both query types (the "single data store" follow-up)
    """

    def __init__(self):
        # word -> doc_id -> list of positions (built left-to-right, so sorted)
        self.index = defaultdict(lambda: defaultdict(list))

    def add_document(self, doc_id: int, text: str) -> None:
        for pos, word in enumerate(text.lower().split()):
            self.index[word][doc_id].append(pos)

    def search(self, word: str):
        """Doc IDs containing the word. O(1) lookup + O(docs)."""
        return list(self.index.get(word.lower(), {}).keys())

    def search_phrase(self, phrase: str):
        """
        Doc IDs where the phrase appears consecutively in order.
        For phrase w1..wk in doc D: p in positions(w1,D) starts an occurrence
        iff p+1 in positions(w2,D), ..., p+k-1 in positions(wk,D).
        """
        words = phrase.lower().split()
        if not words:
            return []
        first_postings = self.index.get(words[0], {})
        result = []
        for doc_id, positions in first_postings.items():
            # position sets for O(1) offset checks
            pos_sets = []
            ok = True
            for w in words[1:]:
                s = self.index.get(w, {}).get(doc_id)
                if s is None:
                    ok = False
                    break
                pos_sets.append(set(s))
            if not ok:
                continue
            for p in positions:
                if all((p + i + 1) in pos_sets[i] for i in range(len(pos_sets))):
                    result.append(doc_id)
                    break  # one hit per doc is enough
        return result

    def search_and(self, words):
        """Doc IDs containing ALL words — intersect smallest posting list first."""
        posting_sets = [set(self.index.get(w.lower(), {})) for w in words]
        posting_sets.sort(key=len)  # WHY: minimize intermediate intersection work
        out = posting_sets[0]
        for s in posting_sets[1:]:
            out &= s
        return list(out)

    def search_or(self, words):
        out = set()
        for w in words:
            out |= set(self.index.get(w.lower(), {}))
        return list(out)


if __name__ == "__main__":
    ds = DocumentStore()
    ds.add_document(1, "the quick brown fox jumps")
    ds.add_document(2, "the quick rabbit runs quick")
    ds.add_document(3, "brown fox brown fox")
    assert set(ds.search("quick")) == {1, 2}
    assert ds.search_phrase("quick brown fox") == [1]
    assert ds.search_phrase("brown fox") == [1, 3]
    assert ds.search_phrase("fox quick") == []
    assert set(ds.search_and(["quick", "fox"])) == {1}
    print("DocumentStore OK")
```

### Confluent follow-ups — how to handle them

1. **"Single data store for word and phrase search?"** The structure above *is* the answer —
   point at it. Word queries use the outer map; phrase queries use the position lists.
2. **"Scale to millions of documents?"** Shard the index by word hash (term partitioning):
   each shard owns a slice of the vocabulary; a query fans out and merges. Alternative doc
   partitioning (each shard owns whole docs, partial indexes) — better for phrase queries
   (no cross-shard position joins) but every query hits every shard. Name the trade-off.
3. **"Rank results?"** TF-IDF or BM25 over the same posting lists; positions enable proximity
   scoring. Don't implement unless asked — just name it.
4. **Concurrency:** index build is single-writer; make the query path lock-free by building
   an immutable index and atomically swapping the reference (copy-on-write / RCU pattern).

### What to say out loud / pitfalls

- Say: "I'll pay O(total words) once to build an inverted index with positions, so queries
  never rescan text."
- Pitfall: case sensitivity — normalize (`lower()`) at index *and* query time.
- Pitfall: tokenization — `"fox."` vs `"fox"`; mention a real tokenizer/stemming as a
  production note, keep `split()` for the interview.
- Pitfall: phrase search via string `in` on raw text — breaks word boundaries ("he" in "the").

---
## 3. Validate Sudoku + Solve Sudoku

**Frequency:** 6 posts. The classic two-part escalation: validator first, then solver.

### Problem restatement (as Confluent asks it)

> - Part 1: given a 9×9 board (partially filled, `'.'` for empty), determine if it is **valid**:
>   no duplicate digits 1–9 in any row, column, or 3×3 box. (Note: not "solvable" — just valid.)
> - Part 2 (follow-up): **solve** the puzzle in place via backtracking.

### Solution approach and WHY

**Part 1 — validation with three hash sets (or bitmasks), single pass.**

- **Why one pass with sets instead of three separate scans:** A single pass over 81 cells,
  recording seen digits per row/column/box in hash sets, is O(81) = O(1) with a tiny constant.
  Three separate scans are also O(1) but triple the constant and triple the code — the
  interviewer explicitly rewards "optimizing traversals (single pass)" per the reports.
- **Why sets over counting arrays:** `set` of chars is the most readable; a `9×9` boolean array
  or bitmask is marginally faster. Mention bitmasks as the production variant
  (`rows[i] |= 1 << digit`), but write the set version — clarity wins in interviews.
- **Why not check solvability in validation:** The problem asks only for validity. Say so;
  don't over-engineer.

**Part 2 — backtracking with constraint propagation (MRV heuristic).**

- **Why backtracking at all:** Sudoku is NP-complete-ish constraint satisfaction; systematic
  trial with undo is the standard exact approach. Alternatives: DLX (dancing links, overkill
  to implement), constraint propagation only (incomplete — can't solve hard puzzles alone).
- **Why MRV (minimum remaining values) instead of naive row-major order:** Naive backtracking
  tries cells in fixed order, branching up to 9 ways deep. MRV always picks the empty cell
  with the fewest legal candidates, which prunes doomed branches earliest — often 10–100×
  faster on hard boards. This is the single optimization that separates a passing solution
  from an impressive one. Say: "I'll pick the most constrained cell first."
- **Why maintain candidate sets incrementally vs. recompute:** Recomputing candidates per cell
  from scratch each recursion is O(81) per node. Maintaining row/col/box occupancy sets and
  deriving candidates as `digits − (row ∪ col ∪ box)` is O(1) per cell. Implement with the
  occupancy sets updated on place/unplace.
- **Why in-place mutation with undo:** Copying the board per recursion is O(81) per node and
  allocation-heavy. Mutate + undo is O(1) per step.

### Complexity

| Operation | Time | Space |
|---|---|---|
| Validate | O(1) — fixed 81 cells | O(1) |
| Solve (backtracking + MRV) | O(9^m) worst case, m = empty cells; MRV prunes heavily in practice | O(m) recursion depth |

Reasoning: worst case is exponential (Sudoku is NP-complete), but MRV + constraint
propagation makes real puzzles fast. Space is the recursion stack plus occupancy sets.

### Reference implementation

```python
def is_valid_sudoku(board) -> bool:
    """
    Single-pass validation. WHY one pass: 81 cells, one traversal, three
    set-arrays updated together — minimal constant factor, which interviewers
    explicitly look for here.
    """
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
            rows[r].add(v)
            cols[c].add(v)
            boxes[b].add(v)
    return True


def solve_sudoku(board) -> bool:
    """
    Backtracking with MRV (most-constrained-cell) heuristic.
    WHY MRV over naive row-major: picks the cell with fewest candidates first,
    pruning dead branches earliest — the difference between timing out and
    solving hard boards.
    """
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
                rows[r].add(v)
                cols[c].add(v)
                boxes[(r // 3) * 3 + c // 3].add(v)

    ALL = set("123456789")

    def candidates(r, c):
        # WHY derive from occupancy sets: O(1) per cell vs O(81) rescan
        return ALL - rows[r] - cols[c] - boxes[(r // 3) * 3 + c // 3]

    def backtrack(k: int) -> bool:
        if k == len(empties):
            return True
        # MRV: choose the most constrained among remaining cells
        best, best_cands, best_i = None, None, k
        for i in range(k, len(empties)):
            r, c = empties[i]
            cand = candidates(r, c)
            if best_cands is None or len(cand) < len(best_cands):
                best, best_cands, best_i = (r, c), cand, i
                if len(cand) == 1:
                    break
        if not best_cands:      # dead end — prune immediately
            return False
        empties[k], empties[best_i] = empties[best_i], empties[k]  # fix choice at k
        r, c = best
        b = (r // 3) * 3 + c // 3
        for v in best_cands:
            board[r][c] = v       # mutate in place...
            rows[r].add(v); cols[c].add(v); boxes[b].add(v)
            if backtrack(k + 1):
                return True
            rows[r].remove(v); cols[c].remove(v); boxes[b].remove(v)  # ...undo
            board[r][c] = '.'
        empties[k], empties[best_i] = empties[best_i], empties[k]
        return False

    return backtrack(0)


if __name__ == "__main__":
    b = [
        ["5","3",".",".","7",".",".",".","."],
        ["6",".",".","1","9","5",".",".","."],
        [".","9","8",".",".",".",".","6","."],
        ["8",".",".",".","6",".",".",".","3"],
        ["4",".",".","8",".","3",".",".","1"],
        ["7",".",".",".","2",".",".",".","6"],
        [".","6",".",".",".",".","2","8","."],
        [".",".",".","4","1","9",".",".","5"],
        [".",".",".",".","8",".",".","7","9"],
    ]
    assert is_valid_sudoku(b)
    b[0][0] = "8"  # duplicate in column 0 (row 3 has "8")
    assert not is_valid_sudoku(b)
    b[0][0] = "5"
    assert solve_sudoku(b)
    assert is_valid_sudoku(b) and all('.' not in row for row in b)
    print("Sudoku OK")
```

### Confluent follow-ups — how to handle them

1. **"Optimize further."** Bitmask occupancy (`int` bit operations instead of sets) and
   precomputed peer lists. Mention, don't necessarily implement.
2. **"Parallelize the solver?"** Split on the first branching cell: each candidate value
   becomes an independent task. Backtracking subtrees are disjoint, so it's embarrassingly
   parallel — but work distribution is uneven (another MRV argument: balanced-ish).
3. **"Validate a generalized N²×N² board?"** Box index becomes `(r // N) * N + c // N`;
   everything else is identical. Say the formula generalizes.

### What to say out loud / pitfalls

- Say: "Validator first, single pass. For the solver I'll do backtracking but always expand
  the most constrained cell — that's the MRV heuristic, it prunes hardest first."
- Pitfall: validating "solvable" instead of "valid" — re-read the prompt.
- Pitfall: box index arithmetic `(r // 3) * 3 + c // 3` — get it right once, reuse.
- Pitfall: forgetting to undo the board cell (`board[r][c] = '.'`) on backtrack.

---

## 4. LRU Cache (and Variants incl. TTL)

**Frequency:** 4 posts, plus the TTL variant overlaps question 1.

### Problem restatement (as Confluent asks it)

> Design a data structure supporting `get(key)` and `put(key, value)` in O(1), evicting the
> **least recently used** item when capacity is exceeded.
>
> Variants seen: LRU with TTL per entry; "modified LRU"; LRU-like cache with explicit
> concurrency requirements (locks for concurrent reads/writes).

### Solution approach and WHY

**Core: hash map + doubly linked list (with dummy head/tail sentinels).**

- **Why hash map + doubly linked list, not anything else:**
  - Hash map alone can't track recency order.
  - A queue/array alone can't find a key in O(1).
  - A singly linked list can't remove a node in O(1) without its predecessor — you'd need
    O(n) to find it. Doubly linked gives O(1) removal given the node pointer from the map.
  - Balanced BST keyed by timestamp: O(log n) per op and timestamps need updating on every
    access — strictly worse.
  - `OrderedDict` (Python): fine to *mention* as the production shortcut, but interviewers
    want the manual structure to prove you understand the mechanics. Implement it by hand.
- **Why dummy head/tail sentinels:** eliminates all null-check branches in insert/remove —
  fewer edge cases, fewer bugs under time pressure. This is a "I've done this before" signal.
- **Why move-to-front on `get`:** recency must update on reads too, not just writes —
  that's the definition of LRU (vs. FIFO).
- **TTL variant:** store `expiry` per node; on `get`, treat expired as missing and evict it;
  on `put`, evict-then-insert. A min-heap of expiries (as in question 1) handles bulk
  expiration if needed — mention it, implement lazy per-access expiry for simplicity.
- **Why this eviction policy vs. LFU/Random:** LRU exploits temporal locality with O(1)
  ops; LFU needs frequency counters + min-frequency tracking (more complex, and frequency
  can go stale). Say when you'd pick differently: LFU for stable hot keys, TTL for
  time-sensitive data.

### Complexity

| Operation | Time | Space |
|---|---|---|
| `get` | O(1) | O(capacity) |
| `put` | O(1) | O(capacity) |

### Reference implementation

```python
import threading
import time

class _Node:
    __slots__ = ("key", "value", "expiry", "prev", "next")
    def __init__(self, key=None, value=None, expiry=None):
        self.key, self.value, self.expiry = key, value, expiry
        self.prev = self.next = None

class LRUCache:
    """
    Hash map + doubly linked list with dummy head (MRU) / tail (LRU) sentinels.

    WHY doubly linked: O(1) removal of an arbitrary node via the map pointer —
    singly linked would need O(n) to find the predecessor.
    WHY sentinels: no null branches in _remove/_add_to_front.
    """

    def __init__(self, capacity: int, default_ttl: float | None = None):
        assert capacity > 0
        self.capacity = capacity
        self.default_ttl = default_ttl   # None => no expiration
        self.map = {}                    # key -> _Node
        self.head = _Node()               # dummy MRU sentinel
        self.tail = _Node()               # dummy LRU sentinel
        self.head.next = self.tail
        self.tail.prev = self.head
        self._lock = threading.RLock()   # see concurrency follow-up

    # ---- list plumbing (all assume lock held) ----
    def _remove(self, node: _Node) -> None:
        node.prev.next = node.next
        node.next.prev = node.prev

    def _add_to_front(self, node: _Node) -> None:
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node

    def _is_expired(self, node: _Node) -> bool:
        return node.expiry is not None and node.expiry <= time.monotonic()

    def get(self, key):
        with self._lock:
            node = self.map.get(key)
            if node is None or self._is_expired(node):
                if node is not None:          # lazy TTL eviction
                    self._remove(node)
                    del self.map[key]
                return -1
            self._remove(node)                # recency updates on READ too
            self._add_to_front(node)
            return node.value

    def put(self, key, value, ttl: float | None = None) -> None:
        with self._lock:
            ttl = self.default_ttl if ttl is None else ttl
            expiry = time.monotonic() + ttl if ttl is not None else None
            node = self.map.get(key)
            if node is not None:
                if self._is_expired(node):     # expired => treat as new insert
                    self._remove(node)
                    del self.map[key]
                    node = None
                else:
                    node.value, node.expiry = value, expiry
                    self._remove(node)
                    self._add_to_front(node)
                    return
            node = _Node(key, value, expiry)
            self.map[key] = node
            self._add_to_front(node)
            if len(self.map) > self.capacity:  # evict LRU (before dummy tail)
                lru = self.tail.prev
                self._remove(lru)
                del self.map[lru.key]


if __name__ == "__main__":
    c = LRUCache(2)
    c.put(1, 1); c.put(2, 2)
    assert c.get(1) == 1      # 1 becomes MRU
    c.put(3, 3)              # evicts 2 (LRU)
    assert c.get(2) == -1
    c.put(4, 4)              # evicts 1
    assert c.get(1) == -1 and c.get(3) == 3 and c.get(4) == 4

    c2 = LRUCache(2, default_ttl=0.05)
    c2.put("a", 1)
    assert c2.get("a") == 1
    time.sleep(0.06)
    assert c2.get("a") == -1  # expired
    print("LRUCache OK")
```

### Confluent follow-ups — how to handle them

1. **"Locks for concurrent reads/writes"** (explicitly asked): the `RLock` above is the safe
   baseline. Escalation path to discuss: read-write lock (gets dominate in caches, so
   shared read access matters); sharded caches (N independent LRU shards by key hash —
   reduces contention, slightly approximate global LRU); lock-free with atomics (experts
   only — don't volunteer to implement).
2. **"Distributed LRU?"** Consistent hashing over cache nodes; each node runs the structure
   above. Eviction stays local — global LRU across nodes is prohibitively expensive to
   coordinate. Say that.
3. **TTL + LRU interaction:** which wins? Expired entries are evicted lazily on access;
   capacity eviction picks the LRU *live* node. If the tail node is expired, remove it
   instead of a live one — the `put` path above handles this via the expiry check.

### What to say out loud / pitfalls

- Say: "Hash map for O(1) lookup, doubly linked list for O(1) recency updates — singly
  linked can't unlink without the predecessor."
- Pitfall: forgetting `get` updates recency (that's what makes it LRU, not FIFO).
- Pitfall: off-by-one on capacity check — evict *after* insert when `len > capacity`.
- Pitfall: in the TTL variant, returning expired values — always check expiry on `get`.

---
## 5. `tail -n` — Last N Lines of a File

**Frequency:** 4 posts. Variants: logging system printing last N lines in original order
without storing everything; "practical file operations" round.

### Problem restatement (as Confluent asks it)

> Implement `tail(file_name, n)` that prints the last `n` lines of a file **without loading
> the entire file into memory**. Handle `n = 0` and `n > total lines`. Optimize for huge files.

### Solution approach and WHY

**Core: circular buffer (ring buffer) of size n, single streaming pass.**

- **Why a ring buffer instead of storing all lines:** Storing all lines is O(file size)
  memory — the thing the prompt forbids. A ring buffer keeps exactly the last n lines:
  O(n) memory regardless of file size. Say the memory bound out loud.
- **Why a single forward pass instead of seeking from the end:** Reading backwards from EOF
  in fixed-size byte blocks is the *production* `tail` implementation (optimal I/O: reads
  only the tail bytes). But it requires binary-mode seeking, partial-line stitching across
  block boundaries, and encoding care — high bug risk in an interview. The ring buffer is
  O(file size) time / O(n) memory, trivially correct, and what interviewers accept. **Name
  the backwards-seek approach as the production upgrade** — that sentence alone scores points.
- **Why `collections.deque(maxlen=n)`:** it's a ready-made ring buffer: `append` evicts the
  oldest automatically in O(1). Hand-rolling a list with modulo indexing is also fine, but
  deque is cleaner. Do NOT use `lines[-n:]` on a full read — that's the forbidden approach.
- **Edge cases:** `n <= 0` → print nothing (don't crash on `maxlen=0` — deque requires
  maxlen ≥ 0 but `[-0:]` slices everything; handle explicitly). `n > total lines` → print
  all lines in order (ring buffer naturally holds fewer than n).
- **"Without storing everything" logging variant:** same answer — the ring buffer *is* the
  "don't store everything" mechanism. If lines arrive as a stream (not a file), drop the
  file I/O and keep the deque.

### Complexity

| Operation | Time | Space |
|---|---|---|
| `tail(f, n)` | O(L), L = total lines (one pass) | O(n) lines |

Production backwards-seek variant: O(bytes in last n lines) time, O(n) space — strictly
better I/O, more complex code.

### Reference implementation

```python
from collections import deque

def tail(file_name: str, n: int) -> None:
    """
    Print the last n lines without loading the whole file.

    WHY a ring buffer (deque(maxlen=n)): O(n) memory no matter how large the
    file is; each new line evicts the oldest in O(1). A full read + [-n:]
    slice would be O(file size) memory — exactly what the prompt forbids.
    """
    if n <= 0:
        return                      # WHY explicit: deque(maxlen=0) discards
                                    # everything, and lines[-0:] == whole list
    buf = deque(maxlen=n)           # ring buffer: append evicts oldest
    with open(file_name, "r", encoding="utf-8", errors="replace") as f:
        for line in f:              # single streaming pass, O(1) per line
            buf.append(line.rstrip("\n"))
    for line in buf:                # already in original order
        print(line)


def tail_lines(lines, n: int):
    """Stream variant (logging-system follow-up): works on any iterable."""
    if n <= 0:
        return []
    return list(deque(lines, maxlen=n))


if __name__ == "__main__":
    import tempfile, os
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".txt") as f:
        fname = f.name
        for i in range(1, 101):
            f.write(f"line {i}\n")
    print("--- last 3 of 100 ---")
    tail(fname, 3)          # line 98, 99, 100
    print("--- n > total ---")
    tail(fname, 200)        # all 100 lines, in order
    print("--- n = 0 (no output) ---")
    tail(fname, 0)
    os.unlink(fname)
    assert tail_lines(iter(["a", "b", "c", "d"]), 2) == ["c", "d"]
    print("tail OK")
```

### Confluent follow-ups — how to handle them

1. **"Optimize for huge files / minimize I/O."** Backwards block reads: seek to EOF, read
   fixed-size blocks backwards, count newlines until you have n+1, then print from the right
   position. O(tail bytes) I/O instead of O(file). Mention encoding pitfalls (a multi-byte
   character split across a block boundary) as the reason it's production-only.
2. **"Follow mode (`tail -f`)?"** After printing, keep the file open and poll for new data
   (or use inotify). Separate concern — name it, don't implement unless asked.
3. **"Multiple files / `tail -n +k` (from line k)?"** Straightforward extensions of the
   same streaming pattern.

### What to say out loud / pitfalls

- Say: "I'll stream the file once through a fixed-size ring buffer — O(n) memory no matter
  the file size. In production I'd seek backwards from EOF to avoid reading the whole file,
  but the ring buffer is the correct interview answer."
- Pitfall: `lines[-n:]` after `readlines()` — fails the "without loading" requirement.
- Pitfall: `n = 0` — `[-0:]` is the whole list; guard explicitly.
- Pitfall: forgetting output stays in original order (deque preserves it — just iterate).

---

## 6. Function Signature Matching

**Frequency:** 3 posts. Type-matching/parsing focus; follow-up: variadic args.

### Problem restatement (as Confluent asks it)

> Given a list of function signatures (name + ordered parameter types) and a call site with
> argument values/types, return the signatures that match. Follow-up: support variadic
> parameters (`Integer... args`).

### Solution approach and WHY

**Core: normalize each signature to `(name, [param_types], is_variadic)` once, then match
by arity + pairwise type compatibility.**

- **Why normalize up front:** Parsing `"foo(Integer, String)"` on every match attempt is
  O(signatures × calls × parse). Parse once into structured form; matching becomes pure
  list comparison. Standard preprocess-once/query-many trade-off.
- **Why pairwise type check instead of string equality:** argument *values* (`42`, `"hi"`)
  must map to types (`Integer`, `String`) before comparison. Define `typeof(arg)` and compare
  type names — this handles the value-vs-type gap the problem is testing.
- **Why arity check first:** cheap O(1) filter before the O(k) pairwise walk. For variadic
  `f(T...)`: matches iff len(args) ≥ len(fixed params) and all extra args are type T.
  (Java semantics: variadic must be last, accepts zero+ args.)
- **Why not regex for parsing:** signatures nest (`Map<String, List<Integer>>`); regex can't
  count brackets. A tiny paren-depth-aware splitter is correct and short. For the interview,
  `split(",")` at depth 0 is the right 10-line parser.
- **Overload resolution tie-breaking (if asked):** most specific match wins — exact arity
  beats variadic-with-zero-varargs; no match → ambiguity error. Name it; implement only the
  boolean match unless pressed.

### Complexity

| Operation | Time | Space |
|---|---|---|
| Parse s signatures | O(s · L), L = signature length | O(s · k) |
| Match one call vs s signatures | O(s · k), k = max arity | O(1) extra |

### Reference implementation

```python
def split_top_level(s: str):
    """Split on commas at paren depth 0. WHY: types nest (Map<String, List<Integer>>),
    so naive split(',') breaks; a depth counter is the minimal correct parser."""
    parts, depth, cur = [], 0, []
    for ch in s:
        if ch == '<':
            depth += 1
        elif ch == '>':
            depth -= 1
        if ch == ',' and depth == 0:
            parts.append(''.join(cur).strip())
            cur = []
        else:
            cur.append(ch)
    parts.append(''.join(cur).strip())
    return [p for p in parts if p]


def parse_signature(sig: str):
    """'foo(Integer, String...)' -> ('foo', ['Integer'], variadic_type='String')."""
    name, rest = sig.split('(', 1)
    inner = rest.rstrip(')').strip()
    params = split_top_level(inner) if inner else []
    variadic_type = None
    fixed = []
    for i, p in enumerate(params):
        if p.endswith('...'):
            # WHY enforce last: matches Java/C semantics; variadic in the middle
            # is ambiguous about where fixed params resume.
            assert i == len(params) - 1, "variadic must be last"
            variadic_type = p[:-3].strip()
        else:
            fixed.append(p)
    return name.strip(), fixed, variadic_type


def typeof(value: str) -> str:
    """Map a literal argument to its type name."""
    v = value.strip()
    if v.startswith('"') and v.endswith('"'):
        return 'String'
    try:
        int(v)
        return 'Integer'
    except ValueError:
        pass
    try:
        float(v)
        return 'Double'
    except ValueError:
        pass
    return 'Object'


def matches(sig, call_name: str, arg_types) -> bool:
    """Arity check first (cheap filter), then pairwise type compatibility."""
    name, fixed, variadic = sig
    if name != call_name:
        return False
    if variadic is None:
        return len(arg_types) == len(fixed) and all(
            a == f for a, f in zip(arg_types, fixed))
    # variadic: fixed params must match, extras must match variadic type
    if len(arg_types) < len(fixed):
        return False
    if any(a != f for a, f in zip(arg_types, fixed)):
        return False
    return all(a == variadic for a in arg_types[len(fixed):])


def find_matches(signatures, call_name: str, args):
    parsed = [parse_signature(s) for s in signatures]
    arg_types = [typeof(a) for a in args]
    return [s for s, p in zip(signatures, parsed) if matches(p, call_name, arg_types)]


if __name__ == "__main__":
    sigs = ["foo(Integer, String)", "foo(Integer...)", "foo(Integer, Integer)",
            "bar(Map<String, List<Integer>>)"]
    assert find_matches(sigs, "foo", ["42", '"hi"']) == ["foo(Integer, String)"]
    assert find_matches(sigs, "foo", ["1", "2", "3"]) == ["foo(Integer...)"]
    assert find_matches(sigs, "foo", ["7"]) == ["foo(Integer...)"]  # zero+ varargs
    assert find_matches(sigs, "bar", ["x"]) == []  # type unknown -> no match
    print("Signature matching OK")
```

### Confluent follow-ups — how to handle them

1. **Variadic edge cases:** `f()` with zero args matches `f(T...)`; `f(T...)` vs `f(T)` both
   match a single arg — flag as ambiguous (Java resolves to the fixed-arity one; say that).
2. **Subtyping:** `Integer` arg vs `Number` param — walk a type hierarchy instead of `==`.
   Mention; implement only if asked.
3. **Performance at scale:** index signatures by `(name, arity)` in a dict; variadic
   signatures indexed by `(name, min_arity)`. Turns matching into O(k) dict lookups.

### What to say out loud / pitfalls

- Say: "I'll parse once into (name, fixed types, variadic type), then match by arity first —
  it's the cheap filter — then pairwise types."
- Pitfall: comparing raw values to types without a `typeof` step.
- Pitfall: `split(',')` breaking on nested generics — use the depth-aware splitter.
- Pitfall: variadic matching zero extra args — must still match.

---
## 7. Time-Based Key-Value Store

**Frequency:** 2 posts. Variant seen: maintain sum/average over the window; get/set with
eviction in a millisecond window.

### Problem restatement (as Confluent asks it)

> Design a time-based key-value store: `set(key, value, timestamp)`, `get(key, timestamp)`
> returns the value set at the **latest timestamp ≤ given timestamp**. Follow-up variant:
> maintain a running sum/average over entries in a time window with eviction.

### Solution approach and WHY

**Core: `dict[key → sorted list of (timestamp, value)]` + binary search.**

- **Why per-key sorted lists instead of one global structure:** queries are per-key
  ("latest value for *this* key at time t"). A global time-ordered structure would need
  filtering by key — O(n). Per-key lists make each query local to that key's history.
- **Why binary search (`bisect`) instead of linear scan:** histories only grow; linear scan
  is O(h) per get. `bisect_right` on the timestamp list is O(log h). Since `set` timestamps
  are typically non-decreasing, appends are O(1) amortized — but use `insort` (or note the
  assumption) if out-of-order sets are possible.
- **Why not a balanced BST / sorted dict per key:** overkill — a sorted list with bisect
  is simpler and cache-friendly; the O(h) insert cost only bites with out-of-order
  timestamps, which the prompt usually excludes.
- **Sum/average window variant:** this collapses into question 1's design (running sum +
  expiry heap). Say that explicitly: "this is the WindowedMap pattern — running aggregates
  plus lazy eviction." Interviewers love recognizing the reduction.
- **Space concern:** histories grow forever. Mention compaction: keep only the latest value
  per key if intermediate history is never queried (or TTL the history, tying back to Q1).

### Complexity

| Operation | Time | Space |
|---|---|---|
| `set` (increasing timestamps) | O(1) amortized append | O(total sets) |
| `set` (arbitrary order) | O(h) insert | O(total sets) |
| `get` | O(log h), h = history length for key | — |

### Reference implementation

```python
from bisect import bisect_right

class TimeMap:
    """
    Per-key chronology: key -> [(timestamp, value)] kept sorted.

    WHY per-key lists: queries are per-key, so co-locating a key's history
    makes get() a local binary search instead of a global filtered scan.
    WHY bisect: O(log h) lookup vs O(h) linear scan over history.
    """

    def __init__(self):
        self.store = {}  # key -> [timestamps], [values] (parallel lists)

    def set(self, key: str, value: str, timestamp: int) -> None:
        entry = self.store.setdefault(key, ([], []))
        ts, vs = entry
        if ts and timestamp < ts[-1]:
            # Out-of-order: insert in sorted position (O(h)). If the prompt
            # guarantees increasing timestamps, plain append is O(1).
            i = bisect_right(ts, timestamp)
            ts.insert(i, timestamp)
            vs.insert(i, value)
        else:
            ts.append(timestamp)
            vs.append(value)

    def get(self, key: str, timestamp: int) -> str:
        entry = self.store.get(key)
        if not entry:
            return ""
        ts, vs = entry
        # WHY bisect_right - 1: we want the LATEST timestamp <= query time
        i = bisect_right(ts, timestamp) - 1
        return vs[i] if i >= 0 else ""


if __name__ == "__main__":
    tm = TimeMap()
    tm.set("k", "v1", 1)
    tm.set("k", "v2", 5)
    tm.set("k", "v3", 10)
    assert tm.get("k", 0) == ""
    assert tm.get("k", 1) == "v1"
    assert tm.get("k", 7) == "v2"   # latest <= 7
    assert tm.get("k", 10) == "v3"
    assert tm.get("missing", 10) == ""
    print("TimeMap OK")
```

### Confluent follow-ups — how to handle them

1. **"Add a windowed sum/average."** → Question 1's design. Running sum + expiry structure;
   say the reduction out loud.
2. **"Concurrent writers?"** Per-key locks (striped by key hash) — writes to different keys
   don't contend. A single global lock serializes everything; sharding is the standard
   escalation.
3. **"Bound memory?"** TTL on history entries (→ Q1 again) or keep only the last K versions
   per key if queries only need recent history — state the assumption and ask.

### What to say out loud / pitfalls

- Say: "Per-key sorted history plus binary search — O(log h) gets, O(1) sets when timestamps
  increase."
- Pitfall: `bisect_left` vs `bisect_right` — you want the latest ≤ t, so `bisect_right(...) - 1`.
- Pitfall: returning a value when all timestamps are > t (index −1) — guard it.

---

## 8. Debounce (JavaScript)

**Frequency:** 2 posts. Frontend roles; explicitly "JavaScript only — study JS APIs."

### Problem restatement (as Confluent asks it)

> Implement `debounce(fn, delay)`: return a wrapper that postpones invoking `fn` until
> `delay` ms have elapsed since the last call. Support leading/trailing edge options and
> cancellation.

### Solution approach and WHY

**Core: closure over a timer id; each call clears the previous timer and sets a new one.**

- **Why `clearTimeout` + `setTimeout` instead of timestamps:** Timer handles are the idiomatic
  JS mechanism; comparing `Date.now()` in a poll loop wastes cycles. The closure keeps
  exactly one pending timer — O(1) state.
- **Why preserve `this` and arguments:** the wrapper must be a transparent proxy —
  `fn.apply(this, args)`. Arrow-function-only implementations silently break method calls;
  interviewers test this.
- **Why trailing edge by default, leading as option:** trailing (fire after quiet period) is
  the standard "search-as-you-type" semantic. Leading (fire immediately, then ignore) suits
  "submit button" spam-prevention. Implement both via flags — it shows API design sense.
- **Why expose `cancel()` (and `flush()`):** real debounce utilities (lodash) have them;
  component unmount / test teardown needs cancellation. Cheap to add, frequently asked.
- **Debounce vs. throttle (say the difference):** debounce = fire after silence; throttle =
  fire at most once per interval. Conflating them is the classic pitfall — state the
  distinction before coding.

### Complexity

| Aspect | Cost |
|---|---|
| Per call | O(1) — one clearTimeout + one setTimeout |
| Memory | O(1) — single timer id + latest args in closure |

### Reference implementation

```javascript
/**
 * WHY closure + clearTimeout/setTimeout: exactly one pending timer exists at
 * any time, so each new call simply reschedules — O(1) per call, O(1) state.
 * WHY .apply(this, args): the wrapper must be transparent to `this` and args.
 */
function debounce(fn, delay, { leading = false, trailing = true } = {}) {
  let timerId = null;
  let lastArgs, lastThis;

  function invoke() {
    fn.apply(lastThis, lastArgs);
    lastArgs = lastThis = null;
  }

  function debounced(...args) {
    lastArgs = args;
    lastThis = this;
    const callNow = leading && timerId === null;

    clearTimeout(timerId);                 // WHY: reschedule on every call —
    timerId = setTimeout(() => {           // only the last call's timer survives
      timerId = null;
      if (trailing && !callNow) invoke();  // trailing edge
    }, delay);

    if (callNow) invoke();                 // leading edge
  }

  debounced.cancel = () => {               // WHY: cleanup on unmount / tests
    clearTimeout(timerId);
    timerId = lastArgs = lastThis = null;
  };

  debounced.flush = () => {                // fire pending trailing call now
    if (timerId !== null) {
      clearTimeout(timerId);
      timerId = null;
      if (trailing) invoke();
    }
  };

  return debounced;
}

// Sanity check (node):
// const d = debounce((x) => console.log("fired:", x), 100);
// d(1); d(2); d(3); // only "fired: 3" after 100ms of silence
```

### Confluent follow-ups — how to handle them

1. **"Throttle instead?"** Same skeleton, but the timer *isn't* cleared on each call —
   it fires at most once per `delay`. One-line conceptual difference; say it.
2. **"Leading + trailing both true?"** Handled above: fire immediately on the first call
   of a burst *and* once more after the burst ends (if calls kept coming). lodash behavior.
3. **"Test it?"** Fake timers (`jest.useFakeTimers()` + `advanceTimersByTime`) — never
   real `setTimeout` in tests. Say this; it's a seniority signal.

### What to say out loud / pitfalls

- Say first: "Debounce fires after a quiet period; throttle caps the rate — I'll implement
  debounce with trailing edge default."
- Pitfall: losing `this` (arrow function assigned as method).
- Pitfall: forgetting `clearTimeout` — without it you get throttle-ish repeated firing.
- Pitfall: `leading` without resetting state — the `timerId === null` check is the guard.

---

# PART 2 — SYSTEM DESIGN

> **General interview playbook for Confluent design rounds** (they require a "strong hire"
> signal for SSE2): start with requirements → back-of-envelope scale → API → data model →
> high-level components → deep dive on the 2–3 hardest parts → failure handling. Narrate
> trade-offs at every step; Confluent interviewers explicitly probe API design (verbs,
> status codes, auth), data modeling, and scale reasoning (nodes, replicas, partitions).

---

## SD1. Podcast / Feed Service

**Frequency:** 6 posts — the most-asked system design question.

### Requirements

**Functional:**
- Creators: publish podcasts, add/remove episodes (audio metadata + media URL).
- Users: subscribe/unsubscribe to podcasts, fetch personalized feed (latest episodes from
  subscriptions, paginated), fetch top-N episodes.
- Feed view: reverse-chronological merged timeline of subscribed podcasts.

**Non-functional:**
- Scale: 10M users, 1M podcasts, 100M episodes; read-heavy (feed reads ≫ writes).
- Latency: feed load p99 < 300ms.
- Availability over strict consistency: a seconds-stale feed is fine (say this — it drives
  the push-vs-pull decision).
- Durability: never lose a published episode.

### API design

| Method | Endpoint | Purpose | Notes |
|---|---|---|---|
| `POST` | `/podcasts` | Create podcast | 201 + `Location` header; auth: creator role |
| `POST` | `/podcasts/{id}/episodes` | Publish episode | 202 accepted (async media processing) |
| `POST` | `/subscriptions` `{podcast_id}` | Subscribe | idempotent — 200 if already subscribed |
| `DELETE` | `/subscriptions/{podcast_id}` | Unsubscribe | 204 |
| `GET` | `/feed?cursor=&limit=` | Personalized feed | cursor pagination (see below) |
| `GET` | `/podcasts/{id}/episodes?cursor=&limit=` | Podcast episodes | cursor pagination |

**WHY these choices:**
- `POST /subscriptions` with body (not `PUT /users/{u}/subscriptions/{p}`): subscription is
  a relationship resource; POST is idempotent here via dedupe key. Say why.
- **Cursor pagination, not offset:** offset (`?page=3`) skips/duplicates rows when new
  episodes arrive between requests — the classic feed bug. Cursor = `(published_at, id)`
  is stable under inserts. This is a high-signal detail; interviewers look for it.
- `202 Accepted` for episode publish: media upload/transcode is slow; decouple via async
  pipeline, return immediately.

### Data model

```sql
-- WHY relational for metadata: strong consistency for subscribe/unsubscribe and
-- podcast catalog; joins are simple; scale via read replicas + sharding later.
users(id PK, email, created_at)
podcasts(id PK, creator_id FK, title, description, created_at)
episodes(id PK, podcast_id FK, title, audio_url, duration_s, published_at, INDEX(podcast_id, published_at DESC))
subscriptions(user_id, podcast_id, created_at, PK(user_id, podcast_id))
```

Feed materialization: **fan-out-on-write (push)** vs. **fan-out-on-read (pull)** — the core
decision (below).

### High-level architecture

```
[Client] → [API Gateway / LB] → [Feed Service] → [Cache (Redis): feed:{user_id}]
     → [Subscription Service] → [Postgres (sharded by user_id)]
     → [Episode Service] → [Postgres (sharded by podcast_id)] + [Object Store (audio)]
[Ingest pipeline: upload → transcode workers → metadata write → fan-out queue (Kafka)]
```

**Request flows:**
- Publish: creator uploads → object store → transcode workers → episode row written →
  event to Kafka → fan-out workers push episode id into followers' feed caches.
- Read feed: check Redis `feed:{user_id}` (precomputed list of episode ids) → batch-fetch
  episode metadata → return. Cache miss → fall back to pull (query subscriptions +
  episodes) and repopulate.

### The key decision: push vs. pull (fan-out) — and WHY

| | Push (fan-out on write) | Pull (fan-out on read) |
|---|---|---|
| Write cost | O(followers) per episode | O(1) |
| Read cost | O(1) cache lookup | O(subscriptions) merge |
| Best for | normal users, read-heavy | celebrity podcasts (millions of followers) |

**WHY hybrid (the answer Confluent wants):** pure push collapses when a top podcast
publishes (millions of cache writes, thundering herd). Pure pull makes every feed read do
a scatter-gather merge — p99 suffers. The standard answer: **push for normal podcasts,
pull for celebrities** (threshold ~10k followers). Say the threshold is tunable and
justify it with the read/write ratio.

### Back-of-envelope scale

- Assume 10M DAU, each loads feed 5×/day → 50M feed reads/day ≈ **600 RPS average**,
  ~3k RPS peak (5×).
- Episode publishes: 100k/day ≈ 1.2 RPS — trivial; the cost is fan-out, not the write.
- Storage: 100M episodes × 1KB metadata = **100GB** (fits comfortably in sharded Postgres);
  audio in object store: 100M × 50MB = 5PB (object store's problem, not ours — say that).
- Cache: feed per user = 500 episode ids × 16B = 8KB → 10M users = **80GB** Redis —
  shardable, and only active users need resident feeds (LRU the rest).

### Failure handling and trade-offs

- **Cache stampede on celebrity publish:** pull-path for celebrities avoids it by design.
- **Fan-out worker lag:** feed briefly stale — acceptable per our consistency choice;
  monitor queue depth, autoscale workers.
- **DB sharding:** subscriptions sharded by `user_id` (query pattern), episodes by
  `podcast_id` (write pattern) — shard by query pattern, say why.
- **Hot partitions:** celebrity podcast rows — mitigated by the pull path + read replicas.
- **CAP:** AP for feed reads (available + partition-tolerant, eventually consistent);
  CP for subscription writes (a subscribe must not be lost — use quorum writes).

### What to say out loud / pitfalls

- Open with: "Reads dominate writes ~500:1, and a slightly stale feed is fine — that
  pushes me toward push-based fan-out with a pull fallback for celebrities."
- Pitfall: offset pagination in a live feed (duplicates/skips).
- Pitfall: pure push without addressing the celebrity problem.
- Pitfall: putting audio bytes in the database instead of object storage.

---
## SD2. URL Shortener (TinyURL)

**Frequency:** 4 posts. Interview focus per reports: scalability, reliability, DB/cache
sharding, resource calculations, read-heavy optimization.

### Requirements

**Functional:**
- `POST /shorten {long_url}` → short URL (e.g. `sho.rt/aB3x9Z`).
- `GET /{short_key}` → 302 redirect to long URL.
- Optional: custom aliases, expiry, click analytics.

**Non-functional:**
- Read-heavy: ~100:1 read:write ratio (redirects dominate).
- Latency: redirect p99 < 50ms (it's in the critical path of a click).
- Availability: 99.99% for reads; short links must never break (durability).
- Scale: 100M URLs/month written; 10B redirects/month.

### API design

| Method | Endpoint | Response | Notes |
|---|---|---|---|
| `POST` | `/api/v1/urls` `{url, custom_alias?, ttl?}` | `201 {short_url, key}` | 409 if alias taken; validate URL, normalize |
| `GET` | `/{key}` | `302 Location: <long_url>` | cacheable; 404 for unknown/expired |

**WHY `302` not `301`:** 301 is cached permanently by browsers — you can never change or
expire the mapping or count clicks accurately. 302 keeps control server-side. This is a
classic interview probe — have the answer ready. (Use 301 only if links are guaranteed
immutable *and* you don't need analytics.)

### Key generation — the core decision: counter + base62 vs. hash, and WHY

**Chosen: distributed unique-ID counter → base62 encode.**

- **How:** a ZooKeeper/etcd-backed range allocator hands each app server a block of ids
  (e.g. 1M at a time); servers encode locally with base62 (`0-9a-zA-Z`, 62 chars).
  7 chars → 62⁷ ≈ 3.5 trillion keys.
- **WHY not MD5/hash of the URL:** hashes collide (birthday paradox) → need
  collision-resolution loops; same URL → same hash (fine) but different URLs can collide
  (bad); hash output is long, requiring truncation which *increases* collisions. Counter
  ids are guaranteed unique with zero collision logic.
- **WHY not a single DB auto-increment:** single point of contention and failure at
  100M writes/month; range allocation removes the per-write coordination (each server
  works independently until its block runs out).
- **WHY base62:** URL-safe, compact, no ambiguous characters to confuse users. (base64
  includes `+/=` which need escaping.)
- **Custom aliases:** separate namespace checked first; 409 on conflict.

### Data model

```sql
-- WHY relational: the mapping is a simple key→value with strong durability needs;
-- range lookups by key are trivially shardable.
urls(
  short_key  VARCHAR(16) PK,   -- base62 id, also the shard key
  long_url   TEXT NOT NULL,
  created_at TIMESTAMP,
  expires_at TIMESTAMP NULL,
  creator_id BIGINT NULL
)
-- Secondary: clicks(key, ts) in a columnar/OLAP store for analytics (not on read path)
```

### High-level architecture

```
[Client] → [CDN / Edge] → [LB] → [API servers (stateless)]
    → [Redis cache: key → long_url (85%+ hit rate target)]
    → [Postgres/MySQL sharded by short_key] → [Range allocator (ZK/etcd)]
[Async: click events → Kafka → analytics warehouse]
```

**Read path (the hot path):** `GET /{key}` → check Redis → hit: 302 immediately (~5ms);
miss: DB lookup → populate cache → 302. Cache-aside (lazy population).

**WHY cache-aside over write-through:** the workload is read-heavy with a long tail —
write-through would cache millions of links nobody ever clicks. Cache-aside only stores
what's actually requested. Say the 80/20: a small fraction of links gets most clicks.

### Scale estimates

- Writes: 100M/month ≈ **40 writes/sec** — trivial for any DB.
- Reads: 10B/month ≈ **4k reads/sec average**, ~20k peak. With 85% cache hit: ~600 DB
  reads/sec — one modest Postgres primary + replicas handles it, but shard anyway for
  growth (range-based sharding on `short_key`, per the reports' hint).
- Storage: 100M/month × ~500B/row ≈ **50GB/month** → 600GB/year before TTL cleanup.
- Cache: top 20% of keys ≈ working set; size Redis for ~100GB with LRU.

### Sharding, failure handling, trade-offs

- **Range-based sharding on `short_key`:** keys are random-ish base62, so range shards
  distribute evenly (no hot shard from sequential ids — another reason base62-encoded
  *random-looking* counter blocks beat raw sequential ids). Rebalance by splitting ranges.
- **Cache failure:** fall back to DB (degraded latency, not outage). Cache stampede on a
  viral link: request coalescing (singleflight) — only one DB fetch per key at a time.
- **DB failure:** read replicas take over; writes queue briefly (durable intent log) —
  writes are low-rate so brief buffering is safe.
- **CAP:** AP for reads (serve slightly stale mapping rather than fail); CP for the
  id allocator (duplicate ids would be catastrophic — correctness over availability there).

### What to say out loud / pitfalls

- Open with: "100:1 read-heavy, so everything optimizes the redirect path: cache-aside,
  302 not 301, counter+base62 for collision-free keys."
- Pitfall: saying 301 (breaks analytics and mutability).
- Pitfall: hash-based keys without addressing collisions.
- Pitfall: forgetting the analytics path must be async (never block the redirect on it).

---

## SD3. Distributed Persistent Key-Value Store

**Frequency:** 2 posts. Framing from reports: "high throughput, low latency, fault-tolerant
persistent KV store as a network service; get/put/delete; high write throughput."

### Requirements

**Functional:** `get(key)`, `put(key, value)`, `delete(key)` over a network API.
Keys/values are opaque bytes.

**Non-functional:**
- High write throughput (write-heavy, unlike the URL shortener).
- Low latency: p99 < 10ms for reads.
- Fault-tolerant: survive node failures without data loss.
- Persistent: data survives process restarts (unlike pure memcache).
- Scale: 10TB+ data, 100k+ ops/sec, linear horizontal scaling.

### API design

```
PUT    /v1/kv/{key}   {value}      → 200 (or 201)
GET    /v1/kv/{key}                → 200 {value} / 404
DELETE /v1/kv/{key}                → 204 / 404
```

Versioning for conflicts: each write carries a vector clock or last-write-wins timestamp —
say which and why (below).

### Data model / storage engine

Per node: **LSM-tree** (like LevelDB/RocksDB) for the persistent store.

**WHY LSM over B-tree:**
- Write-heavy workload → LSM turns random writes into sequential log appends + batched
  memtable flushes: far higher write throughput than B-tree's random page writes.
- Reads pay a merge cost across levels, mitigated by Bloom filters per SSTable (skip
  levels that can't contain the key) + block cache. Say both mitigations.
- Alternative B-tree (InnoDB-style): better for read-heavy point lookups with in-place
  updates, worse write amplification. Name the trade-off; LSM wins for this spec.

```
[Memtable (RAM, sorted)] → immutable → flush → [SSTables L0..Ln on SSD]
Write-ahead log (WAL) for crash recovery before memtable ack
Bloom filter per SSTable to skip irrelevant levels on reads
```

### High-level architecture

```
[Client] → [Coordinator / smart client w/ partition map]
    → consistent-hash ring → [Storage nodes (each: LSM engine)]
[Replication: each key on N=3 nodes, quorum R+W > N]
[Gossip-based membership + failure detection; anti-entropy repair]
```

**Partitioning: consistent hashing — WHY:**
- Keys hash onto a ring; each node owns arcs of the ring. Adding/removing a node moves
  only ~1/N of keys (vs. mod-N hashing which reshuffles everything). Minimal data
  movement on membership change is *the* reason — say it verbatim.
- Virtual nodes (vnodes, e.g. 256/node) smooth out imbalance from random hashing.

**Replication + consistency: quorum (Dynamo-style) — WHY:**
- N=3, W=2, R=2: tolerates 1 node failure; R+W > N gives strong consistency for the
  common case. Tune per operation: reads that can be stale use R=1 (lower latency).
- **WHY quorum over primary-backup:** no failover promotion, no single-writer bottleneck,
  writes succeed during partitions (with hinted handoff). Cost: conflict resolution.
- **Conflict resolution:** vector clocks + application merge, or last-write-wins with
  logical timestamps. LWW is simpler and usually sufficient for opaque blobs — say when
  you'd need vector clocks (concurrent writes to the *same* key from partitioned clients
  where losing a write is unacceptable).

### CAP positioning — say this explicitly

This design is **AP with tunable consistency**: available during partitions (sloppy quorum
+ hinted handoff), consistent when R+W>N. Contrast with CP alternatives (Raft/Paxos per
shard — stronger consistency, writes block without a quorum/leader). For a general KV
store at Confluent-scale write throughput, AP+tunable is the defensible default; choose
CP only if the interviewer stresses linearizability (e.g. coordination metadata).

### Failure handling

| Failure | Handling |
|---|---|
| Node crash | WAL replay on restart; replicas serve reads (R still satisfiable); hinted handoff replays missed writes |
| Disk corruption | SSTable checksums; restore from replica + anti-entropy (Merkle-tree sync) |
| Network partition | Sloppy quorum keeps writes flowing; read-repair reconciles on healing |
| Hot key | Key-level caching at coordinator; consider replicating hot keys wider (say as an option) |
| Thundering restart | Stagger restarts; throttle anti-entropy to avoid cascade |

### Scale estimates

- 100k ops/sec ÷ 1k ops/sec/node ≈ **100 storage nodes** (3× replication → ~300 node-instances,
  or 100 physical nodes × 3 roles — clarify the counting).
- 10TB ÷ 100 nodes = 100GB/node — comfortable for SSD + LSM.
- Network: values ~1KB → 100k × 1KB = 100MB/s aggregate — fine.

### Single-host vs. distributed (the report mentions both)

- Single host (LevelDB/RocksDB embedded): zero network, no consistency problem — right
  choice when data fits one machine and only the local process needs it.
- Distributed: needed exactly when data or throughput exceeds one box. The interview
  framing ("network service, high write throughput") forces distributed — say why the
  simpler option doesn't meet the spec.

### What to say out loud / pitfalls

- Open with: "Write-heavy + fault-tolerant + persistent → LSM per node, consistent hashing
  across nodes, quorum replication, AP with tunable consistency."
- Pitfall: proposing B-trees without justifying against the write-heavy spec.
- Pitfall: mod-N partitioning (reshuffles everything on scaling).
- Pitfall: claiming strong consistency *and* full availability during partitions — pick a
  side and justify it.

---

## SD Briefs (lower frequency — know the shape, not the full deep dive)

### TempMail — temporary email service (5-hour expiry)

- **Requirements:** generate disposable address, receive mail for 5h, auto-delete after.
- **Key decisions:** expiry via TTL column + lazy deletion on read plus a periodic sweeper
  (same pattern as Coding Q1 — say the connection); addresses as random tokens (unguessable,
  no enumeration); inbound mail via MX → queue → lookup token → store.
- **WHY lazy + sweeper:** reads are the common path; a pure background sweeper leaves
  expired-but-unread mail visible. Both, like the TTL cache.
- **Access control:** token-in-URL is the credential (no accounts by design); rate-limit
  creation per IP to prevent abuse.

### Movie Ticketing Platform

- **Requirements:** browse movies/showtimes, seat selection, booking, payment.
- **Key decisions:** seat hold with short TTL (e.g. 10 min) via reservation state machine
  (`available → held → booked`), NOT a distributed lock per seat — locks don't survive
  crashes, TTL'd holds do. Idempotency keys on the booking endpoint (double-clicks,
  retries). Optimistic concurrency on the seat row (version column) to prevent
  double-booking.
- **WHY TTL holds over locks:** failure of the holder must self-heal; a lock needs a
  failure detector, a TTL just needs a clock.
- **Scale note:** contention is per-showtime (tiny shard of the data) — partition by
  theater/showtime; the rest is a standard catalog + checkout flow.

### Stock Alert Notification System (1M+ rules, notify within a minute)

- **Requirements:** users define rules ("alert me if AAPL > $200"); evaluate against price
  stream; notify (push/email/SMS) within 60s of trigger.
- **Key decisions:** stream processing (Kafka → Flink/Spark Streaming) over the price feed;
  rules indexed by symbol (only evaluate AAPL rules on AAPL ticks — the fan-out that
  matters); per-user dedupe/cooldown so a hovering price doesn't spam (state store with
  "last alerted" timestamp).
- **WHY stream over poll:** 1M rules × polling = 1M queries/min against a price API;
  stream evaluation is O(ticks × rules-per-symbol) and naturally meets the 60s SLA.
- **Delivery:** at-least-once with idempotent notification keys (better a duplicate alert
  than a missed one — say the trade-off); dead-letter queue for failed sends.

---

# Closing notes — Confluent-specific patterns across all questions

1. **Concurrency is the through-line.** Nearly every coding question has a concurrency
   follow-up. Default posture: start single-threaded and correct, then discuss the
   escalation (coarse lock → RW lock → sharding → lock-free) with trade-offs.
2. **Streaming/time is the domain.** TTLs, windows, increasing timestamps, Kafka-style
   event flows — Confluent *is* a streaming company. Reach for time-aware structures
   (heaps by expiry, ring buffers, LSM) and say why the domain favors them.
3. **Say the reduction.** Time-based KV with aggregates → WindowedMap. TempMail expiry →
   TTL cache. Recognizing "this is the same problem in a new costume" is a strong-hire
   signal.
4. **Fully running code on-site.** No pseudocode stubs. The reference implementations above
   all run as-is — type them, don't narrate them.
