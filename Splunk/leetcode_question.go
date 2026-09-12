package splunk

/*
20. Valid Parentheses
https://leetcode.com/problems/valid-parentheses
*/

func isValid(s string) bool {
	closeToOpenBrackets := map[rune]rune{
		')': '(',
		']': '[',
		'}': '{',
	}

	stack := []rune{}

	for _, ch := range s {
		openBracket, isValid := closeToOpenBrackets[ch]

		if isValid {
			if len(stack) == 0 || stack[len(stack)-1] != openBracket {
				return false
			}

			stack = stack[:len(stack)-1]
		} else {
			stack = append(stack, ch)
		}
	}

	return len(stack) == 0
}

func twoSum(nums []int, target int) []int {
	valueToIndex := map[int]int{}

	for index, value := range nums {
		complimentValue := target - value

		complimentIndex, isExist := valueToIndex[complimentValue]
		if isExist {
			return []int{complimentIndex, index}
		} else {
			valueToIndex[value] = index
		}
	}

	return []int{}
}
