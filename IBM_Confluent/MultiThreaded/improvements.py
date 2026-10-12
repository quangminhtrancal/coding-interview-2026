# file: improvements.py
"""
Improvements to existing sections:
  - Scheduler: cancellation support
  - LRU Cache: TTL expiration
  - Web crawler: async alternative (using Queue + counter termination)
"""
import heapq
import itertools
import queue
import threading
import time
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse


# ---------------------------------------------------------------------------
# Improved Scheduler with cancellation
# ---------------------------------------------------------------------------
class CancellableScheduler:
    """Delayed-task scheduler with cancel(task_id)."""

    def __init__(self):
        self._heap = []
        self._seq = itertools.count()
        self._cv = threading.Condition()
        self._closed = False
        self._cancelled = set()
        self._counter = itertools.count()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def schedule(self, fn, delay):
        with self._cv:
            task_id = next(self._counter)
            heapq.heappush(self._heap,
                           (time.monotonic() + delay, next(self._seq), fn, task_id))
            self._cv.notify()
            return task_id

    def cancel(self, task_id):
        with self._cv:
            self._cancelled.add(task_id)
            self._cv.notify_all()

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
                        self._cv.wait()
                        continue
                    # Skip cancelled tasks at the head
                    while self._heap and self._heap[0][3] in self._cancelled:
                        _, _, _, tid = heapq.heappop(self._heap)
                        self._cancelled.discard(tid)
                    if not self._heap:
                        continue
                    delay = self._heap[0][0] - time.monotonic()
                    if delay <= 0:
                        _, _, fn, tid = heapq.heappop(self._heap)
                        if tid in self._cancelled:
                            self._cancelled.discard(tid)
                            continue
                        break
                    self._cv.wait(delay)
            fn()


# ---------------------------------------------------------------------------
# LRU with TTL expiration
# ---------------------------------------------------------------------------
class TTLCache:
    """LRU cache with per-entry TTL (time-to-live). Entries expire lazily on
    access. A background sweeper (optional) cleans up expired entries to bound
    memory."""

    def __init__(self, capacity, ttl, clock=time.monotonic, sweep_interval=None):
        self._cap = capacity
        self._ttl = ttl
        self._clock = clock
        self._d = OrderedDict()       # key -> (value, expiry_time)
        self._lock = threading.Lock()
        self._sweep_interval = sweep_interval
        self._sweeper = None
        if sweep_interval:
            self._sweeper = threading.Thread(target=self._sweep_loop, daemon=True)
            self._sweeper.start()

    def get(self, key, default=None):
        with self._lock:
            entry = self._d.get(key)
            if entry is None:
                return default
            value, expiry = entry
            if self._clock() >= expiry:
                del self._d[key]
                return default
            self._d.move_to_end(key)
            return value

    def put(self, key, value, ttl=None):
        with self._lock:
            expiry = self._clock() + (ttl if ttl is not None else self._ttl)
            self._d[key] = (value, expiry)
            self._d.move_to_end(key)
            if len(self._d) > self._cap:
                self._d.popitem(last=False)

    def _sweep_loop(self):
        while True:
            time.sleep(self._sweep_interval)
            with self._lock:
                now = self._clock()
                expired = [k for k, (_, exp) in self._d.items() if now >= exp]
                for k in expired:
                    del self._d[k]

    def size(self):
        with self._lock:
            return len(self._d)


# ---------------------------------------------------------------------------
# Web crawler: async alternative (queue + counter termination)
# ---------------------------------------------------------------------------
def crawl_async(startUrl, htmlParser, workers=8):
    """Alternative to the BFS-level crawler: workers pull from a shared queue
    and push new URLs. Termination via a pending-task counter (active workers
    + queued tasks). visited is guarded by a lock.
    """
    host = urlparse(startUrl).hostname
    visited = {startUrl}
    visited_lock = threading.Lock()
    work_queue = queue.Queue()
    work_queue.put(startUrl)
    pending = [1]            # tasks queued or in progress
    pending_lock = threading.Lock()
    done = threading.Event()

    def task_done():
        with pending_lock:
            pending[0] -= 1
            if pending[0] == 0:
                done.set()

    def worker():
        while not done.is_set():
            try:
                url = work_queue.get(timeout=0.05)
            except queue.Empty:
                continue
            try:
                urls = htmlParser.getUrls(url)
                for u in urls:
                    if urlparse(u).hostname == host:
                        with visited_lock:
                            if u not in visited:
                                visited.add(u)
                                work_queue.put(u)
                                with pending_lock:
                                    pending[0] += 1
            finally:
                task_done()

    threads = [threading.Thread(target=worker, daemon=True) for _ in range(workers)]
    for t in threads:
        t.start()
    done.wait(timeout=30)
    for t in threads:
        t.join(timeout=5)
    return list(visited)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def test_cancellable_scheduler():
    s = CancellableScheduler()
    order = []
    lock = threading.Lock()

    def make(msg):
        def fn():
            with lock:
                order.append(msg)
        return fn

    t1 = s.schedule(make("fast"), 0.05)
    t2 = s.schedule(make("cancelled"), 0.10)
    t3 = s.schedule(make("slow"), 0.15)

    s.cancel(t2)
    time.sleep(0.3)
    s.close()

    assert order == ["fast", "slow"], order
    print("test_cancellable_scheduler OK")


def test_ttl_cache():
    now = [0.0]
    c = TTLCache(capacity=3, ttl=2.0, clock=lambda: now[0])

    c.put("a", 1)
    now[0] = 1.0                     # advance 1 second
    c.put("b", 2)                    # b expires 1s later than a
    assert c.get("a") == 1           # still valid (t=1, expiry=2)
    assert c.get("b") == 2

    now[0] = 2.5                     # a expired (expiry=2), b still valid (expiry=3)
    assert c.get("a") is None       # expired
    assert c.get("b") == 2          # b put at t=1, expiry=3, still valid

    now[0] = 3.5                     # b also expired now
    assert c.get("b") is None

    # Test per-entry TTL
    now[0] = 0.0
    c2 = TTLCache(capacity=3, ttl=10, clock=lambda: now[0])
    c2.put("x", 1, ttl=1)    # expires at 1
    c2.put("y", 2, ttl=5)    # expires at 5
    now[0] = 1.5
    assert c2.get("x") is None   # expired
    assert c2.get("y") == 2      # still valid

    # Test LRU eviction still works
    now[0] = 0.0
    c3 = TTLCache(capacity=2, ttl=100, clock=lambda: now[0])
    c3.put("a", 1)
    c3.put("b", 2)
    c3.get("a")                 # touch a
    c3.put("c", 3)              # evict b (LRU)
    assert c3.get("b") is None
    assert c3.get("a") == 1
    assert c3.get("c") == 3

    print("test_ttl_cache OK")


def test_crawl_async():
    class FakeParser:
        def __init__(self, graph):
            self.graph = graph
        def getUrls(self, url):
            time.sleep(0.01)
            return self.graph.get(url, [])

    g = {
        "http://a.com/": ["http://a.com/1", "http://a.com/2", "http://b.com/x"],
        "http://a.com/1": ["http://a.com/3", "http://a.com/"],
        "http://a.com/2": ["http://a.com/3"],
        "http://b.com/x": ["http://a.com/hidden"],
    }
    got = set(crawl_async("http://a.com/", FakeParser(g)))
    assert got == {"http://a.com/", "http://a.com/1",
                   "http://a.com/2", "http://a.com/3"}, got
    print("test_crawl_async OK")


if __name__ == "__main__":
    test_cancellable_scheduler()
    test_ttl_cache()
    test_crawl_async()
    print("improvements OK")
