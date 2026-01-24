'''
https://www.reddit.com/r/leetcode/comments/1i0jygq/codesignals_storage_system_design/

nahh I don’t, level 1-3 were basically the same but 4 was different. 
Mine was that I had create a banking system that stores accounts. 
The first level was creating a create account, transferring money to another account, depositing money. 
The second level was seeing the highest k accounts based on their balances. The 3 was dealing a merge of accounts. 

The 4 was different cuz it dealt with scheduling transfers and making sure in the original methods created, 
any scheduled transfers would happen first(used a helper). I finished it all, besides the last one. I didn’t get all the hidden test passed.


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

Goal: Perform bulk operations (like copy_directory or delete_expired) or complex filtering (e.g., "return all files larger than X MB that were created by user Y").

Logic: Requires efficient indexing. Candidates often discussed whether to use multiple maps to keep time complexity low.

'''

import time
from bisect import bisect_right

class StorageSystem:
    def __init__(self):
        # Level 1 & 2: { file_id: [[timestamp, value], ...] }
        self.storage = {} 
        # Level 3: { file_id: expiration_timestamp }
        self.ttls = {}
        # Level 4: Metadata for filtering { file_id: { 'user': str, 'size': int } }
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
        self.metadata[file_id] = {'user': user_id, 'size': size}
        
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
            
            meta = self.metadata.get(file_id, {})
            size_match = meta.get('size', 0) >= min_size
            user_match = (user_id is None) or (meta.get('user') == user_id)
            
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

if __name__ == "__main__":
    run_tests()