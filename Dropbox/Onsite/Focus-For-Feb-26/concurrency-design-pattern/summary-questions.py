'''
2025 (Oct-Dec)
Two rounds of coding.\u003c/a\u003e \u003ca i=1\u003

The first round was about a file crawler, divided into three steps:\u003c/a\u003e \u003ca i=2\u003e
Step 1: Implement an API that, given a file path, returns all files within that path, along with a helper function.

Step 2: No coding required, just verbal instructions on how to crawl the file.\u003c/a\u003e",

a bit more difficult. The person choosing the words can change them midway, 
while the person guessing the words needs to minimize the number of guesses. 
We just need to discuss the solution and write some pseudocode",



https://www.1point3acres.com/bbs/thread-1156153-1-1.html
First Round In-Store Interview: Coding: Simulate a file system, given a List<List<string>> folders and a HashS...


https://www.1point3acres.com/bbs/thread-1142281-1-1.html 
https://www.1point3acres.com/bbs/thread-1142281-1-1.html 
human interview 1:
human interview 1:
A standard DSA problem involving finding largest area of island from grid (pretty standard lc problem). 
However, they added at the end that they wanted to also make one water cell -> land, and make one land cell -> water.
 They want to do this repeatedly, and also tell yo

 Analyze which test is failing.

 
 https://www.1point3acres.com/bbs/thread-1134760-1-1.html
 A total of 6 rounds . Code: Key-Value transactions + multi-threaded issues similar to token buckets 
 (same exam point, changed to resource management, same principle). 
 The rollback implementation for the Key-Value one is too complicated; don't worry about that.

 Q: Dropbox, logging system—that's what they asked on the exam, and the question itself was quite difficult.


 https://www.1point3acres.com/bbs/thread-1128041-1-1.html
 Asking for details about a project, such as how to collaborate, the plan, design, etc.
 If I were to redo it, what would be different? (Seeking points for this post. )


 https://www.1point3acres.com/bbs/thread-1035232-1-1.html
 Dropbox hasn't had any staff-level backend positions for the past few months. 
 In November, I saw a staff infrastructure software engineer position and applied immediately. 
 After passing the online assessment (OA), the recruiter scheduled an HR call for me. 
 I learned that this infrastructure position mainly involves search, and 
 staff-level positions require a deep understanding of big data search systems, 
 including Elastic Search. I've used Elastic Search before, but that's about it; 
 I haven't worked on the internal mechanisms of Elastic Search, let alone built a large-scale search system. 
 The recruiter suggested scheduling a meeting with hiring manager (HM) to discuss further, but I declined. 
 I acknowledged my lack of experience in this area and even if HM agreed to the interview and 
 I was hired, insufficient experience might hinder my performance. I asked the recruiter to contact me 
 if they saw any other business intelligence (BE) positions available.

Also, I noticed the online assessment (OA) only had a few questions, but even for the same questions 
(e.g., in memory systems, bank systems, editors, cloud systems), the requirements varied from person to person. 
It's crucial to avoid simply memorizing answers from past questions and carefully reading the specific requirements 
of the question you receive. (


https://www.1point3acres.com/bbs/thread-1031118-1-1.html
I had 5 rounds of interviews. The first round was coding, involving a file crawler; the second round was C++.


https://www.1point3acres.com/bbs/thread-918888-1-1.html
Coding 1: Top N photo views, using a treeMap. 
Coding 2: Key-value store, requiring at least read-committed operation. 
However, the question stated a single-threaded environment with concurrent transactions.

Or Kafka, which actually requires you to design the Producer/Consumer side of the Queue, focusing on API and schema design.




https://www.hacktherounds.com/problem/464?company=27
File access control

 "solutions": [
        {
            "approach_number": 1,
            "title": "Approach 1: Prefix Matching",
            "intuition": "Check if the requested path starts with any allowed path prefix. This gives immediate access check without building a tree.",
            "algorithm": "1. Store allowed paths in a set\n2. For each access check, compare path against all allowed prefixes\n3. A path is accessible if any allowed path is a prefix of it\n4. Handle the exact match case and proper path boundaries",
            "code": {
                "python": "class AccessControl:\n    \"\"\"\n    File System Access Control using Prefix Matching.\n    \n    Approach: Check if requested path has any allowed path as prefix.\n    Time Complexity: O(a) per check where a = number of allowed paths\n    Space Complexity: O(a) for storing allowed paths\n    \"\"\"\n    def __init__(self):\n        # Paths the user has direct access to\n        self.allowed_paths = {\"/A/B\", \"/A/B/C\", \"/A/B/C/D\"}\n\n    def has_access(self, path: str) -> bool:\n        \"\"\"\n        Check if user has access to the given path.\n        User has access if path or any parent path is in allowed_paths.\n        \"\"\"\n        # Check exact path match\n        if path in self.allowed_paths:\n            return True\n\n        # Check if any allowed path is a prefix of the requested path\n        for allowed in self.allowed_paths:\n            # Ensure proper path boundary (allowed + \"/\" is prefix of path)\n            if path.startswith(allowed + \"/\"):\n                return True\n\n        return False\n"
            },
            "time_complexity": "O(a) where a = number of allowed paths",
            "space_complexity": "O(a) for storing allowed paths"
        },
        {
            "approach_number": 2,
            "title": "Approach 2: Parent Traversal",
            "intuition": "Walk up the path hierarchy checking each parent. This is efficient when the path depth is small compared to allowed paths count.",
            "algorithm": "1. Store allowed paths in a set\n2. Starting from the requested path, walk up to each parent\n3. Check if current path or any parent is in allowed set\n4. Stop when root is reached or access is found",
            "code": {
                "python": "class AccessControl:\n    \"\"\"\n    File System Access Control using Parent Traversal.\n    \n    Approach: Walk up the path hierarchy checking each ancestor.\n    Time Complexity: O(d) per check where d = path depth\n    Space Complexity: O(a) for storing allowed paths\n    \"\"\"\n    def __init__(self):\n        # Paths the user has direct access to\n        self.allowed_paths = {\"/A/B\", \"/A/B/C\", \"/A/B/C/D\"}\n\n    def has_access(self, path: str) -> bool:\n        \"\"\"\n        Check if user has access to the given path.\n        Walk up the path hierarchy and check if any ancestor is allowed.\n        \"\"\"\n        current = path\n        \n        while current:\n            # Check if current path is allowed\n            if current in self.allowed_paths:\n                return True\n            \n            # Move to parent path\n            if \"/\" in current[1:]:  # Has a parent (not just root)\n                current = current.rsplit(\"/\", 1)[0]\n                if not current:  # Reached root\n                    current = \"/\"\n            elif current == \"/\":\n                break  # Already at root\n            else:\n                current = \"/\"  # Move to root\n        \n        return False\n"
            },
            "time_complexity": "O(d) where d = depth of path",
            "space_complexity": "O(a) for storing allowed paths"
        }
    ],


https://www.hacktherounds.com/problem/621?company=27
WordGame Hangman

 "solutions": [
        {
            "approach_number": 1,
            "title": "Approach 1: Set-based Tracking",
            "intuition": "Track game state using sets for efficient lookup of guessed letters and revealed positions.",
            "algorithm": "1. Store guessed letters in a set\n2. Track revealed positions as a list\n3. On each guess, check if letter is in secret word\n4. Return HIT or MISS accordingly\n5. Track win/lose conditions",
            "code": {
                "python": "class WordGame:\n    \"\"\"\n    Hangman Word Game with Set-based State Tracking.\n    \n    Approach: Use sets for O(1) lookup of guessed letters.\n    Time Complexity: O(n) per guess where n = word length\n    Space Complexity: O(k + m) where k = unique letters, m = guesses\n    \"\"\"\n    def __init__(self, dictionary: list, secret_word: str, max_misses: int = 6):\n        self.dictionary = set(dictionary)\n        self.secret = secret_word.lower()\n        self.max_misses = max_misses\n        self.revealed = ['_'] * len(self.secret)\n        self.misses = []\n        self.guessed = set()\n        self.game_over = False\n        self.won = False\n    \n    def guess(self, letter: str) -> str:\n        \"\"\"Guess a letter. Returns 'HIT', 'MISS', or 'INVALID'.\"\"\"\n        if self.game_over or letter in self.guessed:\n            return \"INVALID\"\n        \n        letter = letter.lower()\n        self.guessed.add(letter)\n        \n        if letter in self.secret:\n            # Reveal all occurrences\n            for i, c in enumerate(self.secret):\n                if c == letter:\n                    self.revealed[i] = letter\n            \n            # Check win condition\n            if '_' not in self.revealed:\n                self.game_over = True\n                self.won = True\n            \n            return \"HIT\"\n        else:\n            self.misses.append(letter)\n            \n            # Check lose condition\n            if len(self.misses) >= self.max_misses:\n                self.game_over = True\n            \n            return \"MISS\"\n    \n    def get_revealed(self) -> str:\n        \"\"\"Get current revealed state of word.\"\"\"\n        return ''.join(self.revealed)\n    \n    def get_misses(self) -> list:\n        \"\"\"Get list of missed letters.\"\"\"\n        return self.misses.copy()\n    \n    def is_game_over(self) -> bool:\n        \"\"\"Check if game is over.\"\"\"\n        return self.game_over\n    \n    def has_won(self) -> bool:\n        \"\"\"Check if player has won.\"\"\"\n        return self.won\n"
            },
            "time_complexity": "O(n) per guess where n = word length",
            "space_complexity": "O(k + m) where k = unique letters, m = guesses"
        },
        {
            "approach_number": 2,
            "title": "Approach 2: Frequency-based with Word Filtering",
            "intuition": "Track state and also maintain a list of possible words for adaptive guessing strategy.",
            "algorithm": "1. Same basic tracking as Approach 1\n2. Additionally maintain list of possible words from dictionary\n3. Filter possible words based on revealed letters and misses\n4. Can be used to implement adaptive picker strategy",
            "code": {
                "python": "class WordGame:\n    \"\"\"\n    Hangman with Word Filtering for Adaptive Strategy.\n    \n    Approach: Maintain possible words list for smart guessing/picking.\n    Time Complexity: O(n) per guess, O(d*m) for filtering possible words\n    Space Complexity: O(d) where d = dictionary size\n    \"\"\"\n    def __init__(self, dictionary: list, secret_word: str, max_misses: int = 6):\n        self.dictionary = set(dictionary)\n        self.secret = secret_word.lower()\n        self.max_misses = max_misses\n        self.revealed = ['_'] * len(self.secret)\n        self.misses = []\n        self.guessed = set()\n        self.game_over = False\n        self.won = False\n        # Filter to same-length words\n        self.possible_words = [w for w in dictionary if len(w) == len(self.secret)]\n    \n    def guess(self, letter: str) -> str:\n        \"\"\"Guess a letter.\"\"\"\n        if self.game_over or letter in self.guessed:\n            return \"INVALID\"\n        \n        letter = letter.lower()\n        self.guessed.add(letter)\n        \n        if letter in self.secret:\n            for i, c in enumerate(self.secret):\n                if c == letter:\n                    self.revealed[i] = letter\n            \n            # Update possible words\n            self._filter_possible_words()\n            \n            if '_' not in self.revealed:\n                self.game_over = True\n                self.won = True\n            \n            return \"HIT\"\n        else:\n            self.misses.append(letter)\n            \n            # Update possible words (remove words containing missed letter)\n            self._filter_possible_words()\n            \n            if len(self.misses) >= self.max_misses:\n                self.game_over = True\n            \n            return \"MISS\"\n    \n    def _filter_possible_words(self):\n        \"\"\"Filter possible words based on current state.\"\"\"\n        new_possible = []\n        for word in self.possible_words:\n            valid = True\n            # Check revealed letters match\n            for i, c in enumerate(self.revealed):\n                if c != '_' and word[i] != c:\n                    valid = False\n                    break\n            # Check no missed letters in word\n            if valid:\n                for miss in self.misses:\n                    if miss in word:\n                        valid = False\n                        break\n            if valid:\n                new_possible.append(word)\n        self.possible_words = new_possible\n    \n    def get_revealed(self) -> str:\n        return ''.join(self.revealed)\n    \n    def get_misses(self) -> list:\n        return self.misses.copy()\n    \n    def is_game_over(self) -> bool:\n        return self.game_over\n    \n    def has_won(self) -> bool:\n        return self.won\n    \n    def get_possible_words(self) -> list:\n        \"\"\"Get list of words that could still be the secret.\"\"\"\n        return self.possible_words.copy()\n"
            },
            "time_complexity": "O(n) per guess, O(d*m) for word filtering",
            "space_complexity": "O(d) where d = dictionary size"
        }
    ],
    "test_cases": [],
    "hints": [
        {
            "level": 1,
            "title": "High-Level Approach",
            "content": "Track game state with: revealed positions (list), guessed letters (set), and misses (list). Each guess updates these and checks win/lose conditions."
        },
        {
            "level": 2,
            "title": "Data Structure Choice",
            "content": "Use a set for guessed letters (O(1) lookup), a list for revealed word state, and a list for ordered misses."
        },
        {
            "level": 3,
            "title": "Edge Cases to Consider",
            "content": "Handle: repeated guesses (return INVALID), letters appearing multiple times in word, case sensitivity, and exact win/lose boundary conditions."
        },
        {
            "level": 4,
            "title": "Adaptive Strategy Hint",
            "content": "For Part 2, the picker can change words mid-game. To counter this, the guesser should track all possible words matching current state and guess letters that maximize information gain."
        }
    ],

    
    https://www.reddit.com/r/cscareerquestions/comments/jhob3n/how_to_answer_this_question_asked_by_snapchat_and/
    
    I've gotten asked this algorithm/problem-solving question by Snap and Dropbox. 
    In both scenarios, I felt like my answer was lacking, and I'm wondering if there are any senior engineers 
    in this thread who might have a more robust answer to this question:


Given a list of files and their contents (file1 -> "aaa", file2 -> "b", file3 -> "b", file4 -> "aaa"), return output grouped by files with identical contents, so: [[file1, file4], [file2, file3]]. It's similar to this leetcode question https://leetcode.com/problems/find-duplicate-file-in-system/ However the actual coding in this problem is quite trivial. The more difficult part were the layers of complexity that could be added to it. My approach for the problem was as follows:

Read each file, compute a hash, and store that as a key in hashmap along with a list of file names as the value. Of course the bottle neck here is opening files, which could each be GB.

I suggested to first group files by their size, and only perform reads on files with the same size (this would reduce number of reads).

Interviewer then asked what if each file is the same size? I suggested to read the first 10% of the file, but that number was arbitrary. My interviewer mentioned you could read each file a "block" at a time, though I'm not entirely sure what that means.

He also asked how can we guarantee accuracy. For example, if there are a million files, even your hashmap could be a bottleneck and you could end up with collisions. I wasn't sure how to answer this part, but apparently the answer was that you can't get around reading the files while computing the results to truly guarantee accuracy.

I feel like there are a lot of other optimizations I could've made to this problem. My interviewer mentioned you could also account for file headers and skip the first few lines of each file when performing a read, and account for file formats. Overall it was a difficult question with lots of what-ifs. Would appreciate if anyone in this thread could add on to my approach above and suggest better ways of optimizing/answering this question? It seems to be a pretty popular one...


https://github.com/insideofdrop/Dropbox-Interview-Prep?tab=readme-ov-file


https://github.com/snehasishroy/leetcode-companywise-interview-questions/blob/master/dropbox/all.csv
All dropbox questions

    https://www.hacktherounds.com/problem/467?company=27
    Blob storage system design
 '''