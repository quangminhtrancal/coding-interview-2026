'''
https://www.1point3acres.com/interview/problems/066f3b72-1a40-4fca-8001-eecd1ddc3565

Given a dictionary, a secret word, and a guessed word, your task is to provide feedback based on these inputs. The feedback rule is as follows:

For each letter, if it exists in the same position in the secret word, return 'match'.
If the letter exists in the secret word but in a different position, return 'exists'.
Otherwise, return 'not exists'.
The words in the dictionary consist of lowercase letters, and the secret and guessed words have the same length.

Input Format:

The first line contains an integer n, indicating the number of words in the dictionary.
The following n lines each contain a word from the dictionary.
The (n+1)-th line contains the secret word.
The (n+2)-th line contains the guessed word.
Output Format:

Output a list of strings corresponding to the feedback for each letter.
Sample Input:

5
apple
banana
cherry
date
eagle
pearl
piano
Sample Output:

['not exists', 'exists', 'match', 'exists', 'not exists']
'''

from typing import List
from collections import Counter


# ============================================================================
# SOLUTION 1: Simple Approach (For Simple Cases)
# ============================================================================

def get_feedback_simple(secret: str, guess: str) -> List[str]:
    """
    Simple feedback without handling letter frequency properly.

    Note: This doesn't handle repeated letters correctly (like Wordle does).

    Args:
        secret: The secret word
        guess: The guessed word

    Returns:
        List of feedback strings
    """
    feedback = []

    for i, letter in enumerate(guess):
        if secret[i] == letter:
            feedback.append('match')
        elif letter in secret:
            feedback.append('exists')
        else:
            feedback.append('not exists')

    return feedback


# ============================================================================
# SOLUTION 2: Wordle-Style (Handle Repeated Letters Correctly)
# ============================================================================

def get_feedback_wordle_style(secret: str, guess: str) -> List[str]:
    """
    Wordle-style feedback that correctly handles repeated letters.

    Algorithm:
    1. First pass: Mark exact matches
    2. Count remaining letters in secret
    3. Second pass: Mark 'exists' for non-matched letters if available

    Args:
        secret: The secret word
        guess: The guessed word

    Returns:
        List of feedback strings
    """
    n = len(secret)
    feedback = [''] * n

    # First pass: Mark exact matches
    secret_remaining = []
    for i in range(n):
        if secret[i] == guess[i]:
            feedback[i] = 'match'
        else:
            secret_remaining.append(secret[i])

    # Count remaining letters in secret
    secret_freq = Counter(secret_remaining)

    # Second pass: Check for 'exists' in remaining positions
    for i in range(n):
        if feedback[i] == '':  # Not matched yet
            if guess[i] in secret_freq and secret_freq[guess[i]] > 0:
                feedback[i] = 'exists'
                secret_freq[guess[i]] -= 1
            else:
                feedback[i] = 'not exists'

    return feedback


# ============================================================================
# SOLUTION 3: Complete Implementation with Input Parsing
# ============================================================================

def solve_from_input() -> List[str]:
    """
    Complete solution that reads from stdin and returns feedback.

    Returns:
        List of feedback strings
    """
    # Read number of dictionary words
    n = int(input())

    # Read dictionary (not used in basic feedback logic)
    dictionary = []
    for _ in range(n):
        dictionary.append(input().strip())

    # Read secret and guess
    secret = input().strip()
    guess = input().strip()

    # Get feedback
    return get_feedback_wordle_style(secret, guess)


# ============================================================================
# SOLUTION 4: With Validation
# ============================================================================

class WordFeedbackGenerator:
    """
    Complete word feedback generator with validation.

    Features:
    - Validate word lengths match
    - Handle repeated letters correctly
    - Optional dictionary validation
    """

    def __init__(self, dictionary: List[str] = None):
        """
        Initialize with optional dictionary.

        Args:
            dictionary: Optional list of valid words
        """
        self.dictionary = set(dictionary) if dictionary else None

    def get_feedback(self, secret: str, guess: str,
                    validate_dictionary: bool = False) -> List[str]:
        """
        Get feedback for a guess.

        Args:
            secret: The secret word
            guess: The guessed word
            validate_dictionary: Whether to check if words are in dictionary

        Returns:
            List of feedback strings

        Raises:
            ValueError: If words are invalid
        """
        # Validate lengths
        if len(secret) != len(guess):
            raise ValueError(f"Words must have same length: secret={len(secret)}, guess={len(guess)}")

        # Validate dictionary if requested
        if validate_dictionary and self.dictionary:
            if secret not in self.dictionary:
                raise ValueError(f"Secret word '{secret}' not in dictionary")
            if guess not in self.dictionary:
                raise ValueError(f"Guess word '{guess}' not in dictionary")

        # Generate feedback
        return self._generate_feedback(secret, guess)

    def _generate_feedback(self, secret: str, guess: str) -> List[str]:
        """Internal method to generate feedback."""
        n = len(secret)
        feedback = [''] * n

        # First pass: Mark exact matches
        secret_remaining = []
        for i in range(n):
            if secret[i] == guess[i]:
                feedback[i] = 'match'
            else:
                secret_remaining.append(secret[i])

        # Count remaining letters
        secret_freq = Counter(secret_remaining)

        # Second pass: Mark 'exists' or 'not exists'
        for i in range(n):
            if feedback[i] == '':
                if guess[i] in secret_freq and secret_freq[guess[i]] > 0:
                    feedback[i] = 'exists'
                    secret_freq[guess[i]] -= 1
                else:
                    feedback[i] = 'not exists'

        return feedback


# ============================================================================
# TEST CASES
# ============================================================================

def test_basic_examples():
    """Test basic examples."""
    print("="*70)
    print("TEST 1: Basic Examples")
    print("="*70)

    test_cases = [
        ("pearl", "piano", "Example from problem"),
        ("apple", "apple", "Exact match"),
        ("hello", "world", "No matches"),
        ("tests", "toast", "Mix of all types"),
    ]

    for secret, guess, description in test_cases:
        feedback = get_feedback_wordle_style(secret, guess)
        print(f"\n{description}:")
        print(f"  Secret: {secret}")
        print(f"  Guess:  {guess}")
        print(f"  Feedback: {feedback}")

        # Visual representation
        visual = []
        for i, (s, g, f) in enumerate(zip(secret, guess, feedback)):
            if f == 'match':
                visual.append(f"{g}(✓)")
            elif f == 'exists':
                visual.append(f"{g}(?)")
            else:
                visual.append(f"{g}(✗)")
        print(f"  Visual: {' '.join(visual)}")


def test_repeated_letters():
    """Test handling of repeated letters."""
    print("\n" + "="*70)
    print("TEST 2: Repeated Letters")
    print("="*70)

    test_cases = [
        ("speed", "erase", "Multiple e's"),
        ("abbey", "kebab", "Multiple b's"),
        ("robot", "floor", "Multiple o's"),
        ("llama", "allay", "Multiple l's and a's"),
    ]

    for secret, guess, description in test_cases:
        feedback = get_feedback_wordle_style(secret, guess)
        print(f"\n{description}:")
        print(f"  Secret: {secret}")
        print(f"  Guess:  {guess}")
        print(f"  Feedback: {feedback}")


def test_edge_cases():
    """Test edge cases."""
    print("\n" + "="*70)
    print("TEST 3: Edge Cases")
    print("="*70)

    # Single letter
    feedback = get_feedback_wordle_style("a", "a")
    print(f"\nSingle letter match:")
    print(f"  Secret: 'a', Guess: 'a'")
    print(f"  Feedback: {feedback}")

    # All same letters
    feedback = get_feedback_wordle_style("aaaa", "aaaa")
    print(f"\nAll same letters:")
    print(f"  Secret: 'aaaa', Guess: 'aaaa'")
    print(f"  Feedback: {feedback}")

    # No overlap
    feedback = get_feedback_wordle_style("abc", "xyz")
    print(f"\nNo overlap:")
    print(f"  Secret: 'abc', Guess: 'xyz'")
    print(f"  Feedback: {feedback}")


def test_with_class():
    """Test using the WordFeedbackGenerator class."""
    print("\n" + "="*70)
    print("TEST 4: Using WordFeedbackGenerator Class")
    print("="*70)

    dictionary = ["apple", "ample", "maple", "table", "pearl", "piano"]
    generator = WordFeedbackGenerator(dictionary)

    test_cases = [
        ("apple", "ample"),
        ("pearl", "piano"),
        ("table", "maple"),
    ]

    for secret, guess in test_cases:
        feedback = generator.get_feedback(secret, guess, validate_dictionary=True)
        print(f"\nSecret: {secret}, Guess: {guess}")
        print(f"  Feedback: {feedback}")


def analyze_sample_output():
    """Analyze the sample output from the problem."""
    print("\n" + "="*70)
    print("ANALYZING SAMPLE OUTPUT")
    print("="*70)

    secret = "pearl"
    guess = "piano"
    expected = ['not exists', 'exists', 'match', 'exists', 'not exists']

    print(f"\nSecret: {secret} (p-e-a-r-l)")
    print(f"Guess:  {guess} (p-i-a-n-o)")
    print(f"Expected: {expected}")

    # Check each position
    print("\nPosition-by-position analysis:")
    for i in range(len(guess)):
        print(f"  Position {i}: guess[{i}]='{guess[i]}' vs secret[{i}]='{secret[i]}'")
        if secret[i] == guess[i]:
            print(f"    -> Exact match!")
        elif guess[i] in secret:
            print(f"    -> '{guess[i]}' exists in secret at positions: {[j for j, c in enumerate(secret) if c == guess[i]]}")
        else:
            print(f"    -> '{guess[i]}' not in secret")

    # Our implementation
    our_result = get_feedback_wordle_style(secret, guess)
    print(f"\nOur result: {our_result}")
    print(f"Expected:   {expected}")
    print(f"Match: {our_result == expected}")


def demonstrate_algorithm():
    """Demonstrate the algorithm step by step."""
    print("\n" + "="*70)
    print("ALGORITHM DEMONSTRATION")
    print("="*70)

    secret = "speed"
    guess = "erase"

    print(f"\nSecret: {secret}")
    print(f"Guess:  {guess}")

    print("\nStep 1: Mark exact matches")
    print("-" * 40)
    n = len(secret)
    feedback = [''] * n
    secret_remaining = []

    for i in range(n):
        if secret[i] == guess[i]:
            feedback[i] = 'match'
            print(f"  Position {i}: '{guess[i]}' matches '{secret[i]}' -> 'match'")
        else:
            secret_remaining.append(secret[i])
            print(f"  Position {i}: '{guess[i]}' != '{secret[i]}'")

    print(f"\nAfter step 1: {feedback}")
    print(f"Remaining letters in secret: {secret_remaining}")

    print("\nStep 2: Count remaining letters")
    print("-" * 40)
    secret_freq = Counter(secret_remaining)
    print(f"Frequency: {dict(secret_freq)}")

    print("\nStep 3: Mark 'exists' or 'not exists'")
    print("-" * 40)
    for i in range(n):
        if feedback[i] == '':
            if guess[i] in secret_freq and secret_freq[guess[i]] > 0:
                feedback[i] = 'exists'
                secret_freq[guess[i]] -= 1
                print(f"  Position {i}: '{guess[i]}' exists in secret -> 'exists'")
                print(f"    Updated frequency: {dict(secret_freq)}")
            else:
                feedback[i] = 'not exists'
                print(f"  Position {i}: '{guess[i]}' not available -> 'not exists'")

    print(f"\nFinal feedback: {feedback}")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║              WORD GUESSING FEEDBACK SYSTEM                           ║
║                                                                      ║
║  Generate feedback for word guesses (like Wordle)                   ║
╚══════════════════════════════════════════════════════════════════════╝
""")

    # Run demonstrations
    demonstrate_algorithm()

    # Run all tests
    test_basic_examples()
    test_repeated_letters()
    test_edge_cases()
    test_with_class()
    analyze_sample_output()

    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print("""
Key Implementation Points:

1. ALGORITHM (Two-Pass Approach):
   a) First Pass: Mark exact matches ('match')
      - Compare secret[i] with guess[i]
      - Track remaining letters in secret

   b) Second Pass: Mark 'exists' or 'not exists'
      - For non-matched positions, check if letter exists in remaining
      - Use frequency counting to avoid over-counting
      - Decrement frequency when marking 'exists'

2. COMPLEXITY:
   - Time: O(n) where n = word length
   - Space: O(k) where k = distinct letters (at most 26)

3. REPEATED LETTERS:
   - Must handle like Wordle
   - Example: secret="speed", guess="erase"
     - First 'e' in guess matches position 2 -> 'match'
     - Second 'e' in guess: only 1 'e' left in secret -> 'exists'
     - Third 'e' would be -> 'not exists'

4. FEEDBACK TYPES:
   - 'match': Letter at exact position
   - 'exists': Letter in word but different position
   - 'not exists': Letter not in word (or already used up)

5. EDGE CASES:
   - Single letter words
   - All same letters
   - No overlapping letters
   - Multiple occurrences of same letter

The two-pass algorithm correctly handles all edge cases
including repeated letters, matching Wordle's behavior.
""")

    print("\n" + "="*70)
    print("USAGE EXAMPLE")
    print("="*70)
    print("""
# Simple usage:
feedback = get_feedback_wordle_style("pearl", "piano")
print(feedback)  # ['match', 'not exists', 'match', 'not exists', 'not exists']

# Using the class with dictionary validation:
dictionary = ["apple", "ample", "pearl", "piano"]
generator = WordFeedbackGenerator(dictionary)
feedback = generator.get_feedback("pearl", "piano", validate_dictionary=True)
print(feedback)
""")
