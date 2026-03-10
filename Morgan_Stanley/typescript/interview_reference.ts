// ============================================================================
// TYPESCRIPT INTERVIEW REFERENCE GUIDE
// Morgan Stanley Interview Preparation
// ============================================================================

// ============================================================================
// 1. STRING MANIPULATION
// ============================================================================

// Basic String Methods
function stringBasics() {
  const str = "Hello World";

  // Length
  console.log(str.length); // 11

  // Access characters
  console.log(str[0]); // 'H'
  console.log(str.charAt(0)); // 'H'
  console.log(str.charCodeAt(0)); // 72 (ASCII code)

  // Case conversion
  console.log(str.toLowerCase()); // "hello world"
  console.log(str.toUpperCase()); // "HELLO WORLD"

  // Substring operations
  console.log(str.substring(0, 5)); // "Hello"
  console.log(str.slice(0, 5)); // "Hello"
  console.log(str.slice(-5)); // "World" (negative index from end)

  // Search operations
  console.log(str.indexOf("o")); // 4 (first occurrence)
  console.log(str.lastIndexOf("o")); // 7 (last occurrence)
  console.log(str.includes("World")); // true
  console.log(str.startsWith("Hello")); // true
  console.log(str.endsWith("World")); // true

  // Split and join
  console.log(str.split(" ")); // ["Hello", "World"]
  console.log(["Hello", "World"].join(" ")); // "Hello World"

  // Replace
  console.log(str.replace("World", "TypeScript")); // "Hello TypeScript"
  console.log(str.replaceAll("o", "0")); // "Hell0 W0rld"

  // Trim whitespace
  console.log("  hello  ".trim()); // "hello"
  console.log("  hello  ".trimStart()); // "hello  "
  console.log("  hello  ".trimEnd()); // "  hello"

  // Repeat and pad
  console.log("ha".repeat(3)); // "hahaha"
  console.log("5".padStart(3, "0")); // "005"
  console.log("5".padEnd(3, "0")); // "500"
}

// String to Array conversions
function stringToArray() {
  const str = "hello";

  // Convert to character array
  const arr1 = str.split(""); // ['h', 'e', 'l', 'l', 'o']
  const arr2 = Array.from(str); // ['h', 'e', 'l', 'l', 'o']
  const arr3 = [...str]; // ['h', 'e', 'l', 'l', 'o']

  // Back to string
  console.log(arr1.join("")); // "hello"
}

// Template literals
function templateLiterals() {
  const name = "Alice";
  const age = 25;

  // Multi-line and interpolation
  const message = `Hello ${name},
You are ${age} years old.
Next year you'll be ${age + 1}.`;

  console.log(message);
}

// ============================================================================
// 2. ARRAY OPERATIONS
// ============================================================================

// Array Creation
function arrayCreation() {
  // Different ways to create arrays
  const arr1 = [1, 2, 3];
  const arr2 = new Array(5); // Empty array with length 5
  const arr3 = Array.from({ length: 5 }, (_, i) => i); // [0, 1, 2, 3, 4]
  const arr4 = Array(5).fill(0); // [0, 0, 0, 0, 0]

  // 2D array
  const matrix = Array.from({ length: 3 }, () => Array(3).fill(0));
}

// Array Methods - Adding/Removing
function arrayAddRemove() {
  const arr = [1, 2, 3];

  // Add to end
  arr.push(4); // [1, 2, 3, 4]

  // Remove from end
  const last = arr.pop(); // last = 4, arr = [1, 2, 3]

  // Add to beginning
  arr.unshift(0); // [0, 1, 2, 3]

  // Remove from beginning
  const first = arr.shift(); // first = 0, arr = [1, 2, 3]

  // Remove/Add at specific position
  arr.splice(1, 1); // Remove 1 element at index 1
  arr.splice(1, 0, 5, 6); // Insert 5, 6 at index 1

  // Slice (doesn't modify original)
  const sliced = arr.slice(0, 2); // First 2 elements
}

// Array Iteration Methods
function arrayIteration() {
  const numbers = [1, 2, 3, 4, 5];

  // forEach - iterate without return
  numbers.forEach((num, index) => {
    console.log(`Index ${index}: ${num}`);
  });

  // map - transform each element
  const doubled = numbers.map(num => num * 2); // [2, 4, 6, 8, 10]

  // filter - keep elements that pass test
  const evens = numbers.filter(num => num % 2 === 0); // [2, 4]

  // reduce - accumulate to single value
  const sum = numbers.reduce((acc, num) => acc + num, 0); // 15

  // find - first element that passes test
  const firstEven = numbers.find(num => num % 2 === 0); // 2

  // findIndex - index of first element that passes test
  const firstEvenIndex = numbers.findIndex(num => num % 2 === 0); // 1

  // some - check if any element passes test
  const hasEven = numbers.some(num => num % 2 === 0); // true

  // every - check if all elements pass test
  const allPositive = numbers.every(num => num > 0); // true
}

// Array Search and Check
function arraySearch() {
  const arr = [1, 2, 3, 4, 5, 3];

  // indexOf - first occurrence
  console.log(arr.indexOf(3)); // 2

  // lastIndexOf - last occurrence
  console.log(arr.lastIndexOf(3)); // 5

  // includes - check if element exists
  console.log(arr.includes(3)); // true
}

// Array Sorting and Reversing
function arraySorting() {
  const arr = [3, 1, 4, 1, 5, 9, 2, 6];

  // Sort (modifies original)
  arr.sort((a, b) => a - b); // Ascending
  arr.sort((a, b) => b - a); // Descending

  // Reverse
  arr.reverse();

  // Sort strings
  const words = ["banana", "apple", "cherry"];
  words.sort(); // Alphabetical
}

// Array Destructuring and Spread
function arrayDestructuring() {
  const arr = [1, 2, 3, 4, 5];

  // Destructuring
  const [first, second, ...rest] = arr; // first=1, second=2, rest=[3,4,5]

  // Spread operator
  const arr2 = [...arr]; // Copy array
  const combined = [...arr, 6, 7, 8]; // Combine

  // Math with spread
  console.log(Math.max(...arr)); // 5
  console.log(Math.min(...arr)); // 1
}

// ============================================================================
// 3. LOOPS AND ITERATION
// ============================================================================

function loopExamples() {
  const arr = [1, 2, 3, 4, 5];
  const obj = { a: 1, b: 2, c: 3 };

  // Traditional for loop
  for (let i = 0; i < arr.length; i++) {
    console.log(arr[i]);
  }

  // for...of (for iterables - arrays, strings, sets, maps)
  for (const num of arr) {
    console.log(num);
  }

  // for...in (for object keys)
  for (const key in obj) {
    console.log(`${key}: ${obj[key]}`);
  }

  // while loop
  let i = 0;
  while (i < arr.length) {
    console.log(arr[i]);
    i++;
  }

  // do...while loop
  i = 0;
  do {
    console.log(arr[i]);
    i++;
  } while (i < arr.length);

  // forEach method
  arr.forEach((num, index) => {
    console.log(`Index ${index}: ${num}`);
  });

  // Loop with break and continue
  for (let i = 0; i < 10; i++) {
    if (i === 3) continue; // Skip 3
    if (i === 7) break; // Stop at 7
    console.log(i);
  }
}

// ============================================================================
// 4. COMMON CODING PATTERNS
// ============================================================================

// Pattern 1: Two Pointers
function twoPointersPattern() {
  // Example: Check if string is palindrome
  function isPalindrome(s: string): boolean {
    let left = 0;
    let right = s.length - 1;

    while (left < right) {
      if (s[left] !== s[right]) {
        return false;
      }
      left++;
      right--;
    }
    return true;
  }

  // Example: Two Sum on sorted array
  function twoSumSorted(nums: number[], target: number): number[] {
    let left = 0;
    let right = nums.length - 1;

    while (left < right) {
      const sum = nums[left] + nums[right];
      if (sum === target) {
        return [left, right];
      } else if (sum < target) {
        left++;
      } else {
        right--;
      }
    }
    return [];
  }

  // Example: Remove duplicates from sorted array
  function removeDuplicates(nums: number[]): number {
    if (nums.length === 0) return 0;

    let slow = 0;
    for (let fast = 1; fast < nums.length; fast++) {
      if (nums[fast] !== nums[slow]) {
        slow++;
        nums[slow] = nums[fast];
      }
    }
    return slow + 1;
  }
}

// Pattern 2: Sliding Window
function slidingWindowPattern() {
  // Example: Maximum sum subarray of size k
  function maxSubarraySum(arr: number[], k: number): number {
    let maxSum = 0;
    let windowSum = 0;

    // First window
    for (let i = 0; i < k; i++) {
      windowSum += arr[i];
    }
    maxSum = windowSum;

    // Slide window
    for (let i = k; i < arr.length; i++) {
      windowSum = windowSum - arr[i - k] + arr[i];
      maxSum = Math.max(maxSum, windowSum);
    }

    return maxSum;
  }

  // Example: Longest substring without repeating characters
  function lengthOfLongestSubstring(s: string): number {
    const charSet = new Set<string>();
    let left = 0;
    let maxLength = 0;

    for (let right = 0; right < s.length; right++) {
      while (charSet.has(s[right])) {
        charSet.delete(s[left]);
        left++;
      }
      charSet.add(s[right]);
      maxLength = Math.max(maxLength, right - left + 1);
    }

    return maxLength;
  }
}

// Pattern 3: Hash Map / Hash Set
function hashMapPattern() {
  // Example: Two Sum
  function twoSum(nums: number[], target: number): number[] {
    const map = new Map<number, number>();

    for (let i = 0; i < nums.length; i++) {
      const complement = target - nums[i];
      if (map.has(complement)) {
        return [map.get(complement)!, i];
      }
      map.set(nums[i], i);
    }

    return [];
  }

  // Example: Find first non-repeating character
  function firstNonRepeatingChar(s: string): string | null {
    const charCount = new Map<string, number>();

    // Count frequencies
    for (const char of s) {
      charCount.set(char, (charCount.get(char) || 0) + 1);
    }

    // Find first with count 1
    for (const char of s) {
      if (charCount.get(char) === 1) {
        return char;
      }
    }

    return null;
  }

  // Example: Group anagrams
  function groupAnagrams(strs: string[]): string[][] {
    const map = new Map<string, string[]>();

    for (const str of strs) {
      const sorted = str.split("").sort().join("");
      if (!map.has(sorted)) {
        map.set(sorted, []);
      }
      map.get(sorted)!.push(str);
    }

    return Array.from(map.values());
  }
}

// Pattern 4: Frequency Counter
function frequencyCounterPattern() {
  // Example: Valid anagram
  function isAnagram(s: string, t: string): boolean {
    if (s.length !== t.length) return false;

    const count = new Map<string, number>();

    for (const char of s) {
      count.set(char, (count.get(char) || 0) + 1);
    }

    for (const char of t) {
      if (!count.has(char)) return false;
      count.set(char, count.get(char)! - 1);
      if (count.get(char)! < 0) return false;
    }

    return true;
  }

  // Using array for lowercase letters
  function isAnagramArray(s: string, t: string): boolean {
    if (s.length !== t.length) return false;

    const count = new Array(26).fill(0);

    for (let i = 0; i < s.length; i++) {
      count[s.charCodeAt(i) - 97]++;
      count[t.charCodeAt(i) - 97]--;
    }

    return count.every(c => c === 0);
  }
}

// Pattern 5: Stack Pattern
function stackPattern() {
  // Example: Valid parentheses
  function isValidParentheses(s: string): boolean {
    const stack: string[] = [];
    const pairs: { [key: string]: string } = {
      ")": "(",
      "}": "{",
      "]": "["
    };

    for (const char of s) {
      if (char === "(" || char === "{" || char === "[") {
        stack.push(char);
      } else {
        if (stack.length === 0 || stack.pop() !== pairs[char]) {
          return false;
        }
      }
    }

    return stack.length === 0;
  }

  // Example: Next greater element
  function nextGreaterElement(nums: number[]): number[] {
    const result = new Array(nums.length).fill(-1);
    const stack: number[] = [];

    for (let i = 0; i < nums.length; i++) {
      while (stack.length > 0 && nums[stack[stack.length - 1]] < nums[i]) {
        const idx = stack.pop()!;
        result[idx] = nums[i];
      }
      stack.push(i);
    }

    return result;
  }
}

// Pattern 6: Binary Search
function binarySearchPattern() {
  // Basic binary search
  function binarySearch(arr: number[], target: number): number {
    let left = 0;
    let right = arr.length - 1;

    while (left <= right) {
      const mid = Math.floor((left + right) / 2);

      if (arr[mid] === target) {
        return mid;
      } else if (arr[mid] < target) {
        left = mid + 1;
      } else {
        right = mid - 1;
      }
    }

    return -1;
  }

  // Find first occurrence
  function findFirst(arr: number[], target: number): number {
    let left = 0;
    let right = arr.length - 1;
    let result = -1;

    while (left <= right) {
      const mid = Math.floor((left + right) / 2);

      if (arr[mid] === target) {
        result = mid;
        right = mid - 1; // Continue searching left
      } else if (arr[mid] < target) {
        left = mid + 1;
      } else {
        right = mid - 1;
      }
    }

    return result;
  }

  // Find insert position
  function searchInsert(nums: number[], target: number): number {
    let left = 0;
    let right = nums.length - 1;

    while (left <= right) {
      const mid = Math.floor((left + right) / 2);

      if (nums[mid] === target) {
        return mid;
      } else if (nums[mid] < target) {
        left = mid + 1;
      } else {
        right = mid - 1;
      }
    }

    return left;
  }
}

// Pattern 7: Recursion and Backtracking
function recursionPattern() {
  // Example: Generate all permutations
  function permute(nums: number[]): number[][] {
    const result: number[][] = [];

    function backtrack(current: number[], remaining: number[]) {
      if (remaining.length === 0) {
        result.push([...current]);
        return;
      }

      for (let i = 0; i < remaining.length; i++) {
        current.push(remaining[i]);
        backtrack(current, [...remaining.slice(0, i), ...remaining.slice(i + 1)]);
        current.pop();
      }
    }

    backtrack([], nums);
    return result;
  }

  // Example: Generate all subsets
  function subsets(nums: number[]): number[][] {
    const result: number[][] = [];

    function backtrack(start: number, current: number[]) {
      result.push([...current]);

      for (let i = start; i < nums.length; i++) {
        current.push(nums[i]);
        backtrack(i + 1, current);
        current.pop();
      }
    }

    backtrack(0, []);
    return result;
  }

  // Example: Fibonacci
  function fibonacci(n: number): number {
    if (n <= 1) return n;
    return fibonacci(n - 1) + fibonacci(n - 2);
  }

  // Fibonacci with memoization
  function fibonacciMemo(n: number, memo: Map<number, number> = new Map()): number {
    if (n <= 1) return n;
    if (memo.has(n)) return memo.get(n)!;

    const result = fibonacciMemo(n - 1, memo) + fibonacciMemo(n - 2, memo);
    memo.set(n, result);
    return result;
  }
}

// Pattern 8: Dynamic Programming
function dynamicProgrammingPattern() {
  // Example: Climbing stairs
  function climbStairs(n: number): number {
    if (n <= 2) return n;

    const dp = new Array(n + 1);
    dp[1] = 1;
    dp[2] = 2;

    for (let i = 3; i <= n; i++) {
      dp[i] = dp[i - 1] + dp[i - 2];
    }

    return dp[n];
  }

  // Example: Maximum subarray sum (Kadane's algorithm)
  function maxSubArray(nums: number[]): number {
    let maxSum = nums[0];
    let currentSum = nums[0];

    for (let i = 1; i < nums.length; i++) {
      currentSum = Math.max(nums[i], currentSum + nums[i]);
      maxSum = Math.max(maxSum, currentSum);
    }

    return maxSum;
  }

  // Example: Coin change
  function coinChange(coins: number[], amount: number): number {
    const dp = new Array(amount + 1).fill(Infinity);
    dp[0] = 0;

    for (let i = 1; i <= amount; i++) {
      for (const coin of coins) {
        if (i - coin >= 0) {
          dp[i] = Math.min(dp[i], dp[i - coin] + 1);
        }
      }
    }

    return dp[amount] === Infinity ? -1 : dp[amount];
  }
}

// Pattern 9: Matrix Traversal
function matrixPattern() {
  // Example: Spiral order
  function spiralOrder(matrix: number[][]): number[] {
    const result: number[] = [];
    if (matrix.length === 0) return result;

    let top = 0;
    let bottom = matrix.length - 1;
    let left = 0;
    let right = matrix[0].length - 1;

    while (top <= bottom && left <= right) {
      // Right
      for (let i = left; i <= right; i++) {
        result.push(matrix[top][i]);
      }
      top++;

      // Down
      for (let i = top; i <= bottom; i++) {
        result.push(matrix[i][right]);
      }
      right--;

      // Left
      if (top <= bottom) {
        for (let i = right; i >= left; i--) {
          result.push(matrix[bottom][i]);
        }
        bottom--;
      }

      // Up
      if (left <= right) {
        for (let i = bottom; i >= top; i--) {
          result.push(matrix[i][left]);
        }
        left++;
      }
    }

    return result;
  }

  // Example: Rotate matrix 90 degrees
  function rotate(matrix: number[][]): void {
    const n = matrix.length;

    // Transpose
    for (let i = 0; i < n; i++) {
      for (let j = i; j < n; j++) {
        [matrix[i][j], matrix[j][i]] = [matrix[j][i], matrix[i][j]];
      }
    }

    // Reverse each row
    for (let i = 0; i < n; i++) {
      matrix[i].reverse();
    }
  }
}

// Pattern 10: Linked List Operations
class ListNode {
  val: number;
  next: ListNode | null;

  constructor(val?: number, next?: ListNode | null) {
    this.val = val === undefined ? 0 : val;
    this.next = next === undefined ? null : next;
  }
}

function linkedListPattern() {
  // Reverse linked list
  function reverseList(head: ListNode | null): ListNode | null {
    let prev: ListNode | null = null;
    let curr = head;

    while (curr !== null) {
      const next = curr.next;
      curr.next = prev;
      prev = curr;
      curr = next;
    }

    return prev;
  }

  // Detect cycle
  function hasCycle(head: ListNode | null): boolean {
    let slow = head;
    let fast = head;

    while (fast !== null && fast.next !== null) {
      slow = slow!.next;
      fast = fast.next.next;

      if (slow === fast) {
        return true;
      }
    }

    return false;
  }

  // Merge two sorted lists
  function mergeTwoLists(l1: ListNode | null, l2: ListNode | null): ListNode | null {
    const dummy = new ListNode(0);
    let current = dummy;

    while (l1 !== null && l2 !== null) {
      if (l1.val < l2.val) {
        current.next = l1;
        l1 = l1.next;
      } else {
        current.next = l2;
        l2 = l2.next;
      }
      current = current.next;
    }

    current.next = l1 !== null ? l1 : l2;

    return dummy.next;
  }
}

// ============================================================================
// 5. TYPESCRIPT SPECIFIC FEATURES
// ============================================================================

// Type Annotations
function typeAnnotations() {
  // Basic types
  let num: number = 42;
  let str: string = "hello";
  let bool: boolean = true;
  let arr: number[] = [1, 2, 3];
  let tuple: [string, number] = ["age", 25];

  // Function types
  const add: (a: number, b: number) => number = (a, b) => a + b;

  // Union types
  let id: string | number = 123;

  // Type aliases
  type Point = { x: number; y: number };
  const point: Point = { x: 10, y: 20 };

  // Interfaces
  interface User {
    name: string;
    age: number;
    email?: string; // Optional property
  }

  const user: User = { name: "Alice", age: 25 };
}

// Generics
function genericsExamples() {
  // Generic function
  function identity<T>(arg: T): T {
    return arg;
  }

  // Generic array function
  function getFirstElement<T>(arr: T[]): T | undefined {
    return arr[0];
  }

  // Generic class
  class Queue<T> {
    private items: T[] = [];

    enqueue(item: T): void {
      this.items.push(item);
    }

    dequeue(): T | undefined {
      return this.items.shift();
    }
  }

  const numberQueue = new Queue<number>();
  numberQueue.enqueue(1);
  numberQueue.enqueue(2);
}

// Utility Types
function utilityTypes() {
  interface User {
    name: string;
    age: number;
    email: string;
  }

  // Partial - all properties optional
  type PartialUser = Partial<User>;

  // Required - all properties required
  type RequiredUser = Required<User>;

  // Pick - select specific properties
  type UserNameAge = Pick<User, "name" | "age">;

  // Omit - exclude specific properties
  type UserWithoutEmail = Omit<User, "email">;

  // Record - create object type with specific keys
  type Scores = Record<string, number>;
  const scores: Scores = { math: 90, english: 85 };
}

// ============================================================================
// 6. COMMON HELPER FUNCTIONS
// ============================================================================

// Number helpers
function numberHelpers() {
  // Check if number is integer
  Number.isInteger(4.5); // false

  // Parse numbers
  parseInt("123"); // 123
  parseFloat("123.45"); // 123.45

  // Convert to fixed decimal places
  const num = 123.456;
  num.toFixed(2); // "123.46"

  // Check if NaN
  Number.isNaN(NaN); // true

  // Math operations
  Math.abs(-5); // 5
  Math.ceil(4.3); // 5
  Math.floor(4.7); // 4
  Math.round(4.5); // 5
  Math.max(1, 2, 3); // 3
  Math.min(1, 2, 3); // 1
  Math.pow(2, 3); // 8
  Math.sqrt(16); // 4
}

// Object helpers
function objectHelpers() {
  const obj = { a: 1, b: 2, c: 3 };

  // Get keys, values, entries
  Object.keys(obj); // ['a', 'b', 'c']
  Object.values(obj); // [1, 2, 3]
  Object.entries(obj); // [['a', 1], ['b', 2], ['c', 3]]

  // Check if property exists
  "a" in obj; // true
  obj.hasOwnProperty("a"); // true

  // Merge objects
  const obj2 = { d: 4 };
  const merged = { ...obj, ...obj2 }; // { a: 1, b: 2, c: 3, d: 4 }
  const merged2 = Object.assign({}, obj, obj2);

  // Clone object
  const clone = { ...obj };
  const deepClone = JSON.parse(JSON.stringify(obj));
}

// Set and Map
function setMapExamples() {
  // Set - unique values
  const set = new Set<number>();
  set.add(1);
  set.add(2);
  set.add(1); // Ignored, already exists
  set.has(1); // true
  set.delete(1);
  set.size; // 1

  // Iterate set
  for (const value of set) {
    console.log(value);
  }

  // Map - key-value pairs
  const map = new Map<string, number>();
  map.set("a", 1);
  map.set("b", 2);
  map.get("a"); // 1
  map.has("a"); // true
  map.delete("a");
  map.size; // 1

  // Iterate map
  for (const [key, value] of map) {
    console.log(`${key}: ${value}`);
  }
}

// ============================================================================
// 7. TIME AND SPACE COMPLEXITY QUICK REFERENCE
// ============================================================================

/*
COMMON TIME COMPLEXITIES (from fastest to slowest):
- O(1): Constant - accessing array index, hash map lookup
- O(log n): Logarithmic - binary search
- O(n): Linear - single loop through array
- O(n log n): Linearithmic - efficient sorting (merge sort, quick sort)
- O(n²): Quadratic - nested loops
- O(2^n): Exponential - recursive fibonacci without memoization
- O(n!): Factorial - generating all permutations

SPACE COMPLEXITY:
- O(1): Using fixed amount of extra space
- O(n): Using extra space proportional to input size
- O(n²): Using 2D matrix of size n×n
*/

// ============================================================================
// 8. COMMON INTERVIEW TIPS
// ============================================================================

/*
PROBLEM-SOLVING APPROACH:
1. Clarify the problem - ask questions about inputs, outputs, edge cases
2. Think of examples - write out test cases
3. Consider different approaches - brute force first, then optimize
4. Choose data structures - what fits the problem best?
5. Write pseudocode - plan before coding
6. Implement the solution - write clean, readable code
7. Test with examples - verify your solution works
8. Analyze complexity - discuss time and space complexity
9. Optimize if needed - can you do better?

COMMON EDGE CASES TO CONSIDER:
- Empty input (empty array, empty string)
- Single element
- All elements the same
- Negative numbers
- Very large numbers
- null or undefined values
- Sorted vs unsorted input
- Duplicates

GOOD CODING PRACTICES:
- Use meaningful variable names
- Add comments for complex logic
- Handle edge cases
- Write modular, reusable code
- Consider error handling
- Test as you go
- Communicate your thought process
*/

// ============================================================================
// END OF REFERENCE GUIDE
// ============================================================================
