package splunk

/*
CODING INTERVIEW PATTERNS IN GO
================================
Common algorithmic patterns and techniques for technical interviews
*/

import (
	"regexp"
	"sort"
	"strconv"
	"strings"
	"unicode"
)

// ============================================================================
// 1. TWO POINTERS PATTERNS
// ============================================================================

// Pattern 1.1: Two pointers moving towards each other (from both ends)
// Example: Check if string is palindrome
func IsPalindrome(s string) bool {
	left, right := 0, len(s)-1

	for left < right {
		if s[left] != s[right] {
			return false
		}
		left++
		right--
	}
	return true
}

// Pattern 1.2: Two pointers moving in same direction (slow and fast)
// Example: Remove duplicates from sorted array
func RemoveDuplicates(nums []int) int {
	if len(nums) == 0 {
		return 0
	}

	slow := 0
	for fast := 1; fast < len(nums); fast++ {
		if nums[fast] != nums[slow] {
			slow++
			nums[slow] = nums[fast]
		}
	}
	return slow + 1
}

// Pattern 1.3: Two pointers - partition array (Dutch National Flag)
// Example: Move zeros to end
func MoveZeroes(nums []int) {
	writePtr := 0

	// Move all non-zero elements to front
	for readPtr := 0; readPtr < len(nums); readPtr++ {
		if nums[readPtr] != 0 {
			nums[writePtr], nums[readPtr] = nums[readPtr], nums[writePtr]
			writePtr++
		}
	}
}

// Pattern 1.4: Two Sum - sorted array
func TwoSum(numbers []int, target int) []int {
	left, right := 0, len(numbers)-1

	for left < right {
		sum := numbers[left] + numbers[right]
		if sum == target {
			return []int{left, right}
		} else if sum < target {
			left++
		} else {
			right--
		}
	}
	return []int{}
}

// Pattern 1.5: Three Sum
func ThreeSum(nums []int) [][]int {
	sort.Ints(nums)
	result := [][]int{}

	for i := 0; i < len(nums)-2; i++ {
		// Skip duplicates
		if i > 0 && nums[i] == nums[i-1] {
			continue
		}

		left, right := i+1, len(nums)-1
		for left < right {
			sum := nums[i] + nums[left] + nums[right]

			if sum == 0 {
				result = append(result, []int{nums[i], nums[left], nums[right]})

				// Skip duplicates
				for left < right && nums[left] == nums[left+1] {
					left++
				}
				for left < right && nums[right] == nums[right-1] {
					right--
				}
				left++
				right--
			} else if sum < 0 {
				left++
			} else {
				right--
			}
		}
	}
	return result
}

// Pattern 1.6: Container with most water
func MaxArea(height []int) int {
	maxArea := 0
	left, right := 0, len(height)-1

	for left < right {
		width := right - left
		h := min(height[left], height[right])
		area := width * h
		maxArea = max(maxArea, area)

		// Move pointer with smaller height
		if height[left] < height[right] {
			left++
		} else {
			right--
		}
	}
	return maxArea
}

// ============================================================================
// 2. SLIDING WINDOW PATTERNS
// ============================================================================

// Pattern 2.1: Fixed size sliding window
// Example: Maximum sum of subarray of size k
func MaxSumSubarray(nums []int, k int) int {
	if len(nums) < k {
		return 0
	}

	// Calculate sum of first window
	windowSum := 0
	for i := 0; i < k; i++ {
		windowSum += nums[i]
	}

	maxSum := windowSum

	// Slide the window
	for i := k; i < len(nums); i++ {
		windowSum = windowSum - nums[i-k] + nums[i]
		maxSum = max(maxSum, windowSum)
	}

	return maxSum
}

// Pattern 2.2: Dynamic sliding window
// Example: Longest substring without repeating characters
func LengthOfLongestSubstring(s string) int {
	charMap := make(map[byte]int)
	left := 0
	maxLen := 0

	for right := 0; right < len(s); right++ {
		// If character exists in window, shrink from left
		if idx, exists := charMap[s[right]]; exists && idx >= left {
			left = idx + 1
		}

		charMap[s[right]] = right
		maxLen = max(maxLen, right-left+1)
	}

	return maxLen
}

// Pattern 2.3: Substring with condition
// Example: Minimum window substring containing all characters
func MinWindow(s string, t string) string {
	if len(s) < len(t) {
		return ""
	}

	// Count characters needed
	need := make(map[byte]int)
	for i := 0; i < len(t); i++ {
		need[t[i]]++
	}

	window := make(map[byte]int)
	left, right := 0, 0
	valid := 0
	start, length := 0, len(s)+1

	for right < len(s) {
		c := s[right]
		right++

		if _, exists := need[c]; exists {
			window[c]++
			if window[c] == need[c] {
				valid++
			}
		}

		// Shrink window when valid
		for valid == len(need) {
			if right-left < length {
				start = left
				length = right - left
			}

			d := s[left]
			left++

			if _, exists := need[d]; exists {
				if window[d] == need[d] {
					valid--
				}
				window[d]--
			}
		}
	}

	if length == len(s)+1 {
		return ""
	}
	return s[start : start+length]
}

// Pattern 2.4: Longest repeating character replacement
func CharacterReplacement(s string, k int) int {
	count := make(map[byte]int)
	left := 0
	maxCount := 0
	result := 0

	for right := 0; right < len(s); right++ {
		count[s[right]]++
		maxCount = max(maxCount, count[s[right]])

		// If window size - most frequent char > k, shrink window
		if right-left+1-maxCount > k {
			count[s[left]]--
			left++
		}

		result = max(result, right-left+1)
	}

	return result
}

// ============================================================================
// 3. STRING MANIPULATION PATTERNS
// ============================================================================

// Pattern 3.1: String reversal (in-place for slice of bytes)
func ReverseString(s []byte) {
	left, right := 0, len(s)-1
	for left < right {
		s[left], s[right] = s[right], s[left]
		left++
		right--
	}
}

// Pattern 3.2: Reverse words in string
func ReverseWords(s string) string {
	// Trim and split by spaces
	words := strings.Fields(s)

	// Reverse the slice
	for i, j := 0, len(words)-1; i < j; i, j = i+1, j-1 {
		words[i], words[j] = words[j], words[i]
	}

	return strings.Join(words, " ")
}

// Pattern 3.3: Check anagram
func IsAnagram(s string, t string) bool {
	if len(s) != len(t) {
		return false
	}

	count := make(map[rune]int)

	for _, ch := range s {
		count[ch]++
	}

	for _, ch := range t {
		count[ch]--
		if count[ch] < 0 {
			return false
		}
	}

	return true
}

// Pattern 3.4: Group anagrams
func GroupAnagrams(strs []string) [][]string {
	groups := make(map[string][]string)

	for _, str := range strs {
		// Sort string to use as key
		key := sortString(str)
		groups[key] = append(groups[key], str)
	}

	result := make([][]string, 0, len(groups))
	for _, group := range groups {
		result = append(result, group)
	}

	return result
}

func sortString(s string) string {
	runes := []rune(s)
	sort.Slice(runes, func(i, j int) bool {
		return runes[i] < runes[j]
	})
	return string(runes)
}

// Pattern 3.5: String to integer (atoi)
func Atoi(s string) int {
	s = strings.TrimSpace(s)
	if len(s) == 0 {
		return 0
	}

	sign := 1
	i := 0

	if s[i] == '+' || s[i] == '-' {
		if s[i] == '-' {
			sign = -1
		}
		i++
	}

	result := 0
	for i < len(s) && s[i] >= '0' && s[i] <= '9' {
		digit := int(s[i] - '0')

		// Check overflow
		if result > (1<<31-1)/10 || (result == (1<<31-1)/10 && digit > 7) {
			if sign == 1 {
				return 1<<31 - 1
			}
			return -1 << 31
		}

		result = result*10 + digit
		i++
	}

	return sign * result
}

// Pattern 3.6: Longest common prefix
func LongestCommonPrefix(strs []string) string {
	if len(strs) == 0 {
		return ""
	}

	prefix := strs[0]

	for i := 1; i < len(strs); i++ {
		for !strings.HasPrefix(strs[i], prefix) {
			prefix = prefix[:len(prefix)-1]
			if prefix == "" {
				return ""
			}
		}
	}

	return prefix
}

// Pattern 3.7: Valid parentheses
func IsValidParentheses(s string) bool {
	stack := []rune{}
	pairs := map[rune]rune{
		')': '(',
		'}': '{',
		']': '[',
	}

	for _, ch := range s {
		if ch == '(' || ch == '{' || ch == '[' {
			stack = append(stack, ch)
		} else if close, ok := pairs[ch]; ok {
			if len(stack) == 0 || stack[len(stack)-1] != close {
				return false
			}
			stack = stack[:len(stack)-1]
		}
	}

	return len(stack) == 0
}

// Pattern 3.8: Implement strStr (substring search)
func StrStr(haystack string, needle string) int {
	if len(needle) == 0 {
		return 0
	}
	if len(haystack) < len(needle) {
		return -1
	}

	// Simple approach
	for i := 0; i <= len(haystack)-len(needle); i++ {
		if haystack[i:i+len(needle)] == needle {
			return i
		}
	}

	return -1
}

// Pattern 3.9: Count and say sequence
func CountAndSay(n int) string {
	if n == 1 {
		return "1"
	}

	prev := CountAndSay(n - 1)
	result := strings.Builder{}

	i := 0
	for i < len(prev) {
		count := 1
		digit := prev[i]

		// Count consecutive same digits
		for i+1 < len(prev) && prev[i+1] == digit {
			count++
			i++
		}

		result.WriteString(strconv.Itoa(count))
		result.WriteByte(digit)
		i++
	}

	return result.String()
}

// ============================================================================
// 4. REGEX PATTERNS
// ============================================================================

// Pattern 4.1: Email validation
func IsValidEmail(email string) bool {
	pattern := `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`
	matched, _ := regexp.MatchString(pattern, email)
	return matched
}

// Pattern 4.2: Phone number validation (US format)
func IsValidPhoneNumber(phone string) bool {
	// Matches: (123) 456-7890, 123-456-7890, 1234567890
	pattern := `^(\+1[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}$`
	matched, _ := regexp.MatchString(pattern, phone)
	return matched
}

// Pattern 4.3: Extract all numbers from string
func ExtractNumbers(s string) []string {
	re := regexp.MustCompile(`\d+`)
	return re.FindAllString(s, -1)
}

// Pattern 4.4: Extract all words
func ExtractWords(s string) []string {
	re := regexp.MustCompile(`\b\w+\b`)
	return re.FindAllString(s, -1)
}

// Pattern 4.5: Replace multiple spaces with single space
func NormalizeSpaces(s string) string {
	re := regexp.MustCompile(`\s+`)
	return strings.TrimSpace(re.ReplaceAllString(s, " "))
}

// Pattern 4.6: Validate IP address
func IsValidIPv4(ip string) bool {
	pattern := `^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$`
	matched, _ := regexp.MatchString(pattern, ip)
	return matched
}

// Pattern 4.7: Extract URLs from text
func ExtractURLs(text string) []string {
	pattern := `https?://[^\s]+`
	re := regexp.MustCompile(pattern)
	return re.FindAllString(text, -1)
}

// Pattern 4.8: Password strength validation
func IsStrongPassword(password string) bool {
	// At least 8 chars, 1 uppercase, 1 lowercase, 1 digit, 1 special char
	if len(password) < 8 {
		return false
	}

	hasUpper := regexp.MustCompile(`[A-Z]`).MatchString(password)
	hasLower := regexp.MustCompile(`[a-z]`).MatchString(password)
	hasDigit := regexp.MustCompile(`\d`).MatchString(password)
	hasSpecial := regexp.MustCompile(`[!@#$%^&*(),.?":{}|<>]`).MatchString(password)

	return hasUpper && hasLower && hasDigit && hasSpecial
}

// Pattern 4.9: Remove HTML tags
func StripHTMLTags(html string) string {
	re := regexp.MustCompile(`<[^>]*>`)
	return re.ReplaceAllString(html, "")
}

// ============================================================================
// 5. HASH MAP / SET PATTERNS
// ============================================================================

// Pattern 5.1: Two sum - unsorted array
func TwoSumUnsorted(nums []int, target int) []int {
	seen := make(map[int]int)

	for i, num := range nums {
		complement := target - num
		if idx, exists := seen[complement]; exists {
			return []int{idx, i}
		}
		seen[num] = i
	}

	return []int{}
}

// Pattern 5.2: First unique character
func FirstUniqChar(s string) int {
	count := make(map[rune]int)

	for _, ch := range s {
		count[ch]++
	}

	for i, ch := range s {
		if count[ch] == 1 {
			return i
		}
	}

	return -1
}

// Pattern 5.3: Intersection of two arrays
func Intersection(nums1 []int, nums2 []int) []int {
	set1 := make(map[int]bool)
	result := make(map[int]bool)

	for _, num := range nums1 {
		set1[num] = true
	}

	for _, num := range nums2 {
		if set1[num] {
			result[num] = true
		}
	}

	intersection := make([]int, 0, len(result))
	for num := range result {
		intersection = append(intersection, num)
	}

	return intersection
}

// Pattern 5.4: Top K frequent elements
func TopKFrequent(nums []int, k int) []int {
	// Count frequencies
	freq := make(map[int]int)
	for _, num := range nums {
		freq[num]++
	}

	// Bucket sort by frequency
	buckets := make([][]int, len(nums)+1)
	for num, count := range freq {
		buckets[count] = append(buckets[count], num)
	}

	// Collect top k
	result := []int{}
	for i := len(buckets) - 1; i >= 0 && len(result) < k; i-- {
		result = append(result, buckets[i]...)
	}

	return result[:k]
}

// ============================================================================
// 6. ARRAY/SLICE MANIPULATION PATTERNS
// ============================================================================

// Pattern 6.1: Rotate array right by k steps
func RotateArray(nums []int, k int) {
	k = k % len(nums)
	reverse(nums, 0, len(nums)-1)
	reverse(nums, 0, k-1)
	reverse(nums, k, len(nums)-1)
}

func reverse(nums []int, start, end int) {
	for start < end {
		nums[start], nums[end] = nums[end], nums[start]
		start++
		end--
	}
}

// Pattern 6.2: Product of array except self
func ProductExceptSelf(nums []int) []int {
	n := len(nums)
	result := make([]int, n)

	// Left products
	result[0] = 1
	for i := 1; i < n; i++ {
		result[i] = result[i-1] * nums[i-1]
	}

	// Right products
	right := 1
	for i := n - 1; i >= 0; i-- {
		result[i] *= right
		right *= nums[i]
	}

	return result
}

// Pattern 6.3: Find missing number (0 to n)
func MissingNumber(nums []int) int {
	n := len(nums)
	expectedSum := n * (n + 1) / 2
	actualSum := 0

	for _, num := range nums {
		actualSum += num
	}

	return expectedSum - actualSum
}

// Pattern 6.4: Find duplicate number
func FindDuplicate(nums []int) int {
	// Floyd's cycle detection
	slow, fast := nums[0], nums[nums[0]]

	for slow != fast {
		slow = nums[slow]
		fast = nums[nums[fast]]
	}

	slow = 0
	for slow != fast {
		slow = nums[slow]
		fast = nums[fast]
	}

	return slow
}

// Pattern 6.5: Maximum subarray sum (Kadane's algorithm)
func MaxSubArray(nums []int) int {
	maxSum := nums[0]
	currentSum := nums[0]

	for i := 1; i < len(nums); i++ {
		currentSum = max(nums[i], currentSum+nums[i])
		maxSum = max(maxSum, currentSum)
	}

	return maxSum
}

// Pattern 6.6: Merge intervals
type Interval struct {
	Start int
	End   int
}

func MergeIntervals(intervals []Interval) []Interval {
	if len(intervals) == 0 {
		return []Interval{}
	}

	// Sort by start time
	sort.Slice(intervals, func(i, j int) bool {
		return intervals[i].Start < intervals[j].Start
	})

	merged := []Interval{intervals[0]}

	for i := 1; i < len(intervals); i++ {
		last := &merged[len(merged)-1]

		if intervals[i].Start <= last.End {
			// Overlapping, merge
			last.End = max(last.End, intervals[i].End)
		} else {
			// Non-overlapping, add new interval
			merged = append(merged, intervals[i])
		}
	}

	return merged
}

// ============================================================================
// 7. BINARY SEARCH PATTERNS
// ============================================================================

// Pattern 7.1: Standard binary search
func BinarySearch(nums []int, target int) int {
	left, right := 0, len(nums)-1

	for left <= right {
		mid := left + (right-left)/2

		if nums[mid] == target {
			return mid
		} else if nums[mid] < target {
			left = mid + 1
		} else {
			right = mid - 1
		}
	}

	return -1
}

// Pattern 7.2: Find first occurrence
func FindFirstOccurrence(nums []int, target int) int {
	left, right := 0, len(nums)-1
	result := -1

	for left <= right {
		mid := left + (right-left)/2

		if nums[mid] == target {
			result = mid
			right = mid - 1 // Continue searching left
		} else if nums[mid] < target {
			left = mid + 1
		} else {
			right = mid - 1
		}
	}

	return result
}

// Pattern 7.3: Search in rotated sorted array
func SearchRotated(nums []int, target int) int {
	left, right := 0, len(nums)-1

	for left <= right {
		mid := left + (right-left)/2

		if nums[mid] == target {
			return mid
		}

		// Determine which half is sorted
		if nums[left] <= nums[mid] {
			// Left half is sorted
			if nums[left] <= target && target < nums[mid] {
				right = mid - 1
			} else {
				left = mid + 1
			}
		} else {
			// Right half is sorted
			if nums[mid] < target && target <= nums[right] {
				left = mid + 1
			} else {
				right = mid - 1
			}
		}
	}

	return -1
}

// Pattern 7.4: Find peak element
func FindPeakElement(nums []int) int {
	left, right := 0, len(nums)-1

	for left < right {
		mid := left + (right-left)/2

		if nums[mid] > nums[mid+1] {
			// Peak is in left half
			right = mid
		} else {
			// Peak is in right half
			left = mid + 1
		}
	}

	return left
}

// ============================================================================
// 8. SORTING PATTERNS
// ============================================================================

// Pattern 8.1: Quick sort
func QuickSort(arr []int) {
	if len(arr) < 2 {
		return
	}
	quickSortHelper(arr, 0, len(arr)-1)
}

func quickSortHelper(arr []int, low, high int) {
	if low < high {
		pivot := partition(arr, low, high)
		quickSortHelper(arr, low, pivot-1)
		quickSortHelper(arr, pivot+1, high)
	}
}

func partition(arr []int, low, high int) int {
	pivot := arr[high]
	i := low - 1

	for j := low; j < high; j++ {
		if arr[j] < pivot {
			i++
			arr[i], arr[j] = arr[j], arr[i]
		}
	}

	arr[i+1], arr[high] = arr[high], arr[i+1]
	return i + 1
}

// Pattern 8.2: Merge sort
func MergeSort(arr []int) []int {
	if len(arr) <= 1 {
		return arr
	}

	mid := len(arr) / 2
	left := MergeSort(arr[:mid])
	right := MergeSort(arr[mid:])

	return merge(left, right)
}

func merge(left, right []int) []int {
	result := make([]int, 0, len(left)+len(right))
	i, j := 0, 0

	for i < len(left) && j < len(right) {
		if left[i] <= right[j] {
			result = append(result, left[i])
			i++
		} else {
			result = append(result, right[j])
			j++
		}
	}

	result = append(result, left[i:]...)
	result = append(result, right[j:]...)

	return result
}

// Pattern 8.3: Custom sorting with comparator
type Person struct {
	Name string
	Age  int
}

func SortPersons(persons []Person) {
	sort.Slice(persons, func(i, j int) bool {
		if persons[i].Age == persons[j].Age {
			return persons[i].Name < persons[j].Name
		}
		return persons[i].Age < persons[j].Age
	})
}

// ============================================================================
// 9. BIT MANIPULATION PATTERNS
// ============================================================================

// Pattern 9.1: Single number (all others appear twice)
func SingleNumber(nums []int) int {
	result := 0
	for _, num := range nums {
		result ^= num // XOR cancels out pairs
	}
	return result
}

// Pattern 9.2: Number of 1 bits (Hamming weight)
func HammingWeight(n uint32) int {
	count := 0
	for n != 0 {
		n &= n - 1 // Clear rightmost 1 bit
		count++
	}
	return count
}

// Pattern 9.3: Power of two
func IsPowerOfTwo(n int) bool {
	return n > 0 && (n&(n-1)) == 0
}

// Pattern 9.4: Reverse bits
func ReverseBits(n uint32) uint32 {
	result := uint32(0)
	for i := 0; i < 32; i++ {
		result = (result << 1) | (n & 1)
		n >>= 1
	}
	return result
}

// Pattern 9.5: Count bits (0 to n)
func CountBits(n int) []int {
	result := make([]int, n+1)
	for i := 1; i <= n; i++ {
		result[i] = result[i>>1] + (i & 1)
	}
	return result
}

// ============================================================================
// 10. BACKTRACKING PATTERNS
// ============================================================================

// Pattern 10.1: Generate all permutations
func Permute(nums []int) [][]int {
	result := [][]int{}
	backtrackPermute(nums, []int{}, &result)
	return result
}

func backtrackPermute(nums []int, current []int, result *[][]int) {
	if len(current) == len(nums) {
		temp := make([]int, len(current))
		copy(temp, current)
		*result = append(*result, temp)
		return
	}

	for i := 0; i < len(nums); i++ {
		if contains(current, nums[i]) {
			continue
		}
		current = append(current, nums[i])
		backtrackPermute(nums, current, result)
		current = current[:len(current)-1]
	}
}

// Pattern 10.2: Generate all subsets
func Subsets(nums []int) [][]int {
	result := [][]int{}
	backtrackSubsets(nums, 0, []int{}, &result)
	return result
}

func backtrackSubsets(nums []int, start int, current []int, result *[][]int) {
	temp := make([]int, len(current))
	copy(temp, current)
	*result = append(*result, temp)

	for i := start; i < len(nums); i++ {
		current = append(current, nums[i])
		backtrackSubsets(nums, i+1, current, result)
		current = current[:len(current)-1]
	}
}

// Pattern 10.3: Combination sum
func CombinationSum(candidates []int, target int) [][]int {
	result := [][]int{}
	backtrackCombSum(candidates, target, 0, []int{}, &result)
	return result
}

func backtrackCombSum(candidates []int, target int, start int, current []int, result *[][]int) {
	if target == 0 {
		temp := make([]int, len(current))
		copy(temp, current)
		*result = append(*result, temp)
		return
	}

	if target < 0 {
		return
	}

	for i := start; i < len(candidates); i++ {
		current = append(current, candidates[i])
		backtrackCombSum(candidates, target-candidates[i], i, current, result)
		current = current[:len(current)-1]
	}
}

// ============================================================================
// 11. DYNAMIC PROGRAMMING PATTERNS
// ============================================================================

// Pattern 11.1: Climbing stairs (Fibonacci variant)
func ClimbStairs(n int) int {
	if n <= 2 {
		return n
	}

	prev2, prev1 := 1, 2

	for i := 3; i <= n; i++ {
		current := prev1 + prev2
		prev2 = prev1
		prev1 = current
	}

	return prev1
}

// Pattern 11.2: House robber
func Rob(nums []int) int {
	if len(nums) == 0 {
		return 0
	}
	if len(nums) == 1 {
		return nums[0]
	}

	prev2, prev1 := 0, 0

	for _, num := range nums {
		current := max(prev1, prev2+num)
		prev2 = prev1
		prev1 = current
	}

	return prev1
}

// Pattern 11.3: Longest increasing subsequence
func LengthOfLIS(nums []int) int {
	if len(nums) == 0 {
		return 0
	}

	dp := make([]int, len(nums))
	for i := range dp {
		dp[i] = 1
	}

	maxLen := 1

	for i := 1; i < len(nums); i++ {
		for j := 0; j < i; j++ {
			if nums[i] > nums[j] {
				dp[i] = max(dp[i], dp[j]+1)
			}
		}
		maxLen = max(maxLen, dp[i])
	}

	return maxLen
}

// Pattern 11.4: Coin change
func CoinChange(coins []int, amount int) int {
	dp := make([]int, amount+1)
	for i := 1; i <= amount; i++ {
		dp[i] = amount + 1
	}
	dp[0] = 0

	for i := 1; i <= amount; i++ {
		for _, coin := range coins {
			if coin <= i {
				dp[i] = min(dp[i], dp[i-coin]+1)
			}
		}
	}

	if dp[amount] > amount {
		return -1
	}
	return dp[amount]
}

// ============================================================================
// 12. UTILITY FUNCTIONS
// ============================================================================

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}

func max(a, b int) int {
	if a > b {
		return a
	}
	return b
}

func abs(x int) int {
	if x < 0 {
		return -x
	}
	return x
}

func contains(slice []int, val int) bool {
	for _, item := range slice {
		if item == val {
			return true
		}
	}
	return false
}

// ============================================================================
// 13. ADDITIONAL STRING PATTERNS
// ============================================================================

// Pattern 13.1: Encode and decode strings
type Codec struct{}

func (c *Codec) Encode(strs []string) string {
	var sb strings.Builder
	for _, s := range strs {
		sb.WriteString(strconv.Itoa(len(s)))
		sb.WriteString("#")
		sb.WriteString(s)
	}
	return sb.String()
}

func (c *Codec) Decode(s string) []string {
	result := []string{}
	i := 0

	for i < len(s) {
		// Find the delimiter
		j := i
		for s[j] != '#' {
			j++
		}

		length, _ := strconv.Atoi(s[i:j])
		result = append(result, s[j+1:j+1+length])
		i = j + 1 + length
	}

	return result
}

// Pattern 13.2: Longest palindromic substring
func LongestPalindrome(s string) string {
	if len(s) < 2 {
		return s
	}

	start, maxLen := 0, 0

	for i := 0; i < len(s); i++ {
		// Odd length palindromes
		len1 := expandAroundCenter(s, i, i)
		// Even length palindromes
		len2 := expandAroundCenter(s, i, i+1)

		length := max(len1, len2)
		if length > maxLen {
			maxLen = length
			start = i - (length-1)/2
		}
	}

	return s[start : start+maxLen]
}

func expandAroundCenter(s string, left, right int) int {
	for left >= 0 && right < len(s) && s[left] == s[right] {
		left--
		right++
	}
	return right - left - 1
}

// Pattern 13.3: Check if strings are one edit away
func IsOneEditDistance(s string, t string) bool {
	if abs(len(s)-len(t)) > 1 {
		return false
	}

	shorter, longer := s, t
	if len(s) > len(t) {
		shorter, longer = t, s
	}

	foundDiff := false
	i, j := 0, 0

	for i < len(shorter) && j < len(longer) {
		if shorter[i] != longer[j] {
			if foundDiff {
				return false
			}
			foundDiff = true

			if len(shorter) == len(longer) {
				i++
			}
		} else {
			i++
		}
		j++
	}

	return foundDiff || len(shorter) != len(longer)
}

// Pattern 13.4: Word break
func WordBreak(s string, wordDict []string) bool {
	wordSet := make(map[string]bool)
	for _, word := range wordDict {
		wordSet[word] = true
	}

	dp := make([]bool, len(s)+1)
	dp[0] = true

	for i := 1; i <= len(s); i++ {
		for j := 0; j < i; j++ {
			if dp[j] && wordSet[s[j:i]] {
				dp[i] = true
				break
			}
		}
	}

	return dp[len(s)]
}

// ============================================================================
// 14. ADVANCED PATTERNS
// ============================================================================

// Pattern 14.1: LRU Cache
type LRUCache struct {
	capacity int
	cache    map[int]*Node
	head     *Node
	tail     *Node
}

type Node struct {
	key   int
	value int
	prev  *Node
	next  *Node
}

func NewLRUCache(capacity int) LRUCache {
	head := &Node{}
	tail := &Node{}
	head.next = tail
	tail.prev = head

	return LRUCache{
		capacity: capacity,
		cache:    make(map[int]*Node),
		head:     head,
		tail:     tail,
	}
}

func (lru *LRUCache) Get(key int) int {
	if node, exists := lru.cache[key]; exists {
		lru.moveToFront(node)
		return node.value
	}
	return -1
}

func (lru *LRUCache) Put(key int, value int) {
	if node, exists := lru.cache[key]; exists {
		node.value = value
		lru.moveToFront(node)
	} else {
		node := &Node{key: key, value: value}
		lru.cache[key] = node
		lru.addToFront(node)

		if len(lru.cache) > lru.capacity {
			removed := lru.removeLast()
			delete(lru.cache, removed.key)
		}
	}
}

func (lru *LRUCache) moveToFront(node *Node) {
	lru.removeNode(node)
	lru.addToFront(node)
}

func (lru *LRUCache) addToFront(node *Node) {
	node.next = lru.head.next
	node.prev = lru.head
	lru.head.next.prev = node
	lru.head.next = node
}

func (lru *LRUCache) removeNode(node *Node) {
	node.prev.next = node.next
	node.next.prev = node.prev
}

func (lru *LRUCache) removeLast() *Node {
	node := lru.tail.prev
	lru.removeNode(node)
	return node
}

// Pattern 14.2: Trie (Prefix Tree)
type TrieNode struct {
	children map[rune]*TrieNode
	isEnd    bool
}

type Trie struct {
	root *TrieNode
}

func NewTrie() *Trie {
	return &Trie{
		root: &TrieNode{
			children: make(map[rune]*TrieNode),
		},
	}
}

func (t *Trie) Insert(word string) {
	node := t.root
	for _, ch := range word {
		if _, exists := node.children[ch]; !exists {
			node.children[ch] = &TrieNode{
				children: make(map[rune]*TrieNode),
			}
		}
		node = node.children[ch]
	}
	node.isEnd = true
}

func (t *Trie) Search(word string) bool {
	node := t.root
	for _, ch := range word {
		if _, exists := node.children[ch]; !exists {
			return false
		}
		node = node.children[ch]
	}
	return node.isEnd
}

func (t *Trie) StartsWith(prefix string) bool {
	node := t.root
	for _, ch := range prefix {
		if _, exists := node.children[ch]; !exists {
			return false
		}
		node = node.children[ch]
	}
	return true
}

// ============================================================================
// 15. UNICODE AND RUNE HANDLING
// ============================================================================

// Pattern 15.1: Count Unicode characters properly
func CountUnicodeChars(s string) int {
	return len([]rune(s))
}

// Pattern 15.2: Reverse Unicode string
func ReverseUnicodeString(s string) string {
	runes := []rune(s)
	for i, j := 0, len(runes)-1; i < j; i, j = i+1, j-1 {
		runes[i], runes[j] = runes[j], runes[i]
	}
	return string(runes)
}

// Pattern 15.3: Check if character is alphanumeric (Unicode-aware)
func IsAlphanumeric(r rune) bool {
	return unicode.IsLetter(r) || unicode.IsDigit(r)
}

// Pattern 15.4: To lowercase/uppercase (Unicode-aware)
func ToLowerUnicode(s string) string {
	runes := []rune(s)
	for i, r := range runes {
		runes[i] = unicode.ToLower(r)
	}
	return string(runes)
}

/*
============================================================================
COMPLEXITY REFERENCE
============================================================================

TWO POINTERS:
- Time: O(n), Space: O(1)

SLIDING WINDOW:
- Time: O(n), Space: O(k) where k is window/char set size

HASH MAP/SET:
- Time: O(n), Space: O(n)

SORTING:
- Quick Sort: O(n log n) average, O(n²) worst, Space: O(log n)
- Merge Sort: O(n log n) always, Space: O(n)

BINARY SEARCH:
- Time: O(log n), Space: O(1)

BACKTRACKING:
- Time: O(2^n) or O(n!), Space: O(n) for recursion stack

DYNAMIC PROGRAMMING:
- Time: O(n²) typical, Space: O(n) with optimization

============================================================================
KEY INTERVIEW TIPS
============================================================================

1. Always clarify input constraints (size, range, duplicates, etc.)
2. Start with brute force, then optimize
3. Consider edge cases (empty input, single element, all same, etc.)
4. Use meaningful variable names
5. Test with examples while coding
6. Analyze time and space complexity
7. Know when to use which pattern
8. Practice explaining your thought process

*/
