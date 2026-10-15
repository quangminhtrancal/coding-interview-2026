"""Last-N-lines of a huge file: two single-file options plus a multi-threaded wrapper.

Notation: F = file size, K = bytes in the last n lines, L = average line length, B = block size.

| Function        | Time   | Space     | Use when                                   |
|-----------------|--------|-----------|--------------------------------------------|
| tail_backward   | O(K+B) | O(K+B)    | Seekable file (the normal case). Fast.     |
| tail_deque      | O(F)   | O(n * L)  | Not seekable (pipe, stdin, .gz) or tiny file. |
| tail_many_files | max over files, run in parallel | sum of results | Many files at once. |
"""

import os
from collections import deque
from concurrent.futures import ThreadPoolExecutor


def tail_backward(path: str, n: int, block_size: int = 8192) -> list[str]:
    """Read blocks from the end of the file. O(K) time and space, K = bytes of last n lines.

    Args:
        path: Path of the file to read. It must be seekable (a regular file, not a pipe).
        n: How many lines to return from the end. If n <= 0, an empty list is returned.
            If the file has fewer than n lines, all of its lines are returned.
        block_size: Number of bytes read per step while walking backwards. Larger values mean
            fewer system calls but more over-read when n is small. Use a multiple of the page
            size (4 KB to 64 KB is typical).

    Returns:
        The last n lines in file order (oldest first), decoded as UTF-8 without line endings.
        Invalid bytes are replaced with U+FFFD instead of raising.

    Raises:
        FileNotFoundError / PermissionError: If the file cannot be opened.
    """
    # Nothing to return, and avoids opening the file at all.
    if n <= 0:
        return []

    # "rb": bytes mode, so offsets are real byte positions and "\n" is a single byte.
    # In text mode, seeking to an arbitrary offset can land inside a multi-byte character.
    # The with-block closes the file (and its OS handle) even if an exception happens.
    with open(path, "rb") as f:
        # seek(0, SEEK_END) jumps to the end in O(1) and returns that offset, which is the file size.
        # We use it as "pos", the start of the part of the file we have not read yet.
        pos = f.seek(0, os.SEEK_END)

        # Blocks are collected newest-to-oldest. A list is used instead of "data = chunk + data",
        # because repeated bytes concatenation copies everything each time (O(K^2) overall).
        chunks: list[bytes] = []

        # Running count of "\n" seen so far in the bytes we have read.
        newlines = 0

        # Stop when we hit the start of the file (pos == 0) or have seen more than n newlines.
        # n + 1 newlines guarantee the n-th line from the end is complete, because the newline
        # in front of it is inside what we read. Using ">= n" would let the first kept line be cut
        # off at a block boundary. (With a trailing newline, n lines need n + 1 newlines.)
        while pos > 0 and newlines <= n:
            # The last block may be smaller than block_size near the start of the file.
            read_size = min(block_size, pos)

            # Move the window back by one block. Going backwards is the whole point:
            # the lines we want are at the end, so we never touch the other F - K bytes.
            pos -= read_size

            # Jump to the start of that block and read exactly read_size bytes.
            f.seek(pos)
            chunk = f.read(read_size)
            chunks.append(chunk)

            # bytes.count runs in C, so counting is much faster than looping over lines in Python.
            newlines += chunk.count(b"\n")

    # The file is closed here, since we only need the bytes in memory from now on.
    # chunks are newest-first, so reverse them to restore the original byte order, then join once.
    data = b"".join(reversed(chunks))

    # splitlines handles "\n" and "\r\n" and does not return a trailing empty string.
    # data may start in the middle of a line, so we keep only the last n lines,
    # and the partial first line is dropped because we read more than n newlines.
    lines = data.splitlines()[-n:]

    # Decode only the n lines we return, not the whole block. Splitting happened on raw bytes,
    # which is safe for UTF-8 because b"\n" never appears inside a multi-byte character.
    # errors="replace" turns invalid bytes into U+FFFD instead of raising an exception.
    return [line.decode("utf-8", errors="replace") for line in lines]


def tail_deque(path: str, n: int) -> list[str]:
    """Stream the whole file keeping only n lines. O(F) time, O(n * L) space.

    Args:
        path: Path of the file to read. Unlike tail_backward, the file is only read forwards,
            so the same approach also works for streams that cannot seek.
        n: How many lines to return from the end. If n <= 0, an empty list is returned.
            If the file has fewer than n lines, all of its lines are returned.

    Returns:
        The last n lines in file order (oldest first), decoded as UTF-8 without line endings.
        Invalid bytes are replaced with U+FFFD instead of raising.

    Raises:
        FileNotFoundError / PermissionError: If the file cannot be opened.
    """
    if n <= 0:
        # deque(maxlen=0) would work, but returning early keeps both functions consistent.
        return []

    # Text mode: Python decodes and splits lines for us. "replace" avoids crashing on bad bytes.
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        # Iterating a file yields one line at a time using a buffer, so memory stays small.
        # deque(maxlen=n) drops the oldest line when line n + 1 arrives, which leaves the last n.
        # The price is that every one of the F bytes is read and decoded.
        # Lines keep their line ending, so strip "\r\n" to match tail_backward's output.
        return [line.rstrip("\r\n") for line in deque(f, maxlen=n)]


def tail_many_files(paths: list[str], n: int, max_workers: int = 8) -> dict[str, list[str]]:
    """Run tail_backward on many files in parallel. Returns {path: last n lines}.

    Args:
        paths: Files to read. Each one must be seekable. Duplicate paths are allowed, and the
            result keeps a single entry per distinct path.
        n: How many lines to return from the end of each file (same meaning as in tail_backward).
        max_workers: Maximum number of threads, which is also the maximum number of files open
            at the same time. Raise it for slow storage (network disks), lower it to limit load.

    Returns:
        A dict mapping each path to its last n lines (oldest first).

    Raises:
        FileNotFoundError / PermissionError: Re-raised from the first file (in input order)
            that fails. Results for the other files are discarded.
    """
    # Threads (not processes) are enough: the work is I/O bound, and file reads release the GIL
    # while waiting on the OS. tail_backward has no shared state (each call opens its own file
    # handle and uses local variables), so it is already thread-safe without any locks.
    # The pool also caps concurrency so we do not open thousands of files at once.
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        # map keeps the input order and re-raises the first exception when results are consumed.
        results = pool.map(lambda p: tail_backward(p, n), paths)
        return dict(zip(paths, results))


# Why this design, and how to make it multi-threaded
#
# Why tail_backward is the main answer
#   - The wanted lines are at the end, and seek() is O(1), so cost depends on K, not on F.
#   - Reading blocks (not single bytes) keeps system calls to about K / B.
#   - Bytes mode + split on b"\n" is safe for UTF-8 and avoids text-mode seek problems.
#
# Why tail_deque exists
#   - It is the simplest code and it also works on streams that cannot seek.
#   - It is O(F), so on 10 GB it needs about 7 s versus well under 1 s for tail_backward.
#
# Making ONE file multi-threaded: usually not worth it
#   - tail_backward reads only K bytes (often a few KB), which finishes in about a millisecond.
#     Thread start-up and coordination cost more than the work itself.
#   - If you did want it (huge n, so K is hundreds of MB), split the range [F - K_estimate, F)
#     into blocks and let each thread read its block with os.pread(fd, size, offset). pread takes
#     the offset as an argument, so threads share one file descriptor without a seek/read race.
#     Do NOT share a file object and call f.seek() + f.read() from several threads: another
#     thread can move the position between the two calls. Then join the blocks in order.
#   - For tail_deque, parallelizing is awkward: split the file into byte ranges, align each range
#     to the next "\n", keep a deque per range, and merge. Only the last ranges matter, which is
#     exactly what tail_backward already exploits, so you would rebuild it with more cost.
#
# Making MANY files multi-threaded: yes, see tail_many_files
#   - One task per file, a bounded ThreadPoolExecutor, no shared mutable state, no locks.
#   - Use processes (ProcessPoolExecutor) only if decoding becomes CPU bound, for example
#     with a very large n and a complicated parser per line.
