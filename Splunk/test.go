package main

import (
	"fmt"
	"sort"
	"strconv"
)

func Add(a, b int) int {
	return a + b
}

func Map[T any, U any](s []T, f func(T) U) []U {
	result := make([]U, len(s))
	for i, v := range s {
		result[i] = f(v)
	}
	return result
}

// Constraints
type Number interface {
	int | float64
}

func Sum[T Number](nums []T) T {
	var total T

	for _, val := range nums {
		total += val
	}

	return total
}

/*
Common patterns
*/

type Person struct {
	Name string
	Age  int
}

// Stringer (like toString)
func (p Person) String() string {
	return fmt.Sprintf("%s (%d)", p.Name, p.Age)
}

// Min / Max (Go 1.21+ has built in min/max)
// Before 1.21
func max(a, b int) int {
	if a > b {
		return a
	}
	return b
}

func main() {

	fmt.Printf("output is %d\n", Add(3, 4))

	stringTranslation := Map([]int{1, 2, 3}, func(n int) string {
		return fmt.Sprintf("Number: %d", n)
	})
	fmt.Println("translated strings: ", stringTranslation)

	nums1 := []float64{1, 2.5, 3.2, 4}
	fmt.Println("Sum is ", Sum(nums1))

	nums2 := []int{1, 2, 3, 4}
	fmt.Println("Sum is ", Sum(nums2))

	// Sort examples
	nums := []int{5, 3, 1, 4, 2}
	sort.Ints(nums)
	fmt.Println("Sorted ints:", nums)

	words := []string{"banana", "apple", "cherry"}
	sort.Strings(words)
	fmt.Println("Sorted strings:", words)

	people := []Person{{"Alice", 30}, {"Bob", 25}, {"Charlie", 35}}
	sort.Slice(people, func(i, j int) bool {
		return people[i].Age < people[j].Age
	})
	fmt.Println("Sorted people:", people)

	// String <-> Int
	n, err := strconv.Atoi("42")
	if err == nil {
		fmt.Println("String to int:", n)
	}
	s := strconv.Itoa(42)
	fmt.Println("Int to string:", s)

	fmt.Println("Max:", max(10, 20))
}
