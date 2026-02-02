'''
https://prachub.com/interview-questions/implement-feedback-for-word-guessing-game
You are implementing the core logic for a simple word-guessing game.

There is:

A dictionary of valid words: a list of distinct lowercase strings, all of the same length L .
A secret word: one of the words from the dictionary.
A player's guess word.
For each guess you must return feedback consisting of:

exact_matches : the number of positions i where secret[i] == guess[i] .
misplaced_matches : the number of letters that appear in both secret and guess but in different positions , without double-counting any letter.
If the guessed word is not in the dictionary, you should indicate it is invalid (for example, by returning a special value or throwing an error).
More formally:

Let secret and guess be strings of length L .
A character at index i contributes to exact_matches if secret[i] == guess[i] .
After counting exact matches, remaining characters can contribute to misplaced_matches :
For each distinct character c , count how many times c appears in the non-exact positions of secret and in the non-exact positions of guess .
Add to misplaced_matches the minimum of those two counts.
Requirements
Implement a function with the following behavior:

get_feedback(dictionary: List[str], secret: str, guess: str) -> (int exact_matches, int misplaced_matches)
If guess is not in dictionary , you may assume the function should signal an invalid guess in a clear way (e.g., by raising an exception or returning (-1, -1) ).
Otherwise, return the pair (exact_matches, misplaced_matches) as defined above.
You can assume:

1 <= len(dictionary) <= 10^5
All words in dictionary , and secret and guess , have the same length 1 <= L <= 20 .
All words consist only of lowercase English letters 'a' – 'z' .
Example
dictionary = ["apple", "angle", "ample"]
secret = "apple"
guess = "alley" (this is in the dictionary or you may assume it is added for the example)
Then:

Positions: a p p l e (secret)
      `a l l e y` (guess)
exact_matches = 1 (only the first 'a' matches in the same position)
Remaining letters:
Secret has p, p, l, e
Guess has l, l, e, y
Common letters in different positions: 'l' (1 time), 'e' (1 time)
So misplaced_matches = 2 .
Design and implement an efficient algorithm to compute this feedback for a single guess.
'''

from typing import List, Tuple
from collections import Counter


# ============================================================================
# SOLUTION 1: Clean and Efficient (RECOMMENDED)
# ============================================================================

def get_feedback(dictionary: List[str], secret: str, guess: str) -> Tuple[int, int]:
    """
    Calculate feedback for a word guess (Wordle-style).

    Algorithm:
    1. Validate guess is in dictionary
    2. Count exact matches (same position)
    3. Count character frequencies in non-exact positions
    4. Calculate misplaced matches as sum of min frequencies

    Args:
        dictionary: List of valid words
        secret: The secret word to guess
        guess: The player's guess

    Returns:
        Tuple of (exact_matches, misplaced_matches)
        Returns (-1, -1) if guess is not in dictionary

    Time Complexity: O(L) where L is word length
    Space Complexity: O(1) (at most 26 characters)
    """
    # Validate guess is in dictionary
    if guess not in dictionary:
        return (-1, -1)

    # Count exact matches
    exact_matches = 0
    secret_remaining = []  # Non-exact positions in secret
    guess_remaining = []   # Non-exact positions in guess

    for i in range(len(secret)):
        if secret[i] == guess[i]:
            exact_matches += 1
        else:
            secret_remaining.append(secret[i])
            guess_remaining.append(guess[i])

    # Count misplaced matches
    secret_freq = Counter(secret_remaining)
    guess_freq = Counter(guess_remaining)

    misplaced_matches = 0
    for char in guess_freq:
        if char in secret_freq:
            misplaced_matches += min(secret_freq[char], guess_freq[char])

    return (exact_matches, misplaced_matches)


# ============================================================================
# SOLUTION 2: Optimized with Set for Dictionary
# ============================================================================

class WordGuessingGame:
    """
    Optimized implementation with set-based dictionary lookup.

    Preprocesses dictionary as a set for O(1) lookup.
    """

    def __init__(self, dictionary: List[str]):
        """
        Initialize with dictionary.

        Args:
            dictionary: List of valid words
        """
        self.dictionary_set = set(dictionary)

    def get_feedback(self, secret: str, guess: str) -> Tuple[int, int]:
        """
        Get feedback for a guess.

        Time: O(L) where L is word length
        Space: O(1)
        """
        # Validate guess
        if guess not in self.dictionary_set:
            return (-1, -1)

        exact_matches = 0
        secret_remaining = []
        guess_remaining = []

        # Count exact matches
        for i in range(len(secret)):
            if secret[i] == guess[i]:
                exact_matches += 1
            else:
                secret_remaining.append(secret[i])
                guess_remaining.append(guess[i])

        # Count misplaced matches
        secret_freq = Counter(secret_remaining)
        guess_freq = Counter(guess_remaining)

        misplaced_matches = sum(
            min(secret_freq[char], guess_freq[char])
            for char in guess_freq
            if char in secret_freq
        )

        return (exact_matches, misplaced_matches)


# ============================================================================
# SOLUTION 3: With Exception Handling
# ============================================================================

class InvalidGuessError(Exception):
    """Raised when guess is not in dictionary."""
    pass


def get_feedback_with_exception(dictionary: List[str], secret: str, guess: str) -> Tuple[int, int]:
    """
    Version that raises exception for invalid guesses.

    This is often cleaner than returning sentinel values.
    """
    if guess not in dictionary:
        raise InvalidGuessError(f"'{guess}' is not in the dictionary")

    exact_matches = 0
    secret_remaining = []
    guess_remaining = []

    for i in range(len(secret)):
        if secret[i] == guess[i]:
            exact_matches += 1
        else:
            secret_remaining.append(secret[i])
            guess_remaining.append(guess[i])

    secret_freq = Counter(secret_remaining)
    guess_freq = Counter(guess_remaining)

    misplaced_matches = sum(
        min(secret_freq[char], guess_freq[char])
        for char in guess_freq
        if char in secret_freq
    )

    return (exact_matches, misplaced_matches)


# ============================================================================
# SOLUTION 4: Manual Counting (No Counter)
# ============================================================================

def get_feedback_manual(dictionary: List[str], secret: str, guess: str) -> Tuple[int, int]:
    """
    Alternative implementation without using Counter.

    Demonstrates the algorithm more explicitly.
    """
    if guess not in dictionary:
        return (-1, -1)

    exact_matches = 0
    secret_freq = {}
    guess_freq = {}

    # First pass: count exact matches and build frequency maps
    for i in range(len(secret)):
        if secret[i] == guess[i]:
            exact_matches += 1
        else:
            # Add to frequency maps
            secret_freq[secret[i]] = secret_freq.get(secret[i], 0) + 1
            guess_freq[guess[i]] = guess_freq.get(guess[i], 0) + 1

    # Second pass: count misplaced matches
    misplaced_matches = 0
    for char in guess_freq:
        if char in secret_freq:
            misplaced_matches += min(secret_freq[char], guess_freq[char])

    return (exact_matches, misplaced_matches)


# ============================================================================
# TEST CASES
# ============================================================================

def test_basic_example():
    """Test the example from the problem."""
    print("="*70)
    print("TEST 1: Basic Example from Problem")
    print("="*70)

    dictionary = ["apple", "angle", "ample", "alley"]
    secret = "apple"
    guess = "alley"

    exact, misplaced = get_feedback(dictionary, secret, guess)

    print(f"\nDictionary: {dictionary}")
    print(f"Secret: {secret}")
    print(f"Guess:  {guess}")
    print(f"\nPositions:")
    print(f"  Secret: {' '.join(secret)}")
    print(f"  Guess:  {' '.join(guess)}")
    print(f"\nResult:")
    print(f"  Exact matches: {exact} (expected: 1)")
    print(f"  Misplaced matches: {misplaced} (expected: 2)")
    print(f"\nCorrect: {exact == 1 and misplaced == 2}")


def test_various_cases():
    """Test various cases."""
    print("\n" + "="*70)
    print("TEST 2: Various Cases")
    print("="*70)

    dictionary = ["apple", "ample", "maple", "table", "alley"]

    test_cases = [
        ("apple", "apple", 5, 0, "Perfect match"),
        ("apple", "ample", 3, 1, "Some exact, some misplaced"),
        ("apple", "table", 0, 3, "No exact, some misplaced"),
        ("apple", "alley", 1, 2, "Example from problem"),
        ("apple", "xxxxx", 0, 0, "No matches (invalid but testing)"),
    ]

    for secret, guess, expected_exact, expected_misplaced, description in test_cases:
        # Add guess to dictionary if needed
        if guess not in dictionary:
            test_dict = dictionary + [guess]
        else:
            test_dict = dictionary

        exact, misplaced = get_feedback(test_dict, secret, guess)
        status = "✓" if (exact, misplaced) == (expected_exact, expected_misplaced) else "✗"

        print(f"\n{status} {description}:")
        print(f"  Secret: {secret}, Guess: {guess}")
        print(f"  Got: ({exact}, {misplaced}), Expected: ({expected_exact}, {expected_misplaced})")


def test_repeated_letters():
    """Test handling of repeated letters."""
    print("\n" + "="*70)
    print("TEST 3: Repeated Letters (Critical Test)")
    print("="*70)

    dictionary = ["aabbc", "bccaa", "aaaaa", "abcde"]

    test_cases = [
        ("aabbc", "aabbc", 5, 0, "Perfect match with repeats"),
        ("aabbc", "bccaa", 1, 4, "All letters present, mostly wrong positions"),
        ("aabbc", "aaaaa", 2, 0, "Multiple a's but only 2 match"),
        ("aabbc", "abcde", 1, 2, "Some repeats, some unique"),
    ]

    for secret, guess, expected_exact, expected_misplaced, description in test_cases:
        exact, misplaced = get_feedback(dictionary, secret, guess)
        status = "✓" if (exact, misplaced) == (expected_exact, expected_misplaced) else "✗"

        print(f"\n{status} {description}:")
        print(f"  Secret: {secret}, Guess: {guess}")
        print(f"  Result: ({exact}, {misplaced})")


def test_invalid_guess():
    """Test invalid guess handling."""
    print("\n" + "="*70)
    print("TEST 4: Invalid Guess")
    print("="*70)

    dictionary = ["apple", "ample", "maple"]
    secret = "apple"
    guess = "invalid"

    exact, misplaced = get_feedback(dictionary, secret, guess)

    print(f"\nGuess '{guess}' not in dictionary")
    print(f"Result: ({exact}, {misplaced})")
    print(f"Expected: (-1, -1)")
    print(f"Correct: {(exact, misplaced) == (-1, -1)}")


def test_all_implementations():
    """Test all implementations."""
    print("\n" + "="*70)
    print("TEST 5: Compare All Implementations")
    print("="*70)

    dictionary = ["apple", "alley", "ample"]
    secret = "apple"
    guess = "alley"

    # Test basic function
    result1 = get_feedback(dictionary, secret, guess)

    # Test class
    game = WordGuessingGame(dictionary)
    result2 = game.get_feedback(secret, guess)

    # Test manual counting
    result3 = get_feedback_manual(dictionary, secret, guess)

    # Test with exception
    try:
        result4 = get_feedback_with_exception(dictionary, secret, guess)
    except InvalidGuessError:
        result4 = (-1, -1)

    print(f"\nSecret: {secret}, Guess: {guess}")
    print(f"Basic function: {result1}")
    print(f"Class-based: {result2}")
    print(f"Manual counting: {result3}")
    print(f"With exception: {result4}")
    print(f"\nAll match: {result1 == result2 == result3 == result4}")


def demonstrate_algorithm():
    """Demonstrate the algorithm step by step."""
    print("\n" + "="*70)
    print("ALGORITHM DEMONSTRATION")
    print("="*70)

    secret = "apple"
    guess = "alley"

    print(f"\nSecret: {secret}")
    print(f"Guess:  {guess}")

    print("\nStep 1: Count exact matches")
    print("-" * 40)
    exact_matches = 0
    secret_remaining = []
    guess_remaining = []

    for i in range(len(secret)):
        if secret[i] == guess[i]:
            print(f"  Position {i}: '{secret[i]}' == '{guess[i]}' ✓ (exact match)")
            exact_matches += 1
        else:
            print(f"  Position {i}: '{secret[i]}' != '{guess[i]}'")
            secret_remaining.append(secret[i])
            guess_remaining.append(guess[i])

    print(f"\nExact matches: {exact_matches}")
    print(f"Secret remaining: {secret_remaining}")
    print(f"Guess remaining:  {guess_remaining}")

    print("\nStep 2: Count character frequencies in remaining positions")
    print("-" * 40)
    secret_freq = Counter(secret_remaining)
    guess_freq = Counter(guess_remaining)

    print(f"Secret frequencies: {dict(secret_freq)}")
    print(f"Guess frequencies:  {dict(guess_freq)}")

    print("\nStep 3: Calculate misplaced matches")
    print("-" * 40)
    misplaced_matches = 0
    for char in guess_freq:
        if char in secret_freq:
            count = min(secret_freq[char], guess_freq[char])
            print(f"  '{char}': min({secret_freq[char]}, {guess_freq[char]}) = {count}")
            misplaced_matches += count
        else:
            print(f"  '{char}': not in secret")

    print(f"\nMisplaced matches: {misplaced_matches}")
    print(f"\nFinal result: ({exact_matches}, {misplaced_matches})")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║         WORD GUESSING GAME - FEEDBACK IMPLEMENTATION                 ║
║                                                                      ║
║  Calculate exact and misplaced matches (like Wordle)                ║
╚══════════════════════════════════════════════════════════════════════╝
""")

    # Run algorithm demonstration
    demonstrate_algorithm()

    # Run all tests
    test_basic_example()
    test_various_cases()
    test_repeated_letters()
    test_invalid_guess()
    test_all_implementations()

    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print("""
Key Implementation Points:

1. ALGORITHM (Two-Pass Approach):
   Pass 1: Count exact matches
   - Compare secret[i] with guess[i]
   - Collect non-matching characters

   Pass 2: Count misplaced matches
   - Build frequency maps of remaining characters
   - For each character, take min(secret_freq, guess_freq)
   - Sum all minimums

2. TIME COMPLEXITY:
   - O(L) where L = word length
   - Two passes through the word
   - Frequency counting is O(L)

3. SPACE COMPLEXITY:
   - O(k) where k = distinct letters (at most 26)
   - Frequency maps

4. REPEATED LETTERS (Critical):
   - Must handle like Wordle
   - Example: secret="aabbc", guess="aaaaa"
     * Exact matches: positions 0, 1 -> count = 2
     * Remaining: secret has [b,b,c], guess has [a,a,a]
     * No common letters in remaining
     * Result: (2, 0) ✓

5. INVALID GUESS HANDLING:
   - Return (-1, -1) as sentinel value, OR
   - Raise InvalidGuessError exception
   - Choose based on language conventions

6. EDGE CASES:
   - Perfect match (all exact)
   - No matches at all
   - All misplaced (no exact)
   - Repeated letters
   - Single character words

The recommended solution uses Counter for clean, efficient
frequency counting and handles all edge cases correctly.
""")

    print("\n" + "="*70)
    print("EXAMPLE WALKTHROUGH")
    print("="*70)
    print("""
Problem: secret = "apple", guess = "alley"

Positions:  0 1 2 3 4
Secret:     a p p l e
Guess:      a l l e y

Step 1: Exact matches
  Position 0: 'a' == 'a' ✓ -> exact_match = 1

Step 2: Remaining characters
  Secret: [p, p, l, e]  -> freq: {p:2, l:1, e:1}
  Guess:  [l, l, e, y]  -> freq: {l:2, e:1, y:1}

Step 3: Misplaced matches
  'l': min(1, 2) = 1
  'e': min(1, 1) = 1
  'y': not in secret
  Total misplaced = 1 + 1 = 2

Result: (1, 2) ✓
""")
