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
