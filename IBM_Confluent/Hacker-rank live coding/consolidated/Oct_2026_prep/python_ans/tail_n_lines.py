import os
from collections import deque
from concurrent.futures import ThreadPoolExecutor


'''
n: how many lines to return from the end
block_size: number of bytes rea per step while walking backward

return last n lines from the big file with oldest first

Time O(K+B) K is the bytes of last n lines
Space O(K+B)
'''
def tail_backward(path: str, n: int, block_size: int=8192) -> list[str]:
    # block_size: int = 8192 specifies reading 8,192 bytes (or 8 KiB) at a time.
    if n <= 0:
        return []

    with open(path, "rb") as f:
        '''
        In f.seek(0, os.SEEK_END):

            0 (the offset): The number of bytes to move. Here, 0 means zero bytes.

            os.SEEK_END (the reference position/whence): Refers to the end of the file (equivalent to the integer 2).
            Combining them: Moving 0 bytes relative to the end of the file positions the file pointer at the very end of the file.
        '''
        pos = f.seek(0, os.SEEK_END)

        chunks: list[bytes] = []

        newlines = 0

        while pos > 0 and newlines <= n:
            read_size = min(block_size, pos) # last block might be smaller than block_size

            pos -= read_size

            f.seek(pos)
            chunk = f.read(read_size)
            chunks.append(chunk)

            newlines += chunk.count(b"\n") # bytes.count runs in C much faster than in python

    data = b"".join(reversed(chunks))

    # splitlines handles "\n" and "\r\n" and does not return a trailing empty string.
    # which is safe for UTF-8 because b"\n" never appears inside a multi-byte character
    lines = data.splitlines()[-n:]

    return [line.decode("utf-8", errors="replace") for line in lines]

# not goo solution since it read from front
def tail_deque(path: str, n: int) -> list[str]:
    """
    Stream the whole file keeping only n lines. O(F) time and O(n * L) space

    raises FileNotFoundError/ PermissionError

    """
    if n <= 0:
        return []

    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return (line.rstrip("\r\n") for line in deque(f, maxlen=n))


'''

'''