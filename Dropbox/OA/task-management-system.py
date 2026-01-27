'''
https://aonecode.com/iq/docs/antropic/online-assessment/task-management-system

Level 1
Implement a simple task management system that handles tasks with CRUD operations.

addTask(taskId: String, priority: Int) -> Boolean: Adds a task. Returns false if the taskId already exists; otherwise, returns true.
updateTask(taskId: String, newPriority: Int) -> Boolean: Updates the priority of an existing task. Returns false if the task is not found.
getTask(taskId: String) -> Task | null: Returns the task details.
Examples
addTask("task1", 10); 
addTask("task1", 20); 
updateTask("task2", 5);
getTask("task1");
Explanations

returns true because "task1" is new.
returns false because "task1" already exists.
returns false because "task2" was never added.
returns 10, the current priority of "task1".
Level 2
Implement Search and Sorting functions based on task priority.

searchTasks(minP: Int, maxP: Int) -> List<String>: Returns a list of taskIds where minP <= priority <= maxP.
Sorting Requirement: Results must be sorted by priority (descending).
Tie-breaking: If priorities are equal, sort by creation order (descending)—meaning the task added most recently appears first.

Examples
addTask("task1", 10); 
addTask("task2", 20); 
addTask("task3", 20); 
addTask("task4", 5);
searchTasks(10, 25);
Explanations

returns ["task3", "task2", "task1"] because:
- "task3" and "task2" both have priority 20, but "task3" was created after "task2".
- "task1" has priority 10, which is inside the range [10, 25].
- "task4" is excluded (priority 5 is too low).
Level 3
Introduce user ownership, time-sensitive expiration, and resource limits.

addUser(userId: String, quota: Int) -> Boolean: Registers a user with a maximum number of active tasks. Returns false if the userId already exists.

assignTask(taskId: String, userId: String, priority: Int, ttl: Int, timestamp: Int) -> Boolean:

Checks if the user exists and has not exceeded their quota.

Calculates expiration: Task expires at timestamp + ttl.

Returns false if the user is at quota, the user doesn't exist, or the taskId already exists.

Note: Before processing, the system must expire any tasks whose timestamp + ttl <= current_timestamp.

Examples
addUser("user1", 1);
assignTask("task1", "user1", 10, 5, 100); 
assignTask("task2", "user1", 20, 5, 102); 
assignTask("task2", "user1", 20, 5, 105);
Explanations

returns true. "user1" is created with a quota of 1.
returns true. "task1" assigned at T=100 (expires T=105). Quota is 1/1.
returns false. At T=102, "task1" is still active. User1 is at quota.
returns true. At T=105, "task1" expires (100+5 <= 105). Quota becomes 0/1, allowing "task2" to be added.
Level 4
Track the lifecycle of tasks to differentiate between successful completion and expiration.

completeTask(taskId: String, finishTime: Int) -> Boolean: Marks a task as "Completed." Returns false if the task does not exist, has already expired (based on finishTime), or was already completed. If successful, the user’s active task count decreases, freeing up quota.

getOverdueTasks() -> List<String>: Returns a list of taskIds that transitioned to an "Expired" state without being completed.

Examples
addUser("user2", 2);
assignTask("task_A", "user2", 10, 10, 200); 
assignTask("task_B", "user2", 10, 10, 205); 
completeTask("task_A", 208); 
completeTask("task_B", 220); 
getOverdueTasks();
Explanations

returns true. "user2" created.
returns true. "task_A" expires at 210.
returns true. "task_B" expires at 215.
returns true. Finish time 208 is before expiry 210. Task is completed.
returns false. Finish time 220 is after expiry 215. Task is already expired.
returns ["task_B"] because "task_B" expired at T=215 without being completed.




======================= TASK MANAGEMENT SYSTEM ======================
1. The "Creation Order" Tie-breaker
In Level 2, when priorities are equal, you must return the task added most recently. Using a simple self.creation_counter += 1 
whenever any task is added (via addTask or assignTask) gives you a unique, incrementing ID that represents time. 
Sorting by -creation_order ensures the "newest" comes first.

2. Lazy Expiration
The prompt says: Before processing, the system must expire any tasks whose timestamp + ttl <= current_timestamp. 
I implemented this as _cleanup_expired(timestamp). You must call this at the start of assignTask and completeTask. 
If you don't, a user might be blocked by a task that should have expired one second ago.

3. Transition Logic (Level 4)
A task can only be "Completed" if it hasn't already "Expired."

If finishTime >= expiryTime, the task is already overdue.

Once a task is is_expired, it can never be is_completed, and vice-versa.

Both states must decrement the user's active count to free up their quota.

4. The getTask nuance
In most CodeSignal assessments of this type, getTask should only return info for tasks that are currently "valid." 
If a task has expired, it is effectively removed from the active system, 
so returning None is safer unless the prompt explicitly asks for historical data.
'''

import bisect

class Task:
    def __init__(self, task_id, priority, creation_order, user_id=None, expiry_time=None):
        self.task_id = task_id
        self.priority = priority
        self.creation_order = creation_order
        self.user_id = user_id
        self.expiry_time = expiry_time
        self.is_completed = False
        self.is_expired = False

class TaskManager:
    def __init__(self):
        self.tasks = {}           # taskId -> Task object
        self.users = {}           # userId -> quota_limit
        self.user_active_count = {} # userId -> current_active_tasks
        self.creation_counter = 0
        self.overdue_tasks = []

    def _cleanup_expired(self, current_time):
        """Helper to expire tasks across the system based on current timestamp."""
        for task_id, task in self.tasks.items():
            if not task.is_completed and not task.is_expired:
                if task.expiry_time is not None and task.expiry_time <= current_time:
                    task.is_expired = True
                    self.overdue_tasks.append(task_id)
                    if task.user_id:
                        self.user_active_count[task.user_id] -= 1

    # --- Level 1 ---
    def addTask(self, taskId, priority):
        if taskId in self.tasks:
            return False
        self.creation_counter += 1
        self.tasks[taskId] = Task(taskId, priority, self.creation_counter)
        return True

    def updateTask(self, taskId, newPriority):
        if taskId not in self.tasks or self.tasks[taskId].is_expired:
            return False
        self.tasks[taskId].priority = newPriority
        return True

    def getTask(self, taskId):
        task = self.tasks.get(taskId)
        if not task or task.is_expired: return None
        return task.priority

    # --- Level 2 ---
    def searchTasks(self, minP, maxP):
        # Filter active, non-completed tasks within priority range
        valid_tasks = [t for t in self.tasks.values() 
                       if minP <= t.priority <= maxP and not t.is_completed and not t.is_expired]
        
        # Sort: Priority (desc), then Creation Order (desc)
        valid_tasks.sort(key=lambda x: (-x.priority, -x.creation_order))
        return [t.task_id for t in valid_tasks]

    # --- Level 3 ---
    def addUser(self, userId, quota):
        if userId in self.users:
            return False
        self.users[userId] = quota
        self.user_active_count[userId] = 0
        return True

    def assignTask(self, taskId, userId, priority, ttl, timestamp):
        # Step 1: Invalidate expired tasks first
        self._cleanup_expired(timestamp)
        
        if userId not in self.users or taskId in self.tasks:
            return False
        
        if self.user_active_count[userId] >= self.users[userId]:
            return False
        
        self.creation_counter += 1
        expiry = timestamp + ttl
        new_task = Task(taskId, priority, self.creation_counter, userId, expiry)
        
        self.tasks[taskId] = new_task
        self.user_active_count[userId] += 1
        return True

    # --- Level 4 ---
    def completeTask(self, taskId, finishTime):
        # Run cleanup up to the finishTime
        self._cleanup_expired(finishTime)
        
        task = self.tasks.get(taskId)
        if not task or task.is_completed or task.is_expired:
            return False
        
        task.is_completed = True
        if task.user_id:
            self.user_active_count[task.user_id] -= 1
        return True

    def getOverdueTasks(self):
        return self.overdue_tasks