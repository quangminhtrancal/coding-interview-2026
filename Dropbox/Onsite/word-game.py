'''
https://www.1point3acres.com/interview/problems/company/dropbox
Question Description
Implement a word guessing game:

Two players, one selects a word, and the other guesses letters.
For each guess, if the letter is in the word, it's a hit and reveal its positions.
If the letter is not in the word, it's a miss, and the letter goes into a miss array.
An example should be provided to ensure understanding of what to implement.
Variant Problem
Allowing the word selector to change the word mid-game, and the guesser tries to minimize the number of guesses.
Test Cases
No specific test cases. Discuss possible implementations during the interview.

https://www.1point3acres.com/interview/problems/50f1d1df-b408-4e3d-93bc-c186cae04e46
'''

from typing import List, Set, Dict, Optional
from collections import defaultdict, Counter
from copy import deepcopy


# ============================================================================
# PART 1: Basic Word Guessing Game (Hangman)
# ============================================================================

class WordGame:
    """
    Basic word guessing game implementation.

    Features:
    - Player 1 selects a secret word
    - Player 2 guesses letters one at a time
    - Track hits (revealed letters) and misses
    - Determine win/loss conditions
    """

    def __init__(self, secret_word: str, max_misses: int = 6):
        """
        Initialize the word game.

        Args:
            secret_word: The word to guess
            max_misses: Maximum number of incorrect guesses allowed
        """
        self.secret_word = secret_word.lower()
        self.word_length = len(secret_word)
        self.max_misses = max_misses

        # Game state
        self.revealed = ['_'] * self.word_length  # Current revealed pattern
        self.misses = []  # List of missed letters (in order)
        self.guessed_letters = set()  # All guessed letters
        self.game_over = False
        self.won = False

    def guess(self, letter: str) -> Dict:
        """
        Process a letter guess.

        Args:
            letter: Single letter to guess

        Returns:
            Dictionary with game state information
        """
        letter = letter.lower()

        # Validate input
        if len(letter) != 1 or not letter.isalpha():
            return {
                'valid': False,
                'message': 'Please guess a single letter',
                'is_hit': None
            }

        # Check if already guessed
        if letter in self.guessed_letters:
            return {
                'valid': False,
                'message': f'Already guessed "{letter}"',
                'is_hit': None
            }

        # Mark as guessed
        self.guessed_letters.add(letter)

        # Check if it's a hit or miss
        if letter in self.secret_word:
            # Hit: reveal all positions with this letter
            for i, char in enumerate(self.secret_word):
                if char == letter:
                    self.revealed[i] = letter

            is_hit = True
            message = f'Hit! "{letter}" is in the word'

            # Check win condition
            if '_' not in self.revealed:
                self.game_over = True
                self.won = True
                message = f'You won! The word is "{self.secret_word}"'
        else:
            # Miss: add to misses list
            self.misses.append(letter)
            is_hit = False
            message = f'Miss! "{letter}" is not in the word'

            # Check loss condition
            if len(self.misses) >= self.max_misses:
                self.game_over = True
                self.won = False
                message = f'Game over! The word was "{self.secret_word}"'

        return {
            'valid': True,
            'is_hit': is_hit,
            'message': message,
            'pattern': ' '.join(self.revealed),
            'misses': self.misses.copy(),
            'remaining_guesses': self.max_misses - len(self.misses),
            'game_over': self.game_over,
            'won': self.won
        }

    def get_state(self) -> Dict:
        """Get current game state."""
        return {
            'pattern': ' '.join(self.revealed),
            'misses': self.misses.copy(),
            'remaining_guesses': self.max_misses - len(self.misses),
            'game_over': self.game_over,
            'won': self.won
        }

    def __repr__(self) -> str:
        """String representation of the game state."""
        pattern = ' '.join(self.revealed)
        misses_str = ', '.join(self.misses) if self.misses else 'none'
        return f"Pattern: {pattern} | Misses: [{misses_str}] | Remaining: {self.max_misses - len(self.misses)}"


# ============================================================================
# PART 2: Variant - Evil Hangman (Word Can Change)
# ============================================================================

class EvilWordGame:
    """
    Variant where the word selector can change the word mid-game.

    Strategy: Choose the word family that maximizes remaining candidates
    after each guess (adversarial strategy).
    """

    def __init__(self, word_list: List[str], word_length: int, max_misses: int = 6):
        """
        Initialize evil word game.

        Args:
            word_list: List of valid words
            word_length: Length of words to use
            max_misses: Maximum incorrect guesses allowed
        """
        # Filter words by length
        self.candidates = [w.lower() for w in word_list if len(w) == word_length]
        self.word_length = word_length
        self.max_misses = max_misses

        # Game state
        self.pattern = ['_'] * word_length
        self.misses = []
        self.guessed_letters = set()
        self.game_over = False
        self.won = False

    def guess(self, letter: str) -> Dict:
        """
        Process a guess with adversarial word selection.

        Args:
            letter: Letter to guess

        Returns:
            Game state dictionary
        """
        letter = letter.lower()

        # Validate
        if len(letter) != 1 or not letter.isalpha():
            return {'valid': False, 'message': 'Please guess a single letter'}

        if letter in self.guessed_letters:
            return {'valid': False, 'message': f'Already guessed "{letter}"'}

        self.guessed_letters.add(letter)

        # Partition candidates by pattern families
        families = self._partition_by_pattern(letter)

        if not families:
            return {'valid': False, 'message': 'No valid candidates remaining'}

        # Choose largest family (adversarial move)
        largest_pattern = max(families.keys(), key=lambda p: len(families[p]))
        self.candidates = families[largest_pattern]

        # Check if it's a hit or miss
        is_hit = letter in ''.join(largest_pattern)

        if is_hit:
            self.pattern = list(largest_pattern)
            message = f'Hit! "{letter}" is in the word'

            # Check win condition
            if '_' not in self.pattern:
                self.game_over = True
                self.won = True
                message = f'You won! The word is "{self.candidates[0]}"'
        else:
            self.misses.append(letter)
            message = f'Miss! "{letter}" is not in the word'

            # Check loss condition
            if len(self.misses) >= self.max_misses:
                self.game_over = True
                self.won = False
                final_word = self.candidates[0] if self.candidates else 'unknown'
                message = f'Game over! The word was "{final_word}"'

        return {
            'valid': True,
            'is_hit': is_hit,
            'message': message,
            'pattern': ' '.join(self.pattern),
            'misses': self.misses.copy(),
            'remaining_guesses': self.max_misses - len(self.misses),
            'candidates_remaining': len(self.candidates),
            'game_over': self.game_over,
            'won': self.won
        }

    def _partition_by_pattern(self, letter: str) -> Dict:
        """
        Partition candidates by pattern families for the guessed letter.

        Returns:
            Dictionary mapping patterns to word lists
        """
        families = defaultdict(list)

        for word in self.candidates:
            # Build pattern for this word
            pattern = []
            for i, char in enumerate(word):
                if self.pattern[i] != '_':
                    # Already revealed
                    pattern.append(self.pattern[i])
                elif char == letter:
                    # New letter reveals this position
                    pattern.append(letter)
                else:
                    # Still hidden
                    pattern.append('_')

            families[tuple(pattern)].append(word)

        return families

    def get_state(self) -> Dict:
        """Get current game state."""
        return {
            'pattern': ' '.join(self.pattern),
            'misses': self.misses.copy(),
            'remaining_guesses': self.max_misses - len(self.misses),
            'candidates_remaining': len(self.candidates),
            'game_over': self.game_over,
            'won': self.won
        }

    def __repr__(self) -> str:
        """String representation."""
        pattern = ' '.join(self.pattern)
        misses_str = ', '.join(self.misses) if self.misses else 'none'
        return (f"Pattern: {pattern} | Misses: [{misses_str}] | "
                f"Remaining: {self.max_misses - len(self.misses)} | "
                f"Candidates: {len(self.candidates)}")


# ============================================================================
# OPTIMAL GUESSER (For Variant Problem)
# ============================================================================

class OptimalGuesser:
    """
    Optimal strategy for guessing against adversarial word selector.

    Uses entropy-based approach to maximize information gain.
    """

    def __init__(self, word_list: List[str], word_length: int):
        """Initialize with candidate words."""
        self.candidates = [w.lower() for w in word_list if len(w) == word_length]
        self.word_length = word_length
        self.pattern = ['_'] * word_length
        self.guessed_letters = set()

    def get_best_guess(self) -> Optional[str]:
        """
        Get the best letter to guess using entropy strategy.

        Returns:
            Best letter to guess, or None if no letters left
        """
        remaining_letters = set('abcdefghijklmnopqrstuvwxyz') - self.guessed_letters

        if not remaining_letters or not self.candidates:
            return None

        # Calculate entropy for each letter
        best_letter = None
        max_entropy = -1

        for letter in remaining_letters:
            families = self._simulate_partition(letter)

            # Calculate Shannon entropy
            total = len(self.candidates)
            entropy = 0

            for words in families.values():
                if len(words) > 0:
                    p = len(words) / total
                    entropy -= p * (p.bit_length() if p > 0 else 0)  # Approximation

            if entropy > max_entropy:
                max_entropy = entropy
                best_letter = letter

        return best_letter

    def _simulate_partition(self, letter: str) -> Dict:
        """Simulate partitioning candidates by a letter."""
        families = defaultdict(list)

        for word in self.candidates:
            pattern = []
            for i, char in enumerate(word):
                if self.pattern[i] != '_':
                    pattern.append(self.pattern[i])
                elif char == letter:
                    pattern.append(letter)
                else:
                    pattern.append('_')

            families[tuple(pattern)].append(word)

        return families

    def update_state(self, letter: str, new_pattern: List[str], was_hit: bool):
        """Update guesser state after a guess."""
        self.guessed_letters.add(letter)
        self.pattern = new_pattern

        # Filter candidates
        self.candidates = [
            word for word in self.candidates
            if all(
                pat == '_' or word[i] == pat
                for i, pat in enumerate(new_pattern)
            ) and (letter in word if was_hit else letter not in word)
        ]


# ============================================================================
# TEST CASES
# ============================================================================

def test_basic_game():
    """Test basic word guessing game."""
    print("="*70)
    print("TEST 1: Basic Word Guessing Game")
    print("="*70)

    game = WordGame("python", max_misses=6)

    print(f"\nSecret word: {'*' * len(game.secret_word)} (length: {game.word_length})")
    print(f"Max misses allowed: {game.max_misses}\n")

    # Simulate some guesses
    guesses = ['e', 'p', 'y', 't', 'h', 'o', 'n']

    for letter in guesses:
        result = game.guess(letter)

        if result['valid']:
            print(f"Guess '{letter}': {result['message']}")
            print(f"  {game}")

            if result['game_over']:
                break
        else:
            print(f"Guess '{letter}': {result['message']}")


def test_basic_game_with_mistakes():
    """Test game with some wrong guesses."""
    print("\n" + "="*70)
    print("TEST 2: Basic Game with Mistakes")
    print("="*70)

    game = WordGame("apple", max_misses=6)

    print(f"\nSecret word: {'*' * len(game.secret_word)}")
    print("Making guesses: a, e, i, o, u, p, l, z, x\n")

    guesses = ['a', 'e', 'i', 'o', 'u', 'p', 'l', 'z', 'x']

    for letter in guesses:
        result = game.guess(letter)

        if result['valid']:
            status = "✓" if result['is_hit'] else "✗"
            print(f"{status} Guess '{letter}': {result['is_hit'] and 'HIT' or 'MISS'}")
            print(f"  {game}")

            if result['game_over']:
                print(f"\n{result['message']}")
                break


def test_evil_game():
    """Test evil hangman variant."""
    print("\n" + "="*70)
    print("TEST 3: Evil Word Game (Word Changes)")
    print("="*70)

    word_list = ["apple", "ample", "maple", "table", "cable", "label", "fable"]

    game = EvilWordGame(word_list, word_length=5, max_misses=8)

    print(f"\nStarting with {len(game.candidates)} possible words:")
    print(f"{game.candidates}\n")

    guesses = ['e', 'a', 'l', 'b', 'p']

    for letter in guesses:
        result = game.guess(letter)

        if result['valid']:
            status = "✓" if result['is_hit'] else "✗"
            print(f"{status} Guess '{letter}': {result['is_hit'] and 'HIT' or 'MISS'}")
            print(f"  {game}")

            if result['candidates_remaining'] <= 5:
                print(f"  Remaining words: {game.candidates}")

            if result['game_over']:
                print(f"\n{result['message']}")
                break


def test_optimal_guesser_vs_evil():
    """Test optimal guesser against evil word game."""
    print("\n" + "="*70)
    print("TEST 4: Optimal Guesser vs Evil Game")
    print("="*70)

    word_list = ["apple", "ample", "maple", "table", "cable", "label", "fable", "gable"]

    # Initialize both players
    evil_game = EvilWordGame(word_list, word_length=5, max_misses=10)
    guesser = OptimalGuesser(word_list, word_length=5)

    print(f"\nStarting candidates: {len(evil_game.candidates)} words")
    print("Optimal guesser using entropy strategy\n")

    turn = 0
    max_turns = 15

    while not evil_game.game_over and turn < max_turns:
        turn += 1

        # Guesser chooses best letter
        guess = guesser.get_best_guess()

        if guess is None:
            print("No more letters to guess!")
            break

        print(f"Turn {turn}: Guessing '{guess}'")

        # Make the guess
        result = evil_game.guess(guess)

        if result['valid']:
            # Update guesser with result
            pattern = result['pattern'].split()
            guesser.update_state(guess, pattern, result['is_hit'])

            status = "✓ HIT" if result['is_hit'] else "✗ MISS"
            print(f"  {status} - Pattern: {result['pattern']}")
            print(f"  Candidates: {result['candidates_remaining']}")

            if result['game_over']:
                print(f"\n{result['message']}")
                print(f"Total guesses: {turn}")
                break


def demonstration():
    """Detailed demonstration of the game."""
    print("\n" + "="*70)
    print("DETAILED DEMONSTRATION")
    print("="*70)

    print("""
BASIC GAME RULES:
-----------------
1. Player 1 chooses a secret word
2. Player 2 guesses letters one at a time
3. HIT: If letter is in the word, reveal all positions
4. MISS: If letter is not in the word, add to miss list
5. WIN: Reveal all letters before running out of guesses
6. LOSE: Too many misses (typically 6)

EVIL VARIANT RULES:
-------------------
1. Word selector starts with a list of candidate words
2. After each guess, partition words by where letter appears
3. Choose the largest partition (maximize remaining options)
4. This maximizes the number of guesses needed

OPTIMAL STRATEGY:
-----------------
1. Use entropy-based guessing
2. Choose letter that creates most balanced partitions
3. Maximizes expected information gain
4. Minimizes expected number of guesses
""")

    # Run a simple demonstration
    print("\nSimple Example:")
    print("-" * 40)

    game = WordGame("code")

    print(f"Secret: {game.secret_word}")
    print(f"Initial: {' '.join(game.revealed)}\n")

    demo_guesses = ['c', 'o', 'd', 'e']

    for letter in demo_guesses:
        result = game.guess(letter)
        print(f"Guess '{letter}': {result['pattern']}")

        if result['game_over']:
            print(f"\n✓ {result['message']}")
            break


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                      WORD GUESSING GAME                              ║
║                                                                      ║
║  Basic: Classic Hangman game                                        ║
║  Variant: Evil Hangman (word can change mid-game)                   ║
╚══════════════════════════════════════════════════════════════════════╝
""")

    # Run demonstrations
    demonstration()

    # Run all tests
    test_basic_game()
    test_basic_game_with_mistakes()
    test_evil_game()
    test_optimal_guesser_vs_evil()

    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print("""
Key Implementation Points:

1. BASIC GAME (WordGame class):
   - Track secret word, revealed pattern, misses
   - guess() method processes each letter
   - Check win/loss conditions
   - Time: O(1) per guess
   - Space: O(word_length)

2. EVIL VARIANT (EvilWordGame class):
   - Start with list of candidate words
   - Partition by pattern after each guess
   - Choose largest partition (adversarial)
   - Forces maximum number of guesses
   - Time: O(candidates * word_length) per guess
   - Space: O(candidates * word_length)

3. OPTIMAL GUESSER (OptimalGuesser class):
   - Use entropy to choose best letter
   - Maximize information gain
   - Filter candidates after each guess
   - Minimizes expected guesses
   - Time: O(26 * candidates * word_length) per guess

4. EDGE CASES:
   - Duplicate letter guesses
   - Invalid input (non-letters, multiple chars)
   - Empty candidate list
   - Already won/lost game

5. INTERVIEW DISCUSSION POINTS:
   - Basic implementation is straightforward
   - Evil variant shows understanding of adversarial algorithms
   - Optimal guesser demonstrates information theory
   - Trade-offs between complexity and optimality

The basic implementation is simple and correct. The variant
problem demonstrates advanced algorithm design and game theory
concepts that are commonly tested in interviews.
""")
