### Answer from chatGPT [here](https://chatgpt.com/s/t_6acdc6bd0c208191b8aec960852ae1c9)

# Confluent Senior Coding Round: Data Structures + Concurrency (Python)

The round you pasted: *initial coding, then expand it with more intricate data structures, then discuss concurrency impact, and system design if time permits; evaluated on understanding of concurrency and clean code.*

This guide has the **questions candidates have reported for Confluent**, the **likely extensions** an interviewer will bolt on, and a **ladder for every "now make it thread-safe" follow-up**. All code is Python 3 (standard library only), and every code block was extracted and run with tests.

Companion files from this conversation: `python-concurrency-interview-guide.md` (bounded queue, thread pool, rate limiter, thread-safe LRU, readers-writer lock, scheduler, KV store with transactions, resource pool), `confluent-file-operations-interview-guide.md` (tail, file search, external sort) and `confluent-document-search-answer.md` (phrase search plus AND/OR). I don't repeat those here; I point to them.

> **Caveat on sources.** Everything "reported" below comes from public interview posts and summaries (LeetCode Discuss, Glassdoor, PracHub, TechPrep, one blog). I saw search snippets or page excerpts, not full threads. Prompts are paraphrased by candidates, so details may differ in your interview. Items marked **predicted** are my extrapolation from the round description and Confluent's domain (Kafka), not reports.

## Contents

1. [What has been reported](#1-what-has-been-reported)
2. [How to run this round](#2-how-to-run-this-round)
3. [The "make it thread-safe" ladder](#3-the-make-it-thread-safe-ladder)
4. [Question inventory](#4-question-inventory)
5. Reported: [Q1 Function library with variadics](#q1-function-library-with-variadic-signatures-reported-confluent-phone-screen) · [Q2 TTL cache, LRU with TTL, windowed average](#q2-ttl-cache-lru-with-ttl-and-windowed-average-reported) · [Q3 Thread-safe, then without a global lock](#q3-thread-safe-then-without-a-global-lock-reported-follow-up) · [Q4 Time-windowed map and hit counter](#q4-time-windowed-map-and-hit-counter-reported-theme-spec-unknown) · [Q5 Sudoku validate and solve](#q5-sudoku-validate-in-one-traversal-then-solve-reported)
6. Predicted: [Q6 LFU cache](#q6-lfu-cache-in-o1-predicted) · [Q7 In-memory message broker](#q7-in-memory-message-broker-with-consumer-groups-predicted-kafka-flavoured) · [Q8 Consistent hashing ring](#q8-consistent-hashing-ring-predicted) · [Q9 Bloom filter](#q9-bloom-filter-for-stream-dedup-predicted) · [Q10 Event-time windows and watermarks](#q10-event-time-windows-with-a-watermark-predicted-kafka-streams-flavoured)
7. [Concurrency theory: questions and answers](#7-concurrency-questions-and-answers-the-discussion-part)
8. [Systems design discussion](#8-systems-design-discussion-for-senior-candidates)
9. [Sources](#9-sources)

---

## 1. What has been reported

| Reported item | Detail | Source |
|---|---|---|
| **Format** | Phone screen about 60 min on HackerRank/CoderPad: a medium algorithm problem plus a concurrency or design follow-up. Onsite coding about 60 min; onsite low-level design about 60 min (thread-safe data structures, correctness under concurrent callers). *Single blog; treat as unconfirmed.* | techinterview.org |
| **Follow-ups are the point** | "Implement a data structure, then make it thread-safe, or reason about its behaviour under partial failure." | TechPrep Confluent guide |
| **"Without a global lock"** | "Make the cache thread-safe. Now make it thread-safe without a single global lock, because that lock is your throughput ceiling." *Single blog; plausible, unconfirmed.* | techinterview.org |
| **Function library with variadic arguments** | `register(Set<Function>)` and `findMatches(List<String> argumentTypes)`; a function may be variadic, meaning its last argument can occur one or more times. Confluent senior phone interview. A similar zero-or-more version was reported for another company | LeetCode Discuss (Confluent phone interview); PracHub (variant) |
| **LRU cache with TTL** | Reported as a recent coding question | TechPrep |
| **Windowed average** | "Implement a cache where each item has an expiration time; return the average of the valid elements at any point in time." First round of a Senior/Staff loop | LeetCode Discuss |
| **Thread-safe LRU or time-windowed map** | "The concurrency questions ask you to build thread-safe structures yourself"; at least one virtual-onsite session is on concurrent data structures and synchronization | PracHub Confluent guide |
| **Multi-threaded data structure take-home** | Phone interview, then a take-home implementing a multi-threaded data structure, then another phone interview. Advice: revise locks, condition variables and language primitives | Glassdoor |
| **Sudoku** | Validate a filled board **in one traversal** (and run tests); extension: solve an unsolved board with backtracking (not implemented). TechPrep also lists a Sudoku solver | LeetCode Discuss; TechPrep |
| **Last N lines of a large file** | Logging-style `tail` with minimal memory | TechPrep (see the file-operations guide) |
| **Document phrase search** | Phrase search over documents, follow-up AND/OR/brackets | LeetCode Discuss (see the document-search answer) |
| **Systems design for seniors** | TinyURL (read-heavy, sharded DB, caches); Spotify-like podcast API (pagination, versioning, estimates) | LeetCode Discuss |

---

## 2. How to run this round

1. **Clarify** inputs, scale, time/clock semantics (is expiry `<` or `<=`?), whether single-threaded *for now*. Ask: *"Should I design for concurrent callers, or get a correct single-threaded version first?"* (Seniors are expected to ask.)
2. **Write the simple correct version first**, with an **injected clock** (`clock=time.monotonic`) so tests are deterministic. Say the invariants out loud.
3. **Test as you go**: tiny cases, edge cases, then a randomized comparison against a brute-force model (the fastest way to find bugs, and it impresses).
4. **Expand**: the interviewer will push on complexity ("can `average()` be O(1)?"), then on a harder variant ("with per-item TTL", "with capacity", "zero-or-more").
5. **Concurrency discussion**: identify *shared mutable state and the invariant across it*, choose the lock granularity, then walk the [ladder](#3-the-make-it-thread-safe-ladder). Name the trade-offs, don't just add `with lock:`.
6. **Close with**: complexity, what breaks at scale, how you would test concurrency, what you'd monitor.

---

## 3. The "make it thread-safe" ladder

Every follow-up of this type is solved by walking up this ladder as far as the question demands. Say which rung you are on and why.

| Rung | Technique | Use when | Cost / catch |
|---|---|---|---|
| 0 | **Name the shared state and the invariant** ("`_sum` always equals the sum of live values"; "`_d` and the expiry heap agree") | always, first | Invariants spanning *two* structures are why per-structure locks aren't enough |
| 1 | **One coarse lock** around every public method | baseline; correct; low contention | Throughput ceiling: all operations serialize |
| 2 | **Shorten critical sections**; never do I/O or call user code (loaders, callbacks) under the lock | any | Needs care that the invariant still holds between the sections |
| 3 | **Read-write lock** | read-heavy, reads truly don't mutate | **Trap:** in an LRU/LFU/TTL cache `get` *mutates* recency, frequency or expiry, so it is a write. An RW lock gives no gain there |
| 4 | **Lock striping / sharding** (N independent shards, each with its own lock, route by `hash(key) % N`) | the answer to "without a global lock" | Cross-shard operations (global average, global LRU order, snapshot) become approximate, or need all locks taken in a fixed order |
| 5 | **Immutable snapshot / copy-on-write**: build a new structure, publish with one atomic reference swap; readers read the reference once | read-mostly, rare updates (function library, routing table, consistent hash ring) | Write cost O(size); readers may see slightly stale data |
| 6 | **Lock-free / atomics (CAS)** | hot counters, queues in Java/C++ (`AtomicLong`, `LongAdder`, `ConcurrentHashMap`) | Hard to get right (ABA, memory ordering); Python has no CAS primitive, so say you'd use a lock or sharded counters |
| 7 | **Confinement**: one thread owns the data; others send it messages (queue/actor/event loop) | when you can partition the work | This is how Kafka Streams works: one task per partition, local state, no locks |

**Also be ready to say:**
- **Partial failure:** what if `loader()` raises (release the lock, wake waiters, don't cache the failure), a thread dies holding a lock (`with` releases it; a crashed *process* does not, so use leases/timeouts for distributed locks), a node crashes mid-write (atomic swap/rename, write-ahead log, idempotent retries)?
- **Deadlock avoidance:** fixed lock order, all-or-nothing acquisition, `acquire(timeout=...)`.
- **How I'd test it:** stress test with many threads and an invariant check at the end; run with timeouts to detect deadlock; randomize `time.sleep(0)` yields to widen race windows; in Java use jcstress / thread sanitizers.

---

## 4. Question inventory

| # | Question | Status | Core ideas |
|---|---|---|---|
| Q1 | Function library with variadic signatures (`register`, `findMatches`) | **Reported** (Confluent phone) | Trie over argument types, suffix-uniform check, copy-on-write |
| Q2 | TTL cache; LRU with TTL; windowed average of valid items | **Reported** | Hash map + expiry heap with lazy deletion, running sum, injected clock |
| Q3 | Make it thread-safe; then without a global lock | **Reported** (follow-up) | Coarse lock, sharding, ordered multi-lock snapshot |
| Q4 | Time-windowed map; hit counter (spec unknown) | Reported theme | Binary search by timestamp, bucketed ring |
| Q5 | Validate a filled Sudoku in one traversal; solve it | **Reported** | Bitmasks, backtracking with MRV |
| Q6 | LFU cache in O(1) | Predicted | Frequency buckets of ordered dicts |
| Q7 | In-memory message broker with partitions and consumer groups | Predicted | Append-only log, offsets, rebalance, lost-wakeup-safe polling |
| Q8 | Consistent hashing ring | Predicted | Virtual nodes, bisect, immutable snapshot |
| Q9 | Bloom filter | Predicted | Double hashing, race on shared bytes |
| Q10 | Event-time windows with watermark | Predicted | Tumbling/hopping windows, lateness, ordered emission |
| Q11 | Concurrency theory Q&A | Reported theme | See section 7 |
| Q12 | System design | Reported for seniors | See section 8 |

Already covered in companion guides: bounded blocking queue, thread pool, rate limiter, thread-safe LRU with single-flight loading, readers-writer lock, delayed-task scheduler, resource pool with priorities, KV store with transactions (`python-concurrency-interview-guide.md`); `tail -n` (`confluent-file-operations-interview-guide.md`); phrase search and AND/OR (`confluent-document-search-answer.md`).

---

## Q1. Function library with variadic signatures (reported, Confluent phone screen)

> *`register(Set<Function>)` and `findMatches(List<String> argumentTypes)`. A `Function` has a name, a list of argument types and `isVariadic`; if variadic, the **last argument type can occur one or more times**. Return all registered functions that match the call's argument types.*
>
> Reported example: `A:[String,Integer,Integer]`, `B:[String,Integer] variadic`, `C:[Integer] variadic`, `D:[Integer,Integer] variadic`, `E:[Integer,Integer,Integer]`, `F:[String]`, `G:[Integer]`.
> `findMatches([String]) → [F]`; `[Integer] → [C, G]`; `[Integer×4] → [C, D]`; `[Integer×3] → [C, D, E]`.

**Clarify:** zero-or-more or one-or-more occurrences of the variadic type? (The Confluent example is **one or more**: `B` does *not* match `[String]`. A similar question reported for another company says zero or more; the code below takes a `min_repeat` parameter.) Output order? (I use registration order.) Duplicate registrations? Subtype matching (`Integer` is a `Number`)? Case sensitivity?

**Approach, from naive to expected**

| Version | `findMatches` cost | Comment |
|---|---|---|
| Scan all functions, test each | O(F · n) | Correct baseline. Say it first |
| **Trie over argument types** | O(n + matches) | Query cost no longer depends on how many functions are registered |

**Trie design and why**

- Each function is inserted along the path of its **fixed** argument types. For a non-variadic function that is *all* its types, and it is recorded in the final node's `exact` list. For a variadic function it is the types **except the last**, and it is recorded in that node's `variadic[last_type]` list.
- To answer a query `q[0..n)`, walk the trie along `q`. At each depth `d` (the node reached after consuming `q[:d]`), a variadic function stored there with type `T` matches iff **`q[d:]` is non-empty and every element equals `T`**. Precompute `uniform[d]` (is `q[d:]` all one type?) from the right in O(n), then it is one dict lookup per depth. At depth `n`, collect the node's `exact` list.
- Total O(n) plus output size, regardless of the number of registered functions. Sort the hits by registration order at the end.

**Concurrency angle:** reads (`findMatches`) vastly outnumber writes (`register`). Use **copy-on-write**: `register` rebuilds the trie and publishes it with one reference assignment; `findMatches` reads the reference **once** into a local variable and works on that immutable snapshot, so it never sees a half-built trie and needs no lock. Writers take a lock only to serialize themselves. (The API already registers a *set* at a time, which fits batch rebuilds.)

```python
# file: funclib.py
import threading
from dataclasses import dataclass


@dataclass(frozen=True)
class Function:
    name: str
    argument_types: tuple
    is_variadic: bool = False

    def __post_init__(self):
        object.__setattr__(self, "argument_types", tuple(self.argument_types))   # accept lists, stay hashable
        if self.is_variadic and not self.argument_types:
            raise ValueError("a variadic function needs at least one argument type")


def matches(fn, query, min_repeat=1):
    """Reference implementation (used as the test oracle): O(len(query)) per function."""
    p, q = fn.argument_types, tuple(query)
    if not fn.is_variadic:
        return q == p
    fixed, last = p[:-1], p[-1]
    rest = q[len(fixed):]
    return q[:len(fixed)] == fixed and len(rest) >= min_repeat and all(t == last for t in rest)


class _Node:
    __slots__ = ("children", "exact", "variadic")

    def __init__(self):
        self.children = {}        # argument type -> _Node
        self.exact = []           # (order, fn): non-variadic functions ending exactly here
        self.variadic = {}        # last type -> [(order, fn)]; the fixed prefix is the path to this node


class FunctionLibrary:
    def __init__(self, min_repeat=1):
        assert min_repeat in (0, 1)            # 1: "one or more" (Confluent), 0: "zero or more"
        self._min_repeat = min_repeat
        self._write_lock = threading.Lock()    # serializes writers only; readers never lock
        self._functions, self._known = [], set()
        self._root = _Node()

    def register(self, functions):
        with self._write_lock:
            added = False
            for fn in functions:
                if fn not in self._known:      # duplicate registrations are ignored
                    self._known.add(fn)
                    self._functions.append(fn)
                    added = True
            if added:
                self._root = self._build(self._functions)   # ONE reference swap publishes the new trie

    @staticmethod
    def _build(functions):
        root = _Node()
        for order, fn in enumerate(functions):
            node = root
            fixed = fn.argument_types[:-1] if fn.is_variadic else fn.argument_types
            for t in fixed:
                node = node.children.setdefault(t, _Node())
            if fn.is_variadic:
                node.variadic.setdefault(fn.argument_types[-1], []).append((order, fn))
            else:
                node.exact.append((order, fn))
        return root

    def find_matches(self, argument_types):
        root = self._root                      # read the reference ONCE: a consistent immutable snapshot
        q = tuple(argument_types)
        n = len(q)
        uniform = [False] * (n + 1)            # uniform[d]: q[d:] is non-empty and all of one type
        for d in range(n - 1, -1, -1):
            uniform[d] = d == n - 1 or (uniform[d + 1] and q[d] == q[d + 1])
        hits, node = [], root
        for d in range(n + 1):
            if d < n and uniform[d]:
                hits.extend(node.variadic.get(q[d], ()))
            if d == n:
                hits.extend(node.exact)
                if self._min_repeat == 0:      # zero repetitions: the query is just the fixed prefix
                    for lst in node.variadic.values():
                        hits.extend(lst)
                break
            node = node.children.get(q[d])
            if node is None:
                break
        hits.sort(key=lambda h: h[0])          # registration order
        return [fn for _, fn in hits]
```

```python
# file: funclib.py
import random


def test_reported_example():
    S, I = "String", "Integer"
    fs = {n: Function(n, t, v) for n, t, v in [
        ("A", [S, I, I], False), ("B", [S, I], True), ("C", [I], True), ("D", [I, I], True),
        ("E", [I, I, I], False), ("F", [S], False), ("G", [I], False)]}
    lib = FunctionLibrary()
    lib.register(fs.values())           # the prompt passes a Set; a fixed order here makes the output order deterministic
    names = lambda q: [f.name for f in lib.find_matches(q)]
    assert names([S]) == ["F"]
    assert names([I]) == ["C", "G"]
    assert names([I] * 4) == ["C", "D"]
    assert names([I] * 3) == ["C", "D", "E"]
    assert names([S, I, I]) == ["A", "B"]
    assert names([S, I]) == ["B"] and names([]) == [] and names([S, S]) == []


def test_matches_oracle_and_zero_or_more():
    rnd = random.Random(4)
    for min_repeat in (0, 1):
        for _ in range(200):
            fns = []
            for i in range(rnd.randint(0, 8)):
                types = [rnd.choice("IS") for _ in range(rnd.randint(0, 4))]
                variadic = bool(types) and rnd.random() < .5
                fns.append(Function(f"f{i}", types, variadic))
            lib = FunctionLibrary(min_repeat)
            lib.register(fns)
            for _ in range(15):
                q = [rnd.choice("IS") for _ in range(rnd.randint(0, 5))]
                want = [f for f in fns if matches(f, q, min_repeat)]
                assert lib.find_matches(q) == want, (fns, q, min_repeat)


def test_concurrent_register_and_find():
    lib, errors, stop = FunctionLibrary(), [], threading.Event()

    def reader():
        while not stop.is_set():
            res = lib.find_matches(["I", "I"])
            names = [f.name for f in res]
            if names != sorted(names, key=lambda s: int(s[1:])):       # always a consistent registration-ordered view
                errors.append(names)

    ts = [threading.Thread(target=reader) for _ in range(4)]
    for t in ts:
        t.start()
    for i in range(300):
        lib.register([Function(f"f{i}", ["I", "I"] if i % 2 else ["I"], i % 2 == 0)])
    stop.set()
    for t in ts:
        t.join(10)
    assert not errors
    assert len(lib.find_matches(["I", "I"])) == 300


if __name__ == "__main__":
    test_reported_example()
    test_matches_oracle_and_zero_or_more()
    test_concurrent_register_and_find()
    print("funclib OK")
```

**Follow-ups to expect**

- *"Subtype matching / wildcards (`Integer` is a `Number`, `Object` accepts anything)."* Replace the single `children.get(q[d])` with a DFS that follows every compatible child (exact type and its supertypes), carrying each branch's depth; keep the same `uniform` idea per variadic type. Cost grows with the branching factor; mention caching.
- *"Return the **most specific** match (overload resolution like Java)."* Rank candidates: exact fixed signature beats variadic; fewer variadic expansions beat more; ties are ambiguous (raise).
- *"Variadic in the middle / multiple variadics."* The `uniform` suffix trick no longer works; use an NFA/DP over (position in query, position in signature).
- *"Unregister a function."* With copy-on-write, rebuild without it; or tombstone it in a set checked at query time and rebuild lazily.
- *"Millions of registrations, rare updates."* Incremental persistent trie (path copying) instead of full rebuild, so each registration costs O(depth).

---

## Q2. TTL cache, LRU with TTL, and windowed average (reported)

> *Implement a cache where each item has an expiration time, and return the average of the currently valid elements at any point in time.* Reported variants: LRU cache with TTL, time-windowed map.

**Clarify:** Expiry boundary: valid while `now < expires_at` (I use this; say it). Are values numbers (needed for the average)? Per-item TTL, or one TTL for all? Capacity? What does `average()` return when nothing is valid (I return `None`; `0.0` or an exception are also defensible, ask)? Is time injected or the wall clock? (Use `time.monotonic()`, not `time.time()`, which can jump backwards.)

**Approach and why**

- **Dict for lookups, expiry heap for expiration.** A min-heap of `(expires_at, seq, key)` finds the next item to expire in O(1) and removes it in O(log n). Items are *overwritten* and *deleted* too, so heap entries become stale; rather than searching the heap (O(n)) use **lazy deletion**: when an entry pops, check it is still the key's *current* version (the `seq` stored in the dict matches). Each entry is pushed once and popped once: **amortized O(log n)** per operation.
- **Expire on access (no background thread).** Every public method first purges everything with `expires_at <= now`. State is then *exactly* "what is valid right now", so no reader can observe an expired value. A background reaper is optional (to free memory of untouched keys) and brings thread-safety issues of its own.
- **Running sum.** Maintain `sum` of valid values: add on insert, subtract the old value on overwrite, subtract on expiry/delete/eviction. Then `average()` = `sum / count` in O(1). The classic bug is forgetting one of those subtract paths (the randomized test below catches it). Floating-point drift over millions of updates: use ints/`Fraction`, or recompute periodically.
- **LRU on top:** keep the dict as an `OrderedDict` (`move_to_end` on access, `popitem(last=False)` to evict) and subtract the evicted value from the sum.
- **Uniform TTL special case ("sliding window average"):** expiry order equals insertion order, so a **deque** plus running sum is O(1) with no heap at all. Mentioning this shows you see the structure of the problem.
- Heap memory: stale entries live until their original expiry; if overwrites are very frequent, rebuild the heap when stale entries exceed about 2× live ones.

```python
# file: ttlcache.py
import heapq
import itertools
import threading
import time
from collections import OrderedDict, deque
from contextlib import ExitStack


class TTLCache:
    """LRU cache with per-item TTL. An item is valid at `now` iff now < expires_at.
    Keeps the sum of valid (numeric) values so average() is O(1) amortized."""

    def __init__(self, capacity=None, default_ttl=None, clock=time.monotonic, numeric=True):
        self._cap, self._default_ttl, self._clock, self._numeric = capacity, default_ttl, clock, numeric
        self._d = OrderedDict()               # key -> (value, expires_at, seq), LRU first, MRU last
        self._heap = []                       # (expires_at, seq, key); stale entries are skipped lazily
        self._seq = itertools.count()
        self._sum = 0

    # ---- public API ----
    def put(self, key, value, ttl=None):
        ttl = self._default_ttl if ttl is None else ttl
        if ttl is None:
            raise ValueError("ttl is required (no default_ttl configured)")
        now = self._clock()
        self._purge(now)
        old = self._d.pop(key, None)          # overwrite: remove the old value from the sum first
        if old is not None:
            self._adjust(-old[0])
        seq, expires = next(self._seq), now + ttl
        self._d[key] = (value, expires, seq)  # new items go to the MRU end
        self._adjust(value)
        heapq.heappush(self._heap, (expires, seq, key))
        if self._cap is not None and len(self._d) > self._cap:
            _, (evicted, _, _) = self._d.popitem(last=False)   # evict the least recently used
            self._adjust(-evicted)

    def get(self, key, default=None):
        self._purge(self._clock())
        entry = self._d.get(key)
        if entry is None:
            return default
        self._d.move_to_end(key)              # a read is a use
        return entry[0]

    def delete(self, key):
        self._purge(self._clock())
        entry = self._d.pop(key, None)
        if entry is not None:
            self._adjust(-entry[0])
        return entry is not None

    def __len__(self):
        self._purge(self._clock())
        return len(self._d)

    def average(self):
        """Mean of currently valid values, or None if there are none."""
        self._purge(self._clock())
        return self._sum / len(self._d) if self._d else None

    def snapshot(self):
        """(count, sum) of valid items at one instant; used to combine shards exactly."""
        self._purge(self._clock())
        return len(self._d), self._sum

    # ---- internals ----
    def _adjust(self, delta):
        if self._numeric:
            self._sum += delta

    def _purge(self, now):
        while self._heap and self._heap[0][0] <= now:          # expires_at <= now means expired
            _, seq, key = heapq.heappop(self._heap)
            entry = self._d.get(key)
            if entry is not None and entry[2] == seq:          # still the CURRENT version of this key
                del self._d[key]                               # (overwritten/evicted entries are just dropped)
                self._adjust(-entry[0])


class SlidingWindowAverage:
    """Uniform TTL special case: expiry order == insertion order, so a deque + running sum is O(1)."""

    def __init__(self, window, clock=time.monotonic):
        self._w, self._clock, self._q, self._sum = window, clock, deque(), 0

    def add(self, value):
        now = self._clock()
        self._expire(now)
        self._q.append((now, value))
        self._sum += value

    def average(self):
        self._expire(self._clock())
        return self._sum / len(self._q) if self._q else None

    def _expire(self, now):
        while self._q and self._q[0][0] <= now - self._w:      # same boundary as TTLCache: ts + window <= now
            self._sum -= self._q.popleft()[1]
```

### Q3. Thread-safe, then without a global lock (reported follow-up)

> *"Make the cache thread-safe." then "Now without a single global lock, because that lock is your throughput ceiling."*

**Step 1: one lock.** Every public method, including `get` (it mutates recency and purges), takes the same lock. This is correct, and you should say so before optimizing. Note again: an RW lock would be **wrong or useless** here, because `get` is a write.

**Step 2: shard.** Create `N` independent `TTLCache` shards, each with its own lock; route a key with `hash(key) % N`. Operations on different shards run in parallel. Trade-offs to state:
- **LRU becomes per-shard**: each shard evicts its own least-recently-used item, so global recency is only approximate (capacity per shard is `ceil(capacity / N)`). Caffeine and ConcurrentLinkedHashMap accept the same approximation (they record accesses in buffers and replay them to the policy).
- **Global aggregates**: `average()` needs `(count, sum)` from every shard. Locking shards **one at a time** gives a non-atomic result (items may expire or arrive between shard reads). For an **exact point-in-time** result take **all** shard locks **in index order** (a fixed global lock order makes deadlock impossible), read, release. Offer both: cheap approximate and exact.
- Hot keys still serialize on one shard; choose `N` around 4x the number of cores, and use a good hash.
- **In Python** the GIL means sharding won't raise CPU throughput much, but it models the right design and does help when work inside the lock releases the GIL. In Java, use `ConcurrentHashMap` (CAS plus per-bin locks) or Caffeine; say that you'd not hand-roll this in production.

```python
# file: ttlcache.py
class ThreadSafeTTLCache:
    """Rung 1: one coarse lock. Correct; the baseline answer."""

    def __init__(self, **kwargs):
        self._cache, self._lock = TTLCache(**kwargs), threading.Lock()

    def put(self, key, value, ttl=None):
        with self._lock:
            self._cache.put(key, value, ttl)

    def get(self, key, default=None):
        with self._lock:                   # get MUTATES (recency, purge): it needs the exclusive lock
            return self._cache.get(key, default)

    def delete(self, key):
        with self._lock:
            return self._cache.delete(key)

    def average(self):
        with self._lock:
            return self._cache.average()


class ShardedTTLCache:
    """Rung 4: N shards, each with its own lock; no global lock on the hot path."""

    def __init__(self, shards=16, capacity=None, default_ttl=None, clock=time.monotonic):
        per_shard = None if capacity is None else max(1, -(-capacity // shards))   # ceil division
        self._shards = [TTLCache(per_shard, default_ttl, clock) for _ in range(shards)]
        self._locks = [threading.Lock() for _ in range(shards)]

    def _i(self, key):
        return hash(key) % len(self._shards)

    def put(self, key, value, ttl=None):
        i = self._i(key)
        with self._locks[i]:
            self._shards[i].put(key, value, ttl)

    def get(self, key, default=None):
        i = self._i(key)
        with self._locks[i]:
            return self._shards[i].get(key, default)

    def delete(self, key):
        i = self._i(key)
        with self._locks[i]:
            return self._shards[i].delete(key)

    def average(self, exact=True):
        count = total = 0
        if exact:
            with ExitStack() as stack:                       # all locks, ALWAYS in index order: no deadlock
                for lock in self._locks:
                    stack.enter_context(lock)
                for shard in self._shards:
                    c, s = shard.snapshot()
                    count, total = count + c, total + s
        else:                                                # one shard at a time: cheap but not point-in-time
            for lock, shard in zip(self._locks, self._shards):
                with lock:
                    c, s = shard.snapshot()
                count, total = count + c, total + s
        return total / count if count else None
```

```python
# file: ttlcache.py
import random


class FakeClock:
    def __init__(self):
        self.t = 0
    def __call__(self):
        return self.t
    def advance(self, dt):
        self.t += dt


def test_ttl_basics():
    clk = FakeClock()
    c = TTLCache(clock=clk)
    c.put("a", 10, ttl=5); c.put("b", 20, ttl=10)
    assert c.average() == 15 and len(c) == 2
    clk.advance(5)                                    # a expires exactly at t=5 (valid iff now < expires)
    assert c.get("a") is None and c.average() == 20 and len(c) == 1
    c.put("b", 1, ttl=100)                            # overwrite: the old heap entry (t=10) is now stale
    clk.advance(5)                                    # t=10: the stale entry pops and must NOT delete b
    assert c.get("b") == 1 and c.average() == 1
    clk.advance(200)
    assert c.average() is None and len(c) == 0
    assert c.put("x", 3, ttl=1) is None and c.delete("x") and not c.delete("x") and c.average() is None
    try:
        TTLCache(clock=clk).put("k", 1)
        raise AssertionError("expected ValueError")
    except ValueError:
        pass


def test_lru_eviction_and_sum():
    clk = FakeClock()
    c = TTLCache(capacity=2, default_ttl=100, clock=clk)
    c.put("a", 10); c.put("b", 20); c.get("a")        # b is now the least recently used
    c.put("c", 30)                                    # evicts b
    assert c.get("b") is None and c.average() == 20   # (10 + 30) / 2
    c.put("a", 50)                                    # overwrite must drop the old 10 from the sum
    assert c.average() == 40


def test_random_against_model():
    class Model:                                      # obviously-correct O(n) reference
        def __init__(self, cap):
            self.cap, self.items, self.order = cap, {}, []
        def purge(self, now):
            for k in [k for k, (_, e) in self.items.items() if e <= now]:
                del self.items[k]; self.order.remove(k)
        def put(self, now, k, v, ttl):
            self.purge(now)
            if k in self.items:
                self.order.remove(k)
            self.items[k] = (v, now + ttl); self.order.append(k)
            while len(self.items) > self.cap:
                del self.items[self.order.pop(0)]
        def get(self, now, k):
            self.purge(now)
            if k not in self.items:
                return None
            self.order.remove(k); self.order.append(k)
            return self.items[k][0]
        def delete(self, now, k):
            self.purge(now)
            if k not in self.items:
                return False
            del self.items[k]; self.order.remove(k)
            return True
        def stats(self, now):
            self.purge(now)
            vals = [v for v, _ in self.items.values()]
            return len(vals), (sum(vals) / len(vals) if vals else None)

    rnd = random.Random(8)
    for _ in range(300):
        clk, cap = FakeClock(), rnd.randint(1, 5)
        c, m = TTLCache(capacity=cap, clock=clk), Model(cap)
        for _ in range(80):
            op, k = rnd.random(), rnd.randint(0, 7)
            if op < .4:
                v, ttl = rnd.randint(-5, 50), rnd.randint(1, 8)
                c.put(k, v, ttl); m.put(clk.t, k, v, ttl)
            elif op < .65:
                assert c.get(k) == m.get(clk.t, k)
            elif op < .75:
                assert c.delete(k) == m.delete(clk.t, k)
            else:
                clk.advance(rnd.randint(0, 3))
            assert (len(c), c.average()) == m.stats(clk.t)


def test_sliding_window_matches_ttl_cache():
    rnd = random.Random(2)
    clk = FakeClock()
    w, c = SlidingWindowAverage(5, clk), TTLCache(default_ttl=5, clock=clk)
    for i in range(500):
        clk.advance(rnd.randint(0, 2))
        if rnd.random() < .6:
            v = rnd.randint(0, 100)
            w.add(v); c.put(i, v)                     # distinct keys, same TTL
        assert w.average() == c.average()


def test_threads():
    for cache in (ThreadSafeTTLCache(default_ttl=1e9), ShardedTTLCache(shards=8, default_ttl=1e9)):
        def worker(tid):
            for i in range(500):
                cache.put((tid, i), 1)
                assert cache.get((tid, i)) == 1
        ts = [threading.Thread(target=worker, args=(t,)) for t in range(8)]
        stop, errs = threading.Event(), []

        def averager():                               # runs concurrently: must never deadlock or crash
            while not stop.is_set():
                avg = cache.average()
                if avg is not None and avg != 1:
                    errs.append(avg)
        a = threading.Thread(target=averager)
        a.start()
        for t in ts:
            t.start()
        for t in ts:
            t.join(30)
        stop.set(); a.join(10)
        assert not a.is_alive() and not any(t.is_alive() for t in ts) and not errs
        assert cache.average() == 1
    sharded = ShardedTTLCache(shards=8, default_ttl=1e9)
    for i in range(1000):
        sharded.put(i, 2)
    assert sharded.average(exact=True) == sharded.average(exact=False) == 2
    assert sum(len(s) for s in sharded._shards) == 1000


if __name__ == "__main__":
    test_ttl_basics()
    test_lru_eviction_and_sum()
    test_random_against_model()
    test_sliding_window_matches_ttl_cache()
    test_threads()
    print("ttlcache OK")
```

**Follow-ups to expect**

- *"`average()` must also be correct if the clock is slow or items expire between calls."* Yes: we purge on every call; mention that expiry is evaluated lazily on read, never in the background.
- *"Memory leak for keys never read again."* Purge also runs on every `put`; add an optional reaper thread that calls `_purge` periodically (taking the lock).
- *"Cache stampede / thundering herd on a hot key."* Single-flight loading (see the `LRUCache.get_or_load` in the companion guide) plus **jittered TTLs** so keys don't expire together.
- *"Per-item TTL refresh on read (sliding expiration)."* On `get`, push a new heap entry with a new `seq`; the old entry is now stale and is dropped lazily.
- *"Distributed version."* Consistent hashing across nodes (Q8), replicate hot keys, TTL via the store (Redis `EXPIRE`), and note that clocks differ per node, so prefer relative TTLs.
- *"Median / percentile of the valid items instead of the average."* A running sum no longer works. Two heaps with lazy deletion, or an order-statistic tree; expiry removal is the hard part.

---

## Q4. Time-windowed map and hit counter (reported theme, spec unknown)

> The PracHub guide mentions "a time-windowed map" without a spec. The two standard readings are: a **time-versioned map** (`get(key, t)` returns the value as of time `t`; LeetCode 981 "Time Based Key-Value Store") and a **rolling counter** ("hits in the last N seconds"; LeetCode 362 "Design Hit Counter"). Clarify which one, or do both quickly.

**TimeMap design:** per key keep two parallel lists (timestamps ascending, values). `set` appends (or inserts with `bisect` if timestamps can arrive out of order); `get` does `bisect_right(ts, t) - 1`: O(log n). **Concurrency:** a lock per map suffices; appends are cheap. Because values are immutable once written, readers could read snapshots if you copy-on-write per key.

**HitCounter design:** a ring of `window` one-second buckets. Each bucket stores *which second it currently represents* plus a count. A hit resets the bucket if it holds an older second. `count()` sums buckets whose second is within the window. O(1) update and O(window) read with fixed memory, regardless of traffic. (A deque of timestamps is O(hits) memory.) **Concurrency:** one lock; or per-bucket atomics/`LongAdder` in Java.

```python
# file: timemap.py
import bisect
import threading
import time
from collections import defaultdict


class TimeMap:
    def __init__(self):
        self._ts, self._vals = defaultdict(list), defaultdict(list)
        self._lock = threading.Lock()

    def set(self, key, value, timestamp):
        with self._lock:
            ts = self._ts[key]
            i = bisect.bisect_right(ts, timestamp)         # append in the common case; insert if out of order
            ts.insert(i, timestamp)
            self._vals[key].insert(i, value)

    def get(self, key, timestamp):
        """Value with the largest timestamp <= `timestamp`, else None."""
        with self._lock:
            ts = self._ts.get(key)
            if not ts:
                return None
            i = bisect.bisect_right(ts, timestamp)
            return self._vals[key][i - 1] if i else None


class HitCounter:
    """Hits in the last `window` seconds with fixed memory: one bucket per second, reused in a ring."""

    def __init__(self, window=300, clock=time.time):
        self._w, self._clock = window, clock
        self._second, self._hits = [None] * window, [0] * window
        self._lock = threading.Lock()

    def hit(self):
        t = int(self._clock())
        i = t % self._w
        with self._lock:
            if self._second[i] != t:                       # bucket still holds an old second: reset it
                self._second[i], self._hits[i] = t, 0
            self._hits[i] += 1

    def count(self):
        t = int(self._clock())
        with self._lock:
            return sum(h for s, h in zip(self._second, self._hits) if s is not None and t - s < self._w)


def test_timemap_and_hits():
    tm = TimeMap()
    tm.set("k", "v1", 1); tm.set("k", "v3", 3); tm.set("k", "v2", 2)      # out-of-order insert
    assert tm.get("k", 0) is None and tm.get("k", 1) == "v1" and tm.get("k", 2) == "v2"
    assert tm.get("k", 99) == "v3" and tm.get("nope", 5) is None
    tm.set("k", "v3b", 3)
    assert tm.get("k", 3) == "v3b"                                       # later write at the same timestamp wins

    now = [0]
    hc = HitCounter(window=300, clock=lambda: now[0])
    for t in (1, 1, 2, 300):
        now[0] = t; hc.hit()
    assert hc.count() == 4
    now[0] = 301; assert hc.count() == 2                                 # second 1 left the window
    now[0] = 302; assert hc.count() == 1
    now[0] = 301; hc.hit()                                               # bucket 1 is reused: old second 1 is reset
    assert hc.count() == 3
    now[0] = 1000; assert hc.count() == 0
    now[0] = 5
    hc2 = HitCounter(window=10, clock=lambda: now[0])
    ts = [threading.Thread(target=lambda: [hc2.hit() for _ in range(500)]) for _ in range(8)]
    for t in ts: t.start()
    for t in ts: t.join()
    assert hc2.count() == 4000                                           # no lost updates


if __name__ == "__main__":
    test_timemap_and_hits()
    print("timemap OK")
```

---

## Q5. Sudoku: validate in one traversal, then solve (reported)

> *Given a **filled** board, validate whether it is solved, **optimizing the number of traversals (one pass)**; add tests and make them pass. Extension: given an unsolved board, solve it (backtracking; reportedly not required to implement).*

**Approach and why (validate):** three arrays of 9 **bitmasks** (rows, columns, 3x3 boxes). For each cell with value `v`, test bit `v` in the three masks; if set, it's a duplicate; otherwise set it in all three. One pass, O(81) = O(1) time, O(1) extra memory, no sets or per-unit re-scans. The box index is `(r // 3) * 3 + c // 3`. For a **complete** board you also require every cell to be an integer in `1..9` (reject `0`, `10`, `None`, strings, `True`); then "no duplicates in any row, column or box" implies "each unit contains 1 to 9 exactly once" by pigeonhole.

**Clarify:** blanks represented as `0`, `.` or `None`? Is "valid" (no conflicts yet, blanks allowed, like LeetCode 36) or "solved" (complete) wanted? Board always 9x9? (I validate shape too.) Mention both and implement both with one helper.

**Approach (solve):** backtracking with the same bitmasks, plus the **MRV heuristic** (pick the empty cell with the fewest candidates, ie "most constrained first"). It prunes the search enormously: ordinary puzzles are solved with very little backtracking; even a famously hard one finishes quickly. Checks done up front: givens must not already conflict (otherwise return `False`). Complexity: worst case exponential, but 9^(empties) is irrelevant in practice with constraint propagation. Mention **Dancing Links (Algorithm X)** as the exact-cover formulation, and **uniqueness checking** (count solutions up to 2).

**Concurrency angle:** the board is tiny and validation is O(1): not interesting to parallelize. If asked: validating *many* boards is embarrassingly parallel (thread/process pool, no shared state); for a solver, split the first branching cell's candidates across workers (each with its own copy of the board and masks: no sharing) and cancel the others when one finds a solution.

```python
# file: sudoku.py
def _unit_ok(board, allow_blank):
    if len(board) != 9 or any(len(row) != 9 for row in board):
        return False
    rows, cols, boxes = [0] * 9, [0] * 9, [0] * 9           # bit v set <=> value v already seen in that unit
    for r in range(9):
        for c in range(9):                                  # ONE traversal of the 81 cells
            v = board[r][c]
            if allow_blank and v == 0:
                continue
            if type(v) is not int or not 1 <= v <= 9:       # type(...) is int also rejects True/False
                return False
            bit, b = 1 << v, (r // 3) * 3 + c // 3
            if (rows[r] | cols[c] | boxes[b]) & bit:        # duplicate in row, column or box
                return False
            rows[r] |= bit
            cols[c] |= bit
            boxes[b] |= bit
    return True


def is_solved(board):
    """Complete board (all 81 cells in 1..9) with no duplicate in any row, column or 3x3 box."""
    return _unit_ok(board, allow_blank=False)


def is_valid_partial(board):
    """Blanks (0) allowed; no conflicts among the given digits (LeetCode 36 semantics)."""
    return _unit_ok(board, allow_blank=True)


def solve(board):
    """Solve in place by backtracking + MRV. Returns False if the givens conflict or no solution exists."""
    rows, cols, boxes, empties = [0] * 9, [0] * 9, [0] * 9, []
    for r in range(9):
        for c in range(9):
            v = board[r][c]
            if v == 0:
                empties.append((r, c))
                continue
            bit, b = 1 << v, (r // 3) * 3 + c // 3
            if (rows[r] | cols[c] | boxes[b]) & bit:
                return False                                # the givens already conflict
            rows[r] |= bit; cols[c] |= bit; boxes[b] |= bit

    def search(remaining):
        if not remaining:
            return True
        best_i, best = -1, None
        for i, (r, c) in enumerate(remaining):              # MRV: the most constrained empty cell first
            used = rows[r] | cols[c] | boxes[(r // 3) * 3 + c // 3]
            cand = [v for v in range(1, 10) if not used >> v & 1]
            if best is None or len(cand) < len(best):
                best_i, best = i, cand
                if len(cand) <= 1:
                    break                                   # a forced move (or a dead end) can't be beaten
        if not best:
            return False                                    # an empty cell with no candidate: backtrack
        r, c = remaining[best_i]
        rest = remaining[:best_i] + remaining[best_i + 1:]
        b = (r // 3) * 3 + c // 3
        for v in best:
            bit = 1 << v
            rows[r] |= bit; cols[c] |= bit; boxes[b] |= bit; board[r][c] = v
            if search(rest):
                return True
            rows[r] ^= bit; cols[c] ^= bit; boxes[b] ^= bit        # undo and try the next candidate
        board[r][c] = 0
        return False

    return search(empties)
```

```python
# file: sudoku.py
import copy
import random


def _grid():
    return [[(r * 3 + r // 3 + c) % 9 + 1 for c in range(9)] for r in range(9)]   # a known valid solution


def test_validate():
    g = _grid()
    assert is_solved(g) and is_valid_partial(g)
    bad = copy.deepcopy(g); bad[0][0], bad[0][1] = bad[0][1], bad[0][0]           # swap: columns now conflict
    assert not is_solved(bad)
    row_dup = copy.deepcopy(g); row_dup[4][8] = row_dup[4][0]
    assert not is_solved(row_dup)
    zero = copy.deepcopy(g); zero[3][3] = 0
    assert not is_solved(zero) and is_valid_partial(zero)                          # incomplete but conflict-free
    for v in (10, -1, None, "5", True):
        weird = copy.deepcopy(g); weird[2][2] = v
        assert not is_solved(weird)
    # a duplicate that only the 3x3 box rule catches (row and column are fine)
    box = [[0] * 9 for _ in range(9)]
    box[0][0], box[1][1] = 5, 5
    assert not is_valid_partial(box)
    assert not is_solved(g[:8]) and not is_solved([row[:8] for row in g])


def test_solver():
    rnd = random.Random(3)
    sol = _grid()
    for _ in range(5):
        puzzle = copy.deepcopy(sol)
        for r, c in rnd.sample([(r, c) for r in range(9) for c in range(9)], 50):
            puzzle[r][c] = 0
        givens = [(r, c, puzzle[r][c]) for r in range(9) for c in range(9) if puzzle[r][c]]
        assert solve(puzzle) and is_solved(puzzle)
        assert all(puzzle[r][c] == v for r, c, v in givens)                       # givens preserved
    hard = [[int(ch) if ch.isdigit() else 0 for ch in row] for row in (
        "8........", "..36.....", ".7..9.2..", ".5...7...", "....457..",
        "...1...3.", "..1....68", "..85...1.", ".9....4..")]
    assert solve(hard) and is_solved(hard)                                         # a famously hard puzzle
    conflict = [[0] * 9 for _ in range(9)]
    conflict[0][0] = conflict[0][5] = 5
    assert solve(conflict) is False                                                # conflicting givens
    dead = [[0] * 9 for _ in range(9)]
    dead[0][:8] = range(1, 9)
    dead[1][8] = 9                                                                 # cell (0,8) has no candidate
    assert solve(dead) is False


if __name__ == "__main__":
    test_validate()
    test_solver()
    print("sudoku OK")
```

---

## Q6. LFU cache in O(1) (predicted)

> *Like an LRU cache but evict the **least frequently used** item; ties broken by least recently used.* (LeetCode 460.)

**Design and why:** `key → value`, `key → frequency`, and `frequency → OrderedDict(keys)` (the OrderedDict keeps recency within a frequency), plus `min_freq`. On access, move the key from bucket `f` to `f+1`. If bucket `f` empties and `f == min_freq`, `min_freq` becomes `f+1`. Eviction pops the oldest key from `buckets[min_freq]`. A **new** key always has frequency 1, so `min_freq = 1` after an insert. All operations O(1). The classic bug: forgetting that `min_freq` must be updated when the min bucket empties.

**Concurrency angle:** every operation, including `get`, mutates frequency metadata, so a read-write lock does not help (same trap as LRU/TTL). One lock for correctness; shard for scale (approximate global LFU, as in Q3); production caches (Caffeine's W-TinyLFU) use a probabilistic frequency sketch and *buffer* access events so reads don't contend on the policy.

```python
# file: lfu.py
import threading
from collections import OrderedDict, defaultdict


class LFUCache:
    def __init__(self, capacity):
        self._cap = capacity
        self._vals, self._freq = {}, {}
        self._buckets = defaultdict(OrderedDict)    # freq -> keys in LRU -> MRU order
        self._min = 0
        self._lock = threading.Lock()               # get() mutates metadata, so every method takes it

    def _touch(self, key):
        f = self._freq[key]
        del self._buckets[f][key]
        if not self._buckets[f]:
            del self._buckets[f]
            if self._min == f:                      # the minimum bucket just emptied
                self._min = f + 1
        self._freq[key] = f + 1
        self._buckets[f + 1][key] = None

    def get(self, key, default=-1):
        with self._lock:
            if key not in self._vals:
                return default
            self._touch(key)
            return self._vals[key]

    def put(self, key, value):
        if self._cap <= 0:
            return
        with self._lock:
            if key in self._vals:
                self._vals[key] = value
                self._touch(key)
                return
            if len(self._vals) >= self._cap:
                victim, _ = self._buckets[self._min].popitem(last=False)   # LFU, then LRU among ties
                if not self._buckets[self._min]:
                    del self._buckets[self._min]
                del self._vals[victim], self._freq[victim]
            self._vals[key], self._freq[key] = value, 1
            self._buckets[1][key] = None
            self._min = 1                           # a brand-new key always has frequency 1
```

```python
# file: lfu.py
import random


def test_lfu_against_model():
    rnd = random.Random(6)
    for _ in range(300):
        cap = rnd.randint(1, 4)
        c, model, tick = LFUCache(cap), {}, 0          # model: key -> [value, freq, last_used_tick]
        for _ in range(120):
            tick += 1
            k = rnd.randint(0, 6)
            if rnd.random() < .5:
                got = c.get(k)
                if k in model:
                    model[k][1] += 1; model[k][2] = tick
                assert got == (model[k][0] if k in model else -1)
            else:
                v = rnd.randint(0, 99)
                c.put(k, v)
                if k in model:
                    model[k][0], model[k][1], model[k][2] = v, model[k][1] + 1, tick
                else:
                    if len(model) >= cap:
                        del model[min(model, key=lambda x: (model[x][1], model[x][2]))]   # lowest freq, then oldest
                    model[k] = [v, 1, tick]
    z = LFUCache(0); z.put(1, 1); assert z.get(1) == -1


def test_lfu_threads():
    c = LFUCache(50)
    def work(seed):
        rnd = random.Random(seed)
        for _ in range(2000):
            k = rnd.randint(0, 99)
            c.put(k, k) if rnd.random() < .5 else c.get(k)
    ts = [threading.Thread(target=work, args=(i,)) for i in range(8)]
    for t in ts: t.start()
    for t in ts: t.join(30)
    assert len(c._vals) <= 50 and set(c._vals) == set(c._freq)
    assert sum(len(b) for b in c._buckets.values()) == len(c._vals)       # structures agree (the invariant)


if __name__ == "__main__":
    test_lfu_against_model()
    test_lfu_threads()
    print("lfu OK")
```

---

## Q7. In-memory message broker with consumer groups (predicted, Kafka-flavoured)

> This is my extrapolation from Confluent's domain, **not** a reported question. *Implement a mini Kafka: topics with partitions, `produce(topic, key, value)`, consumer groups with `poll` and `commit`, rebalancing when members join or leave.* It exercises append-only logs, offsets, partitioning by key, delivery semantics and several concurrency patterns at once.

**Design and why**

- **Partition = append-only list.** An offset is just the index. `append` takes the partition's lock to assign `offset = len(log)` and append **atomically**, so concurrent producers never get the same offset and never leave gaps. Written records are **immutable**, and the log only grows, so readers can read a slice without locking (in Java you'd publish a volatile "high watermark" and let consumers read only below it; Kafka consumers also read only up to the high watermark).
- **Partitioning by key:** `crc32(key) % partitions`: a **stable** hash (Python's `hash()` of strings is salted per process), so all records with the same key land in one partition and are consumed **in order**. Ordering is guaranteed **per partition**, never globally. With no key: round-robin.
- **Consumer group:** each partition is consumed by **exactly one member** of a group at a time (`partition i → members[i % len(members)]`); different groups each get every record. State per group: members, assignment, **committed offsets** (durable progress) and each member's in-memory **fetch position**.
- **Delivery semantics:** `poll` advances the fetch position; only `commit` moves the committed offset. On rebalance (a member joins or leaves) positions reset to the committed offsets, so uncommitted records are **redelivered**: **at-least-once**. Commit *before* processing would give at-most-once; exactly-once needs idempotent processing or transactions (section 7).
- **Commit validation:** reject commits for partitions the member doesn't currently own (Kafka rejects stale-generation commits, otherwise a zombie consumer overwrites progress).
- **Blocking `poll(timeout)` without lost wake-ups:** a naive "check; if empty `wait()`" misses a record produced between the check and the wait. Use a **version counter**: read it *before* fetching; if nothing found, `wait_for(lambda: counter != seen)`. A produce between the check and the wait changes the counter, so the wait returns immediately.
- **Locks:** per-partition lock (appends), per-group lock (membership, positions, commits), one condition for wake-ups. A thread never holds the group lock while waiting on the condition.

```python
# file: broker.py
import itertools
import threading
import time
import zlib
from collections import namedtuple

Record = namedtuple("Record", "partition offset key value")


class NotAssignedError(Exception):
    pass


class _Partition:
    def __init__(self, index):
        self.index, self._log, self._lock = index, [], threading.Lock()

    def append(self, key, value):
        with self._lock:                                   # offset assignment + append: one atomic step
            offset = len(self._log)
            self._log.append(Record(self.index, offset, key, value))
            return offset

    def read(self, offset, max_records):
        return self._log[offset:offset + max_records]      # immutable records, log only grows: no lock needed


class _Group:
    def __init__(self, topic):
        self.topic, self.lock = topic, threading.Lock()
        self.members, self.assignment = [], {}             # member -> [partitions]
        self.committed, self.position = {}, {}             # partition -> next offset | (member, partition) -> next offset


class Broker:
    def __init__(self):
        self._topics, self._groups = {}, {}
        self._admin = threading.Lock()                     # topic / group creation only
        self._news = threading.Condition()
        self._produced = 0                                 # version counter: avoids lost wake-ups
        self._round_robin = itertools.count()

    # ---- producing ----
    def create_topic(self, name, partitions):
        with self._admin:
            if name in self._topics:
                raise ValueError(f"topic {name!r} exists")
            self._topics[name] = [_Partition(i) for i in range(partitions)]

    def produce(self, topic, value, key=None):
        parts = self._topics[topic]
        h = zlib.crc32(str(key).encode()) if key is not None else next(self._round_robin)   # stable hash
        p = h % len(parts)
        offset = parts[p].append(key, value)
        with self._news:
            self._produced += 1
            self._news.notify_all()                        # wake blocked consumers
        return p, offset

    # ---- consumer groups ----
    def join(self, group, topic, member):
        with self._admin:
            g = self._groups.setdefault(group, _Group(topic))
        if g.topic != topic:
            raise ValueError("a group consumes one topic")
        with g.lock:
            if member not in g.members:
                g.members.append(member)
                self._rebalance(g)

    def leave(self, group, member):
        g = self._groups[group]
        with g.lock:
            if member in g.members:
                g.members.remove(member)
                self._rebalance(g)

    def _rebalance(self, g):
        n = len(self._topics[g.topic])
        g.assignment = {m: [] for m in g.members}
        for p in range(n):
            if g.members:
                g.assignment[g.members[p % len(g.members)]].append(p)
        # restart every member at the last COMMITTED offset: uncommitted records are redelivered (at-least-once)
        g.position = {(m, p): g.committed.get(p, 0) for m, ps in g.assignment.items() for p in ps}

    def poll(self, group, member, max_records=10, timeout=0.0):
        g = self._groups[group]
        parts = self._topics[g.topic]
        deadline = time.monotonic() + timeout
        while True:
            with self._news:
                seen = self._produced                      # snapshot BEFORE looking, to avoid a lost wake-up
            with g.lock:
                if member not in g.assignment:
                    raise NotAssignedError(f"{member} is not in group {group}")
                out = []
                for p in g.assignment[member]:
                    if len(out) >= max_records:
                        break
                    pos = g.position[(member, p)]
                    recs = parts[p].read(pos, max_records - len(out))
                    g.position[(member, p)] = pos + len(recs)
                    out.extend(recs)
            if out:
                return out
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return []
            with self._news:                               # never wait while holding the group lock
                self._news.wait_for(lambda: self._produced != seen, remaining)

    def commit(self, group, member, partition, next_offset):
        g = self._groups[group]
        with g.lock:
            if partition not in g.assignment.get(member, ()):
                raise NotAssignedError(f"{member} does not own partition {partition}")   # stale / zombie consumer
            g.committed[partition] = max(g.committed.get(partition, 0), next_offset)

    def committed(self, group, partition):
        g = self._groups[group]
        with g.lock:
            return g.committed.get(partition, 0)

    def assignment(self, group, member):
        g = self._groups[group]
        with g.lock:
            return list(g.assignment.get(member, ()))
```

```python
# file: broker.py
def test_key_partitioning_and_order():
    b = Broker(); b.create_topic("t", 4)
    placed = {}
    for i in range(200):
        key = f"user-{i % 7}"
        p, off = b.produce("t", i, key=key)
        placed.setdefault(key, set()).add(p)
    assert all(len(ps) == 1 for ps in placed.values())          # a key always maps to one partition
    b.join("g", "t", "solo")
    got = []
    while recs := b.poll("g", "solo", 1000):
        got.extend(recs)
    by_partition = {}
    for r in got:
        by_partition.setdefault(r.partition, []).append(r.offset)
    assert len(got) == 200 and all(offs == list(range(len(offs))) for offs in by_partition.values())
    per_key = {}
    for r in got:
        per_key.setdefault(r.key, []).append(r.value)
    assert all(vals == sorted(vals) for vals in per_key.values())   # per-key order preserved


def test_concurrent_producers_get_unique_contiguous_offsets():
    b = Broker(); b.create_topic("t", 3)
    results, lock = [], threading.Lock()

    def produce(tid):
        local = [b.produce("t", (tid, i)) for i in range(250)]
        with lock:
            results.extend(local)
    ts = [threading.Thread(target=produce, args=(t,)) for t in range(8)]
    for t in ts: t.start()
    for t in ts: t.join(30)
    for p in range(3):
        offs = sorted(o for part, o in results if part == p)
        assert offs == list(range(len(offs)))                   # no duplicates, no gaps
    assert len(results) == 2000


def test_group_rebalance_at_least_once():
    b = Broker(); b.create_topic("t", 3)
    for i in range(30):
        b.produce("t", i)                                       # round-robin: 10 per partition
    b.join("g", "t", "m1")
    first = b.poll("g", "m1", 100)
    assert len(first) == 30
    b.commit("g", "m1", 0, 10)                                  # only partition 0 is committed
    b.join("g", "t", "m2")                                      # rebalance: positions reset to committed offsets
    again = b.poll("g", "m1", 100) + b.poll("g", "m2", 100)
    assert {r.partition for r in again} == {1, 2} and len(again) == 20     # p1, p2 redelivered; p0 is not
    owned = [set(b.assignment("g", m)) for m in ("m1", "m2")]
    assert owned[0].isdisjoint(owned[1]) and owned[0] | owned[1] == {0, 1, 2}
    other = "m2" if 0 in owned[0] else "m1"
    try:
        b.commit("g", other, 0, 99)                             # the non-owner must be rejected
        raise AssertionError("expected NotAssignedError")
    except NotAssignedError:
        pass
    b.join("other-group", "t", "x")                             # a different group reads everything again
    assert len(b.poll("other-group", "x", 100)) == 30
    b.leave("g", "m2")
    assert set(b.assignment("g", "m1")) == {0, 1, 2}


def test_blocking_poll_wakes_up():
    b = Broker(); b.create_topic("t", 2); b.join("g", "t", "m")
    assert b.poll("g", "m", 10, timeout=0.05) == []
    result = []
    t = threading.Thread(target=lambda: result.extend(b.poll("g", "m", 10, timeout=5)))
    t.start()
    time.sleep(0.1)
    start = time.monotonic()
    b.produce("t", "hello", key="k")
    t.join(5)
    assert [r.value for r in result] == ["hello"] and time.monotonic() - start < 1.0


if __name__ == "__main__":
    test_key_partitioning_and_order()
    test_concurrent_producers_get_unique_contiguous_offsets()
    test_group_rebalance_at_least_once()
    test_blocking_poll_wakes_up()
    print("broker OK")
```

**Follow-ups:** retention (delete or compact old segments; Q16 of the file-operations guide); replication and an in-sync-replica set with a leader per partition; **idempotent producer** (producer id + sequence number per partition, so retried sends aren't duplicated); transactions for exactly-once across partitions; **cooperative** rebalancing (don't stop the world); heartbeats and session timeouts to detect dead members; backpressure (bounded partitions, quotas); ordering with retries (`max.in.flight`).

---

## Q8. Consistent hashing ring (predicted)

> *Distribute keys across N cache/broker nodes so that adding or removing a node moves as few keys as possible.* (Used for partitioning caches, Kafka-like partition assignment, sharding.)

**Design and why:** plain `hash(key) % N` remaps almost **all** keys when `N` changes. Consistent hashing places nodes on a hash **ring**; a key belongs to the first node clockwise from the key's hash, so adding a node steals keys only from its successor (about `1/N` of the keys). Few physical points give uneven load, so each node gets **virtual nodes** (about 100 to 200 points on the ring); the load evens out as a smoothed average. Lookup: binary search (`bisect`) in the sorted array of points, O(log(N·v)). **Replication:** the next `r` **distinct** nodes clockwise.

**Concurrency angle:** lookups are hot and membership changes are rare, so use the **copy-on-write snapshot** from the ladder: membership changes rebuild immutable tuples and publish them with one assignment; `get_node` reads the snapshot reference once. No lock on the read path. (State the cost: a reader may route using slightly stale membership, which is fine for caches and handled by retries/rebalance in stores.)

```python
# file: ds.py
import bisect
import hashlib
import math
import threading


def _h64(s):
    return int.from_bytes(hashlib.md5(s.encode()).digest()[:8], "big")      # stable across processes


class HashRing:
    def __init__(self, nodes=(), vnodes=128):
        self._vnodes, self._nodes = vnodes, set(nodes)
        self._write_lock = threading.Lock()
        self._snapshot = ((), ())
        self._rebuild()

    def _rebuild(self):
        points = sorted((_h64(f"{n}#{i}"), n) for n in self._nodes for i in range(self._vnodes))
        self._snapshot = (tuple(h for h, _ in points), tuple(n for _, n in points))   # one atomic publish

    def add_node(self, node):
        with self._write_lock:
            self._nodes.add(node)
            self._rebuild()

    def remove_node(self, node):
        with self._write_lock:
            self._nodes.discard(node)
            self._rebuild()

    def get_node(self, key):
        hashes, owners = self._snapshot                    # read ONCE: an immutable, consistent view
        if not hashes:
            raise LookupError("no nodes")
        return owners[bisect.bisect_right(hashes, _h64(str(key))) % len(hashes)]

    def get_nodes(self, key, count):
        """`count` DISTINCT nodes clockwise from the key: primary first, then replicas."""
        hashes, owners = self._snapshot
        if not hashes:
            raise LookupError("no nodes")
        start, out, seen = bisect.bisect_right(hashes, _h64(str(key))), [], set()
        for step in range(len(hashes)):
            node = owners[(start + step) % len(hashes)]
            if node not in seen:
                seen.add(node)
                out.append(node)
                if len(out) == count:
                    break
        return out


class BloomFilter:
    """Set membership with no false negatives and a tunable false-positive rate."""

    def __init__(self, expected_items, fp_rate=0.01):
        self.m = max(8, math.ceil(-expected_items * math.log(fp_rate) / math.log(2) ** 2))   # bits
        self.k = max(1, round(self.m / expected_items * math.log(2)))                        # hash functions
        self._bits = bytearray((self.m + 7) // 8)
        self._lock = threading.Lock()

    def _positions(self, item):
        d = hashlib.sha256(str(item).encode()).digest()
        h1, h2 = int.from_bytes(d[:8], "big"), int.from_bytes(d[8:16], "big") | 1
        return [(h1 + i * h2) % self.m for i in range(self.k)]                              # double hashing

    def add(self, item):
        positions = self._positions(item)
        with self._lock:                       # |= on a shared byte is read-modify-write: without the lock two
            for p in positions:                # threads touching bits of the SAME byte can lose an update,
                self._bits[p >> 3] |= 1 << (p & 7)   # which creates a FALSE NEGATIVE

    def __contains__(self, item):              # reads one byte at a time: atomic, so no lock needed
        return all(self._bits[p >> 3] >> (p & 7) & 1 for p in self._positions(item))
```

---

## Q9. Bloom filter for stream dedup (predicted)

> *Remember which message ids you've already seen with far less memory than a set; tolerate a few false positives.* (Dedup in a stream consumer, "might this key exist in this SSTable?" in LSM stores.)

**Design and why:** a bit array of `m` bits and `k` hash functions; `add` sets `k` bits, `contains` checks all `k` are set. **No false negatives**, a false-positive probability of about `(1 - e^(-kn/m))^k`. Sizing for `n` expected items and target rate `p`: `m = -n ln p / (ln 2)^2` and `k = (m/n) ln 2` (about 9.6 bits per item for 1%). **Double hashing** (`h1 + i*h2`) derives all `k` positions from one digest. A deleted item cannot be removed (use a **counting** Bloom filter, or a cuckoo filter); a filter that fills up (more than `n` items) degrades silently, so scalable/partitioned Bloom filters rotate by time window for streams.

**Concurrency angle (a good trap):** `bits[i] |= mask` is a read-modify-write on a shared **byte**, not atomic. Two threads setting different bits **in the same byte** can overwrite each other, so one item's bit disappears and you get a **false negative**, which the structure promises never to produce. Fixes: a lock around `add` (as coded), a byte-per-bit array where each write is a plain store, or atomic OR (`AtomicLongArray`/CAS loop) in Java. Reads without a lock are fine: they can only miss an `add` that hasn't finished yet.

### Tests for Q8 and Q9

```python
# file: ds.py
import random


def test_hash_ring():
    nodes = [f"node-{i}" for i in range(5)]
    ring = HashRing(nodes, vnodes=200)
    keys = [f"key-{i}" for i in range(20000)]
    before = {k: ring.get_node(k) for k in keys}
    counts = {n: sum(1 for v in before.values() if v == n) for n in nodes}
    assert max(counts.values()) / min(counts.values()) < 1.6            # virtual nodes even out the load
    ring.add_node("node-5")
    after = {k: ring.get_node(k) for k in keys}
    moved = [k for k in keys if before[k] != after[k]]
    assert 0.08 < len(moved) / len(keys) < 0.28                          # about 1/6 of the keys move, not ~5/6
    assert all(after[k] == "node-5" for k in moved)                      # ...and only TO the new node
    ring.remove_node("node-2")
    final = {k: ring.get_node(k) for k in keys}
    assert all(final[k] == after[k] for k in keys if after[k] != "node-2")   # only node-2's keys moved
    replicas = ring.get_nodes("key-1", 3)
    assert len(replicas) == len(set(replicas)) == 3 and replicas[0] == ring.get_node("key-1")
    assert len(ring.get_nodes("key-1", 99)) == 5                         # fewer nodes than requested
    try:
        HashRing().get_node("k")
        raise AssertionError("expected LookupError")
    except LookupError:
        pass


def test_hash_ring_concurrent_membership_changes():
    ring, errors, stop = HashRing(["a", "b", "c"]), [], threading.Event()

    def reader():
        while not stop.is_set():
            n = ring.get_node("some-key")                                # must never raise or return None
            if n is None:
                errors.append(n)
    ts = [threading.Thread(target=reader) for _ in range(4)]
    for t in ts: t.start()
    for i in range(30):
        ring.add_node(f"x{i}"); ring.remove_node(f"x{i}")
    stop.set()
    for t in ts: t.join(10)
    assert not errors and not any(t.is_alive() for t in ts)


def test_bloom_filter():
    n = 5000
    bf = BloomFilter(n, 0.01)
    members = [f"id-{i}" for i in range(n)]
    for m in members:
        bf.add(m)
    assert all(m in bf for m in members)                                 # never a false negative
    fp = sum(1 for i in range(20000) if f"other-{i}" in bf) / 20000
    assert fp < 0.02, fp                                                 # target 1%, allow slack
    bf2 = BloomFilter(8 * 5000, 0.01)
    parts = [[f"t{t}-{i}" for i in range(5000)] for t in range(8)]
    ts = [threading.Thread(target=lambda p=p: [bf2.add(x) for x in p]) for p in parts]
    for t in ts: t.start()
    for t in ts: t.join(30)
    assert all(x in bf2 for p in parts for x in p)                       # concurrent adds lose no bits


if __name__ == "__main__":
    test_hash_ring()
    test_hash_ring_concurrent_membership_changes()
    test_bloom_filter()
    print("ds OK")
```

---

## Q10. Event-time windows with a watermark (predicted, Kafka-Streams-flavoured)

> *Count (or sum) events per key in fixed windows of **event time**; events arrive out of order. Emit each window once it is complete; drop events that are too late.* Variants: **hopping/sliding** windows (size 10, advance 5).

**Design and why**

- **Event time vs processing time:** events carry their own timestamp; arrival order is not time order. Windows are keyed by the event timestamp.
- **Window assignment:** tumbling (`slide == size`): `start = ts - ts % size`. Hopping: an event belongs to every window `[s, s+size)` with `s` a multiple of `slide` and `ts - size < s <= ts`, i.e. `size/slide` windows. Windows start at 0 or later.
- **Watermark** = `max event time seen - allowed_lateness`: "we assume nothing older than this will arrive". A window is **closed and emitted** when its end `<= watermark`. Events whose windows are all closed are **late**: dropped (and counted, so you can alert/side-output). The watermark only moves forward, so a closed window never reopens.
- **Ordered emission:** keep a min-heap of open window starts; all windows have the same size, so end order equals start order.
- **State bound:** memory is limited to the windows within `allowed_lateness + size` of the watermark.
- **`flush()`** at shutdown/end of input emits remaining windows (Kafka Streams has "emit on close" semantics too).

**Concurrency angle:** the scalable design is **confinement** (rung 7): partition the input by key, give each partition **one thread that owns its window state**, so no locks are needed (that is Kafka Streams' task model). A shared aggregator would need one lock around `add`, and the watermark logic (max over *all* threads' events) would become the bottleneck, which is a good argument to partition. With several input partitions per task, the watermark is the **minimum** across partitions, so one stalled partition holds back window closing (a known real-world problem: idleness timeouts).

```python
# file: windows.py
import heapq
from collections import defaultdict


class WindowedAggregator:
    """Sums values per key in event-time windows (tumbling if slide == size, hopping otherwise)."""

    def __init__(self, size, slide=None, allowed_lateness=0):
        self.size, self.slide, self.lateness = size, slide or size, allowed_lateness
        self._windows = {}          # window start -> {key: total}
        self._starts = []           # min-heap of open window starts (emission order)
        self._max_ts = None
        self.dropped = 0            # late events: expose as a metric / side output

    def add(self, ts, key, value=1):
        """Process one event. Returns the windows that CLOSED because of it: [(start, end, {key: total})]."""
        self._max_ts = ts if self._max_ts is None else max(self._max_ts, ts)
        watermark = self._max_ts - self.lateness
        accepted = False
        start = ts - ts % self.slide
        while start > ts - self.size and start >= 0:          # every window [start, start+size) containing ts
            if start + self.size > watermark:                 # window still open
                if start not in self._windows:
                    self._windows[start] = defaultdict(int)
                    heapq.heappush(self._starts, start)
                self._windows[start][key] += value
                accepted = True
            start -= self.slide
        if not accepted:
            self.dropped += 1                                 # every window for this event already closed
        return self._close(watermark)

    def _close(self, watermark):
        out = []
        while self._starts and self._starts[0] + self.size <= watermark:
            start = heapq.heappop(self._starts)
            out.append((start, start + self.size, dict(self._windows.pop(start))))
        return out

    def flush(self):
        out = []
        while self._starts:
            start = heapq.heappop(self._starts)
            out.append((start, start + self.size, dict(self._windows.pop(start))))
        return out
```

```python
# file: windows.py
import random


def test_tumbling_with_lateness():
    w = WindowedAggregator(size=10, allowed_lateness=5)
    assert w.add(1, "a") == [] and w.add(12, "a") == []         # watermark is now 7
    assert w.add(3, "b") == []                                   # out of order but within lateness: accepted
    assert w.add(20, "a") == [(0, 10, {"a": 1, "b": 1})]         # watermark 15 closes [0,10)
    assert w.add(4, "c") == [] and w.dropped == 1                # too late: its window is already closed
    assert w.flush() == [(10, 20, {"a": 1}), (20, 30, {"a": 1})]
    assert w.flush() == []


def test_hopping_windows():
    w = WindowedAggregator(size=10, slide=5)
    out = w.add(7, "x")                                          # belongs to [0,10) and [5,15)
    out += w.add(12, "x")                                        # belongs to [5,15) and [10,20); watermark 12 closes [0,10)
    assert out == [(0, 10, {"x": 1})]
    assert w.flush() == [(5, 15, {"x": 2}), (10, 20, {"x": 1})]


def test_matches_brute_force_when_nothing_is_late():
    rnd = random.Random(9)
    for _ in range(200):
        size = rnd.choice([5, 10])
        events = [(rnd.randint(0, 60), rnd.choice("ab")) for _ in range(rnd.randint(0, 40))]
        w = WindowedAggregator(size, allowed_lateness=10 ** 9)   # lateness so large that no event is dropped
        for ts, k in events:
            w.add(ts, k)
        want = defaultdict(lambda: defaultdict(int))
        for ts, k in events:
            want[ts - ts % size][k] += 1
        assert w.flush() == [(s, s + size, dict(want[s])) for s in sorted(want)] and w.dropped == 0


if __name__ == "__main__":
    test_tumbling_with_lateness()
    test_hopping_windows()
    test_matches_brute_force_when_nothing_is_late()
    print("windows OK")
```

---

## 7. Concurrency questions and answers (the discussion part)

The round description says to expect discussion of "concurrency impact on code". These are the questions to answer crisply.

| Question | Answer |
|---|---|
| **What is a race condition vs a data race?** | A *data race* is unsynchronized concurrent access to the same memory where at least one is a write (undefined/ill-defined in many languages). A *race condition* is any outcome that depends on timing, even with properly synchronized access (e.g. check-then-act: `if k not in d: d[k] = load(k)`). Locking individual operations does not remove race conditions across *multiple* operations. |
| **What do locks give you besides mutual exclusion?** | **Visibility** (a thread sees writes made before another thread released the same lock: the happens-before edge) and **ordering**. In Java this is why `volatile`/`synchronized` matter; Python's GIL hides most of this for pure-Python code, but you should still state it. |
| **What does the Python GIL change?** | Only one thread executes Python bytecode at a time, so single bytecodes (`list.append`, `dict[k]=v`) are effectively atomic, but `x += 1`, `d[k] += 1`, and check-then-act are *not*. CPU-bound threads gain no speed-up (use `multiprocessing`, or native extensions that release the GIL); I/O-bound threads do. Free-threaded (no-GIL) CPython builds exist as an opt-in; check the current status of your Python version, and note that code relying on the GIL for atomicity then breaks. |
| **Four conditions for deadlock, and how to avoid it?** | Mutual exclusion, hold-and-wait, no preemption, circular wait. Break one: **global lock ordering** (e.g. take shard locks by index, as in `ShardedTTLCache.average`), all-or-nothing acquisition, `acquire(timeout=...)` with back-off, or avoid nested locks by restructuring. |
| **Livelock, starvation, priority inversion?** | Livelock: threads keep reacting to each other without progress (fix with randomized back-off). Starvation: a thread never gets the lock/resource (fix with fair locks, writer preference in RW locks, FIFO tickets). Priority inversion: a low-priority holder blocks a high-priority waiter (priority inheritance). |
| **Condition variables: what are the rules?** | Always wait in a *loop* or with `wait_for(predicate)` (spurious wake-ups, stolen wake-ups); hold the lock when changing the predicate; `notify()` only if all waiters are interchangeable, otherwise `notify_all()`; avoid lost wake-ups with a state/version check *under the lock* (see `Broker.poll`). |
| **Lock granularity trade-offs?** | Coarse: simple, correct, a throughput ceiling. Fine-grained: more parallelism but invariants spanning structures get hard, deadlock risk grows. Striping/sharding: parallel for independent keys, cross-shard operations get approximate or need ordered locking. COW/immutable: lock-free reads, expensive writes. See the [ladder](#3-the-make-it-thread-safe-ladder). |
| **Why isn't an RW lock the fix for a cache?** | Because cache hits mutate the policy state (recency, frequency, expiry, stats). Real caches buffer access records and apply them under the lock in batches (Caffeine), or accept approximate policy per shard. |
| **What is a CAS, and the ABA problem?** | Compare-and-swap atomically sets a location only if it still holds the expected value, the basis of lock-free structures (`AtomicInteger`, `ConcurrentLinkedQueue`). ABA: the value changed A→B→A, so CAS succeeds although the structure changed (fix with version tags / hazard pointers / GC). Python has no CAS; use locks or `queue.Queue`. |
| **Contention and false sharing?** | Many threads hammering one counter or one cache line slows everything; shard the counter (`LongAdder`, per-thread counters summed on read) and pad hot fields apart. |
| **Producer-consumer: bounded or unbounded, and why?** | Always bounded unless you can prove otherwise: an unbounded queue turns a slow consumer into an out-of-memory crash. A bounded queue gives **backpressure**. Choose the policy: block, drop newest/oldest, or fail fast. |
| **How do you shut down cleanly?** | Close flag + `notify_all`, sentinel/poison pills per worker, `join` with timeouts, make blocked calls interruptible (timeouts), and don't swallow exceptions in workers. |
| **Which Java classes correspond to what you wrote?** | `ConcurrentHashMap` (CAS + per-bin locking; `computeIfAbsent` = single-flight), `CopyOnWriteArrayList` (COW), `ReentrantLock`/`Condition`, `ReentrantReadWriteLock`/`StampedLock`, `Semaphore`, `CountDownLatch`/`CyclicBarrier`, `BlockingQueue` family, `DelayQueue` and `ScheduledThreadPoolExecutor` (TTL expiry, delayed tasks), `AtomicLong`/`LongAdder`, `CompletableFuture`, and Caffeine for production caches. |
| **How would this change in a distributed system?** | There is no shared memory, so no locks: use **partitioning/ownership** (one owner per key via consistent hashing), **idempotent operations** with retries, **leases** with fencing tokens instead of locks (a crashed holder's lock must expire, and a stale holder must be rejected), and consensus (Raft/ZooKeeper-style, KRaft in Kafka) where agreement is needed. Clocks differ, so use relative TTLs and logical timestamps for ordering. |
| **Partial failure: what do you do when a loader or callback throws while holding state?** | Release locks via `with`/`finally`, don't cache failures (or cache them briefly on purpose), wake waiters so they retry, keep invariants true on every exit path, and test the exception path explicitly. |
| **How do you test concurrent code?** | Invariant checks after stress runs (counts, sums, uniqueness of offsets); randomized yields (`time.sleep(0)`) to widen interleavings; timeouts on every `join` to detect deadlock; deterministic fake clocks for time logic; model-based tests against a simple sequential reference (as done above); in Java, jcstress/ThreadSanitizer-style tools. |

---

## 8. Systems design discussion for senior candidates

Reported design questions for Confluent loops: **TinyURL** (the candidate was told to optimize for high-volume reads and not overcomplicate) and a **Spotify-like podcast API**. Given the company, a **Kafka-like log** is also plausible (predicted). Outlines of what to cover:

**TinyURL (reported):** requirements and read/write ratio first (reads dominate: say 100:1); short code generation (counter + base62, or a pre-generated key service; avoid hashing collisions or handle them); storage as a key-value (`short → long`), **range or hash sharding on the short key**, read replicas, a cache in front (hot keys, CDN/edge); 301 vs 302 (analytics vs cacheability); expiry, abuse/malware, rate limits; back-of-envelope: e.g. 100M new URLs/month, 7 characters of base62 = 3.5 trillion codes. Resist over-engineering: a stateless service layer, a sharded store, and a cache is the answer.

**Spotify-like podcast API (reported):** APIs to fetch *X* channels at a time and *X* clips per channel; **pagination** (offset/limit is simple but slow and unstable under inserts; **cursor/skip-token** pagination is stable and efficient: encode the last seen sort key); API **versioning** (URL or header), response shapes and limits; schema (users, subscriptions, channels, clips); corner cases the interviewer named: users with a huge number of subscriptions, channels with a huge number of clips (always paginate both levels; fan-out reads; per-user "feed" precomputation vs on-read join); estimates (users to channels to clips per channel) to size storage and QPS; caching of hot channels.

**Kafka-like distributed log (predicted):**
- **Partitioned, replicated, append-only log**; each partition has a **leader** and followers; **in-sync replicas (ISR)**; a record is *committed* when all ISR members have it (the high watermark); a producer `acks=all` waits for that.
- **Ordering** only within a partition; keying chooses the partition; **consumer groups** give parallelism and load-sharing; offsets stored in an internal topic.
- **Delivery semantics:** at-most-once, at-least-once (commit after processing), exactly-once (idempotent producer with sequence numbers + transactions + `read_committed`).
- **Storage:** segment files, sparse offset/time indexes, sequential I/O, page cache, zero-copy `sendfile`; retention by time/size; **log compaction** (keep the latest value per key; tombstones delete) as in the file-operations guide Q16.
- **Failure handling:** leader election from the ISR, controller (KRaft/Raft), rebalances, backpressure, quotas.

**Distributed rate limiter / cache with TTL (predicted):** per-key counters in a shared store with atomic increments and expiry (or token bucket per key stored with last-refill time), sticky routing by consistent hashing to avoid cross-node coordination, local approximate limits plus periodic sync, failure mode (fail open vs closed), clock skew handled by using the store's clock.

**How to present:** state requirements and numbers, draw the happy path, identify the **bottleneck and the failure modes**, pick consistency vs availability explicitly, and say what you would **not** build (and why).

---

## 9. Sources

**Confluent interview reports** (I viewed snippets or excerpts; confirm details on the pages):
- LeetCode Discuss, "Confluent | Senior Software Engineer | Phone interview" (function library with variadic arguments): <https://leetcode.com/discuss/interview-question/759611/confluent-senior-software-engineer-phone-interview>
- LeetCode Discuss, "Confluent | Senior/Staff Software Engineer Experience" (windowed average with expiring cache, Sudoku validation in one traversal, document phrase search, TinyURL, podcast API design): <https://leetcode.com/discuss/post/4188001/confluent-seniorstaff-software-engineer-5219u/>
- TechPrep, "Confluent's Interview Process" (LRU cache with TTL, Sudoku solver, function signature matcher, last N lines; thread-safety and partial-failure follow-ups): <https://www.techprep.app/blog/confluent-interview-process>
- PracHub, "Confluent Software Engineer interview questions guide 2026" (thread-safe LRU or time-windowed map; a session on concurrent data structures): <https://prachub.com/interview-guide/confluent-software-engineer-interview-questions-guide-2026>
- Glassdoor, Confluent Software Engineer interview review (take-home implementing a multi-threaded data structure; revise locks and condition variables): <https://fr.glassdoor.ch/Entretien/Confluent-Entretien-E1048428-RVW17579904.htm>
- techinterview.org, "How Confluent interviews engineers, round by round" (round format; "thread-safe without a single global lock"). A blog with unknown provenance, so treat as unconfirmed: <https://www.techinterview.org/post/3233476180/confluent-engineering-interview-rounds/>
- PracHub, a similar zero-or-more variadic signature question reported for another company: <https://prachub.com/interview-experiences/ibm-software-engineer-interview-experience-coding-phone-screen-on-an-ide-function-signature-matcher>

**Problem references used as bases** (names/numbers from memory, not re-opened): LeetCode 460 LFU Cache, 981 Time Based Key-Value Store, 362 Design Hit Counter, 36 Valid Sudoku, 37 Sudoku Solver.

**Background references** (concepts, from memory): *Designing Data-Intensive Applications* (partitioning, replication, stream processing, event time and watermarks); the Apache Kafka documentation (partitions, consumer groups, ISR, idempotent producer, log compaction); *Java Concurrency in Practice* (lock granularity, visibility, happens-before); the Python documentation for `threading`, `queue`, `heapq`, `bisect` and `collections.OrderedDict`; the Caffeine cache design notes (W-TinyLFU, buffered policy updates).

**What is predicted, not reported:** Q6 to Q10, the systems-design outlines for a Kafka-like log and distributed rate limiter, and the specific concurrency follow-ups beyond what the reports list. The shape (a data-structure problem, then "make it thread-safe", then partial failure and design) matches what the reports describe.
