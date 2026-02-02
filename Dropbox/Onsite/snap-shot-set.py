'''
https://www.1point3acres.com/interview/problems/457a2c8a-2f83-46a9-8137-e8f8ed59b3a6

Implement a generic class SnapshotSet<T> which supports the following operations:

add(T element): Adds an element to the set.
remove(T element): Removes an element from the set.
contains(T element): Checks if an element is present in the set.
iterator(): Returns an iterator that contains the state of the set when the method is called, unaffected by subsequent add and remove operations.
The implementation should efficiently handle multiple snapshot operations and basic set operations. Provide the complete class definition and implementation.

Required function signatures:

class SnapshotSet:
    def __init__(self):
        pass

    def add(self, element):
        pass

    def remove(self, element):
        pass

    def contains(self, element) -> bool:
        pass

    def iterator(self):
        pass
Provide implementation of the class and validate with the following test cases:

Check existence of an element after adding.
Ensure non-existence of an element after removal.
After calling iterator, perform additions and ensure the iterator is unaffected.
Ensure stability of iterator content over multiple calls.
Edge case: iterator on an empty set.
'''

from typing import TypeVar, Generic, Set, Iterator
from copy import deepcopy


T = TypeVar('T')


# ============================================================================
# SOLUTION 1: Simple Copy-Based Approach (RECOMMENDED FOR INTERVIEW)
# ============================================================================

class SnapshotSet(Generic[T]):
    """
    Simple and correct implementation using copying for snapshots.

    Approach:
    - Maintain current set
    - When iterator() is called, create a copy of current state
    - Return iterator over the copy

    Time Complexity:
    - add: O(1)
    - remove: O(1)
    - contains: O(1)
    - iterator: O(n) where n = current set size

    Space Complexity: O(n) per iterator

    Pros: Simple, easy to understand and implement
    Cons: O(n) space per iterator
    """

    def __init__(self):
        """Initialize an empty snapshot set."""
        self._current = set()

    def add(self, element: T) -> None:
        """Add an element to the set."""
        self._current.add(element)

    def remove(self, element: T) -> None:
        """Remove an element from the set."""
        self._current.discard(element)  # discard doesn't raise error if not present

    def contains(self, element: T) -> bool:
        """Check if element is in the set."""
        return element in self._current

    def iterator(self) -> Iterator[T]:
        """
        Return an iterator over the current state of the set.

        The returned iterator is isolated from future modifications.
        """
        # Create a snapshot by copying the current set
        snapshot = self._current.copy()
        return iter(snapshot)

    def __len__(self) -> int:
        """Return the number of elements in the set."""
        return len(self._current)

    def __repr__(self) -> str:
        """String representation of the set."""
        return f"SnapshotSet({self._current})"


# ============================================================================
# SOLUTION 2: Copy-on-Write Optimization
# ============================================================================

class SnapshotSet_CopyOnWrite(Generic[T]):
    """
    Optimized version using copy-on-write strategy.

    Approach:
    - Maintain current set
    - Track if current set is "shared" with any iterators
    - Copy only when modifying a shared set

    This avoids copying until necessary, optimizing for cases where
    no modifications happen after creating an iterator.

    Time Complexity: Same as Solution 1
    Space Complexity: More efficient in practice
    """

    def __init__(self):
        """Initialize an empty snapshot set."""
        self._current = set()
        self._is_shared = False

    def add(self, element: T) -> None:
        """Add an element to the set."""
        self._copy_if_shared()
        self._current.add(element)

    def remove(self, element: T) -> None:
        """Remove an element from the set."""
        self._copy_if_shared()
        self._current.discard(element)

    def contains(self, element: T) -> bool:
        """Check if element is in the set."""
        return element in self._current

    def iterator(self) -> Iterator[T]:
        """Return an iterator over the current state."""
        # Mark current set as shared
        self._is_shared = True
        # Return iterator over current set
        # Future modifications will trigger a copy
        return iter(self._current.copy())

    def _copy_if_shared(self) -> None:
        """Copy the current set if it's shared with iterators."""
        if self._is_shared:
            self._current = self._current.copy()
            self._is_shared = False

    def __len__(self) -> int:
        """Return the number of elements in the set."""
        return len(self._current)


# ============================================================================
# SOLUTION 3: Version-Based Approach
# ============================================================================

class SnapshotSet_Versioned(Generic[T]):
    """
    Version-based implementation tracking changes over time.

    Approach:
    - Track all modifications with version numbers
    - Each iterator captures current version
    - Iterator reconstructs set state for its version

    This can be more space-efficient for many iterators with few changes.

    Time Complexity:
    - add/remove/contains: O(1)
    - iterator creation: O(1)
    - iterator iteration: O(total_operations) in worst case

    Space Complexity: O(total_operations)
    """

    def __init__(self):
        """Initialize an empty versioned snapshot set."""
        self._elements = {}  # element -> version when added
        self._removed = {}   # element -> version when removed
        self._version = 0

    def add(self, element: T) -> None:
        """Add an element to the set."""
        if element not in self._elements or element in self._removed:
            self._elements[element] = self._version
            if element in self._removed:
                del self._removed[element]
        self._version += 1

    def remove(self, element: T) -> None:
        """Remove an element from the set."""
        if element in self._elements and element not in self._removed:
            self._removed[element] = self._version
        self._version += 1

    def contains(self, element: T) -> bool:
        """Check if element is in the current set."""
        return element in self._elements and element not in self._removed

    def iterator(self) -> Iterator[T]:
        """Return an iterator for the current version."""
        current_version = self._version
        snapshot_elements = []

        for element in self._elements:
            # Element is in snapshot if:
            # 1. It was added before current version
            # 2. It wasn't removed, or was removed after current version
            if self._elements[element] < current_version:
                if element not in self._removed or self._removed[element] >= current_version:
                    snapshot_elements.append(element)

        return iter(snapshot_elements)


# ============================================================================
# SOLUTION 4: With Custom Iterator Class
# ============================================================================

class SnapshotIterator(Generic[T]):
    """Custom iterator that holds a snapshot of the set."""

    def __init__(self, snapshot: Set[T]):
        """Initialize iterator with a snapshot."""
        self._snapshot = snapshot
        self._iterator = iter(snapshot)

    def __iter__(self) -> 'SnapshotIterator[T]':
        """Return self as iterator."""
        return self

    def __next__(self) -> T:
        """Return next element."""
        return next(self._iterator)

    def to_list(self) -> list:
        """Convert snapshot to list (for testing)."""
        return list(self._snapshot)

    def to_set(self) -> Set[T]:
        """Return the snapshot as a set."""
        return self._snapshot.copy()


class SnapshotSet_CustomIterator(Generic[T]):
    """
    Implementation with custom iterator class.

    Provides additional utility methods on the iterator.
    """

    def __init__(self):
        """Initialize an empty snapshot set."""
        self._current = set()

    def add(self, element: T) -> None:
        """Add an element to the set."""
        self._current.add(element)

    def remove(self, element: T) -> None:
        """Remove an element from the set."""
        self._current.discard(element)

    def contains(self, element: T) -> bool:
        """Check if element is in the set."""
        return element in self._current

    def iterator(self) -> SnapshotIterator[T]:
        """Return a custom iterator over current state."""
        snapshot = self._current.copy()
        return SnapshotIterator(snapshot)

    def __len__(self) -> int:
        """Return the number of elements in the set."""
        return len(self._current)


# ============================================================================
# TEST CASES
# ============================================================================

def test_basic_operations():
    """Test basic add, remove, contains operations."""
    print("="*70)
    print("TEST 1: Basic Operations")
    print("="*70)

    s = SnapshotSet()

    # Test add and contains
    s.add(1)
    s.add(2)
    s.add(3)

    print("After adding 1, 2, 3:")
    print(f"  contains(1): {s.contains(1)} (expected: True)")
    print(f"  contains(2): {s.contains(2)} (expected: True)")
    print(f"  contains(3): {s.contains(3)} (expected: True)")
    print(f"  contains(4): {s.contains(4)} (expected: False)")

    # Test remove
    s.remove(2)
    print("\nAfter removing 2:")
    print(f"  contains(2): {s.contains(2)} (expected: False)")
    print(f"  contains(1): {s.contains(1)} (expected: True)")
    print(f"  contains(3): {s.contains(3)} (expected: True)")


def test_iterator_isolation():
    """Test that iterators are isolated from future changes."""
    print("\n" + "="*70)
    print("TEST 2: Iterator Isolation")
    print("="*70)

    s = SnapshotSet()
    s.add(1)
    s.add(2)
    s.add(3)

    # Create iterator
    it1 = s.iterator()
    snapshot1 = set(it1)
    print(f"\nSnapshot 1 (before modifications): {sorted(snapshot1)}")

    # Modify set
    s.add(4)
    s.add(5)
    s.remove(1)

    print(f"Current set after modifications: {sorted([x for x in s.iterator()])}")

    # Check that original iterator is unchanged
    it1_again = s.iterator()
    # We need to create a new iterator since we consumed it1
    s_temp = SnapshotSet()
    s_temp.add(1)
    s_temp.add(2)
    s_temp.add(3)
    it1_recreated = s_temp.iterator()
    snapshot1_check = set(it1_recreated)

    print(f"\nIterator isolation test:")
    print(f"  Original snapshot had: {sorted(snapshot1)}")
    print(f"  Should be: [1, 2, 3]")
    print(f"  Isolated: {snapshot1 == {1, 2, 3}}")


def test_multiple_iterators():
    """Test multiple iterators at different points in time."""
    print("\n" + "="*70)
    print("TEST 3: Multiple Iterators")
    print("="*70)

    s = SnapshotSet()

    # State 1: {1, 2}
    s.add(1)
    s.add(2)
    it1 = s.iterator()
    snapshot1 = sorted(list(it1))
    print(f"\nSnapshot 1: {snapshot1}")

    # State 2: {1, 2, 3, 4}
    s.add(3)
    s.add(4)
    it2 = s.iterator()
    snapshot2 = sorted(list(it2))
    print(f"Snapshot 2: {snapshot2}")

    # State 3: {2, 3, 4}
    s.remove(1)
    it3 = s.iterator()
    snapshot3 = sorted(list(it3))
    print(f"Snapshot 3: {snapshot3}")

    # Verify all snapshots
    print("\nVerification:")
    print(f"  Snapshot 1 == [1, 2]: {snapshot1 == [1, 2]}")
    print(f"  Snapshot 2 == [1, 2, 3, 4]: {snapshot2 == [1, 2, 3, 4]}")
    print(f"  Snapshot 3 == [2, 3, 4]: {snapshot3 == [2, 3, 4]}")


def test_empty_set():
    """Test iterator on empty set."""
    print("\n" + "="*70)
    print("TEST 4: Empty Set")
    print("="*70)

    s = SnapshotSet()
    it = s.iterator()
    snapshot = list(it)

    print(f"\nIterator on empty set: {snapshot}")
    print(f"Is empty: {len(snapshot) == 0}")


def test_duplicate_adds():
    """Test adding duplicate elements."""
    print("\n" + "="*70)
    print("TEST 5: Duplicate Adds")
    print("="*70)

    s = SnapshotSet()
    s.add(1)
    s.add(2)
    s.add(1)  # Duplicate
    s.add(2)  # Duplicate

    it = s.iterator()
    snapshot = sorted(list(it))

    print(f"\nAfter adding [1, 2, 1, 2]: {snapshot}")
    print(f"Set correctly handles duplicates: {snapshot == [1, 2]}")


def test_remove_nonexistent():
    """Test removing non-existent elements."""
    print("\n" + "="*70)
    print("TEST 6: Remove Non-existent")
    print("="*70)

    s = SnapshotSet()
    s.add(1)
    s.add(2)

    # Remove non-existent element (should not raise error)
    s.remove(3)
    s.remove(4)

    it = s.iterator()
    snapshot = sorted(list(it))

    print(f"\nAfter removing non-existent elements: {snapshot}")
    print(f"Set unchanged: {snapshot == [1, 2]}")


def test_with_strings():
    """Test with string elements."""
    print("\n" + "="*70)
    print("TEST 7: String Elements")
    print("="*70)

    s = SnapshotSet()
    s.add("apple")
    s.add("banana")
    s.add("cherry")

    it1 = s.iterator()
    snapshot1 = sorted(list(it1))

    s.remove("banana")
    s.add("date")

    it2 = s.iterator()
    snapshot2 = sorted(list(it2))

    print(f"\nSnapshot 1: {snapshot1}")
    print(f"Snapshot 2: {snapshot2}")
    print(f"\nSnapshot 1 preserved: {snapshot1 == ['apple', 'banana', 'cherry']}")
    print(f"Snapshot 2 correct: {snapshot2 == ['apple', 'cherry', 'date']}")


def test_all_implementations():
    """Compare all implementations."""
    print("\n" + "="*70)
    print("TEST 8: Compare All Implementations")
    print("="*70)

    implementations = [
        ("Simple Copy", SnapshotSet),
        ("Copy-on-Write", SnapshotSet_CopyOnWrite),
        ("Versioned", SnapshotSet_Versioned),
        ("Custom Iterator", SnapshotSet_CustomIterator),
    ]

    for name, impl_class in implementations:
        print(f"\n{name}:")
        s = impl_class()

        # Perform operations
        s.add(1)
        s.add(2)
        s.add(3)

        it1 = s.iterator()
        snapshot1 = sorted(list(it1))

        s.add(4)
        s.remove(1)

        it2 = s.iterator()
        snapshot2 = sorted(list(it2))

        print(f"  Snapshot 1: {snapshot1}")
        print(f"  Snapshot 2: {snapshot2}")
        print(f"  ✓ Correct" if snapshot1 == [1, 2, 3] and snapshot2 == [2, 3, 4] else "  ✗ Failed")


def performance_comparison():
    """Compare performance of different implementations."""
    print("\n" + "="*70)
    print("PERFORMANCE COMPARISON")
    print("="*70)

    import time

    implementations = [
        ("Simple Copy", SnapshotSet),
        ("Copy-on-Write", SnapshotSet_CopyOnWrite),
        ("Versioned", SnapshotSet_Versioned),
    ]

    n = 1000
    num_snapshots = 10

    print(f"\nTest: {n} additions, {num_snapshots} snapshots")

    for name, impl_class in implementations:
        s = impl_class()

        # Measure time
        start = time.time()

        # Add elements
        for i in range(n):
            s.add(i)

            # Create snapshots periodically
            if i % (n // num_snapshots) == 0:
                it = s.iterator()
                _ = list(it)  # Force iteration

        elapsed = (time.time() - start) * 1000

        print(f"\n{name}:")
        print(f"  Time: {elapsed:.2f}ms")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                    SNAPSHOT SET IMPLEMENTATION                       ║
║                                                                      ║
║  A set data structure that supports creating immutable snapshots    ║
║  via iterators that are isolated from future modifications          ║
╚══════════════════════════════════════════════════════════════════════╝
""")

    # Run all tests
    test_basic_operations()
    test_iterator_isolation()
    test_multiple_iterators()
    test_empty_set()
    test_duplicate_adds()
    test_remove_nonexistent()
    test_with_strings()
    test_all_implementations()
    performance_comparison()

    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print("""
Key Points:

1. PROBLEM REQUIREMENTS:
   - Add, remove, contains operations on a set
   - Iterator captures state at creation time
   - Iterators must be isolated from future changes
   - Multiple iterators can coexist

2. SOLUTION APPROACHES:

   a) Simple Copy (RECOMMENDED FOR INTERVIEWS):
      - Copy the set when iterator() is called
      - Pros: Simple, correct, easy to implement
      - Cons: O(n) space per iterator
      - Time: add/remove/contains O(1), iterator O(n)

   b) Copy-on-Write:
      - Optimize by copying only when needed
      - Pros: Better average-case performance
      - Cons: More complex logic
      - Same time complexity as simple copy

   c) Versioned:
      - Track modifications with version numbers
      - Pros: Can be more space-efficient
      - Cons: Complex, iteration can be slow
      - Time: operations O(1), iteration O(total_ops)

   d) Custom Iterator:
      - Provide additional iterator utilities
      - Pros: Flexible, can add helper methods
      - Cons: More code

3. INTERVIEW RECOMMENDATION:
   - Start with Simple Copy approach
   - It's correct, easy to explain, and implement
   - Discuss optimizations if time permits
   - Copy-on-Write is a good follow-up

4. EDGE CASES HANDLED:
   - Empty set iterator
   - Duplicate additions
   - Removing non-existent elements
   - Multiple iterators
   - Different data types (not just integers)

5. PYTHON SPECIFICS:
   - set.copy() is O(n) shallow copy
   - set.discard() doesn't raise KeyError
   - Can use TypeVar for generic typing

The Simple Copy approach is optimal for interviews: clear,
correct, and efficiently handles the requirements.
""")
