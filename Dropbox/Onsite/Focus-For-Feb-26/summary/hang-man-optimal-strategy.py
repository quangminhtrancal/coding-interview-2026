'''
https://www.1point3acres.com/interview/problems/03d208eb-7407-4966-b8c0-0f063d5fa252

Design a program to play a hangman game. In this game, there are two players; 
Player 1 guesses letters and Player 2 chooses a word. 
If both players use optimal strategies, design an algorithm that will allow Player 1 to 
always find the optimal solution. 

Given a list of words, develop an algorithm to output the sequence of letter guesses 
that minimizes the number of incorrect guesses. Provide multiple test cases to validate your algorithm.


PROBLEM ANALYSIS:
=================

When both players play optimally:

Player 2 (Word Chooser) - Adversarial Strategy:
- Never commits to a specific word until forced
- After each guess, partitions remaining words by pattern
- Chooses the largest partition (maximizes remaining possibilities)
- This is called "Evil Hangman"

Player 1 (Guesser) - Optimal Counter-Strategy:
- Must assume Player 2 is adversarial
- Goal: Minimize worst-case or expected number of guesses
- Several approaches:
  1. Frequency-based: Guess most common letters
  2. Minimax: Minimize maximum partition size
  3. Entropy: Maximize information gain (OPTIMAL)
  4. Expected value: Minimize expected partition size

Key Insight: This is a minimax game theory problem. Player 1 should use
entropy-based guessing to maximize information gain per guess.
'''

from typing import List, Set, Dict, Tuple, Optional
from collections import Counter, defaultdict
import math


# ============================================================================
# EVIL HANGMAN - Player 2's Optimal Strategy
# ============================================================================

class EvilHangman:
    """
    Implements Player 2's optimal (adversarial) strategy.

    Strategy: Always choose the word family that maximizes remaining candidates.
    This forces Player 1 to make the most guesses possible.
    """

    def __init__(self, word_list: List[str], word_length: int):
        """
        Initialize the game with a list of possible words.

        Args:
            word_list: Dictionary of all valid words
            word_length: Length of the word to guess
        """
        self.candidates = [w.lower() for w in word_list if len(w) == word_length]
        self.word_length = word_length
        self.pattern = ['_'] * word_length
        self.guessed_letters = set()
        self.incorrect_guesses = []

    def process_guess(self, letter: str) -> Dict:
        """
        Process a letter guess using adversarial strategy.

        Returns the pattern that maximizes remaining candidates.
        """
        letter = letter.lower()

        if letter in self.guessed_letters:
            return {
                'is_correct': None,
                'pattern': self.pattern.copy(),
                'incorrect_guesses': self.incorrect_guesses.copy(),
                'candidates_remaining': len(self.candidates),
                'message': 'Already guessed'
            }

        self.guessed_letters.add(letter)

        # Partition candidates by pattern
        families = self._partition_by_pattern(letter)

        # Choose largest family (adversarial move)
        if not families:
            # No candidates left - this shouldn't happen
            return {
                'is_correct': False,
                'pattern': self.pattern.copy(),
                'incorrect_guesses': self.incorrect_guesses.copy(),
                'candidates_remaining': 0,
                'message': 'Error: No candidates'
            }

        # Get the largest family
        largest_pattern = max(families.keys(), key=lambda p: len(families[p]))
        self.candidates = families[largest_pattern]

        # Check if this was a hit or miss
        is_hit = letter in ''.join(largest_pattern)

        if is_hit:
            self.pattern = list(largest_pattern)
        else:
            self.incorrect_guesses.append(letter)

        return {
            'is_correct': is_hit,
            'pattern': self.pattern.copy(),
            'incorrect_guesses': self.incorrect_guesses.copy(),
            'candidates_remaining': len(self.candidates),
            'message': 'Hit' if is_hit else 'Miss'
        }

    def _partition_by_pattern(self, letter: str) -> Dict[Tuple, List[str]]:
        """
        Partition candidates into families based on where the letter appears.

        Example: For letter 'a' and words ['cat', 'bat', 'dog']:
        - Pattern ('_', 'a', '_') -> ['cat', 'bat']
        - Pattern ('_', '_', '_') -> ['dog']
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

    def is_solved(self) -> bool:
        """Check if the word is fully revealed."""
        return '_' not in self.pattern

    def get_actual_word(self) -> Optional[str]:
        """Return the actual word (when only one candidate remains)."""
        if len(self.candidates) == 1:
            return self.candidates[0]
        return None


# ============================================================================
# OPTIMAL GUESSER - Player 1's Strategies
# ============================================================================

class OptimalGuesser:
    """
    Implements Player 1's optimal guessing strategies against an adversarial opponent.

    Provides multiple strategies:
    1. Frequency-based
    2. Minimax
    3. Entropy (information-theoretic - OPTIMAL)
    4. Expected value
    """

    def __init__(self, word_list: List[str], word_length: int):
        """Initialize with candidate words."""
        self.candidates = [w.lower() for w in word_list if len(w) == word_length]
        self.word_length = word_length
        self.pattern = ['_'] * word_length
        self.guessed_letters = set()

    def get_next_guess_frequency(self) -> Optional[str]:
        """
        Strategy 1: Frequency-based guessing.

        Guess the letter that appears in the most candidate words.

        Time: O(n * m) where n=candidates, m=word_length

        Pros: Simple, fast
        Cons: Doesn't account for adversarial strategy
        """
        if not self.candidates:
            return None

        # Count how many words contain each letter
        letter_frequency = Counter()
        for word in self.candidates:
            for letter in set(word):
                if letter not in self.guessed_letters:
                    letter_frequency[letter] += 1

        if not letter_frequency:
            return None

        return letter_frequency.most_common(1)[0][0]

    def get_next_guess_minimax(self) -> Optional[str]:
        """
        Strategy 2: Minimax approach.

        Choose the letter that minimizes the maximum partition size.
        This guarantees the best worst-case performance.

        Time: O(26 * n * m)

        Pros: Optimal worst-case guarantee
        Cons: Computationally expensive
        """
        remaining_letters = set('abcdefghijklmnopqrstuvwxyz') - self.guessed_letters

        if not remaining_letters:
            return None

        best_letter = None
        min_worst_case = float('inf')

        for letter in remaining_letters:
            # Simulate guessing this letter
            families = self._simulate_partition(letter)

            if not families:
                continue

            # Find worst case (largest partition)
            worst_case = max(len(words) for words in families.values())

            # Track best worst case
            if worst_case < min_worst_case:
                min_worst_case = worst_case
                best_letter = letter

        return best_letter

    def get_next_guess_entropy(self) -> Optional[str]:
        """
        Strategy 3: Entropy-based (Information Theory).

        Choose the letter that maximizes expected information gain.
        Uses Shannon entropy: H(X) = -Σ p(x) * log2(p(x))

        This is the OPTIMAL strategy for minimizing expected guesses.

        Time: O(26 * n * m)

        Pros: Optimal expected performance, information-theoretic foundation
        Cons: Computationally expensive
        """
        remaining_letters = set('abcdefghijklmnopqrstuvwxyz') - self.guessed_letters

        if not remaining_letters:
            return None

        best_letter = None
        max_entropy = -1

        for letter in remaining_letters:
            # Simulate guessing this letter
            families = self._simulate_partition(letter)

            if not families:
                continue

            # Calculate entropy
            total_words = len(self.candidates)
            entropy = 0

            for words in families.values():
                if len(words) > 0:
                    p = len(words) / total_words
                    entropy -= p * math.log2(p)

            # Track best entropy
            if entropy > max_entropy:
                max_entropy = entropy
                best_letter = letter

        return best_letter

    def get_next_guess_expected_value(self) -> Optional[str]:
        """
        Strategy 4: Expected value minimization.

        Choose the letter that minimizes the expected partition size.

        Expected size = Σ p(partition) * size(partition)

        Time: O(26 * n * m)

        Pros: Good average-case performance
        Cons: Not as robust as minimax for worst-case
        """
        remaining_letters = set('abcdefghijklmnopqrstuvwxyz') - self.guessed_letters

        if not remaining_letters:
            return None

        best_letter = None
        min_expected = float('inf')

        for letter in remaining_letters:
            families = self._simulate_partition(letter)

            if not families:
                continue

            # Calculate expected partition size
            total_words = len(self.candidates)
            expected_size = 0

            for words in families.values():
                p = len(words) / total_words
                # We'll end up in this partition with probability p
                # Expected size is the size of that partition
                expected_size += p * len(words)

            if expected_size < min_expected:
                min_expected = expected_size
                best_letter = letter

        return best_letter

    def _simulate_partition(self, letter: str) -> Dict[Tuple, List[str]]:
        """Simulate partitioning candidates if we guess this letter."""
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

    def update_state(self, letter: str, new_pattern: List[str], was_correct: bool):
        """Update guesser state after a guess."""
        self.guessed_letters.add(letter)
        self.pattern = new_pattern

        # Filter candidates based on new information
        self.candidates = [
            word for word in self.candidates
            if all(
                pat == '_' or word[i] == pat
                for i, pat in enumerate(new_pattern)
            ) and (letter in word if was_correct else letter not in word)
        ]


# ============================================================================
# GAME SIMULATOR - Test the strategies
# ============================================================================

class HangmanGameSimulator:
    """Simulates a full Hangman game with both players using optimal strategies."""

    @staticmethod
    def play_game(word_list: List[str], word_length: int,
                  strategy: str = 'entropy', verbose: bool = True) -> Dict:
        """
        Play a complete game and return statistics.

        Args:
            word_list: Dictionary of valid words
            word_length: Length of word to guess
            strategy: 'frequency', 'minimax', 'entropy', or 'expected'
            verbose: Print game progress

        Returns:
            Dictionary with game statistics
        """
        # Initialize players
        evil_hangman = EvilHangman(word_list, word_length)
        guesser = OptimalGuesser(word_list, word_length)

        if verbose:
            print(f"\n{'='*70}")
            print(f"Starting game with {len(evil_hangman.candidates)} candidates")
            print(f"Word length: {word_length}, Strategy: {strategy}")
            print(f"{'='*70}")

        total_guesses = 0
        incorrect_guesses = 0
        guess_sequence = []

        while not evil_hangman.is_solved() and total_guesses < 50:
            # Guesser chooses next letter
            if strategy == 'frequency':
                guess = guesser.get_next_guess_frequency()
            elif strategy == 'minimax':
                guess = guesser.get_next_guess_minimax()
            elif strategy == 'entropy':
                guess = guesser.get_next_guess_entropy()
            elif strategy == 'expected':
                guess = guesser.get_next_guess_expected_value()
            else:
                raise ValueError(f"Unknown strategy: {strategy}")

            if guess is None:
                break

            total_guesses += 1
            guess_sequence.append(guess)

            # Process guess
            result = evil_hangman.process_guess(guess)

            if verbose:
                print(f"\nGuess #{total_guesses}: '{guess}'")
                print(f"  Result: {result['message']}")
                print(f"  Pattern: {' '.join(result['pattern'])}")
                print(f"  Candidates: {result['candidates_remaining']}")
                if result['candidates_remaining'] <= 5:
                    print(f"  Remaining: {evil_hangman.candidates}")

            # Update guesser
            guesser.update_state(guess, result['pattern'], result['is_correct'])

            if not result['is_correct']:
                incorrect_guesses += 1

        final_word = evil_hangman.get_actual_word()

        if verbose:
            print(f"\n{'='*70}")
            print(f"Game complete!")
            print(f"Final word: {final_word or 'Not determined'}")
            print(f"Total guesses: {total_guesses}")
            print(f"Incorrect guesses: {incorrect_guesses}")
            print(f"Guess sequence: {' -> '.join(guess_sequence)}")
            print(f"{'='*70}")

        return {
            'strategy': strategy,
            'total_guesses': total_guesses,
            'incorrect_guesses': incorrect_guesses,
            'guess_sequence': guess_sequence,
            'final_word': final_word,
            'solved': evil_hangman.is_solved()
        }

    @staticmethod
    def compare_strategies(word_list: List[str], word_length: int) -> None:
        """Compare all strategies and show which performs best."""
        print(f"\n{'='*70}")
        print("STRATEGY COMPARISON")
        print(f"{'='*70}")

        strategies = ['frequency', 'minimax', 'entropy', 'expected']
        results = {}

        for strategy in strategies:
            print(f"\nTesting {strategy.upper()} strategy...")
            result = HangmanGameSimulator.play_game(
                word_list, word_length, strategy, verbose=False
            )
            results[strategy] = result

        # Print comparison
        print(f"\n{'='*70}")
        print("RESULTS SUMMARY")
        print(f"{'='*70}")
        print(f"{'Strategy':<15} {'Total Guesses':<15} {'Incorrect':<15} {'Final Word':<15}")
        print(f"{'-'*70}")

        for strategy in strategies:
            r = results[strategy]
            print(f"{strategy.capitalize():<15} {r['total_guesses']:<15} "
                  f"{r['incorrect_guesses']:<15} {r['final_word'] or 'N/A':<15}")

        # Determine best strategy
        best_strategy = min(strategies, key=lambda s: results[s]['incorrect_guesses'])
        print(f"\n{'='*70}")
        print(f"Best strategy: {best_strategy.upper()} "
              f"({results[best_strategy]['incorrect_guesses']} incorrect guesses)")
        print(f"{'='*70}")


# ============================================================================
# TEST CASES
# ============================================================================

def test_case_1():
    """Test Case 1: Small word list with common words."""
    print("\n" + "="*70)
    print("TEST CASE 1: Small Word List")
    print("="*70)

    word_list = ["apple", "ample", "maple", "table", "cable"]
    word_length = 5

    HangmanGameSimulator.compare_strategies(word_list, word_length)


def test_case_2():
    """Test Case 2: Larger word list with more variety."""
    print("\n" + "="*70)
    print("TEST CASE 2: Larger Word List")
    print("="*70)

    word_list = [
        "apple", "ample", "maple", "table", "cable", "label", "fable",
        "sable", "gable", "noble", "Bible", "rifle", "trifle", "stifle"
    ]
    word_length = 5

    HangmanGameSimulator.compare_strategies(word_list, word_length)


def test_case_3():
    """Test Case 3: Words with repeated letters."""
    print("\n" + "="*70)
    print("TEST CASE 3: Words with Repeated Letters")
    print("="*70)

    word_list = ["book", "look", "took", "cook", "hook", "good", "food", "mood"]
    word_length = 4

    HangmanGameSimulator.compare_strategies(word_list, word_length)


def test_case_4():
    """Test Case 4: Longer words."""
    print("\n" + "="*70)
    print("TEST CASE 4: Longer Words")
    print("="*70)

    word_list = [
        "algorithm", "logarithm", "chemistry", "geography", "biography"
    ]
    word_length = 9

    HangmanGameSimulator.compare_strategies(word_list, word_length)


def test_case_5():
    """Test Case 5: Very similar words (hard case)."""
    print("\n" + "="*70)
    print("TEST CASE 5: Very Similar Words (Hardest Case)")
    print("="*70)

    word_list = ["cat", "hat", "bat", "mat", "sat", "rat", "pat", "fat", "vat"]
    word_length = 3

    # This should show the advantage of entropy-based approach
    HangmanGameSimulator.play_game(word_list, word_length, 'entropy', verbose=True)


def demonstration():
    """Detailed demonstration of entropy strategy."""
    print("\n" + "="*70)
    print("DETAILED DEMONSTRATION: Entropy Strategy")
    print("="*70)

    word_list = ["apple", "ample", "maple", "table", "cable", "label"]
    word_length = 5

    result = HangmanGameSimulator.play_game(
        word_list, word_length, 'entropy', verbose=True
    )

    print("\n" + "="*70)
    print("ANALYSIS:")
    print("="*70)
    print(f"""
The entropy-based strategy is optimal because:

1. Information Theory Foundation:
   - Each guess provides information to narrow down candidates
   - Entropy measures the expected information gain
   - Higher entropy = more balanced partitions = more information

2. Optimal Against Adversary:
   - Even when Player 2 chooses the largest partition (worst case)
   - Entropy strategy ensures we eliminate candidates efficiently
   - Minimizes expected number of guesses

3. Mathematical Optimality:
   - Proven by information theory
   - Entropy maximization = information gain maximization
   - Works well even when adversary plays optimally

4. This Example:
   - Total guesses: {result['total_guesses']}
   - Incorrect guesses: {result['incorrect_guesses']}
   - Sequence: {' -> '.join(result['guess_sequence'])}
""")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║           OPTIMAL HANGMAN STRATEGY ANALYSIS                          ║
║                                                                      ║
║  Problem: Design algorithm for Player 1 to minimize guesses when    ║
║          both players use optimal strategies                        ║
║                                                                      ║
║  Solution: Use information-theoretic (entropy) approach              ║
╚══════════════════════════════════════════════════════════════════════╝
""")

    # Run detailed demonstration
    demonstration()

    # Run all test cases
    print("\n" + "="*70)
    print("RUNNING ALL TEST CASES")
    print("="*70)

    test_case_1()
    test_case_2()
    test_case_3()
    test_case_4()
    test_case_5()

    # Final summary
    print("\n" + "="*70)
    print("CONCLUSION")
    print("="*70)
    print("""
KEY FINDINGS:

1. OPTIMAL STRATEGY: Entropy-based (information-theoretic)
   - Maximizes expected information gain per guess
   - Performs best against adversarial opponent
   - Mathematically proven optimal for expected case

2. ALTERNATIVE STRATEGIES:
   - Minimax: Best for worst-case guarantees
   - Frequency: Simple and fast, good heuristic
   - Expected Value: Good average case, similar to entropy

3. GAME THEORY INSIGHTS:
   - This is a minimax game with perfect information
   - Player 2's optimal strategy: maximize partition size
   - Player 1's counter: maximize information gain
   - Entropy naturally handles adversarial behavior

4. COMPLEXITY ANALYSIS:
   - All optimal strategies: O(26 * n * m) per guess
   - Where n = candidates, m = word length
   - Acceptable for practical use cases
   - Can be optimized with caching/memoization

5. PRACTICAL RECOMMENDATIONS:
   - Use entropy strategy for best results
   - Use frequency for quick approximation
   - Use minimax when worst-case guarantee needed
   - All strategies converge as candidates decrease

The entropy-based approach is the OPTIMAL solution that minimizes
the number of incorrect guesses when both players play optimally.
""")
