import sys
import os
import csv
import tempfile

def test_1(input="hello world"):
    assert 'ellohay orldway' == translate(input)

def test_2(input="Hello World"):
    assert 'Ellohay Orldway' == translate(input)

def test_3(input="Hello,  world!"): # having punctuation and spaces 
    assert 'Ellohay,  orldway!' == translate(input)

def translate(input):
    import re
    def pig_word(word):
        if not word.isalpha():
            return word
        if word[0].isupper():
            core = word[1:] + word[0].lower() + 'ay'
            return core.capitalize()
        else:
            return word[1:] + word[0] + 'ay'

    # Split input into words and non-words (punctuation, spaces)
    tokens = re.findall(r'\w+|\W+', input)
    result = []
    for token in tokens:
        if token.strip() and token[0].isalpha():
            result.append(pig_word(token))
        else:
            result.append(token)
    return ''.join(result)


if __name__ == '__main__':
    test_1()
    test_2()
    test_3()
    
'''

1. Word and Non-Word Splitting
r'\w+' — Matches a word (letters, digits, underscore).
r'\W+' — Matches non-word characters (spaces, punctuation).
r'\w+|\W+' — Alternates between word and non-word tokens (used in your code).
2. Whitespace
r'\s+' — Matches one or more whitespace characters (space, tab, newline).
r'\S+' — Matches one or more non-whitespace characters.
3. Punctuation
r'[^\w\s]+' — Matches one or more punctuation characters.
4. Start/End of String or Line
^ — Start of string/line.
$ — End of string/line.
5. Word Boundaries
r'\bword\b' — Matches the word “word” as a whole word.
r'\b' — Word boundary (between word and non-word).
6. Digits and Numbers
r'\d+' — Matches one or more digits.
r'\D+' — Matches one or more non-digits.
7. Letters Only
r'[a-zA-Z]+' — Matches one or more ASCII letters.
8. Optional and Repetition
? — Zero or one (optional).
* — Zero or more.
+ — One or more.
{n} — Exactly n times.
{n,} — At least n times.
{n,m} — Between n and m times.
9. Grouping and Capturing
(pattern) — Capturing group.
(?:pattern) — Non-capturing group.
10. Escaping Special Characters
\\. — Matches a literal dot (or any special character).
Example Use Cases:

Split by words and punctuation: re.findall(r'\w+|\W+', text)
Find all words: re.findall(r'\b\w+\b', text)
Remove punctuation: re.sub(r'[^\w\s]', '', text)
Find all numbers: re.findall(r'\d+', text)
These patterns cover most needs for tokenizing, cleaning, and analyzing text in coding challenges and string manipulation tasks.

'''