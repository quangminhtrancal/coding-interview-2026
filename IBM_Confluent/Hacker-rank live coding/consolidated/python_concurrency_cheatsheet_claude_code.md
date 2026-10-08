# Python Concurrency Interview Cheat Sheet

## 1. Core concepts

| Concept | One-liner |
|---|---|
| **Concurrency vs parallelism** | Concurrency = dealing with many things at once (interleaving). Parallelism = doing many things at the same instant (multiple cores). |
| **GIL** | CPython lets only one thread execute bytecode at a time. Threads **don't speed up CPU-bound work**, but they do help with **I/O-bound** work (the GIL is released while blocking). |
| **Race condition** | Result depends on thread timing. `counter += 1` is **not atomic** (load, add, store). |
| **Deadlock** | Threads wait on each other forever. Needs: mutual exclusion, hold-and-wait, no preemption, circular wait. Break one, usually with **lock ordering**. |
| **Livelock / starvation** | Threads keep running but make no progress, or one thread never gets the resource. |
| **Thread-safe** | Correct under concurrent access without external synchronization. |
| **Daemon thread** | Killed abruptly when the main thread exits. |

**Which tool to use:**

| Workload | Use |
|---|---|
| I/O-bound, few to hundreds of tasks | `threading` / `ThreadPoolExecutor` |
| I/O-bound, thousands of connections | `asyncio` |
| CPU-bound | `multiprocessing` / `ProcessPoolExecutor` |

## 2. Primitives

| Primitive | Use | Key methods |
|---|---|---|
| `Lock` | Mutual exclusion | `acquire()`, `release()`, `with lock:` |
| `RLock` | Re-entrant (same thread can re-acquire) | same |
| `Semaphore(n)` | Allow up to n holders, also used for signaling | `acquire()`, `release()` |
| `Event` | One-shot or flag signal | `set()`, `clear()`, `wait()`, `is_set()` |
| `Condition` | Wait until a predicate is true | `wait()`, `notify()`, `notify_all()` |
| `Barrier(n)` | Wait until n threads arrive | `wait()` |
| `queue.Queue` | Thread-safe FIFO, **blocking** put/get | `put()`, `get()`, `task_done()`, `join()` |
| `Timer` | Run a function after a delay | `start()`, `cancel()` |
| `threading.local()` | Per-thread storage | attributes |

**Golden rules:**
- Always use `with lock:` so the lock is released on exceptions.
- Always wait on a `Condition` in a **`while` loop**, not `if`, because of spurious wakeups.
- Acquire multiple locks in a **consistent global order**.
- Keep critical sections small, and never call unknown or blocking code while holding a lock.
- Prefer `Queue` over hand-rolled shared state.

## 3. Coding patterns

### Pattern 1: Basic threads and join
```python
import threading

def worker(n):
    print(f"worker {n}")

threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]
for t in threads: t.start()
for t in threads: t.join()
```

### Pattern 2: Race condition and fix
```python
counter = 0
lock = threading.Lock()

def inc():
    global counter
    for _ in range(100_000):
        with lock:          # remove the lock to demonstrate the race
            counter += 1
```

### Pattern 3: Producer-consumer with `Queue` (most common)
```python
import threading, queue

q = queue.Queue(maxsize=10)   # bounded gives back-pressure
SENTINEL = object()

def producer():
    for i in range(20):
        q.put(i)              # blocks if full
    q.put(SENTINEL)

def consumer():
    while True:
        item = q.get()        # blocks if empty
        if item is SENTINEL:
            q.put(SENTINEL)   # propagate to other consumers
            break
        print("got", item)

threading.Thread(target=producer).start()
cs = [threading.Thread(target=consumer) for _ in range(3)]
for c in cs: c.start()
```
Use `q.task_done()` per item and `q.join()` in the main thread if you want to wait until all work is processed.

### Pattern 4: Bounded blocking queue from scratch (`Condition`)
```python
from collections import deque

class BoundedBlockingQueue:
    def __init__(self, capacity):
        self.q, self.cap = deque(), capacity
        lock = threading.Lock()
        self.not_full = threading.Condition(lock)
        self.not_empty = threading.Condition(lock)

    def put(self, x):
        with self.not_full:
            while len(self.q) >= self.cap:
                self.not_full.wait()
            self.q.append(x)
            self.not_empty.notify()

    def get(self):
        with self.not_empty:
            while not self.q:
                self.not_empty.wait()
            x = self.q.popleft()
            self.not_full.notify()
            return x
```

### Pattern 5: Thread pool and futures
```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def fetch(url): ...

with ThreadPoolExecutor(max_workers=8) as ex:
    # ordered results
    results = list(ex.map(fetch, urls))

    # as they finish, with error handling
    futs = {ex.submit(fetch, u): u for u in urls}
    for f in as_completed(futs):
        try:
            print(futs[f], f.result())
        except Exception as e:
            print("failed", futs[f], e)
```

### Pattern 6: Custom thread pool
```python
class ThreadPool:
    def __init__(self, n):
        self.q = queue.Queue()
        self.threads = [threading.Thread(target=self._run, daemon=True) for _ in range(n)]
        for t in self.threads: t.start()

    def _run(self):
        while True:
            fn, args = self.q.get()
            if fn is None: break           # shutdown signal
            try: fn(*args)
            finally: self.q.task_done()

    def submit(self, fn, *args): self.q.put((fn, args))
    def wait(self): self.q.join()
    def shutdown(self):
        for _ in self.threads: self.q.put((None, ()))
        for t in self.threads: t.join()
```

### Pattern 7: Limit concurrency (Semaphore)
```python
sem = threading.Semaphore(3)   # max 3 concurrent

def limited_task(i):
    with sem:
        ...                    # at most 3 threads here
```

### Pattern 8: Ordering and signaling (LeetCode 1114/1115/1116/1195)

**Print in order** (first, second, third):
```python
class Foo:
    def __init__(self):
        self.e1, self.e2 = threading.Event(), threading.Event()
    def first(self, f):  f();  self.e1.set()
    def second(self, f): self.e1.wait(); f(); self.e2.set()
    def third(self, f):  self.e2.wait(); f()
```

**Alternate FooBar** (n times each, strictly alternating):
```python
class FooBar:
    def __init__(self, n):
        self.n = n
        self.foo_sem = threading.Semaphore(1)
        self.bar_sem = threading.Semaphore(0)
    def foo(self, printFoo):
        for _ in range(self.n):
            self.foo_sem.acquire(); printFoo(); self.bar_sem.release()
    def bar(self, printBar):
        for _ in range(self.n):
            self.bar_sem.acquire(); printBar(); self.foo_sem.release()
```

**Zero-Even-Odd** (`0102030405...`):
```python
class ZeroEvenOdd:
    def __init__(self, n):
        self.n = n
        self.z = threading.Semaphore(1)
        self.o = threading.Semaphore(0)
        self.e = threading.Semaphore(0)
    def zero(self, pr):
        for i in range(1, self.n + 1):
            self.z.acquire(); pr(0)
            (self.o if i % 2 else self.e).release()
    def odd(self, pr):
        for i in range(1, self.n + 1, 2):
            self.o.acquire(); pr(i); self.z.release()
    def even(self, pr):
        for i in range(2, self.n + 1, 2):
            self.e.acquire(); pr(i); self.z.release()
```

**H2O** (every 3 consecutive outputs form 2H + 1O):
```python
class H2O:
    def __init__(self):
        self.h = threading.Semaphore(2)
        self.o = threading.Semaphore(1)
        self.barrier = threading.Barrier(3)
    def hydrogen(self, releaseHydrogen):
        self.h.acquire(); self.barrier.wait()
        releaseHydrogen(); self.h.release()
    def oxygen(self, releaseOxygen):
        self.o.acquire(); self.barrier.wait()
        releaseOxygen(); self.o.release()
```

### Pattern 9: Readers-writer lock
```python
class RWLock:
    def __init__(self):
        self._readers = 0
        self._mutex = threading.Lock()   # protects _readers
        self._write = threading.Lock()   # held by writer or by the reader group

    def acquire_read(self):
        with self._mutex:
            self._readers += 1
            if self._readers == 1: self._write.acquire()
    def release_read(self):
        with self._mutex:
            self._readers -= 1
            if self._readers == 0: self._write.release()
    def acquire_write(self): self._write.acquire()
    def release_write(self): self._write.release()
```
Note: this favors readers, so writers can starve. Mention that, plus a writer-preference variant, as a follow-up.

### Pattern 10: Dining philosophers (deadlock avoidance)
```python
forks = [threading.Lock() for _ in range(5)]

def philosopher(i):
    left, right = i, (i + 1) % 5
    first, second = sorted((left, right))   # global lock ordering breaks circular wait
    for _ in range(3):
        with forks[first]:
            with forks[second]:
                print(f"{i} eating")
```
Alternatives: allow at most 4 philosophers to sit (a `Semaphore(4)`), or use `acquire(timeout=...)` with back-off.

### Pattern 11: Thread-safe singleton (double-checked locking)
```python
class Singleton:
    _inst = None
    _lock = threading.Lock()
    def __new__(cls):
        if cls._inst is None:
            with cls._lock:
                if cls._inst is None:
                    cls._inst = super().__new__(cls)
        return cls._inst
```

### Pattern 12: Thread-safe counter / cache
```python
class SafeCounter:
    def __init__(self): self._v, self._l = 0, threading.Lock()
    def inc(self):
        with self._l: self._v += 1
    def get(self):
        with self._l: return self._v

class ThreadSafeLRU:
    def __init__(self, cap):
        from collections import OrderedDict
        self.d, self.cap, self.l = OrderedDict(), cap, threading.Lock()
    def get(self, k):
        with self.l:
            if k not in self.d: return None
            self.d.move_to_end(k); return self.d[k]
    def put(self, k, v):
        with self.l:
            self.d[k] = v; self.d.move_to_end(k)
            if len(self.d) > self.cap: self.d.popitem(last=False)
```

### Pattern 13: Rate limiter (token bucket)
```python
import time

class TokenBucket:
    def __init__(self, rate, capacity):
        self.rate, self.cap = rate, capacity
        self.tokens, self.last = capacity, time.monotonic()
        self.lock = threading.Lock()
    def allow(self):
        with self.lock:
            now = time.monotonic()
            self.tokens = min(self.cap, self.tokens + (now - self.last) * self.rate)
            self.last = now
            if self.tokens >= 1:
                self.tokens -= 1
                return True
            return False
```

### Pattern 14: Concurrent web crawler
```python
def crawl(start, get_links, max_workers=8):
    visited, lock = {start}, threading.Lock()
    with ThreadPoolExecutor(max_workers) as ex:
        frontier = [ex.submit(get_links, start)]
        while frontier:
            next_frontier = []
            for f in frontier:
                for link in f.result():
                    with lock:
                        if link in visited: continue
                        visited.add(link)
                    next_frontier.append(ex.submit(get_links, link))
            frontier = next_frontier
    return visited
```

### Pattern 15: Barrier and phased work
```python
barrier = threading.Barrier(4)
def phase_worker(i):
    ...                    # phase 1
    barrier.wait()         # all 4 must arrive
    ...                    # phase 2
```

### Pattern 16: Graceful shutdown with `Event`
```python
stop = threading.Event()
def loop():
    while not stop.is_set():
        ...
        stop.wait(timeout=1)   # sleeps but wakes instantly on set()
# later: stop.set(); t.join()
```

### Pattern 17: Multiprocessing for CPU-bound work
```python
from concurrent.futures import ProcessPoolExecutor

def heavy(n): return sum(i * i for i in range(n))

if __name__ == "__main__":          # required on Windows/macOS (spawn)
    with ProcessPoolExecutor() as ex:
        print(list(ex.map(heavy, [10**6] * 8)))
```
Arguments and results must be picklable. For sharing state, use `multiprocessing.Queue`, `Value`/`Array`, or `Manager`.

### Pattern 18: asyncio equivalents
```python
import asyncio

async def fetch(i, sem):
    async with sem:                    # limit concurrency
        await asyncio.sleep(1)         # simulated I/O
        return i

async def main():
    sem = asyncio.Semaphore(5)
    results = await asyncio.gather(*(fetch(i, sem) for i in range(20)))

    # producer/consumer
    q = asyncio.Queue(maxsize=10)
    async def prod():
        for i in range(10): await q.put(i)
    async def cons():
        while True:
            x = await q.get(); q.task_done()

    # timeout
    try:
        await asyncio.wait_for(fetch(1, sem), timeout=0.5)
    except asyncio.TimeoutError:
        pass

asyncio.run(main())
```
Never call blocking code (`time.sleep`, `requests`) inside a coroutine. Use `await asyncio.to_thread(fn)` instead.

## 4. Deadlock toolbox

1. **Lock ordering**: always acquire in the same global order (sort by `id()` or an index).
2. **Timeouts**: `lock.acquire(timeout=1)`, then back off and retry.
3. **Lock hierarchy / single big lock** for simplicity.
4. **Avoid nested locks** and never call callbacks while holding a lock.
5. **Use higher-level tools** (`Queue`, executors) that hide the locks.

## 5. Interview talking points

- **"Is `dict`/`list` thread-safe in Python?"** Single operations like `append` and `d[k] = v` are atomic under the GIL, but compound ones (`if k not in d: d[k] = ...`, `x += 1`) are not.
- **"Why threads if there's a GIL?"** I/O releases the GIL. C extensions like NumPy can too. Otherwise use processes.
- **`Lock` vs `RLock`**: an `RLock` lets the same thread re-acquire it, which is useful for recursive or nested method calls. It costs slightly more.
- **`Condition` vs `Event`**: an `Event` is a simple flag. A `Condition` is for "wait until some state predicate holds" and is always paired with a lock.
- **`notify` vs `notify_all`**: use `notify_all` when waiters wait for different predicates or when unsure.
- **Back-pressure**: bound your queues, because unbounded queues hide overload and eat memory.
- **Testing concurrency**: use stress loops, `sys.setswitchinterval(1e-6)` to force more context switches, and run many iterations.
- **Free-threaded Python (3.13+ experimental, PEP 703)**: the GIL becomes optional, so races you never saw before become real. Always lock shared mutable state.
- **Always mention:** correctness first (no races, no deadlocks), then liveness (no starvation), then performance.

## 6. Quick decision flow

```
Shared mutable state?            → Lock (or avoid sharing: use Queue)
Wait for a condition?            → Condition (or Event for simple flags)
Limit N concurrent things?       → Semaphore
Hand off work between threads?   → Queue
Run many tasks, collect results? → ThreadPoolExecutor / ProcessPoolExecutor
Thousands of I/O connections?    → asyncio
CPU-heavy?                       → multiprocessing
Threads must meet at a point?    → Barrier
Signal "stop"?                   → Event
```
