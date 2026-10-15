import os
import sys

TARGET_BYTES = 10 * 1024**3
TAIL_LINES = 100


def make_big_log(path: str, target_bytes: int = TARGET_BYTES, tail_lines: int = TAIL_LINES) -> int:
    """Write filler log lines until target_bytes, then end with 'line 1' ... 'line <tail_lines>'."""
    # One ~1 MB block of filler lines, repeated until the target size is reached.
    block = "".join(
        f"2026-10-14T12:00:00Z INFO service=orders request_id={i:08d} msg=filler entry for big log test\n"
        for i in range(11_000)
    ).encode()

    written = 0
    with open(path, "wb") as f:
        while written < target_bytes:
            f.write(block)
            written += len(block)
        tail = "".join(f"line {i}\n" for i in range(1, tail_lines + 1)).encode()
        f.write(tail)
        written += len(tail)
    return written


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/big_10gb.log"
    size = make_big_log(out)
    print(f"{out}: {size} bytes ({size / 1024**3:.2f} GiB), on disk: {os.path.getsize(out)}")
