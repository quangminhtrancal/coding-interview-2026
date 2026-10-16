"""
Two concurrency interview questions, answered in Python.

Q1. Token bucket rate limiter (capacity N, refill R tokens/sec), thread-safe.
Q2. Bounded queue for many producers and consumers; block when full/empty; clean shutdown.

Run this file to execute the tests at the bottom:  python concurrency_answers.py
"""
import threading
import time
from collections import deque


# =============================================================================
# Q1. TOKEN BUCKET
# =============================================================================
"""
IDEA
  * The bucket holds up to `capacity` tokens. Each request takes one token.
  * Refill LAZILY: on each request, add (elapsed_time * rate) tokens, capped at capacity.
    No background thread is needed.
  * Allows bursts up to `capacity`, then a steady rate of `rate` requests/second.

WHY IT IS NOT THREAD-SAFE WITHOUT A LOCK
  allow() is a read-modify-write on `tokens` and `last`. Two threads can both read
  tokens == 1, both decide "enough", and both subtract: 2 requests pass on 1 token.
  Also `last` can be overwritten with a stale value, losing or double-counting refill.

HOW TO MAKE IT THREAD-SAFE
  * One mutex around the whole refill + check + decrement (critical section is tiny: O(1)).
  * Read the clock INSIDE the lock, so `now` is never older than `last`.
  * Use time.monotonic(), not time.time(): wall clocks can jump backwards (NTP).
  * Keep tokens as a float so fractional refills are not lost.

FOLLOW-UPS
  * Many users: one bucket per key in a dict. Creation needs a lock (or use setdefault);
    for very high contention, shard locks by hash(key) % K.
  * Multiple processes/servers: keep (tokens, last) in Redis and do the same
    read-modify-write inside a Lua script so it is atomic.
  * Complexity: O(1) time per call, O(1) space per bucket.
"""


class TokenBucket:
    def __init__(self, capacity, refill_rate, clock=time.monotonic):
        if capacity <= 0 or refill_rate <= 0:
            raise ValueError("capacity and refill_rate must be positive")
        self.capacity = capacity
        self.rate = refill_rate                 # tokens per second
        self.clock = clock                      # injectable, so tests can fake time
        self.tokens = float(capacity)           # start full
        self.last = clock()
        self.lock = threading.Lock()

    def _refill(self, now):
        elapsed = now - self.last
        if elapsed > 0:
            self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
            self.last = now

    def allow(self, n=1):
        """Take n tokens if available. Never blocks. Returns True (allowed) or False (rejected)."""
        with self.lock:
            self._refill(self.clock())          # clock read INSIDE the lock
            if self.tokens >= n:
                self.tokens -= n
                return True
            return False

    def retry_after(self, n=1):
        """Seconds until n tokens will be available (useful for a 429 Retry-After header)."""
        with self.lock:
            self._refill(self.clock())
            missing = n - self.tokens
            return 0.0 if missing <= 0 else missing / self.rate


# =============================================================================
# Q2. BOUNDED BLOCKING QUEUE (many producers, many consumers)
# =============================================================================
"""
IDEA
  * A deque protected by ONE lock, with TWO condition variables on that lock:
        not_full   -> producers wait here while the queue is full
        not_empty  -> consumers wait here while the queue is empty
  * put():  wait while full,  append, notify one consumer.
    get():  wait while empty, pop,    notify one producer.
  * Always wait in a `while` loop, never `if`: after waking, another thread may have
    taken the slot/item (and wakeups can be spurious), so re-check the condition.
  * Wait() releases the lock while sleeping and re-acquires it on wake, so no busy-waiting.

SHUTDOWN (the part interviewers care about)
  Add close(). It sets a `closed` flag and calls notify_all() on BOTH conditions so every
  blocked thread wakes up and re-checks.
    * put() after close      -> raises Closed (no new work accepted).
    * get() after close      -> keeps returning remaining items (DRAIN), then raises Closed
                                once the queue is empty. Consumers use that to exit cleanly.
    * close(drain=False)     -> discard queued items: immediate shutdown.
  Without notify_all() on close, threads blocked in wait() would hang forever.

ALTERNATIVES
  * Poison pill: producers put one sentinel per consumer. Simple, but the sentinel must
    be ordered correctly and needs the consumer count.
  * queue.Queue in the standard library does the blocking part, but has no built-in close
    (use sentinels), and shutdown() only exists in Python 3.13+.
"""


class Closed(Exception):
    """Raised when putting to a closed queue, or getting from a closed and drained queue."""


class BoundedQueue:
    def __init__(self, capacity):
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self.capacity = capacity
        self.items = deque()
        self.closed = False
        self.lock = threading.Lock()
        self.not_full = threading.Condition(self.lock)
        self.not_empty = threading.Condition(self.lock)

    @staticmethod
    def _wait(cond, deadline):
        """Wait on cond. Returns False if the deadline has already passed."""
        if deadline is None:
            cond.wait()
            return True
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return False
        cond.wait(remaining)
        return True

    def put(self, item, timeout=None):
        deadline = None if timeout is None else time.monotonic() + timeout
        with self.lock:
            while len(self.items) >= self.capacity and not self.closed:
                if not self._wait(self.not_full, deadline):
                    raise TimeoutError("queue full")
            if self.closed:
                raise Closed("queue is closed")
            self.items.append(item)
            self.not_empty.notify()             # wake one waiting consumer

    def get(self, timeout=None):
        deadline = None if timeout is None else time.monotonic() + timeout
        with self.lock:
            while not self.items and not self.closed:
                if not self._wait(self.not_empty, deadline):
                    raise TimeoutError("queue empty")
            if not self.items:                  # closed AND drained
                raise Closed("queue is closed and empty")
            item = self.items.popleft()
            self.not_full.notify()              # wake one waiting producer
            return item

    def close(self, drain=True):
        with self.lock:
            self.closed = True
            if not drain:
                self.items.clear()              # immediate shutdown: drop pending work
            self.not_full.notify_all()          # wake ALL blocked producers (they will raise Closed)
            self.not_empty.notify_all()         # wake ALL blocked consumers (they drain, then raise Closed)

    def __len__(self):
        with self.lock:
            return len(self.items)


# =============================================================================
# TESTS
# =============================================================================
def _test_token_bucket():
    now = [0.0]
    tb = TokenBucket(capacity=3, refill_rate=1.0, clock=lambda: now[0])
    assert [tb.allow() for _ in range(4)] == [True, True, True, False]   # burst of 3, then rejected
    assert abs(tb.retry_after() - 1.0) < 1e-9
    now[0] = 2.0                                                          # 2 tokens refilled
    assert tb.allow() and tb.allow() and not tb.allow()
    now[0] = 1000.0                                                       # refill is capped at capacity
    assert [tb.allow() for _ in range(4)] == [True, True, True, False]
    now[0] = 999.0                                                        # clock going backwards: no negative refill
    assert tb.allow() is False

    # Thread safety: 100 threads x 10 requests = 1000 attempts against 50 tokens, no refill
    # (refill_rate is tiny and the test is short), so EXACTLY 50 may pass.
    tb = TokenBucket(capacity=50, refill_rate=1e-6)
    allowed, lock = [], threading.Lock()

    def worker():
        got = sum(tb.allow() for _ in range(10))
        with lock:
            allowed.append(got)

    threads = [threading.Thread(target=worker) for _ in range(100)]
    [t.start() for t in threads]
    [t.join() for t in threads]
    assert sum(allowed) == 50, sum(allowed)

    # Real-time refill: 20 tokens/sec means about 2 tokens after 0.1 s
    tb = TokenBucket(capacity=2, refill_rate=20)
    assert tb.allow() and tb.allow() and not tb.allow()
    time.sleep(0.12)
    assert tb.allow()
    print("token bucket: OK")


def _test_bounded_queue():
    # Basic blocking behaviour with timeouts
    q = BoundedQueue(2)
    q.put(1)
    q.put(2)
    try:
        q.put(3, timeout=0.05)
        assert False
    except TimeoutError:
        pass
    assert q.get() == 1 and q.get() == 2
    try:
        q.get(timeout=0.05)
        assert False
    except TimeoutError:
        pass

    # Many producers, many consumers, graceful shutdown: nothing lost, nothing duplicated
    q = BoundedQueue(5)
    produced = [(p, i) for p in range(4) for i in range(200)]
    consumed, lock = [], threading.Lock()

    def producer(p):
        for i in range(200):
            q.put((p, i))                        # blocks when full

    def consumer():
        while True:
            try:
                item = q.get()                   # blocks when empty
            except Closed:
                return                           # closed and drained: exit cleanly
            with lock:
                consumed.append(item)

    prods = [threading.Thread(target=producer, args=(p,)) for p in range(4)]
    cons = [threading.Thread(target=consumer) for _ in range(3)]
    [t.start() for t in prods + cons]
    [t.join() for t in prods]                    # all producers finished
    q.close()                                    # then close: consumers drain the rest and exit
    [t.join(5) for t in cons]
    assert not any(t.is_alive() for t in cons)
    assert sorted(consumed) == sorted(produced)

    # close() wakes blocked consumers and blocked producers
    q = BoundedQueue(1)
    errors = []

    def blocked_get():
        try:
            q.get()
        except Closed:
            errors.append("get")

    t = threading.Thread(target=blocked_get)
    t.start()
    time.sleep(0.05)
    q.close()
    t.join(2)
    assert errors == ["get"] and not t.is_alive()

    q = BoundedQueue(1)
    q.put("x")

    def blocked_put():
        try:
            q.put("y")
        except Closed:
            errors.append("put")

    t = threading.Thread(target=blocked_put)
    t.start()
    time.sleep(0.05)
    q.close()
    t.join(2)
    assert errors == ["get", "put"] and not t.is_alive()
    assert q.get() == "x"                        # drain: the queued item is still delivered
    try:
        q.get()
        assert False
    except Closed:
        pass
    try:
        q.put("z")
        assert False
    except Closed:
        pass

    # Immediate shutdown discards pending items
    q = BoundedQueue(3)
    q.put(1)
    q.put(2)
    q.close(drain=False)
    try:
        q.get()
        assert False
    except Closed:
        pass
    print("bounded queue: OK")


if __name__ == "__main__":
    _test_token_bucket()
    _test_bounded_queue()
    print("ALL TESTS PASSED")
