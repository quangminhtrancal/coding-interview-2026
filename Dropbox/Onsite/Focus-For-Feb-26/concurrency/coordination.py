'''
Wait/notify is a low-level primitive for thread coordination that is useful to know, 
but is unlikely to be used directly in an interview. 
If you're looking to "cut to the chase," feel free to skip this section and jump to Blocking Queues.

Python's threading.Condition combines a lock and condition variable. 
The "with" statement handles lock acquisition. wait() releases the lock and sleeps. 
"notify_all()" wakes all waiting threads. The lock is reacquired before wait() returns.

The while loop is essential. When a thread wakes from wait(), 
it must recheck the condition because another thread might have already consumed 
what it was waiting for between when this thread was notified and when it reacquired the lock. 
The JVM can also wake threads spuriously without any notify() call, 
so you always need to verify the condition still holds.

'''
import threading

condition = threading.Confition()

with condition:
    while not condition_is_met():
        condition.wait() # releases the lock and waits
    
    do_work()
    condition.notify_all() # wakes up waiting threads

'''
Blocking queues also appear in resource pooling (see Scarcity article) where they 
store actual resource objects instead of tasks. Here we focus on their role 
as a communication channel between threads—coordinating work handoff.

Python's queue.Queue provides blocking operations. put() blocks if the queue is full, 
get() blocks if empty. Use maxsize to bound the queue. 
The queue handles all thread synchronization internally.
'''

import queue
from typing import Callable

class TaskScheduler:
    def __init__(self):
        self._queue = queue.Queue(maxsize=1000)

    def submit_task(self, task: Callable) -> None:
        self._queue.put(task)  # Blocks if queue is full

    def worker_loop(self) -> None:
        while True:
            task = self._queue.get()  # Blocks if queue is empty
            task()

'''
Actor model is another concurrency paradigm that uses message passing
'''

import threading
import queue
from abc import ABC, abstractmethod

class Actor(ABC):
    def __init__(self):
        self.mailbox = queue.Queue()
        self.running = True
        self.thread = threading.Thread(target=self._run)
        self.thread.start()

    def _run(self):
        while self.running:
            try:
                message = self.mailbox.get(timeout=0.1)
                self.on_receive(message)
            except queue.Empty:
                continue

    def send(self, message):
        self.mailbox.put(message)

    @abstractmethod
    def on_receive(self, message):
        pass

    def stop(self):
        self.running = False
        self.thread.join()

class EmailActor(Actor):
    def __init__(self):
        super().__init__()
        self.email_client = EmailClient()

    def on_receive(self, request):
        self.email_client.send(request.to, request.subject, request.body)


# Usage: no shared state, no locks needed
class SignupHandler:
    def __init__(self, user_repository):
        self.email_actor = EmailActor()
        self.user_repository = user_repository

    def handle_signup(self, request):
        user = self.user_repository.save(User(request.email))

        # Send message to actor - returns immediately
        self.email_actor.send(EmailRequest(
            to=user.email,
            subject="Welcome!",
            body="Thanks for signing up..."
        ))
