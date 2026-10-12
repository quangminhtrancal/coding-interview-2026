# Python Concurrency & KV-Store Interview Guide

Everything in this file is Python 3 (standard library only). Each problem has: **the question and where it comes from, the design and why, the code, and the follow-ups to expect.** All code blocks are runnable and each section ends with tests.

> **Why threads still need locks in Python.** The GIL makes individual bytecodes atomic, but `x += 1`, "check then act" (`if k not in d: d[k] = ...`) and "wait then take" are *not* atomic. Interviewers expect you to write as if threads were truly parallel. Also, the GIL does nothing about **deadlock**, **lost wake-ups** or **ordering**, which is what most of these questions test.

## Contents

1. [Concurrency toolbox](#0-concurrency-toolbox)
2. [Key-value store with transactions](#1-key-value-store-with-transactions) (nested, conflict detection on commit, multi-threaded)
3. [Resource pool: get/put, then priority](#2-resource-pool-getput-then-priority)
4. [Classic concurrency questions](#3-classic-concurrency-questions) (bounded queue, print-in-order, FooBar, Zero-Even-Odd, H2O, FizzBuzz, dining philosophers, web crawler)
5. [Systems-style concurrency questions](#4-systems-style-concurrency-questions) (rate limiter, thread-safe LRU, readers-writer lock, thread pool, delayed scheduler)
6. [Rules of thumb](#5-rules-of-thumb-for-the-interview)
7. [Sources](#6-sources)

---

## 0. Concurrency toolbox

| Tool | Use it when | Watch out for |
|---|---|---|
| `Lock` / `RLock` | Protect one invariant (a data structure) | Keep critical sections short; `RLock` only if you truly re-enter |
| `Condition` | "Wait until predicate is true" (pool has m free, queue not empty) | Always wait in a loop / `wait_for(pred)`; use `notify_all` when waiters have *different* predicates |
| `Semaphore` | Count permits, or hand a baton between threads (FooBar, Zero-Even-Odd) | Release exactly as many times as you acquire |
| `Event` | One-shot "this happened" signal (Print in Order) | Not reusable without `clear()` |
| `Barrier` | N threads must meet before any continues (H2O) | A broken barrier raises in everyone |
| `queue.Queue` | Hand-off between producers and consumers; already thread-safe | Don't wrap it in another lock "for safety" |
| `ThreadPoolExecutor` | Bounded parallelism for independent tasks | Keep shared state confined to the coordinating thread when you can |

**The canonical blocking pattern** (used everywhere below):

```python
with cv:                                   # 1. take the lock
    cv.wait_for(lambda: predicate())       # 2. sleeps AND releases the lock, re-checks on wake
    mutate_state()                         # 3. predicate is guaranteed true here
    cv.notify_all()                        # 4. tell others the state changed
```

---

## 1. Key-value store with transactions

### 1.1 The questions and where they come from

| # | Question | Source |
|---|---|---|
| A | Key-value store with `begin / commit / rollback`, nested transactions, `delete` reversible by rollback, O(1) average per operation | Rippling phone screen report and Bloomberg onsite report (both links supplied in your notes, see [Sources](#6-sources)); also the "more advanced questions" text in your notes |
| B | Two interleaved transactions; **the second one fails on commit** because the first committed a conflicting write (your whiteboard: T1 reads k1,k2, writes k3; T2 reads k2, writes k3, reads k4; T2's commit fails) | Your whiteboard notes (no public source attached) |
| C | Make it safe for multiple threads; state your guarantees (linearizability vs weaker) and synchronization approach | The "Follow-up 2: Concurrency" text in your notes |

### 1.2 Design decisions (and why)

**A. Nested transactions → one flat undo log + a stack of marks.**
- The data lives in a single dict, so `get`, `put`, `delete` are O(1) with no layer lookups. (The "stack of overlay dicts" approach from the Rippling post is also valid, but `get` becomes O(depth) and `commit` has to merge dicts, which breaks the "O(1) per operation" requirement.)
- Every write inside a transaction appends `(key, old_value)` to the undo log. `begin()` records the current log length as a *mark*.
- `rollback()` pops entries back to the last mark and restores them. `commit()` of a nested transaction just pops the mark: its undo entries are now simply part of the parent's, so a later parent rollback also undoes the child's committed work, which is exactly the required semantics.
- A **sentinel** (`_MISSING`) distinguishes "key did not exist" from "value was `None`". Deleting inside a transaction is just another recorded write, so rollback brings the key back. (In an overlay design you would need a tombstone for the same reason.)
- Complexity: `begin/commit/get/put/delete` O(1); `rollback` is O(writes undone) (unavoidable: you must undo them).

**B. Conflict detection on commit → optimistic concurrency control (OCC) on top of MVCC.**
- Your whiteboard says "single threaded", yet two transactions are open at once. That is *interleaving*, not parallelism, and locks would just make T2 block forever (single thread!). So transactions work optimistically: do everything on a private buffer, **validate at commit**.
- Each commit gets a monotonically increasing **commit timestamp**. Every key keeps a short version chain `[(commit_ts, value)]`. A transaction records `start_ts`, the latest commit it can see (its **snapshot**).
- **Reads** come from the snapshot (`bisect` on the chain), so a transaction never sees another transaction's later commits. **Writes** go to a private write buffer; `delete` writes a tombstone.
- **Commit validation, "first committer wins":** if any key in my write set has a version newer than my `start_ts`, someone else committed that key after I started, so I abort with `ConflictError`. That is exactly your whiteboard: T1 commits `k3`, then T2 (started earlier, also writing `k3`) fails.
- This is **snapshot isolation** (DDIA ch. 7). It prevents dirty reads, non-repeatable reads and lost updates, but allows **write skew** (T1 reads y writes x; T2 reads x writes y). `isolation="serializable"` also validates the **read set** (abort if anything I read was committed after I started), which closes write skew. It is stricter, but aborts more often. (It does not protect range/predicate reads: that needs predicate/gap tracking.)
- Rollback is trivial: throw the buffer away.

**C. Multi-threading → keep the transaction logic, add one lock around the shared parts, give each thread its own transaction.**
- Shared mutable state is only: the version chains, the clock, and the active-transaction table. A single `RLock` guards them. **Commit (validate + apply + bump clock) must be one critical section**, otherwise two transactions could both pass validation and both write.
- Each thread's transaction state (buffer, read set, nested frames) is private, so it needs no lock. That is why `Session` stores it in `threading.local()`.
- **Guarantee:** with the lock, operations on the store are linearizable (each takes effect atomically at a point inside its critical section). Transactions are snapshot-isolated (or serializable in strict mode), and a conflicting committer gets a retryable `ConflictError`. Callers retry the whole transaction.
- Why not one global lock held from `begin` to `commit`? It is trivially serializable and trivially correct, but it makes every transaction run one at a time and one slow transaction blocks everybody (and a thread that forgets to commit blocks the world). It is a fine *first answer* to say out loud before moving to OCC.
- Why not a lock per key (two-phase locking)? Higher concurrency, but you now need deadlock detection or lock ordering. OCC with a short commit critical section is simpler and wins when conflicts are rare.
- **Production caveats to mention:** garbage-collect versions older than the oldest active `start_ts`; reads under the lock could become lock-free with immutable version lists; write-ahead log for durability (DDIA ch. 3).

### 1.3 Code: nested transactions (single-threaded, Question A)

```python
# file: kv_nested.py
_MISSING = object()          # "key did not exist", distinct from a stored None


class NestedKV:
    """get/put/delete/begin/commit/rollback; nested transactions; O(1) per operation."""

    def __init__(self):
        self._data = {}
        self._undo = []      # flat undo log: (key, previous value or _MISSING)
        self._marks = []     # one entry per open transaction: len(self._undo) at begin()

    # ---- data operations ----
    def get(self, key, default=None):
        return self._data.get(key, default)

    def put(self, key, value):
        self._record(key)
        self._data[key] = value

    def delete(self, key):
        if key not in self._data:
            return False
        self._record(key)
        del self._data[key]
        return True

    # ---- transactions ----
    def begin(self):
        self._marks.append(len(self._undo))

    def commit(self):
        if not self._marks:
            return False                     # no active transaction
        self._marks.pop()                    # child's undo entries now belong to the parent
        if not self._marks:                  # outermost commit: nothing can be undone any more
            self._undo.clear()
        return True

    def rollback(self):
        if not self._marks:
            return False
        mark = self._marks.pop()
        while len(self._undo) > mark:        # undo newest-first
            key, old = self._undo.pop()
            if old is _MISSING:
                self._data.pop(key, None)
            else:
                self._data[key] = old
        return True

    def _record(self, key):
        if self._marks:                      # outside a transaction there is nothing to undo
            self._undo.append((key, self._data.get(key, _MISSING)))
```

```python
# file: kv_nested.py
# ---- tests ----
def test_nested():
    kv = NestedKV()
    kv.put("a", 1)
    kv.begin(); kv.put("a", 2); kv.put("b", 3)
    kv.begin(); kv.delete("a"); assert kv.get("a") is None
    assert kv.rollback() and kv.get("a") == 2          # delete is reversible
    kv.begin(); kv.put("c", 9); assert kv.commit()     # child commits into parent
    assert kv.get("c") == 9
    assert kv.rollback()                               # parent rollback undoes child's commit too
    assert (kv.get("a"), kv.get("b"), kv.get("c")) == (1, None, None)
    assert not kv.commit() and not kv.rollback()       # no active transaction
    kv.begin(); kv.put("x", None); assert kv.commit()  # None is a real value
    assert "x" in kv._data and kv.get("x", "d") is None
    print("kv_nested OK")


if __name__ == "__main__":
    test_nested()
```

*Note on your skeleton:* `txid` is a class attribute referenced as a bare name inside `__init__`, and `put`/`get`/`commit` have no bodies and `put` lacks `self`. The version below keeps your names (`Transaction`, `KV`, `put/get/commit`) and fixes that: transaction ids are minted by the store (`begin()`), not by the constructor.

### 1.4 Code: transactions with conflict detection on commit (Questions B and C)

```python
# file: kv_mvcc.py
import bisect
import threading

TOMBSTONE = object()                 # marks a deleted key in a write buffer / version chain


class ConflictError(Exception):
    """commit() lost to a transaction that committed a conflicting change first. Retry."""


class TransactionError(Exception):
    """Unknown or already finished transaction id."""


class Transaction:
    __slots__ = ("txid", "start_ts", "reads", "writes")

    def __init__(self, txid, start_ts):
        self.txid = txid
        self.start_ts = start_ts     # snapshot: sees commits with commit_ts <= start_ts
        self.reads = set()           # keys read from the snapshot (for serializable mode)
        self.writes = {}             # private write buffer: key -> value | TOMBSTONE


class KV:
    """MVCC store, optimistic commit-time validation.

    isolation="snapshot":     first committer wins on write-write conflicts.
    isolation="serializable": additionally aborts if anything the transaction read was
                              committed by someone else after it started (stops write skew).
    The single RLock makes every public method atomic; in a purely single-threaded program
    you can delete the `with self._lock:` lines and nothing else changes.
    """

    def __init__(self, isolation="snapshot"):
        assert isolation in ("snapshot", "serializable")
        self.isolation = isolation
        self._stamps = {}            # key -> [commit_ts, ...] ascending
        self._values = {}            # key -> [value | TOMBSTONE, ...] parallel to _stamps
        self._clock = 0              # timestamp of the latest commit
        self._next_txid = 1
        self._active = {}            # txid -> Transaction
        self._lock = threading.RLock()

    # ---- transaction lifecycle ----
    def begin(self):
        with self._lock:
            tx = Transaction(self._next_txid, self._clock)
            self._next_txid += 1
            self._active[tx.txid] = tx
            return tx.txid

    def get(self, txid, key, default=None):
        with self._lock:
            tx = self._tx(txid)
            if key in tx.writes:                         # read-your-own-writes
                value = tx.writes[key]
            else:
                tx.reads.add(key)
                value = self._read_at(key, tx.start_ts)  # snapshot read
            return default if value is TOMBSTONE else value

    def put(self, txid, key, value):
        with self._lock:
            self._tx(txid).writes[key] = value

    def delete(self, txid, key):
        with self._lock:
            self._tx(txid).writes[key] = TOMBSTONE

    def rollback(self, txid):
        with self._lock:
            self._tx(txid)
            del self._active[txid]                       # just drop the private buffer

    def commit(self, txid):
        with self._lock:                                 # validate + apply = ONE critical section
            tx = self._tx(txid)
            del self._active[txid]                       # finished whether it succeeds or not
            to_check = set(tx.writes)
            if self.isolation == "serializable":
                to_check |= tx.reads
            for key in to_check:
                stamps = self._stamps.get(key)
                if stamps and stamps[-1] > tx.start_ts:  # someone committed it after my snapshot
                    raise ConflictError(
                        f"tx {txid}: key {key!r} committed at ts={stamps[-1]} "
                        f"after tx started at ts={tx.start_ts}")
            if tx.writes:
                self._clock += 1
                for key, value in tx.writes.items():
                    self._stamps.setdefault(key, []).append(self._clock)
                    self._values.setdefault(key, []).append(value)
            return self._clock

    # ---- helpers ----
    def get_committed(self, key, default=None):
        """Latest committed value (auto-commit read)."""
        with self._lock:
            value = self._read_at(key, self._clock)
            return default if value is TOMBSTONE else value

    def _read_at(self, key, ts):
        stamps = self._stamps.get(key)
        if not stamps:
            return TOMBSTONE
        i = bisect.bisect_right(stamps, ts)              # newest version with commit_ts <= ts
        return self._values[key][i - 1] if i else TOMBSTONE

    def _tx(self, txid):
        try:
            return self._active[txid]
        except KeyError:
            raise TransactionError(f"transaction {txid} is not active") from None
```

### 1.5 Code: per-thread nested transactions on top of the MVCC store (Question C)

This gives the exact `begin / commit / rollback / get / put / delete` API from the question, safe for many threads. Each thread has its own transaction stack; the outermost `begin` opens an MVCC transaction and nested `begin`s are **savepoint buffers** in front of it.

```python
# file: kv_mvcc.py
class Session:
    """Nested-transaction API. State is per thread (threading.local); the store is shared."""

    def __init__(self, kv=None):
        self.kv = kv or KV()
        self._local = threading.local()

    def _st(self):
        st = self._local
        if not hasattr(st, "txid"):
            st.txid = None           # outermost MVCC transaction, or None if no transaction
            st.frames = []           # buffers for NESTED transactions (outermost writes live in the txn)
        return st

    # ---- transactions ----
    def begin(self):
        st = self._st()
        if st.txid is None:
            st.txid = self.kv.begin()
        else:
            st.frames.append({})

    def commit(self):
        st = self._st()
        if st.txid is None:
            return False
        if st.frames:                                    # nested commit: merge into the parent
            top = st.frames.pop()
            for key, value in top.items():
                if st.frames:
                    st.frames[-1][key] = value
                else:
                    self._apply(st.txid, key, value)
            return True
        txid, st.txid = st.txid, None
        self.kv.commit(txid)                             # may raise ConflictError; txn is already closed
        return True

    def rollback(self):
        st = self._st()
        if st.txid is None:
            return False
        if st.frames:
            st.frames.pop()
        else:
            txid, st.txid = st.txid, None
            self.kv.rollback(txid)
        return True

    # ---- data operations ----
    def get(self, key, default=None):
        st = self._st()
        if st.txid is None:
            return self.kv.get_committed(key, default)
        for frame in reversed(st.frames):                # innermost savepoint first
            if key in frame:
                value = frame[key]
                return default if value is TOMBSTONE else value
        return self.kv.get(st.txid, key, default)

    def put(self, key, value):
        self._write(key, value)

    def delete(self, key):
        self._write(key, TOMBSTONE)

    def _write(self, key, value):
        st = self._st()
        if st.txid is None:                              # auto-commit single write; retry on conflict
            while True:
                txid = self.kv.begin()
                self._apply(txid, key, value)
                try:
                    self.kv.commit(txid)
                    return
                except ConflictError:
                    continue
        elif st.frames:
            st.frames[-1][key] = value
        else:
            self._apply(st.txid, key, value)

    def _apply(self, txid, key, value):
        if value is TOMBSTONE:
            self.kv.delete(txid, key)
        else:
            self.kv.put(txid, key, value)
```

```python
# file: kv_mvcc.py
# ---- tests ----
import time


def test_whiteboard():
    kv = KV()
    t = kv.begin()
    for k in ("k1", "k2", "k4"):
        kv.put(t, k, k.upper())
    kv.commit(t)

    a, b = kv.begin(), kv.begin()                        # both start from the same snapshot
    kv.get(a, "k1"); kv.get(a, "k2"); kv.put(a, "k3", "V3")
    kv.get(b, "k2"); kv.put(b, "k3", "V4"); assert kv.get(b, "k4") == "K4"
    kv.commit(a)                                          # left side commits first
    assert kv.get(b, "k3") == "V4"                        # b still sees its own write
    try:
        kv.commit(b)
        raise AssertionError("expected ConflictError")
    except ConflictError:
        pass
    assert kv.get_committed("k3") == "V3"                 # b's write never became visible
    try:
        kv.put(b, "x", 1)
        raise AssertionError("expected TransactionError")
    except TransactionError:
        pass


def test_snapshot_reads_and_delete():
    kv = KV()
    t = kv.begin(); kv.put(t, "a", 1); kv.commit(t)
    reader = kv.begin()
    w = kv.begin(); kv.put(w, "a", 2); kv.commit(w)
    assert kv.get(reader, "a") == 1                       # repeatable read: sees old snapshot
    assert kv.get_committed("a") == 2
    d = kv.begin(); kv.delete(d, "a"); assert kv.get(d, "a") is None
    kv.rollback(d); assert kv.get_committed("a") == 2     # rollback reverses the delete
    d = kv.begin(); kv.delete(d, "a"); kv.commit(d); assert kv.get_committed("a") is None


def test_write_skew():
    for isolation, conflicts in (("snapshot", False), ("serializable", True)):
        kv = KV(isolation)
        t = kv.begin(); kv.put(t, "x", 1); kv.put(t, "y", 1); kv.commit(t)
        a, b = kv.begin(), kv.begin()
        kv.get(a, "y"); kv.put(a, "x", 0)
        kv.get(b, "x"); kv.put(b, "y", 0)
        kv.commit(a)
        try:
            kv.commit(b); got = False
        except ConflictError:
            got = True
        assert got == conflicts, isolation


def test_session_nested():
    s = Session()
    s.put("a", 1)
    s.begin(); s.put("a", 2)
    s.begin(); s.delete("a"); assert s.get("a") is None
    assert s.rollback() and s.get("a") == 2
    s.begin(); s.put("c", 3); assert s.commit() and s.get("c") == 3
    seen = []
    t = threading.Thread(target=lambda: seen.append((s.get("a"), s.get("c"))))
    t.start(); t.join()
    assert seen == [(1, None)]                            # other threads see only committed data
    assert s.rollback()
    assert (s.get("a"), s.get("c")) == (1, None)
    assert not s.commit() and not s.rollback()


def test_threads_no_lost_updates():
    s = Session(); s.put("n", 0)
    retries = []

    def worker():
        for _ in range(200):
            while True:
                s.begin()
                v = s.get("n")
                time.sleep(0.0002)                        # widen the race window on purpose
                s.put("n", v + 1)                         # read-modify-write
                try:
                    s.commit(); break
                except ConflictError:
                    retries.append(1)                     # lost the race: redo the whole transaction
    ts = [threading.Thread(target=worker) for _ in range(8)]
    for t in ts: t.start()
    for t in ts: t.join(60)
    assert all(not t.is_alive() for t in ts)
    assert s.get("n") == 1600, s.get("n")                 # no increment lost
    print("kv_mvcc OK (conflict retries:", len(retries), ")")


if __name__ == "__main__":
    test_whiteboard(); test_snapshot_reads_and_delete(); test_write_skew()
    test_session_nested(); test_threads_no_lost_updates()
```

### 1.6 Follow-ups to be ready for

- *"commit/rollback with no active transaction?"* Return `False` (done) or raise; say which and why.
- *"What if the thread dies mid-transaction?"* In OCC nothing is locked, so the abandoned buffer is garbage; just expire stale entries in `_active`.
- *"Why can't I just copy the dict on `begin`?"* O(n) per `begin`; the undo log / MVCC cost is proportional to what you *change*.
- *"Durability / crash recovery?"* Write-ahead log; replay committed transactions (DDIA ch. 3).
- *"Reads blocking writers?"* They don't: readers use snapshots (that is the point of MVCC).

---

## 2. Resource pool: get/put, then priority

### 2.1 The question and where it comes from

> *Given a pool of resources, implement `get` and `put` to manage *n* resources in a multi-threaded environment. Follow-up: `get` also takes a `priority` (unique; higher number = served first).*

This is from your own prep notes. No public source was attached to it, and I haven't been able to attribute it to a specific company. It is a variant of the classic **connection-pool / counting-semaphore** problem, and the follow-up is the classic **priority-ordered waiting** problem. Treat the source as "your notes".

### 2.2 Review of the code you pasted (what would break)

| # | Problem | Consequence | Fix |
|---|---|---|---|
| 1 | `self.count` is used but never defined (only a local `count` exists) | `AttributeError` on first `get`/`put` | Use a local counter, or a list comprehension |
| 2 | In `put`, the `while count < m` loop never increments a defined counter | Infinite loop / crash | Same as above |
| 3 | Two different locks: your `self.lock` and the `Condition()`'s own hidden lock. `self.cv.wait()` is called without holding the Condition's lock | `RuntimeError: cannot wait on un-acquired lock`. Even if it worked, sleeping while holding `self.lock` blocks every other thread forever | **One** `Condition`, used as both lock and signal |
| 4 | `put` waits while `qsize() >= n - m` | Wrong capacity check (a full pool should be `size + m > n`) | Validate instead: returning more than was lent out is a bug, not something to wait on |
| 5 | `put` calls `notify()` (wakes one thread) | The woken getter may need more than is free while another could proceed → lost wake-up / stall | `notify_all()` (waiters have different predicates) |
| 6 | `Queue` already has its own lock; wrapping it again is redundant and `Queue.get()` blocks if empty, hiding bugs | Confusing, nested locking | Plain `deque` under the one Condition |
| 7 | Priority version: the waiter pushes itself into the heap **after** the wait loop | The heap is empty while waiting, so nobody is ever eligible → everyone waits forever | Register in the heap **before** waiting, remove in `finally` |
| 8 | `max_heap[0] != priority` compares a *negated* heap entry to the raw priority | Condition never true | Compare like with like (`(-priority, ticket)`) |
| 9 | No timeout/cancellation | A cancelled waiter would block everyone behind it | Remove the waiter in `finally` and `notify_all()` |

### 2.3 Design (and why)

- **One `Condition`, one invariant.** The invariant is "free + checked-out = n, and nobody holds the same resource twice". Everything (the free list, the checked-out set, the waiter heap) is only touched under `with self._cv:`.
- **`get(m)` is all-or-nothing.** Taking resources one at a time while waiting for the rest is the classic way to **deadlock** (two threads each hold half of what they need). Wait until `m` are free, then take all `m` in the same critical section.
- **`wait_for(predicate)` instead of `if/wait`.** Wakeups can be spurious, and another thread can take the resources between your wake-up and your re-acquiring the lock. The predicate is re-checked every time.
- **`put` never blocks.** In a pool, `put` returns something that was lent out, so it can't overflow. Blocking `put`s only make sense for a *bounded queue* (section 3.1). We validate instead (`ValueError` if you return something you don't own or return it twice).
- **Priority = a heap of waiters, and only the head may take.** Each `get` registers `(-priority, ticket)` in a min-heap (negated, since `heapq` is a min-heap; the ticket gives FIFO among equal priorities if priorities ever repeat). A waiter proceeds only when it is the head *and* enough resources are free.
- **`notify_all` everywhere.** With priorities the *specific* waiter that may proceed is the head; `notify()` could wake the wrong thread and the right one would sleep through it.
- **Trade-off to say out loud:** strict priority gives **head-of-line blocking**: if the highest-priority request wants 5 and only 2 are free, lower-priority requests wanting 1 wait too. That prevents starving big requests, which is usually the point. The alternative is "skip the head if it can't be satisfied" (better utilization, but a large high-priority request can starve). Also mention **priority inversion/aging** if the interviewer pushes.

### 2.4 Code

```python
# file: resource_pool.py
import heapq
import itertools
import threading
from collections import deque


class ResourcePool:
    """n interchangeable resources. get(m) blocks until m are free; put returns them."""

    def __init__(self, resources):
        items = list(range(resources)) if isinstance(resources, int) else list(resources)
        self._n = len(items)
        self._free = deque(items)
        self._out = set()                    # checked-out resources (catches foreign / double returns)
        self._cv = threading.Condition()     # the ONLY lock

    def get(self, m=1, timeout=None):
        if not 1 <= m <= self._n:
            raise ValueError(f"m must be between 1 and {self._n}")   # would wait forever otherwise
        with self._cv:
            if not self._cv.wait_for(lambda: len(self._free) >= m, timeout):
                raise TimeoutError(f"could not get {m} resources")
            got = [self._free.popleft() for _ in range(m)]          # all-or-nothing
            self._out.update(got)
            return got

    def put(self, resources):
        resources = list(resources)
        with self._cv:
            returning = set(resources)
            if len(returning) != len(resources) or not returning <= self._out:
                raise ValueError("returning a resource that is not checked out (or twice)")
            self._out -= returning
            self._free.extend(resources)
            self._cv.notify_all()            # waiters want different amounts: wake them all


class PriorityResourcePool(ResourcePool):
    """Same, but waiting get() calls are served strictly by priority (higher number first)."""

    def __init__(self, resources):
        super().__init__(resources)
        self._waiters = []                   # min-heap of (-priority, ticket)
        self._tickets = itertools.count()    # FIFO tie-break if priorities are not unique

    def get(self, m=1, priority=0, timeout=None):
        if not 1 <= m <= self._n:
            raise ValueError(f"m must be between 1 and {self._n}")
        with self._cv:
            me = (-priority, next(self._tickets))
            heapq.heappush(self._waiters, me)                # register BEFORE waiting
            try:
                ok = self._cv.wait_for(
                    lambda: self._waiters[0] == me and len(self._free) >= m, timeout)
                if not ok:
                    raise TimeoutError(f"priority {priority}: could not get {m} resources")
                got = [self._free.popleft() for _ in range(m)]
                self._out.update(got)
                return got
            finally:
                self._leave(me)
                self._cv.notify_all()                        # a new head may now be eligible

    def _leave(self, me):
        if self._waiters[0] == me:
            heapq.heappop(self._waiters)
        else:                                                # timed out while not at the head
            self._waiters.remove(me)
            heapq.heapify(self._waiters)
```

```python
# file: resource_pool.py
# ---- tests ----
import random
import time


def run(*fns, timeout=30):
    errors = []

    def wrap(fn):
        def inner():
            try:
                fn()
            except BaseException as e:
                errors.append(e)
        return inner
    ts = [threading.Thread(target=wrap(f), daemon=True) for f in fns]
    for t in ts: t.start()
    for t in ts: t.join(timeout); assert not t.is_alive(), "deadlock?"
    if errors:
        raise errors[0]


def wait_until(pred, timeout=3.0):
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        if pred():
            return
        time.sleep(0.001)
    raise AssertionError("condition not reached")


def test_pool_stress():
    pool = ResourcePool(3)
    held, hl = set(), threading.Lock()

    def worker(seed):
        rnd = random.Random(seed)
        for _ in range(100):
            got = pool.get(rnd.randint(1, 3))
            with hl:
                assert not (held & set(got)), "resource handed out twice"
                held.update(got)
            time.sleep(0.0002)
            with hl:
                held.difference_update(got)
            pool.put(got)
    run(*[(lambda s=s: worker(s)) for s in range(8)])
    assert len(pool._free) == 3 and not pool._out


def test_pool_validation_and_timeout():
    pool = ResourcePool(2)
    got = pool.get(2)
    for bad in ([99], got + got):
        try:
            pool.put(bad); raise AssertionError("expected ValueError")
        except ValueError:
            pass
    try:
        pool.get(1, timeout=0.05); raise AssertionError("expected TimeoutError")
    except TimeoutError:
        pass
    pool.put(got)


def test_priority_order():
    pool = PriorityResourcePool(3)
    held = pool.get(3, priority=100)
    order, ol = [], threading.Lock()

    def waiter(p):
        pool.get(1, p)
        with ol:
            order.append(p)
    ts = [threading.Thread(target=waiter, args=(p,), daemon=True) for p in (1, 10, 5)]
    for t in ts: t.start()
    wait_until(lambda: len(pool._waiters) == 3)
    for i in range(3):
        pool.put([held[i]])                   # release one at a time
        wait_until(lambda: len(order) == i + 1)
    for t in ts: t.join(5)
    assert order == [10, 5, 1], order


def test_priority_timeout_cleans_up():
    pool = PriorityResourcePool(1)
    held = pool.get(1, priority=1)
    try:
        pool.get(1, priority=5, timeout=0.05); raise AssertionError("expected TimeoutError")
    except TimeoutError:
        pass
    assert pool._waiters == []                # the timed-out waiter must not block anybody
    pool.put(held)
    assert pool.get(1, priority=2) == held


if __name__ == "__main__":
    test_pool_stress(); test_pool_validation_and_timeout()
    test_priority_order(); test_priority_timeout_cleans_up()
    print("resource_pool OK")
```

### 2.5 Follow-ups to be ready for

- *"Add a timeout"* → already there (`wait_for(..., timeout)`; clean up in `finally`).
- *"Context manager"* → `with pool.lease(m) as resources:` that calls `put` in `finally`; the most common source of leaks is forgetting `put` on an exception path.
- *"Resources are objects that can break / be created lazily"* → keep `_free` as a deque; create up to `n` on demand; discard broken ones and decrease `_out` without returning them to `_free`.
- *"Fairness for equal priority"* → the ticket in the heap entry gives FIFO.
- *"Semaphore version"* → for `m == 1` and no priority, `threading.Semaphore(n)` + a thread-safe free list is enough; the Condition version is needed for `m > 1`.

---

## 3. Classic concurrency questions

These are the standard multi-threaded questions that come up in interviews. Items 3.1 to 3.8 map to numbered LeetCode "Concurrency" problems; see [Sources](#6-sources). For each: the problem, the trick, the code.

All code in this section goes in one file with a shared test block at the end.

### 3.1 Bounded blocking queue (producer-consumer), LeetCode 1188

**Trick:** one lock, **two conditions** (`not_full`, `not_empty`) so producers only wake consumers and vice versa. Each condition's waiters have identical predicates, so `notify()` (one) is enough, unlike the resource pool.

```python
# file: classics.py
import random
import threading
import time
from collections import deque


class BoundedBlockingQueue:
    def __init__(self, capacity):
        self._cap = capacity
        self._q = deque()
        lock = threading.Lock()
        self._not_full = threading.Condition(lock)       # two conditions, ONE shared lock
        self._not_empty = threading.Condition(lock)

    def enqueue(self, item):
        with self._not_full:
            self._not_full.wait_for(lambda: len(self._q) < self._cap)
            self._q.append(item)
            self._not_empty.notify()                     # one new item -> wake one consumer

    def dequeue(self):
        with self._not_empty:
            self._not_empty.wait_for(lambda: len(self._q) > 0)
            item = self._q.popleft()
            self._not_full.notify()                      # one free slot -> wake one producer
            return item

    def size(self):
        with self._not_empty:
            return len(self._q)
```

In real code you would use `queue.Queue(maxsize=n)`, which is exactly this. Say so, then show you know how it works.

### 3.2 Print in order, LeetCode 1114

Three threads call `first`, `second`, `third` in arbitrary order; output must be "firstsecondthird". **Trick:** one `Event` per edge in the chain (`first → second`, `second → third`).

```python
# file: classics.py
class Foo:
    def __init__(self):
        self._first_done = threading.Event()
        self._second_done = threading.Event()

    def first(self, printFirst):
        printFirst()
        self._first_done.set()

    def second(self, printSecond):
        self._first_done.wait()
        printSecond()
        self._second_done.set()

    def third(self, printThird):
        self._second_done.wait()
        printThird()
```

### 3.3 Print FooBar alternately, LeetCode 1115

Two threads must print `foobarfoobar...`. **Trick:** two semaphores passing a baton: `foo` starts with 1 permit, `bar` with 0.

```python
# file: classics.py
class FooBar:
    def __init__(self, n):
        self.n = n
        self._foo = threading.Semaphore(1)
        self._bar = threading.Semaphore(0)

    def foo(self, printFoo):
        for _ in range(self.n):
            self._foo.acquire()
            printFoo()
            self._bar.release()

    def bar(self, printBar):
        for _ in range(self.n):
            self._bar.acquire()
            printBar()
            self._foo.release()
```

### 3.4 Print Zero-Even-Odd, LeetCode 1116

Three threads print `0 1 0 2 0 3 ...` up to `n`. **Trick:** a three-way baton: `zero` runs, then hands to `odd` or `even` depending on the next number; they hand back to `zero`.

```python
# file: classics.py
class ZeroEvenOdd:
    def __init__(self, n):
        self.n = n
        self._zero = threading.Semaphore(1)
        self._odd = threading.Semaphore(0)
        self._even = threading.Semaphore(0)

    def zero(self, printNumber):
        for i in range(1, self.n + 1):
            self._zero.acquire()
            printNumber(0)
            (self._odd if i % 2 else self._even).release()

    def even(self, printNumber):
        for i in range(2, self.n + 1, 2):
            self._even.acquire()
            printNumber(i)
            self._zero.release()

    def odd(self, printNumber):
        for i in range(1, self.n + 1, 2):
            self._odd.acquire()
            printNumber(i)
            self._zero.release()
```

### 3.5 Building H2O, LeetCode 1117

Threads arrive one atom at a time; every group of three consecutive outputs must be one H2O (2 H + 1 O). **Trick:** semaphores cap atoms *per molecule* (2 H, 1 O); a **barrier of 3** assembles the molecule; a **second barrier** stops the next molecule from starting to print before this one has finished printing. (A common one-barrier solution can interleave two molecules' output; the second barrier is what makes the grouping strictly correct.)

```python
# file: classics.py
class H2O:
    def __init__(self):
        self._h = threading.Semaphore(2)
        self._o = threading.Semaphore(1)
        self._assemble = threading.Barrier(3)   # 2 H + 1 O present
        self._printed = threading.Barrier(3)    # all three have printed

    def hydrogen(self, releaseHydrogen):
        self._h.acquire()
        self._assemble.wait()
        releaseHydrogen()
        self._printed.wait()
        self._h.release()                        # only now may the next molecule's H enter

    def oxygen(self, releaseOxygen):
        self._o.acquire()
        self._assemble.wait()
        releaseOxygen()
        self._printed.wait()
        self._o.release()
```

### 3.6 Fizz Buzz multithreaded, LeetCode 1195

Four threads (`fizz`, `buzz`, `fizzbuzz`, `number`); together they must print 1..n in order. **Trick:** one shared counter `i` under a `Condition`; each thread waits until `i` is *its* kind of number, prints, increments, and `notify_all()`s. It is the same "wait for my predicate" pattern as the resource pool. Every thread must also exit when `i > n`.

```python
# file: classics.py
class FizzBuzz:
    def __init__(self, n):
        self.n = n
        self._i = 1
        self._cv = threading.Condition()

    def _run(self, mine, emit):
        while True:
            with self._cv:
                self._cv.wait_for(lambda: self._i > self.n or mine(self._i))
                if self._i > self.n:
                    return                       # everyone is woken by the last notify_all
                emit(self._i)                    # printing under the lock keeps the order exact
                self._i += 1
                self._cv.notify_all()

    def fizz(self, printFizz):
        self._run(lambda i: i % 3 == 0 and i % 5 != 0, lambda i: printFizz())

    def buzz(self, printBuzz):
        self._run(lambda i: i % 5 == 0 and i % 3 != 0, lambda i: printBuzz())

    def fizzbuzz(self, printFizzBuzz):
        self._run(lambda i: i % 15 == 0, lambda i: printFizzBuzz())

    def number(self, printNumber):
        self._run(lambda i: i % 3 != 0 and i % 5 != 0, printNumber)
```

### 3.7 Dining philosophers, LeetCode 1226

Five philosophers, five forks, each needs two. If everyone grabs their left fork first, everyone holds one and waits forever: **deadlock**. **Trick:** break the circular wait with a **global lock ordering**: always take the lower-numbered fork first. (Alternative: a "waiter" semaphore allowing at most 4 philosophers to try at once.)

```python
# file: classics.py
class DiningPhilosophers:
    def __init__(self):
        self._forks = [threading.Lock() for _ in range(5)]

    def wantsToEat(self, philosopher, pickLeftFork, pickRightFork,
                   eat, putLeftFork, putRightFork):
        left, right = philosopher, (philosopher + 1) % 5
        first, second = (left, right) if left < right else (right, left)   # lock ordering
        with self._forks[first]:
            with self._forks[second]:
                pickLeftFork(); pickRightFork()
                eat()
                putLeftFork(); putRightFork()
```

### 3.8 Multithreaded web crawler, LeetCode 1242

Crawl every URL reachable from `startUrl` on the **same hostname**, using `htmlParser.getUrls(url)` (a slow, blocking call). **Trick:** parallelize only the slow part (`getUrls`) with a thread pool, and crawl **level by level**, so the `visited` set is only touched by the coordinating thread, so no lock is needed. Confining shared state to one thread is usually simpler and safer than locking it.

```python
# file: classics.py
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse


def crawl(startUrl, htmlParser, workers=8):
    host = urlparse(startUrl).hostname
    visited = {startUrl}
    frontier = [startUrl]
    with ThreadPoolExecutor(max_workers=workers) as pool:
        while frontier:
            next_frontier = []
            for urls in pool.map(htmlParser.getUrls, frontier):   # parallel fetch of one BFS level
                for url in urls:                                  # single-threaded bookkeeping
                    if urlparse(url).hostname == host and url not in visited:
                        visited.add(url)
                        next_frontier.append(url)
            frontier = next_frontier
    return list(visited)
```

Trade-off: a level waits for its slowest page. The fully asynchronous alternative (workers push new URLs onto a shared queue, `visited` guarded by a lock, termination via a pending-task counter) keeps all workers busy but is harder to get right.

### 3.9 Tests for section 3

```python
# file: classics.py
# ---- tests ----
def run(*fns, timeout=15):
    errors = []

    def wrap(fn):
        def inner():
            try:
                fn()
            except BaseException as e:
                errors.append(e)
        return inner
    ts = [threading.Thread(target=wrap(f), daemon=True) for f in fns]
    for t in ts: t.start()
    for t in ts: t.join(timeout); assert not t.is_alive(), "deadlock?"
    if errors:
        raise errors[0]


def test_bounded_queue():
    q, N, out, lock = BoundedBlockingQueue(2), 300, [], threading.Lock()

    def producer(base):
        for i in range(N):
            q.enqueue(base + i)

    def consumer():
        for _ in range(N):
            x = q.dequeue()
            with lock:
                out.append(x)
    run(*[lambda b=b: producer(b) for b in (0, 1000, 2000)], *[consumer] * 3)
    assert sorted(out) == sorted(b + i for b in (0, 1000, 2000) for i in range(N))
    assert q.size() == 0


def test_print_in_order():
    foo, out = Foo(), []
    run(lambda: foo.third(lambda: out.append("third")),
        lambda: foo.second(lambda: out.append("second")),
        lambda: foo.first(lambda: out.append("first")))
    assert out == ["first", "second", "third"]


def test_foobar():
    fb, out = FooBar(5), []
    run(lambda: fb.bar(lambda: out.append("bar")), lambda: fb.foo(lambda: out.append("foo")))
    assert "".join(out) == "foobar" * 5


def test_zero_even_odd():
    z, out = ZeroEvenOdd(7), []
    run(lambda: z.odd(out.append), lambda: z.even(out.append), lambda: z.zero(out.append))
    assert "".join(map(str, out)) == "01020304050607"


def test_h2o():
    h2o, out = H2O(), []
    atoms = ["H"] * 12 + ["O"] * 6
    random.Random(1).shuffle(atoms)
    run(*[(lambda: h2o.hydrogen(lambda: out.append("H"))) if a == "H"
          else (lambda: h2o.oxygen(lambda: out.append("O"))) for a in atoms])
    chunks = ["".join(sorted(out[i:i + 3])) for i in range(0, len(out), 3)]
    assert len(out) == 18 and all(c == "HHO" for c in chunks), out


def test_fizzbuzz():
    fb, out = FizzBuzz(15), []
    run(lambda: fb.fizz(lambda: out.append("fizz")), lambda: fb.buzz(lambda: out.append("buzz")),
        lambda: fb.fizzbuzz(lambda: out.append("fizzbuzz")), lambda: fb.number(out.append))
    want = ["fizzbuzz" if i % 15 == 0 else "fizz" if i % 3 == 0 else "buzz" if i % 5 == 0 else i
            for i in range(1, 16)]
    assert out == want, out


def test_philosophers():
    dp, meals, eating = DiningPhilosophers(), [0] * 5, set()

    def philosopher(p):
        def eat():
            assert (p + 1) % 5 not in eating and (p - 1) % 5 not in eating, "neighbour eating"
            eating.add(p); time.sleep(0.0003); eating.discard(p)
            meals[p] += 1
        for _ in range(40):
            dp.wantsToEat(p, lambda: None, lambda: None, eat, lambda: None, lambda: None)
    run(*[lambda p=p: philosopher(p) for p in range(5)])
    assert meals == [40] * 5


def test_crawler():
    class FakeParser:
        def __init__(self, graph): self.graph = graph
        def getUrls(self, url):
            time.sleep(0.01)
            return self.graph.get(url, [])
    g = {"http://a.com/": ["http://a.com/1", "http://a.com/2", "http://b.com/x"],
         "http://a.com/1": ["http://a.com/3", "http://a.com/"],
         "http://a.com/2": ["http://a.com/3"],
         "http://b.com/x": ["http://a.com/hidden"]}
    got = set(crawl("http://a.com/", FakeParser(g)))
    assert got == {"http://a.com/", "http://a.com/1", "http://a.com/2", "http://a.com/3"}, got


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
    print("classics OK")
```

---

## 4. Systems-style concurrency questions

These are the "design a thread-safe X" questions that show up in onsite loops. They are not tied to numbered LeetCode problems, but each is a well-known interview and system-design staple (see [Sources](#6-sources)).

### 4.1 Rate limiter (token bucket)

**Trick:** don't run a timer thread. Store `(tokens, last_refill_time)` and **refill lazily** on each call using elapsed time. The refill + check + decrement must be one critical section. Inject the clock so it is testable.

```python
# file: systems.py
import threading
import time
from collections import OrderedDict


class TokenBucket:
    """Allows bursts up to `capacity`, sustained `rate` tokens per second."""

    def __init__(self, rate, capacity, clock=time.monotonic):
        self.rate, self.capacity, self._clock = rate, capacity, clock
        self._tokens = float(capacity)
        self._last = clock()
        self._lock = threading.Lock()

    def allow(self, cost=1):
        with self._lock:
            now = self._clock()
            self._tokens = min(self.capacity, self._tokens + (now - self._last) * self.rate)
            self._last = now
            if self._tokens >= cost:
                self._tokens -= cost
                return True
            return False


class KeyedRateLimiter:
    """One bucket per user/IP. (Production: evict idle buckets to bound memory.)"""

    def __init__(self, rate, capacity, clock=time.monotonic):
        self._args = (rate, capacity, clock)
        self._buckets = {}
        self._lock = threading.Lock()

    def allow(self, key, cost=1):
        with self._lock:                                  # lock only the get-or-create
            bucket = self._buckets.get(key)
            if bucket is None:
                bucket = self._buckets[key] = TokenBucket(*self._args)
        return bucket.allow(cost)                         # per-bucket lock: keys don't contend
```

Why token bucket over a fixed window: fixed windows allow a 2× burst across the boundary. Sliding-window log is exact but stores every timestamp (O(requests) memory).

### 4.2 Thread-safe LRU cache (with single-flight loading)

**Trick:** `OrderedDict` gives O(1) `move_to_end` / `popitem`. Even `get` **mutates** (recency order), so `get` needs the lock too. A frequent follow-up is the **cache stampede**: 100 threads miss the same key and all call the slow loader. Fix with *single-flight*: the first thread loads, the rest wait on an `Event` for that key. Never run the loader while holding the cache lock.

```python
# file: systems.py
class LRUCache:
    def __init__(self, capacity):
        self._cap = capacity
        self._d = OrderedDict()
        self._loading = {}                       # key -> Event for in-flight loads
        self._lock = threading.Lock()

    def get(self, key, default=None):
        with self._lock:
            if key not in self._d:
                return default
            self._d.move_to_end(key)             # a read is also a "use"
            return self._d[key]

    def put(self, key, value):
        with self._lock:
            self._put_locked(key, value)

    def _put_locked(self, key, value):
        self._d[key] = value
        self._d.move_to_end(key)
        if len(self._d) > self._cap:
            self._d.popitem(last=False)          # evict least recently used

    def get_or_load(self, key, loader):
        while True:
            with self._lock:
                if key in self._d:
                    self._d.move_to_end(key)
                    return self._d[key]
                event = self._loading.get(key)
                owner = event is None
                if owner:
                    event = self._loading[key] = threading.Event()
            if not owner:
                event.wait()                     # someone else is loading this key
                continue                         # then re-check the cache
            try:
                value = loader(key)              # slow call OUTSIDE the lock
            except BaseException:
                with self._lock:
                    del self._loading[key]
                event.set()                      # waiters retry (one becomes the new owner)
                raise
            with self._lock:
                self._put_locked(key, value)
                del self._loading[key]
            event.set()
            return value
```

### 4.3 Readers-writer lock (writer-preference)

**Trick:** many readers **or** one writer. Naive reader-preference **starves writers** under continuous reads, so new readers must yield when a writer is waiting (`writers_waiting > 0`). One `Condition` guards three counters.

```python
# file: systems.py
from contextlib import contextmanager


class RWLock:
    def __init__(self):
        self._cv = threading.Condition()
        self._readers = 0
        self._writer = False
        self._writers_waiting = 0

    def acquire_read(self):
        with self._cv:
            self._cv.wait_for(lambda: not self._writer and self._writers_waiting == 0)
            self._readers += 1

    def release_read(self):
        with self._cv:
            self._readers -= 1
            if self._readers == 0:
                self._cv.notify_all()            # a waiting writer may go

    def acquire_write(self):
        with self._cv:
            self._writers_waiting += 1           # announce, so new readers hold back
            try:
                self._cv.wait_for(lambda: not self._writer and self._readers == 0)
            finally:
                self._writers_waiting -= 1
            self._writer = True

    def release_write(self):
        with self._cv:
            self._writer = False
            self._cv.notify_all()                # wake readers and writers; predicates decide

    @contextmanager
    def read_locked(self):
        self.acquire_read()
        try:
            yield
        finally:
            self.release_read()

    @contextmanager
    def write_locked(self):
        self.acquire_write()
        try:
            yield
        finally:
            self.release_write()
```

### 4.4 Thread pool / task executor

**Trick:** N workers loop on a `queue.Queue`; a **sentinel** (`None`) per worker is the shutdown signal. Return a `concurrent.futures.Future` so callers get results and exceptions. An uncaught exception must not kill a worker.

```python
# file: systems.py
import queue
from concurrent.futures import Future


class ThreadPool:
    def __init__(self, n_workers):
        self._q = queue.Queue()
        self._threads = [threading.Thread(target=self._worker, daemon=True)
                         for _ in range(n_workers)]
        for t in self._threads:
            t.start()

    def submit(self, fn, *args, **kwargs):
        future = Future()
        self._q.put((future, fn, args, kwargs))
        return future

    def _worker(self):
        while True:
            item = self._q.get()
            if item is None:                                  # shutdown sentinel
                return
            future, fn, args, kwargs = item
            if not future.set_running_or_notify_cancel():
                continue                                      # cancelled before it started
            try:
                future.set_result(fn(*args, **kwargs))
            except BaseException as exc:                      # worker survives task failures
                future.set_exception(exc)

    def shutdown(self):
        for _ in self._threads:
            self._q.put(None)                                 # queued AFTER pending tasks: drains first
        for t in self._threads:
            t.join()
```

(In real code: `concurrent.futures.ThreadPoolExecutor`. Know what it does under the hood.)

### 4.5 Delayed-task scheduler

**Trick:** a **min-heap by due time** plus one worker that sleeps on a `Condition` **until the earliest due time or until a new, earlier task arrives**. `wait(timeout)` is exactly "sleep until due, but wake early if notified". Run the callback *outside* the lock so a slow task can't block `schedule()`.

```python
# file: systems.py
import heapq
import itertools


class Scheduler:
    def __init__(self):
        self._heap = []                                       # (due_time, seq, fn)
        self._seq = itertools.count()                         # tie-break so fns are never compared
        self._cv = threading.Condition()
        self._closed = False
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def schedule(self, fn, delay):
        with self._cv:
            heapq.heappush(self._heap, (time.monotonic() + delay, next(self._seq), fn))
            self._cv.notify()                                 # the new task may be the earliest

    def close(self):
        with self._cv:
            self._closed = True
            self._cv.notify_all()
        self._thread.join()

    def _loop(self):
        while True:
            with self._cv:
                while True:
                    if self._closed:
                        return
                    if not self._heap:
                        self._cv.wait()                       # nothing scheduled
                        continue
                    delay = self._heap[0][0] - time.monotonic()
                    if delay <= 0:
                        _, _, fn = heapq.heappop(self._heap)
                        break
                    self._cv.wait(delay)                      # sleep until due OR new earlier task
            fn()                                              # outside the lock
```

### 4.6 Tests for section 4

```python
# file: systems.py
# ---- tests ----
def test_token_bucket():
    now = [0.0]
    tb = TokenBucket(rate=1, capacity=3, clock=lambda: now[0])
    assert [tb.allow() for _ in range(4)] == [True, True, True, False]
    now[0] += 2
    assert [tb.allow() for _ in range(3)] == [True, True, False]
    # concurrency: with a frozen clock exactly `capacity` calls may succeed
    tb = TokenBucket(rate=1, capacity=50, clock=lambda: 0.0)
    results, lock = [], threading.Lock()

    def hit():
        ok = tb.allow()
        with lock:
            results.append(ok)
    ts = [threading.Thread(target=hit) for _ in range(200)]
    for t in ts: t.start()
    for t in ts: t.join()
    assert sum(results) == 50
    kl = KeyedRateLimiter(1, 1, clock=lambda: 0.0)
    assert kl.allow("u1") and not kl.allow("u1") and kl.allow("u2")


def test_lru():
    c = LRUCache(2)
    c.put("a", 1); c.put("b", 2); assert c.get("a") == 1
    c.put("c", 3)                                              # evicts b (LRU), not a
    assert c.get("b") is None and c.get("a") == 1 and c.get("c") == 3
    calls, cl = [], threading.Lock()

    def loader(k):
        time.sleep(0.05)
        with cl:
            calls.append(k)
        return k * 2
    c2, out = LRUCache(10), []
    ts = [threading.Thread(target=lambda: out.append(c2.get_or_load(7, loader))) for _ in range(10)]
    for t in ts: t.start()
    for t in ts: t.join()
    assert out == [14] * 10 and len(calls) == 1               # single flight: loaded once

    def bad(k):
        raise RuntimeError("boom")
    try:
        c2.get_or_load(99, bad); raise AssertionError("expected RuntimeError")
    except RuntimeError:
        pass
    assert c2.get_or_load(99, lambda k: "ok") == "ok"          # failure didn't wedge the key


def test_rwlock():
    lock = RWLock()
    st = {"readers": 0, "writing": False, "max_readers": 0}
    sl, errors = threading.Lock(), []

    def reader():
        for _ in range(20):
            with lock.read_locked():
                with sl:
                    st["readers"] += 1
                    st["max_readers"] = max(st["max_readers"], st["readers"])
                    if st["writing"]:
                        errors.append("reader saw writer")
                time.sleep(0.001)
                with sl:
                    st["readers"] -= 1

    def writer():
        for _ in range(10):
            with lock.write_locked():
                with sl:
                    if st["readers"] or st["writing"]:
                        errors.append("writer not exclusive")
                    st["writing"] = True
                time.sleep(0.001)
                with sl:
                    st["writing"] = False
    ts = [threading.Thread(target=reader) for _ in range(5)] + \
         [threading.Thread(target=writer) for _ in range(2)]
    for t in ts: t.start()
    for t in ts: t.join(30); assert not t.is_alive(), "deadlock / writer starvation?"
    assert not errors, errors
    assert st["max_readers"] > 1                               # readers really ran together


def test_thread_pool():
    pool = ThreadPool(4)
    futures = [pool.submit(lambda x=x: x * x) for x in range(20)]
    assert [f.result(5) for f in futures] == [x * x for x in range(20)]
    bad = pool.submit(lambda: 1 / 0)
    try:
        bad.result(5); raise AssertionError("expected ZeroDivisionError")
    except ZeroDivisionError:
        pass
    assert pool.submit(lambda: "still alive").result(5) == "still alive"
    pool.shutdown()


def test_scheduler():
    s, order, done = Scheduler(), [], threading.Event()
    s.schedule(lambda: order.append("slow"), 0.15)
    s.schedule(lambda: order.append("fast"), 0.05)
    s.schedule(lambda: (order.append("mid"), None)[1], 0.10)
    s.schedule(done.set, 0.2)
    assert done.wait(2)
    s.close()
    assert order == ["fast", "mid", "slow"], order


if __name__ == "__main__":
    test_token_bucket(); test_lru(); test_rwlock(); test_thread_pool(); test_scheduler()
    print("systems OK")
```

---

## 5. Rules of thumb for the interview

1. **Name the invariant first.** "This lock protects: free list + checked-out set." If you can't state it, you can't place the lock.
2. **`Condition` + `wait_for(predicate)`.** Never `if not ready: wait()` (spurious wakeups, stolen wakeups). `notify()` only when all waiters on that condition are interchangeable; otherwise `notify_all()`.
3. **All-or-nothing acquisition** for multi-resource requests (avoids hold-and-wait deadlock). If you must take several locks, impose a **global order** (dining philosophers).
4. **Register before you wait, deregister in `finally`.** Every waiter structure (priority heap, in-flight map) must be cleaned on timeout and exceptions, and followed by `notify_all`.
5. **Don't call slow or foreign code while holding a lock** (loaders, callbacks, I/O). Hold the lock only for state changes.
6. **Prefer confining state to one thread** (web crawler) or using thread-safe hand-offs (`Queue`) over sharing state with locks.
7. **Optimistic vs pessimistic:** short, rarely conflicting transactions → validate at commit and retry (KV store). Long or hot-spot transactions → locks.
8. **Always say the guarantee out loud:** "each operation is atomic/linearizable; transactions are snapshot-isolated; conflicts are retryable".
9. **Test with deadlock detection:** join with a timeout and fail loudly (`assert not t.is_alive()`), as in the tests here. A hung test run is a failed interview.
10. **Know the production answer** (`queue.Queue`, `Semaphore`, `ThreadPoolExecutor`) *and* how to build it by hand. Interviewers ask for the latter.

---

## 6. Sources

**Supplied by you (in your notes)**
- Rippling phone screen, "KeyValue datastore with begin, commit and rollback": <https://leetcode.com/discuss/post/4985212/rippling-phonescreen-keyvalue-datastore-fi5hl/>
- Bloomberg onsite, "Key value store with transactions": <https://leetcode.com/discuss/interview-question/279913/bloomberg-onsite-key-value-store-with-transactions>
- The "Design and implement an in-memory key–value store... Follow-up 1 (nested transactions) / Follow-up 2 (concurrency)" text and the whiteboard conflict example (T1 commits `k3`, T2 fails): from your notes, **no origin was given** for these.
- Resource-pool `get`/`put` and priority variant (section 2): from your notes, **no public source attached**.

**LeetCode Concurrency problems used in section 3** (problem names and numbers as I know them; I did not re-open the live pages while writing this, so confirm slugs/numbers on the site):
- 1114 Print in Order: <https://leetcode.com/problems/print-in-order/>
- 1115 Print FooBar Alternately: <https://leetcode.com/problems/print-foobar-alternately/>
- 1116 Print Zero Even Odd: <https://leetcode.com/problems/print-zero-even-odd/>
- 1117 Building H2O: <https://leetcode.com/problems/building-h2o/>
- 1188 Design Bounded Blocking Queue: <https://leetcode.com/problems/design-bounded-blocking-queue/>
- 1195 Fizz Buzz Multithreaded: <https://leetcode.com/problems/fizz-buzz-multithreaded/>
- 1226 The Dining Philosophers: <https://leetcode.com/problems/the-dining-philosophers/>
- 1242 Web Crawler Multithreaded: <https://leetcode.com/problems/web-crawler-multithreaded/>
- 146 LRU Cache (the single-threaded base of 4.2): <https://leetcode.com/problems/lru-cache/>

**Background references** (concepts behind the designs; cited from memory)
- Martin Kleppmann, *Designing Data-Intensive Applications*: ch. 3 (storage and retrieval, write-ahead log) and ch. 7 (transactions: snapshot isolation, write skew, serializability, optimistic concurrency).
- Remzi and Andrea Arpaci-Dusseau, *Operating Systems: Three Easy Pieces*: the concurrency chapters (locks, condition variables, semaphores, common concurrency bugs).
- Allen B. Downey, *The Little Book of Semaphores*: baton-passing, barriers, readers-writers, dining philosophers, H2O-style problems.
- Alex Xu, *System Design Interview, Vol. 1*: "Design a Rate Limiter" (token bucket vs window algorithms).
- Python standard library documentation: `threading` (Lock, Condition, Semaphore, Event, Barrier), `queue`, `concurrent.futures`.

**Not verified:** I have not confirmed how often any of the section 4 questions are reported at specific companies; they are widely used as general interview staples rather than tied to one source.
