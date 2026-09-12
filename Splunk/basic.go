package splunk

import (
	"fmt"
	"strings"
	"math"
)

var x int = 10
var y = 20 // type inferred
z := 30 // short declaration (inside function only)

// Multiple variables
var a, b, c int = 1, 2, 3

const Pi = 3.14
const (
	StatusOK = 200
	StatusError = 500
)

bool // true, false
string // "hello"
int, int8, int16, int32, int64
uint, uint8, uint16, uint32, uint64
float32, float64
byte // alias for uint8
rune // alias for int32 (unicode code point)

var x int = 10

if x > 10 {
	fmt.Println("big")
} else if x > 5 {
	fmt.Println("medium")
} else {
	fmt.Println("small")
}

if val := compute(); val > 0 {
	fmt.Println(val)
}

switch day {
case "Mon":
	fmt.Println("Monday")

case "Tue", "Wed":
	fmt.Println("Mid-week")
default:
	fmt.Println("Other")
}

// Type switch
switch v := i.(type) {
case int:
	fmt.Println("int", v)
case string:
	fmt.Println("string", v)
}


// For loop
for i := 0; i < 10; i++ {

}

for x < 100 {
	x++
}

for {break}

// Range
for i, v := range slice {

}

for k, v := range myMap {

}

for i, ch := range "hello" {

} // ch is a rune????

// Function
func add(a int, b int) int {
	return a + b
}

// Multiple returns
func divide(a, b float64) (float64, error) {
	if b == 0 {
		return 0, fmt.Errorf("division by zero")
	}

	return a / b, nil
}

// Named returns
func swap(a, b int) (x, y int) {
	x, y = b, a
	return // naked return
}

// variadic ???
func sum(nums ...int) int {
	total := 0
	for _, n := range nums {
		total += n
	}

	return total
}

// Anonymous / closures
square := func(x int) int { return x * x }


/*
DATA STRUCTURE
*/
// Array ( fixed size )
var arr [5]int
arr := [3]int{1, 2, 3}

// Slice (dynamic)
s := []int{1, 2, 3}
s = append(s, 4, 5)

sub := s[1:3] // element at index 1, 2
s2 := make([]int, 5) // length 5, cap 5
s3 := make([]int, 0, 10) // length 0, cap 10
len(s) // length
cap(s) // capacity ???

// copy
dst := make([]int, len(src))
copy(dst, src)

// Maps
m := map[string]int{
	"alice": 90,
	"bob": 85,
}
m["charlie"] = 95

val := m["alice"]
val, ok := m["dave"]
delete(m, "bob")

m2 := make(map[string]int)

for k, v := range m {

}


/* struct
*/

type Person struct {
	Name string
	Age int
}

p := Person{Name: "Alive", Age: 30}
p.Name = "Bob"

pp := &Person{"Eve", 25}
pp.Age = 26

type Employee struct {
	Person
	Company string
}
e := Employee{Person{"Alice", 30}, "Google"}
e.Name // accessible directly


/* Pointers
*/

x := 42
p := &x // pointer to x
fmt.Println(*p) // dereference -> 42
*p = 21 // modify through pointer

// No pointer arithmetic in GO

/* 
Methods and Interfaces
*/
// Method (value receiver)
func (p Person) Greet() string {
	return "Hi, I'm " + p.Name
}

// Method (pointer receiver - can modify)
funct (p *Person) SetAge(age int) {
	p.Age = age
}

// Interface
type Shape interface {
	Area() float64
	Perimiter() float64
}

// Implement Shape implicitly
type Circle struct { Radius float64 }
func (c Circle) Area() floate64 {
	return math.Pi * c.Radius * c.Radius
}
func (c Circle) Perimeter() float64 {
	return 2 * math.Pi * c.Radius
}

// Empty interface (any type)
var i interface{} = "hello"

// GO 1.18+ use `any` instead of `interface{}`

// type assertion
s, ok := i.(string)


/*
Error handling
*/

// Errors are values
f, err := os.Open("file.txt")
if err != nil {
	log.Fatal(err)
}
defer f.Close()

// Custom error
type MyError struct {
	Code int
	Message string
}
func (e *MyError) Error() string {
	return fmt.Sprintf(("%d: %s", e.Code, e.Message))
}

// Wrap/unwrap (Go 1.13+)
err = fmt.Errorf("open failed: %w", err)
errors.Is(err, os.ErrNotExist)
errors.As(err, &target) // ????

// Goroutines and channels
// Goroutine
go func() {
	fmt.Println("running concurrently")
}()

// Channel
ch := make(chan int) // unbuffered
ch := make(chan int, 5) // buffered

ch <- 42 // send to channel 42
val := <- ch // receive
close(ch) // close

// Select multiplexing
select {
case msg := <- ch1:
	fmt.Println(msg)
case chr <- 42:
	fmt.Println("sent")
case <- time.After(time.Second):
	fmt.Println("timeout")
default:
	fmt.Println("no activity")
}

// WaitGroup
var wg sync.WaitGroup
for i:= 0; i < 5; i++ {
	wg.Add(1)
	go func(id int) {
		defer wg.Done()
		fmt.Println((id))
	}(i)
}
wg.Wait()

// Mutex
var mu sync.Mutex
mu.Lock()
// Critical section
mu.Unlock()

// Defer, Panic, Recover
defer fmt.Println("cleanup")

// Panic & Recover
func safeDivide(a, b int) (result int, err error) {
	defer func() {
		if r := recover(); r != nil {
			err = fmt.Error("panic: %w", r)
		}
	}() // why we have () here ???

	return a / b, nil
}

// Strings
len(s) // bye length
len([]rune(s)) // character length
strins.Contain(s, "go")
strings.HasPrefix(s, "he")
stirngs.HasSuffix(s, "lo")
strings.Split("a,b,c", ",") // []string("a","b","c")

strings.Join(parts, "-")
strings.ToUpper(s)
strings.ToLower(s)
stirngs.TrimSpace(s)
strings.Replce(s, "old", "new", -1)
strings.Index(s, "sub") // -1 if not found

fmt.Sprintf("Hello %s, age %d", name, age)

// String ..[]byte
b := []bye("hello")
s := string(b)

// Generic Go 1.18 +
func Map[T any, U any](s []T, f func(T) U) []U {
    result := make([]U, len(s))
    for i, v := range s {
        result[i] = f(v)
    }
    return result
}

/*
===============================================
DATA STRUCTURES: STACK, QUEUE, SET, MAP, TREE
===============================================
*/

// ============================================
// STACK (LIFO - Last In First Out)
// ============================================
// Use slice directly - simple and idiomatic Go
func stackExample() {
	// Create stack
	stack := []int{}

	// Push - add to end
	stack = append(stack, 1)
	stack = append(stack, 2)
	stack = append(stack, 3)
	// stack: [1, 2, 3]

	// Peek - view top without removing
	if len(stack) > 0 {
		top := stack[len(stack)-1] // 3
		fmt.Println(top)
	}

	// Pop - remove from end
	if len(stack) > 0 {
		val := stack[len(stack)-1] // 3
		stack = stack[:len(stack)-1]
		fmt.Println(val)
	}
	// stack: [1, 2]

	// Check if empty
	isEmpty := len(stack) == 0 // false

	// Size
	size := len(stack) // 2
}

// Stack helper functions (optional)
func push(stack []int, val int) []int {
	return append(stack, val)
}

func pop(stack []int) ([]int, int, bool) {
	if len(stack) == 0 {
		return stack, 0, false
	}
	val := stack[len(stack)-1]
	return stack[:len(stack)-1], val, true
}

func peek(stack []int) (int, bool) {
	if len(stack) == 0 {
		return 0, false
	}
	return stack[len(stack)-1], true
}

// Generic stack with helpers
func pushGeneric[T any](stack []T, val T) []T {
	return append(stack, val)
}

func popGeneric[T any](stack []T) ([]T, T, bool) {
	if len(stack) == 0 {
		var zero T
		return stack, zero, false
	}
	val := stack[len(stack)-1]
	return stack[:len(stack)-1], val, true
}

// ============================================
// QUEUE (FIFO - First In First Out)
// ============================================
// Option 1: Using slice directly (simple, good for small queues)
func queueExample() {
	// Create queue
	queue := []int{}

	// Enqueue - add to end
	queue = append(queue, 1)
	queue = append(queue, 2)
	queue = append(queue, 3)
	// queue: [1, 2, 3]

	// Dequeue - remove from front
	if len(queue) > 0 {
		val := queue[0] // 1
		queue = queue[1:]
		fmt.Println(val)
	}
	// queue: [2, 3]

	// Peek front
	if len(queue) > 0 {
		front := queue[0] // 2
		fmt.Println(front)
	}

	// Check if empty
	isEmpty := len(queue) == 0 // false

	// Size
	size := len(queue) // 2
}

// Queue helper functions (optional)
func enqueue(queue []int, val int) []int {
	return append(queue, val)
}

func dequeue(queue []int) ([]int, int, bool) {
	if len(queue) == 0 {
		return queue, 0, false
	}
	val := queue[0]
	return queue[1:], val, true
}

// Generic queue helpers
func enqueueGeneric[T any](queue []T, val T) []T {
	return append(queue, val)
}

func dequeueGeneric[T any](queue []T) ([]T, T, bool) {
	if len(queue) == 0 {
		var zero T
		return queue, zero, false
	}
	val := queue[0]
	return queue[1:], val, true
}

// Option 2: Using container/list (efficient for large queues)
// Use when you need O(1) dequeue operations
func queueWithListExample() {
	// Import: "container/list"
	queue := list.New()

	// Enqueue - add to back
	queue.PushBack(1)
	queue.PushBack(2)
	queue.PushBack(3)

	// Dequeue - remove from front
	if queue.Len() > 0 {
		front := queue.Front()
		val := front.Value.(int) // 1
		queue.Remove(front)
		fmt.Println(val)
	}

	// Peek front
	if queue.Len() > 0 {
		front := queue.Front()
		val := front.Value.(int) // 2
		fmt.Println(val)
	}

	// Size
	size := queue.Len() // 2

	// Check if empty
	isEmpty := queue.Len() == 0 // false
}

// ============================================
// SET (Unique elements)
// ============================================
// Go doesn't have built-in set, use map directly
// Using map[T]struct{} is more memory efficient than map[T]bool

// Option 1: Using map[string]bool (simple, intuitive)
func setExample() {
	// Create set
	set := make(map[string]bool)

	// Add elements
	set["apple"] = true
	set["banana"] = true
	set["apple"] = true // duplicate, no effect

	// Check if contains
	exists := set["apple"] // true
	exists = set["orange"] // false

	// Better way to check (distinguish between false and not exists)
	_, exists = set["apple"] // true
	_, exists = set["orange"] // false

	// Remove element
	delete(set, "banana")

	// Size
	size := len(set) // 1

	// Get all values
	values := []string{}
	for k := range set {
		values = append(values, k)
	}

	// Iterate
	for item := range set {
		fmt.Println(item)
	}
}

// Option 2: Using map[T]struct{} (more memory efficient)
func setWithStructExample() {
	// Create set
	set := make(map[int]struct{})

	// Add elements (struct{}{} is empty struct)
	set[1] = struct{}{}
	set[2] = struct{}{}
	set[3] = struct{}{}
	set[1] = struct{}{} // duplicate, no effect

	// Check if contains
	_, exists := set[2] // true
	_, exists = set[5] // false

	// Remove element
	delete(set, 2)

	// Size
	size := len(set) // 2

	// Iterate
	for item := range set {
		fmt.Println(item)
	}
}

// Set operations
func setOperations() {
	// Union
	set1 := map[int]bool{1: true, 2: true, 3: true}
	set2 := map[int]bool{3: true, 4: true, 5: true}

	union := make(map[int]bool)
	for k := range set1 {
		union[k] = true
	}
	for k := range set2 {
		union[k] = true
	}
	// union: {1, 2, 3, 4, 5}

	// Intersection
	intersection := make(map[int]bool)
	for k := range set1 {
		if set2[k] {
			intersection[k] = true
		}
	}
	// intersection: {3}

	// Difference (set1 - set2)
	difference := make(map[int]bool)
	for k := range set1 {
		if !set2[k] {
			difference[k] = true
		}
	}
	// difference: {1, 2}

	// Symmetric difference
	symDiff := make(map[int]bool)
	for k := range set1 {
		if !set2[k] {
			symDiff[k] = true
		}
	}
	for k := range set2 {
		if !set1[k] {
			symDiff[k] = true
		}
	}
	// symDiff: {1, 2, 4, 5}
}

// ============================================
// MAP (Key-Value pairs)
// ============================================
// Already covered above, but here are more operations:

func mapAdvancedExample() {
	// Create map
	m1 := make(map[string]int)
	m2 := map[string]int{"a": 1, "b": 2}

	// Add/Update
	m1["key"] = 100

	// Get (safe way)
	val, ok := m1["key"]
	if !ok {
		// key doesn't exist
	}

	// Delete
	delete(m1, "key")

	// Check if key exists
	_, exists := m1["key"]

	// Iterate
	for key, value := range m1 {
		fmt.Println(key, value)
	}

	// Get all keys
	keys := make([]string, 0, len(m1))
	for k := range m1 {
		keys = append(keys, k)
	}

	// Get all values
	values := make([]int, 0, len(m1))
	for _, v := range m1 {
		values = append(values, v)
	}

	// Clear map (Go 1.21+)
	clear(m1) // removes all elements

	// Map of slices
	m3 := make(map[string][]int)
	m3["numbers"] = []int{1, 2, 3}
	m3["numbers"] = append(m3["numbers"], 4)

	// Map of maps (nested)
	m4 := make(map[string]map[string]int)
	m4["user1"] = map[string]int{"age": 25, "score": 100}
}

// Concurrent-safe map (using sync.Map)
import "sync"

func syncMapExample() {
	var m sync.Map

	// Store
	m.Store("key", "value")

	// Load
	val, ok := m.Load("key")

	// LoadOrStore (atomic)
	actual, loaded := m.LoadOrStore("key", "default")

	// Delete
	m.Delete("key")

	// Range (iterate)
	m.Range(func(key, value interface{}) bool {
		fmt.Println(key, value)
		return true // continue iteration
	})
}

// ============================================
// BINARY TREE
// ============================================
type TreeNode struct {
	Val   int
	Left  *TreeNode
	Right *TreeNode
}

// Create node
func NewTreeNode(val int) *TreeNode {
	return &TreeNode{Val: val}
}

// Insert (BST - Binary Search Tree)
func (root *TreeNode) Insert(val int) *TreeNode {
	if root == nil {
		return NewTreeNode(val)
	}
	if val < root.Val {
		root.Left = root.Left.Insert(val)
	} else {
		root.Right = root.Right.Insert(val)
	}
	return root
}

// Search (BST)
func (root *TreeNode) Search(val int) bool {
	if root == nil {
		return false
	}
	if root.Val == val {
		return true
	}
	if val < root.Val {
		return root.Left.Search(val)
	}
	return root.Right.Search(val)
}

// In-order traversal (Left -> Root -> Right)
func (root *TreeNode) InOrder() []int {
	if root == nil {
		return []int{}
	}
	result := []int{}
	result = append(result, root.Left.InOrder()...)
	result = append(result, root.Val)
	result = append(result, root.Right.InOrder()...)
	return result
}

// Pre-order traversal (Root -> Left -> Right)
func (root *TreeNode) PreOrder() []int {
	if root == nil {
		return []int{}
	}
	result := []int{root.Val}
	result = append(result, root.Left.PreOrder()...)
	result = append(result, root.Right.PreOrder()...)
	return result
}

// Post-order traversal (Left -> Right -> Root)
func (root *TreeNode) PostOrder() []int {
	if root == nil {
		return []int{}
	}
	result := []int{}
	result = append(result, root.Left.PostOrder()...)
	result = append(result, root.Right.PostOrder()...)
	result = append(result, root.Val)
	return result
}

// Level-order traversal (BFS)
func (root *TreeNode) LevelOrder() [][]int {
	if root == nil {
		return [][]int{}
	}

	result := [][]int{}
	queue := []*TreeNode{root}

	for len(queue) > 0 {
		levelSize := len(queue)
		level := []int{}

		for i := 0; i < levelSize; i++ {
			node := queue[0]
			queue = queue[1:]
			level = append(level, node.Val)

			if node.Left != nil {
				queue = append(queue, node.Left)
			}
			if node.Right != nil {
				queue = append(queue, node.Right)
			}
		}
		result = append(result, level)
	}
	return result
}

// Height of tree
func (root *TreeNode) Height() int {
	if root == nil {
		return 0
	}
	leftHeight := root.Left.Height()
	rightHeight := root.Right.Height()
	if leftHeight > rightHeight {
		return leftHeight + 1
	}
	return rightHeight + 1
}

// Usage example:
func treeExample() {
	// Create BST
	var root *TreeNode
	root = root.Insert(5)
	root = root.Insert(3)
	root = root.Insert(7)
	root = root.Insert(2)
	root = root.Insert(4)
	root = root.Insert(6)
	root = root.Insert(8)

	//       5
	//      / \
	//     3   7
	//    / \ / \
	//   2  4 6  8

	// Search
	found := root.Search(4) // true
	found = root.Search(10) // false

	// Traversals
	inorder := root.InOrder()     // [2, 3, 4, 5, 6, 7, 8] (sorted)
	preorder := root.PreOrder()   // [5, 3, 2, 4, 7, 6, 8]
	postorder := root.PostOrder() // [2, 4, 3, 6, 8, 7, 5]
	levelorder := root.LevelOrder() // [[5], [3, 7], [2, 4, 6, 8]]

	// Height
	height := root.Height() // 3
}

// Generic Tree Node
type GenericTreeNode[T any] struct {
	Val   T
	Left  *GenericTreeNode[T]
	Right *GenericTreeNode[T]
}

// N-ary Tree (multiple children)
type NaryTreeNode struct {
	Val      int
	Children []*NaryTreeNode
}

func NewNaryTreeNode(val int) *NaryTreeNode {
	return &NaryTreeNode{Val: val, Children: []*NaryTreeNode{}}
}

func (n *NaryTreeNode) AddChild(child *NaryTreeNode) {
	n.Children = append(n.Children, child)
}

// Trie (Prefix Tree) - useful for string operations
type TrieNode struct {
	children map[rune]*TrieNode
	isEnd    bool
}

type Trie struct {
	root *TrieNode
}

func NewTrie() *Trie {
	return &Trie{root: &TrieNode{children: make(map[rune]*TrieNode)}}
}

func (t *Trie) Insert(word string) {
	node := t.root
	for _, ch := range word {
		if _, exists := node.children[ch]; !exists {
			node.children[ch] = &TrieNode{children: make(map[rune]*TrieNode)}
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

func trieExample() {
	trie := NewTrie()
	trie.Insert("apple")
	trie.Insert("app")

	found := trie.Search("apple")      // true
	found = trie.Search("app")         // true
	found = trie.Search("appl")        // false
	hasPrefix := trie.StartsWith("app") // true
}