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

