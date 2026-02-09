'''
https://www.1point3acres.com/interview/problems/ea7d38db-f5ac-4619-b82f-c7d0228d01ca

API Design for Long Running Requests

Design an API to handle a list of files. Part 1: Implement a function to accept a list of files and process each file simply.
The file processing steps are as follows:

Accept a list of strings representing files.
Simulate processing each file and return the result.
Part 2: For the follow-up question, design a method to handle long-running requests.

Each file's processing time can be long, so requests need to be handled asynchronously.
Implement a function to store requests in a queue, support querying request status, and retrieving results.
Input Format:

The first line receives the number of files.
The following lines each represent a file name.
Output Format:

Part 1 returns the simulated processing result of each file.
Part 2 supports querying the request status and retrieving processing results.
Sample Input:

3
data1.txt
data2.txt
data3.txt
Sample Output:

['data1_processed', 'data2_processed', 'data3_processed']
Asynchronous Processing:

Upon submission, return a request id.
Query processing progress and retrieve results based on the request id.
'''

import time
import uuid
import threading
import asyncio
from enum import Enum
from typing import List, Dict, Optional
from queue import Queue
from dataclasses import dataclass


class RequestStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class RequestInfo:
    request_id: str
    status: RequestStatus
    files: List[str]
    results: Optional[List[str]] = None
    error: Optional[str] = None
    created_at: float = None
    completed_at: Optional[float] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.time()


class FileProcessor:
    @staticmethod
    def process_file(filename: str) -> str:
        """Simulate processing a single file"""
        # Simulate some processing time
        time.sleep(0.1)
        # Return processed filename
        return f"{filename.split('.')[0]}_processed"

    def process_files(self, files: List[str]) -> List[str]:
        """Process a list of files synchronously"""
        results = []
        for file in files:
            result = self.process_file(file)
            results.append(result)
        return results


class AsyncFileProcessor:
    def __init__(self, num_workers: int = 3):
        self.requests: Dict[str, RequestInfo] = {}
        self.request_queue = Queue()
        self.num_workers = num_workers
        self.workers = []
        self.lock = threading.Lock()
        self._start_workers()

    def _start_workers(self):
        """Start worker threads to process requests"""
        for _ in range(self.num_workers):
            worker = threading.Thread(target=self._worker, daemon=True)
            worker.start()
            self.workers.append(worker)

    def _worker(self):
        """Worker thread that processes requests from the queue"""
        while True:
            request_id = self.request_queue.get()
            if request_id is None:  # Shutdown signal
                break

            try:
                self._process_request(request_id)
            except Exception as e:
                with self.lock:
                    request = self.requests[request_id]
                    request.status = RequestStatus.FAILED
                    request.error = str(e)
                    request.completed_at = time.time()
            finally:
                self.request_queue.task_done()

    def _process_request(self, request_id: str):
        """Process a single request"""
        with self.lock:
            request = self.requests[request_id]
            request.status = RequestStatus.PROCESSING

        # Process each file
        results = []
        for file in request.files:
            # Simulate file processing
            time.sleep(0.5)  # Simulate long-running operation
            result = f"{file.split('.')[0]}_processed"
            results.append(result)

        # Update request with results
        with self.lock:
            request.results = results
            request.status = RequestStatus.COMPLETED
            request.completed_at = time.time()

    def submit_request(self, files: List[str]) -> str:
        """
        Submit a new file processing request
        Returns: request_id for tracking
        """
        request_id = str(uuid.uuid4())

        request_info = RequestInfo(
            request_id=request_id,
            status=RequestStatus.PENDING,
            files=files
        )

        with self.lock:
            self.requests[request_id] = request_info

        # Add to queue for processing
        self.request_queue.put(request_id)

        return request_id

    def get_status(self, request_id: str) -> Optional[str]:
        """Query the status of a request"""
        with self.lock:
            if request_id not in self.requests:
                return None
            return self.requests[request_id].status.value

    def get_result(self, request_id: str) -> Optional[Dict]:
        """
        Retrieve the result of a request
        Returns: dict with status, results, and other metadata
        """
        with self.lock:
            if request_id not in self.requests:
                return None

            request = self.requests[request_id]
            return {
                "request_id": request.request_id,
                "status": request.status.value,
                "files": request.files,
                "results": request.results,
                "error": request.error,
                "created_at": request.created_at,
                "completed_at": request.completed_at
            }

    def get_progress(self, request_id: str) -> Optional[Dict]:
        """Get detailed progress information
        Note: results are set all at once after processing, so progress
        will only ever show 0% or 100%. For real progress tracking,
        update results incrementally in _process_request.
        """
        with self.lock:
            if request_id not in self.requests:
                return None

            request = self.requests[request_id]
            total_files = len(request.files)
            processed_files = len(request.results) if request.results else 0

            return {
                "request_id": request.request_id,
                "status": request.status.value,
                "total_files": total_files,
                "processed_files": processed_files,
                "progress_percentage": (processed_files / total_files * 100) if total_files > 0 else 0
            }

    def shutdown(self):
        """Gracefully shutdown the processor"""
        # Send shutdown signal to all workers
        for _ in range(self.num_workers):
            self.request_queue.put(None)

        # Wait for all workers to finish
        for worker in self.workers:
            worker.join()


class AsyncAwaitFileProcessor:
    """Part 2 Alternative: Using async/await pattern instead of threading"""

    def __init__(self):
        self.requests: Dict[str, RequestInfo] = {}
        self.lock = asyncio.Lock()

    async def _process_file(self, filename: str) -> str:
        """Simulate async file processing"""
        # Use asyncio.sleep instead of time.sleep to yield control
        await asyncio.sleep(0.5)  # Non-blocking sleep
        return f"{filename.split('.')[0]}_processed"

    async def _process_request(self, request_id: str):
        """Process a single request asynchronously"""
        async with self.lock:
            request = self.requests[request_id]
            request.status = RequestStatus.PROCESSING

        # Process each file sequentially (use asyncio.gather for true concurrency)
        results = []
        for file in self.requests[request_id].files:
            result = await self._process_file(file)
            results.append(result)

        # Update request with results
        async with self.lock:
            request.results = results
            request.status = RequestStatus.COMPLETED
            request.completed_at = time.time()

    async def submit_request(self, files: List[str]) -> str:
        """
        Submit a new file processing request
        Returns: request_id for tracking
        """
        request_id = str(uuid.uuid4())

        request_info = RequestInfo(
            request_id=request_id,
            status=RequestStatus.PENDING,
            files=files
        )

        async with self.lock:
            self.requests[request_id] = request_info

        # Start processing in background (fire and forget)
        asyncio.create_task(self._process_request(request_id))

        return request_id

    async def get_status(self, request_id: str) -> Optional[str]:
        """Query the status of a request"""
        async with self.lock:
            if request_id not in self.requests:
                return None
            return self.requests[request_id].status.value

    async def get_result(self, request_id: str) -> Optional[Dict]:
        """Retrieve the result of a request"""
        async with self.lock:
            if request_id not in self.requests:
                return None

            request = self.requests[request_id]
            return {
                "request_id": request.request_id,
                "status": request.status.value,
                "files": request.files,
                "results": request.results,
                "error": request.error,
                "created_at": request.created_at,
                "completed_at": request.completed_at
            }

if __name__ == "__main__":
    # Part 1: Synchronous
    files = ["data1.txt", "data2.txt", "data3.txt"]
    print(FileProcessor().process_files(files))
    # Output: ['data1_processed', 'data2_processed', 'data3_processed']

    # Part 2: Async with threading
    processor = AsyncFileProcessor(num_workers=2)
    request_id = processor.submit_request(files)
    print(f"Request ID: {request_id}")

    # Poll until done
    while processor.get_status(request_id) not in ["completed", "failed"]:
        time.sleep(0.3)

    print(processor.get_result(request_id))
    processor.shutdown()