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
