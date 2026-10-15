"""First-N-lines (head) of a huge file with bounded memory.

Notation: F = file size, K = bytes in the first n lines, L = average line length, B = block size.

| Function      | Time   | Space              | Use when                                          |
|---------------|--------|--------------------|---------------------------------------------------|
| head_forward  | O(K+B) | O(K+B)             | n is small enough that the result fits in memory. |
| head_iter     | O(K)   | O(B + longest line)| n is huge, or you want to process lines lazily.   |
| head_islice   | O(K)   | O(n * L)           | Simplest code, text mode.                         |

All three stop reading as soon as n lines are found, so the cost depends on K, never on F.
Reading forwards needs no seek, so unlike tail_big_file.tail_backward these also work on
pipes and stdin.
"""

import os
from itertools import islice
from typing import Iterator


def head_forward(path: str, n: int, block_size: int = 8192) -> list[str]:
    """Read blocks from the start of the file until n lines are complete.

    Args:
        path: Path of the file to read.
        n: How many lines to return from the start. If n <= 0, an empty list is returned.
            If the file has fewer than n lines, all of its lines are returned.
        block_size: Number of bytes read per step. Larger values mean fewer system calls but
            more over-read when n is small. Use a multiple of the page size (4 KB to 64 KB).

    Returns:
        The first n lines in file order, decoded as UTF-8 without line endings.
        Invalid bytes are replaced with U+FFFD instead of raising.

    Raises:
        FileNotFoundError / PermissionError: If the file cannot be opened.
    """
    if n <= 0:
        return []

    # "rb": bytes mode, so "\n" is a single byte and counting it is a fast C-level operation.
    with open(path, "rb") as f:
        chunks: list[bytes] = []
        newlines = 0

        # n newlines mean n complete lines (the n-th line ends with the n-th newline).
        # Unlike tail_backward, there is no partial line at the front, so ">= n" is enough.
        while newlines < n:
            chunk = f.read(block_size)

            # Empty read means end of file: the file has fewer than n lines, return what we have.
            if not chunk:
                break

            chunks.append(chunk)
            newlines += chunk.count(b"\n")

    # The last block usually holds lines beyond n, so slice to n after splitting.
    # splitlines also returns a final line that has no trailing newline.
    data = b"".join(chunks)
    lines = data.splitlines()[:n]
    return [line.decode("utf-8", errors="replace") for line in lines]


def head_iter(path: str, n: int, block_size: int = 65536) -> Iterator[str]:
    """Yield the first n lines one at a time. Memory is O(block_size + longest line), not O(n).

    Args:
        path: Path of the file to read.
        n: How many lines to yield from the start. If n <= 0, nothing is yielded.
            If the file has fewer than n lines, all of its lines are yielded.
        block_size: Number of bytes read per step. It bounds memory together with the longest line.

    Yields:
        Each of the first n lines, decoded as UTF-8, without the trailing "\\n" or "\\r\\n".

    Raises:
        FileNotFoundError / PermissionError: If the file cannot be opened (on first iteration).
    """
    if n <= 0:
        return

    with open(path, "rb") as f:
        remaining = n

        # Bytes after the last newline of the previous block: the start of a line that is
        # still incomplete. It is glued to the next block.
        leftover = b""

        while remaining > 0:
            chunk = f.read(block_size)
            if not chunk:
                break

            # split leaves the (possibly incomplete) last piece at the end of the list.
            parts = (leftover + chunk).split(b"\n")
            leftover = parts.pop()

            for part in parts:
                # "\r\n" files leave a trailing "\r" after splitting on "\n".
                yield part.rstrip(b"\r").decode("utf-8", errors="replace")
                remaining -= 1
                if remaining == 0:
                    return

        # End of file reached with fewer than n lines: the last line has no trailing newline.
        if leftover:
            yield leftover.rstrip(b"\r").decode("utf-8", errors="replace")


def head_islice(path: str, n: int) -> list[str]:
    """Take the first n lines with itertools.islice. Simplest version, text mode.

    Args:
        path: Path of the file to read.
        n: How many lines to return from the start. If n <= 0, an empty list is returned.

    Returns:
        The first n lines, decoded as UTF-8 without line endings.
    """
    if n <= 0:
        return []

    with open(path, "r", encoding="utf-8", errors="replace") as f:
        # islice stops pulling from the file iterator after n lines, so the rest is never read.
        return [line.rstrip("\r\n") for line in islice(f, n)]


# Why this design
#   - The wanted lines are at the start, so reading forwards and stopping early costs O(K).
#     Compare with tail_deque, which has to read the whole file because the end is unknown.
#   - head_forward and head_iter work in bytes and split on b"\n", which is safe for UTF-8.
#   - head_iter is the memory-optimized one: it never holds more than a block plus one partial
#     line, so even n = 100 million lines does not need 100 million lines in memory.
#
# Multi-threading
#   - One file: not useful. Reading forwards is sequential and stops after K bytes, so there is
#     nothing to split. For huge K, the disk, not the CPU, is the limit.
#   - Many files: run head_forward per file in a bounded ThreadPoolExecutor, exactly like
#     tail_many_files in tail_big_file.py. Each call has its own file handle and local state.
