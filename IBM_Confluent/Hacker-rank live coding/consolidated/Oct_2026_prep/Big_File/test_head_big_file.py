import os
import subprocess
import sys
import tempfile
import time

from head_big_file import head_forward, head_islice, head_iter

LOG_PATH = sys.argv[1] if len(sys.argv) > 1 else "/tmp/big_10gb.log"


def filler(j: int) -> str:
    # make_big_log.py repeats a block of 11,000 filler lines, so line j has request_id = j % 11000.
    return f"2026-10-14T12:00:00Z INFO service=orders request_id={j % 11000:08d} msg=filler entry for big log test"


def timed(fn, *args):
    start = time.perf_counter()
    result = fn(*args)
    return result, time.perf_counter() - start


def check_big_file() -> None:
    size = os.path.getsize(LOG_PATH)
    print(f"file: {LOG_PATH} ({size / 1024**3:.2f} GiB)")

    # n = 25000 crosses the 11,000-line block boundary of the generator twice.
    for n in (1, 100, 25_000):
        expected = [filler(j) for j in range(n)]

        result, secs = timed(head_forward, LOG_PATH, n)
        assert result == expected, f"head_forward mismatch for n={n}"
        print(f"head_forward n={n:>6}: OK in {secs * 1000:.2f} ms")

        result, secs = timed(lambda: list(head_iter(LOG_PATH, n)))
        assert result == expected, f"head_iter mismatch for n={n}"
        print(f"head_iter    n={n:>6}: OK in {secs * 1000:.2f} ms")

        result, secs = timed(head_islice, LOG_PATH, n)
        assert result == expected, f"head_islice mismatch for n={n}"
        print(f"head_islice  n={n:>6}: OK in {secs * 1000:.2f} ms")

    # Cross-check against the system head command.
    out = subprocess.run(["head", "-n", "100", LOG_PATH], capture_output=True, text=True, check=True).stdout
    assert head_forward(LOG_PATH, 100) == out.splitlines(), "differs from `head -n 100`"
    print("matches `head -n 100`")


def check_small_files() -> None:
    cases = {
        "empty": b"",
        "one line no newline": b"a",
        "no trailing newline": b"a\nb\nc",
        "trailing newline": b"a\nb\nc\n",
        "crlf": b"a\r\nb\r\nc\r\n",
        "blank lines": b"\n\na\n\n",
    }
    for name, content in cases.items():
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(content)
        try:
            for n in (0, 1, 2, 3, 10):
                expected = content.decode().splitlines()[:n]
                for block_size in (1, 2, 8192):
                    assert head_forward(tmp.name, n, block_size) == expected, (name, n, block_size)
                    assert list(head_iter(tmp.name, n, block_size)) == expected, (name, n, block_size)
                assert head_islice(tmp.name, n) == expected, (name, n)
        finally:
            os.remove(tmp.name)
    print("small-file edge cases OK")


if __name__ == "__main__":
    check_small_files()
    check_big_file()
    print("all head options match")
