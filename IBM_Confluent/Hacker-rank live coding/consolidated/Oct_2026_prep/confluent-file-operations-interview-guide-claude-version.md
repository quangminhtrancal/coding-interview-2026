# Confluent "Practical File Operations" Interview: Questions and Answers (Python)

The round description you pasted says the focus is *how you approach the problem, structure your code and handle edge cases*, using file APIs, with the ability to run code on example files. This guide has two parts:

1. **What candidates have actually reported** for Confluent (with links), and
2. **Other questions this kind of round can plausibly ask**, which are my extrapolation, labelled as such.

Every question has: clarifying questions to ask, the approach and *why*, runnable Python, edge cases and follow-ups. All code blocks were extracted and run with tests (see the end of each section).

> **Caveat on sources.** The reports below come from public interview-experience posts (Blind, LeetCode Discuss, Exponent, PracHub). I only saw search snippets of them, several are paywalled or partially hidden, and candidates paraphrase. Treat the exact prompts as approximate. The "predicted" questions are not reports from anyone.

## Contents

1. [What has been reported](#1-what-has-been-reported)
2. [How to run the interview](#2-how-to-run-the-interview-the-part-they-are-grading)
3. [Question inventory](#3-question-inventory)
4. Reported questions: [Q1 tail -n](#q1-implement-tail--n-for-a-very-large-file-reported-most-frequent) · [Q2 tail -f](#q2-follow-mode-tail--f-predicted-follow-up) · [Q3 search a huge file](#q3-find-a-word-or-phrase-in-a-huge-file-reported) · [Q4 sensor health](#q4-sensor-health-from-heartbeats-reported-spec-reconstructed) · [Q5 LRU get/put/getAverage](#q5-get--put--getaverage-on-a-stream-reported-spec-reconstructed) · [Q6 memory-bounded reads](#q6-process-a-file-bigger-than-memory-reported-theme)
5. Predicted questions: [Q7 top-K](#q7-top-k-most-frequent-words--ips-predicted) · [Q8 external sort and merge](#q8-sort-or-merge-files-larger-than-memory-predicted) · [Q9 dedup](#q9-deduplicate-lines-in-a-huge-file-predicted) · [Q10 binary search a sorted log](#q10-binary-search-a-sorted-log-by-timestamp-predicted) · [Q11 grep with context and log aggregation](#q11-grep-with-context-and-log-aggregation-predicted) · [Q12 rotating log writer](#q12-size-based-rotating-log-writer-predicted) · [Q13 atomic write, copy, duplicates](#q13-safe-file-writes-copy-and-duplicate-finder-predicted) · [Q14 CSV and JSONL](#q14-csv-and-json-lines-processing-predicted) · [Q15 parallel byte ranges](#q15-split-a-file-for-parallel-processing-predicted) · [Q16 append-only log with compaction](#q16-append-only-log-with-index-and-compaction-predicted-kafka-flavoured)
6. [Linux / OS questions that were reported alongside](#6-linux-and-os-fundamentals-reported-in-the-same-loops)
7. [Java NIO cheat table](#7-java-nio-equivalents)
8. [Edge-case checklist](#8-edge-case-checklist)
9. [Sources](#9-sources)

---

## 1. What has been reported

| Reported item | What was said | Source |
|---|---|---|
| **Round format** | A recruiter told a candidate one round is "a practical problem working with files and files APIs". Commenters guessed: traverse a directory, read/write/append, buffered readers/writers, copy a file, temp files, `Files`/`Paths` utilities, watch out for out-of-memory on big files, remember to close streams | Blind thread "Confluent coding round on files" |
| **`tail -n` on arbitrary file sizes** | Repeatedly reported as a coding question. One report gives a restricted API: `read(k)`, `movePointer(pos)`, `getSize()`, "write pseudocode to stream the last N lines; the file may be much larger than memory". Another lists the grading points: backward block reads, chunk boundaries, trailing-newline semantics, bounded memory, binary-vs-text, safe decoding, mutation assumptions | PracHub "Implement File Tail and Sensor Health", PracHub "Implement tail -n for a Very Large File", PracHub super-day report, Blind "implement tail and word search" |
| **Interviewer pushback on a naive tail** | A candidate who seeked backwards and scanned for `\n` one character at a time was told that means *a lot of system calls*, i.e. read in blocks | Blind "implement tail and word search" |
| **Search a word, then a phrase/sentence, in a huge line-oriented file** | "Each line is one sentence." First find a word, follow-up: a phrase or sentence. A hashmap optimization was enough. Another report: substring search where the haystack is a huge file and a match can straddle two chunks | PracHub super-day report, Blind "implement tail and word search", PracHub "Search Words and Phrases in a Large Line-Oriented File" (listed as related) |
| **Sensor health from heartbeat timestamps** | Second task in the same onsite as `tail`; evaluates "data-structure and time-window reasoning for tracking sensor liveness from heartbeat timestamps". Exact API not visible to me | PracHub "Implement File Tail and Sensor Health" |
| **`get`, `put`, `getAverage` on a data stream, "LRU-style"** | Garbled in the original post; listed as a coding question in a senior-role loop | PracHub super-day report |
| **Memory optimization while reading a huge file** | A low-level-design onsite round: "optimizing memory while reading a huge file"; working, runnable code was expected; follow-up on further memory-access optimization; "struggled a little with API knowledge" | LeetCode Discuss offer post |
| **File seek / chunked-read bug** | One candidate lost points by not understanding `seek` and mishandling chunked reads (the classic chunk-boundary bug) | PracHub super-day report |
| **Linux depth** | How a command executes, `ls`/`pwd`/`ip`/`ifconfig` internally, permissions and groups | PracHub super-day report |
| **General** | "Make sure to be fluent with file system APIs"; "provide the most optimal solutions" | Exponent report |

**Takeaway:** the reported core is `tail -n` plus *searching a big file* plus *bounded-memory streaming*. If you are fluent in block-wise reading, boundary handling and `seek`, you cover most of it. The rest of this guide stretches into neighbouring problems that use the same skills.

---

## 2. How to run the interview (the part they are grading)

The prompt says problem-solving and communication matter more than the final code. A reliable script:

1. **Clarify before coding** (30 to 60 seconds). Ask:
   - File size vs memory? Can I assume it fits? (Never assume yes.)
   - Text or binary? Encoding (UTF-8)? Line endings (`\n` vs `\r\n`)? Is the last line newline-terminated?
   - Is the file static, or being appended to / rotated while I read it?
   - Sorted? Single query or many queries against the same file?
   - Which API am I allowed (random access `seek`, or only forward streams)? Which language/runtime, and can I run tests?
2. **State the brute force and its cost**, then improve. ("Read all lines into a list: O(file) memory. `deque(maxlen=n)` forward scan: O(n) memory but O(file) I/O. Backward block reads: O(answer) I/O.")
3. **Think in I/O, not CPU.** Cost is dominated by bytes read and number of syscalls. Read in blocks (64 KB to 1 MB), not byte by byte.
4. **Name the invariants at boundaries.** Most file-bug stories are "a record straddles two reads". Say how you carry state across chunks.
5. **Write the simple correct version first, run it on tiny inputs** (empty file, one line, no trailing newline), then optimize.
6. **Use context managers** (`with open(...)`) so files close on every path; mention it out loud.
7. **Talk through complexity** in terms of file size `F`, answer size, block size `B`.

---

## 3. Question inventory

| # | Question | Status | Core skill |
|---|---|---|---|
| Q1 | `tail -n` for a very large file (also with a restricted `read/movePointer/getSize` API) | **Reported** | Backward block reads, chunk boundaries |
| Q2 | `tail -f` follow mode (rotation, truncation) | Predicted follow-up | Polling, inode/size checks, partial lines |
| Q3 | Find a word / phrase / sentence in a huge file; chunk-straddling substring search; repeated queries | **Reported** | Overlap handling, inverted index |
| Q4 | Sensor liveness from heartbeats | **Reported** (spec reconstructed) | Time windows, ordered dict |
| Q5 | `get/put/getAverage` over a stream, LRU style | **Reported** (spec reconstructed) | LRU + running sum |
| Q6 | Process a file bigger than memory (line/word count) | **Reported theme** | Streaming, carry-over |
| Q7 | Top-K frequent words/IPs | Predicted | Counter, heap, hash partitioning |
| Q8 | Sort/merge files larger than memory | Predicted | External sort, k-way merge |
| Q9 | Deduplicate lines in a huge file | Predicted | Set, hash partitioning |
| Q10 | Binary search a sorted log by timestamp | Predicted | Seek, line alignment |
| Q11 | `grep -A/-B/-C`; errors-per-minute; malformed lines | Predicted | deque, regex, robustness |
| Q12 | Size-based rotating log writer | Predicted | Rename order, flush |
| Q13 | Atomic write, safe copy, duplicate-file finder | Predicted | `os.replace`, `os.walk`, hashing |
| Q14 | CSV and JSON-lines processing, hash join | Predicted | `csv` module, error handling |
| Q15 | Split a file into line-aligned ranges for parallel work | Predicted | Offsets, `readline` alignment |
| Q16 | Append-only log with index and compaction (Kafka-flavoured) | Predicted | Binary records, CRC, recovery |
| Q17 | Linux / OS fundamentals | **Reported** | Syscalls, permissions, FDs |

---

## Q1. Implement `tail -n` for a very large file (reported, most frequent)

> *Given a seekable file and `n`, return the last `n` lines without reading the whole file. Variant: you only get `read(k)`, `movePointer(pos)`, `getSize()`.* Graded on: backward block reads, chunk boundaries, trailing-newline semantics, bounded memory, binary vs text, decoding, complexity.

**Clarifying questions:** Is the file static while I read? (We assume a snapshot.) Is a trailing newline part of the last line, or does it terminate it? (POSIX: it *terminates* it, so `a\nb\n` has 2 lines, `a\nb` also has 2.) `n` larger than the number of lines? `n == 0`? Encoding?

**Approaches, from naive to expected**

| Approach | Memory | I/O | Comment |
|---|---|---|---|
| `f.readlines()[-n:]` | whole file | whole file | Fine for tiny files only; the classic mistake |
| `deque(f, maxlen=n)` | O(n lines) | whole file, sequential | Simple and often acceptable; reads everything |
| `seek` to end, scan back **one byte at a time** for `\n` | O(n lines) | O(answer) bytes but **one syscall per byte** | Reportedly rejected by an interviewer for the syscall count |
| **Read backwards in blocks of B bytes** until you have seen more than `n` newlines | O(answer + B) | O(answer) bytes, `answer/B` syscalls | The expected answer |

**Design and why**

- Work in **bytes**, not text. Split on `b"\n"`. In UTF-8 the byte `0x0A` never appears inside a multi-byte character (continuation bytes are `0x80..0xBF`), so splitting bytes on newline is safe; **decode each line afterwards**. That is *not* true for UTF-16/32, so state the assumption.
- Blocks are read from the end towards the start; collect them in a list and `b"".join(reversed(blocks))` once at the end. (`data = block + data` in a loop is O(n²).)
- **Stop condition:** we need `n` complete lines. If the file ends with `\n`, the final newline terminates the last line, so we need **more than `n` newlines** in the collected suffix to be sure the first of our `n` lines is complete (the text before the first newline we saw might be the tail of a longer line). Using `newlines > n` is correct whether or not the file ends in a newline (it may read one extra block, never fewer than needed).
- **Boundary correctness** falls out of this design: we never decode or split a block in isolation, only the concatenation, so a line (or a UTF-8 character) straddling two blocks is never cut.
- Trailing newline: `split(b"\n")` yields a final empty string when the data ends with `\n`; drop it. An empty file gives `[]`. A file of just `\n` is one empty line.
- `\r\n`: lines keep a trailing `\r` (this is what real `tail` does too). Strip it if the interviewer wants "logical" lines.
- **Mutation assumption:** we use a size snapshot taken once. If the file is appended to meanwhile, we still return a consistent suffix of the snapshot; if it is truncated, a short read can happen, so we raise instead of returning garbage.

**Code** (works against the restricted API; `PathFile` adapts a real file to it)

```python
# file: tail.py
import os
import time


class PathFile:
    """The restricted API from the prompt, backed by a real file."""

    def __init__(self, path):
        self._f = open(path, "rb")
        self._size = os.fstat(self._f.fileno()).st_size      # snapshot of the size

    def read(self, k):
        return self._f.read(k)

    def movePointer(self, pos):
        self._f.seek(pos)

    def getSize(self):
        return self._size

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self._f.close()


def tail_lines(api, n, block_size=64 * 1024):
    """Last n lines as bytes (newline stripped). Reads only the file's tail, in blocks."""
    if n <= 0:
        return []
    pos = api.getSize()
    blocks, newlines = [], 0
    while pos > 0 and newlines <= n:             # need MORE than n newlines (see notes)
        step = min(block_size, pos)
        pos -= step
        api.movePointer(pos)
        block = api.read(step)
        if len(block) != step:                   # file shrank or a non-regular file
            raise OSError("short read: file changed while reading")
        blocks.append(block)
        newlines += block.count(b"\n")
    data = b"".join(reversed(blocks))            # one join; never block + data in a loop
    lines = data.split(b"\n")
    if lines[-1] == b"":                         # data ended with "\n" (or was empty)
        lines.pop()
    return lines[-n:]                            # first element may be partial; it is dropped here


def tail(path, n, encoding="utf-8"):
    """Decode AFTER splitting on bytes; safe for UTF-8 because 0x0A never occurs inside a character."""
    with PathFile(path) as f:
        return [line.decode(encoding, "replace") for line in tail_lines(f, n)]
```

**Complexity:** time and I/O O(bytes in the last `n` lines + B); memory the same; syscalls ≈ `answer / B`. Versus `deque(f, maxlen=n)`: O(F) I/O.

**Follow-ups to expect**

- *"Why not `readline()` backwards?"* There is no such call; reverse scanning must be built from block reads.
- *"What block size?"* A multiple of the filesystem block/page size (4 KB multiples; 64 KB to 1 MB is typical); bigger = fewer syscalls but more over-read for small `n`.
- *"Could you use `mmap`?"* Yes: `mmap.rfind(b"\n", 0, end)` loops over the mapped file with no copying; the OS pages in only what you touch. Caveats: 32-bit address space, `SIGBUS` if the file is truncated underneath you, and `mmap` of an empty file raises.
- *"Streaming output?"* Return a generator, or print as you go once you know the start offset: find the start of the last `n` lines first, then `seek` there and stream forward with `shutil.copyfileobj`. That keeps memory O(B) regardless of line length.
- *"Binary / no newlines at all?"* The loop reads the entire file in the worst case (one huge line); mention a cap or a streaming fallback.

### Tests

```python
# file: tail.py
import io
import random
import tempfile


def _ref(data, n):
    """Independent oracle: forward scan with BytesIO."""
    lines = [l[:-1] if l.endswith(b"\n") else l for l in io.BytesIO(data).readlines()]
    return lines[-n:] if n > 0 else []


def test_tail():
    rnd = random.Random(7)
    cases = [b"", b"\n", b"a", b"a\n", b"a\nb", b"a\nb\n", b"\n\n\n", b"a\r\nb\r\n",
             "héllo\nwörld\n日本語\n".encode()]
    for _ in range(150):
        lines = [bytes(rnd.choice(b"abc \xc3\xa9") for _ in range(rnd.randint(0, 9)))
                 for _ in range(rnd.randint(0, 12))]
        cases.append(b"\n".join(lines) + rnd.choice([b"", b"\n"]))
    with tempfile.TemporaryDirectory() as tmp:
        for i, data in enumerate(cases):
            path = os.path.join(tmp, f"f{i}")
            with open(path, "wb") as f:
                f.write(data)
            for n in (0, 1, 2, 5, 50):
                for bs in (1, 2, 3, 7, 64):          # tiny blocks force every boundary case
                    with PathFile(path) as api:
                        assert tail_lines(api, n, bs) == _ref(data, n), (data, n, bs)
        path = os.path.join(tmp, "utf8")
        with open(path, "wb") as f:
            f.write("a\nb\n日本語\n".encode())
        assert tail(path, 2) == ["b", "日本語"]
```

---

## Q2. Follow mode, `tail -f` (predicted follow-up)

> *Now keep printing new lines as they are appended. Handle log rotation and truncation.*

**Design and why**

- Open, seek to end, then loop: `read` new bytes. **Keep a `partial` buffer**: a writer may have flushed half a line, and emitting it would split one log line into two. Only yield up to the last `\n`.
- No new data → sleep a short poll interval (or use `inotify`/`kqueue`/`watchdog`; polling is the portable answer, say so).
- Detect **rotation** (`logrotate` renames the file and creates a new one): the path now has a different **inode** (`st_ino`). Detect **truncation** (`copytruncate`): same inode but `st_size < our offset`. In both cases reopen and read from the start. Importantly, only check *after* draining the old file, otherwise you lose its last lines.
- `stop` is injected so the generator can be tested (real `tail -f` runs forever).

```python
# file: tail.py
def follow(path, stop, poll=0.05, from_end=True):
    """Yield complete new lines (bytes) as they are appended. Survives rotation and truncation."""
    f = open(path, "rb")
    try:
        if from_end:
            f.seek(0, os.SEEK_END)
        inode = os.fstat(f.fileno()).st_ino
        partial = b""
        while True:
            chunk = f.read(64 * 1024)
            if chunk:
                partial += chunk
                *lines, partial = partial.split(b"\n")   # last element = incomplete line (maybe empty)
                yield from lines
                continue
            if stop():
                return
            try:
                st = os.stat(path)
            except FileNotFoundError:
                st = None                                # mid-rotation: wait for the new file
            if st is not None and (st.st_ino != inode or st.st_size < f.tell()):
                f.close()
                f = open(path, "rb")                     # rotated or truncated: read from the start
                inode = os.fstat(f.fileno()).st_ino
                partial = b""
                continue
            time.sleep(poll)
    finally:
        f.close()
```

```python
# file: tail.py
import threading


def test_follow():
    with tempfile.TemporaryDirectory() as tmp:
        p = os.path.join(tmp, "app.log")
        with open(p, "wb") as f:
            f.write(b"old\n")
        stop, out = threading.Event(), []
        t = threading.Thread(target=lambda: out.extend(follow(p, stop.is_set, poll=0.01)))
        t.start()
        time.sleep(0.1)
        with open(p, "ab") as f:
            f.write(b"a\nb"); f.flush(); time.sleep(0.1)   # "b" is a partial line: must not be emitted yet
            f.write(b"c\n")
        time.sleep(0.1)
        os.rename(p, p + ".1")                              # rotation: new inode
        with open(p, "wb") as f:
            f.write(b"dddd\n")
        time.sleep(0.15)
        with open(p, "wb") as f:                            # truncation: same inode, smaller size
            f.write(b"e\n")
        time.sleep(0.15)
        stop.set(); t.join(5)
        assert not t.is_alive()
        assert out == [b"a", b"bc", b"dddd", b"e"], out


if __name__ == "__main__":
    test_tail()
    test_follow()
    print("tail OK")
```

**Follow-ups:** `tail -F` vs `-f` (retry by name vs by descriptor); a slow consumer; very long lines without newline (cap the partial buffer); multiple files.

---

## Q3. Find a word or phrase in a huge file (reported)

> *A file; each line is a sentence. Find a word. Follow-up: find a phrase/sentence. (Variant: substring search where the "haystack" is a huge file and a match can straddle two chunks. Variant: many queries against the same file.)*

Answer in **three levels**, and say which you are on:

**Level 1: one query, line-oriented, stream it.** `for line in f` reads a buffer at a time and holds one line, so memory is O(longest line). Match **tokens**, not substrings, if the question says "word" (`cat` must not match `concatenate`). Case-fold if told to.

**Level 2: substring in a byte stream, with chunk boundaries.** This is the bug the reports mention. A match can start in chunk *k* and end in chunk *k+1*. **Keep the last `len(needle) - 1` bytes of the previous chunk** and search `tail + chunk`. Why exactly `m-1`? A match that lies completely inside those `m-1` bytes is impossible (shorter than the needle), so nothing is reported twice, and any match that started earlier than that window would have been found in the previous iteration. Track the file offset of `buf[0]` so you report global positions.

**Level 3: many queries, so index once.** Build an **inverted index** `word → [line numbers]` (the "hashmap optimization" from the report) plus an array of **byte offsets per line** so you can jump to any line with `seek` instead of rescanning. A **phrase** query = intersect the posting lists of its words (cheap candidate filter), then **verify** on the real line, because "red" and "car" both occurring does not make "red car" a phrase. An exact **sentence** query = hash of the whole line → line numbers, verify on hit. Trade-off: the index costs memory (roughly the vocabulary plus one int per word occurrence per line); for files bigger than that, store the index on disk (sorted terms, like an SSTable) or use SQLite FTS / a real search engine, and say so.

```python
# file: search.py
import re
from array import array
from collections import defaultdict


def find_all(path, needle: bytes, chunk_size=1 << 20):
    """Yield the byte offset of every (possibly overlapping) occurrence of needle. Streaming, chunk-safe."""
    m = len(needle)
    if m == 0:
        raise ValueError("empty needle")
    carry, consumed = b"", 0                       # carry = last m-1 bytes of what we already searched
    with open(path, "rb") as f:
        while chunk := f.read(chunk_size):
            buf = carry + chunk
            base = consumed - len(carry)           # file offset of buf[0]
            i = buf.find(needle)
            while i != -1:
                yield base + i
                i = buf.find(needle, i + 1)        # i + 1 so overlapping matches are found
            carry = buf[-(m - 1):] if m > 1 else b""   # NOT buf[-0:], which would be the whole buffer
            consumed += len(chunk)


_WORD = re.compile(r"\w+")


def tokens(text):
    return _WORD.findall(text.lower())


def grep_word(path, word):
    """Level 1: one-shot, streaming, whole-word match."""
    w = word.lower()
    with open(path, encoding="utf-8", errors="replace") as f:
        for lineno, line in enumerate(f):
            if w in tokens(line):
                yield lineno, line.rstrip("\r\n")


class LineIndex:
    """Level 3: build once, query many times. Line numbers are 0-based."""

    def __init__(self, path):
        self.path = path
        self._offsets = array("Q")                      # byte offset of each line start: 8 bytes per line
        self._postings = defaultdict(list)              # word -> ascending line numbers
        pos = 0
        with open(path, "rb") as f:
            for n, raw in enumerate(f):
                self._offsets.append(pos)
                pos += len(raw)
                for w in set(tokens(raw.decode("utf-8", "replace"))):   # set: one posting per line
                    self._postings[w].append(n)

    def line(self, n):
        with open(self.path, "rb") as f:
            f.seek(self._offsets[n])                    # random access instead of rescanning
            return f.readline().decode("utf-8", "replace").rstrip("\r\n")

    def find_word(self, word):
        return list(self._postings.get(word.lower(), ()))

    def find_phrase(self, phrase):
        want = tokens(phrase)
        if not want:
            return []
        lists = [self._postings.get(t) for t in want]
        if any(l is None for l in lists):
            return []
        out = []
        for n in sorted(set(lists[0]).intersection(*lists[1:])):    # candidates: all words present
            have = tokens(self.line(n))                              # verify: words adjacent, in order
            if any(have[i:i + len(want)] == want for i in range(len(have) - len(want) + 1)):
                out.append(n)
        return out
```

```python
# file: search.py
import os
import random
import tempfile


def test_find_all():
    rnd = random.Random(3)
    with tempfile.TemporaryDirectory() as tmp:
        p = os.path.join(tmp, "f")
        for _ in range(100):
            data = bytes(rnd.choice(b"ab") for _ in range(rnd.randint(0, 60)))
            with open(p, "wb") as f:
                f.write(data)
            for needle in (b"a", b"ab", b"aba", b"aaaa", b"abab"):
                want = [i for i in range(len(data) - len(needle) + 1) if data[i:i + len(needle)] == needle]
                for chunk in (1, 2, 3, 5, 1 << 20):                     # tiny chunks force straddling
                    assert list(find_all(p, needle, chunk)) == want, (data, needle, chunk)


def test_line_index():
    text = ("The red car stopped.\nA red bus and a car.\nconcatenate cats\n"
            "Red car, red car!\nlast line without newline")
    with tempfile.TemporaryDirectory() as tmp:
        p = os.path.join(tmp, "s.txt")
        with open(p, "w", encoding="utf-8") as f:
            f.write(text)
        idx = LineIndex(p)
        assert idx.find_word("car") == [0, 1, 3]
        assert idx.find_word("cat") == []                                 # not a substring match
        assert [n for n, _ in grep_word(p, "CAR")] == [0, 1, 3]
        assert idx.find_phrase("red car") == [0, 3]                       # line 1 has both words, not adjacent
        assert idx.find_phrase("missing word") == []
        assert idx.line(4) == "last line without newline"


if __name__ == "__main__":
    test_find_all()
    test_line_index()
    print("search OK")
```

**Follow-ups:** case-insensitive/Unicode normalization; *regex or wildcard* queries (index doesn't help; stream); *sorted file* (binary search by key, see Q10); *the index doesn't fit in memory* (on-disk sorted terms, or partition by hash like Q7); *multi-pattern search* (Aho-Corasick); *file changes* (re-index appended region only: remember the last indexed offset).

---

## Q4. Sensor health from heartbeats (reported; spec reconstructed)

> The report says only: "track sensor liveness from heartbeat timestamps" (time-window reasoning). Here is the natural API; **state your assumptions out loud** if the real prompt differs.
> `heartbeat(sensor_id, ts)`, `is_alive(sensor_id, now)`, `dead_sensors(now)`, `alive_count(now)`. A sensor is **alive** if `now - last_heartbeat <= timeout`.

**Design and why**

- A dict `sensor → last ts` answers `is_alive` in O(1).
- To list **dead** sensors without scanning all of them, keep sensors ordered by last heartbeat: an `OrderedDict`, `move_to_end` on each heartbeat. The *oldest* are at the front, so `dead_sensors` walks from the front and stops at the first live one: **O(#dead)** rather than O(#sensors).
- That ordering is correct **if heartbeats arrive in non-decreasing timestamp order** (a stream). If they can be out of order across sensors, use a **min-heap of `(ts, sensor)` with lazy deletion** (skip entries whose ts is stale versus the dict), at O(log n) per heartbeat.
- Decide and state: boundary (`<=` vs `<`), unknown sensors (treated as not alive), duplicate or late heartbeats (ignored if older than what we have).
- If the heartbeats come from a **file**, stream it line by line and feed `heartbeat`; never load it all. If the question is "which sensors were down for more than T at any point", you need per-sensor gaps (sort by `(sensor, ts)` or keep `prev_ts` per sensor and emit when `ts - prev_ts > T`).

```python
# file: streams.py
from collections import OrderedDict


class SensorMonitor:
    """alive  <=>  now - last_heartbeat <= timeout.  Assumes heartbeats arrive in non-decreasing ts order."""

    def __init__(self, timeout):
        self.timeout = timeout
        self._last = OrderedDict()                # sensor_id -> last ts, oldest first

    def heartbeat(self, sensor_id, ts):
        prev = self._last.get(sensor_id)
        if prev is not None and ts <= prev:       # duplicate / late heartbeat: ignore
            return
        self._last[sensor_id] = ts
        self._last.move_to_end(sensor_id)         # keeps the dict ordered by last heartbeat

    def is_alive(self, sensor_id, now):
        ts = self._last.get(sensor_id)
        return ts is not None and now - ts <= self.timeout

    def dead_sensors(self, now):
        dead = []
        for sensor_id, ts in self._last.items():  # oldest first
            if now - ts <= self.timeout:
                break                             # everything after this one is newer, so alive
            dead.append(sensor_id)
        return dead

    def alive_count(self, now):
        return len(self._last) - len(self.dead_sensors(now))
```

---

## Q5. `get` / `put` / `getAverage` on a stream (reported; spec reconstructed)

> The post is garbled: "an LRU-style approach to implement get, put, getAverage on a data stream". The most natural reading: a fixed-capacity LRU cache of numeric values whose `getAverage()` returns the mean of what is **currently in the cache**, all O(1). If your prompt is a *sliding-window* average instead, use a `deque` plus a running sum (pop from the left when the window slides and subtract).

**Design and why:** `OrderedDict` gives O(1) `move_to_end` and `popitem(last=False)`. Maintain a **running sum** updated on every insert, overwrite and eviction, so `getAverage` is `sum / len`. The classic bug is forgetting to subtract the *old value* on overwrite. Floating-point drift over millions of updates is a follow-up: use integers, `fractions.Fraction`, or periodically recompute.

```python
# file: streams.py
class LRUAverageCache:
    def __init__(self, capacity):
        self._cap = capacity
        self._d = OrderedDict()
        self._sum = 0

    def get(self, key):
        if key not in self._d:
            return -1
        self._d.move_to_end(key)                 # a read counts as a use
        return self._d[key]

    def put(self, key, value):
        if key in self._d:
            self._sum -= self._d[key]            # overwrite: remove the old value from the sum
        self._d[key] = value
        self._d.move_to_end(key)
        self._sum += value
        if len(self._d) > self._cap:
            _, evicted = self._d.popitem(last=False)
            self._sum -= evicted

    def get_average(self):
        return self._sum / len(self._d) if self._d else 0.0
```

```python
# file: streams.py
def test_streams():
    m = SensorMonitor(timeout=10)
    m.heartbeat("a", 0); m.heartbeat("b", 5); m.heartbeat("c", 8)
    assert m.dead_sensors(12) == ["a"] and m.is_alive("b", 12) and not m.is_alive("zzz", 12)
    m.heartbeat("a", 13)
    assert m.dead_sensors(14) == [] and m.alive_count(14) == 3
    assert m.dead_sensors(20) == ["b", "c"] and m.alive_count(20) == 1
    m.heartbeat("a", 5)                           # late heartbeat is ignored
    assert m.is_alive("a", 23) and not m.is_alive("a", 24)

    c = LRUAverageCache(2)
    c.put("a", 10); c.put("b", 20)
    assert c.get_average() == 15
    c.get("a"); c.put("c", 30)                    # evicts b
    assert c.get("b") == -1 and c.get_average() == 20
    c.put("a", 50)                                # overwrite: sum must drop the old 10
    assert c.get_average() == 40 and LRUAverageCache(1).get_average() == 0.0


if __name__ == "__main__":
    test_streams()
    print("streams OK")
```

---

## Q6. Process a file bigger than memory (reported theme)

> *"Optimize memory while reading a huge file"*: count lines, count words, find the longest line, sum a column. The skill: **stream, and carry state across chunk boundaries**.

**Ladder (say it out loud):**

| Style | Memory | Notes |
|---|---|---|
| `f.read()` / `f.readlines()` | whole file | the mistake they are looking for |
| `for line in f` | one line | buffered by the runtime; the default answer for text |
| `f.read(1 << 20)` loop | one chunk | needed for binary data, or when lines can be enormous or you want to count bytes fast |
| `mmap` | virtual only | OS pages it in lazily; random access; mind truncation and 32-bit limits |
| `os.sendfile` / `shutil.copyfileobj` | O(buffer) | copying without Python touching the bytes |

**Chunk-boundary rule:** anything with a *unit that can straddle a boundary* (a word, a record, a UTF-8 character) needs a **carry-over**. For words: if the chunk does not end with whitespace, the last token may be cut, so hold it back and prepend it to the next chunk. For lines: hold back the text after the last newline.

```python
# file: bigfile.py
def count_lines(path, chunk_size=1 << 20):
    """Counts newline-terminated lines plus a final unterminated one (wc -l would not count that)."""
    n, last = 0, b""
    with open(path, "rb") as f:
        while chunk := f.read(chunk_size):
            n += chunk.count(b"\n")                  # C-speed; no Python-level loop over lines
            last = chunk[-1:]
    return n + (1 if last and last != b"\n" else 0)


def count_words(path, chunk_size=1 << 16):
    """Whitespace-separated tokens (ASCII whitespace); a word may straddle two chunks."""
    total, carry = 0, b""
    with open(path, "rb") as f:
        while chunk := f.read(chunk_size):
            data = carry + chunk
            parts = data.split()
            if not parts or data[-1:].isspace():
                carry = b""                          # chunk ended on a boundary: nothing is cut
            else:
                carry = parts.pop()                  # last token may continue in the next chunk
            total += len(parts)
    return total + (1 if carry else 0)
```

**Follow-ups:** a **500 GB** file → still O(1) memory, but time-bound: parallelize by byte ranges (Q15); a single multi-GB line → chunked reads with a cap; compressed input → `gzip.open` streams too; `readline(limit)` to bound a pathological line.

---

## Q7. Top-K most frequent words / IPs (predicted)

> *Return the K most frequent tokens in a huge log.*

**Design and why**

- **Counter + heap:** stream the file, `Counter` the tokens, take the top K with `heapq.nsmallest(k, ..., key=(-count, token))` in O(D log K) for D distinct tokens. Define the **tie-break** explicitly (count desc, then token asc) so the output is deterministic.
- **If D is too large for memory**, partition by hash: write each token to one of `P` files by `crc32(token) % P` (**stable** hash; Python's `hash()` is salted per process). Each partition holds a *disjoint* set of tokens, so a token's whole count lives in one partition. Count each partition separately (memory ≈ D/P), keep each partition's top K, and take the top K of those candidates. Correct because the global top K is contained in the union of the per-partition top Ks.
- Never use a Count-Min Sketch unless approximate is acceptable; mention it as the streaming alternative.

```python
# file: bigfile.py
import heapq
import itertools
import os
import tempfile
import zlib
from collections import Counter


def _top(counts, k):
    return heapq.nsmallest(k, counts.items(), key=lambda kv: (-kv[1], kv[0]))


def top_k_words(path, k):
    counts = Counter()
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            counts.update(line.split())
    return _top(counts, k)


def partition(items, tmpdir, parts):
    """Write each item to one of `parts` files chosen by a STABLE hash. Same item -> same file."""
    paths = [os.path.join(tmpdir, f"part-{i}") for i in range(parts)]
    outs = [open(p, "w", encoding="utf-8", newline="\n") for p in paths]
    try:
        for item in items:
            outs[zlib.crc32(item.encode("utf-8")) % parts].write(item + "\n")
    finally:
        for o in outs:
            o.close()
    return paths


def top_k_words_low_memory(path, k, parts=8):
    candidates = []
    with tempfile.TemporaryDirectory() as tmp:
        with open(path, encoding="utf-8", errors="replace") as f:
            files = partition((w for line in f for w in line.split()), tmp, parts)
        for p in files:                                    # one partition in memory at a time
            counts = Counter()
            with open(p, encoding="utf-8") as pf:
                counts.update(line.rstrip("\n") for line in pf)
            candidates.extend(_top(counts, k))             # keep only this partition's top K
    return heapq.nsmallest(k, candidates, key=lambda kv: (-kv[1], kv[0]))
```

---

## Q8. Sort or merge files larger than memory (predicted)

> *Sort a 100 GB file of lines with 1 GB of RAM. Also: merge K already-sorted files.*

**Design and why (external merge sort)**

1. **Run generation:** read up to `M` lines (what fits in memory), sort in memory, write a sorted *run* file. Repeat.
2. **K-way merge:** open all runs, `heapq.merge` them lazily (a heap of one line per run), write the output. Memory O(K). Merging K *given* sorted files is just step 2.
- Cost: reads+writes the data twice, O((F/M)·M log M + F log K) compute, 2 sequential passes of I/O. Sequential I/O is what disks like.
- Too many runs for the OS file-descriptor limit? Merge in **passes** (merge 100 runs at a time into bigger runs).
- Normalize a missing final newline, or the last line of a run glues to the next line in the merge.
- Duplicates / stability / key columns: pass `key=` to both `sort` and `merge`.

```python
# file: bigfile.py
def merge_sorted(paths, dst):
    """K-way merge of files that are already sorted line by line. Memory: one line per input."""
    files = [open(p, encoding="utf-8", newline="") for p in paths]
    try:
        with open(dst, "w", encoding="utf-8", newline="") as out:
            out.writelines(heapq.merge(*files))
    finally:
        for f in files:
            f.close()


def external_sort(src, dst, max_lines=100_000):
    with tempfile.TemporaryDirectory() as tmp:
        runs = []
        with open(src, encoding="utf-8", newline="") as f:
            while True:
                lines = [l if l.endswith("\n") else l + "\n"          # normalise the last line
                         for l in itertools.islice(f, max_lines)]
                if not lines:
                    break
                lines.sort()
                run = os.path.join(tmp, f"run-{len(runs)}")
                with open(run, "w", encoding="utf-8", newline="") as r:
                    r.writelines(lines)
                runs.append(run)
        merge_sorted(runs, dst)
```

---

## Q9. Deduplicate lines in a huge file (predicted)

> *Remove duplicate lines.*

**Design and why**

- Fits in memory? A `set` of seen lines, write on first sight. **Preserves order**, O(unique lines) memory. (Store `hash(line)` instead of the line to save memory, at a tiny collision risk; a 128-bit digest makes that negligible.)
- Doesn't fit? **Hash-partition** (same as Q7): identical lines always land in the same file, so each partition can be deduplicated independently in memory. Output order is *not* preserved; to keep original order, partition `(lineno, line)` and sort by `lineno` afterwards (an external sort).
- Alternative: external sort then drop adjacent equal lines (what `sort | uniq` does).

```python
# file: bigfile.py
def dedup_in_memory(src, dst):
    seen = set()
    with open(src, encoding="utf-8", errors="replace") as f, \
            open(dst, "w", encoding="utf-8", newline="\n") as out:
        for line in f:
            line = line.rstrip("\n")
            if line not in seen:
                seen.add(line)
                out.write(line + "\n")


def dedup_partitioned(src, dst, parts=16):
    """Unordered output; memory ~ (unique lines / parts)."""
    with tempfile.TemporaryDirectory() as tmp, \
            open(src, encoding="utf-8", errors="replace") as f, \
            open(dst, "w", encoding="utf-8", newline="\n") as out:
        files = partition((line.rstrip("\n") for line in f), tmp, parts)
        for p in files:
            seen = set()
            with open(p, encoding="utf-8") as pf:
                for line in pf:
                    if line not in seen:
                        seen.add(line)
                        out.write(line)
```

### Tests for Q6 to Q9

```python
# file: bigfile.py
import random


def test_bigfile():
    rnd = random.Random(5)
    with tempfile.TemporaryDirectory() as tmp:
        p = os.path.join(tmp, "in.txt")
        vocab = ["alpha", "beta", "gamma", "delta", "eps", "zeta", "eta", "theta"]
        words = [rnd.choice(vocab[: rnd.randint(1, 8)]) for _ in range(500)]
        lines = [" ".join(words[i:i + rnd.randint(1, 6)]) for i in range(0, 500, 3)]

        for text in ("\n".join(lines), "\n".join(lines) + "\n", "", "\n", "x"):
            with open(p, "w", encoding="utf-8") as f:
                f.write(text)
            for chunk in (1, 2, 5, 64):
                assert count_lines(p, chunk) == len(text.splitlines()), (text[:20], chunk)
                assert count_words(p, chunk) == len(text.split()), (text[:20], chunk)

        with open(p, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        for k in (1, 3, 20):
            assert top_k_words(p, k) == top_k_words_low_memory(p, k, parts=3)
        c = Counter(" ".join(lines).split())
        assert top_k_words(p, 1)[0] == min(c.items(), key=lambda kv: (-kv[1], kv[0]))

        data = [f"line-{rnd.randint(0, 40)}" for _ in range(300)]
        with open(p, "w", encoding="utf-8") as f:
            f.write("\n".join(data))                                  # no trailing newline
        dst = os.path.join(tmp, "sorted.txt")
        external_sort(p, dst, max_lines=7)
        with open(dst, encoding="utf-8") as f:
            assert f.read() == "".join(l + "\n" for l in sorted(data))
        empty = os.path.join(tmp, "empty.txt")
        open(empty, "w").close()
        external_sort(empty, dst, max_lines=7)
        assert os.path.getsize(dst) == 0

        for fn in (dedup_in_memory, dedup_partitioned):
            out = os.path.join(tmp, "dedup.txt")
            fn(p, out)
            with open(out, encoding="utf-8") as f:
                got = f.read().splitlines()
            assert len(got) == len(set(data)) and set(got) == set(data), fn.__name__
        out = os.path.join(tmp, "dedup2.txt")
        dedup_in_memory(p, out)
        with open(out, encoding="utf-8") as f:
            assert f.read().splitlines() == list(dict.fromkeys(data))   # first-seen order kept


if __name__ == "__main__":
    test_bigfile()
    print("bigfile OK")
```

---

## Q10. Binary search a sorted log by timestamp (predicted)

> *A huge log whose lines start with a fixed-width timestamp (`2024-05-01T12:00:03 ...`) is sorted by time. Return all lines in `[start, end)` without scanning from the beginning.*

**Design and why:** lines have variable length, so you cannot index "line k", but you can binary search **byte offsets**:

1. Pick `mid`, find the **start of the line that contains `mid`** (scan backwards to the previous `\n`, in blocks, not byte by byte).
2. Compare that line's timestamp prefix to the target. If it is *less*, the answer is after this line (`lo = end of this line`), else it is at or before it (`hi = start of this line`).
3. Invariant: `lo` is always a line start and every line starting before `lo` has key < target; every line starting at or after `hi` has key ≥ target. The loop terminates because `lo` strictly increases or `hi` strictly decreases.
- Fixed-width ISO-8601 timestamps compare correctly as **strings/bytes**. If timestamps are variable-width or in another time zone, parse them instead.
- Cost: O(log F) seeks, each reading a line, versus O(F) for a scan. Then stream forward from the found offset until the key reaches `end`.
- This is the same idea as Kafka's offset/time index lookup: sparse index plus a short forward scan.

```python
# file: logs.py
import os
import re
import threading
from collections import Counter, deque


def _line_start(f, pos):
    """Offset of the start of the line containing byte `pos` (looks only at bytes before pos)."""
    while pos > 0:
        step = min(4096, pos)
        f.seek(pos - step)
        block = f.read(step)
        i = block.rfind(b"\n")
        if i != -1:
            return pos - step + i + 1
        pos -= step
    return 0


def first_line_at_or_after(path, target: bytes):
    """Byte offset of the first line whose leading bytes are >= target (file size if none)."""
    with open(path, "rb") as f:
        lo, hi = 0, f.seek(0, os.SEEK_END)
        while lo < hi:
            mid = (lo + hi) // 2
            start = _line_start(f, mid)
            f.seek(start)
            line = f.readline()
            if line[:len(target)] < target:
                lo = start + len(line)           # this whole line is too early
            else:
                hi = start                       # this line (or an earlier one) is the answer
        return lo


def lines_between(path, start: bytes, end: bytes):
    off = first_line_at_or_after(path, start)
    with open(path, "rb") as f:
        f.seek(off)
        for line in f:
            if line[:len(end)] >= end:
                return
            yield line.rstrip(b"\n")
```

---

## Q11. `grep` with context and log aggregation (predicted)

> *Implement `grep -B b -A a PATTERN file`. Then: count ERROR lines per minute, tolerating malformed lines.*

**`grep` with context, design:** keep a `deque(maxlen=b)` of the most recent **unprinted** lines (the "before" window) and a counter of how many "after" lines are still owed. On a match: flush the before-window, print the match, set `remaining = a`. On a non-match: if `remaining > 0` print it and decrement, else push it into the before-window. Because printed lines are never put into the window, overlapping contexts are never printed twice, and the window always contains the lines immediately preceding the current one.

**Aggregation, design:** one pass, a `Counter` keyed by the minute prefix; a regex with explicit groups; count **malformed lines** separately instead of crashing or silently dropping (say what you'd do in production: dead-letter file, metric). Don't `split()` blindly: messages contain spaces.

```python
# file: logs.py
def grep(path, pattern, before=0, after=0):
    """Yield (lineno, text, is_match) like grep -B/-A. 0-based line numbers."""
    rx = re.compile(pattern)
    window = deque(maxlen=before)                  # recent lines NOT yet printed
    owed = 0
    with open(path, encoding="utf-8", errors="replace") as f:
        for i, line in enumerate(f):
            line = line.rstrip("\r\n")
            if rx.search(line):
                for j, prev in enumerate(window, start=i - len(window)):
                    yield j, prev, False
                window.clear()
                yield i, line, True
                owed = after
            elif owed > 0:
                yield i, line, False
                owed -= 1
            else:
                window.append(line)


_LOG = re.compile(r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}):\d{2}\S*\s+([A-Z]+)\s")


def errors_per_minute(path):
    """Returns (Counter of 'YYYY-MM-DDTHH:MM' -> ERROR count, number of malformed lines)."""
    counts, malformed = Counter(), 0
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            m = _LOG.match(line)
            if not m:
                malformed += 1
            elif m.group(2) == "ERROR":
                counts[m.group(1)] += 1
    return counts, malformed
```

---

## Q12. Size-based rotating log writer (predicted)

> *Write lines to `app.log`; when it would exceed `max_bytes`, rotate to `app.log.1`, shift older ones, keep `backups` files. Thread-safe.*

**Design and why**

- Track the current size (initialize from `os.path.getsize`) instead of calling `stat` per write.
- **Rename order matters:** shift from the *oldest* to the newest (`.2 → .3`, then `.1 → .2`, then `app.log → .1`). Doing it newest-first overwrites data. `os.replace` is atomic and overwrites the destination, so the oldest backup falls off the end naturally.
- Rotate **before** the write that would overflow, and never rotate an empty file (a single line larger than `max_bytes` still has to go somewhere).
- A `Lock` makes `rotate + write` one atomic step across threads. **Flush** each line (or accept data loss on crash and say so). Multiple *processes* can't share this safely; use one writer, `logging.handlers.RotatingFileHandler` with a queue, or `O_APPEND` writes without rotation.
- Production answer: use `logging.handlers.RotatingFileHandler`; know how it works.

```python
# file: logs.py
class RotatingLogWriter:
    def __init__(self, path, max_bytes, backups=3):
        self.path, self.max_bytes, self.backups = path, max_bytes, backups
        self._lock = threading.Lock()
        self._f = open(path, "ab")
        self._size = os.path.getsize(path)

    def write_line(self, line):
        data = (line + "\n").encode("utf-8")
        with self._lock:
            if self._size and self._size + len(data) > self.max_bytes:
                self._rotate()
            self._f.write(data)
            self._f.flush()                        # trade-off: durability vs throughput
            self._size += len(data)

    def _rotate(self):
        self._f.close()
        for i in range(self.backups - 1, 0, -1):   # oldest first, so nothing is overwritten early
            src = f"{self.path}.{i}"
            if os.path.exists(src):
                os.replace(src, f"{self.path}.{i + 1}")
        os.replace(self.path, f"{self.path}.1")
        self._f = open(self.path, "ab")
        self._size = 0

    def close(self):
        with self._lock:
            self._f.close()
```

### Tests for Q10 to Q12

```python
# file: logs.py
import datetime
import random
import tempfile


def test_binary_search_log():
    rnd = random.Random(11)
    base = datetime.datetime(2024, 5, 1, 12, 0, 0)
    stamp = lambda s: (base + datetime.timedelta(seconds=s)).strftime("%Y-%m-%dT%H:%M:%S")
    lines, t = [], 0
    for _ in range(600):
        t += rnd.randint(1, 5)
        lines.append(f"{stamp(t)} INFO {'x' * rnd.randint(0, 120)}")   # variable-length lines
    with tempfile.TemporaryDirectory() as tmp:
        p = os.path.join(tmp, "log")
        with open(p, "wb") as f:
            f.write(("\n".join(lines) + "\n").encode())
        data = open(p, "rb").read()
        for _ in range(300):
            target = stamp(rnd.randint(-5, t + 5)).encode()
            want = next((data.index(l.encode()) for l in lines if l.encode()[:len(target)] >= target), len(data))
            assert first_line_at_or_after(p, target) == want, target
        s, e = stamp(100).encode(), stamp(400).encode()
        assert list(lines_between(p, s, e)) == [l.encode() for l in lines if s <= l.encode()[:len(s)] < e]


def test_grep_and_aggregation():
    text = ["a", "ERR 1", "b", "c", "d", "e", "ERR 2", "ERR 3", "f"]
    with tempfile.TemporaryDirectory() as tmp:
        p = os.path.join(tmp, "g")
        with open(p, "w") as f:
            f.write("\n".join(text) + "\n")
        for b, a in ((0, 0), (1, 1), (2, 1), (0, 2), (3, 3)):
            want = set()
            for i, l in enumerate(text):
                if "ERR" in l:
                    want.update(range(max(0, i - b), min(len(text), i + a + 1)))
            got = list(grep(p, "ERR", b, a))
            assert [i for i, _, _ in got] == sorted(want), (b, a)         # in order, no duplicates
            assert all(m == ("ERR" in t) for _, t, m in got)
        log = os.path.join(tmp, "app.log")
        with open(log, "w") as f:
            f.write("2024-05-01T10:00:01 ERROR boom happened\n2024-05-01T10:00:59Z ERROR again\n"
                    "2024-05-01T10:01:00 INFO fine\n2024-05-01T10:01:30 ERROR later\n"
                    "garbage line\n\n2024-05-01 10:02:00 ERROR wrong timestamp format\n")
        counts, bad = errors_per_minute(log)
        assert counts == {"2024-05-01T10:00": 2, "2024-05-01T10:01": 1} and bad == 3


def test_rotating_writer():
    with tempfile.TemporaryDirectory() as tmp:
        p = os.path.join(tmp, "app.log")
        w = RotatingLogWriter(p, max_bytes=30, backups=3)
        for i in range(20):
            w.write_line(f"line-{i:02d}")                                # 8 bytes each: 3 per file
        w.close()
        names = [f"{p}.3", f"{p}.2", f"{p}.1", p]                       # oldest -> newest
        got = []
        for n in names:
            assert os.path.getsize(n) <= 30
            got += open(n).read().split()
        assert not os.path.exists(f"{p}.4")
        assert got == [f"line-{i:02d}" for i in range(20 - len(got), 20)]   # newest lines, in order


if __name__ == "__main__":
    test_binary_search_log()
    test_grep_and_aggregation()
    test_rotating_writer()
    print("logs OK")
```

---

## Q13. Safe file writes, copy, and duplicate finder (predicted)

> This is the "easy stuff you do on the job" the Blind thread predicted: append, temp files, copy, traverse a directory, is-file/is-directory.

**Atomic write (never leave a half-written file):** write to a **temp file in the same directory** (so the final rename stays on one filesystem, where `rename` is atomic), `flush` + `fsync`, then `os.replace(tmp, path)`. Readers see either the old file or the new one, never a mix. For durability across power loss also `fsync` the directory (POSIX). Clean up the temp file on any exception. Pitfalls: temp file on another filesystem → `rename` fails or isn't atomic; forgetting `fsync` → empty file after a crash on some filesystems.

**Copy:** `shutil.copyfileobj` with a buffer (or `shutil.copyfile`, which uses fast kernel paths such as `sendfile`/`copy_file_range` where available). Never `write(read())` a big file.

**Append:** open with `"a"`/`"ab"`; with `O_APPEND` the kernel positions each write at the end atomically, so concurrent appenders don't overwrite each other (small writes only; interleaving of larger writes isn't guaranteed).

**Directory traversal + duplicate finder:** `os.walk` (or `pathlib.Path.rglob`), **skip symlinks** (loops, double counting), handle permission errors. Duplicates: hashing every file is expensive; **group by size first** (free from `stat`), then by a hash of the **first 4 KB**, and only then by a full-content hash. Most files are eliminated by the cheap steps. Caveats: hard links share an inode (not "real" duplicates: dedupe by `(st_dev, st_ino)`), empty files are all identical, and a byte-by-byte comparison is the only fully collision-free confirmation.

```python
# file: fsops.py
import contextlib
import csv
import hashlib
import json
import os
import shutil
import stat
import tempfile
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor


def atomic_write(path, data: bytes):
    directory = os.path.dirname(os.path.abspath(path))
    fd, tmp = tempfile.mkstemp(dir=directory, prefix=".tmp-")     # same filesystem as the target
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())                                  # data on disk before the rename
        os.replace(tmp, path)                                     # atomic; overwrites on POSIX and Windows
    except BaseException:
        with contextlib.suppress(FileNotFoundError):
            os.unlink(tmp)
        raise
    with contextlib.suppress(OSError, AttributeError):            # best effort: persist the rename itself
        dfd = os.open(directory, os.O_RDONLY)
        try:
            os.fsync(dfd)
        finally:
            os.close(dfd)


def copy_file(src, dst, bufsize=1 << 20):
    with open(src, "rb") as r, open(dst, "wb") as w:
        shutil.copyfileobj(r, w, bufsize)


def _hash(path, limit=None, chunk=1 << 20):
    h, remaining = hashlib.sha256(), limit
    with open(path, "rb") as f:
        while True:
            n = chunk if remaining is None else min(chunk, remaining)
            data = f.read(n) if n else b""
            if not data:
                break
            h.update(data)
            if remaining is not None:
                remaining -= len(data)
    return h.digest()


def find_duplicates(root):
    """Groups of identical files under root: size -> hash of first 4 KB -> full hash."""
    by_size = defaultdict(list)
    for dirpath, _dirs, names in os.walk(root, followlinks=False):
        for name in names:
            p = os.path.join(dirpath, name)
            try:
                st = os.lstat(p)                                  # lstat: do not follow symlinks
            except OSError:
                continue                                          # vanished or unreadable
            if stat.S_ISREG(st.st_mode):
                by_size[st.st_size].append(p)
    groups = []
    for paths in by_size.values():
        if len(paths) < 2:
            continue                                              # unique size: cannot be a duplicate
        by_head = defaultdict(list)
        for p in paths:
            by_head[_hash(p, 4096)].append(p)
        for same_head in by_head.values():
            if len(same_head) < 2:
                continue
            by_full = defaultdict(list)
            for p in same_head:
                by_full[_hash(p)].append(p)
            groups.extend(sorted(g) for g in by_full.values() if len(g) > 1)
    return sorted(groups)
```

---

## Q14. CSV and JSON-lines processing (predicted)

> *Sum a column grouped by a key from a big CSV; join two CSVs on a key; read a JSON-lines file that has some corrupt lines.*

**CSV design and why**

- Use the **`csv` module**, never `line.split(",")`: fields can be quoted and contain commas, quotes (`""`) and **embedded newlines**, which also breaks `for line in f` thinking.
- Open with **`newline=""`** (required by the `csv` docs so embedded newlines and `\r\n` are handled) and **`utf-8-sig`** (strips a BOM that otherwise corrupts the first header name).
- Stream rows; **never** `list(reader)` a big file.
- **Bad rows:** short rows give `None` values, non-numeric values raise: count and report, or send to a reject file; say which policy you chose.
- **Join:** hash join. Load the *smaller* file into a dict of lists keyed by the join column, stream the larger one and emit matches: O(small) memory, one pass over the big one. If neither fits: partition both by key hash (Q7), join partition pairs; or external-sort both and merge-join.

**JSONL design:** one JSON object per line, so `for line in f` + `json.loads` streams. A single bad line must not abort a million-line job: catch `JSONDecodeError`, record the line number, continue. (A big single JSON *array* is a different problem: needs a streaming parser such as `ijson`.)

```python
# file: fsops.py
def sum_by_key(path, key_col, val_col):
    """Returns ({key: total}, number_of_bad_rows)."""
    totals, bad = defaultdict(float), 0
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            try:
                totals[row[key_col]] += float(row[val_col])
            except (KeyError, TypeError, ValueError):             # missing column, None, "abc"
                bad += 1
    return dict(totals), bad


def hash_join(small_path, big_path, key):
    """Inner join on `key`. Memory: the small file. The big file is streamed."""
    index = defaultdict(list)
    with open(small_path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            index[row[key]].append(row)
    with open(big_path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            for match in index.get(row[key], ()):
                yield {**match, **row}


def iter_jsonl(path, errors=None):
    """Yield one object per line. If `errors` is a list, bad lines are recorded there instead of raising."""
    with open(path, encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as exc:
                if errors is None:
                    raise
                errors.append((lineno, exc.msg))
```

---

## Q15. Split a file for parallel processing (predicted)

> *Process a huge file with N workers. How do you split it?*

**Design and why:** split by **byte ranges**, not by lines (you can't know line boundaries without reading). Rule: *a line belongs to the range in which it **starts**.* For each boundary `b = size·i/N`, `seek(b-1)` and `readline()`: that consumes either just the newline at `b-1` (the line starting at `b` is the next range's) or the rest of the line straddling `b` (also belongs to the previous range). The position after `readline()` is the first line start ≥ `b`. Each worker then reads from its start while its position `< end`. Result: every line processed exactly once, no worker reads another's lines, and no coordination is needed.

- Edge cases: `b == 0` (don't skip the first line), more workers than lines (empty ranges dropped), a last line without a newline, a single giant line (one range owns it).
- In CPython use **processes** (or a native library) for CPU-bound parsing; threads help only for I/O-bound work because of the GIL. The tests below use threads for simplicity.

```python
# file: fsops.py
def line_aligned_ranges(path, parts):
    size = os.path.getsize(path)
    starts = [0]
    with open(path, "rb") as f:
        for i in range(1, parts):
            b = size * i // parts
            if b == 0:
                starts.append(0)
                continue
            f.seek(b - 1)
            f.readline()                           # finish the line that covers byte b-1
            starts.append(f.tell())                # first line start >= b
    starts.append(size)
    return [(s, e) for s, e in zip(starts, starts[1:]) if s < e]


def iter_range_lines(path, start, end):
    with open(path, "rb") as f:
        f.seek(start)
        pos = start
        while pos < end:                           # `end` is a line start, so pos lands on it exactly
            line = f.readline()
            if not line:
                break
            pos += len(line)
            yield line


def parallel_count(path, needle: bytes, parts=4):
    ranges = line_aligned_ranges(path, parts)
    count = lambda r: sum(1 for line in iter_range_lines(path, *r) if needle in line)
    with ThreadPoolExecutor(max_workers=parts) as pool:
        return sum(pool.map(count, ranges))
```

### Tests for Q13 to Q15

```python
# file: fsops.py
import random


def test_atomic_write_and_copy():
    with tempfile.TemporaryDirectory() as tmp:
        p = os.path.join(tmp, "cfg.json")
        atomic_write(p, b"v1")
        atomic_write(p, b"v2")
        assert open(p, "rb").read() == b"v2" and os.listdir(tmp) == ["cfg.json"]
        try:
            atomic_write(p, "not bytes")                              # fails mid-way
            raise AssertionError("expected TypeError")
        except TypeError:
            pass
        assert open(p, "rb").read() == b"v2" and os.listdir(tmp) == ["cfg.json"]   # old data intact, no tmp left
        big = os.path.join(tmp, "big")
        with open(big, "wb") as f:
            f.write(os.urandom(300_000))
        copy_file(big, big + ".copy", bufsize=4096)
        assert open(big, "rb").read() == open(big + ".copy", "rb").read()


def test_find_duplicates():
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, "sub", "deep"))
        files = {"a.txt": b"hello", "sub/b.txt": b"hello", "sub/deep/c.txt": b"hello",
                 "d.txt": b"hellp", "e.txt": b"x" * 5000 + b"1", "sub/f.txt": b"x" * 5000 + b"2",
                 "g.bin": b"y" * 6000, "sub/h.bin": b"y" * 6000}
        for name, data in files.items():
            with open(os.path.join(tmp, name), "wb") as f:
                f.write(data)
        os.symlink(os.path.join(tmp, "a.txt"), os.path.join(tmp, "link.txt"))   # must be ignored
        rel = lambda gs: [[os.path.relpath(p, tmp) for p in g] for g in gs]
        assert rel(find_duplicates(tmp)) == [["a.txt", "sub/b.txt", "sub/deep/c.txt"], ["g.bin", "sub/h.bin"]]


def test_csv_and_jsonl():
    with tempfile.TemporaryDirectory() as tmp:
        p = os.path.join(tmp, "sales.csv")
        with open(p, "w", newline="", encoding="utf-8-sig") as f:
            f.write('region,amount,note\nEU,10.5,"a, b"\nUS,3,"multi\nline"\nEU,abc,bad\nUS\nEU,4.5,ok\n')
        totals, bad = sum_by_key(p, "region", "amount")
        assert totals == {"EU": 15.0, "US": 3.0} and bad == 2          # "abc" and the short row
        small, big = os.path.join(tmp, "regions.csv"), os.path.join(tmp, "orders.csv")
        with open(small, "w", newline="") as f:
            f.write("region,manager\nEU,Ann\nUS,Bob\n")
        with open(big, "w", newline="") as f:
            f.write("order,region\n1,EU\n2,US\n3,APAC\n4,EU\n")
        joined = list(hash_join(small, big, "region"))
        assert [(r["order"], r["manager"]) for r in joined] == [("1", "Ann"), ("2", "Bob"), ("4", "Ann")]
        j = os.path.join(tmp, "e.jsonl")
        with open(j, "w") as f:
            f.write('{"a": 1}\n\n{broken\n{"a": 3}\n')
        errs = []
        assert list(iter_jsonl(j, errs)) == [{"a": 1}, {"a": 3}] and [n for n, _ in errs] == [3]
        try:
            list(iter_jsonl(j))
            raise AssertionError("expected JSONDecodeError")
        except json.JSONDecodeError:
            pass


def test_ranges_and_parallel_count():
    rnd = random.Random(2)
    with tempfile.TemporaryDirectory() as tmp:
        p = os.path.join(tmp, "f")
        for trial in range(60):
            lines = [("needle " if rnd.random() < 0.3 else "hay ") + "z" * rnd.randint(0, 30)
                     for _ in range(rnd.randint(0, 40))]
            data = "\n".join(lines) + rnd.choice(["", "\n"]) if lines else ""
            with open(p, "w") as f:
                f.write(data)
            for parts in (1, 2, 3, 7, 50):
                ranges = line_aligned_ranges(p, parts)
                got = [l for r in ranges for l in iter_range_lines(p, *r)]
                assert b"".join(got) == data.encode(), (trial, parts)       # every byte exactly once
                assert parallel_count(p, b"needle", parts) == data.count("needle")


if __name__ == "__main__":
    test_atomic_write_and_copy()
    test_find_duplicates()
    test_csv_and_jsonl()
    test_ranges_and_parallel_count()
    print("fsops OK")
```

---

## Q16. Append-only log with index and compaction (predicted, Kafka-flavoured)

> This is my extrapolation from Confluent's domain, **not** a reported question. *Build a persistent key-value store on a single append-only file: `put`, `get`, `delete`, survive restarts and crashes, then compact.* It exercises binary record formats, partial reads, checksums, recovery and rewriting a file safely: every "file operations" skill at once. It is the idea behind Kafka segments, log compaction (the latest value per key survives; a `null` value is a tombstone) and Bitcask-style stores (DDIA ch. 3).

**Design and why**

- **Record format** (big-endian): `crc32 | key_len | value_len | key | value`. Fixed-size header means you can read it with one `read(12)`. A **tombstone** is a record whose `value_len` is a sentinel (`0xFFFFFFFF`) and has no value bytes: a delete is *an append*, because you never modify old bytes.
- **In-memory index** `key → (value_offset, value_len)`: `get` is one `seek` + one `read`. Writes are sequential appends (fast on every medium).
- **Recovery on open:** scan from the start, validating each record (`read_exact`, length sanity check against the file size, CRC). The first short or corrupt record means a **torn write** from a crash: **truncate there** and continue. (This assumes damage only at the tail; corruption in the middle needs a different policy: fail loudly or skip to a segment boundary.)
- **`read_exact`:** a `read(n)` may legally return fewer than `n` bytes (EOF, pipes, sockets). Always check the length.
- **Compaction:** the log only grows, with dead entries from overwrites and deletes. Write **only live records** to a new file, `fsync`, then `os.replace` over the old one (atomic) and rebuild the index offsets. A crash mid-compaction leaves the old file untouched.
- Single writer. Add a lock for concurrent use (the `seek`+`read` pair is not atomic across threads; `os.pread` avoids that on POSIX).
- Durability knob: `sync=True` fsyncs per write (safe, slow); batching or a periodic fsync is the usual compromise (Kafka relies on the page cache plus replication).

```python
# file: logkv.py
import os
import struct
import threading
import zlib

_HEADER = struct.Struct(">III")            # crc32, key_len, value_len
_TOMBSTONE = 0xFFFFFFFF                    # value_len meaning "deleted" (like a null value in Kafka)


def _encode(key: bytes, value):
    """value=None encodes a tombstone."""
    vlen = _TOMBSTONE if value is None else len(value)
    body = key + (b"" if value is None else value)
    crc = zlib.crc32(struct.pack(">II", len(key), vlen) + body)
    return _HEADER.pack(crc, len(key), vlen) + body


def _read_exact(f, n):
    data = f.read(n)
    return data if len(data) == n else None          # None = short read (EOF / torn record)


class LogKV:
    def __init__(self, path, sync=False):
        self.path, self._sync = path, sync
        self._lock = threading.Lock()
        self._index = {}                              # key -> (value_offset, value_len)
        open(path, "ab").close()                      # create if missing
        self._end = self._recover()
        self._w = open(path, "ab")
        self._r = open(path, "rb")

    def _recover(self):
        """Rebuild the index by scanning the log; truncate a torn or corrupt tail. Returns the valid length."""
        good = 0
        size = os.path.getsize(self.path)
        with open(self.path, "r+b") as f:
            while True:
                header = _read_exact(f, _HEADER.size)
                if header is None:
                    break
                crc, klen, vlen = _HEADER.unpack(header)
                body_len = klen + (0 if vlen == _TOMBSTONE else vlen)
                if good + _HEADER.size + body_len > size:        # garbage length: never allocate it
                    break
                body = _read_exact(f, body_len)
                if body is None or zlib.crc32(struct.pack(">II", klen, vlen) + body) != crc:
                    break
                key = body[:klen]
                if vlen == _TOMBSTONE:
                    self._index.pop(key, None)
                else:
                    self._index[key] = (good + _HEADER.size + klen, vlen)
                good += _HEADER.size + body_len
            f.truncate(good)                                      # drop the damaged tail
        return good

    def _append(self, key, value):
        record = _encode(key, value)
        self._w.write(record)
        self._w.flush()
        if self._sync:
            os.fsync(self._w.fileno())
        if value is None:
            self._index.pop(key, None)
        else:
            self._index[key] = (self._end + _HEADER.size + len(key), len(value))
        self._end += len(record)

    def put(self, key: bytes, value: bytes):
        with self._lock:
            self._append(key, value)

    def delete(self, key: bytes):
        with self._lock:
            existed = key in self._index
            if existed:
                self._append(key, None)                           # a delete is an append of a tombstone
            return existed

    def get(self, key: bytes):
        with self._lock:
            loc = self._index.get(key)
            if loc is None:
                return None
            offset, vlen = loc
            self._r.seek(offset)
            return self._r.read(vlen)

    def compact(self):
        """Rewrite only live records, then atomically swap the file in."""
        with self._lock:
            tmp, new_index, end = self.path + ".compact", {}, 0
            with open(tmp, "wb") as out:
                for key, (offset, vlen) in sorted(self._index.items(), key=lambda kv: kv[1][0]):
                    self._r.seek(offset)                           # offset order = sequential reads
                    record = _encode(key, self._r.read(vlen))
                    out.write(record)
                    new_index[key] = (end + _HEADER.size + len(key), vlen)
                    end += len(record)
                out.flush()
                os.fsync(out.fileno())
            self._w.close()
            self._r.close()
            os.replace(tmp, self.path)                              # crash before this line = old file intact
            self._index, self._end = new_index, end
            self._w = open(self.path, "ab")
            self._r = open(self.path, "rb")

    def close(self):
        with self._lock:
            self._w.close()
            self._r.close()
```

```python
# file: logkv.py
import tempfile


def test_logkv():
    with tempfile.TemporaryDirectory() as tmp:
        p = os.path.join(tmp, "data.log")
        kv = LogKV(p)
        kv.put(b"a", b"1"); kv.put(b"b", b"22"); kv.put(b"a", b"333")
        assert kv.delete(b"b") and not kv.delete(b"nope")
        assert kv.get(b"a") == b"333" and kv.get(b"b") is None
        kv.put(b"empty", b"")                                        # empty value != tombstone
        assert kv.get(b"empty") == b""
        good_size = os.path.getsize(p)
        kv.close()

        kv = LogKV(p)                                                # restart: index rebuilt from the log
        assert kv.get(b"a") == b"333" and kv.get(b"b") is None and kv.get(b"empty") == b""
        kv.close()

        with open(p, "ab") as f:
            f.write(b"\x00\x01\x02\x03\x04")                         # crash left a partial header
        kv = LogKV(p)
        assert os.path.getsize(p) == good_size and kv.get(b"a") == b"333"   # torn tail truncated
        kv.put(b"c", b"x"); kv.put(b"c", b"y")
        kv.close()

        with open(p, "r+b") as f:                                    # flip the last byte: CRC must catch it
            f.seek(-1, os.SEEK_END)
            last = f.read(1)
            f.seek(-1, os.SEEK_END)
            f.write(bytes([last[0] ^ 0xFF]))
        kv = LogKV(p)
        assert kv.get(b"c") == b"x"                                  # corrupt newest record dropped
        for i in range(50):
            kv.put(b"a", str(i).encode())                            # lots of dead records
        before = os.path.getsize(p)
        kv.compact()
        assert os.path.getsize(p) < before / 3
        assert kv.get(b"a") == b"49" and kv.get(b"c") == b"x" and kv.get(b"b") is None
        kv.put(b"z", b"after-compaction")
        kv.close()
        kv = LogKV(p)
        assert kv.get(b"z") == b"after-compaction" and kv.get(b"a") == b"49"
        kv.close()


if __name__ == "__main__":
    test_logkv()
    print("logkv OK")
```

**Follow-ups:** segment files (roll at a size, delete or compact old segments independently: how Kafka stores partitions); a **sparse index** instead of one entry per key; time/offset index lookups (Q10); group commit / `fsync` batching; concurrent readers (immutable segments); checksum per batch instead of per record.

---

## 6. Linux and OS fundamentals (reported in the same loops)

The super-day report listed these as "heavy follow-ups". Short, accurate answers:

**How is a command like `ls` executed?** The shell parses the line, resolves `ls` by searching `$PATH` (or a builtin/alias), then `fork()`s (really `clone`/`vfork`); the child sets up redirections (`dup2` on file descriptors 0/1/2), then calls `execve("/bin/ls", argv, envp)`, which replaces the process image (the kernel loads the ELF binary, the dynamic linker loads libc). The parent `wait()`s for the exit status (`$?`). Pipes: `pipe()` creates two FDs; each side of `|` is a child wired to one end.

**What do `pwd` and `ls` do under the hood?** `pwd` (the program) calls `getcwd()`, a syscall returning the kernel's current-directory path (the shell builtin prints its own logical `$PWD`, which can differ across symlinks). `ls` opens the directory (`openat`), reads entries with `getdents64` (names + inode numbers + types), and, for `-l`, calls `lstat` per entry for size, mode, owner, times; it resolves uid/gid to names via NSS (`/etc/passwd`). Sorting and colouring are in user space.

**`ip` vs `ifconfig`?** `ifconfig` (net-tools, legacy) uses `ioctl` calls and `/proc/net`; `ip` (iproute2) talks to the kernel over **netlink** sockets (`AF_NETLINK`), which supports everything modern: multiple addresses, policy routing, namespaces, and so on.

**Permissions and groups.** Every file has an owner, a group, and `rwx` bits for user/group/other (`rwxr-x---` = 750). On a **directory**, `r` = list names, `w` = create/delete/rename entries (needs `x` too), `x` = traverse/open entries by name. Access check: if the process's effective uid is the owner, use the user bits; else if any of its groups matches, use the group bits; else other. root bypasses most checks. `umask` clears bits from new files' default mode (666/777). Special bits: **setuid/setgid** (run as the file's owner/group; setgid on a directory makes new files inherit the group), **sticky** (`/tmp`: only the owner can delete their files). Supplementary groups come from `/etc/group` at login (`id`, `newgrp`). ACLs (`getfacl`) and **capabilities** (`CAP_NET_BIND_SERVICE`) refine this.

**Files, inodes, descriptors (the questions behind file APIs).**
- A **file name is just a directory entry** pointing to an **inode** (metadata + data block pointers). A **hard link** is another name for the same inode (same filesystem only; the data lives until the link count hits 0 *and* no process has it open). A **symlink** is a tiny file containing a path; it can dangle.
- Deleting a file that is still open: the name disappears, the space is reclaimed when the last FD closes (why `lsof | grep deleted` shows space not freed).
- A **file descriptor** is a per-process index to an *open file description* (offset, flags) shared across `fork`/`dup`. `read`/`write` advance the shared offset; `pread`/`pwrite` take an explicit offset (thread-safe, no `seek`).
- **Buffering:** user-space buffers (`BufferedWriter`) → kernel **page cache** → disk. `flush()` moves user → kernel; `fsync()` forces kernel → device. Without `fsync`, a crash can lose "written" data; that is why databases and Kafka care about it (Kafka leans on the page cache and replication instead of fsync per message).
- **Atomicity:** `rename` is atomic within a filesystem; `O_APPEND` writes are positioned atomically; `O_EXCL|O_CREAT` creates a file only if absent (the basis of lock files).
- `mmap` maps a file into the address space: the page cache *is* the memory; page faults do the reads; writes become dirty pages flushed later (`msync`).
- `stat` fields worth knowing: size, mode, uid/gid, nlink, inode, atime/mtime/ctime (**ctime is inode change time, not creation**).
- Max open files: `ulimit -n`; "too many open files" is the usual failure of code that opens a file per record or per run (relevant to Q7/Q8 partitioning).

---

## 7. Java NIO equivalents

Confluent is a heavily Java-based shop, and the Blind commenters assumed Java. If you're asked to use Java, map the same ideas:

| Python (above) | Java |
|---|---|
| `with open(...)` | try-with-resources |
| `for line in f` (stream lines) | `Files.lines(path)` (close the stream!) / `BufferedReader.readLine()` |
| `f.read(n)` / `f.seek(pos)` | `RandomAccessFile.seek/read`, or `FileChannel.position(pos)` + `read(ByteBuffer)` |
| size of file | `Files.size(path)` / `channel.size()` |
| `os.replace` (atomic overwrite) | `Files.move(src, dst, ATOMIC_MOVE, REPLACE_EXISTING)` |
| `tempfile.mkstemp` | `Files.createTempFile(dir, prefix, suffix)` |
| append | `Files.newBufferedWriter(path, CREATE, APPEND)` |
| `shutil.copyfileobj` | `Files.copy(in, path)` / `FileChannel.transferTo` (zero-copy) |
| `os.walk` | `Files.walk(path)` / `Files.walkFileTree` (handles symlinks/visit order) |
| `mmap` | `FileChannel.map(READ_ONLY, 0, size)` → `MappedByteBuffer` |
| `os.path.isdir/isfile` | `Files.isDirectory/isRegularFile` |
| `os.fsync` | `FileChannel.force(true)` |
| `struct.pack` / `zlib.crc32` | `ByteBuffer` (set `order(BIG_ENDIAN)`) / `java.util.zip.CRC32` |
| Read-whole-file one-liner (OOM risk) | `Files.readAllBytes` / `Files.readString`: say the risk out loud |

---

## 8. Edge-case checklist

State these as you code; they are what the evaluation targets.

**Content:** empty file · single line · no trailing newline · only newlines · `\r\n` endings · a single enormous line · blank lines · lines with only whitespace · BOM at the start · invalid UTF-8 bytes (decide: `errors="replace"`, `surrogateescape`, or fail) · multi-byte characters straddling a chunk boundary · NUL bytes / binary file.

**Parameters:** `n == 0` · `n` larger than the number of lines · negative `n` · chunk size 1 (tiny chunks in tests flush out boundary bugs) · chunk size larger than the file · `parts` > number of lines.

**Environment:** file missing / is a directory / permission denied · file shrinks or grows while reading · rotated or replaced mid-read · symlink loops · path with spaces/Unicode · file on a network filesystem · disk full during write (and the temp-file cleanup) · crash between write and rename.

**Resources:** every file closed on every path (`with`) · no `readlines()`/`read()` on unknown sizes · bounded memory stated explicitly · number of open files bounded (partitioning) · no per-byte syscalls.

**Process:** say the complexity in terms of bytes read and syscalls · test with tiny chunk sizes and tiny inputs first · small helper functions · deterministic output order (tie-breaks) · what you would do with more time (streaming output, parallelism, `mmap`, better error reporting).

---

## 9. Sources

**Confluent interview reports (the basis of the "reported" labels).** I viewed search-result snippets of these, not every full page; some content is behind logins or paywalls, so confirm details on the pages themselves.

- Blind, "Confluent coding round on files": <https://www.teamblind.com/post/confluent-coding-round-on-files-6trec0sk>
- Blind, "Interview question: implement tail and word search": <https://www.teamblind.com/post/interview-question-implement-tail-and-word-search-rui1ubzc>
- LeetCode Discuss, "Confluent | Senior Software Engineer | Offer" (huge-file memory round): <https://leetcode.com/discuss/interview-experience/5166350/Confluent-or-Senior-Software-Engineer-or-Offer>
- PracHub, "Implement File Tail and Sensor Health" (Confluent onsite): <https://prachub.com/coding-questions/implement-file-tail-and-sensor-health>
- PracHub, "Implement tail -n for a Very Large File" (Confluent): <https://prachub.com/interview-questions/implement-tail-n-for-a-very-large-file>
- PracHub, "Confluent Senior Software Engineer Interview Experience: A Linux-Heavy Super Day" (word/phrase lookup, `get/put/getAverage`, `tail -n`, Linux questions): <https://prachub.com/interview-experiences/confluent-senior-software-engineer-interview-experience-a-linux-heavy-super-day-with-no-feedback>
- PracHub, "Confluent Software Engineer interview questions guide 2026": <https://prachub.com/interview-guide/confluent-software-engineer-interview-questions-guide-2026>
- Exponent, "Senior Software Engineer 2 interview experience" (Confluent): <https://www.tryexponent.com/experiences/confluent-software-engineer-interview-a3aef3>

**General references for the techniques**
- "Implement your own tail (read last n lines of a huge file)", GeeksforGeeks: <https://www.geeksforgeeks.org/?p=137723> (note its caveat about `fseek`/`ftell` limits on very large files in C)
- Codemia, "Get last n lines of a file, similar to tail": <https://codemia.io/knowledge-hub/path/get_last_n_lines_of_a_file_similar_to_tail>
- GNU coreutils `tail.c`, which a Blind poster cited as the real implementation (complex; just know it uses block-wise reverse reads): <http://git.savannah.gnu.org/cgit/coreutils.git/tree/src/tail.c>
- Python docs: `open`, `io`, `os`, `shutil`, `tempfile`, `mmap`, `csv` (the `newline=""` requirement), `heapq.merge`, `collections.OrderedDict`, `logging.handlers.RotatingFileHandler`.
- Martin Kleppmann, *Designing Data-Intensive Applications*, ch. 3 (log-structured storage, compaction, SSTables) and ch. 7 (transactions): background for Q16. Apache Kafka documentation on the log, segments and log compaction (from memory; not re-opened while writing).

**What I labelled "predicted"** (Q2, Q7 to Q16): these are my extrapolations from the round description (file reading and manipulation, file APIs, optimal implementation, edge cases) and from the Blind thread's list of likely topics. No candidate reported them as Confluent questions. The sensor-health and `getAverage` specs are my reconstructions of garbled or summarized reports.
