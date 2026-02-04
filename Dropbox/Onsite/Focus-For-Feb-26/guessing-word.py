'''
https://prachub.com/companies/dropbox/categories/coding-and-algorithms?sort=hot


Two players play a word guessing game.
- Player A chooses a **secret word**.

Player B repeatedly guesses **single letters**.

- After each guess, the game reports:
  - **hit** if the secret word contains the guessed letter,
     and all occurrences of that letter are revealed in the current pattern
- **miss** otherwise, and the letter is added to a `misses` list

The interviewer will provide an example interaction to confirm behavior.

## Part 1 — Implement the game engine
Design and implement data structures and functions to support:
- Initializing a game with a secret word
- Processing a guessed letter and returning updated state
- Tracking revealed letters (e.g., pattern like `_ _ a _ a`)
- Tracking missed letters (in insertion order)

### Inputs/Outputs (one possible shape)
- Input: `secretWord`, then a sequence of guessed letters
- Output after each guess: `{ result: "hit"|"miss", pattern, misses }`

## Part 2 (Follow-up) — Secret word may change mid-game
Now Player A is allowed to **change the secret word during the game**,
as long as it remains consistent with all previous responses (hits/misses and revealed pattern).

Player B wants to **minimize the number of guesses** needed to fully determine the word.

Discuss an approach and write high-level pseudocode for the strategy Player B should use.

Assumptions you may make (state clearly):
- There is a known dictionary/set of candidate words of the same length.
- Only letter guesses are allowed (no full-word guesses), unless you explicitly add that rule.
- Letters may or may not be repeated in guesses (specify behavior).",

'''

from typing import List, Set, Dict, Tuple
from collections import Counter, defaultdict


# ============================================================================
# PART 1: Basic Game Engine Implementation
# ============================================================================

class WordGuessingGame:
    """
    Implementation of the word guessing game (Hangman-style).

    Features:
    - Track secret word
    - Track revealed pattern (e.g., "_ _ a _ a")
    - Track missed letters in insertion order
    - Process letter guesses and return result
    """

    def __init__(self, secret_word: str):
        """
        Initialize the game with a secret word.

        Args:
            secret_word: The word to guess (should be lowercase)
        """
        self.secret_word = secret_word.lower()
        self.word_length = len(self.secret_word)

        # Track revealed positions (True = revealed, False = hidden)
        self.revealed = [False] * self.word_length

        # Track guessed letters
        self.guessed_letters = set()

        # Track missed letters in insertion order
        self.misses = []

    def guess(self, letter: str) -> Dict:
        """
        Process a letter guess and return the updated game state.

        Args:
            letter: Single letter to guess (case-insensitive)

        Returns:
            Dictionary with:
            - result: "hit" or "miss"
            - pattern: Current pattern (e.g., "_ _ a _ a")
            - misses: List of missed letters
            - game_over: Boolean indicating if word is fully revealed
        """
        letter = letter.lower()

        # Validate input
        if len(letter) != 1 or not letter.isalpha():
            raise ValueError("Guess must be a single letter")

        # Check if already guessed
        if letter in self.guessed_letters:
            return {
                "result": "already_guessed",
                "pattern": self.get_pattern(),
                "misses": self.misses.copy(),
                "game_over": self.is_game_over()
            }

        # Mark as guessed
        self.guessed_letters.add(letter)

        # Check if it's a hit or miss
        if letter in self.secret_word:
            # Hit: reveal all occurrences
            for i, char in enumerate(self.secret_word):
                if char == letter:
                    self.revealed[i] = True

            result = "hit"
        else:
            # Miss: add to misses list
            self.misses.append(letter)
            result = "miss"

        return {
            "result": result,
            "pattern": self.get_pattern(),
            "misses": self.misses.copy(),
            "game_over": self.is_game_over()
        }

    def get_pattern(self) -> str:
        """
        Get the current pattern with revealed letters.

        Returns:
            String like "_ _ a _ a" or "apple"
        """
        pattern = []
        for i, char in enumerate(self.secret_word):
            if self.revealed[i]:
                pattern.append(char)
            else:
                pattern.append("_")
        return " ".join(pattern)

    def is_game_over(self) -> bool:
        """Check if the word is fully revealed."""
        return all(self.revealed)

    def get_remaining_letters(self) -> Set[str]:
        """Get letters that haven't been guessed yet."""
        all_letters = set('abcdefghijklmnopqrstuvwxyz')
        return all_letters - self.guessed_letters


# ============================================================================
# PART 2: Adversarial Version (Evil Hangman Strategy)
# ============================================================================

class AdversarialWordGame:
    """
    Adversarial version where the secret word can change mid-game,
    as long as it remains consistent with previous guesses.

    This implements "Evil Hangman" where Player A tries to maximize
    the number of guesses needed.
    """

    def __init__(self, word_list: List[str], word_length: int):
        """
        Initialize with a dictionary of possible words.

        Args:
            word_list: List of all valid words
            word_length: Length of words to use
        """
        # Filter words by length
        self.candidates = [w.lower() for w in word_list if len(w) == word_length]
        self.word_length = word_length

        # Track game state
        self.guessed_letters = set()
        self.misses = []
        self.pattern = ["_"] * word_length

    def guess(self, letter: str) -> Dict:
        """
        Process a guess and update candidates to maximize difficulty.

        This implements the "evil" strategy: choose the word family
        that maximizes remaining candidates.

        Args:
            letter: Letter to guess

        Returns:
            Game state dictionary
        """
        letter = letter.lower()

        if letter in self.guessed_letters:
            return {
                "result": "already_guessed",
                "pattern": " ".join(self.pattern),
                "misses": self.misses.copy(),
                "candidates_remaining": len(self.candidates)
            }

        self.guessed_letters.add(letter)

        # Partition candidates by pattern families
        families = self._partition_by_pattern(letter)

        # Choose the largest family (most candidates remaining)
        largest_family_pattern = max(families.keys(), key=lambda p: len(families[p]))
        self.candidates = families[largest_family_pattern]

        # Update pattern
        is_hit = letter in "".join(largest_family_pattern)
        if is_hit:
            self.pattern = list(largest_family_pattern)
            result = "hit"
        else:
            self.misses.append(letter)
            result = "miss"

        return {
            "result": result,
            "pattern": " ".join(self.pattern),
            "misses": self.misses.copy(),
            "candidates_remaining": len(self.candidates),
            "sample_candidates": self.candidates[:5] if len(self.candidates) <= 10 else self.candidates[:3]
        }

    def _partition_by_pattern(self, letter: str) -> Dict[Tuple, List[str]]:
        """
        Partition candidate words by their patterns for the guessed letter.

        For example, if letter='a' and word_length=5:
        - "apple" -> ('a', '_', '_', '_', '_')
        - "banana" -> ('_', 'a', '_', 'a', '_', 'a')  (uses current pattern)

        Returns:
            Dictionary mapping pattern tuples to lists of words
        """
        families = defaultdict(list)

        for word in self.candidates:
            # Create pattern for this word with current state + new letter
            pattern = []
            for i, char in enumerate(word):
                if self.pattern[i] != "_":
                    # Already revealed
                    pattern.append(self.pattern[i])
                elif char == letter:
                    # New letter matches
                    pattern.append(letter)
                else:
                    # Still hidden
                    pattern.append("_")

            families[tuple(pattern)].append(word)

        return families


# ============================================================================
# PART 2: Optimal Strategy for Player B
# ============================================================================

class OptimalGuessingStrategy:
    """
    Optimal strategy for Player B to minimize guesses when facing
    an adversarial Player A who can change the word mid-game.

    Strategy:
    1. Frequency-based guessing (good for early game)
    2. Minimax strategy (minimize worst-case partition size)
    3. Entropy-based (maximize information gain)
    """

    def __init__(self, word_list: List[str], word_length: int):
        """Initialize with candidate words."""
        self.candidates = [w.lower() for w in word_list if len(w) == word_length]
        self.word_length = word_length
        self.current_pattern = ["_"] * word_length
        self.guessed_letters = set()

    def get_best_guess_frequency(self) -> str:
        """
        Strategy 1: Guess the most frequent letter in remaining candidates.

        Simple and effective, especially early in the game.
        """
        # Count letter frequencies in all candidate words
        letter_counts = Counter()
        for word in self.candidates:
            for letter in set(word):  # Each letter once per word
                if letter not in self.guessed_letters:
                    letter_counts[letter] += 1

        if not letter_counts:
            return None

        # Return most frequent letter
        return letter_counts.most_common(1)[0][0]

    def get_best_guess_minimax(self) -> str:
        """
        Strategy 2: Minimax approach - minimize the maximum partition size.

        This minimizes worst-case scenario by choosing the letter that
        results in the smallest "largest partition" after guessing.

        Time Complexity: O(26 * n * m) where n=candidates, m=word_length
        """
        remaining_letters = set('abcdefghijklmnopqrstuvwxyz') - self.guessed_letters

        best_letter = None
        min_max_partition = float('inf')

        for letter in remaining_letters:
            # Simulate guessing this letter
            families = self._partition_by_letter(letter)

            # Find the largest partition for this letter
            max_partition_size = max(len(words) for words in families.values())

            # Track the letter with smallest max partition
            if max_partition_size < min_max_partition:
                min_max_partition = max_partition_size
                best_letter = letter

        return best_letter

    def get_best_guess_entropy(self) -> str:
        """
        Strategy 3: Maximize information gain (entropy-based).

        Choose the letter that creates the most balanced partitions,
        maximizing expected information gain.

        This is optimal for minimizing expected number of guesses.
        """
        import math

        remaining_letters = set('abcdefghijklmnopqrstuvwxyz') - self.guessed_letters

        best_letter = None
        max_entropy = -1

        for letter in remaining_letters:
            families = self._partition_by_letter(letter)
            total_words = len(self.candidates)

            # Calculate entropy: -Σ(p * log(p))
            entropy = 0
            for words in families.values():
                if len(words) > 0:
                    p = len(words) / total_words
                    entropy -= p * math.log2(p)

            if entropy > max_entropy:
                max_entropy = entropy
                best_letter = letter

        return best_letter

    def _partition_by_letter(self, letter: str) -> Dict[Tuple, List[str]]:
        """Partition candidates by pattern if we guess this letter."""
        families = defaultdict(list)

        for word in self.candidates:
            pattern = []
            for i, char in enumerate(word):
                if self.current_pattern[i] != "_":
                    pattern.append(self.current_pattern[i])
                elif char == letter:
                    pattern.append(letter)
                else:
                    pattern.append("_")

            families[tuple(pattern)].append(word)

        return families

    def update_state(self, letter: str, new_pattern: List[str], was_hit: bool):
        """Update strategy state after a guess."""
        self.guessed_letters.add(letter)
        self.current_pattern = new_pattern

        # Filter candidates based on new pattern
        self.candidates = [
            word for word in self.candidates
            if all(
                pattern_char == "_" or word[i] == pattern_char
                for i, pattern_char in enumerate(new_pattern)
            ) and (letter in word if was_hit else letter not in word)
        ]


# ============================================================================
# TESTS AND EXAMPLES
# ============================================================================

def test_basic_game():
    """Test the basic word guessing game."""
    print("="*60)
    print("Testing Basic Word Guessing Game")
    print("="*60)

    game = WordGuessingGame("apple")

    test_guesses = ['a', 'e', 'i', 'o', 'p', 'l']

    print(f"\nSecret word: {'*' * len(game.secret_word)} (length: {game.word_length})")
    print(f"Initial pattern: {game.get_pattern()}\n")

    for letter in test_guesses:
        result = game.guess(letter)
        print(f"Guess '{letter}':")
        print(f"  Result: {result['result']}")
        print(f"  Pattern: {result['pattern']}")
        print(f"  Misses: {result['misses']}")
        print(f"  Game Over: {result['game_over']}")
        print()

        if result['game_over']:
            print("🎉 Word fully revealed!")
            break


def test_adversarial_game():
    """Test the adversarial (evil hangman) version."""
    print("\n" + "="*60)
    print("Testing Adversarial Word Guessing Game")
    print("="*60)

    # Example word list
    word_list = [
        "apple", "ample", "maple", "table", "cable",
        "label", "fable", "gable", "sable", "nable"
    ]

    game = AdversarialWordGame(word_list, word_length=5)

    print(f"\nStarting with {len(game.candidates)} possible words")
    print(f"Sample words: {game.candidates[:5]}")

    test_guesses = ['e', 'a', 'l', 'b', 'p']

    for letter in test_guesses:
        result = game.guess(letter)
        print(f"\nGuess '{letter}':")
        print(f"  Result: {result['result']}")
        print(f"  Pattern: {result['pattern']}")
        print(f"  Misses: {result['misses']}")
        print(f"  Candidates remaining: {result['candidates_remaining']}")
        print(f"  Sample candidates: {result['sample_candidates']}")


def test_optimal_strategy():
    """Test the optimal guessing strategies."""
    print("\n" + "="*60)
    print("Testing Optimal Guessing Strategies")
    print("="*60)

    word_list = ["apple", "ample", "maple", "table", "cable", "label"]

    strategy = OptimalGuessingStrategy(word_list, word_length=5)

    print(f"\nCandidates: {strategy.candidates}")
    print(f"Pattern: {' '.join(strategy.current_pattern)}\n")

    # Test different strategies
    print("Strategy Recommendations:")
    print(f"  Frequency-based: '{strategy.get_best_guess_frequency()}'")
    print(f"  Minimax: '{strategy.get_best_guess_minimax()}'")
    print(f"  Entropy-based: '{strategy.get_best_guess_entropy()}'")


def demonstrate_full_game():
    """Demonstrate a complete game with optimal strategy vs adversarial opponent."""
    print("\n" + "="*60)
    print("Full Game: Optimal Strategy vs Adversarial Opponent")
    print("="*60)

    word_list = ["apple", "ample", "maple", "table", "cable", "label", "fable"]

    # Player A (adversarial)
    game = AdversarialWordGame(word_list, word_length=5)

    # Player B (optimal strategy)
    strategy = OptimalGuessingStrategy(word_list, word_length=5)

    print(f"\nStarting candidates: {len(game.candidates)} words")

    turn = 0
    max_turns = 10

    while turn < max_turns:
        turn += 1

        # Player B chooses best guess using entropy strategy
        guess = strategy.get_best_guess_entropy()

        if guess is None:
            print("\nNo more letters to guess!")
            break

        print(f"\nTurn {turn}:")
        print(f"  Player B guesses: '{guess}'")

        # Player A responds (adversarially)
        result = game.guess(guess)

        print(f"  Result: {result['result']}")
        print(f"  Pattern: {result['pattern']}")
        print(f"  Candidates remaining: {result['candidates_remaining']}")

        # Update strategy with result
        was_hit = result['result'] == 'hit'
        new_pattern = result['pattern'].split()
        strategy.update_state(guess, new_pattern, was_hit)

        # Check if only one candidate remains
        if result['candidates_remaining'] == 1:
            print(f"\n🎉 Word determined: {game.candidates[0]}")
            break


if __name__ == "__main__":
    # Run all tests
    test_basic_game()
    test_adversarial_game()
    test_optimal_strategy()
    demonstrate_full_game()

    print("\n" + "="*60)
    print("SUMMARY: Part 2 Strategy Discussion")
    print("="*60)
    print("""
When the secret word can change mid-game (Evil Hangman):

Player A's Strategy (Adversarial):
- Maintain largest possible set of candidate words
- Partition candidates by pattern on each guess
- Choose the partition with most words

Player B's Optimal Counter-Strategy:

1. Frequency-based (Simple):
   - Guess most common letters in remaining candidates
   - O(n) per guess, fast and effective early game

2. Minimax (Worst-case optimal):
   - Choose letter that minimizes maximum partition size
   - Guarantees best worst-case performance
   - O(26 * n * m) per guess

3. Entropy-based (Expected optimal):
   - Choose letter that maximizes information gain
   - Minimizes expected number of guesses
   - O(26 * n * m) per guess

Recommendation: Use entropy-based strategy for best average-case
performance, or minimax for guaranteed worst-case bounds.

Trade-offs:
- Frequency: Fast, simple, good heuristic
- Minimax: Conservative, guarantees performance
- Entropy: Optimal on average, computationally reasonable
""")
