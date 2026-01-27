'''
https://www.reddit.com/r/leetcode/comments/1i0jygq/codesignals_storage_system_design/

The ideia was create a file storage, first level, you have to just create a simple storage in an array, with name and size, 
and override methods addFile, deleteFile and getNTopSize files...
I don't remember exactly what is the second and third level, but the idea is creating some kind of structure by user, using the previous one. 
So, you have to modify a lot of things in order to work the new features


Level 1: Basic Key-Value Storage

Goal: Implement basic set and get operations for a file storage system.

Logic: You typically use a HashMap to store file IDs and their content.

Level 2: Versioning / Snapshotting

Goal: Add the ability to "snapshot" the system or retrieve a version of a file at a specific timestamp.

Logic: You have to modify your data structure to store a list of values (or a TreeMap) for each key, indexed by time.

Level 3: TTL (Time to Live) and Expiration

Goal: Implement a setWithTTL method where files expire after a certain duration.

Logic: You need to check the current timestamp against the expiration time during every get operation and potentially manage a cleanup process.

Level 4: Advanced Filtering and Atomic Transactions

Goal: Perform bulk operations (like copy_directory or delete_expired) or complex filtering (e.g., 
"return all files larger than X MB that were created by user Y").

Logic: Requires efficient indexing. Candidates often discussed whether to use multiple maps to keep time complexity low.

================================

=============== below from Gemeni guess ===================
The CodeSignal assessment you are looking for is known as the "Industry Coding Framework" (sometimes called the "CodeSignal Practice Industry Coding" or "Software Engineering Framework").

This specific problem is commonly referred to in developer communities as the "Cloud Storage System" or "File Storage Design" task.

Where to find it
The most accurate breakdown and practice resources for this specific CodeSignal question can be found at:

GitHub Practice Repositories:

Search for "PaulLockett/CodeSignal_Practice_Industry_Coding_Framework" on GitHub. This repository contains a detailed simulation of the file storage example, including levels 1 through 4, with logic for addFile, deleteFile, and getNTopSize.

Search for "amshrestha2020/CodeSignal" which includes solutions for "Company Challenges" that match this progressive design pattern.

Community Discussion Boards:

Reddit (r/leetcode & r/csMajors): Search for "CodeSignal Industry Coding Framework" or "CodeSignal Cloud Storage Level 4". Recent threads (from late 2024 and 2025) discuss the exact logic you mentioned, specifically how Level 4 requires "scheduling" or "atomic transactions" which often break if not implemented with a helper method to process a queue first.

DEV Community: There is a detailed guide titled "Persona OA Ultimate Guide! Codesignal 90-Minute 4-Question Full Breakdown" that covers this exact storage system design.

Summary of the Task Levels
Based on the framework you described, here is the roadmap typically used in this OA:

Level 1: Basic storage. Methods: addFile(name, size), deleteFile(name), and getNTopSize(n) (returning the largest files).

Level 2: Attribute filtering. Adding user_id or prefixes to the files. 
You often have to return files based on which user owns them or filter names by a prefix.

Level 3: Capacity and Quotas. Implementing addUser(user_id, capacity) and ensuring addFile fails if the user's storage limit is exceeded.

Level 4: Advanced/Atomic Operations. This often involves copying directories, moving files, or scheduling. 
As you noted, the "hidden tests" usually fail if you don't ensure that any pending/scheduled operations are processed 
before the current method executes.

Recommended Next Step
Would you like me to refine the Python code I provided earlier to specifically include the getNTopSize logic and the 
"Process Queue" helper for Level 4?


=======================

Build Cloud storage system - 4 tasks expanding on this - first one was create a cloud file storage in memory, 
keep track of who owns which file, the filename and location, implement functions i.e. addFile, removeFile and in later stages changeOwnership, 
assignCapacity, updateCapacity, copyFile, deleteFile - 
there was one more function I believe to find a file by prefix and / or suffix if it exists ;
 Additionally, some calculations about file sizes, i.e. if user with the next action would go over his cloud capacity return false 
 and if user is deleting file lower his used capacity etc.

 =====================

 The coding challenge timed online and about working with a filesystem. 
 It contained problems like getting filenames that matched the given prefix and sorting it by a given frequency and then alphabetically.

'''

from bisect import bisect_right

class FileMetadata:
    def __init__(self, user=None, size=0):
        self.user = user
        self.size = size

    def __repr__(self):
        return f"FileMetadata(user={self.user}, size={self.size})"

class StorageSystem:
    def __init__(self):
        # Level 1 & 2: { file_id: [[timestamp, value], ...] }
        self.storage = {} 
        # Level 3: { file_id: expiration_timestamp }
        self.ttls = {}
        # Level 4: Metadata for filtering { file_id: FileMetadata }
        self.metadata = {}

    def _is_expired(self, file_id, current_time):
        """Helper to check if a file has passed its TTL."""
        if file_id in self.ttls and current_time >= self.ttls[file_id]:
            return True
        return False

    # Level 1: Basic Set/Get
    # Level 2: Versioning (using timestamp)
    def set_file(self, file_id, value, timestamp, user_id=None, size=0):
        if file_id not in self.storage:
            self.storage[file_id] = []
        self.storage[file_id].append([timestamp, value])
        # Level 4: Metadata indexing
        self.metadata[file_id] = FileMetadata(user_id, size)
        # If a file is re-set, we typically clear old TTL unless specified
        if file_id in self.ttls:
            del self.ttls[file_id]
        return "OK"

    def get_file(self, file_id, current_time, version_ts=None):
        """
        Level 1: Basic Get
        Level 2: Get version at/before version_ts
        Level 3: Check TTL
        """
        if file_id not in self.storage or self._is_expired(file_id, current_time):
            return None

        versions = self.storage[file_id]
        # If no version_ts requested, use current_time
        target_ts = version_ts if version_ts is not None else current_time
        
        # Binary search to find the latest version <= target_ts
        idx = bisect_right(versions, [target_ts, float('inf')]) - 1
        if idx >= 0:
            return versions[idx][1]
        return None

    # Level 3: TTL
    def set_with_ttl(self, file_id, value, timestamp, ttl, user_id=None, size=0):
        self.set_file(file_id, value, timestamp, user_id, size)
        self.ttls[file_id] = timestamp + ttl
        return "OK"

    # Level 4: Advanced Filtering
    def filter_files(self, current_time, min_size=0, user_id=None):
        """Returns file IDs matching criteria that haven't expired."""
        results = []
        for file_id in self.storage:
            if self._is_expired(file_id, current_time):
                continue
            meta = self.metadata.get(file_id, FileMetadata())
            size_match = meta.size >= min_size
            user_match = (user_id is None) or (meta.user == user_id)
            if size_match and user_match:
                results.append(file_id)
        return sorted(results)

    def delete_expired(self, current_time):
        """Level 4: Atomic/Bulk Cleanup"""
        expired_keys = [fid for fid in self.ttls if current_time >= self.ttls[fid]]
        for fid in expired_keys:
            del self.storage[fid]
            del self.ttls[fid]
            del self.metadata[fid]
        return len(expired_keys)


def run_tests():
    fs = StorageSystem()

    print("--- Level 1: Basic Ops ---")
    fs.set_file("doc1", "content_v1", timestamp=10)
    print(f"Get doc1 at T15: {fs.get_file('doc1', 15)}") # content_v1

    print("\n--- Level 2: Versioning ---")
    fs.set_file("doc1", "content_v2", timestamp=20)
    print(f"Get doc1 current (T25): {fs.get_file('doc1', 25)}") # content_v2
    print(f"Get doc1 at T15 (Old Version): {fs.get_file('doc1', 25, version_ts=15)}") # content_v1

    print("\n--- Level 3: TTL ---")
    # Set doc2 with 5 second TTL (expires at T35)
    fs.set_with_ttl("doc2", "temp_data", timestamp=30, ttl=5)
    print(f"Get doc2 at T32: {fs.get_file('doc2', 32)}") # temp_data
    print(f"Get doc2 at T36: {fs.get_file('doc2', 36)}") # None (expired)

    print("\n--- Level 4: Filtering & Bulk ---")
    fs.set_file("big_file", "...", timestamp=40, user_id="Alice", size=500)
    fs.set_file("small_file", ".", timestamp=40, user_id="Bob", size=10)
    fs.set_file("alice_small", ".", timestamp=40, user_id="Alice", size=5)
    
    # Filter: Alice's files >= 10MB
    alice_files = fs.filter_files(current_time=45, min_size=10, user_id="Alice")
    print(f"Alice's files >= 10MB: {alice_files}") # ['big_file']
    
    # Bulk Delete Expired
    # doc2 expired at T35. Calling at T45 should remove it.
    deleted_count = fs.delete_expired(45)
    print(f"Deleted {deleted_count} expired files.") # 1
    print(f"doc2 in storage: {'doc2' in fs.storage}") # False



#=============== Below from Gemeni guess ===================
import heapq

class CloudStorage:
    def __init__(self):
        # file_id -> {'size': int, 'user_id': str, 'created_at': int}
        self.files = {}
        # user_id -> {'capacity': int, 'used': int}
        self.users = {}
        # List of (execute_at, task_type, data)
        self.scheduled_tasks = []

    # --- Level 4 Helper: The "Secret" to passing hidden tests ---
    def _process_pending_tasks(self, current_time):
        """Processes all scheduled tasks that should have happened by current_time."""
        # Use a min-heap for scheduled_tasks for O(log N) efficiency
        while self.scheduled_tasks and self.scheduled_tasks[0][0] <= current_time:
            timestamp, task_type, data = heapq.heappop(self.scheduled_tasks)
            if task_type == "MOVE_FILE":
                self._execute_move(data['file_id'], data['to_user'], timestamp)

    # --- Level 1: Basic Storage ---
    def add_file(self, file_id, size, timestamp, user_id="admin"):
        self._process_pending_tasks(timestamp)
        
        # Level 3: Check User Capacity
        if user_id in self.users:
            if self.users[user_id]['used'] + size > self.users[user_id]['capacity']:
                return "ERROR: OVER_CAPACITY"
        
        if file_id in self.files:
            return "ERROR: FILE_EXISTS"
            
        self.files[file_id] = {'size': size, 'user_id': user_id}
        if user_id in self.users:
            self.users[user_id]['used'] += size
        return "OK"

    def delete_file(self, file_id, timestamp):
        self._process_pending_tasks(timestamp)
        if file_id not in self.files:
            return "ERROR: NOT_FOUND"
        
        file_info = self.files.pop(file_id)
        u_id = file_info['user_id']
        if u_id in self.users:
            self.users[u_id]['used'] -= file_info['size']
        return "OK"

    def get_n_top_size(self, n, timestamp):
        self._process_pending_tasks(timestamp)
        # Sort by size descending, then file_id ascending (lexicographical)
        sorted_files = sorted(
            self.files.items(), 
            key=lambda x: (-x[1]['size'], x[0])
        )
        return [f[0] for f in sorted_files[:n]]

    # --- Level 2 & 3: User Management ---
    def add_user(self, user_id, capacity, timestamp):
        self._process_pending_tasks(timestamp)
        if user_id in self.users:
            return "ERROR: USER_EXISTS"
        self.users[user_id] = {'capacity': capacity, 'used': 0}
        return "OK"

    # --- Level 4: Scheduling & Atomic Operations ---
    def schedule_move(self, file_id, to_user, execute_at, current_time):
        self._process_pending_tasks(current_time)
        if file_id not in self.files:
            return "ERROR: NOT_FOUND"
        
        # We don't move it yet, we just queue it
        heapq.heappush(self.scheduled_tasks, (execute_at, "MOVE_FILE", {
            'file_id': file_id, 
            'to_user': to_user
        }))
        return "OK"

    def _execute_move(self, file_id, to_user, timestamp):
        """Actual logic for moving ownership and checking capacity at time of execution."""
        if file_id not in self.files or to_user not in self.users:
            return
        
        file_info = self.files[file_id]
        from_user = file_info['user_id']
        
        # Check if destination has room
        if self.users[to_user]['used'] + file_info['size'] <= self.users[to_user]['capacity']:
            self.users[from_user]['used'] -= file_info['size']
            self.users[to_user]['used'] += file_info['size']
            file_info['user_id'] = to_user










if __name__ == "__main__":
    run_tests()