# https://chatgpt.com/s/t_6ac3351be6e48191a315ee092b6b51a9

import threading

# Thread
t = threading.Thread(target=worker, args=(arg,))
t.start()
t.join()

# Lock
lock = threading.Lock()

with lock:
    # critical section
    shared_state += 1

# Condition variable
cv = threading.Condition()

with cv:
    while not ready:
        cv.wait()
    # consume state
    cv.notify()
    # or cv.notify_all()

# Semaphore
sem = threading.Semaphore(3)

with sem:
    # at most 3 threads here

# Event
event = threading.Event()

event.set()       # signal
event.clear()     # reset
event.wait()      # block until set

# Barrier
barrier = threading.Barrier(3)

barrier.wait()    # all 3 threads must arrive

"""
Rule of thumb:

Lock → protect shared state

Condition → wait for a state/predicate

Semaphore → limit concurrent access

Event → one-way signal

Barrier → everyone meets before continuing
"""