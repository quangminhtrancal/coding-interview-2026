import threading

# coasrse-fine-grained lock example
class TicketBooking:
    def __init__(self):
        self.lock = threading.Lock()
        self.seat_owners = {}
    
    def book_seat(self, seat_id, visitor_id):
        with self.lock:
            if seat_id in self.seat_owners:
                return False  # Seat already booked
            self.seat_owners[seat_id] = visitor_id
            return True  # Booking successful
    
'''
read-write lock example
In interviews, mention read-write locks when the interviewer asks about read-heavy workloads. 
"If reads dominate and writes are rare, I'd use a read-write lock so readers don't block each other.
 But if the ratio is close to 50/50, a simple mutex is usually faster."

'''
class Cache:
    def __init__(self):
        self.lock = threading.RLock()
        self.read_count = 0
        self.read_count_lock = threading.Lock()
        self.data = {}
    
    def get(self, key):
        with self.read_count_locK:
            self.read_count += 1
            if self.read_count == 1:
                self.lock.acquire()
        
        try:
            return self.data.get(key)
        finally:
            with self.read_count_lock:
                self.read_count -= 1
                if self.read_count == 0:
                    self.lock.release()
    
    def put(self, key, value):
        with self.locK:
            self.data[key] = value

# example fine grained lock
class TicketBookingFineGrained:
    def __init__(self):
        self.locks_lock = threading.Lock()
        self.seat_locks = {}
        self.seat_owners = {}
    
    def get_lock(self, seat_id):
        with self.locks_lock:
            if seat_id not in self.seat_locks:
                self.seat_locks[seat_id] = threading.Lock()
            
            return self.seat_locks[seat_id]
    
    def book_seat(self, seat_id, visitor_id):
        with self.get_lock(seat_id):
            if seat_id in self.seat_owners:
                return False
            
            self.seat_owners[seat_id] = visitor_id
            return True
    
    # if swapping, it can cause deadlock since A wait for B and B wait for A
    # to avoid deadlock: acquire lock in consistent order
    def swap_seats(self, seat_id1, seat_id2):
        first_lock, second_lock = (self.get_lock(seat_id1), self.get_lock(seat_id2)) if seat_id1 < seat_id2 else (self.get_lock(seat_id2), self.get_lock(seat_id1))
        
        with first_lock:
            with second_lock:
                owner1 = self.seat_owners.get(seat_id1)
                owner2 = self.seat_owners.get(seat_id2)
                
                if owner1 is None or owner2 is None:
                    return False
                
                self.seat_owners[seat_id1], self.seat_owners[seat_id2] = owner2, owner1
                return True

'''
atomic counter example
Python's Global Interpreter Lock (GIL) doesn't make operations atomic, 
and Python lacks built-in atomic primitives. The example uses a threading.Lock 
to simulate atomic behavior. For true lock-free atomics, you'd need a library like atomics 
or use multiprocessing.Value with its built-in lock.
'''

class BookingStats:
    def __init__(self):
        self.lock = threading.Lock()
        self.book_count = 0
    
    def increment_successful_bookings(self):
        with self.lock:
            self.book_count += 1
    
    def get_successful_bookings(self):
        with self.lock:
            return self.book_count

'''
For more complex updates, you'll use a CAS loop. 
CAS: Compare-And-Swap is a low-level atomic operation that updates a value

Say you want to track the maximum number of concurrent bookings ever seen. 
You can't just set the value since another thread might have already set it higher. 
Instead, you read the current value, compute what you want to set, and attempt the CAS. 
If it fails (because another thread changed it), you loop and try again with the new value:

'''        
class ConcurrencyTracker:
    def __init__(self):
        self.lock = threading.Lock()
        self.max_concurrent = 0
    
    def update_max_concurrent(self, current):
        while True:
            with self.lock:
                if current <= self.max_concurrent:
                    return
                self.max_concurrent = current
                return

'''
Rate limiter: check and update the count atomically

'''

import threading

class RateLimiter:
    def __init__(self):
        self._lock = threading.Lock()
        self._request_counts = {}
        self._max_requests = 100

    def allow_request(self, user_id: str) -> bool:
        with self._lock:
            count = self._request_counts.get(user_id, 0)
            if count < self._max_requests:
                self._request_counts[user_id] = count + 1
                return True
            return False

#  Lock for general read-modify-write scenarios
import threading

class BankAccount:
    def __init__(self):
        self._lock = threading.Lock()
        self._balance = 0

    def deposit(self, amount: int):
        with self._lock:
            self._balance = self._balance + amount

    def withdraw(self, amount: int):
        with self._lock:
            self._balance = self._balance - amount


'''
When you see arithmetic on shared state (incrementing counters, updating balances, 
accumulating totals), ask yourself: "What happens if two threads do this at the same time?" 
If the answer is "one update gets lost," you need synchronization.

For a single variable, say: "I'll use an atomic integer since the increment operation is atomic." 
For multiple fields, say: "I'll use a lock so the read and write happen together."
'''