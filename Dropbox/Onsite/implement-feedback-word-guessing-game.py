'''
"content_enhanced": "You are implementing the core logic for a simple word-guessing game.\n\nThere is:\n- A **dictionary** of valid words: a list of distinct lowercase strings, all of the same length `L`.\n- A **secret** word: one of the words from the dictionary.\n- A player's **guess** word.\n\nFor each guess you must return **feedback** consisting of:\n\n- `exact_matches`: the number of positions `i` where `secret[i] == guess[i]`.\n- `misplaced_matches`: the number of letters that appear in both `secret` and `guess` but **in different positions**, without double-counting any letter.\n- If the guessed word is **not** in the dictionary, you should indicate it is invalid (for example, by returning a special value or throwing an error).\n\nMore formally:\n- Let `secret` and `guess` be strings of length `L`.\n- A character at index `i` contributes to `exact_matches` if `secret[i] == guess[i]`.\n- After counting exact matches, remaining characters can contribute to `misplaced_matches`:\n  - For each distinct character `c`, count how many times `c` appears in the non-exact positions of `secret` and in the non-exact positions of `guess`.\n  - Add to `misplaced_matches` the minimum of those two counts.\n\n### Requirements\n\nImplement a function with the following behavior:\n\n```text\nget_feedback(dictionary: List[str], secret: str, guess: str) -> (int exact_matches, int misplaced_matches)
```\n\n- If `guess` is not in `dictionary`, you may assume the function should signal an invalid guess in a clear way (e.g., by raising an exception or returning `(-1, -1)`).\n- Otherwise, return the pair `(exact_matches, misplaced_matches)` as defined above.\n\nYou can assume:\n- `1 <= len(dictionary) <= 10^5`\n- All words in `dictionary`, and `secret` and `guess`, have the same length `1 <= L <= 20`.\n- All words consist only of lowercase English letters `'a'`–`'z'`.\n\n### Example\n\n- `dictionary = [\"apple\", \"angle\", \"ample\"]`\n- `secret = \"apple\"`\n- `guess = \"alley\"` (this is in the dictionary or you may assume it is added for the example)\n\nThen:\n- Positions: `a p p l e` (secret)\n-           `a l l e y` (guess)\n- `exact_matches = 1` (only the first `'a'` matches in the same position)\n- Remaining letters:\n  - Secret has `p, p, l, e`\n  - Guess has `l, l, e, y`\n  - Common letters in different positions: `'l'` (1 time), `'e'` (1 time)\n- So `misplaced_matches = 2`.\n\nDesign and implement an efficient algorithm to compute this feedback for a single guess.",
https://prachub.com/interview-questions/implement-feedback-for-word-guessing-game

You are implementing the core logic for a simple word-guessing game.

There is:

A dictionary of valid words: a list of distinct lowercase strings, all of the same length L .
A secret word: one of the words from the dictionary.
A player's guess word.
For each guess you must return feedback consisting of:

exact_matches : the number of positions i where secret[i] == guess[i] .
misplaced_matches : the number of letters that appear in both secret and guess but in different positions ,
without double-counting any letter.
If the guessed word is not in the dictionary, you should indicate it is invalid (for example,
by returning a special value or throwing an error).

More formally:
Let secret and guess be strings of length L .
A character at index i contributes to exact_matches if secret[i] == guess[i] .
After counting exact matches, remaining characters can contribute to misplaced_matches :
For each distinct character c , count how many times c appears in the non-exact positions of secret
and in the non-exact positions of guess .

Add to misplaced_matches the minimum of those two counts.

Requirements
Implement a function with the following behavior:

get_feedback(dictionary: List[str], secret: str, guess: str) -> (int exact_matches, int misplaced_matches)
If guess is not in dictionary , you may assume the function should signal an invalid guess in a clear way
(e.g., by raising an exception or returning (-1, -1) ).
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

from typing import List, Tuple, Dict
from collections import Counter


# ============================================================================
# SOLUTION 1: Clean and Efficient Implementation (RECOMMENDED)
# ============================================================================

def get_feedback(dictionary: List[str], secret: str, guess: str) -> Tuple[int, int]:
    """
    Calculate feedback for a word guess in a word-guessing game (like Wordle).

    Args:
        dictionary: List of valid words
        secret: The secret word to guess
        guess: The player's guess

    Returns:
        Tuple of (exact_matches, misplaced_matches)
        Returns (-1, -1) if guess is not in dictionary

    Time Complexity: O(L) where L is the word length
    Space Complexity: O(1) (at most 26 characters)

    Algorithm:
    1. Validate guess is in dictionary
    2. Count exact matches (same position)
    3. Count character frequencies in non-exact positions
    4. Calculate misplaced matches as sum of min frequencies
    """
    # Validate guess is in dictionary
    # For efficiency with large dictionaries, convert to set
    if guess not in dictionary:
        return (-1, -1)

    # Step 1: Count exact matches
    exact_matches = 0
    secret_remaining = []  # Characters in secret at non-exact positions
    guess_remaining = []   # Characters in guess at non-exact positions

    for i in range(len(secret)):
        if secret[i] == guess[i]:
            exact_matches += 1
        else:
            secret_remaining.append(secret[i])
            guess_remaining.append(guess[i])

    # Step 2: Count misplaced matches
    # Count frequency of each character in remaining positions
    secret_freq = Counter(secret_remaining)
    guess_freq = Counter(guess_remaining)

    # For each character, take minimum of frequencies
    misplaced_matches = 0
    for char in guess_freq:
        if char in secret_freq:
            misplaced_matches += min(secret_freq[char], guess_freq[char])

    return (exact_matches, misplaced_matches)


# ============================================================================
# SOLUTION 2: Optimized with Set-based Dictionary Lookup
# ============================================================================

class WordGuessingGame:
    """
    Optimized implementation for multiple guess operations.

    Precomputes dictionary as a set for O(1) lookup.
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

        # Count exact matches and collect remaining characters
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
# SOLUTION 3: Alternative Implementation with Manual Counting
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
# SOLUTION 4: With Exception Handling
# ============================================================================

class InvalidGuessError(Exception):
    """Raised when guess is not in dictionary."""
    pass


def get_feedback_with_exception(dictionary: List[str], secret: str, guess: str) -> Tuple[int, int]:
    """
    Version that raises an exception for invalid guesses.

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
# COMPLETE GAME IMPLEMENTATION
# ============================================================================

class WordleGame:
    """
    Complete Wordle-style game implementation.

    Features:
    - Track game state
    - Multiple guess support
    - Win condition detection
    - Guess history
    """

    def __init__(self, dictionary: List[str], secret: str, max_guesses: int = 6):
        """
        Initialize a new game.

        Args:
            dictionary: List of valid words
            secret: The secret word
            max_guesses: Maximum number of guesses allowed
        """
        self.dictionary_set = set(dictionary)
        self.secret = secret
        self.max_guesses = max_guesses
        self.guesses = []
        self.game_over = False
        self.won = False

    def make_guess(self, guess: str) -> Dict:
        """
        Make a guess and get feedback.

        Returns:
            Dictionary with game state
        """
        if self.game_over:
            return {
                'valid': False,
                'message': 'Game is already over',
                'exact': None,
                'misplaced': None
            }

        # Validate guess
        if guess not in self.dictionary_set:
            return {
                'valid': False,
                'message': f"'{guess}' is not in dictionary",
                'exact': None,
                'misplaced': None
            }

        # Get feedback
        exact, misplaced = get_feedback(list(self.dictionary_set), self.secret, guess)

        # Record guess
        self.guesses.append({
            'word': guess,
            'exact': exact,
            'misplaced': misplaced
        })

        # Check win condition
        if exact == len(self.secret):
            self.game_over = True
            self.won = True

        # Check loss condition
        if len(self.guesses) >= self.max_guesses and not self.won:
            self.game_over = True

        return {
            'valid': True,
            'message': 'Valid guess',
            'exact': exact,
            'misplaced': misplaced,
            'won': self.won,
            'game_over': self.game_over,
            'guesses_remaining': self.max_guesses - len(self.guesses)
        }

    def get_game_state(self) -> Dict:
        """Get current game state."""
        return {
            'guesses': self.guesses,
            'won': self.won,
            'game_over': self.game_over,
            'guesses_remaining': self.max_guesses - len(self.guesses),
            'secret_revealed': self.secret if self.game_over else None
        }


# ============================================================================
# TEST CASES
# ============================================================================

def test_basic_functionality():
    """Test basic feedback calculation."""
    print("="*70)
    print("TEST 1: Basic Functionality")
    print("="*70)

    dictionary = ["apple", "angle", "ample", "alley"]
    secret = "apple"

    test_cases = [
        ("apple", 5, 0, "Perfect match"),
        ("alley", 1, 2, "Example from problem"),
        ("ample", 3, 1, "Some exact, some misplaced"),
        ("angle", 2, 2, "Mix of exact and misplaced"),
        ("xxxxx", -1, -1, "Not in dictionary"),
    ]

    for guess, expected_exact, expected_misplaced, description in test_cases:
        exact, misplaced = get_feedback(dictionary, secret, guess)
        status = "✓" if (exact, misplaced) == (expected_exact, expected_misplaced) else "✗"
        print(f"{status} guess='{guess}': ({exact}, {misplaced}) - {description}")
        if (exact, misplaced) != (expected_exact, expected_misplaced):
            print(f"  Expected: ({expected_exact}, {expected_misplaced})")


def test_edge_cases():
    """Test edge cases."""
    print("\n" + "="*70)
    print("TEST 2: Edge Cases")
    print("="*70)

    # Test case 1: Repeated letters
    print("\nEdge Case 1: Repeated letters")
    dictionary = ["aabbc", "bccaa", "aaaaa"]
    secret = "aabbc"

    test_cases = [
        ("aabbc", 5, 0, "Exact match"),
        ("bccaa", 1, 4, "All letters present, mostly wrong positions"),
        ("aaaaa", 2, 0, "Repeated a's, but only 2 match"),
    ]

    for guess, expected_exact, expected_misplaced, description in test_cases:
        exact, misplaced = get_feedback(dictionary, secret, guess)
        status = "✓" if (exact, misplaced) == (expected_exact, expected_misplaced) else "✗"
        print(f"{status} secret='{secret}', guess='{guess}': ({exact}, {misplaced})")
        print(f"   {description}")

    # Test case 2: No matches
    print("\nEdge Case 2: No matches at all")
    dictionary = ["abc", "xyz"]
    secret = "abc"
    guess = "xyz"
    exact, misplaced = get_feedback(dictionary, secret, guess)
    print(f"secret='{secret}', guess='{guess}': ({exact}, {misplaced})")
    print(f"Expected: (0, 0)")

    # Test case 3: Single character words
    print("\nEdge Case 3: Single character")
    dictionary = ["a", "b"]
    secret = "a"
    guess = "a"
    exact, misplaced = get_feedback(dictionary, secret, guess)
    print(f"secret='{secret}', guess='{guess}': ({exact}, {misplaced})")
    print(f"Expected: (1, 0)")


def test_wordle_examples():
    """Test with actual Wordle-style examples."""
    print("\n" + "="*70)
    print("TEST 3: Wordle-Style Examples")
    print("="*70)

    dictionary = ["arose", "route", "outer", "roast", "toast", "sport"]
    secret = "sport"

    print(f"Secret word: {secret}\n")

    guesses = ["arose", "route", "roast", "toast"]

    for guess in guesses:
        exact, misplaced = get_feedback(dictionary, secret, guess)
        print(f"Guess: {guess}")
        print(f"  Exact matches: {exact}")
        print(f"  Misplaced matches: {misplaced}")
        print()


def test_game_implementation():
    """Test the complete game implementation."""
    print("="*70)
    print("TEST 4: Complete Game Implementation")
    print("="*70)

    dictionary = ["apple", "ample", "maple", "table", "cable", "label"]
    secret = "apple"

    game = WordleGame(dictionary, secret, max_guesses=6)

    print(f"Starting game with secret word (hidden)")
    print(f"Max guesses: {game.max_guesses}\n")

    test_guesses = ["cable", "ample", "maple", "apple"]

    for guess in test_guesses:
        result = game.make_guess(guess)
        print(f"Guess: {guess}")
        print(f"  Valid: {result['valid']}")
        print(f"  Exact: {result['exact']}")
        print(f"  Misplaced: {result['misplaced']}")
        print(f"  Game Over: {result['game_over']}")
        print(f"  Won: {result['won']}")
        print()

        if result['game_over']:
            state = game.get_game_state()
            print(f"Game finished!")
            print(f"Secret word: {state['secret_revealed']}")
            print(f"Total guesses: {len(state['guesses'])}")
            break


def demonstrate_algorithm():
    """Detailed demonstration of the algorithm."""
    print("="*70)
    print("ALGORITHM DEMONSTRATION")
    print("="*70)

    secret = "apple"
    guess = "alley"

    print(f"\nSecret: {secret}")
    print(f"Guess:  {guess}\n")

    print("Step 1: Find exact matches")
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
# COMPLEXITY ANALYSIS
# ============================================================================

def complexity_analysis():
    """Analyze time and space complexity."""
    print("\n" + "="*70)
    print("COMPLEXITY ANALYSIS")
    print("="*70)
    print("""
Time Complexity Analysis:
-------------------------
Let L = length of words, D = size of dictionary

1. Dictionary lookup:
   - List: O(D) - need to search entire list
   - Set: O(1) - hash table lookup
   Recommendation: Convert dictionary to set for O(1) lookup

2. Exact match counting:
   - O(L) - single pass through word

3. Frequency counting:
   - O(L) - count characters in remaining positions
   - At most 26 distinct characters

4. Misplaced match calculation:
   - O(1) or O(26) - iterate through at most 26 characters

Overall Time Complexity: O(L) per guess (with set-based dictionary)

Space Complexity Analysis:
--------------------------
1. Remaining character lists: O(L)
2. Frequency counters: O(1) or O(26) - at most 26 letters
3. Dictionary set: O(D) - one-time preprocessing cost

Overall Space Complexity: O(L) per guess, O(D) for preprocessing

Optimization Opportunities:
---------------------------
1. Preprocess dictionary into a set: O(D) one-time cost
2. Reuse frequency counter objects
3. Early termination if all positions matched
4. For multiple guesses against same secret, cache secret frequencies
""")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║         WORD GUESSING GAME - FEEDBACK IMPLEMENTATION                 ║
║                                                                      ║
║  Problem: Calculate exact and misplaced matches for word guesses    ║
║  (Similar to Wordle)                                                 ║
╚══════════════════════════════════════════════════════════════════════╝
""")

    # Run algorithm demonstration
    demonstrate_algorithm()

    # Run all tests
    print("\n" + "="*70)
    print("RUNNING ALL TESTS")
    print("="*70)

    test_basic_functionality()
    test_edge_cases()
    test_wordle_examples()
    test_game_implementation()
    complexity_analysis()

    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print("""
Key Points:

1. ALGORITHM:
   - Count exact matches first (same position)
   - Build frequency maps of remaining characters
   - Sum min(secret_freq, guess_freq) for each character

2. EDGE CASES TO HANDLE:
   - Repeated letters (use frequency counting)
   - Invalid guesses (not in dictionary)
   - Perfect matches (all exact)
   - No matches at all

3. OPTIMIZATION:
   - Preprocess dictionary as set for O(1) lookup
   - Time: O(L) per guess
   - Space: O(L) per guess, O(D) for dictionary

4. IMPLEMENTATION CHOICES:
   - Return (-1, -1) for invalid guesses, OR
   - Raise exception for cleaner error handling

5. PRODUCTION CONSIDERATIONS:
   - Input validation (word length, character set)
   - Game state management for multiple guesses
   - Win/loss condition tracking
   - Guess history and statistics

The recommended solution uses Counter for clean, efficient
frequency counting and set-based dictionary lookup for O(1)
validation.
""")
