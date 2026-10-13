# Confluent Practical Interview Guide: File Operations & Stream Processing

This guide covers common interview scenarios, edge cases, design principles, and problem sets related to practical file reading, writing, and log analysis for backend engineering interviews (such as Confluent's Practical Coding Round).

## Key Concepts & Best Practices

1. **Memory Efficiency (Streaming vs. Loading All into Memory)**

   * **Rule:** Never use `f.read()` or `f.readlines()` on large files.

   * **Solution:** Stream files line-by-line using chunked reading, generators, or line iterators (`for line in file:`).

2. **Resource Management**

   * **Rule:** Always manage file handles safely to avoid leaks.

   * **Solution:** Use Context Managers (`with open(...) as f:`).

3. **Handling File System & Format Edge Cases**

   * **File Size:** Files larger than available RAM (e.g., 10GB+ file on a 4GB machine).

   * **Encoding Issues:** Non-UTF-8 characters, invalid byte sequences (`errors='replace'` or `errors='ignore'`).

   * **Malformed Lines:** Missing separators, truncated lines, trailing newlines (`\r\n` vs `\n`).

   * **Unsorted Data:** Timestamps or records arriving out of order.

   * **Empty Files / Missing Files:** `FileNotFoundError`, `PermissionError`, zero-byte files.

## Core Problems & Solutions

### Problem 1: Large File Log Aggregator & Top-K Extraction

#### Problem Statement

Given a massive log file (e.g., 50GB) where each line represents an API request in the format:
`<TIMESTAMP> <HTTP_METHOD> <ENDPOINT> <RESPONSE_TIME_MS> <STATUS_CODE>`

**Tasks:**

1. Find the top $K$ most requested endpoints.

2. Calculate the average response time for each endpoint.

3. Handle potentially malformed lines without crashing.

#### Solution Architecture & Code

```python
import sys
from collections import defaultdict
import heapq

def process_log_line(line: str):
    """
    Parses a single log line safely.
    Format: <TIMESTAMP> <HTTP_METHOD> <ENDPOINT> <RESPONSE_TIME_MS> <STATUS_CODE>
    """
    parts = line.strip().split()
    if len(parts) != 5:
        return None
    
    timestamp, method, endpoint, duration_str, status_str = parts
    
    try:
        duration = float(duration_str)
        status = int(status_str)
        return endpoint, duration
    except ValueError:
        # Silently drop or log malformed numbers
        return None

def analyze_logs(filepath: str, top_k: int = 5):
    """
    Processes log file line-by-line with O(1) memory per line.
    Calculates top K endpoints and average response times.
    """
    # Dictionary storing [count, total_duration]
    endpoint_stats = defaultdict(lambda: [0, 0.0])
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as file:
            for line_num, line in enumerate(file, 1):
                if not line.strip():
                    continue
                
                parsed = process_log_line(line)
                if not parsed:
                    continue
                
                endpoint, duration = parsed
                endpoint_stats[endpoint][0] += 1
                endpoint_stats[endpoint][1] += duration
                
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.", file=sys.stderr)
        return
    except PermissionError:
        print(f"Error: Permission denied for file '{filepath}'.", file=sys.stderr)
        return

    # Heap to find top-K most requested endpoints: O(U log K) where U = unique endpoints
    min_heap = []
    
    for endpoint, (count, total_time) in endpoint_stats.items():
        avg_time = total_time / count
        heapq.heappush(min_heap, (count, avg_time, endpoint))
        if len(min_heap) > top_k:
            heapq.heappop(min_heap)
            
    # Print results sorted descending by count
    results = sorted(min_heap, reverse=True)
    
    print(f"{'Endpoint':<30} | {'Request Count':<15} | {'Avg Duration (ms)':<18}")
    print("-" * 70)
    for count, avg_time, endpoint in results:
        print(f"{endpoint:<30} | {count:<15} | {avg_time:<18.2f}")

# Example Usage:
# analyze_logs("server.log", top_k=3)
```

---

### Problem 2: Merge $N$ Sorted Log Files (K-Way Merge)

#### Problem Statement

Given $N$ different log files, each individually sorted by timestamp in ascending order, merge them into a single sorted output file without loading all files entirely into memory.

#### Solution Architecture & Code

```python
import heapq

class LogLineEntry:
    def __init__(self, timestamp: str, raw_line: str, file_index: int):
        self.timestamp = timestamp
        self.raw_line = raw_line
        self.file_index = file_index

    # Min-heap comparison based on timestamp
    def __lt__(self, other):
        return self.timestamp < other.timestamp

def extract_timestamp(line: str) -> str:
    """Extracts timestamp assumed to be at the beginning of the line."""
    parts = line.strip().split(' ', 1)
    return parts[0] if parts else ""

def merge_sorted_log_files(input_filepaths: list[str], output_filepath: str):
    """
    Merges N sorted log files into one sorted output file.
    Time Complexity: O(M log N) where M = total lines, N = number of files.
    Space Complexity: O(N) memory.
    """
    file_handles = []
    min_heap = []

    try:
        # Open all files and read initial lines
        for idx, path in enumerate(input_filepaths):
            f = open(path, 'r', encoding='utf-8', errors='replace')
            file_handles.append(f)
            
            first_line = f.readline()
            if first_line:
                ts = extract_timestamp(first_line)
                heapq.heappush(min_heap, LogLineEntry(ts, first_line, idx))

        with open(output_filepath, 'w', encoding='utf-8') as out_f:
            while min_heap:
                smallest_entry = heapq.heappop(min_heap)
                out_f.write(smallest_entry.raw_line)

                # Read next line from the same file handle
                next_line = file_handles[smallest_entry.file_index].readline()
                if next_line:
                    next_ts = extract_timestamp(next_line)
                    heapq.heappush(
                        min_heap, 
                        LogLineEntry(next_ts, next_line, smallest_entry.file_index)
                    )

    finally:
        # Ensure all opened files are properly closed
        for f in file_handles:
            f.close()

# Example Usage:
# merge_sorted_log_files(["log1.txt", "log2.txt", "log3.txt"], "merged_output.txt")
```

---

### Problem 3: Large File Tailer (`tail -n N -f` Emulation)

#### Problem Statement

Write a function that reads the last $N$ lines of a potentially massive file (e.g., 10 GB+) without scanning from the beginning, and then continuously streams newly appended lines as they arrive (handling file rotation or truncation).

#### Key Design Points
* **Binary Backward Chunking:** Seek backward from `os.SEEK_END` in binary mode (`'rb'`) in fixed-size blocks (e.g., 4 KB). Count newline (`\n`) characters until $N$ lines are retrieved.
* **$O(N)$ Startup Time:** Startup time depends solely on $N \times \text{line length}$, ignoring overall file size.
* **Follow Mode (`-f`):** Once the tail is produced, keep track of the current byte position (`f.tell()`) and yield new lines as they are written to disk.

#### Solution Architecture & Code

```python
import os
import time
from typing import Generator, List

def tail_n_and_follow(
    filepath: str, 
    n_lines: int = 10, 
    poll_interval: float = 0.5, 
    buffer_size: int = 4096
) -> Generator[str, None, None]:
    """
    Tails the last `n_lines` of a file without scanning from the beginning,
    then continuously yields new lines appended to the file.
    
    Time Complexity to start: O(N * avg_line_length) — independent of total file size.
    Space Complexity: O(N * avg_line_length) to store the last N lines.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    file_size = os.path.getsize(filepath)
    
    with open(filepath, 'rb') as f:
        # =================================================================
        # STEP 1: Seek backward from the end to find the last N lines
        # =================================================================
        found_lines: List[bytes] = []
        pointer = file_size
        remainder = b""

        while pointer > 0 and len(found_lines) <= n_lines:
            read_size = min(buffer_size, pointer)
            pointer -= read_size
            f.seek(pointer)
            
            chunk = f.read(read_size) + remainder
            lines = chunk.split(b'\n')
            
            # The first chunk element may be an incomplete line spanning the previous block
            remainder = lines[0]
            
            # Process complete lines from bottom to top
            for line in reversed(lines[1:]):
                found_lines.append(line)
                if len(found_lines) == n_lines:
                    break

        # Collect top fragment if file top was reached before getting N lines
        if pointer == 0 and remainder and len(found_lines) < n_lines:
            found_lines.append(remainder)

        # Yield initial N lines in chronological order
        for line in reversed(found_lines):
            yield line.decode('utf-8', errors='replace').rstrip('\r\n')

        # =================================================================
        # STEP 2: Follow mode (tail -f)
        # =================================================================
        f.seek(0, os.SEEK_END)
        current_pos = f.tell()

        while True:
            line = f.readline()
            if line:
                yield line.decode('utf-8', errors='replace').rstrip('\r\n')
                current_pos = f.tell()
            else:
                # Check for file truncation or log rotation
                try:
                    new_size = os.path.getsize(filepath)
                    if new_size < current_pos:
                        print("\n[Notice: File truncated or rotated. Resetting pointer.]")
                        f.seek(0, os.SEEK_SET)
                        current_pos = 0
                    else:
                        time.sleep(poll_interval)
                        f.seek(current_pos)
                except FileNotFoundError:
                    # Handle file re-creation during log rotation
                    time.sleep(poll_interval)

# Example Usage:
# for line in tail_n_and_follow("app.log", n_lines=10):
#     print(f"TAIL: {line}")
```

---

### Problem 4: Sliding Window Log Rate Limiter / Event Counter

#### Problem Statement

Given a large log file where entries contain ISO timestamps, calculate the maximum number of requests processed within any rolling 1-minute window across the entire file.

#### Solution Architecture & Code

```python
from collections import deque
from datetime import datetime

def parse_iso_timestamp(ts_str: str) -> float:
    """Converts ISO timestamp string to epoch seconds."""
    dt = datetime.fromisoformat(ts_str)
    return dt.timestamp()

def max_requests_per_window(filepath: str, window_seconds: int = 60) -> int:
    """
    Finds maximum requests within a rolling time window using a sliding deque.
    Time Complexity: O(M) where M is number of lines.
    Space Complexity: O(W) where W is max events in window.
    """
    window = deque()
    max_count = 0

    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            if not line.strip():
                continue
            
            parts = line.strip().split()
            if not parts:
                continue
            
            try:
                curr_time = parse_iso_timestamp(parts[0])
            except ValueError:
                continue  # Skip invalid timestamp formats

            window.append(curr_time)

            # Evict timestamps outside the sliding window
            while window and window[-1] - window[0] > window_seconds:
                window.popleft()

            max_count = max(max_count, len(window))

    return max_count
```

---

## Summary Checklist for the Confluent Interview

1. **Clarify Input Constraints:**
   * Is the file small enough to fit in RAM or massive (e.g., 10 GB+)?
   * Is the input file sorted?
   * What is the expected behavior for malformed lines?

2. **Structure & Readability:**
   * Break code into clean, single-responsibility helper functions.
   * Name variables clearly (`curr_node`, `file_handle`, `min_heap`).

3. **Always Add Defensive Checks:**
   * Check for empty lines, missing fields, or invalid types.
   * Clean up resource handles in `finally` blocks or context managers.
---

### Problem 3: File Tailer / Log Monitor (`tail -f` Emulation) Easy way -might be wrong

#### Problem Statement
Write a function that continuously monitors an actively written log file and prints new lines as they are appended, handling potential file rotations or truncation.

#### Solution Architecture & Code

```python
import time
import os

def tail_f(filepath: str, poll_interval: float = 1.0):
    """
    Emulates 'tail -f'.
    Continuously yields new lines appended to the file.
    Handles file truncation (e.g., log rotation).
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Target file {filepath} does not exist.")

    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        # Move pointer to the end of the file initially
        f.seek(0, os.SEEK_END)
        current_pos = f.tell()

        while True:
            line = f.readline()
            if line:
                yield line.strip()
            else:
                # Check if file was truncated (current size < last read position)
                if os.path.getsize(filepath) < current_pos:
                    print("\n[Log File Rotated/Truncated. Resetting pointer...]")
                    f.seek(0, os.SEEK_SET)
                else:
                    time.sleep(poll_interval)
                    f.seek(current_pos)
            
            current_pos = f.tell()

# Example Usage:
# for new_line in tail_f("app.log"):
#     print(f"NEW LOG: {new_line}")
```
