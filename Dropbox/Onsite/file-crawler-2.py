'''
https://www.1point3acres.com/interview/problems/868c0ea1-62d7-4555-aeb2-7d9033aebbe5

Question Description
Implement a File Crawler:

Implement an API that, given a file path, returns all the files in that path.
Discuss how to scale the function in step 1 to handle larger directories. (Verbal discussion, no coding required)
Based on the second step discussion, implement an asynchronous job using provided template code.
Test Cases
No specific test cases. Discuss possible implementations during the interview.
'''

import os
from pathlib import Path
from typing import List, Set
import asyncio
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
import threading

# ============================================================================
# PART 1: Basic File Crawler Implementation
# ============================================================================

def crawl_files_basic(root_path: str) -> List[str]:
    """
    Basic implementation: Returns all files in the given directory path.

    Args:
        root_path: The root directory path to crawl

    Returns:
        List of all file paths found
    """
    files = []

    # Validate input
    if not os.path.exists(root_path):
        raise ValueError(f"Path does not exist: {root_path}")

    # If it's a file, return it directly
    if os.path.isfile(root_path):
        return [root_path]

    # Walk through directory tree
    for dirpath, dirnames, filenames in os.walk(root_path):
        for filename in filenames:
            full_path = os.path.join(dirpath, filename)
            files.append(full_path)

    return files


def crawl_files_with_filter(root_path: str, extensions: Set[str] = None) -> List[str]:
    """
    Enhanced version with file extension filtering.

    Args:
        root_path: The root directory path to crawl
        extensions: Set of file extensions to include (e.g., {'.txt', '.py'})

    Returns:
        List of filtered file paths
    """
    files = []

    if not os.path.exists(root_path):
        raise ValueError(f"Path does not exist: {root_path}")

    if os.path.isfile(root_path):
        if extensions is None or Path(root_path).suffix in extensions:
            return [root_path]
        return []

    for dirpath, dirnames, filenames in os.walk(root_path):
        for filename in filenames:
            if extensions is None or Path(filename).suffix in extensions:
                full_path = os.path.join(dirpath, filename)
                files.append(full_path)

    return files


# ============================================================================
# PART 2: Scalability Discussion
# ============================================================================

"""
SCALABILITY CONSIDERATIONS:

1. **Memory Issues**:
   - Problem: Loading all files into memory at once can cause OOM for large directories
   - Solution: Use generators/iterators to yield results one at a time

2. **Performance Issues**:
   - Problem: Single-threaded I/O is slow for large directories
   - Solution: Use parallel processing (multi-threading or multi-processing)

3. **Distributed Systems**:
   - Problem: Single machine may not handle extremely large file systems
   - Solution: Distribute work across multiple machines using a task queue

4. **Rate Limiting**:
   - Problem: Too many concurrent file operations can overwhelm the file system
   - Solution: Implement rate limiting and backpressure mechanisms

5. **Error Handling**:
   - Problem: Permission errors, symlinks, or corrupted files can crash the crawler
   - Solution: Robust error handling, skip inaccessible files, handle symlinks

6. **Progress Tracking**:
   - Problem: Long-running jobs need progress monitoring
   - Solution: Implement callbacks or status tracking
"""


# ============================================================================
# PART 3: Scalable Implementations
# ============================================================================

# APPROACH 1: Generator-based (Memory Efficient)
def crawl_files_generator(root_path: str):
    """
    Memory-efficient implementation using generators.
    Yields files one at a time instead of loading all into memory.
    """
    if not os.path.exists(root_path):
        raise ValueError(f"Path does not exist: {root_path}")

    if os.path.isfile(root_path):
        yield root_path
        return

    for dirpath, dirnames, filenames in os.walk(root_path):
        for filename in filenames:
            full_path = os.path.join(dirpath, filename)
            yield full_path


# APPROACH 2: Multi-threaded (Performance Optimized)
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


# APPROACH 3: Asynchronous Implementation
async def crawl_directory_async(path: str, semaphore: asyncio.Semaphore):
    """
    Asynchronously crawl a single directory.
    Uses semaphore to limit concurrent operations.
    """
    async with semaphore:
        files = []
        subdirs = []

        try:
            # os.scandir is synchronous, run in executor
            loop = asyncio.get_event_loop()
            entries = await loop.run_in_executor(None, lambda: list(os.scandir(path)))

            for entry in entries:
                if entry.is_file(follow_symlinks=False):
                    files.append(entry.path)
                elif entry.is_dir(follow_symlinks=False):
                    subdirs.append(entry.path)
        except (PermissionError, OSError) as e:
            print(f"Error accessing {path}: {e}")

        return files, subdirs


async def crawl_files_async(root_path: str, max_concurrent: int = 50) -> List[str]:
    """
    Asynchronous file crawler with concurrency control.

    Args:
        root_path: Root directory to crawl
        max_concurrent: Maximum number of concurrent operations

    Returns:
        List of all file paths found
    """
    if not os.path.exists(root_path):
        raise ValueError(f"Path does not exist: {root_path}")

    if os.path.isfile(root_path):
        return [root_path]

    all_files = []
    semaphore = asyncio.Semaphore(max_concurrent)
    pending_dirs = [root_path]

    while pending_dirs:
        # Process current batch of directories
        tasks = [crawl_directory_async(d, semaphore) for d in pending_dirs]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        pending_dirs = []
        for result in results:
            if isinstance(result, Exception):
                print(f"Error: {result}")
                continue

            files, subdirs = result
            all_files.extend(files)
            pending_dirs.extend(subdirs)

    return all_files


# APPROACH 4: Job Queue Pattern (Production-Ready)
class FileCrawlerJob:
    """
    Production-ready file crawler with job queue pattern.
    Suitable for distributed systems with task queues like Celery.
    """

    def __init__(self, root_path: str, job_id: str = None):
        self.root_path = root_path
        self.job_id = job_id or f"job_{id(self)}"
        self.status = "pending"
        self.progress = 0
        self.total_files = 0
        self.errors = []

    def update_status(self, status: str, progress: int = None):
        """Update job status - in production, this would update a database."""
        self.status = status
        if progress is not None:
            self.progress = progress
        print(f"Job {self.job_id}: {status} ({progress}%)")

    async def execute(self, callback=None):
        """
        Execute the crawl job asynchronously.

        Args:
            callback: Optional callback function called for each file found
        """
        self.update_status("running", 0)

        try:
            files = await crawl_files_async(self.root_path)
            self.total_files = len(files)

            # Process files with progress tracking
            for i, file_path in enumerate(files):
                if callback:
                    await callback(file_path)

                # Update progress every 10%
                progress = int((i + 1) / self.total_files * 100)
                if progress % 10 == 0 and progress != self.progress:
                    self.update_status("running", progress)

            self.update_status("completed", 100)
            return files

        except Exception as e:
            self.status = "failed"
            self.errors.append(str(e))
            print(f"Job {self.job_id} failed: {e}")
            raise


# ============================================================================
# EXAMPLE USAGE AND TESTS
# ============================================================================

def example_usage():
    """Examples of how to use the different implementations."""

    test_path = "/tmp/test_directory"  # Change to a real path

    # Example 1: Basic usage
    print("=== Basic Crawler ===")
    try:
        files = crawl_files_basic(test_path)
        print(f"Found {len(files)} files")
    except ValueError as e:
        print(f"Error: {e}")

    # Example 2: With filter
    print("\n=== Filtered Crawler (Python files only) ===")
    try:
        py_files = crawl_files_with_filter(test_path, {'.py'})
        print(f"Found {len(py_files)} Python files")
    except ValueError as e:
        print(f"Error: {e}")

    # Example 3: Generator (memory efficient)
    print("\n=== Generator-based Crawler ===")
    try:
        count = 0
        for file_path in crawl_files_generator(test_path):
            count += 1
            if count <= 5:  # Print first 5
                print(f"  {file_path}")
        print(f"Total: {count} files")
    except ValueError as e:
        print(f"Error: {e}")

    # Example 4: Multi-threaded
    print("\n=== Multi-threaded Crawler ===")
    try:
        crawler = MultiThreadedCrawler(max_workers=5)
        files = crawler.crawl(test_path)
        print(f"Found {len(files)} files using {crawler.max_workers} threads")
    except ValueError as e:
        print(f"Error: {e}")

    # Example 5: Async
    print("\n=== Async Crawler ===")
    async def run_async():
        try:
            files = await crawl_files_async(test_path, max_concurrent=20)
            print(f"Found {len(files)} files asynchronously")
        except ValueError as e:
            print(f"Error: {e}")

    asyncio.run(run_async())

    # Example 6: Job pattern
    print("\n=== Job Queue Pattern ===")
    async def run_job():
        job = FileCrawlerJob(test_path, job_id="test_job_1")

        async def file_callback(file_path):
            # Process each file (e.g., compute hash, upload to S3, etc.)
            pass

        try:
            files = await job.execute(callback=file_callback)
            print(f"Job completed: {len(files)} files processed")
        except Exception as e:
            print(f"Job failed: {e}")

    asyncio.run(run_job())


if __name__ == "__main__":
    # Test with current directory
    print("Testing file crawler implementations...\n")

    # Use current directory for testing
    current_dir = os.getcwd()

    print(f"Crawling current directory: {current_dir}\n")

    # Basic test
    files = crawl_files_basic(current_dir)
    print(f"Basic crawler found {len(files)} files")

    # Show first 5 files
    print("\nFirst 5 files:")
    for f in files[:5]:
        print(f"  {f}")
