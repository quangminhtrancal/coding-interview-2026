package main

func outputIndexesToSum(array []int, target int) []int {
	l := len(array)
	for i := 0; i < l; i ++ {
		for j:= i; j < l; j++ {
			if array[i] + array[j] == target {
				return int[]{i, j}
			}
		}
	} 

	return nil
}

func twoSumHashMap(nums []int, target int) []int {
	valueToIndex := make(map[int]int)

	for index, value := range nums {
		compliment := target - value

		idx, err := valueToIndex[compliment]

		if err != nil {
			valueToIndex[value] = index
		}
		else {
			return []int{index, idx}
		}
	}

	return nil
}

func main() {
	nums := []int{2, 7, 11, 15}
	target := 9

	fmt.Println("Brute force:", twoSumBruteForce(nums, target))
	fmt.Println("Hash map:   ", twoSumHashMap(nums, target))
}