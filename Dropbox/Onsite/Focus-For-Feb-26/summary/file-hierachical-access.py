'''
"You are asked to simulate a simple hierarchical file system and implement an access-check function.\n\nThe file system consists of folders arranged in a tree. A user is granted **direct access** to a subset of folders. Access is **inherited down the tree**: if the user has access to a parent folder, they automatically have access to all of its descendant folders.\n\nYou are given:\n\n- A list of all folders in the system, represented as absolute paths from the root. For example, a tree like:\n\n```text\n/\n├── A\n│   ├── B\n│   │   ├── C\n│   │   └── D\n│   └── E\n└── F\n```\n\ncould be represented as:\n\n```text\nallFolders = [\n  \"/\",
  \"/A\",
  \"/A/B\",
  \"/A/B/C\",
  \"/A/B/D\",
  \"/A/E\",
  \"/F\"
]\n```\n\n- A set of folder paths `accessibleFolders` representing folders to which the user has **direct** access. For example:\n\n
```text\naccessibleFolders = { \"/A\", \"/F\" }\n```\n\nYou need to implement the function:\n\n```text\nbool HasAccess(string folderPath)\n
```\n\nthat returns:\n\n- `true` if the user has access to `folderPath` **either** because:\n  
- `folderPath` is in `accessibleFolders`, **or**\n  - some ancestor folder of `folderPath` 
(e.g., `/A` is an ancestor of `/A/B/C`) is in `accessibleFolders`.\n- `false` otherwise.\n\nAssume:\n\n
- All folder paths in `allFolders` and `accessibleFolders` are normalized absolute paths starting with `'/'`, 
with components separated by `'/'` (e.g., `/A/B/C`).\n- `folderPath` passed into `HasAccess` is always a valid folder path present in `allFolders`.\n\n
Examples (given the tree above and `accessibleFolders = {\"/A\", \"/F\"}`):\n\n

- `HasAccess(\"/A\")` → `true` (direct access)\n
- `HasAccess(\"/A/B\")` → `true` (inherits from `/A`)\n
- `HasAccess(\"/A/B/C\")` → `true` (inherits from `/A`)\n
- `HasAccess(\"/A/E\")` → `true` (inherits from `/A`)\n-
 `HasAccess(\"/F\")` → `true` (direct access)\n- `HasAccess(\"/\")` → `false` (no access to root unless `/` is in `accessibleFolders`)\n\n
 
 Design and implement `HasAccess` so that it can be called many times efficiently after the initial inputs (`allFolders` and `accessibleFolders`) are known.",

https://prachub.com/interview-questions/implement-hierarchical-folder-access-check

You are asked to simulate a simple hierarchical file system and implement an access-check function.

The file system consists of folders arranged in a tree. A user is granted direct access to a subset of folders. Access is inherited down the tree: if the user has access to a parent folder, they automatically have access to all of its descendant folders.

You are given:

A list of all folders in the system, represented as absolute paths from the root. For example, a tree like:
/
├── A
│   ├── B
│   │   ├── C
│   │   └── D
│   └── E
└── F
could be represented as:

allFolders = [
  "/",
  "/A",
  "/A/B",
  "/A/B/C",
  "/A/B/D",
  "/A/E",
  "/F"
]
A set of folder paths accessibleFolders representing folders to which the user has direct access. For example:
accessibleFolders = { "/A", "/F" }
You need to implement the function:

bool HasAccess(string folderPath)
that returns:

true if the user has access to folderPath either because:
folderPath is in accessibleFolders , or
some ancestor folder of folderPath (e.g., /A is an ancestor of /A/B/C ) is in accessibleFolders .
false otherwise.
Assume:

All folder paths in allFolders and accessibleFolders are normalized absolute paths starting with '/' , with components separated by '/' (e.g., /A/B/C ).
folderPath passed into HasAccess is always a valid folder path present in allFolders .
Examples (given the tree above and accessibleFolders = {"/A", "/F"}):

HasAccess("/A") → true (direct access)
HasAccess("/A/B") → true (inherits from /A )
HasAccess("/A/B/C") → true (inherits from /A )
HasAccess("/A/E") → true (inherits from /A )
HasAccess("/F") → true (direct access)
HasAccess("/") → false (no access to root unless / is in accessibleFolders )
Design and implement HasAccess so that it can be called many times efficiently after the initial inputs (allFolders and accessibleFolders) are known.
'''

from typing import List, Set

#### Gemini simple answer

# Implementation 1: The "Lookup" Optimized ApproachThis is the most common and practical solution for a Dropbox-style interview. 
# It uses $O(1)$ average time for set lookups and $O(L)$ time to traverse the path string (where $L$ is the depth of the folder).Python

class FileAccessSystem:

    def __init__(self, allFolders, accessibleFolders):
        # We store accessibleFolders in a Set for O(1) lookup
        # Optimization: We can "shrink" this set by removing redundant paths.
        # (e.g., if we have "/A" and "/A/B", "/A/B" is redundant)
        self.accessible = self._simplify_access(accessibleFolders)

    def _simplify_access(self, folders):
        # This pre-processing step makes the set smaller and lookups faster
        sorted_folders = sorted(folders, key=len)
        minimized = set()
        for f in sorted_folders:
            # Only add folder if none of its ancestors are already in minimized
            if not self._check_ancestors(f, minimized):
                minimized.add(f)
        return minimized

    def _check_ancestors(self, path, folder_set):
        if path in folder_set:
            return True
        # Logic to climb up the tree
        while path != "/":
            # Strip the last part of the path (e.g., /A/B/C -> /A/B)
            path = path.rsplit('/', 1)[0]
            if not path: # Handle the root edge case after rsplit
                path = "/"
            if path in folder_set:
                return True
        return False

    def HasAccess(self, folderPath: str) -> bool:
        # Standard lookup: climb the path until we hit a match or the root
        return self._check_ancestors(folderPath, self.accessible)


#### Gemini trie

class FolderNode:
    def __init__(self):
        self.children = {}
        self.has_access = False

class FileAccessTrie:
    def __init__(self, allFolders, accessibleFolders):
        self.root = FolderNode()
        for path in accessibleFolders:
            self.add_access(path)

    def add_access(self, path):
        node = self.root
        if path == "/":
            node.has_access = True
            return
        
        parts = path.strip("/").split("/")
        for part in parts:
            if part not in node.children:
                node.children[part] = FolderNode()
            node = node.children[part]
        node.has_access = True

    def HasAccess(self, folderPath: str) -> bool:
        node = self.root
        if node.has_access: return True # Root access
        
        if folderPath == "/": return node.has_access
        
        parts = folderPath.strip("/").split("/")
        for part in parts:
            if part not in node.children:
                return False # No more direct access markers found
            node = node.children[part]
            if node.has_access:
                return True # Inherited access found!
        return False
    
# ============================================================================
# APPROACH 1: Simple Solution - Check Ancestors On-The-Fly
# ============================================================================

class FileAccessChecker_Simple:
    """
    Simple approach: For each HasAccess call, check all ancestors.

    Time Complexity:
    - Initialization: O(1)
    - HasAccess: O(depth) where depth is the folder depth

    Space Complexity: O(m) where m = len(accessibleFolders)

    Good for: Few HasAccess calls, deep folder structures
    """

    def __init__(self, all_folders: List[str], accessible_folders: Set[str]):
        self.accessible_folders = accessible_folders

    def has_access(self, folder_path: str) -> bool:
        """Check if user has access by checking all ancestor paths."""
        # Check if folder itself is accessible
        if folder_path in self.accessible_folders:
            return True

        # Check all ancestors
        # For "/A/B/C", check "/A/B", "/A", "/"
        path = folder_path
        while path != "/":
            # Remove last component
            last_slash = path.rfind("/")
            if last_slash == 0:  # We're at root level
                path = "/"
            else:
                path = path[:last_slash]

            if path in self.accessible_folders:
                return True

        return False


# ============================================================================
# APPROACH 2: Optimized - Precompute All Accessible Folders
# ============================================================================

class FileAccessChecker_Optimized:
    """
    Optimized approach: Precompute all accessible folders during initialization.

    Time Complexity:
    - Initialization: O(n) where n = len(allFolders)
    - HasAccess: O(1)

    Space Complexity: O(n)

    Good for: Many HasAccess calls (trade initialization time for query time)
    """

    def __init__(self, all_folders: List[str], accessible_folders: Set[str]):
        # Precompute all folders that are accessible (directly or through inheritance)
        self.all_accessible = set()

        for folder in all_folders:
            if self._is_accessible(folder, accessible_folders):
                self.all_accessible.add(folder)

    def _is_accessible(self, folder_path: str, accessible_folders: Set[str]) -> bool:
        """Helper to check if a folder is accessible."""
        # Check if folder itself is accessible
        if folder_path in accessible_folders:
            return True

        # Check all ancestors
        path = folder_path
        while path != "/":
            last_slash = path.rfind("/")
            if last_slash == 0:
                path = "/"
            else:
                path = path[:last_slash]

            if path in accessible_folders:
                return True

        return False

    def has_access(self, folder_path: str) -> bool:
        """O(1) lookup after preprocessing."""
        return folder_path in self.all_accessible


# ============================================================================
# APPROACH 3: Trie-Based Solution (Most Efficient for Deep Hierarchies)
# ============================================================================

class TrieNode:
    """Node in the folder trie."""

    def __init__(self):
        self.children = {}  # folder_name -> TrieNode
        self.has_direct_access = False  # Is this folder directly accessible?
        self.has_inherited_access = False  # Does this inherit access from parent?


class FileAccessChecker_Trie:
    """
    Trie-based approach: Build a trie of accessible folders.

    Time Complexity:
    - Initialization: O(m * k) where m = len(accessibleFolders), k = avg path depth
    - HasAccess: O(depth) with early termination

    Space Complexity: O(m * k)

    Good for: Large number of folders with deep hierarchies, prefix-based queries
    """

    def __init__(self, all_folders: List[str], accessible_folders: Set[str]):
        self.root = TrieNode()

        # Build trie from accessible folders
        for folder in accessible_folders:
            self._insert(folder)

        # Mark all descendants as having inherited access
        self._propagate_access(self.root, False)

    def _insert(self, folder_path: str):
        """Insert a folder path into the trie."""
        if folder_path == "/":
            self.root.has_direct_access = True
            return

        # Split path into components
        components = folder_path.split("/")[1:]  # Skip empty string from leading /

        node = self.root
        for component in components:
            if component not in node.children:
                node.children[component] = TrieNode()
            node = node.children[component]

        node.has_direct_access = True

    def _propagate_access(self, node: TrieNode, parent_has_access: bool):
        """Propagate access rights down the tree."""
        # If parent has access or this node has direct access, mark as accessible
        has_access = parent_has_access or node.has_direct_access
        node.has_inherited_access = has_access

        # Propagate to children
        for child in node.children.values():
            self._propagate_access(child, has_access)

    def has_access(self, folder_path: str) -> bool:
        """Check access by traversing trie."""
        if folder_path == "/":
            return self.root.has_direct_access or self.root.has_inherited_access

        components = folder_path.split("/")[1:]
        node = self.root

        # Early termination: if any ancestor has access, we have access
        if node.has_direct_access or node.has_inherited_access:
            return True

        for component in components:
            if component not in node.children:
                return False
            node = node.children[component]
            if node.has_direct_access or node.has_inherited_access:
                return True

        return node.has_inherited_access


# ============================================================================
# APPROACH 4: Most Practical Solution (Recommended for Interview)
# ============================================================================

class FileAccessChecker:
    """
    Best balance between simplicity and efficiency.

    Approach: Store accessible folders in a set, check ancestors on query.
    Use path manipulation tricks for efficiency.

    Time Complexity:
    - Initialization: O(1)
    - HasAccess: O(depth) = typically O(log n) for balanced trees

    Space Complexity: O(m)

    This is the recommended solution for interviews because:
    1. Simple and easy to explain
    2. Efficient for most practical cases
    3. Low memory overhead
    4. Easy to extend (e.g., add caching)
    """

    def __init__(self, all_folders: List[str], accessible_folders: Set[str]):
        """
        Initialize the access checker.

        Args:
            all_folders: List of all folder paths in the system
            accessible_folders: Set of folders the user has direct access to
        """
        self.accessible_folders = accessible_folders
        # Optional: Add caching for frequently accessed paths
        self.cache = {}

    def has_access(self, folder_path: str) -> bool:
        """
        Check if the user has access to the given folder.

        Returns True if the user has direct access to the folder or any of its ancestors.

        Args:
            folder_path: The folder path to check

        Returns:
            True if user has access, False otherwise
        """
        # Check cache first (optional optimization)
        if folder_path in self.cache:
            return self.cache[folder_path]

        # Check current folder and all ancestors
        current = folder_path

        while True:
            if current in self.accessible_folders:
                self.cache[folder_path] = True
                return True

            # Reached root without finding access
            if current == "/":
                self.cache[folder_path] = False
                return False

            # Move to parent folder
            # For "/A/B/C" -> "/A/B", for "/A" -> "/"
            last_slash_idx = current.rfind("/")
            if last_slash_idx == 0:  # Parent is root
                current = "/"
            else:
                current = current[:last_slash_idx]

    def get_all_accessible_folders(self, all_folders: List[str]) -> Set[str]:
        """
        Optional: Get all accessible folders (including inherited access).
        Useful for UI or reporting purposes.
        """
        accessible = set()
        for folder in all_folders:
            if self.has_access(folder):
                accessible.add(folder)
        return accessible


'''
https://www.1point3acres.com/interview/problems/f0867d5b-4d3f-4ff4-9af3-0c7f8b8160ca

Problem Description
Given a file system represented as a List<List<string>> folders and a HashSet<string> accesses, 
implement a function HasAccess(string folder) to determine if a user has access to a specified folder. 
Access rights are inherited, meaning if a user can access a parent folder, they can also access the child folder.

Input:

folders: A hierarchical structure representation of the file system, where each list describes a parent-child relationship. 
Example: [['A', 'B'], ['B', 'C'], ['B', 'D'], ['A', 'E'], ['E', 'F']] means /A has directories /B and /E, /B contains /C and /D, and /E contains /F.
accesses: An initial set of folders the user has access to. Example: {'A'}
Output:

Return a boolean value indicating whether the user has access to the specified folder or not.
Requirement:

Implement the function HasAccess(string folder) to check permission according to the given rules.
Example

Input: folders = [['A', 'B'], ['B', 'C'], ['B', 'D'], ['A', 'E'], ['E', 'F']], accesses = {'A'}

Queries:

HasAccess('C') should return True
HasAccess('F') should return True
HasAccess('D') should return True
HasAccess('B') should return True
Constraints
Folder names are unique strings
Assume the number of folders will not exceed 10,000
'''

from typing import List, Set, Dict
from collections import defaultdict, deque


# ============================================================================
# SOLUTION 1: Precompute All Accessible Folders (RECOMMENDED)
# ============================================================================

class FileSystemAccessControl:
    """
    Optimal solution: Precompute all accessible folders during initialization.

    Time Complexity:
    - Initialization: O(N) where N = number of folders
    - HasAccess: O(1)

    Space Complexity: O(N)

    Best for: Multiple HasAccess queries
    """

    def __init__(self, folders: List[List[str]], accesses: Set[str]):
        """
        Initialize the file system with folder structure and access rights.

        Args:
            folders: List of [parent, child] relationships
            accesses: Set of folders user has direct access to
        """
        # Build parent->children mapping
        self.children_map = defaultdict(list)
        for parent, child in folders:
            self.children_map[parent].append(child)

        # Precompute all accessible folders using BFS
        self.accessible_folders = self._compute_accessible_folders(accesses)

    def _compute_accessible_folders(self, accesses: Set[str]) -> Set[str]:
        """
        Compute all folders accessible from the initial access set.

        Uses BFS to traverse from accessible roots to all descendants.
        """
        accessible = set(accesses)  # Start with directly accessible folders
        queue = deque(accesses)

        while queue:
            folder = queue.popleft()

            # Add all children to accessible set
            for child in self.children_map[folder]:
                if child not in accessible:
                    accessible.add(child)
                    queue.append(child)

        return accessible

    def has_access(self, folder: str) -> bool:
        """
        Check if user has access to the folder.

        O(1) lookup after preprocessing.
        """
        return folder in self.accessible_folders