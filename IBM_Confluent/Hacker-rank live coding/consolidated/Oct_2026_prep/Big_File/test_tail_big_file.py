import os
import sys
import time

from tail_big_file import tail_backward, tail_deque

LOG_PATH = sys.argv[1] if len(sys.argv) > 1 else "/tmp/big_10gb.log"
N = 100
EXPECTED = [f"line {i}" for i in range(1, N + 1)]


def timed(fn, *args):
    start = time.perf_counter()
    result = fn(*args)
    return result, time.perf_counter() - start


def main() -> None:
    size = os.path.getsize(LOG_PATH)
    print(f"file: {LOG_PATH} ({size / 1024**3:.2f} GiB)")

    result, secs = timed(tail_backward, LOG_PATH, N)
    assert result == EXPECTED, "tail_backward mismatch"
    print(f"tail_backward: OK in {secs * 1000:.2f} ms")

    # A smaller n and a larger n spanning filler lines must also agree between the two options.
    for n in (1, 5, 250):
        a = tail_backward(LOG_PATH, n)
        assert len(a) == n
        assert a[-min(n, N):] == EXPECTED[-min(n, N):]

    result, secs = timed(tail_deque, LOG_PATH, N)
    assert result == EXPECTED, "tail_deque mismatch"
    print(f"tail_deque:    OK in {secs:.2f} s")

    assert tail_backward(LOG_PATH, 250) == tail_deque(LOG_PATH, 250), "options disagree for n=250"
    print("both options match the expected last 100 lines")


if __name__ == "__main__":
    main()
