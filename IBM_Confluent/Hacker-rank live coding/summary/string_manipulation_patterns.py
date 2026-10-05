"""
COMPREHENSIVE STRING MANIPULATION PATTERNS FOR SENIOR DEVELOPER INTERVIEWS
===========================================================================
All string techniques, methods, patterns and edge cases
Optimized for Clio (Legal Tech) - includes text processing, parsing, validation
"""

# ============================================================================
# 1. CORE STRING METHODS & OPERATIONS
# ============================================================================

def string_basics():
    """Essential string methods every developer must know"""

    s = "  Hello World!  "

    # Creation and basic operations
    s1 = "Hello"
    s2 = 'World'
    s3 = """Multi
    line
    string"""
    s4 = r"Raw string\n"  # Raw string (no escape)

    # Length
    length = len(s)  # 15

    # Stripping whitespace
    stripped = s.strip()      # "Hello World!"
    lstripped = s.lstrip()    # "Hello World!  "
    rstripped = s.rstrip()    # "  Hello World!"

    # Case operations
    upper = s.upper()         # "  HELLO WORLD!  "
    lower = s.lower()         # "  hello world!  "
    title = s.title()         # "  Hello World!  "
    capitalize = s.capitalize()  # "  hello world!  "
    swapcase = s.swapcase()   # "  hELLO wORLD!  "

    # Checking case
    is_upper = s.isupper()    # False
    is_lower = s.islower()    # False
    is_title = s.istitle()    # False

    # Searching
    index = s.find("World")   # 8 (returns -1 if not found)
    index2 = s.index("World") # 8 (raises ValueError if not found)
    count = s.count("l")      # 3
    starts = s.startswith("  Hello")  # True
    ends = s.endswith("!  ")  # True

    # Replacing
    replaced = s.replace("World", "Python")  # "  Hello Python!  "
    replaced_n = s.replace("l", "L", 2)  # "  HeLLo World!  " (max 2 replacements)

    # Splitting
    words = s.split()         # ["Hello", "World!"]
    split_by = "a,b,c".split(",")  # ["a", "b", "c"]
    lines = "a\nb\nc".splitlines()  # ["a", "b", "c"]
    rsplit = "a-b-c".rsplit("-", 1)  # ["a-b", "c"] (split from right)

    # Joining
    joined = "-".join(["a", "b", "c"])  # "a-b-c"

    # Checking content
    is_alpha = "abc".isalpha()      # True
    is_digit = "123".isdigit()      # True
    is_alnum = "abc123".isalnum()   # True
    is_space = "   ".isspace()      # True

    # Padding and alignment
    centered = "hi".center(10, "*")  # "****hi****"
    left_just = "hi".ljust(5, "*")   # "hi***"
    right_just = "hi".rjust(5, "*")  # "***hi"
    zfill = "42".zfill(5)            # "00042"

    # Partitioning
    before, sep, after = "hello-world".partition("-")  # ("hello", "-", "world")

    return {
        'stripped': stripped,
        'words': words,
        'replaced': replaced
    }


# ============================================================================
# 2. STRING VALIDATION & CHECKING PATTERNS
# ============================================================================

def is_palindrome(s):
    """Check if string is palindrome (case-insensitive, alphanumeric only)"""
    # Method 1: Two pointers
    left, right = 0, len(s) - 1

    while left < right:
        while left < right and not s[left].isalnum():
            left += 1
        while left < right and not s[right].isalnum():
            right -= 1

        if s[left].lower() != s[right].lower():
            return False

        left += 1
        right -= 1

    return True


def is_palindrome_simple(s):
    """Simple palindrome check"""
    cleaned = ''.join(c.lower() for c in s if c.isalnum())
    return cleaned == cleaned[::-1]


def is_anagram(s1, s2):
    """Check if two strings are anagrams"""
    # Method 1: Sorting
    return sorted(s1) == sorted(s2)


def is_anagram_optimized(s1, s2):
    """Optimized anagram check using Counter"""
    from collections import Counter
    return Counter(s1) == Counter(s2)


def is_rotation(s1, s2):
    """Check if s2 is rotation of s1"""
    return len(s1) == len(s2) and s2 in s1 + s1


def is_subsequence(s, t):
    """Check if s is subsequence of t"""
    i = 0
    for char in t:
        if i < len(s) and char == s[i]:
            i += 1
    return i == len(s)


def valid_parentheses(s):
    """Check if parentheses/brackets are valid"""
    stack = []
    mapping = {')': '(', '}': '{', ']': '['}

    for char in s:
        if char in mapping:
            top = stack.pop() if stack else '#'
            if mapping[char] != top:
                return False
        else:
            stack.append(char)

    return not stack


def is_valid_email(email):
    """Basic email validation"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def is_valid_phone(phone):
    """Validate phone number (US format)"""
    import re
    # Accepts: (123) 456-7890, 123-456-7890, 1234567890
    pattern = r'^(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}$'
    return bool(re.match(pattern, phone))


# ============================================================================
# 3. STRING TRANSFORMATION PATTERNS
# ============================================================================

def reverse_string(s):
    """Reverse entire string"""
    # Method 1: Slicing (most Pythonic)
    return s[::-1]


def reverse_string_in_place(s):
    """Reverse string in-place (list)"""
    s = list(s)
    left, right = 0, len(s) - 1
    while left < right:
        s[left], s[right] = s[right], s[left]
        left += 1
        right -= 1
    return ''.join(s)


def reverse_words(s):
    """Reverse words in string"""
    # Method 1: Built-in
    return ' '.join(s.split()[::-1])


def reverse_words_manual(s):
    """Reverse words manually"""
    words = []
    word = []

    for char in s:
        if char != ' ':
            word.append(char)
        elif word:
            words.append(''.join(word))
            word = []

    if word:
        words.append(''.join(word))

    return ' '.join(reversed(words))


def reverse_words_order_only(s):
    """Reverse word order but keep word characters"""
    words = s.split()
    return ' '.join(words[::-1])


def remove_duplicates(s):
    """Remove duplicate characters while maintaining order"""
    seen = set()
    result = []

    for char in s:
        if char not in seen:
            seen.add(char)
            result.append(char)

    return ''.join(result)


def remove_adjacent_duplicates(s):
    """Remove all adjacent duplicates"""
    stack = []

    for char in s:
        if stack and stack[-1] == char:
            stack.pop()
        else:
            stack.append(char)

    return ''.join(stack)


def compress_string(s):
    """Compress string: 'aaabbc' -> 'a3b2c1'"""
    if not s:
        return ""

    compressed = []
    count = 1

    for i in range(1, len(s)):
        if s[i] == s[i-1]:
            count += 1
        else:
            compressed.append(s[i-1] + str(count))
            count = 1

    compressed.append(s[-1] + str(count))

    result = ''.join(compressed)
    return result if len(result) < len(s) else s


def expand_string(s):
    """Expand compressed string: 'a3b2' -> 'aaabb'"""
    result = []
    i = 0

    while i < len(s):
        char = s[i]
        i += 1
        count = ""
        while i < len(s) and s[i].isdigit():
            count += s[i]
            i += 1
        result.append(char * int(count))

    return ''.join(result)


def to_camel_case(s):
    """Convert to camelCase"""
    words = s.replace('-', '_').split('_')
    return words[0].lower() + ''.join(w.capitalize() for w in words[1:])


def to_snake_case(s):
    """Convert camelCase/PascalCase to snake_case"""
    import re
    s = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', s)
    s = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s)
    return s.lower()


def to_kebab_case(s):
    """Convert to kebab-case"""
    return to_snake_case(s).replace('_', '-')


def title_case_legal(s):
    """
    Title case for legal documents (capitalize first letter of each word,
    except articles, conjunctions, and prepositions unless first word)
    """
    small_words = {'a', 'an', 'and', 'as', 'at', 'but', 'by', 'for',
                   'in', 'of', 'on', 'or', 'the', 'to', 'via'}

    words = s.lower().split()
    result = []

    for i, word in enumerate(words):
        if i == 0 or word not in small_words:
            result.append(word.capitalize())
        else:
            result.append(word)

    return ' '.join(result)


# ============================================================================
# 4. SUBSTRING & PATTERN MATCHING
# ============================================================================

def find_all_occurrences(text, pattern):
    """Find all starting indices of pattern in text"""
    indices = []
    start = 0

    while True:
        index = text.find(pattern, start)
        if index == -1:
            break
        indices.append(index)
        start = index + 1

    return indices


def longest_common_prefix(strs):
    """Find longest common prefix among strings"""
    if not strs:
        return ""

    # Method 1: Horizontal scanning
    prefix = strs[0]
    for s in strs[1:]:
        while not s.startswith(prefix):
            prefix = prefix[:-1]
            if not prefix:
                return ""

    return prefix


def longest_common_prefix_vertical(strs):
    """Vertical scanning approach"""
    if not strs:
        return ""

    for i in range(len(strs[0])):
        char = strs[0][i]
        for s in strs[1:]:
            if i >= len(s) or s[i] != char:
                return strs[0][:i]

    return strs[0]


def longest_substring_without_repeating(s):
    """Longest substring without repeating characters"""
    char_index = {}
    max_len = 0
    start = 0

    for end in range(len(s)):
        if s[end] in char_index and char_index[s[end]] >= start:
            start = char_index[s[end]] + 1

        char_index[s[end]] = end
        max_len = max(max_len, end - start + 1)

    return max_len


def longest_repeating_character_replacement(s, k):
    """
    Longest substring with same char after replacing at most k characters
    """
    from collections import Counter

    char_count = Counter()
    max_len = 0
    max_freq = 0
    left = 0

    for right in range(len(s)):
        char_count[s[right]] += 1
        max_freq = max(max_freq, char_count[s[right]])

        # If window size - max frequency > k, shrink window
        while (right - left + 1) - max_freq > k:
            char_count[s[left]] -= 1
            left += 1

        max_len = max(max_len, right - left + 1)

    return max_len


def is_match_wildcard(s, p):
    """
    Wildcard pattern matching
    '?' matches any single character
    '*' matches any sequence of characters (including empty)
    """
    dp = [[False] * (len(p) + 1) for _ in range(len(s) + 1)]
    dp[0][0] = True

    # Handle patterns starting with *
    for j in range(1, len(p) + 1):
        if p[j-1] == '*':
            dp[0][j] = dp[0][j-1]

    for i in range(1, len(s) + 1):
        for j in range(1, len(p) + 1):
            if p[j-1] == '*':
                dp[i][j] = dp[i-1][j] or dp[i][j-1]
            elif p[j-1] == '?' or s[i-1] == p[j-1]:
                dp[i][j] = dp[i-1][j-1]

    return dp[len(s)][len(p)]


def is_match_regex(s, p):
    """
    Regular expression matching with '.' and '*'
    '.' matches any single character
    '*' matches zero or more of the preceding element
    """
    dp = [[False] * (len(p) + 1) for _ in range(len(s) + 1)]
    dp[0][0] = True

    # Handle patterns like a*, a*b*, etc
    for j in range(2, len(p) + 1):
        if p[j-1] == '*':
            dp[0][j] = dp[0][j-2]

    for i in range(1, len(s) + 1):
        for j in range(1, len(p) + 1):
            if p[j-1] == '.' or p[j-1] == s[i-1]:
                dp[i][j] = dp[i-1][j-1]
            elif p[j-1] == '*':
                dp[i][j] = dp[i][j-2]  # Zero occurrences
                if p[j-2] == '.' or p[j-2] == s[i-1]:
                    dp[i][j] = dp[i][j] or dp[i-1][j]  # One or more occurrences

    return dp[len(s)][len(p)]


def kmp_search(text, pattern):
    """
    KMP (Knuth-Morris-Pratt) pattern matching algorithm
    Time: O(n + m), Space: O(m)
    """
    def compute_lps(pattern):
        """Compute Longest Proper Prefix which is also Suffix"""
        lps = [0] * len(pattern)
        length = 0
        i = 1

        while i < len(pattern):
            if pattern[i] == pattern[length]:
                length += 1
                lps[i] = length
                i += 1
            else:
                if length != 0:
                    length = lps[length - 1]
                else:
                    lps[i] = 0
                    i += 1

        return lps

    if not pattern:
        return 0

    lps = compute_lps(pattern)
    i = j = 0

    while i < len(text):
        if text[i] == pattern[j]:
            i += 1
            j += 1

        if j == len(pattern):
            return i - j  # Found at index i-j
        elif i < len(text) and text[i] != pattern[j]:
            if j != 0:
                j = lps[j - 1]
            else:
                i += 1

    return -1


def rabin_karp(text, pattern):
    """
    Rabin-Karp algorithm for pattern matching using rolling hash
    Average: O(n + m), Worst: O(nm)
    """
    if len(pattern) > len(text):
        return -1

    BASE = 256
    MOD = 101

    pattern_hash = 0
    text_hash = 0
    h = 1

    # h = BASE^(m-1) % MOD
    for _ in range(len(pattern) - 1):
        h = (h * BASE) % MOD

    # Calculate initial hash values
    for i in range(len(pattern)):
        pattern_hash = (BASE * pattern_hash + ord(pattern[i])) % MOD
        text_hash = (BASE * text_hash + ord(text[i])) % MOD

    # Slide pattern over text
    for i in range(len(text) - len(pattern) + 1):
        if pattern_hash == text_hash:
            # Check character by character
            if text[i:i+len(pattern)] == pattern:
                return i

        # Calculate hash for next window
        if i < len(text) - len(pattern):
            text_hash = (BASE * (text_hash - ord(text[i]) * h) +
                        ord(text[i + len(pattern)])) % MOD
            if text_hash < 0:
                text_hash += MOD

    return -1


# ============================================================================
# 5. STRING PARSING & TOKENIZATION
# ============================================================================

def parse_csv_line(line):
    """Parse CSV line handling quoted fields with commas"""
    fields = []
    current_field = []
    in_quotes = False

    for i, char in enumerate(line):
        if char == '"':
            if in_quotes and i + 1 < len(line) and line[i + 1] == '"':
                current_field.append('"')
                continue
            in_quotes = not in_quotes
        elif char == ',' and not in_quotes:
            fields.append(''.join(current_field))
            current_field = []
        else:
            current_field.append(char)

    fields.append(''.join(current_field))
    return fields


def tokenize(text):
    """Simple tokenizer for words"""
    import re
    return re.findall(r'\b\w+\b', text.lower())


def extract_emails(text):
    """Extract all email addresses from text"""
    import re
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.findall(pattern, text)


def extract_urls(text):
    """Extract all URLs from text"""
    import re
    pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    return re.findall(pattern, text)


def extract_phone_numbers(text):
    """Extract phone numbers from text"""
    import re
    pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    return re.findall(pattern, text)


def parse_key_value_pairs(s):
    """Parse key=value pairs: 'name=John age=30' -> {'name': 'John', 'age': '30'}"""
    pairs = s.split()
    result = {}

    for pair in pairs:
        if '=' in pair:
            key, value = pair.split('=', 1)
            result[key] = value

    return result


def parse_json_simple(s):
    """Simple JSON parser (basic objects only)"""
    import json
    try:
        return json.loads(s)
    except json.JSONDecodeError as e:
        return {"error": str(e)}


def split_by_delimiter_with_quotes(s, delimiter=','):
    """Split string by delimiter, respecting quoted sections"""
    parts = []
    current = []
    in_quotes = False

    for char in s:
        if char == '"':
            in_quotes = not in_quotes
            current.append(char)
        elif char == delimiter and not in_quotes:
            parts.append(''.join(current).strip())
            current = []
        else:
            current.append(char)

    if current:
        parts.append(''.join(current).strip())

    return parts


# ============================================================================
# 6. STRING ENCODING & DECODING
# ============================================================================

def encode_base64(s):
    """Encode string to base64"""
    import base64
    return base64.b64encode(s.encode()).decode()


def decode_base64(s):
    """Decode base64 string"""
    import base64
    try:
        return base64.b64decode(s.encode()).decode()
    except Exception as e:
        return f"Error: {e}"


def url_encode(s):
    """URL encode string"""
    from urllib.parse import quote
    return quote(s)


def url_decode(s):
    """URL decode string"""
    from urllib.parse import unquote
    return unquote(s)


def html_encode(s):
    """HTML encode special characters"""
    import html
    return html.escape(s)


def html_decode(s):
    """HTML decode special characters"""
    import html
    return html.unescape(s)


def run_length_encode(s):
    """Run-length encoding: 'aaabbc' -> '3a2b1c'"""
    if not s:
        return ""

    encoded = []
    count = 1

    for i in range(1, len(s)):
        if s[i] == s[i-1]:
            count += 1
        else:
            encoded.append(f"{count}{s[i-1]}")
            count = 1

    encoded.append(f"{count}{s[-1]}")
    return ''.join(encoded)


def run_length_decode(s):
    """Run-length decoding: '3a2b1c' -> 'aaabbc'"""
    decoded = []
    i = 0

    while i < len(s):
        count = ""
        while i < len(s) and s[i].isdigit():
            count += s[i]
            i += 1
        if i < len(s):
            decoded.append(s[i] * int(count))
            i += 1

    return ''.join(decoded)


def caesar_cipher(s, shift):
    """Caesar cipher encryption"""
    result = []

    for char in s:
        if char.isalpha():
            start = ord('A') if char.isupper() else ord('a')
            shifted = (ord(char) - start + shift) % 26 + start
            result.append(chr(shifted))
        else:
            result.append(char)

    return ''.join(result)


def rot13(s):
    """ROT13 encoding"""
    return caesar_cipher(s, 13)


# ============================================================================
# 7. STRING COMPARISON & SIMILARITY
# ============================================================================

def hamming_distance(s1, s2):
    """Hamming distance (number of differing characters)"""
    if len(s1) != len(s2):
        raise ValueError("Strings must be same length")

    return sum(c1 != c2 for c1, c2 in zip(s1, s2))


def levenshtein_distance(s1, s2):
    """
    Levenshtein distance (edit distance)
    Minimum edits (insert, delete, replace) to transform s1 to s2
    """
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i-1] == s2[j-1]:
                dp[i][j] = dp[i-1][j-1]
            else:
                dp[i][j] = 1 + min(
                    dp[i-1][j],      # Delete
                    dp[i][j-1],      # Insert
                    dp[i-1][j-1]     # Replace
                )

    return dp[m][n]


def longest_common_substring(s1, s2):
    """Find longest common substring"""
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    max_len = 0
    ending_index = 0

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i-1] == s2[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
                if dp[i][j] > max_len:
                    max_len = dp[i][j]
                    ending_index = i

    return s1[ending_index - max_len:ending_index]


def similarity_ratio(s1, s2):
    """Calculate similarity ratio (0 to 1)"""
    from difflib import SequenceMatcher
    return SequenceMatcher(None, s1, s2).ratio()


# ============================================================================
# 8. ADVANCED STRING ALGORITHMS
# ============================================================================

def manacher_algorithm(s):
    """
    Manacher's algorithm - find longest palindrome in O(n)
    """
    # Transform string to handle even/odd length palindromes uniformly
    T = '#'.join(f'^{s}$')
    n = len(T)
    P = [0] * n
    C = R = 0

    for i in range(1, n - 1):
        if R > i:
            P[i] = min(R - i, P[2 * C - i])

        # Try to expand palindrome centered at i
        while T[i + 1 + P[i]] == T[i - 1 - P[i]]:
            P[i] += 1

        # Update center and right boundary
        if i + P[i] > R:
            C, R = i, i + P[i]

    # Find the maximum element in P
    max_len, center_index = max((n, i) for i, n in enumerate(P))

    start = (center_index - max_len) // 2
    return s[start:start + max_len]


def z_algorithm(s):
    """
    Z algorithm - compute Z array where Z[i] is length of longest substring
    starting from i which is also prefix of s
    """
    n = len(s)
    Z = [0] * n
    Z[0] = n

    l = r = 0
    for i in range(1, n):
        if i > r:
            l = r = i
            while r < n and s[r - l] == s[r]:
                r += 1
            Z[i] = r - l
            r -= 1
        else:
            k = i - l
            if Z[k] < r - i + 1:
                Z[i] = Z[k]
            else:
                l = i
                while r < n and s[r - l] == s[r]:
                    r += 1
                Z[i] = r - l
                r -= 1

    return Z


def suffix_array_construction(s):
    """
    Build suffix array - sorted array of all suffixes
    """
    suffixes = [(s[i:], i) for i in range(len(s))]
    suffixes.sort()
    return [suffix[1] for suffix in suffixes]


def lcp_array(s, suffix_arr):
    """
    Longest Common Prefix array for suffix array
    """
    n = len(s)
    rank = [0] * n
    lcp = [0] * n

    for i in range(n):
        rank[suffix_arr[i]] = i

    k = 0
    for i in range(n):
        if rank[i] == n - 1:
            k = 0
            continue

        j = suffix_arr[rank[i] + 1]
        while i + k < n and j + k < n and s[i + k] == s[j + k]:
            k += 1

        lcp[rank[i]] = k
        if k > 0:
            k -= 1

    return lcp


# ============================================================================
# 9. STRING MANIPULATION FOR LEGAL TECH / DOCUMENT PROCESSING
# ============================================================================

def extract_case_citations(text):
    """
    Extract legal case citations
    Format: Number Name Number (Year)
    Example: 123 F.3d 456 (2020)
    """
    import re
    pattern = r'\d+\s+[A-Z][a-z.]+\s+\d+\s+\(\d{4}\)'
    return re.findall(pattern, text)


def redact_pii(text):
    """
    Redact personally identifiable information
    Replace SSN, credit cards, emails with [REDACTED]
    """
    import re

    # SSN pattern
    text = re.sub(r'\d{3}-\d{2}-\d{4}', '[SSN-REDACTED]', text)

    # Credit card pattern
    text = re.sub(r'\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}', '[CC-REDACTED]', text)

    # Email pattern
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                  '[EMAIL-REDACTED]', text)

    # Phone pattern
    text = re.sub(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', '[PHONE-REDACTED]', text)

    return text


def normalize_legal_text(text):
    """
    Normalize legal document text
    - Remove extra whitespace
    - Standardize quotes
    - Fix common issues
    """
    # Replace multiple spaces with single space
    text = re.sub(r'\s+', ' ', text)

    # Standardize quotes
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace(''', "'").replace(''', "'")

    # Remove leading/trailing whitespace
    text = text.strip()

    # Fix spacing around punctuation
    text = re.sub(r'\s+([.,;:!?])', r'\1', text)

    return text


def extract_section_numbers(text):
    """
    Extract section/article numbers from legal text
    Examples: Section 1.2.3, Article IV, § 123
    """
    import re
    patterns = [
        r'Section\s+[\d.]+',
        r'Article\s+[IVX]+',
        r'§\s*\d+',
        r'\d+\s+U\.S\.C\.\s*§\s*\d+'
    ]

    results = []
    for pattern in patterns:
        results.extend(re.findall(pattern, text, re.IGNORECASE))

    return results


def parse_date_formats(text):
    """
    Parse various date formats from legal documents
    Handles: MM/DD/YYYY, Month DD, YYYY, DD Month YYYY, etc.
    """
    import re
    from datetime import datetime

    patterns = [
        (r'\d{1,2}/\d{1,2}/\d{4}', '%m/%d/%Y'),
        (r'\d{1,2}-\d{1,2}-\d{4}', '%m-%d-%Y'),
        (r'[A-Z][a-z]+\s+\d{1,2},?\s+\d{4}', '%B %d, %Y'),
        (r'\d{1,2}\s+[A-Z][a-z]+\s+\d{4}', '%d %B %Y'),
    ]

    dates = []
    for pattern, date_format in patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            try:
                parsed = datetime.strptime(match, date_format)
                dates.append(parsed)
            except:
                pass

    return dates


def split_into_sentences(text):
    """
    Split text into sentences (handles abbreviations)
    """
    import re

    # Common abbreviations that shouldn't trigger sentence breaks
    abbreviations = ['Dr.', 'Mr.', 'Mrs.', 'Ms.', 'Prof.', 'Sr.', 'Jr.',
                     'U.S.', 'U.K.', 'e.g.', 'i.e.', 'etc.', 'vs.']

    # Replace abbreviations temporarily
    for i, abbr in enumerate(abbreviations):
        text = text.replace(abbr, f'<ABBR{i}>')

    # Split on sentence boundaries
    sentences = re.split(r'[.!?]+\s+', text)

    # Restore abbreviations
    for i, abbr in enumerate(abbreviations):
        sentences = [s.replace(f'<ABBR{i}>', abbr) for s in sentences]

    return [s.strip() for s in sentences if s.strip()]


def extract_dollar_amounts(text):
    """Extract dollar amounts from text"""
    import re
    pattern = r'\$[\d,]+\.?\d*'
    amounts = re.findall(pattern, text)
    return [float(a.replace('$', '').replace(',', '')) for a in amounts]


def generate_document_id(title, date=None):
    """
    Generate unique document identifier from title
    Format: lowercase, hyphens, optional date prefix
    """
    import re
    from datetime import datetime

    # Convert to lowercase and replace spaces
    doc_id = title.lower().strip()

    # Remove special characters
    doc_id = re.sub(r'[^a-z0-9\s-]', '', doc_id)

    # Replace spaces with hyphens
    doc_id = re.sub(r'\s+', '-', doc_id)

    # Add date prefix if provided
    if date:
        if isinstance(date, str):
            date = datetime.fromisoformat(date)
        date_str = date.strftime('%Y%m%d')
        doc_id = f"{date_str}-{doc_id}"

    return doc_id


# ============================================================================
# 10. STRING UTILITIES & HELPERS
# ============================================================================

def word_wrap(text, width):
    """Word wrap text to specified width"""
    words = text.split()
    lines = []
    current_line = []
    current_length = 0

    for word in words:
        if current_length + len(word) + len(current_line) <= width:
            current_line.append(word)
            current_length += len(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
            current_length = len(word)

    if current_line:
        lines.append(' '.join(current_line))

    return lines


def truncate_with_ellipsis(text, max_length):
    """Truncate string with ellipsis"""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + '...'


def remove_html_tags(html):
    """Remove HTML tags from string"""
    import re
    return re.sub(r'<[^>]+>', '', html)


def string_to_int_hash(s):
    """Generate integer hash from string"""
    return hash(s) & 0x7FFFFFFF  # Keep positive


def group_anagrams(strs):
    """Group strings that are anagrams"""
    from collections import defaultdict

    groups = defaultdict(list)
    for s in strs:
        key = ''.join(sorted(s))
        groups[key].append(s)

    return list(groups.values())


def format_file_size(size_bytes):
    """Format bytes into human-readable string"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def pluralize(word, count):
    """Simple pluralization"""
    if count == 1:
        return word

    # Simple rules
    if word.endswith('y'):
        return word[:-1] + 'ies'
    elif word.endswith(('s', 'x', 'z', 'ch', 'sh')):
        return word + 'es'
    else:
        return word + 's'


def natural_sort_key(s):
    """
    Key function for natural sorting
    Example: ['file1', 'file10', 'file2'] -> ['file1', 'file2', 'file10']
    """
    import re
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split(r'(\d+)', s)]


# ============================================================================
# COMPREHENSIVE TEST EXAMPLES
# ============================================================================

def run_all_examples():
    """Run examples of all string manipulation patterns"""

    print("=" * 70)
    print("STRING MANIPULATION PATTERNS - EXAMPLES")
    print("=" * 70)

    # Palindrome
    print("\n1. PALINDROME CHECK:")
    print(f"  'racecar' is palindrome: {is_palindrome('racecar')}")
    print(f"  'A man, a plan, a canal: Panama': {is_palindrome('A man, a plan, a canal: Panama')}")

    # Anagram
    print("\n2. ANAGRAM CHECK:")
    print(f"  'listen' and 'silent': {is_anagram('listen', 'silent')}")

    # String reversal
    print("\n3. STRING REVERSAL:")
    print(f"  Reverse 'hello': {reverse_string('hello')}")
    print(f"  Reverse words 'hello world': {reverse_words('hello world')}")

    # Compression
    print("\n4. STRING COMPRESSION:")
    print(f"  Compress 'aaabbbccc': {compress_string('aaabbbccc')}")

    # Substring
    print("\n5. LONGEST SUBSTRING:")
    s = "abcabcbb"
    print(f"  Longest substring without repeat in '{s}': {longest_substring_without_repeating(s)}")

    # Pattern matching
    print("\n6. PATTERN MATCHING:")
    text = "hello world hello"
    pattern = "hello"
    print(f"  Find all '{pattern}' in '{text}': {find_all_occurrences(text, pattern)}")

    # Case conversion
    print("\n7. CASE CONVERSION:")
    print(f"  'helloWorld' to snake_case: {to_snake_case('helloWorld')}")
    print(f"  'hello_world' to camelCase: {to_camel_case('hello_world')}")

    # Legal text processing
    print("\n8. LEGAL TEXT PROCESSING:")
    legal_text = "Pursuant to Section 1.2.3 of the Agreement dated 12/15/2023"
    print(f"  Extract sections: {extract_section_numbers(legal_text)}")

    # PII Redaction
    print("\n9. PII REDACTION:")
    text_with_pii = "Contact: john@example.com, SSN: 123-45-6789"
    print(f"  Redacted: {redact_pii(text_with_pii)}")

    # Edit distance
    print("\n10. EDIT DISTANCE:")
    print(f"  'kitten' -> 'sitting': {levenshtein_distance('kitten', 'sitting')} edits")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    run_all_examples()

    print("\n" + "=" * 70)
    print("STRING MANIPULATION QUICK REFERENCE")
    print("=" * 70)
    print("""
    1. BASIC OPERATIONS: strip, split, join, replace, find
    2. VALIDATION: palindrome, anagram, parentheses, email, phone
    3. TRANSFORMATION: reverse, remove duplicates, compress, case conversion
    4. PATTERN MATCHING: KMP, Rabin-Karp, regex, wildcard
    5. PARSING: CSV, JSON, tokenization, date extraction
    6. ENCODING: base64, URL encode, HTML encode, run-length, Caesar cipher
    7. SIMILARITY: Hamming, Levenshtein, LCS, similarity ratio
    8. ADVANCED: Manacher, Z-algorithm, suffix array
    9. LEGAL TECH: citations, PII redaction, section extraction, document ID
    10. UTILITIES: word wrap, truncate, HTML removal, natural sort

    Time Complexities:
    - Most basic operations: O(n)
    - KMP pattern matching: O(n + m)
    - Rabin-Karp: O(n + m) average
    - Manacher (longest palindrome): O(n)
    - Edit distance: O(mn)
    - Suffix array: O(n log n) or O(n) with advanced methods

    Space Complexities:
    - In-place operations: O(1)
    - With auxiliary storage: O(n)
    - DP solutions: O(mn) typically
    """)
