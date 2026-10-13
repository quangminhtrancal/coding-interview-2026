Confluent Coding Interview Preparation: Practical File Operations

Focus: File reading, parsing, transformation, manipulation, error handling, and optimization
Reference language: Python 3
Goal: Prepare for practical coding exercises and interviewer follow-up questions.

This is a preparation guide based on the interview description, not a list of verified Confluent interview questions. Treat the problems as realistic practice scenarios rather than predictions of exact interview questions.
Table of Contents
What the interviewer is evaluating
A repeatable problem-solving approach
Core file API knowledge
Basic file operations
File parsing and transformation
Aggregation and comparison problems
Large-file and performance problems
Reliability, correctness, and safety
Advanced follow-up questions
Testing strategy
Complexity cheat sheet
Mock interview exercises
Interview communication checklist
1. What the Interviewer Is Evaluating

The prompt emphasizes five skills.

Skill	What you should demonstrate
File handling	Correctly open, read, write, and close files
Problem solving	Clarify requirements and break problems into steps
Edge cases	Handle empty files, malformed records, missing files, and duplicates
Code structure	Write small, readable functions with clear responsibilities
Optimization	Understand memory usage, runtime, and I/O trade-offs
A typical evaluation scenario

Suppose you receive a file containing records:

alice,100
bob,200
alice,150
charlie,50


An interviewer might ask you to:

Read the file and calculate totals per user.
Ignore malformed records.
Sort users by total.
Write the results to another file.
Handle an empty input file.
Explain how your implementation changes for a 100 GB file.

A strong candidate solves the initial problem first, then adapts the implementation as the interviewer introduces constraints.

2. A Repeatable Problem-Solving Approach

Use this sequence for almost every file-processing question.

Step 1: Clarify requirements

Ask targeted questions before coding:

What is the file format: plain text, CSV, JSON, or binary?
Can the file be empty?
Can records be malformed?
Can the file be too large to fit in memory?
Should duplicate records be retained or removed?
Should output preserve the original order?
What should happen if the input or output file is missing?
Should the program stop on invalid data or skip it?
Can the input file change while being processed?

Do not ask every question mechanically. Ask the questions that materially affect the solution.

Step 2: Define the algorithm

For example, counting lines:

Open the file.
Initialize a counter.
Iterate through each line.
Increment the counter.
Return the count.
Step 3: Implement the simplest correct solution

Prefer:

Context managers such as with open(...).
Iteration over the file instead of reading everything into memory.
Small functions.
Explicit encoding.
Clear error handling.
Step 4: Test edge cases

At minimum, consider:

Empty file.
One record.
Multiple records.
Missing file.
Invalid data.
Duplicate records.
Very large file.
Unexpected whitespace or line endings.
Step 5: Discuss complexity

Explain both time and space complexity.

For example, counting lines in a file with 
𝑁
 characters takes 
𝑂
(
𝑁
)
 time and approximately 
𝑂
(
1
)
 auxiliary memory when processed line by line, excluding internal buffering and the current line.

Step 6: Optimize only when needed

Start with correctness. If the interviewer introduces large files, memory constraints, or throughput requirements, adjust the design accordingly.

3. Core File API Knowledge

These are the operations you should know without looking them up.

3.1 Opening files
with open("input.txt", "r", encoding="utf-8") as file:
    for line in file:
        print(line.rstrip("\n"))


Common modes:

Mode	Meaning
"r"	Read an existing file
"w"	Write; truncate an existing file or create a new one
"a"	Append to a file
"x"	Create a new file; fail if it already exists
"rb"	Read binary data
"wb"	Write binary data
"r+"	Read and write without initially truncating
"w+"	Read and write, truncating first

Interview trap: Opening a file in "w" mode destroys its existing contents immediately. Use it only when replacing the contents is intended.

3.2 Reading methods
file.read()       # Entire file as one string
file.readline()   # One line
file.readlines()  # All lines as a list

for line in file: # Streaming, one line at a time
    process(line)


For large files, prefer iteration unless the algorithm genuinely needs the entire contents.

3.3 File paths

Use pathlib for readable path operations:

from pathlib import Path

path = Path("data") / "input.txt"

if path.is_file():
    print(path.stat().st_size)


Remember that the current working directory may differ from the directory containing your source code.

3.4 Common exceptions
FileNotFoundError: the path does not exist.
PermissionError: the process lacks permission.
IsADirectoryError: a directory was supplied where a file was expected.
UnicodeDecodeError: the bytes cannot be decoded using the chosen encoding.
OSError: other operating-system-level failures.

Catch exceptions at the level where you can handle them meaningfully. Do not silently swallow all exceptions.

4. Basic File Operation Problems
Problem 1: Read a File and Print Its Contents

Question: Write a function that reads a text file and returns its contents.

Answer
from pathlib import Path

def read_file(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")

Complexity
Time: 
𝑂
(
𝑁
)
, where 
𝑁
 is the file size.
Space: 
𝑂
(
𝑁
)
, because the entire file is loaded into memory.
Follow-up: What if the file is huge?

Use streaming:

def print_file(path: str) -> None:
    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            print(line, end="")


This avoids storing the entire file in memory.

Edge cases
Missing file.
Empty file.
Invalid text encoding.
Permission denied.
Very long individual lines.
Problem 2: Count Lines in a File

Question: Count the number of lines without loading the entire file into memory.

Answer
def count_lines(path: str) -> int:
    with open(path, "r", encoding="utf-8") as file:
        return sum(1 for _ in file)

Complexity
Time: 
𝑂
(
𝑁
)
, where 
𝑁
 is the number of characters or bytes processed.
Auxiliary space: 
𝑂
(
1
)
, excluding file buffering and the current line.
Follow-up: Does an empty file have zero lines?

Yes. This implementation returns 0.

Follow-up: What about a file containing hello without a final newline?

It returns 1, which is generally the expected interpretation when counting text records.

Follow-up: What if the file contains hello\nworld\n?

It returns 2, not 3. A trailing newline terminates the second line; it does not necessarily imply another record.

Important distinction: If the interviewer defines line count as the number of newline characters, that is a different requirement. Clarify the intended semantics.

Problem 3: Count Words in a File

Question: Count the words in a text file.

Answer
def count_words(path: str) -> int:
    total = 0

    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            total += len(line.split())

    return total

Complexity
Time: 
𝑂
(
𝑁
)
.
Auxiliary space: proportional to the current line and the temporary list created by split().
Follow-up: How do you define a word?

This implementation defines a word as a whitespace-separated token. Punctuation remains attached to words.

For example:

hello, world!


Counts as two words.

If the requirement calls for linguistic tokenization, Unicode-aware word boundaries, or punctuation removal, the algorithm must change.

Optimization

For extremely long individual lines, a character-by-character tokenizer may reduce temporary allocations, although it increases implementation complexity.

Problem 4: Copy a File

Question: Copy a file to a destination path.

Answer
import shutil

def copy_file(source: str, destination: str) -> None:
    shutil.copyfile(source, destination)


This copies the file contents but does not preserve all file metadata.

Use shutil.copy2() if preserving common metadata such as modification times is desirable.

Follow-up: What if the source and destination are the same file?

The operation should fail rather than overwrite the source. shutil.copyfile() detects this case.

Follow-up: How do you avoid partially written destination files?

Write to a temporary file in the destination directory, flush and close it, and then replace the destination using os.replace().

This can provide atomic visibility of the replacement on supported filesystems, but atomic visibility is not the same as crash durability.

Problem 5: Append a Line to a File

Question: Append a line to an existing file, creating it if necessary.

Answer
def append_line(path: str, text: str) -> None:
    with open(path, "a", encoding="utf-8") as file:
        file.write(text + "\n")

Follow-up: What happens if the file already ends with a newline?

An extra newline is appended after the new text, as expected.

Follow-up: What if multiple processes write concurrently?

Do not assume that application-level append operations provide complete record-level atomicity on every platform and filesystem. Multiple writers may require file locking, a single-writer architecture, or a durable queue.

5. File Parsing and Transformation Problems
Problem 6: Remove Blank Lines

Question: Read a file and write a new file without blank lines.

Answer
def remove_blank_lines(source: str, destination: str) -> None:
    with open(source, "r", encoding="utf-8") as src, \
         open(destination, "w", encoding="utf-8") as dst:

        for line in src:
            if line.strip():
                dst.write(line)

Complexity
Time: 
𝑂
(
𝑁
)
.
Auxiliary space: 
𝑂
(
𝐿
)
, where 
𝐿
 is the longest line processed.
Follow-up: Does this remove lines containing spaces or tabs?

Yes. strip() removes surrounding whitespace for the blank-line check.

Follow-up: What if source and destination are the same path?

This implementation is unsafe for in-place transformation because opening the destination in "w" mode truncates the file. Use a temporary output file and replace the original after successful processing.

Problem 7: Remove Duplicate Lines

Question: Remove duplicate lines while preserving their first occurrence and original order.

Example

Input:

apple
banana
apple
orange
banana


Output:

apple
banana
orange

Answer
def deduplicate_lines(source: str, destination: str) -> None:
    seen = set()

    with open(source, "r", encoding="utf-8") as src, \
         open(destination, "w", encoding="utf-8") as dst:

        for line in src:
            if line not in seen:
                seen.add(line)
                dst.write(line)

Complexity
Expected time: 
𝑂
(
𝑁
)
 total processing for typical hash-based operations, with the cost of hashing each line.
Space: 
𝑂
(
𝑈
)
 stored lines, where 
𝑈
 is the total size of unique lines.
Important edge cases
Should Apple and apple be considered equal?
Should trailing spaces matter?
Should hello and hello\n be equivalent?
Should the first occurrence or last occurrence be retained?
Is the input too large for the set to fit in memory?
Follow-up: How would you deduplicate a huge file?

Options include:

External sorting followed by adjacent duplicate removal.
Partitioning records by hash and processing each partition.
Using a database with a unique key.
Using a disk-backed key-value store.

A Bloom filter can reduce memory usage for approximate membership checks, but false positives mean it cannot guarantee exact deduplication by itself.

Problem 8: Replace Text in a File

Question: Replace every occurrence of a substring with another substring.

Answer
def replace_text(
    source: str,
    destination: str,
    old: str,
    new: str,
) -> None:
    with open(source, "r", encoding="utf-8") as src, \
         open(destination, "w", encoding="utf-8") as dst:

        for line in src:
            dst.write(line.replace(old, new))

Complexity
Time: 
𝑂
(
𝑁
)
 for ordinary substring replacement, with the cost of generating the resulting text.
Auxiliary space: proportional to the current line and transformed output.
Follow-up: Can you replace a string across line boundaries?

Not with this line-by-line implementation, because each line is processed independently. A streaming matcher with overlap handling or whole-file processing may be needed.

Follow-up: How would you replace text in place?

Use a temporary file and replace the original after success. Do not truncate the original before the replacement has been fully generated.

Problem 9: Parse a CSV File and Calculate Totals

Question: A CSV file contains user,amount. Calculate the total amount for each user.

Example
user,amount
alice,100
bob,200
alice,150


Expected result:

alice: 250
bob: 200

Answer
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

Why use csv.DictReader?

CSV files can contain quoted commas, escaped quotes, and embedded newlines. Splitting each line on commas does not correctly handle all valid CSV input.

Follow-up: How do you handle malformed rows?

Choose an explicit policy:

Fail immediately with the row number.
Skip invalid records and report them.
Collect errors and return them alongside the valid results.

Do not silently discard bad data without explaining that behavior.

Follow-up: What if amounts represent money?

Use decimal.Decimal instead of float when exact decimal arithmetic is required.

Complexity
Time: 
𝑂
(
𝑁
)
 for parsing all input characters, plus aggregation overhead.
Space: 
𝑂
(
𝐾
)
, where 
𝐾
 is the number of distinct users.
Problem 10: Parse a JSON Lines File

Question: Each line contains one JSON object. Count events by type.

Example
{"type":"click","user":"alice"}
{"type":"view","user":"bob"}
{"type":"click","user":"charlie"}


Expected result:

click: 2
view: 1

Answer
import json
from collections import Counter

def count_event_types(path: str) -> dict[str, int]:
    counts = Counter()

    with open(path, "r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue

            try:
                record = json.loads(line)
                event_type = record["type"]

                if not isinstance(event_type, str):
                    raise ValueError("'type' must be a string")

                counts[event_type] += 1

            except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
                raise ValueError(
                    f"Invalid record on line {line_number}: {exc}"
                ) from exc

    return dict(counts)

Follow-up: Why process one JSON object per line?

It supports streaming and avoids loading the entire dataset into memory.

Follow-up: What if the file contains one large JSON array?

Use json.load() for manageable files, or a streaming JSON parser for large arrays.

Follow-up: Should malformed records be skipped?

That depends on the requirements. Failing fast provides stronger guarantees about completeness; skipping with metrics may be appropriate for resilient ingestion pipelines.

Problem 11: Merge Multiple Sorted Files

Question: Merge two sorted text files into one sorted output file.

Example

File A:

1
4
7


File B:

2
3
8


Output:

1
2
3
4
7
8

Answer
from itertools import zip_longest

def merge_sorted_files(
    file_a: str,
    file_b: str,
    destination: str,
) -> None:
    sentinel = object()

    with open(file_a, encoding="utf-8") as a, \
         open(file_b, encoding="utf-8") as b, \
         open(destination, "w", encoding="utf-8") as out:

        left = next(a, sentinel)
        right = next(b, sentinel)

        while left is not sentinel and right is not sentinel:
            if int(left.strip()) <= int(right.strip()):
                out.write(left)
                left = next(a, sentinel)
            else:
                out.write(right)
                right = next(b, sentinel)

        if left is not sentinel:
            out.write(left)
            for line in a:
                out.write(line)

        if right is not sentinel:
            out.write(right)
            for line in b:
                out.write(line)

Complexity
Time: 
𝑂
(
𝑛
+
𝑚
)
, where 
𝑛
 and 
𝑚
 are the number of records in the two files.
Auxiliary space: 
𝑂
(
1
)
 records, excluding buffers and the current record.
Assumptions
Both files are sorted numerically.
Each record contains a valid integer.
The output is distinct from both input files.
Follow-up: What if there are 100 sorted files?

Use a min-heap containing the next record from each file. The complexity becomes 
𝑂
(
𝑇
log
⁡
𝑘
)
, where 
𝑇
 is the total number of records and 
𝑘
 is the number of files.

Problem 12: Find the Most Frequent Word

Question: Find the most frequent word in a text file.

Answer
from collections import Counter
import re

def most_frequent_word(path: str) -> tuple[str, int] | None:
    counts = Counter()

    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            words = re.findall(r"\b\w+\b", line.casefold())
            counts.update(words)

    if not counts:
        return None

    word, count = min(
        counts.items(),
        key=lambda item: (-item[1], item[0]),
    )

    return word, count

Design choices
casefold() performs case normalization suitable for caseless matching.
The regular expression defines the tokenization policy.
Ties are broken alphabetically for deterministic results.
An empty file returns None.
Complexity
Time: 
𝑂
(
𝑁
)
 expected for tokenization and counting.
Space: 
𝑂
(
𝑉
)
, where 
𝑉
 is the vocabulary size.
Follow-up: What if the file is too large?

Streaming avoids storing the entire file, but exact word counts still require memory for the vocabulary. Use partitioning, external aggregation, or a database if the number of unique words is too large.

6. File Comparison and Aggregation Problems
Problem 13: Compare Two Files

Question: Determine whether two files contain identical bytes.

Answer
def files_equal(path_a: str, path_b: str) -> bool:
    chunk_size = 1024 * 1024

    with open(path_a, "rb") as a, open(path_b, "rb") as b:
        while True:
            chunk_a = a.read(chunk_size)
            chunk_b = b.read(chunk_size)

            if chunk_a != chunk_b:
                return False

            if not chunk_a:
                return True

Complexity
Time: 
𝑂
(
𝑁
)
 in the worst case.
Auxiliary space: 
𝑂
(
𝐶
)
, where 
𝐶
 is the chunk size.
Follow-up: Would a hash be better?

A cryptographic hash can provide a compact fingerprint, but equal hashes are not a mathematical proof of identical content. For strict byte equality, direct comparison is definitive.

Comparing file sizes first can quickly reject files with different lengths.

Follow-up: How do you compare text while ignoring whitespace?

Define normalization rules first, then compare normalized content. Be aware that line endings, Unicode normalization, and whitespace inside quoted data may affect correctness.

Problem 14: Find Records Present in One File but Not Another

Question: Given two files containing IDs, write IDs that appear in file A but not in file B.

Answer
def difference_file(
    file_a: str,
    file_b: str,
    destination: str,
) -> None:
    with open(file_b, encoding="utf-8") as b:
        ids_b = {line.rstrip("\r\n") for line in b}

    with open(file_a, encoding="utf-8") as a, \
         open(destination, "w", encoding="utf-8") as out:

        for line in a:
            record_id = line.rstrip("\r\n")

            if record_id not in ids_b:
                out.write(line)

Complexity
Time: 
𝑂
(
𝑛
+
𝑚
)
 expected.
Space: 
𝑂
(
𝑚
)
 for the set of IDs from file B.
Follow-up: What if both files are huge?

Use external sorting and a merge-difference algorithm, or a disk-backed index.

Follow-up: Are duplicates preserved?

Yes. If an ID appears multiple times in A and never appears in B, each occurrence is written. If unique output is required, deduplication must be added.

Problem 15: Split a Large File into Smaller Files

Question: Split a text file into chunks of at most 1,000 lines each.

Answer
from pathlib import Path

def split_file(
    source: str,
    output_dir: str,
    lines_per_file: int = 1000,
) -> None:
    if lines_per_file <= 0:
        raise ValueError("lines_per_file must be positive")

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    with open(source, "r", encoding="utf-8") as src:
        part_number = 1

        while True:
            lines = []

            for _ in range(lines_per_file):
                line = src.readline()
                if line == "":
                    break
                lines.append(line)

            if not lines:
                break

            part_path = output_path / f"part_{part_number:04d}.txt"

            with open(part_path, "w", encoding="utf-8") as dst:
                dst.writelines(lines)

            part_number += 1

Complexity
Time: 
𝑂
(
𝑁
)
.
Auxiliary space: proportional to the chunk size and the total size of its lines.
Follow-up: Split by bytes instead of lines?

Read and write binary chunks. Be careful if the output must remain valid UTF-8: an arbitrary byte boundary can split a multibyte character.

Follow-up: What if a line is several gigabytes long?

A line-based limit does not protect against an individual enormous line. A robust implementation may need a maximum record size or a chunk-based parsing strategy.

Problem 16: Read the Last N Lines

Question: Return the last 10 lines of a file without loading the entire file into memory.

Answer
from collections import deque

def tail(path: str, n: int = 10) -> list[str]:
    if n < 0:
        raise ValueError("n must be non-negative")

    with open(path, "r", encoding="utf-8") as file:
        return list(deque(file, maxlen=n))

Complexity
Time: 
𝑂
(
𝑁
)
, because the entire file is read.
Auxiliary space: 
𝑂
(
𝑛
𝐿
)
 approximately, where 
𝐿
 is the average retained line length.
Follow-up: Is this optimal for a huge file?

Not necessarily. A reverse-reading algorithm can seek backward from the end and scan until it finds enough newline delimiters. This can reduce I/O when the file is large and only a few trailing lines are required.

Reverse reading requires additional care with UTF-8 multibyte characters and line-ending conventions.

7. Large-File and Performance Problems
Problem 17: Process a File That Does Not Fit in Memory

Question: How would you process a 100 GB log file on a machine with limited RAM?

Answer

Use streaming:

def process_large_file(path: str) -> None:
    with open(path, "r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            process_record(line_number, line)


def process_record(line_number: int, line: str) -> None:
    # Implement the required business logic here.
    pass

What to explain
Do not use read() or readlines() for the whole file.
Process records incrementally.
Keep only the minimum state needed.
Batch output writes when appropriate.
Track malformed records and processing metrics.
Consider external sorting or database aggregation if the algorithm requires global ordering or large indexes.
Complexity

A single-pass algorithm generally takes 
𝑂
(
𝑁
)
 time. Its memory consumption depends on retained state, not simply on the file size.

Critical distinction: Streaming solves the input-memory problem, but it does not automatically solve algorithms that require remembering every unique key.

Problem 18: Process Only New Data Added to a Log File

Question: How would you process only new lines appended to a file?

Answer: Basic approach

Maintain a file offset and read from the last successfully processed position.

def read_from_offset(path: str, offset: int) -> tuple[list[bytes], int]:
    if offset < 0:
        raise ValueError("offset must be non-negative")

    lines = []

    with open(path, "rb") as file:
        file.seek(offset)

        while True:
            line = file.readline()

            if not line:
                break

            lines.append(line)

        new_offset = file.tell()

    return lines, new_offset

Why use binary mode?

Binary offsets correspond to byte positions. Text-mode offsets may be opaque values rather than arbitrary byte offsets suitable for simple arithmetic.

Follow-up: What if the writer has only written half a line?

The basic implementation may return an incomplete final record. A production implementation should retain the unfinished bytes and process that record only after a newline arrives, unless partial records are valid.

Follow-up: What if the file rotates or is truncated?

Track file identity and size, detect truncation, and define how to handle rotated files. A simple offset alone is insufficient.

Follow-up: What if the process crashes after processing a line but before saving the offset?

You can get duplicate processing after restart. Saving offsets and processing results requires a consistent checkpoint strategy. Exactly-once behavior generally needs idempotency or transactional coordination.

Problem 19: Sort a Very Large File

Question: Sort a file containing millions of records that cannot fit into memory.

Answer: External merge sort
Read a manageable chunk.
Sort the chunk in memory.
Write the sorted chunk to a temporary file.
Repeat until all input is processed.
Merge the sorted temporary files using a min-heap.
Write the final sorted output.
Remove temporary files after successful completion.
Complexity

For 
𝑁
 records and memory-sized runs, external merge sort typically requires 
𝑂
(
𝑁
log
⁡
𝑁
)
 comparison work and multiple sequential disk passes.

If there are 
𝑘
 sorted runs, merging with a heap costs 
𝑂
(
𝑁
log
⁡
𝑘
)
.

Follow-up: Why not load everything and call sorted()?

That may be simplest for small files, but memory usage grows with the entire dataset. External sorting trades additional disk I/O for bounded RAM usage.

Follow-up: What if sorting must be stable?

Preserve the original order of equal keys, for example by including an original sequence number in the sort key or using a stable sorting algorithm at every stage.

Problem 20: Process Multiple Files in a Directory

Question: Read every .log file in a directory and count total lines.

Answer
from pathlib import Path

def count_directory_lines(directory: str) -> int:
    root = Path(directory)
    total = 0

    for path in root.glob("*.log"):
        if not path.is_file():
            continue

        with path.open("r", encoding="utf-8") as file:
            total += sum(1 for _ in file)

    return total

Follow-up: Should subdirectories be included?

Use rglob("*.log") if recursive traversal is required.

Follow-up: What if one file cannot be read?

Choose a clear policy: fail the operation, or record the error and continue. If continuing, report which files were skipped so the result is not mistaken for a complete count.

Follow-up: What about symbolic links?

Decide whether to follow them. Recursive traversal can encounter cycles or files outside the intended directory if symlinks are followed without appropriate safeguards.

8. Reliability, Correctness, and Safety
Problem 21: Write Output Safely Without Corrupting an Existing File

Question: Transform an input file and replace an existing output file only after the transformation succeeds.

Answer
import os
import tempfile
from pathlib import Path

def transform_file_safely(
    source: str,
    destination: str,
) -> None:
    source_path = Path(source)
    destination_path = Path(destination)

    # The temporary file is created in the destination directory.
    fd, temp_name = tempfile.mkstemp(
        dir=destination_path.parent,
        prefix=f".{destination_path.name}.",
        suffix=".tmp",
    )

    try:
        with os.fdopen(fd, "w", encoding="utf-8") as out:
            with source_path.open("r", encoding="utf-8") as src:
                for line in src:
                    out.write(line.upper())

            out.flush()
            os.fsync(out.fileno())

        os.replace(temp_name, destination_path)

    except BaseException:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise

Why this is safer
The old destination remains untouched while the temporary file is generated.
A transformation error prevents the replacement.
The temporary file is on the destination filesystem, which helps support atomic replacement.
The file is flushed and synchronized before replacement.
Limitations
This example assumes the destination directory already exists.
os.replace() can fail due to permissions, open-file restrictions on some platforms, or filesystem errors.
Atomic replacement does not guarantee complete crash durability of directory metadata on every filesystem.
If the source and destination are the same path, the example is still safe because the source is read before the replacement happens.

Interview point: Atomic visibility, durability, and transactional correctness are related but different guarantees.

Problem 22: Handle Malformed Input Records

Question: Process a file containing one integer per line. Skip invalid records and report the valid total and the number of rejected lines.

Answer
def sum_valid_integers(path: str) -> tuple[int, int]:
    total = 0
    rejected = 0

    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            value = line.strip()

            if not value:
                continue

            try:
                total += int(value)
            except ValueError:
                rejected += 1

    return total, rejected

Follow-up: Should blank lines count as invalid?

That depends on the specification. Here, blank lines are ignored and are not counted as rejected records.

Follow-up: How would you debug rejected records in production?

Track line numbers and error categories. If the data is sensitive, avoid logging entire raw records unnecessarily.

Follow-up: Why not use except Exception?

It catches unrelated failures and can hide programming bugs. Catch the exceptions you expect and can handle.

Problem 23: Prevent Path Traversal

Question: Your program receives a filename from a user and must only access files inside a permitted directory.

Answer
from pathlib import Path

def safe_path(base_directory: str, user_filename: str) -> Path:
    base = Path(base_directory).resolve()
    candidate = (base / user_filename).resolve()

    if not candidate.is_relative_to(base):
        raise ValueError("Path escapes the permitted directory")

    return candidate

Follow-up: Is this sufficient for every security-sensitive application?

No. Filesystem state can change between validation and opening. Symbolic links and concurrent filesystem modifications can create time-of-check-to-time-of-use problems.

For stronger guarantees, use platform-appropriate descriptor-relative file APIs, restrict symlink traversal, and apply operating-system permissions.

Problem 24: Handle Unicode and Line Endings

Question: A file contains mixed LF, CRLF, and non-ASCII characters. How do you read and rewrite it safely?

Answer

For ordinary text:

with open(
    "input.txt",
    "r",
    encoding="utf-8",
    newline=None,
) as file:
    for line in file:
        process_record(line)


With newline=None, Python performs universal newline handling and translates recognized line endings to \n during reading.

If exact byte preservation matters, read and write binary data instead.

Follow-up: What if the input is not valid UTF-8?

Confirm the actual encoding. Use a documented alternative encoding if appropriate. errors="replace" or errors="ignore" can lose information and should only be used intentionally.

9. Advanced Follow-Up Questions

These questions test whether you understand practical implementation trade-offs beyond the basic solution.

Q1. What is the difference between buffered and unbuffered I/O?

Buffered I/O collects data in memory to reduce the number of system calls. Unbuffered or lower-level I/O can offer more control but may increase overhead if used inefficiently.

Python file objects normally use buffering by default.

Q2. When would you use binary mode?

Use binary mode for byte-exact comparison, hashes, compressed files, arbitrary binary formats, and precise byte offsets.

Q3. When would you use a generator?

When records should be produced lazily instead of materialized into a list.

def read_records(path: str):
    with open(path, encoding="utf-8") as file:
        for line in file:
            yield line.rstrip("\r\n")


The file remains open while the generator is being consumed. Ensure consumers do not abandon the generator without appropriate cleanup when resource lifetime matters.

Q4. How would you make file processing idempotent?

Make repeated execution produce the same logical result without duplicating effects. Techniques include deterministic output, unique record IDs, checkpoints, atomic replacement, and deduplication.

Appending records is not automatically idempotent.

Q5. How would you recover after a process crashes?

Use durable checkpoints, temporary files, replayable inputs, and idempotent processing. Decide whether partially completed output can be discarded or must be recovered.

Q6. How would you handle concurrent readers and writers?

Clarify the required consistency model. Depending on the system, consider atomic file replacement, locks, immutable files, versioned filenames, or a database.

Q7. Would you use threads or processes to read multiple files?

First measure the bottleneck. Concurrent I/O may help when waiting on storage dominates. CPU-heavy parsing may benefit from processes, but serialization and coordination have costs. Multiple readers can also hurt performance on a single disk.

Q8. How would you handle compressed files?

Use the appropriate library, such as gzip.open() for gzip-compressed data. Compression reduces storage and potentially network transfer, but decompression consumes CPU. Some compression formats do not support efficient arbitrary seeking.

Q9. How would you detect whether a file changed during processing?

Compare relevant metadata before and after reading, or process immutable snapshots. Metadata checks alone do not guarantee that contents remained unchanged.

Q10. How would you benchmark a solution?

Measure wall-clock time, CPU usage, peak memory, bytes read and written, and behavior under realistic input sizes. Repeat runs and distinguish warm-cache from cold-cache behavior where possible.

Q11. How would you avoid partial output when a record is invalid?

Validate each record before committing its effects. If the entire file must succeed or fail as a unit, write to a temporary output and replace it only after validation succeeds.

Q12. What if the file contains records larger than the available memory?

A line iterator still needs to construct a line. Use bounded chunk reads and an incremental parser, or impose and enforce a maximum record size.

Q13. How do you avoid exhausting file descriptors?

Close files promptly with context managers, avoid opening every file at once, and limit concurrency.

Q14. How would you preserve permissions and metadata?

Choose APIs appropriate to the requirement, such as shutil.copy2(), and account for platform differences and ownership or permission restrictions.

Q15. What if the output directory does not exist?

Create it explicitly when appropriate:

from pathlib import Path

Path("output").mkdir(parents=True, exist_ok=True)


Clarify whether creating missing directories is part of the expected behavior.

Q16. Why is splitting a CSV file at arbitrary line counts sometimes unsafe?

Quoted CSV fields can contain embedded newline characters. Splitting at arbitrary physical line boundaries may break logical records. Use a CSV-aware parser when record boundaries matter.

Q17. Why is a checksum useful?

Checksums and cryptographic hashes help detect accidental changes and compare content fingerprints. A cryptographic hash is useful for integrity checks, but it does not replace authentication or access controls.

Q18. How would you process a directory with millions of files?

Avoid materializing all paths in memory. Use incremental directory traversal, bounded concurrency, efficient metadata access, and careful handling of errors and symlinks.

10. Testing Strategy

A practical interview solution should include a small, deliberate test plan.

Test case checklist
Test case	Expected behavior
Empty file	Return the correct empty result
One line	Process exactly one record
No final newline	Handle the final record
Blank lines	Follow the stated policy
Duplicate records	Preserve or remove as required
Malformed record	Fail or skip according to specification
Missing input	Raise or report a clear error
Unreadable file	Handle permission errors appropriately
Unicode characters	Decode using the intended encoding
Large file	Avoid unnecessary whole-file memory usage
Output already exists	Preserve or replace it according to requirements
Input equals output	Avoid accidental truncation
Disk full	Report failure and avoid claiming success
Interrupted execution	Leave recoverable or clearly invalid output
Concurrent access	Follow the specified consistency guarantees
Example: Test line counting
import tempfile
import unittest
from pathlib import Path

class TestCountLines(unittest.TestCase):
    def test_empty_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "empty.txt"
            path.write_text("", encoding="utf-8")
            self.assertEqual(count_lines(str(path)), 0)

    def test_multiple_lines(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.txt"
            path.write_text("a\nb\nc\n", encoding="utf-8")
            self.assertEqual(count_lines(str(path)), 3)

    def test_no_final_newline(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.txt"
            path.write_text("a\nb", encoding="utf-8")
            self.assertEqual(count_lines(str(path)), 2)

if __name__ == "__main__":
    unittest.main()


The count_lines() function from Problem 2 can be tested directly with these cases.

What the interviewer wants to hear

Do not just say, "I will test it." Name concrete cases and explain why each matters.

11. Complexity Cheat Sheet

Let:

𝑁
 = input size.
𝐾
 = number of distinct keys.
𝐿
 = maximum line length.
𝑘
 = number of sorted input files.
Operation	Typical time	Typical auxiliary space
Read entire file	
𝑂
(
𝑁
)
	
𝑂
(
𝑁
)

Count lines by iteration	
𝑂
(
𝑁
)
	
𝑂
(
1
)
 excluding buffers
Stream a transformation	
𝑂
(
𝑁
)
	
𝑂
(
𝐿
)

Count unique words	
𝑂
(
𝑁
)
 expected	
𝑂
(
𝐾
)

Deduplicate with a set	
𝑂
(
𝑁
)
 expected	
𝑂
(
𝐾
)
 in record storage
Compare files byte by byte in chunks	
𝑂
(
𝑁
)
 worst case	
𝑂
(
𝐶
)

Merge two sorted files	
𝑂
(
𝑛
+
𝑚
)
	
𝑂
(
1
)
 records
Merge 
𝑘
 sorted files with a heap	
𝑂
(
𝑁
log
⁡
𝑘
)
	
𝑂
(
𝑘
)
 records
In-memory sorting	
𝑂
(
𝑁
log
⁡
𝑁
)
	Depends on implementation
External merge sort	
𝑂
(
𝑁
log
⁡
𝑁
)
 comparison work	Bounded RAM plus temporary disk
Read the last 
𝑛
 lines with a deque	
𝑂
(
𝑁
)
	
𝑂
(
𝑛
𝐿
)
 approximately

Here, 
𝐶
 is the chosen chunk size.

These are typical bounds, not guarantees for every parser or filesystem. State your assumptions during the interview.

12. Mock Interview Exercises

Try solving these without reading the answers first. Each exercise combines multiple practical skills.

Exercise A: Log Summary

Question: A log file contains:

INFO User logged in
ERROR Database timeout
INFO User logged out
ERROR Connection failed


Write a function that counts records by log level and writes the summary to a new file.

Expected approach:

Stream the input.
Extract and validate the log level.
Count levels with a dictionary or Counter.
Write a deterministic summary.
Decide how malformed lines should be handled.

Follow-up: How would you process a 50 GB log file? How would you report malformed lines?

Exercise B: Find the Largest File

Question: Find the largest regular file in a directory.

Expected approach:

Traverse the directory.
Inspect file metadata.
Track the path with the largest size.
Define behavior for an empty directory and unreadable entries.

Follow-up: Should symlinks be followed? Should the traversal be recursive?

Exercise C: CSV Filtering

Question: Given a CSV of transactions, write only rows whose amount is greater than 100.

Expected approach:

Use csv.DictReader and csv.DictWriter.
Validate the amount field.
Decide whether the header should be retained.
Handle invalid records explicitly.

Follow-up: How would you process multiple CSV files with slightly different schemas?

Exercise D: File Change Detection

Question: Determine whether a file has changed since its last processing.

Expected approach:

Explain the difference between checking modification time, size, and a content hash.
Use a persisted fingerprint if necessary.
Decide how to handle a file changing during processing.

Follow-up: How would you handle a file whose modification timestamp has insufficient precision?

Exercise E: Merge Event Files

Question: Several files contain timestamp-sorted events. Merge them into a single timestamp-sorted file.

Expected approach:

Use a min-heap with one current record per file.
Define behavior for equal timestamps.
Validate record formats.
Preserve deterministic ordering when timestamps tie.

Follow-up: What happens if one file is not actually sorted?

Exercise F: Safe In-Place Transformation

Question: Remove a field from every JSON Lines record without corrupting the source if a record is malformed.

Expected approach:

Read and parse incrementally.
Validate each record.
Write to a temporary file.
Replace the original only after successful completion if all-or-nothing behavior is required.
Clean up temporary files on failure.

Follow-up: What if the transformed output is larger than the available disk space?

Exercise G: Compare Two Large Datasets

Question: Find all IDs that exist in one file but not the other, where neither file fits into memory.

Expected approach:

Explain the limitations of in-memory sets.
Consider external sorting and a merge-based comparison.
Discuss temporary disk requirements and duplicate semantics.
Exercise H: Recover From a Crash

Question: A process reads records, updates an output file, and saves a checkpoint. How do you prevent missing or duplicated records after a crash?

Expected approach:

Identify the order of operations.
Discuss the crash window between processing and checkpointing.
Use idempotent writes or transactional storage where possible.
Explain why exactly-once effects require stronger coordination than merely saving a line number.
13. Interview Communication Checklist

Use this checklist during the live coding session.

Before coding
Restate the problem in your own words.
Clarify the input format and output format.
Ask about file size and memory constraints.
Clarify how invalid data should be handled.
Identify assumptions and edge cases.
While coding
Start with a simple correct algorithm.
Use context managers for resource cleanup.
Prefer streaming when possible.
Separate parsing, transformation, and output when it improves clarity.
Handle errors intentionally.
Use meaningful variable and function names.
Explain important decisions as you make them.
After coding
Run a happy-path test.
Test an empty file.
Test malformed data or missing files.
Check output correctness.
State time and space complexity.
Explain what changes for large files.
Discuss whether partial output is possible after a failure.
Final Preparation Priorities

If preparation time is limited, prioritize these topics in order:

File fundamentals: reading, writing, appending, copying, paths, context managers, and exceptions.
Streaming: line counting, filtering, transforming, and aggregating without loading entire files.
Parsing: CSV, JSON Lines, malformed records, encoding, and line endings.
Collections and algorithms: counting, deduplication, sorting, merging, and file comparison.
Reliability: temporary files, atomic replacement, partial writes, checkpoints, and idempotency.
Optimization: time complexity, memory usage, external sorting, chunking, and large-file processing.
Communication: clarifying requirements, explaining trade-offs, testing edge cases, and iterating on feedback.
The core principle

For a practical file-operations interview, the strongest solution is not necessarily the most sophisticated one. It is the simplest solution that correctly meets the requirements, handles realistic failure cases, and can be adapted when the interviewer adds constraints.

Practice recommendation: Implement Problems 2, 7, 9, 11, 13, 17, and 21 from scratch. Together, they cover the most reusable file-handling patterns: streaming, state tracking, parsing, merging, comparison, bounded memory, and safe output replacement.