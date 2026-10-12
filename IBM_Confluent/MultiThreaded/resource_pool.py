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
