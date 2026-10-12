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
