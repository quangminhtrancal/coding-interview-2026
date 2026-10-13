# Confluent Coding Interview Preparation: Practical File Operations

**Focus:** File reading, parsing, transformation, manipulation, error handling, and optimization  
**Reference Language:** Python 3  
**Goal:** Prepare for practical coding exercises and interviewer follow-up questions.

---

## Table of Contents
1. [What the Interviewer Is Evaluating](#1-what-the-interviewer-is-evaluating)
2. [A Repeatable Problem-Solving Approach](#2-a-repeatable-problem-solving-approach)
3. [Core File API Knowledge](#3-core-file-api-knowledge)
4. [Basic File Operation Problems](#4-basic-file-operation-problems)
5. [File Parsing and Transformation Problems](#5-file-parsing-and-transformation-problems)
6. [Aggregation and Comparison Problems](#6-aggregation-and-comparison-problems)
7. [Large-File and Performance Problems](#7-large-file-and-performance-problems)
8. [Reliability, Correctness, and Safety](#8-reliability-correctness-and-safety)
9. [Advanced Follow-Up Questions](#9-advanced-follow-up-questions)
10. [Testing Strategy](#10-testing-strategy)
11. [Complexity Cheat Sheet](#11-complexity-cheat-sheet)
12. [Mock Interview Exercises](#12-mock-interview-exercises)
13. [Interview Communication Checklist](#13-interview-communication-checklist)

---

## 1. What the Interviewer Is Evaluating

| Skill | What You Should Demonstrate |
| :--- | :--- |
| **File Handling** | Correctly open, read, write, and close files using context managers. |
| **Problem Solving** | Clarify requirements, handle ambiguity, and break problems into incremental steps. |
| **Edge Cases** | Handle empty files, malformed records, missing files, partial lines, and duplicates. |
| **Code Structure** | Write small, readable functions with clear responsibilities and defensive checks. |
| **Optimization** | Understand memory usage, runtime complexity, $O(1)$ streaming vs memory loading, and I/O trade-offs. |

### Typical Evaluation Scenario
Suppose you receive a file containing records:
```text
alice,100
bob,200
alice,150
charlie,50
```

An interviewer might ask you to:
1. Read the file and calculate totals per user.
2. Ignore malformed records.
3. Sort users by total.
4. Write the results to another file.
5. Handle an empty input file.
6. Explain how your implementation changes for a 100 GB file.

A strong candidate solves the initial problem cleanly first, then adapts the implementation as constraints are added.

---

## 2. A Repeatable Problem-Solving Approach

1. **Clarify Requirements:** Ask about format (CSV/JSON/Text), missing/empty files, record malformation policies (skip vs crash), duplicate rules, and scale/memory bounds.
2. **Define Algorithm:** Map out line-by-line streaming, state accumulation, or buffer processing steps.
3. **Implement Simplest Correct Solution:** Use `with open(...)`, explicit `encoding="utf-8"`, Generators/Iterators, and clean exception handling.
4. **Test Edge Cases:** Single record, zero bytes, missing file, missing trailing newline, malformed fields, multi-gigabyte scale.
5. **Discuss Complexity:** Formulate time ($O(N)$) and space ($O(1)$ auxiliary vs $O(K)$ unique state) bounds.
6. **Optimize on Demand:** Pivot to chunked binary seeks or external sorting when scale constraints are introduced.

---

## 3. Core File API Knowledge

### 3.1 Opening Files & Modes
```python
with open("input.txt", "r", encoding="utf-8") as file:
    for line in file:
        print(line.rstrip("\n"))
```

* `"r"`: Read existing file.
* `"w"`: Write; **truncates existing file contents immediately**.
* `"a"`: Append to file end.
* `"x"`: Exclusive creation (fails if file already exists).
* `"rb"` / `"wb"`: Raw binary read/write (essential for precise seeking, byte manipulation, or non-text formats).

### 3.2 Reading Methods
* `file.read()`: Reads entire file into memory as one string ($O(N)$ RAM).
* `file.readline()`: Reads a single line.
* `file.readlines()`: Reads all lines into a memory list ($O(N)$ RAM).
* `for line in file:` **(Preferred)**: Streams line-by-line ($O(1)$ RAM).

---

## 4. Basic File Operation Problems

### Problem 1: Read File and Print Contents
```python
from pathlib import Path

# Memory-bound approach for small files
def read_file(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")

# Streamed approach for large files
def print_file_streamed(path: str) -> None:
    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            print(line, end="")
```

### Problem 2: Count Lines in a File
```python
def count_lines(path: str) -> int:
    with open(path, "r", encoding="utf-8") as file:
        return sum(1 for _ in file)
```
* **Time Complexity:** $O(N)$ where $N$ is character/byte length.
* **Auxiliary Space:** $O(1)$ memory.

### Problem 3: Count Words in a File
```python
def count_words(path: str) -> int:
    total = 0
    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            total += len(line.split())
    return total
```

### Problem 4: Copy a File Safely
```python
import shutil

def copy_file(source: str, destination: str) -> None:
    shutil.copyfile(source, destination) # Use copy2 to preserve timestamps/metadata
```

### Problem 5: Append Line to a File
```python
def append_line(path: str, text: str) -> None:
    with open(path, "a", encoding="utf-8") as file:
        file.write(text + "\n")
```

---

## 5. File Parsing and Transformation Problems

### Problem 6: Remove Blank Lines
```python
def remove_blank_lines(source: str, destination: str) -> None:
    with open(source, "r", encoding="utf-8") as src, \
         open(destination, "w", encoding="utf-8") as dst:
        for line in src:
            if line.strip():
                dst.write(line)
```

### Problem 7: Deduplicate Lines Preserving Order
```python
def deduplicate_lines(source: str, destination: str) -> None:
    seen = set()
    with open(source, "r", encoding="utf-8") as src, \
         open(destination, "w", encoding="utf-8") as dst:
        for line in src:
            if line not in seen:
                seen.add(line)
                dst.write(line)
```
* **Complexity:** Time $O(N)$, Space $O(U)$ where $U$ is total unique line bytes.
* **Large File Follow-up:** External sort & merge, or hash partitioning across buckets.

### Problem 8: Parse CSV and Calculate Totals
```python
import csv
from collections import defaultdict

def calculate_totals(path: str) -> dict[str, float]:
    totals = defaultdict(float)
    with open(path, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            user = row["user"].strip()
            amount = float(row["amount"])
            totals[user] += amount
    return dict(totals)
```

### Problem 9: Parse JSON Lines Stream
```python
import json
from collections import Counter

def count_event_types(path: str) -> dict[str, int]:
    counts = Counter()
    with open(path, "r", encoding="utf-8") as file:
        for line_num, line in enumerate(file, 1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
                counts[record["type"]] += 1
            except (json.JSONDecodeError, KeyError) as exc:
                print(f"Skipping malformed line {line_num}: {exc}")
    return dict(counts)
```

---

## 6. Aggregation and Comparison Problems

### Problem 10: Compare Two Files Byte-by-Byte
```python
def files_equal(path_a: str, path_b: str) -> bool:
    chunk_size = 1024 * 1024  # 1 MB chunk
    with open(path_a, "rb") as a, open(path_b, "rb") as b:
        while True:
            chunk_a = a.read(chunk_size)
            chunk_b = b.read(chunk_size)
            if chunk_a != chunk_b:
                return False
            if not chunk_a:
                return True
```

### Problem 11: Difference Between Two Files ($A \setminus B$)
```python
def difference_file(file_a: str, file_b: str, destination: str) -> None:
    with open(file_b, encoding="utf-8") as b:
        ids_b = {line.rstrip("\r\n") for line in b}

    with open(file_a, encoding="utf-8") as a, \
         open(destination, "w", encoding="utf-8") as out:
        for line in a:
            if line.rstrip("\r\n") not in ids_b:
                out.write(line)
```

---

## 7. Large-File and Performance Problems

### Problem 12: Large File Tailer (`tail -n N -f`)
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
    Tails last n_lines in O(N * avg_line_length) time via binary backward seek,
    then continuously yields newly appended lines.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    file_size = os.path.getsize(filepath)
    
    with open(filepath, 'rb') as f:
        # Step 1: Backward seek to retrieve N trailing lines
        found_lines: List[bytes] = []
        pointer = file_size
        remainder = b""

        while pointer > 0 and len(found_lines) <= n_lines:
            read_size = min(buffer_size, pointer)
            pointer -= read_size
            f.seek(pointer)
            
            chunk = f.read(read_size) + remainder
            lines = chunk.split(b'\n')
            remainder = lines[0]
            
            for line in reversed(lines[1:]):
                found_lines.append(line)
                if len(found_lines) == n_lines:
                    break

        if pointer == 0 and remainder and len(found_lines) < n_lines:
            found_lines.append(remainder)

        for line in reversed(found_lines):
            yield line.decode('utf-8', errors='replace').rstrip('\r\n')

        # Step 2: Continuous Follow Mode
        f.seek(0, os.SEEK_END)
        current_pos = f.tell()

        while True:
            line = f.readline()
            if line:
                yield line.decode('utf-8', errors='replace').rstrip('\r\n')
                current_pos = f.tell()
            else:
                try:
                    if os.path.getsize(filepath) < current_pos:
                        f.seek(0, os.SEEK_SET)
                        current_pos = 0
                    else:
                        time.sleep(poll_interval)
                        f.seek(current_pos)
                except FileNotFoundError:
                    time.sleep(poll_interval)
```

### Problem 13: Merge $K$ Sorted Log Files
```python
import heapq

class LogEntry:
    def __init__(self, line: str, file_idx: int):
        self.line = line
        self.file_idx = file_idx
        self.timestamp = line.split(" ", 1)[0]
        
    def __lt__(self, other):
        return self.timestamp < other.timestamp

def merge_k_sorted_files(input_paths: list[str], output_path: str):
    handles = [open(p, "r", encoding="utf-8") for p in input_paths]
    min_heap = []

    try:
        for idx, h in enumerate(handles):
            line = h.readline()
            if line:
                heapq.heappush(min_heap, LogEntry(line, idx))

        with open(output_path, "w", encoding="utf-8") as out:
            while min_heap:
                entry = heapq.heappop(min_heap)
                out.write(entry.line)
                
                next_line = handles[entry.file_idx].readline()
                if next_line:
                    heapq.heappush(min_heap, LogEntry(next_line, entry.file_idx))
    finally:
        for h in handles:
            h.close()
```

---

## 8. Reliability, Correctness, and Safety

### Safe In-Place Output Replacement (Atomic Writes)
```python
import os
import tempfile
from pathlib import Path

def transform_file_safely(source: str, destination: str) -> None:
    source_path = Path(source)
    dest_path = Path(destination)

    # Create temporary file in same directory to support atomic rename across filesystems
    fd, temp_name = tempfile.mkstemp(
        dir=dest_path.parent,
        prefix=f".{dest_path.name}.",
        suffix=".tmp"
    )

    try:
        with os.fdopen(fd, "w", encoding="utf-8") as out:
            with source_path.open("r", encoding="utf-8") as src:
                for line in src:
                    out.write(line.upper())
            out.flush()
            os.fsync(out.fileno())

        os.replace(temp_name, dest_path)
    except BaseException:
        if os.path.exists(temp_name):
            os.unlink(temp_name)
        raise
```

---

## 11. Complexity Cheat Sheet

Let:
* $N$ = Total input file size in bytes
* $K$ = Number of distinct keys/users/words
* $L$ = Maximum line length
* $k$ = Number of sorted files

| Operation | Time Complexity | Auxiliary Space Complexity |
| :--- | :--- | :--- |
| **Stream Line Count** | $O(N)$ | $O(1)$ |
| **Stream Transformation** | $O(N)$ | $O(L)$ |
| **Unique Word Count / Deduplication** | $O(N)$ | $O(K)$ |
| **Byte Comparison (Chunked)** | $O(N)$ worst-case | $O(\text{Chunk Size})$ |
| **Merge 2 Sorted Files** | $O(N)$ | $O(1)$ records |
| **Merge $k$ Sorted Files (Min-Heap)** | $O(N \log k)$ | $O(k)$ active stream buffer entries |
| **Tail Last $N$ Lines (Backward Seek)**| $O(N \times L)$ | $O(N \times L)$ |

---

## 13. Interview Communication Checklist

### Before Coding
* Restate the core problem and verify expected output schema.
* Clarify scale assumptions (RAM bounds vs multi-GB disk size).
* Establish malformed record policy (drop, fail fast, or collect errors).

### While Coding
* Use Python context managers (`with open(...)`).
* Implement line-by-line generators/iterators to preserve $O(1)$ memory.
* Explicitly set `encoding="utf-8"` and `errors="replace"`.
* Keep parsing logic isolated from file I/O operations.

### After Coding
* Walk through an empty file test case.
* Walk through missing file and malformed line edge cases.
* State explicit time ($O(N)$) and space ($O(1)$ / $O(K)$) complexity.