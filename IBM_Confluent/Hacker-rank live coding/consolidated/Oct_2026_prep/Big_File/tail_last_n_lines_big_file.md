# Read the Last N Lines of a 10 GB File (Python)

## Problem

Return the last `N` lines of a file that is about 10 GB, like `tail -n N`. The file does not fit in memory, and `N` is small compared to the file size.

## Answer in One Line

Seek to the end of the file and read fixed-size blocks backwards until you have seen more than `N` newlines. Then split only that tail and return the last `N` lines.

- Time: $O(K)$, where $K$ is the size of the last `N` lines. It is not $O(\text{file size})$.
- Space: $O(K)$.

## Why Not the Obvious Approaches

| Approach | Time | Space | Problem |
|---|---|---|---|
| `f.readlines()[-N:]` | O(F) | O(F) = 10 GB | Out of memory. |
| `deque(f, maxlen=N)` | O(F) | O(N * L) | Memory is fine, but it reads all 10 GB: tens of seconds of disk I/O to keep a few lines. |
| Read backwards in blocks (recommended) | O(K) | O(K) | Reads only the tail, so it is usually milliseconds. |

- `F` is the file size.
- `L` is the average line length.
- `K` is roughly `N * L`, plus at most one extra block.

## Why Backward Block Reading Works

1. `seek()` jumps to any offset in O(1). The OS does not scan the file to do it.
2. The last `N` lines sit at the end of the file, so reading from the end touches only those bytes.
3. Reading one byte at a time backwards is slow because of syscall overhead. Reading blocks (for example 8 KB, matching the page size) amortizes that cost.
4. Work in bytes (`"rb"`), not text:
   - Seeking to arbitrary offsets in text mode is unreliable for multi-byte encodings.
   - `b"\n"` never appears inside a UTF-8 multi-byte character, so splitting on it is safe.
   - Decode only the final `N` lines, after splitting.
5. A trailing newline means the block we read may end with an empty piece. Stopping when `newlines > N` (not `>= N`) guarantees the first line we keep is complete, not cut off at a block boundary.

## Implementation

```python
import os


def tail(path: str, n: int, block_size: int = 8192) -> list[str]:
    """Return the last n lines of a file without reading the whole file."""
    if n <= 0:
        return []

    with open(path, "rb") as f:
        pos = f.seek(0, os.SEEK_END)
        chunks: list[bytes] = []
        newlines = 0

        # n + 1 newlines guarantee the n-th line from the end is complete.
        while pos > 0 and newlines <= n:
            read_size = min(block_size, pos)
            pos -= read_size
            f.seek(pos)
            chunk = f.read(read_size)
            chunks.append(chunk)
            newlines += chunk.count(b"\n")

    data = b"".join(reversed(chunks))
    lines = data.splitlines()[-n:]
    return [line.decode("utf-8", errors="replace") for line in lines]


if __name__ == "__main__":
    for line in tail("/var/log/big.log", 10):
        print(line)
```

### Walkthrough

File content: `a\nb\nc\n`, with `N = 2`.

1. `pos` starts at 6 (the file size). The block covers the whole file, and `newlines = 3`, which is greater than 2.
2. `data.splitlines()` gives `[a, b, c]`.
3. `[-2:]` gives `[b, c]`.

## Complexity

Let `F` be the file size, `K` the number of bytes in the last `N` lines, and `B` the block size.

- Time: $O(K + B)$. It performs $\lceil K / B \rceil$ seeks and reads, plus one pass to count newlines and split.
  - In practice this is milliseconds, even for a 10 GB file, because the cost does not depend on `F`.
  - Compare with a full scan: 10 GB at roughly 0.5 to 2 GB/s is 5 to 20 seconds or more.
- Space: $O(K + B)$. This holds the chunks and the joined bytes. It does not depend on `F`.
- I/O: about $K / B$ block reads. The OS page cache makes repeated tails of the same file even cheaper.

## Alternative 1: Simple Streaming With `deque`

Use it when the file is small, or when you must handle a stream that cannot seek (pipes, stdin).

```python
from collections import deque


def tail_stream(path: str, n: int) -> list[str]:
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return [line.rstrip("\n") for line in deque(f, maxlen=n)]
```

- Time: O(F). It reads the whole file.
- Space: O(N * L). `deque(maxlen=n)` discards old lines as new ones arrive.
- Trade-off: the simplest code and constant memory, but it is slow on a huge file.

## Alternative 2: `mmap`

```python
import mmap


def tail_mmap(path: str, n: int) -> list[str]:
    with open(path, "rb") as f, mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
        end = len(mm)
        # Ignore one trailing newline so it is not counted as an empty last line.
        if end and mm[end - 1] == ord("\n"):
            end -= 1
        start = end
        for _ in range(n):
            idx = mm.rfind(b"\n", 0, start)
            if idx == -1:
                start = 0
                break
            start = idx + 1 if _ == n - 1 else idx
        return mm[start:end].decode("utf-8", errors="replace").splitlines()
```

- Time: O(K). `rfind` scans backwards, and the OS pages in only the touched pages.
- Space: O(K) of resident pages, and the data is not copied until you slice it.
- Trade-off: no manual block logic, but it is harder to get right at the edges. It behaves differently across platforms and cannot map an empty file.

## Edge Cases to Mention

- File has fewer than `N` lines: the loop reaches `pos == 0` and returns the whole file.
- Trailing newline or no trailing newline: handled by the `newlines > n` condition.
- Windows line endings (`\r\n`): `splitlines()` removes both characters.
- Empty file: the loop does not run, and the result is `[]`.
- `N <= 0`: return `[]` early.
- Very long lines, or a file with no newlines (for example minified JSON): memory grows to the size of the last `N` lines. Cap the total bytes read if the input is untrusted.
- Non-UTF-8 or invalid bytes: `errors="replace"` avoids a crash. UTF-16 and UTF-32 break the `b"\n"` assumption, so decode differently or reject them.
- File being appended to during the read: take the size once at the start (as done here) so the result is a consistent snapshot.
- Compressed files (`.gz`): you cannot seek backwards cheaply, so use the `deque` approach.

## Follow-Up Questions and Answers

- Why not read one byte at a time backwards? Each read is a syscall, so 1 MB of tail costs about a million syscalls instead of about 128.
- How do I choose the block size? Use a multiple of the page size, usually 4 KB to 64 KB. Larger blocks mean fewer syscalls but more over-read for small `N`.
- How do I implement `tail -f`? Start with `tail()`, then remember the offset and poll for new bytes. Handle log rotation by checking whether the inode changed or the size shrank.
- How do I make it a generator for huge `N`? Yield lines as you walk backwards, and keep only the leftover partial line between blocks. Memory stays $O(B + L_{\max})$.
- How do I scale it to many files? Run `tail` per file in a thread pool, because the work is I/O bound and `seek` and `read` release the GIL.

## Hands-On Test on a Real 10 GB File

The files below are in this folder. They test the two main options (`tail_backward` and `tail_deque`) on a real 10 GiB log.

| File | Purpose |
|---|---|
| `tail_big_file.py` | `tail_backward` (backward block read) and `tail_deque` (stream the whole file). |
| `make_big_log.py` | Writes filler log lines until the file is 10 GiB, then appends `line 1` to `line 100` as the last 100 lines. |
| `test_tail_big_file.py` | Asserts that both options return exactly `line 1` to `line 100`, and prints the timing of each. |

### Run the Test

Run these commands from this folder:

```bash
python3 make_big_log.py /tmp/big_10gb.log
python3 test_tail_big_file.py /tmp/big_10gb.log
```

- The log goes to `/tmp` so the 10 GiB file stays out of the repo. Delete it afterwards with `rm /tmp/big_10gb.log`.
- Generating it takes a few seconds. Make sure at least 11 GiB of disk is free.

### Why the Last 100 Lines Are `line 1` to `line 100`

- Filler lines look like `2026-10-14T12:00:00Z INFO service=orders request_id=... msg=filler entry ...`, so they can never be confused with the expected result.
- The expected result is `["line 1", ..., "line 100"]`, so any off-by-one error, missing line, or partial first line makes the assertion fail.

### Result (Python 3.9, macOS, local SSD)

```text
file: /tmp/big_10gb.log (10.00 GiB)
tail_backward: OK in 6.15 ms
tail_deque:    OK in 7.28 s
both options match the expected last 100 lines
```

- `tail_backward` read about one 8 KB block. Its time does not depend on the file size.
- `tail_deque` had to read all 10 GiB, which took about 7 seconds. That is roughly 1,000 times slower for the same answer.
- The test also checks `n = 1`, `5` and `250`. The `n = 250` case reaches into the filler lines, and the two options must agree there.
- Timings vary with disk speed and the OS page cache. The ratio is what matters.
