'''
Give a pool of resources, implement get and put request
to manage n resources with multi threaded environment

'''

from queue import Queue
from threading import Condition, Lock

class ResourcePrioritization:
    def __init__(self, n):
        self.n = n
        self.q = Queue()
        self.cv = Condition()
        self.lock = Lock()

    def get(self, m):
        with self.lock:
            while self.q.qsize() < m:
                self.cv.wait()
            
            count = 0
            resources = []
            while count < m:
                resources.append(self.q.get())
                self.count += 1
            
            self.cv.notify_all()
            return resources
    
    def put(self, m, resources):
        with self.lock:
            while self.q.qsize() >= self.n - m:
                self.cv.wait()
            
            count = 0
            while count < m:
                self.q.put(resources[count])
                self.count += 1
            
            self.cv.notify()
            return
    
                
'''
With resource management, the get request will have one more paramenter which is priority and this priority is unique
The higher the priority, the higher the number
'''
import heapq
    self.max_heap = []

    def get(self, m, priority):
        with self.lock:
            while not self.max_heap or self.max_heap[0] != priority or self.q.qsize() < m:
                self.cv.wait()
            
            heapq.heappush(self.max_heap, -priority)

            count = 0
            resources = []
            while count < m:
                resources.append(self.q.get())
                self.count += 1
            
            self.cv.notify_all()

            heapq.heappop(self.max_heap)
            return resources