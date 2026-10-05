# Python Concurrency Interview Guide

Additional note from ChatGPT [here](https://chatgpt.com/s/t_6ac3351be6e48191a315ee092b6b51a9)

## 0. Key concepts to say out loud

- **GIL**: only one thread runs Python bytecode at a time. Threads help for **I/O-bound** work; use `multiprocessing` / `ProcessPoolExecutor` for **CPU-bound**.
- **Race condition**: result depends on thread timing. `x += 1` is NOT atomic (load, add, store).
- **Deadlock** needs 4 conditions: mutual exclusion, hold-and-wait, no preemption, circular wait. Break one (usually: **consistent lock ordering** or **timeouts**).
- **Always** use `with lock:` (releases on exceptions). **Always** wrap `Condition.wait()` in a `while` loop (spurious wakeups).
- Daemon threads die when main exits; non-daemon threads must be `join()`ed.

## 1. Syntax cheat sheet

```python
import threading, queue, time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed

# --- Thread ---
t = threading.Thread(target=fn, args=(1, 2), kwargs={"k": 3}, daemon=False)
t.start(); t.join(timeout=None); t.is_alive()
threading.current_thread().name; threading.get_ident()

# --- Lock / RLock ---
lock = threading.Lock()
with lock: ...                       # preferred
lock.acquire(blocking=True, timeout=-1); lock.release()
rlock = threading.RLock()            # same thread may re-acquire

# --- Condition (lock + wait/notify) ---
cv = threading.Condition()           # or Condition(existing_lock)
with cv:
    while not predicate(): cv.wait(timeout=None)
    cv.notify(); cv.notify_all()
    cv.wait_for(lambda: predicate()) # built-in while loop

# --- Semaphore (counter) ---
sem = threading.Semaphore(3)         # BoundedSemaphore raises on over-release
sem.acquire(); sem.release()

# --- Event (flag) ---
ev = threading.Event()
ev.set(); ev.clear(); ev.is_set(); ev.wait(timeout=None)

# --- Barrier (N threads rendezvous) ---
bar = threading.Barrier(3); bar.wait()

# --- Thread-local ---
local = threading.local(); local.x = 1

# --- Queue (thread-safe, built-in locking) ---
q = queue.Queue(maxsize=0)           # also LifoQueue, PriorityQueue
q.put(item, block=True, timeout=None); q.get(); q.get_nowait()
q.task_done(); q.join(); q.qsize()   # raises queue.Empty / queue.Full

# --- Executor / Future ---
with ThreadPoolExecutor(max_workers=4) as ex:
    fut = ex.submit(fn, arg)         # returns Future
    fut.result(timeout=None); fut.done(); fut.cancel(); fut.exception()
    results = list(ex.map(fn, items))            # ordered
    for f in as_completed([ex.submit(fn, i) for i in items]):  # completion order
        print(f.result())

# --- multiprocessing ---
from multiprocessing import Process, Pool, Queue as MPQueue, Value, Manager
with ProcessPoolExecutor() as ex: list(ex.map(cpu_fn, items))

# --- asyncio ---
import asyncio
async def main():
    r = await asyncio.gather(coro1(), coro2())
    task = asyncio.create_task(coro())
    async with asyncio.Semaphore(5): ...
    await asyncio.sleep(1)
    await asyncio.wait_for(coro(), timeout=2)
    q = asyncio.Queue()
asyncio.run(main())
```

**Which primitive?**

| Need | Use |
| --- | --- |
| Mutual exclusion | `Lock` |
| Wait until condition true | `Condition` |
| One-time signal / gate | `Event` |
| Limit concurrency / ordered handoff | `Semaphore` |
| N threads meet at a point | `Barrier` |
| Pass work between threads | `queue.Queue` |
| Run tasks, get results | `ThreadPoolExecutor` |

---

## 2. Classic problems with solutions

### 2.1 Race condition and fix (warm-up)

```python
import threading
counter = 0
lock = threading.Lock()

def inc(n):
    global counter
    for _ in range(n):
        with lock:
            counter += 1

ts = [threading.Thread(target=inc, args=(100_000,)) for _ in range(4)]
[t.start() for t in ts]; [t.join() for t in ts]
print(counter)  # 400000
```

### 2.2 Producer–Consumer (Queue)

```python
import threading, queue
q = queue.Queue(maxsize=5)
SENTINEL = object()

def producer(n):
    for i in range(n):
        q.put(i)                 # blocks when full
    q.put(SENTINEL)

def consumer():
    while True:
        item = q.get()
        if item is SENTINEL:
            q.put(SENTINEL)      # let other consumers stop too
            break
        print("got", item)

threading.Thread(target=producer, args=(10,)).start()
cs = [threading.Thread(target=consumer) for _ in range(2)]
[c.start() for c in cs]; [c.join() for c in cs]
```

### 2.3 Bounded Blocking Queue (LeetCode 1188, Condition)

```python
import threading
from collections import deque

class BoundedBlockingQueue:
    def __init__(self, capacity):
        self.cap, self.dq = capacity, deque()
        self.cv = threading.Condition()

    def enqueue(self, x):
        with self.cv:
            self.cv.wait_for(lambda: len(self.dq) < self.cap)
            self.dq.append(x)
            self.cv.notify_all()

    def dequeue(self):
        with self.cv:
            self.cv.wait_for(lambda: self.dq)
            x = self.dq.popleft()
            self.cv.notify_all()
            return x

    def size(self):
        with self.cv:
            return len(self.dq)
```

### 2.4 Print in Order (LeetCode 1114, Event)

```python
import threading
class Foo:
    def __init__(self):
        self.e1, self.e2 = threading.Event(), threading.Event()
    def first(self, printFirst):
        printFirst(); self.e1.set()
    def second(self, printSecond):
        self.e1.wait(); printSecond(); self.e2.set()
    def third(self, printThird):
        self.e2.wait(); printThird()
```

### 2.5 Print FooBar Alternately (LeetCode 1115, Semaphore)

```python
import threading
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

### 2.6 Zero Even Odd (LeetCode 1116) -> 010203...

```python
import threading
class ZeroEvenOdd:
    def __init__(self, n):
        self.n = n
        self.z = threading.Semaphore(1)
        self.o = threading.Semaphore(0)
        self.e = threading.Semaphore(0)
    def zero(self, printNumber):
        for i in range(1, self.n + 1):
            self.z.acquire(); printNumber(0)
            (self.o if i % 2 else self.e).release()
    def odd(self, printNumber):
        for i in range(1, self.n + 1, 2):
            self.o.acquire(); printNumber(i); self.z.release()
    def even(self, printNumber):
        for i in range(2, self.n + 1, 2):
            self.e.acquire(); printNumber(i); self.z.release()
```

### 2.7 Multithreaded FizzBuzz (LeetCode 1195, Condition)

```python
import threading
class FizzBuzz:
    def __init__(self, n):
        self.n, self.i = n, 1
        self.cv = threading.Condition()
    def _run(self, cond, out):
        while True:
            with self.cv:
                self.cv.wait_for(lambda: self.i > self.n or cond(self.i))
                if self.i > self.n:
                    return
                out(self.i); self.i += 1
                self.cv.notify_all()
    def fizz(self, f):   self._run(lambda i: i % 3 == 0 and i % 5 != 0, lambda i: f())
    def buzz(self, f):   self._run(lambda i: i % 5 == 0 and i % 3 != 0, lambda i: f())
    def fizzbuzz(self, f): self._run(lambda i: i % 15 == 0, lambda i: f())
    def number(self, f): self._run(lambda i: i % 3 and i % 5, f)
```

### 2.8 Building H2O (LeetCode 1117, Barrier + Semaphore)

```python
import threading
class H2O:
    def __init__(self):
        self.h = threading.Semaphore(2)
        self.o = threading.Semaphore(1)
        self.bar = threading.Barrier(3)
    def hydrogen(self, releaseHydrogen):
        self.h.acquire(); self.bar.wait()
        releaseHydrogen(); self.h.release()
    def oxygen(self, releaseOxygen):
        self.o.acquire(); self.bar.wait()
        releaseOxygen(); self.o.release()
```

(The barrier resets after 3 threads; each group is exactly 2H + 1O.)

### 2.9 Dining Philosophers (LeetCode 1226, ordered locks)

```python
import threading
class DiningPhilosophers:
    def __init__(self):
        self.forks = [threading.Lock() for _ in range(5)]
    def wantsToEat(self, p, pickLeft, pickRight, eat, putLeft, putRight):
        l, r = p, (p + 1) % 5
        first, second = sorted((l, r))        # global lock ordering, no deadlock
        with self.forks[first], self.forks[second]:
            pickLeft(); pickRight(); eat(); putLeft(); putRight()
```

Alternatives: allow at most 4 philosophers at once (`Semaphore(4)`), or odd/even asymmetric pickup.

### 2.10 Deadlock demo and fix

```python
a, b = threading.Lock(), threading.Lock()
# BAD: T1 takes a->b, T2 takes b->a
# FIX 1: always acquire in same order (a then b)
# FIX 2: timeout + back off
def safe(l1, l2):
    while True:
        if l1.acquire(timeout=0.1):
            if l2.acquire(timeout=0.1):
                try: return  # critical section
                finally: l2.release(); l1.release()
            l1.release()
        time.sleep(0.01)
```

### 2.11 Thread-safe Singleton (double-checked locking)

```python
import threading
class Singleton:
    _inst, _lock = None, threading.Lock()
    def __new__(cls):
        if cls._inst is None:
            with cls._lock:
                if cls._inst is None:
                    cls._inst = super().__new__(cls)
        return cls._inst
```

### 2.12 Readers–Writers Lock (writer-preference)

```python
import threading
class RWLock:
    def __init__(self):
        self.cv = threading.Condition()
        self.readers = 0
        self.writer = False
        self.writers_waiting = 0
    def acquire_read(self):
        with self.cv:
            self.cv.wait_for(lambda: not self.writer and self.writers_waiting == 0)
            self.readers += 1
    def release_read(self):
        with self.cv:
            self.readers -= 1
            if self.readers == 0: self.cv.notify_all()
    def acquire_write(self):
        with self.cv:
            self.writers_waiting += 1
            self.cv.wait_for(lambda: not self.writer and self.readers == 0)
            self.writers_waiting -= 1
            self.writer = True
    def release_write(self):
        with self.cv:
            self.writer = False
            self.cv.notify_all()
```

### 2.13 Custom Thread Pool

```python
import threading, queue
from concurrent.futures import Future

class ThreadPool:
    def __init__(self, n):
        self.q = queue.Queue()
        self.workers = [threading.Thread(target=self._work, daemon=True) for _ in range(n)]
        for w in self.workers: w.start()
    def _work(self):
        while True:
            task = self.q.get()
            if task is None:
                return
            fn, args, fut = task
            try:
                fut.set_result(fn(*args))
            except Exception as e:
                fut.set_exception(e)
    def submit(self, fn, *args):
        fut = Future(); self.q.put((fn, args, fut)); return fut
    def shutdown(self):
        for _ in self.workers: self.q.put(None)
        for w in self.workers: w.join()
```

### 2.14 Rate Limiter (thread-safe token bucket)

```python
import threading, time
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

### 2.15 Thread-safe LRU Cache

```python
import threading
from collections import OrderedDict
class LRUCache:
    def __init__(self, cap):
        self.cap, self.d, self.lock = cap, OrderedDict(), threading.Lock()
    def get(self, k):
        with self.lock:
            if k not in self.d: return -1
            self.d.move_to_end(k); return self.d[k]
    def put(self, k, v):
        with self.lock:
            self.d[k] = v; self.d.move_to_end(k)
            if len(self.d) > self.cap: self.d.popitem(last=False)
```

### 2.16 Countdown Latch

```python
import threading
class CountDownLatch:
    def __init__(self, n):
        self.n, self.cv = n, threading.Condition()
    def count_down(self):
        with self.cv:
            self.n -= 1
            if self.n <= 0: self.cv.notify_all()
    def wait(self):
        with self.cv:
            self.cv.wait_for(lambda: self.n <= 0)
```

### 2.17 Multithreaded Web Crawler (LeetCode 1242)

```python
import threading
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

def crawl(startUrl, htmlParser):
    host = urlparse(startUrl).hostname
    seen, lock = {startUrl}, threading.Lock()
    def visit(url):
        nxt = []
        for u in htmlParser.getUrls(url):
            if urlparse(u).hostname == host:
                with lock:
                    if u in seen: continue
                    seen.add(u)
                nxt.append(u)
        return nxt
    with ThreadPoolExecutor(max_workers=8) as ex:
        frontier = [startUrl]
        while frontier:                       # BFS level by level
            results = list(ex.map(visit, frontier))
            frontier = [u for r in results for u in r]
    return list(seen)
```

### 2.18 Parallel download / map with Executor

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
def fetch(url): ...
with ThreadPoolExecutor(max_workers=10) as ex:
    futs = {ex.submit(fetch, u): u for u in urls}
    for f in as_completed(futs):
        try: print(futs[f], f.result(timeout=5))
        except Exception as e: print(futs[f], "failed:", e)
```

### 2.19 Parallel sum / merge sort pattern (divide and conquer)

```python
from concurrent.futures import ThreadPoolExecutor
def parallel_sum(nums, k=4):
    size = (len(nums) + k - 1) // k
    chunks = [nums[i:i+size] for i in range(0, len(nums), size)]
    with ThreadPoolExecutor(k) as ex:
        return sum(ex.map(sum, chunks))
# CPU-bound? swap in ProcessPoolExecutor (and guard with if __name__ == "__main__":)
```

### 2.20 Pipeline (stages connected by queues)

```python
import threading, queue
def stage(fn, q_in, q_out):
    while (x := q_in.get()) is not None:
        q_out.put(fn(x))
    q_out.put(None)

q1, q2, q3 = queue.Queue(), queue.Queue(), queue.Queue()
threading.Thread(target=stage, args=(lambda x: x + 1, q1, q2)).start()
threading.Thread(target=stage, args=(lambda x: x * 2, q2, q3)).start()
for i in range(5): q1.put(i)
q1.put(None)
while (r := q3.get()) is not None: print(r)
```

### 2.21 Async: bounded concurrency with asyncio

```python
import asyncio
async def worker(i, sem):
    async with sem:
        await asyncio.sleep(0.1)
        return i * i

async def main():
    sem = asyncio.Semaphore(3)
    print(await asyncio.gather(*(worker(i, sem) for i in range(10))))
asyncio.run(main())
```

### 2.22 Async producer-consumer

```python
import asyncio
async def prod(q):
    for i in range(5): await q.put(i)
    await q.put(None)
async def cons(q):
    while (x := await q.get()) is not None: print(x)
async def main():
    q = asyncio.Queue(maxsize=2)
    await asyncio.gather(prod(q), cons(q))
asyncio.run(main())
```

---

## 3. Common follow-up questions (short answers)

- **Lock vs RLock?** RLock can be re-acquired by the owning thread; Lock deadlocks if you do that.
- **Lock vs Semaphore?** Lock = one owner; Semaphore = counter, any thread can release.
- **Why `while` around `wait()`?** Spurious wakeups and another thread may consume the condition first. `wait_for` handles it.
- **`notify` vs `notify_all`?** Use `notify_all` when waiters have different predicates (safer).
- **Threads vs processes vs asyncio?** Threads: blocking I/O with simple code. Processes: CPU-bound, true parallelism, no shared memory. Asyncio: many thousands of I/O tasks, cooperative, single thread.
- **Is `dict`/`list.append` thread-safe?** Individual ops are atomic under the GIL, but compound ops (check-then-act, `+=`) are not. Use a lock.
- **Starvation / livelock?** Starvation: a thread never gets the resource (fix: fair queues/ordering). Livelock: threads keep reacting without progress (fix: randomized backoff).
- **How to stop a thread?** Cooperative: shared `Event` or sentinel on the queue. Python cannot kill threads safely.
- **Avoiding deadlock?** Lock ordering, timeouts, hold fewer locks, use higher-level structures (`Queue`).
- **Testing tips:** add `time.sleep` to widen race windows, run many iterations, use `threading.excepthook` to catch worker exceptions.