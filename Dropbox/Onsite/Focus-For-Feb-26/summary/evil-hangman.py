'''
"Evil Hangman" is a classic Dropbox interview favorite because it flips the traditional game on its head. 
In this version, the computer cheats to make the human player lose.
The Problem: Evil HangmanIn standard Hangman, the computer picks a word and the player guesses letters. 
In Evil Hangman, the computer doesn't pick a specific word. 
Instead, it maintains a list of all possible words and, after every guess, it chooses a "family" of words that keeps the player in the dark for as long as possible.
The ObjectiveYour goal is to write a program that, given a dictionary and a letter guessed by the user, 

partitions the current word list into "word families" and selects the family that provides the maximum number of remaining possibilities for the computer.
The LogicInput: A list of words of the same length (e.g., 4 letters) and a guessed letter (e.g., 'E').

Partitioning: 
You group words based on the pattern they create with that letter.

Selection: You pick the group with the largest number of words and make that your new active word list.

Example: Step-by-StepImagine our dictionary currently has these five 4-letter words:
["DEER", "BEER", "DASH", "DISH", "HELP"]

The player guesses the letter: 'E'1. 
Categorize into FamiliesWe look at where 'E' appears in each word:

Pattern: -EE- → Words: ["DEER", "BEER"] (Count: 2)
Pattern: -E-- → Words: ["HELP"] (Count: 1)
Pattern: ---- (No 'E' at all) → Words: ["DASH", "DISH"] (Count: 2)
2. The "Evil" ChoiceThe computer must choose the largest group to keep its options open. 
In a tie (like -EE- vs ----), you can pick either, but usually, 
the "most evil" choice is the one that reveals the fewest letters to the player.
Winner: Pattern ----New Word List: ["DASH", "DISH"]
Result to Player: "Sorry, there is no 'E' in the word.

"Senior Level ExpectationsAs a senior candidate, 
I’ll be watching for how you handle these specific areas:
1. Data Structure ChoiceHow are you grouping the words?Expected: A Map<String, List<String>> where the key is the pattern (e.g., "_E_E") 
and the value is the list of words matching that pattern.2. EfficiencyIf the dictionary has 200,000 words, 
re-scanning the entire list every time is expensive.Optimization: 
Can you pre-process the dictionary by word length?Complexity: 
Be ready to discuss the Big O of the partitioning step: O(N * K) where N is the number of words in the current pool and K is the length of the word.

3. Tie-Breaking StrategiesWhat if two families are the same size?
Strategy A: Pick the one that reveals the fewest letters.
Strategy B: Pick the one that reveals no letters at all (if available).

Sample Interview Prompt"Write a function get_best_family(word_list, guessed_letter) 
that returns the largest subset of words based on the pattern of the guessed letter. 
If the player guesses 'a' for the list ['apple', 'apply', 'banas'], show me how you'd group them."

###########
Key algorithm: Minimal of maximum => choose the most group and least revealed
'''

from collections import defaultdict

def get_best_family(word_list, guessed_letter):
    """
    Partitions words into families based on the guessed_letter 
    and returns the most 'evil' one.
    """
    families = defaultdict(list)
    
    for word in word_list:
        # Generate the pattern for the current word
        # Example: 'deer' with guess 'e' becomes '_ee_'
        pattern = "".join([guessed_letter if char == guessed_letter else "_" for char in word])
        families[pattern].append(word)
    
    # Senior Tip: Use a robust tie-breaker. 
    # Here, we sort by list size (primary) and number of revealed letters (secondary).
    # We want the LARGEST list, but the FEWEST revealed letters.
    best_pattern = max(
        families.keys(), 
        key=lambda p: (len(families[p]), -len(p.replace("_", "")))
    )
    
    return best_pattern, families[best_pattern]

# Example Usage:
words = ["DEER", "BEER", "DASH", "DISH", "HELP"]
guess = "E"
pattern, new_list = get_best_family(words, guess)

print(f"Pattern Chosen: {pattern}") # Output: ____
print(f"New Word List: {new_list}") # Output: ['DASH', 'DISH']




self.pattern = ['_'] * word_length

def _partition_by_pattern(self, letter: str) -> Dict:
    """
    Partition candidates by pattern families for the guessed letter.

    Returns:
        Dictionary mapping patterns to word lists
    """
    families = defaultdict(list)

    for word in self.candidates:
        # Build pattern for this word
        pattern = [] # new pattern; self.pattern is old pattern
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

'''
### count exact match and mis match to output if needed
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
    def __init__(self, dictionary: List[str]):
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