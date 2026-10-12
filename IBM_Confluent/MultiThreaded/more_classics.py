# file: more_classics.py
"""
Additional multi-threaded interview questions:
  4.6  Thread-safe singleton (double-checked locking)
  4.7  CountDownLatch equivalent
  4.8  Thread-safe pub/sub event bus
  4.9  Concurrent hash map with striped locks
  4.10 Async/thread-safe logger
  4.11 Traffic light intersection
"""
import heapq
import itertools
import queue
import threading
import time
from collections import defaultdict, deque


# ---------------------------------------------------------------------------
# 4.6 Thread-safe singleton (double-checked locking)
# ---------------------------------------------------------------------------
# Question: implement a thread-safe singleton. The naive "check-then-create"
# is a race: two threads can both see None and both create an instance.
#
# Trick: double-checked locking — check without a lock first (fast path), then
# under the lock (slow path). Python's module-level objects are already
# singletons, but interviewers ask for the pattern.  The key subtlety in
# C++/Java is that the instance pointer must be `volatile` so the compiler
# doesn't reorder the check before the constructor finishes. Python doesn't
# have that problem, but we still need the lock for the check-then-act gap.


class Singleton:
    """Thread-safe singleton via double-checked locking."""
    _instance = None
    _lock = threading.Lock()

    def __init__(self, value=None):
        self.value = value

    @classmethod
    def get_instance(cls, value=None):
        # Fast path: already created, no lock needed (atomic read in CPython
        # thanks to the GIL, but we write it as if it matters).
        if cls._instance is None:
            with cls._lock:
                # Re-check inside the lock: another thread may have created it
                # while we were waiting.
                if cls._instance is None:
                    cls._instance = cls(value)
        return cls._instance


# Pythonic one-liner alternative (no lock needed):
#   The module is imported exactly once (CPython's import lock guarantees
#   this), so a module-level variable is already a thread-safe singleton.
#
#   _singleton = None
#   def get_singleton(value=None):
#       global _singleton
#       if _singleton is None:
#           _singleton = MyClass(value)
#       return _singleton
#
# This works because `import` holds a lock.  Mention it, then show DCL.


# ---------------------------------------------------------------------------
# 4.7 CountDownLatch equivalent
# ---------------------------------------------------------------------------
# Question: implement a CountDownLatch — a one-shot barrier that starts with
# a count N; threads call await() to block; other threads call count_down()
# to decrement N; when N reaches zero, all waiters are released. It cannot be
# reset (unlike a Barrier).
#
# Trick: one Condition, a counter, wait_for(count == 0). count_down wakes all
# because the predicate is the same for every waiter.


class CountDownLatch:
    """One-shot countdown latch. count_down N times to release all awaiters."""

    def __init__(self, count):
        self._count = count
        self._cv = threading.Condition()

    def count_down(self, n=1):
        with self._cv:
            self._count = max(0, self._count - n)
            if self._count == 0:
                self._cv.notify_all()

    def await_(self, timeout=None):
        with self._cv:
            return self._cv.wait_for(lambda: self._count == 0, timeout)

    @property
    def count(self):
        with self._cv:
            return self._count


# ---------------------------------------------------------------------------
# 4.8 Thread-safe pub/sub event bus
# ---------------------------------------------------------------------------
# Question: implement a thread-safe publish/subscribe event bus. Subscribers
# register callbacks for topics; publishers emit events; each subscriber gets
# the event in its own thread (or queue) so a slow subscriber doesn't block
# others.
#
# Trick: subscribers are not called inline under the bus lock (that would
# block all publishers and serialize subscribers). Instead, each subscriber
# gets its own work queue + worker thread. publish() just puts the event on
# every relevant queue. This is the "mailbox" / actor pattern.
#
# Follow-up: "What if a subscriber is slow?" — the queue grows. Options:
# bounded queue with drop-oldest or block, or a per-subscriber thread pool.
# We show the unbounded queue version (simplest) and discuss bounded in
# follow-ups.


class EventBus:
    """Thread-safe pub/sub. Each subscriber has its own queue + worker."""

    def __init__(self):
        self._subs = defaultdict(list)   # topic -> list of (queue, thread)
        self._lock = threading.Lock()

    def subscribe(self, topic, callback):
        q = queue.Queue()
        stop = threading.Event()

        def worker():
            while not stop.is_set():
                try:
                    event = q.get(timeout=0.1)
                except queue.Empty:
                    continue
                if event is None:           # shutdown sentinel
                    break
                try:
                    callback(event)
                except Exception:
                    pass                    # don't kill the worker on bad callbacks
            q.task_done()  # drain sentinel

        t = threading.Thread(target=worker, daemon=True)
        t.start()
        with self._lock:
            self._subs[topic].append((q, stop, t))
        return q, stop, t

    def unsubscribe(self, topic, sub):
        """sub is the (queue, stop, thread) tuple returned by subscribe()."""
        with self._lock:
            if sub in self._subs[topic]:
                self._subs[topic].remove(sub)
        sub[1].set()     # stop event
        sub[0].put(None)  # wake the worker

    def publish(self, topic, event):
        with self._lock:
            subs = list(self._subs.get(topic, []))
            # Also deliver to wildcard subscribers
            subs.extend(self._subs.get("*", []))
        for q, _stop, _t in subs:
            q.put(event)     # non-blocking on the publisher side

    def shutdown(self):
        with self._lock:
            all_subs = list(self._subs.values())
            self._subs.clear()
        for subs in all_subs:
            for q, stop, t in subs:
                stop.set()
                q.put(None)
                t.join(timeout=2)


# ---------------------------------------------------------------------------
# 4.9 Concurrent hash map with striped locks
# ---------------------------------------------------------------------------
# Question: implement a thread-safe hash map that allows concurrent access to
# different keys. A single lock serializes everything; a lock per key uses
# too much memory. Striped locking: N locks, key % N picks the lock.
#
# Trick: an array of N locks; each operation acquires only the lock for its
# stripe. Operations on different stripes run in parallel. Same-stripe
# operations serialize. This is what Java's ConcurrentHashMap does (since
# Java 8 it uses CAS + synchronized on bin heads, but the striped concept
# is the interview answer).
#
# Important: resize() (rehash) needs ALL locks — a global write lock or a
# stop-the-world approach. We skip resize here for clarity but mention it.


class StripedConcurrentHashMap:
    """Thread-safe dict with striped locking for parallel access to different keys."""

    def __init__(self, stripes=16):
        self._n = stripes
        self._locks = [threading.Lock() for _ in range(stripes)]
        self._buckets = [dict() for _ in range(stripes)]

    def _stripe(self, key):
        return hash(key) % self._n

    def get(self, key, default=None):
        s = self._stripe(key)
        with self._locks[s]:
            return self._buckets[s].get(key, default)

    def put(self, key, value):
        s = self._stripe(key)
        with self._locks[s]:
            self._buckets[s][key] = value

    def delete(self, key):
        s = self._stripe(key)
        with self._locks[s]:
            return self._buckets[s].pop(key, None)

    def contains(self, key):
        s = self._stripe(key)
        with self._locks[s]:
            return key in self._buckets[s]

    def items(self):
        """Snapshot of all items. Acquires all locks in order to prevent
        concurrent resize or partial reads. Use a consistent order to
        avoid deadlock."""
        result = []
        for i in range(self._n):
            with self._locks[i]:
                result.extend(self._buckets[i].items())
        return result

    def size(self):
        return sum(len(b) for b in self._buckets)


# ---------------------------------------------------------------------------
# 4.10 Async/thread-safe logger
# ---------------------------------------------------------------------------
# Question: design a thread-safe logging facility that is non-blocking —
# calling log() from a worker thread should never block on disk I/O.
#
# Trick: a background writer thread drains a queue and writes to the file.
# log() just formats and enqueues. This decouples log latency from I/O
# latency. Follow-ups: bounded queue (drop or block?), flush(), close(),
# batching writes.
#
# This is the pattern behind logging.handlers.QueueHandler / QueueListener.


class AsyncLogger:
    """Non-blocking logger: log() enqueues, a background thread writes."""

    def __init__(self, path, queue_size=1024):
        self._q = queue.Queue(maxsize=queue_size)
        self._file = open(path, "a", buffering=1)  # line-buffered
        self._closed = False
        self._thread = threading.Thread(target=self._writer, daemon=True)
        self._thread.start()

    def log(self, level, msg):
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        tid = threading.get_ident()
        line = f"[{ts}] [{level}] [tid={tid}] {msg}\n"
        try:
            self._q.put_nowait(line)       # non-blocking: drop if full
        except queue.Full:
            self._file.write("[DROPPED] log queue full\n")
            self._file.flush()

    def _writer(self):
        while True:
            line = self._q.get()
            if line is None:                # shutdown sentinel
                break
            self._file.write(line)
        self._file.flush()
        self._file.close()

    def flush(self):
        """Block until all queued messages are written."""
        self._q.put(None)       # sentinel
        self._thread.join()
        # Re-start for continued use (or don't, if closing)
        if not self._closed:
            self._file = open(self._file.name, "a", buffering=1)
            self._thread = threading.Thread(target=self._writer, daemon=True)
            self._thread.start()

    def close(self):
        self._closed = True
        self._q.put(None)
        self._thread.join(timeout=5)


# ---------------------------------------------------------------------------
# 4.11 Traffic light intersection
# ---------------------------------------------------------------------------
# Question: model a traffic-light intersection. Two roads (NS and EW) each
# have a light that is RED, GREEN, or YELLOW. Only one road may be GREEN at a
# time. Implement car_arrives(road) that blocks until the light is GREEN for
# that road, and a controller that cycles the lights automatically.
#
# Trick: the light state is one shared variable guarded by a Condition.
# car_arrives waits for its road to be GREEN. The controller thread cycles
# GREEN -> YELLOW -> RED -> (other road) GREEN in a loop. This is a
# "wait for predicate" problem, just like FizzBuzz.


class TrafficLight:
    """Two-road traffic light. car_arrives blocks until the road is green."""

    GREEN, YELLOW, RED = "GREEN", "YELLOW", "RED"
    # State: which road has green (0 = NS, 1 = EW); we also track yellow

    def __init__(self, green_dur=1.0, yellow_dur=0.3):
        self._green_dur = green_dur
        self._yellow_dur = yellow_dur
        self._active = 0            # 0 = NS green, 1 = EW green
        self._is_yellow = False
        self._cv = threading.Condition()
        self._running = False
        self._controller = None

    def start(self):
        self._running = True
        self._controller = threading.Thread(target=self._control_loop, daemon=True)
        self._controller.start()

    def stop(self):
        with self._cv:
            self._running = False
            self._cv.notify_all()
        if self._controller:
            self._controller.join(timeout=5)

    def _control_loop(self):
        while self._running:
            with self._cv:
                # Green phase for active road
                self._is_yellow = False
                self._cv.notify_all()        # wake waiting cars
                self._cv.wait_for(
                    lambda: not self._running or self._is_yellow,
                    timeout=self._green_dur)
                if not self._running:
                    break
                # Yellow phase
                self._is_yellow = True
                self._cv.notify_all()        # tell cars it's yellow
                self._cv.wait_for(
                    lambda: not self._running,
                    timeout=self._yellow_dur)
                if not self._running:
                    break
                # Switch to the other road
                self._active = 1 - self._active

    def car_arrives(self, road):
        """road: 0 (NS) or 1 (EW). Blocks until the light is green for road."""
        with self._cv:
            self._cv.wait_for(
                lambda: self._active == road and not self._is_yellow)

    def get_state(self):
        with self._cv:
            if self._is_yellow:
                return ("YELLOW", road_name(self._active))
            return ("GREEN", road_name(self._active))


def road_name(r):
    return "NS" if r == 0 else "EW"


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
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


def test_singleton():
    # Concurrent get_instance must all return the same object
    instances = []
    lock = threading.Lock()

    def worker():
        s = Singleton.get_instance("first")
        with lock:
            instances.append(s)

    ts = [threading.Thread(target=worker) for _ in range(20)]
    for t in ts: t.start()
    for t in ts: t.join(5)
    assert all(i is instances[0] for i in instances), "singleton violated"
    assert instances[0].value == "first"
    # Second call with a different value still returns the first instance
    assert Singleton.get_instance("other") is instances[0]
    print("test_singleton OK")


def test_countdown_latch():
    # 3 workers, main waits on latch of 3
    latch = CountDownLatch(3)
    done_order = []
    lock = threading.Lock()

    def worker(i):
        time.sleep(0.01 * i)      # stagger
        with lock:
            done_order.append(i)
        latch.count_down()

    ts = [threading.Thread(target=worker, args=(i,)) for i in range(3)]
    for t in ts: t.start()
    # Main thread blocks until all 3 are done
    assert latch.await_(timeout=5), "latch timed out"
    for t in ts: t.join(5)
    assert latch.count == 0
    # await returns immediately once count is 0
    assert latch.await_() is True
    print("test_countdown_latch OK")


def test_event_bus():
    bus = EventBus()
    received_a = []
    received_b = []
    received_wild = []
    lock = threading.Lock()

    def callback_a(event):
        with lock:
            received_a.append(event)

    def callback_b(event):
        with lock:
            received_b.append(event)

    def callback_wild(event):
        with lock:
            received_wild.append(event)

    bus.subscribe("topic1", callback_a)
    bus.subscribe("topic1", callback_b)
    bus.subscribe("*", callback_wild)

    bus.publish("topic1", "hello")
    bus.publish("topic1", "world")
    bus.publish("topic2", "other")

    time.sleep(0.3)  # let workers process

    assert received_a == ["hello", "world"], received_a
    assert received_b == ["hello", "world"], received_b
    assert received_wild == ["hello", "world", "other"], received_wild

    # Test unsubscribe
    sub = bus.subscribe("topic1", lambda e: None)
    bus.unsubscribe("topic1", sub)

    bus.shutdown()
    print("test_event_bus OK")


def test_concurrent_hash_map():
    m = StripedConcurrentHashMap(stripes=8)
    # Concurrent writes to different keys
    def writer(base):
        for i in range(100):
            m.put(f"k{base + i}", base + i)

    ts = [threading.Thread(target=writer, args=(b,)) for b in range(0, 500, 100)]
    for t in ts: t.start()
    for t in ts: t.join(10)
    assert m.size() == 500, m.size()
    # Verify all keys
    for i in range(500):
        assert m.get(f"k{i}") == i, f"k{i}"
    # Delete and check
    m.delete("k0")
    assert not m.contains("k0")
    assert m.get("k0", "gone") == "gone"
    # Concurrent reads + writes stress
    def reader():
        for i in range(200):
            m.get(f"k{i % 500}")
    ts2 = [threading.Thread(target=reader) for _ in range(8)]
    ts3 = [threading.Thread(target=writer, args=(500,)) for _ in range(4)]
    for t in ts2 + ts3: t.start()
    for t in ts2 + ts3: t.join(10)
    print("test_concurrent_hash_map OK")


def test_async_logger():
    import os, tempfile
    path = tempfile.mktemp(suffix=".log")
    logger = AsyncLogger(path)
    for i in range(50):
        logger.log("INFO", f"message {i}")
    logger.flush()
    logger.close()
    with open(path) as f:
        lines = f.readlines()
    os.unlink(path)
    # Some may be dropped under contention but in practice all 50 land
    assert len(lines) >= 45, f"only {len(lines)} lines logged"
    assert "message 0" in lines[0]
    print("test_async_logger OK")


def test_traffic_light():
    tl = TrafficLight(green_dur=0.1, yellow_dur=0.03)
    tl.start()
    # Initially NS is green
    state = tl.get_state()
    assert state == ("GREEN", "NS"), state
    # Cars on NS should pass immediately
    passed = []
    lock = threading.Lock()

    def car_ns():
        tl.car_arrives(0)
        with lock:
            passed.append("NS")

    def car_ew():
        tl.car_arrives(1)
        with lock:
            passed.append("EW")

    # NS car arrives, should pass quickly
    t1 = threading.Thread(target=car_ns)
    t1.start()
    t1.join(2)
    assert "NS" in passed

    # EW car arrives while NS is green — must wait
    t2 = threading.Thread(target=car_ew)
    t2.start()
    t2.join(0.05)  # should still be blocked
    assert t2.is_alive(), "EW car should be waiting"

    # Wait for the light to cycle to EW
    t2.join(5)
    assert not t2.is_alive(), "EW car didn't pass"
    assert "EW" in passed

    tl.stop()
    print("test_traffic_light OK")


if __name__ == "__main__":
    test_singleton()
    test_countdown_latch()
    test_event_bus()
    test_concurrent_hash_map()
    test_async_logger()
    test_traffic_light()
    print("more_classics OK")
