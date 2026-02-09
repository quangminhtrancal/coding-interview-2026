import threading

lock = threading.Lock()
counter = 0

with lock:
    counter += 1
    print(f"Counter value: {counter}")

# Semaphore example:
permits = threading.Semaphore(3)
permits.acquire()

try:
    counter += 1
    print(f"Counter value with semaphore: {counter}")
finally:
    permits.release()


# Condition example:
condition = threading.Condition()

with condition:
    while not ready:
        condition.wait()
    counter += 1
    print(f"Counter value with condition: {counter}")


# blocking queue
from queue import Queue
q = Queue(maxsize=5)
q.put(task)
t = q.get()


