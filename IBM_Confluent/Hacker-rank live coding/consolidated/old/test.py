from collections import Counter
import os

def tail_backward(path, n):
    if n == 0:
        return []

    with open(path, "rb") as f:
        f.seek(0, os.SEEK_END)

if __name__ == "__main__":
    counts = count_event_bytes("events.log")
