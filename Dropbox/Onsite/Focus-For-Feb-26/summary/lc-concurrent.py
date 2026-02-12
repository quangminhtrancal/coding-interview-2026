# Web Crawler
from concurrent import futures

class Solution:
    def get_hostname(self, url: str) -> str:
        return url.split('/')[2]

    def crawl(self, startUrl: str, htmlParser: 'HtmlParser') -> List[str]:
        seen = { startUrl }

        with futures.ThreadPoolExecutor(max_workers=5) as executor:
            tasks = { executor.submit(htmlParser.getUrls, startUrl) }

            while tasks:
                # get results as they complete
                for curr_task in futures.as_completed(tasks):
                    tasks.remove(curr_task)
                    retrieved_urls = curr_task.result()

                    for child_url in retrieved_urls:
                        # append seen and chain if necessary
                        if child_url not in seen and self.get_hostname(child_url) == self.get_hostname(startUrl):
                            seen.add(child_url)
                            tasks.add(executor.submit(htmlParser.getUrls, child_url))

        return list(seen)

# Gemini solution
import threading
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED

class Solution:
    def crawl(self, startUrl: str, htmlParser: 'HtmlParser') -> List[str]:
        def get_host_name(url):
            return url.split('/')[2]
        # 1. Extract the hostname to stay within bounds
        hostname = get_host_name(startUrl)
        
        # 2. Use a set to track visited URLs and a lock to make it thread-safe
        visited = {startUrl}
        visited_lock = threading.Lock()


        
        def get_links(url):
            # Fetch all URLs from the current page
            links = htmlParser.getUrls(url)
            new_links = []
            
            for link in links:
                # Only process if it has the same hostname
                if get_host_name(link) == hostname:
                    with visited_lock:
                        if link not in visited:
                            visited.add(link)
                            new_links.append(link)
            return new_links

        # 3. Use a ThreadPoolExecutor to manage the crawling
        with ThreadPoolExecutor(max_workers=10) as executor:
            # We use a list of "futures" (tasks being worked on)
            tasks = {executor.submit(get_links, startUrl)}
            
            while tasks:
                # done is a set of futures that have finished
                done, _ = wait(tasks, return_when=FIRST_COMPLETED)
                
                for future in done:
                    tasks.remove(future)
                    # For every new link found by a finished thread, 
                    # start a new task in the thread pool
                    for new_link in future.result():
                        tasks.add(executor.submit(get_links, new_link))
        
        return list(visited)    
    

# Dining philosophor
# 
import threading

class DiningPhilosophers:
    def __init__(self):
        # One lock for each fork
        self.forks = [threading.Lock() for _ in range(5)]

    def wantsToEat(self,
                   philosopher: int,
                   pickLeftFork: 'Callable[[], None]',
                   pickRightFork: 'Callable[[], None]',
                   eat: 'Callable[[], None]',
                   putLeftFork: 'Callable[[], None]',
                   putRightFork: 'Callable[[], None]') -> None:
        
        # Determine fork indices
        left_fork_id = philosopher
        right_fork_id = (philosopher + 1) % 5
        
        # To prevent deadlock:
        # Philosopher 0 will pick up the right fork FIRST.
        # All others pick up the left fork FIRST.
        if philosopher == 0:
            first, second = self.forks[right_fork_id], self.forks[left_fork_id]
        else:
            first, second = self.forks[left_fork_id], self.forks[right_fork_id]
            
        # The eating process
        with first:
            with second:
                # The requirements state we must call these in order
                # However, the physical picking must happen while holding the locks
                if philosopher == 0:
                    pickRightFork()
                    pickLeftFork()
                else:
                    pickLeftFork()
                    pickRightFork()
                
                eat()
                
                # Putting them back
                if philosopher == 0:
                    putLeftFork()
                    putRightFork()
                else:
                    putRightFork()
                    putLeftFork()    


# print alternate foo bar

from threading import Semaphore

class FooBar:
    def __init__(self, n):
        self.n = n
        self.f_sem = Semaphore(1) # Foo starts "Unlocked"
        self.b_sem = Semaphore(0) # Bar starts "Locked"

    def foo(self, printFoo):
        for _ in range(self.n):
            self.f_sem.acquire()
            printFoo()
            self.b_sem.release()

    def bar(self, printBar):
        for _ in range(self.n):
            self.b_sem.acquire()
            printBar()
            self.f_sem.release()

# other using event

from threading import Event

class FooBar:
    def __init__(self, n):
        self.n = n
        self.f_ev, self.b_ev = Event(), Event()
        self.f_ev.set() # Allow Foo to go first

    def foo(self, printFoo):
        for _ in range(self.n):
            self.f_ev.wait()
            self.f_ev.clear()
            printFoo()
            self.b_ev.set()

    def bar(self, printBar):
        for _ in range(self.n):
            self.b_ev.wait()
            self.b_ev.clear()
            printBar()
            self.f_ev.set()

# other using condition
from threading import Condition

class FooBar:
    def __init__(self, n):
        self.n = n
        self.cv = Condition()
        self.foo_turn = True

    def foo(self, printFoo):
        for _ in range(self.n):
            with self.cv:
                while not self.foo_turn:
                    self.cv.wait()
                printFoo()
                self.foo_turn = False
                self.cv.notify()

    def bar(self, printBar):
        for _ in range(self.n):
            with self.cv:
                while self.foo_turn:
                    self.cv.wait()
                printBar()
                self.foo_turn = True
                self.cv.notify()            


#### Print zero odd even
from threading import Semaphore

class ZeroEvenOdd:
    def __init__(self, n):
        self.n = n
        # Semaphores for each thread
        self.z_sem = Semaphore(1) # Zero goes first
        self.e_sem = Semaphore(0) # Even waits
        self.o_sem = Semaphore(0) # Odd waits

    def zero(self, printNumber: 'Callable[[int], None]') -> None:
        for i in range(1, self.n + 1):
            self.z_sem.acquire()
            printNumber(0)
            # If the NEXT number is odd, release odd gate
            # If the NEXT number is even, release even gate
            if i % 2 == 1:
                self.o_sem.release()
            else:
                self.e_sem.release()

    def even(self, printNumber: 'Callable[[int], None]') -> None:
        for i in range(2, self.n + 1, 2):
            self.e_sem.acquire()
            printNumber(i)
            self.z_sem.release() # Always go back to Zero

    def odd(self, printNumber: 'Callable[[int], None]') -> None:
        for i in range(1, self.n + 1, 2):
            self.o_sem.acquire()
            printNumber(i)
            self.z_sem.release() # Always go back to Zero

# H2O

from threading import Semaphore

class H2O:
    def __init__(self):
        self.h_sem = Semaphore(2) # Allow two H threads to enter
        self.o_sem = Semaphore(0) # Oxygen starts locked
        self.h_count = 0          # Track which H we are on
        self.mutex = Semaphore(1) # Protect the counter

    def hydrogen(self, releaseHydrogen: 'Callable[[], None]') -> None:
        self.h_sem.acquire()      # Limit to 2 H atoms
        releaseHydrogen()
        
        with self.mutex:
            self.h_count += 1
            if self.h_count == 2:
                self.o_sem.release() # After 2 H's, wake up Oxygen

    def oxygen(self, releaseOxygen: 'Callable[[], None]') -> None:
        self.o_sem.acquire()      # Wait for the 2 H's to finish
        releaseOxygen()
        
        with self.mutex:
            self.h_count = 0      # Reset counter
        self.h_sem.release()      # Allow 2 more H's to enter
        self.h_sem.release()

# - or useing Thread Barrier
import threading

class H2O:
    def __init__(self):
        # We allow 2 Hydrogen threads to pass at a time
        self.h_sem = threading.Semaphore(2)
        # We allow 1 Oxygen thread to pass at a time
        self.o_sem = threading.Semaphore(1)
        # The barrier waits for exactly 3 threads (2H + 1O) before releasing them
        self.barrier = threading.Barrier(3)

    def hydrogen(self, releaseHydrogen: 'Callable[[], None]') -> None:
        # 1. Wait for a spot in the H pool
        with self.h_sem:
            # 2. Wait at the barrier for 2 H's and 1 O to arrive
            self.barrier.wait()
            # 3. Form the molecule
            releaseHydrogen()

    def oxygen(self, releaseOxygen: 'Callable[[], None]') -> None:
        # 1. Wait for a spot in the O pool
        with self.o_sem:
            # 2. Wait at the barrier for 2 H's and 1 O to arrive
            self.barrier.wait()
            # 3. Form the molecule
            releaseOxygen()
        

### Print fizzbuzz

from threading import Semaphore

class FizzBuzz:
    def __init__(self, n: int):
        self.n = n
        self.f_sem = Semaphore(0)
        self.b_sem = Semaphore(0)
        self.fb_sem = Semaphore(0)
        self.num_sem = Semaphore(1) # Start with the Number thread

    # Helper to decide who goes next
    def release_next(self, i):
        if i > self.n:
            return
        if i % 3 == 0 and i % 5 == 0:
            self.fb_sem.release()
        elif i % 3 == 0:
            self.f_sem.release()
        elif i % 5 == 0:
            self.b_sem.release()
        else:
            self.num_sem.release()

    def fizz(self, printFizz):
        for i in range(1, self.n + 1):
            if i % 3 == 0 and i % 5 != 0:
                self.f_sem.acquire()
                printFizz()
                self.release_next(i + 1)

    def buzz(self, printBuzz):
        for i in range(1, self.n + 1):
            if i % 5 == 0 and i % 3 != 0:
                self.b_sem.acquire()
                printBuzz()
                self.release_next(i + 1)

    def fizzbuzz(self, printFizzBuzz):
        for i in range(1, self.n + 1):
            if i % 15 == 0:
                self.fb_sem.acquire()
                printFizzBuzz()
                self.release_next(i + 1)

    def number(self, printNumber):
        for i in range(1, self.n + 1):
            if i % 3 != 0 and i % 5 != 0:
                self.num_sem.acquire()
                printNumber(i) # Must pass i here
                self.release_next(i + 1)    

# using Condition
import threading

class FizzBuzz:
    def __init__(self, n: int):
        self.n = n
        self.i = 1
        self.cv = threading.Condition()

    # Thread for multiples of 3 AND 5
    def fizzbuzz(self, printFizzBuzz: 'Callable[[], None]') -> None:
        while True:
            with self.cv:
                while self.i <= self.n and not (self.i % 3 == 0 and self.i % 5 == 0):
                    self.cv.wait()

                if self.i > self.n: return

                printFizzBuzz()
                self.i += 1
                self.cv.notify_all()

    # Thread for multiples of 3 ONLY
    def fizz(self, printFizz: 'Callable[[], None]') -> None:
        while True:
            with self.cv:
                while self.i <= self.n and not (self.i % 3 == 0 and self.i % 5 != 0):
                    self.cv.wait()

                if self.i > self.n: 
                    return
                
                printFizz()
                self.i += 1
                self.cv.notify_all()

    # Thread for multiples of 5 ONLY
    def buzz(self, printBuzz: 'Callable[[], None]') -> None:
        while True:
            with self.cv:
                while self.i <= self.n and not (self.i % 3 != 0 and self.i % 5 == 0):
                    self.cv.wait()

                if self.i > self.n: 
                    return
                
                printBuzz()
                self.i += 1
                self.cv.notify_all()

    # Thread for numbers that are NOT multiples of 3 or 5
    def number(self, printNumber: 'Callable[[int], None]') -> None:
        while True:
            with self.cv:
                while self.i <= self.n and not (self.i % 3 != 0 and self.i % 5 != 0):
                    self.cv.wait()

                if self.i > self.n: 
                    return
                
                printNumber(self.i)
                self.i += 1
                self.cv.notify_all()


'''
Bounded locking queue
'''

import threading
from collections import deque

class BoundedBlockingQueue:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.queue = deque()
        
        # We use a single lock to protect the internal deque
        self.lock = threading.Lock()
        
        # Condition for when the queue is NOT EMPTY (used by dequeue)
        self.not_empty = threading.Condition(self.lock)
        
        # Condition for when the queue is NOT FULL (used by enqueue)
        self.not_full = threading.Condition(self.lock)

    def enqueue(self, element: int) -> None:
        # 'with self.not_full' is shorthand for acquiring the lock
        with self.not_full:
            # While the queue is at capacity, wait for a 'not_full' signal
            while len(self.queue) == self.capacity:
                self.not_full.wait()
            
            self.queue.append(element)
            
            # Since we just added an item, wake up threads waiting to dequeue
            self.not_empty.notify()

    def dequeue(self) -> int:
        # 'with self.not_empty' uses the same lock as not_full
        with self.not_empty:
            # While the queue is empty, wait for a 'not_empty' signal
            while len(self.queue) == 0:
                self.not_empty.wait()
            
            element = self.queue.popleft()
            
            # Since we just removed an item, wake up threads waiting to enqueue
            self.not_full.notify()
            
            return element

    def size(self) -> int:
        with self.lock:
            return len(self.queue)

# the queue class in python is thread safe
import queue
class BoundedBlockingQueue(object):
    def __init__(self, capacity: int):
        self.q = queue.Queue()
        self.cap = capacity
        

    def enqueue(self, element: int) -> None:
        self.q.put(element)
        

    def dequeue(self) -> int:
        return self.q.get()

    def size(self) -> int:
        return self.q.qsize()

'''
# Key-Value transactions + multi-threaded issues similar to token buckets 

The Prompt: "Implement a is_allowed(user_id) function that rate-limits users using a Token Bucket algorithm. 
It must be highly performant under thousands of concurrent requests."

Key Concurrency Issues:
The "Double-Refill" Race: Two threads check the last_refill_time simultaneously. 
Both see that 1 second has passed. Both add 10 tokens. You just gave the user 20 tokens instead of 10.

Drift: If you use a background "refiller" thread, it’s expensive. A senior dev uses Lazy Refilling.

The Implementation (Pythonic/Thread-Safe):
Instead of a background thread, calculate tokens "on the fly" when a request arrives.

'''

import threading
import time

class TokenBucket:
    def __init__(self, capacity, fill_rate):
        self.capacity = capacity
        self.fill_rate = fill_rate  # tokens per second
        self.tokens = capacity
        self.last_refill = time.time()
        self.lock = threading.Lock()

    def allow_request(self, tokens_needed=1):
        with self.lock:
            now = time.time()
            # 1. Lazy Refill: Calculate tokens earned since last check
            passed = now - self.last_refill
            self.tokens = min(self.capacity, self.tokens + (passed * self.fill_rate))
            self.last_refill = now

            # 2. Check and Consume
            if self.tokens >= tokens_needed:
                self.tokens -= tokens_needed
                return True
            return False        

'''
Coding 2: Key-value store, requiring at least read-committed operation. 
However, the question stated a single-threaded environment with concurrent transactions.  
https://leetcode.com/discuss/post/279913/bloomberg-onsite-key-value-store-with-tr-kcrv/

'''
class KVStore:
    def __init__(self):
        # The main data storage (the "Global" state)
        self.storage = {}
        # A stack to track nested transactions
        # Each element is a dict representing changes in that transaction level
        self.stack = []

    def set(self, key, value):
        if self.stack:
            # Update the current (most recent) transaction layer
            self.stack[-1][key] = value
        else:
            # No active transaction, update global storage
            self.storage[key] = value

    def get(self, key):
        # Check from newest transaction down to global storage
        # First, look through the transaction stack in reverse (most recent first)
        for layer in reversed(self.stack):
            if key in layer:
                return layer[key]
        
        # If not found in any transaction, check global storage
        return self.storage.get(key)

    def delete(self, key):
        if self.stack:
            # In a transaction, "Delete" is handled by setting value to None
            # or a specific tombstone object.
            self.stack[-1][key] = None
        else:
            if key in self.storage:
                del self.storage[key]

    def begin(self):
        # Start a new transaction layer
        self.stack.append({})

    def commit(self):
        if not self.stack:
            raise Exception("No active transaction to commit.")
        
        # Pop the top layer and merge it into the layer below
        # If it's the last layer, merge it into global storage
        completed_layer = self.stack.pop()
        
        if self.stack:
            self.stack[-1].update(completed_layer)
        else:
            # Apply changes to global storage
            for k, v in completed_layer.items():
                if v is None:
                    self.storage.pop(k, None)
                else:
                    self.storage[k] = v

    def rollback(self):
        if not self.stack:
            raise Exception("No active transaction to rollback.")
        # Simply discard the latest transaction layer
        self.stack.pop()


    '''
    Bloomberg | Onsite | Key Value Store with transactions

Implement (code) a Key value store with transactions.

Write a Fully funcitonal code in 25-30 min in interview with test cases

Set
Get
Delete are methods in Key value store

for transactions
Begin
Commit
Rollback

Ideas are welcome,

https://www.reddit.com/r/ExperiencedDevs/comments/16o0i1p/asked_to_implemented_windowed_key_value_store_for/

Was asked to implement a windowed key value store (with an “expiry window”) say keys are only valid for 1 hour. The apis to implement are

put(String key, long value)

get(String key) //return -1 if value doesn’t exist or expired

getAverage()

The getAverage is the tricky part, needed to make it as fast as possible (as close to O(1) as we can get)

I fumbled around a bit then use a HashMap which stored <key:String, value: TimedValue> where I defined TimedValue class to just be a wrapper for the long value and the timestamp. Used a doubly LinkedList in conjunction with the HashMap that also stored references to the TimedValue objects so we can find the oldest element in O(1) by accessing the tail of the list.

On insertion, I checked if value already exists, remove it from the LinkedList, and then insert the new value at the head of the list. On retrieval, just got the value from the HashMap, check if timestamp is still valid given the window and currentTimeStamp.

For average, I suggested removing from the tail in a while loop as long as tail is invalid (removing the expired values that are old to be included in our window) then obtaining the average of the remaining items that are still in our window.

Interviewer asked how to make getAverage faster, I suggested caching the average value (maintaining a sum and count of the items in our window) and we can return the cached value if the tail isn’t expired at the time of retrieval - I see how this was wrong because I needed to also update the cached average on insertion. A further improvement I mentioned was to update that cached average value on insertion and retrieval, by updating the average with the newly inserted value and removing the expired values from the tail of the list.

This morning I got an email that they will be proceeding with other candidates. I’m really upset as I really wanted that position. What could I have done better, what’s a better way to implement this? And generally how did you personally gain the technical knowledge to come up with that better solution. Is it from leetcode design questions or doing data structures and algos course? Book? Just curious.
    '''