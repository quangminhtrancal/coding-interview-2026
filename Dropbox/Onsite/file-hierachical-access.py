'''
"You are asked to simulate a simple hierarchical file system and implement an access-check function.\n\nThe file system consists of folders arranged in a tree. A user is granted **direct access** to a subset of folders. Access is **inherited down the tree**: if the user has access to a parent folder, they automatically have access to all of its descendant folders.\n\nYou are given:\n\n- A list of all folders in the system, represented as absolute paths from the root. For example, a tree like:\n\n```text\n/\n├── A\n│   ├── B\n│   │   ├── C\n│   │   └── D\n│   └── E\n└── F\n```\n\ncould be represented as:\n\n```text\nallFolders = [\n  \"/\",
  \"/A\",
  \"/A/B\",
  \"/A/B/C\",
  \"/A/B/D\",
  \"/A/E\",
  \"/F\"
]\n```\n\n- A set of folder paths `accessibleFolders` representing folders to which the user has **direct** access. For example:\n\n```text\naccessibleFolders = { \"/A\", \"/F\" }\n```\n\nYou need to implement the function:\n\n```text\nbool HasAccess(string folderPath)\n```\n\nthat returns:\n\n- `true` if the user has access to `folderPath` **either** because:\n  - `folderPath` is in `accessibleFolders`, **or**\n  - some ancestor folder of `folderPath` (e.g., `/A` is an ancestor of `/A/B/C`) is in `accessibleFolders`.\n- `false` otherwise.\n\nAssume:\n\n- All folder paths in `allFolders` and `accessibleFolders` are normalized absolute paths starting with `'/'`, with components separated by `'/'` (e.g., `/A/B/C`).\n- `folderPath` passed into `HasAccess` is always a valid folder path present in `allFolders`.\n\nExamples (given the tree above and `accessibleFolders = {\"/A\", \"/F\"}`):\n\n- `HasAccess(\"/A\")` → `true` (direct access)\n- `HasAccess(\"/A/B\")` → `true` (inherits from `/A`)\n- `HasAccess(\"/A/B/C\")` → `true` (inherits from `/A`)\n- `HasAccess(\"/A/E\")` → `true` (inherits from `/A`)\n- `HasAccess(\"/F\")` → `true` (direct access)\n- `HasAccess(\"/\")` → `false` (no access to root unless `/` is in `accessibleFolders`)\n\nDesign and implement `HasAccess` so that it can be called many times efficiently after the initial inputs (`allFolders` and `accessibleFolders`) are known.",

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


# ============================================================================
# TESTS
# ============================================================================

def test_file_access_checker():
    """Test all implementations with the provided examples."""

    # Test data from problem statement
    all_folders = [
        "/",
        "/A",
        "/A/B",
        "/A/B/C",
        "/A/B/D",
        "/A/E",
        "/F"
    ]

    accessible_folders = {"/A", "/F"}

    # Test all implementations
    implementations = [
        ("Simple", FileAccessChecker_Simple),
        ("Optimized", FileAccessChecker_Optimized),
        ("Trie", FileAccessChecker_Trie),
        ("Recommended", FileAccessChecker),
    ]

    test_cases = [
        ("/A", True, "direct access"),
        ("/A/B", True, "inherits from /A"),
        ("/A/B/C", True, "inherits from /A"),
        ("/A/E", True, "inherits from /A"),
        ("/F", True, "direct access"),
        ("/", False, "no access to root"),
    ]

    for impl_name, impl_class in implementations:
        print(f"\n{'='*60}")
        print(f"Testing: {impl_name}")
        print(f"{'='*60}")

        checker = impl_class(all_folders, accessible_folders)

        all_passed = True
        for folder_path, expected, description in test_cases:
            result = checker.has_access(folder_path)
            status = "✓" if result == expected else "✗"

            if result != expected:
                all_passed = False

            print(f"{status} HasAccess('{folder_path}') = {result} (expected {expected}) - {description}")

        if all_passed:
            print(f"\n✓ All tests passed for {impl_name}!")
        else:
            print(f"\n✗ Some tests failed for {impl_name}")


def test_edge_cases():
    """Test edge cases."""

    print(f"\n{'='*60}")
    print("Testing Edge Cases")
    print(f"{'='*60}")

    # Edge case 1: Root access
    all_folders = ["/", "/A", "/A/B"]
    accessible_folders = {"/"}
    checker = FileAccessChecker(all_folders, accessible_folders)

    print("\nEdge Case 1: Root has access")
    print(f"  HasAccess('/') = {checker.has_access('/')} (expected True)")
    print(f"  HasAccess('/A') = {checker.has_access('/A')} (expected True)")
    print(f"  HasAccess('/A/B') = {checker.has_access('/A/B')} (expected True)")

    # Edge case 2: No access at all
    accessible_folders = set()
    checker = FileAccessChecker(all_folders, accessible_folders)

    print("\nEdge Case 2: No accessible folders")
    print(f"  HasAccess('/') = {checker.has_access('/')} (expected False)")
    print(f"  HasAccess('/A') = {checker.has_access('/A')} (expected False)")

    # Edge case 3: Deep nesting
    all_folders = ["/", "/A", "/A/B", "/A/B/C", "/A/B/C/D", "/A/B/C/D/E"]
    accessible_folders = {"/A"}
    checker = FileAccessChecker(all_folders, accessible_folders)

    print("\nEdge Case 3: Deep nesting")
    print(f"  HasAccess('/A/B/C/D/E') = {checker.has_access('/A/B/C/D/E')} (expected True)")

    # Edge case 4: Multiple accessible folders in same path
    all_folders = ["/", "/A", "/A/B", "/A/B/C"]
    accessible_folders = {"/A", "/A/B"}  # Redundant, but valid
    checker = FileAccessChecker(all_folders, accessible_folders)

    print("\nEdge Case 4: Redundant accessible folders")
    print(f"  HasAccess('/A/B/C') = {checker.has_access('/A/B/C')} (expected True)")


def performance_comparison():
    """Compare performance of different implementations."""
    import time

    print(f"\n{'='*60}")
    print("Performance Comparison")
    print(f"{'='*60}")

    # Create a large test case
    all_folders = ["/"]
    for i in range(100):
        all_folders.append(f"/folder{i}")
        for j in range(10):
            all_folders.append(f"/folder{i}/subfolder{j}")
            for k in range(5):
                all_folders.append(f"/folder{i}/subfolder{j}/deep{k}")

    accessible_folders = {f"/folder{i}" for i in range(0, 100, 10)}

    implementations = [
        ("Simple", FileAccessChecker_Simple),
        ("Optimized", FileAccessChecker_Optimized),
        ("Trie", FileAccessChecker_Trie),
        ("Recommended", FileAccessChecker),
    ]

    print(f"\nTest set: {len(all_folders)} folders, {len(accessible_folders)} accessible")

    for impl_name, impl_class in implementations:
        # Measure initialization time
        start = time.time()
        checker = impl_class(all_folders, accessible_folders)
        init_time = (time.time() - start) * 1000

        # Measure query time (1000 queries)
        test_queries = all_folders[:1000]
        start = time.time()
        for folder in test_queries:
            checker.has_access(folder)
        query_time = (time.time() - start) * 1000

        print(f"\n{impl_name}:")
        print(f"  Init time: {init_time:.2f}ms")
        print(f"  Query time (1000 queries): {query_time:.2f}ms")
        print(f"  Avg per query: {query_time/1000:.4f}ms")


if __name__ == "__main__":
    # Run all tests
    test_file_access_checker()
    test_edge_cases()
    performance_comparison()

    print(f"\n{'='*60}")
    print("Example Usage")
    print(f"{'='*60}")

    # Example from problem statement
    all_folders = ["/", "/A", "/A/B", "/A/B/C", "/A/B/D", "/A/E", "/F"]
    accessible_folders = {"/A", "/F"}

    checker = FileAccessChecker(all_folders, accessible_folders)

    print("\nFolder structure:")
    print("  /")
    print("  ├── A (accessible)")
    print("  │   ├── B")
    print("  │   │   ├── C")
    print("  │   │   └── D")
    print("  │   └── E")
    print("  └── F (accessible)")

    print("\nAccess checks:")
    for folder in all_folders:
        has_access = checker.has_access(folder)
        print(f"  HasAccess('{folder}') = {has_access}")

    # Show all accessible folders
    all_accessible = checker.get_all_accessible_folders(all_folders)
    print(f"\nAll accessible folders: {sorted(all_accessible)}")
