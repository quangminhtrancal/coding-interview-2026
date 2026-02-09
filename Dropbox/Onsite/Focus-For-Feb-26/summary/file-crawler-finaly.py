'''
Implement a file crawler that can traverse directories and handle long

https://www.hacktherounds.com/problem/462?company=27

Implement a file crawler that can traverse directories and handle long-running file processing asynchronously.\n\n
**Part 1 - Basic File Listing:**\n
Given a file path, return all files under that path. A helper function `list_dir(path)` is provided.\n\n

**Part 2 - Scaling Discussion (No Code):**\n
Discuss how to scale for very large directory trees.\n\n

**Part 3 - Async Processing:**\nImplement an async job system where each file takes a long time to process.\n\n

**Requirements:**\n- Handle nested directories recursively\n
- Process files concurrently\n
- Track progress and handle failures\n
- Consider memory constraints for large trees\n\n*

*Constraints:**\n- Directory tree can be arbitrarily deep\n

- Individual file processing may take seconds to minutes\n

- Should not block on slow file operations",


************ IMPORTANT NOte SYMLINK => avoid infinite loop


https://prachub.com/companies/dropbox/categories/coding-and-algorithms?sort=hot

You are building a simple file crawler. Task Implement an API function: 
Input:** a filesystem path `rootPath`\n- **Output:** a list/array of **all file paths** 
contained under `rootPath` (recursively), 
in any order.

Assume:- Paths can be directories or files.- 

You are given a helper function similar to:
- `listChildren(path) -> (subdirs, files)` where `subdirs` are immediate child directories and 
`files` are immediate child files.

# Notes / edge cases to clarify in your solution\n- 
If `rootPath` is a file, return just `[rootPath]`.
 Decide what to do if the path does not exist or is not accessible 
 (e.g., throw an error vs return empty).
 Avoid infinite loops if the filesystem can contain symlinks 
 (state your assumption if you ignore symlinks).",
{
    "title": "File Crawler with Async Processing",
    "tags": [ "DFS", "Async", "File System", "Concurrency"],
    "description": "
    "constraints": [
        "Directory tree can be arbitrarily deep",
        "File processing may take seconds to minutes",
        "Should not block on slow operations"
    ],
    "examples": [
        {
            "input": "crawl('/home/user/docs')\\nlist_dir('/home/user/docs') → ['file1.txt', 'subdir/']\\nlist_dir('/home/user/docs/subdir') → ['file2.txt']",
            "output": "['/home/user/docs/file1.txt', '/home/user/docs/subdir/file2.txt']",
            "explanation": "Recursively traverse and collect all files"
        }
    ],
    "starter_code": {
        "python": "import os\nfrom typing import List, Callable\nfrom concurrent.futures import ThreadPoolExecutor, as_completed\nimport asyncio\n\n# Helper function provided in interview\ndef list_dir(path: str) -> List[str]:\n    \"\"\"Returns list of items in directory. Directories end with '/'.\"\"\"\n    # Mock implementation\n    pass\n\ndef crawl_files(root_path: str) -> List[str]:\n    \"\"\"\n    Part 1: Return all files under root_path.\n    \n    Args:\n        root_path: Starting directory path\n    \n    Returns:\n        List of all file paths (not directories)\n    \"\"\"\n    # Your implementation here\n    pass\n\n\n# Part 3: Async processing\nclass AsyncFileCrawler:\n    def __init__(self, max_workers: int = 10):\n        self.max_workers = max_workers\n        self.results = []\n        self.errors = []\n    \n    async def process_file(self, file_path: str) -> dict:\n        \"\"\"Process a single file (simulated long-running operation).\"\"\"\n        # Your implementation here\n        pass\n    \n    async def crawl_and_process(self, root_path: str, \n                                 process_fn: Callable[[str], dict]) -> List[dict]:\n        \"\"\"\n        Crawl directory and process files asynchronously.\n        \n        Args:\n            root_path: Starting directory\n            process_fn: Function to apply to each file\n        \n        Returns:\n            List of processing results\n        \"\"\"\n        # Your implementation here\n        pass\n",
    },
    # ========================================================================
    # Approach 1: Iterative BFS with Queue
    # ========================================================================
    #
    # Intuition: Use a queue-based BFS to traverse the directory tree level
    # by level, which avoids deep recursion issues.
    #
    # Algorithm:
    # 1. Start with root path in queue
    # 2. For each path, check if it's a file or directory
    # 3. If directory, add all children to queue
    # 4. If file, add to results
    # 5. Continue until queue is empty
    #
    # Time Complexity: O(n) where n = total files and directories
    # Space Complexity: O(w) where w = maximum width of tree


    # ========================================================================
    # Approach 2: Recursive DFS with Depth Tracking
    # ========================================================================
    #
    # Intuition: Use recursive DFS which is more intuitive for tree traversal
    # and easier to implement async processing on top of.
    #
    # Algorithm:
    # 1. Base case: if path is a file, return [path]
    # 2. Recursive case: get directory contents
    # 3. Recursively crawl each item
    # 4. Combine all results
    # 5. Track depth for limiting traversal if needed
    #
    # Time Complexity: O(n) where n = total files and directories
    # Space Complexity: O(d) where d = maximum depth of tree (call stack)
'''

### example bfs with os and join path
class BFSFileCrawler:
    """File Crawler using iterative BFS traversal."""

    def __init__(self):
        self.file_system = {
            "/home/user/docs": ["/home/user/docs/file1.txt", "/home/user/docs/subdir/"],
            "/home/user/docs/subdir": ["/home/user/docs/subdir/file2.txt"]
        }

    def list_dir(self, path: str) -> list:
        """List contents of a directory"""
        path = path.rstrip('/')
        return self.file_system.get(path, [])

    def crawl(self, root: str) -> list:
        """Crawl directory tree using BFS. Returns list of all files found."""
        files = []
        queue = [root]

        while queue:
            path = queue.pop(0)

            # Check if it's a directory (ends with / or has contents)
            if path.endswith('/'):
                path = path.rstrip('/')
                contents = self.list_dir(path)
                queue.extend(contents)
            elif path.rstrip('/') in self.file_system:
                contents = self.list_dir(path)
                queue.extend(contents)
            else:
                # It's a file
                files.append(path)

        return files
        
import os
from typing import List, Callable, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import asyncio

# Mock file system for testing
MOCK_FILE_SYSTEM = {
    "/home/user/docs": ["/home/user/docs/file1.txt", "/home/user/docs/subdir/"],
    "/home/user/docs/subdir": ["/home/user/docs/subdir/file2.txt", "/home/user/docs/subdir/nested/"],
    "/home/user/docs/subdir/nested": ["/home/user/docs/subdir/nested/file3.txt"],
    "/empty": [],
    "/single": ["/single/file.txt"]
}

# Helper function provided in interview
def list_dir(path: str) -> List[str]:
    """Returns list of items in directory. Directories end with '/'."""
    path = path.rstrip('/')
    return MOCK_FILE_SYSTEM.get(path, [])


# ============================================================================
# PART 1: Basic File Listing
# ============================================================================

def crawl_files(root_path: str) -> List[str]:
    """
    Part 1: Return all files under root_path using DFS.
    """
    root_path = root_path.rstrip('/')

    # Check if path is a directory
    contents = list_dir(root_path)

    # If no contents, it's a file
    if not contents:
        return [root_path]

    # Otherwise, it's a directory - recursively crawl
    files = []
    for item in contents:
        if item.endswith('/'):
            # It's a directory
            files.extend(crawl_files(item))
        else:
            # It's a file
            files.append(item)

    return files



# ============================================================================
# PART 2: Scaling Discussion
# ============================================================================

"""
PART 2: How to Scale for Very Large Directory Trees

Question: Discuss how to scale this solution for massive directory trees (millions of files).

ANSWER:

1. **Memory Constraints:**
   - Problem: Loading all file paths into memory can exhaust RAM
   - Solution: Use generator/iterator pattern to yield results incrementally
   - Instead of returning List[str], return Iterator[str]

2. **Distributed Processing:**
   - Problem: Single machine can't handle billions of files
   - Solution: Distribute across multiple workers
     * Use message queue (RabbitMQ, Kafka) to distribute directory paths
     * Each worker processes subset of directory tree
     * Coordinator aggregates results

3. **Depth Limits:**
   - Problem: Extremely deep trees can cause stack overflow
   - Solution:
     * Use iterative BFS instead of recursive DFS
     * Set maximum depth limit
     * Use explicit stack instead of recursion

4. **Persistent State:**
   - Problem: Process crashes lose all progress
   - Solution:
     * Checkpoint progress to database/file
     * Track visited paths to enable resume
     * Use idempotent operations

5. **Rate Limiting:**
   - Problem: Overwhelming file system with requests
   - Solution:
     * Implement backpressure mechanisms
     * Limit concurrent directory reads
     * Add delay between batches

6. **Caching:**
   - Problem: Re-crawling same directories is wasteful
   - Solution:
     * Cache directory listings with TTL
     * Use file system watching for incremental updates
     * Store metadata in database for fast queries

7. **Parallel Processing:**
   - Problem: Single-threaded crawling is slow
   - Solution:
     * Process directories in parallel using ThreadPoolExecutor
     * Use asyncio for I/O-bound operations
     * Limit concurrency to avoid resource exhaustion

Trade-offs:
- Memory vs Speed: Buffering results is faster but uses more memory
- Consistency vs Performance: Real-time watching is accurate but expensive
- Complexity vs Reliability: Distributed systems are powerful but harder to debug
"""


# ============================================================================
# PART 3: Async Processing
# ============================================================================


### other solution with queue and threadpool BFS

class MultiThreadedCrawler:
    """
    Multi-threaded file crawler for better I/O performance.
    """

    def __init__(self, max_workers: int = 10):
        self.max_workers = max_workers
        self.files = []
        self.lock = threading.Lock()

    def crawl_directory(self, path: str) -> List[str]:
        """Crawl a single directory (non-recursive)."""
        local_files = []
        subdirs = []

        try:
            with os.scandir(path) as entries:
                for entry in entries:
                    if entry.is_file(follow_symlinks=False):
                        local_files.append(entry.path)
                    elif entry.is_dir(follow_symlinks=False):
                        subdirs.append(entry.path)
        except (PermissionError, OSError) as e:
            print(f"Error accessing {path}: {e}")

        return local_files, subdirs

    def crawl(self, root_path: str) -> List[str]:
        """Main crawl method using thread pool."""
        if not os.path.exists(root_path):
            raise ValueError(f"Path does not exist: {root_path}")

        if os.path.isfile(root_path):
            return [root_path]

        # BFS approach with thread pool
        queue = Queue()
        queue.put(root_path)

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            while not queue.empty():
                futures = []

                # Submit batch of directories to process
                batch_size = min(queue.qsize(), self.max_workers * 2)
                for _ in range(batch_size):
                    if queue.empty():
                        break
                    dir_path = queue.get()
                    future = executor.submit(self.crawl_directory, dir_path)
                    futures.append(future)

                # Collect results
                for future in futures:
                    try:
                        files, subdirs = future.result()
                        with self.lock:
                            self.files.extend(files)
                        for subdir in subdirs:
                            queue.put(subdir)
                    except Exception as e:
                        print(f"Error processing directory: {e}")

        return self.files

# can consider to use webcraweler

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
    