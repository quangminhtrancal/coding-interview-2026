'''
https://prachub.com/companies/dropbox/categories/coding-and-algorithms?sort=hot

You are building a simple file crawler. Task Implement an API function: 
Input:** a filesystem path `rootPath`\n- **Output:** a list/array of **all file paths** 
contained under `rootPath` (recursively), 
in any order.

Assume:- Paths can be directories or files.- 

You are given a helper function similar to:
- `listChildren(path) -> (subdirs, files)` where `subdirs` are immediate child directories and 
`files` are immediate child files.

# Notes / edge cases to clarify in your solution\n- 
If `rootPath` is a file, return just `[rootPath]`.
 Decide what to do if the path does not exist or is not accessible 
 (e.g., throw an error vs return empty).
 Avoid infinite loops if the filesystem can contain symlinks 
 (state your assumption if you ignore symlinks).",

'''

import os
from collections import deque

def bfs_file_crawler(root_path):
    """
    Breadth-first search file crawler.
    Returns a list of all file paths under root_path.
    """
    files = []
    queue = deque([root_path])

    while queue:
        current = queue.popleft()
        if os.path.isdir(current):
            try:
                for entry in os.listdir(current):
                    full_path = os.path.join(current, entry)
                    queue.append(full_path)
            except PermissionError:
                continue  # Skip directories we can't access
        elif os.path.isfile(current):
            files.append(current)
    return files

if __name__ == "__main__":
    root = "."  # or any directory you want to crawl
    all_files = bfs_file_crawler(root)
    for f in all_files:
        print(f)