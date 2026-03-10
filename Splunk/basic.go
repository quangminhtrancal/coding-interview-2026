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