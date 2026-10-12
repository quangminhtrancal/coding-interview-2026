# LeetCode Data Structures Summary (Go 1.21+)

## Complexity at a glance

| Structure | Access | Search | Insert | Delete |
|---|---|---|---|---|
| Slice | O(1) | O(n) | O(1) amortized append | O(n) |
| Map | - | O(1) avg | O(1) avg | O(1) avg |
| Stack / Queue (slice) | O(1) end | O(n) | O(1) | O(1) |
| Heap | O(1) top | O(n) | O(log n) | O(log n) |
| Linked list | O(n) | O(n) | O(1) at node | O(1) at node |
| Balanced BST | - | O(log n) | O(log n) | O(log n) |
| Trie | - | O(L) | O(L) | O(L) |
| Union-Find | - | ~O(1) | ~O(1) | - |

## Slices
```go
a := make([]int, 0, n)
a = append(a, x)
cp := slices.Clone(a)                    // slices alias memory; clone before saving
a = append(a[:i], a[i+1:]...)            // delete index i
sort.Slice(p, func(i, j int) bool { return p[i][0] < p[j][0] })
grid := make([][]int, m); for i := range grid { grid[i] = make([]int, n) }
```
Tips: `mid := lo + (hi-lo)/2`; `math.MaxInt` / `math.MinInt`; built-in `min`/`max`.

## Strings
```go
b := []byte(s); r := []rune(s)           // mutate / Unicode
idx := s[i] - 'a'                        // char to 0..25
var cnt [26]int                          // arrays are comparable -> usable as map keys
var sb strings.Builder; sb.WriteByte('a'); sb.String()
```
Handy: `strings.Split/Join/Fields/Contains/HasPrefix`, `strconv.Atoi/Itoa`.

## Map / Set
```go
m := map[string]int{}; m[k]++            // missing key -> zero value
if v, ok := m[k]; ok {}; delete(m, k)
set := map[int]struct{}{}                // set
type P struct{ r, c int }; seen := map[P]bool{}
```
Iteration order is random; slices can't be keys; writing to a nil map panics.

## Stack / Queue / Deque
```go
st = append(st, x); top := st[len(st)-1]; st = st[:len(st)-1]   // stack
x := q[0]; q = q[1:]; q = append(q, y)                           // queue
```
- **Monotonic stack**: keep indices; pop while top is smaller than current (next greater element).
- **Monotonic deque**: keep indices, pop back while worse, pop front when out of window (sliding window max).

## Heap (`container/heap`)
Implement `Len, Less, Swap, Push(x any), Pop() any` (Push/Pop on pointer receiver).
```go
func (h MinHeap) Less(i, j int) bool { return h[i] < h[j] }   // flip for max-heap
func (h *MinHeap) Pop() any { o := *h; n := len(o); x := o[n-1]; *h = o[:n-1]; return x }
heap.Push(h, v); v := heap.Pop(h).(int); top := (*h)[0]
```
Use a struct item (`node, dist`) for Dijkstra and top-K.

## Linked list
```go
dummy := &ListNode{}; tail := dummy      // dummy head avoids head edge cases
// reverse
for cur != nil { next := cur.Next; cur.Next = prev; prev, cur = cur, next }
// fast/slow: middle node, cycle detection
```

## Binary tree
- DFS recursion (pre/in/post); BFS with `size := len(q)` per level.
- BST inorder is sorted; validate with `(lo, hi)` bounds.
- For diameter / max path: closure `dfs` returns height, updates outer `ans`.
```go
var dfs func(*TreeNode) int
dfs = func(n *TreeNode) int { if n == nil { return 0 }; l, r := dfs(n.Left), dfs(n.Right); ans = max(ans, l+r); return 1 + max(l, r) }
```

## Graph
```go
graph := make([][]int, n)                // adjacency list
dirs := [][2]int{{1,0},{-1,0},{0,1},{0,-1}}   // grid neighbors
```
- BFS = shortest path (unweighted); DFS = components, cycles.
- **Topo sort (Kahn)**: queue nodes with indegree 0; cycle if `len(order) < n`.
- **Dijkstra**: min-heap; skip popped item if `item.dist > dist[node]`.

## Union-Find
```go
func (u *UF) Find(x int) int { for u.parent[x] != x { u.parent[x] = u.parent[u.parent[x]]; x = u.parent[x] }; return x }
// Union by rank; count-- on successful merge
```
Use for components, redundant connection, Kruskal, accounts merge.

## Trie
```go
type Trie struct { children [26]*Trie; end bool }
```
Insert/walk by `c := w[i]-'a'`; `Search` needs `end`, `StartsWith` only needs the node. Use `map[rune]*Trie` for general alphabets.

## LRU cache
`container/list` + `map[int]*list.Element`: on get/put `MoveToFront`; on overflow remove `Back()` and delete its key from the map.

## Algorithm templates
- **Binary search (lower bound)**: `lo, hi := 0, n; for lo < hi { mid := lo+(hi-lo)/2; if a[mid] < t { lo = mid+1 } else { hi = mid } }`. Also `sort.SearchInts`, `sort.Search`. For "min feasible answer", binary search on `feasible(x)`.
- **Two pointers**: sorted array pair sum, move `l++` or `r--`.
- **Sliding window**: map of last-seen index, move `l` past repeats.
- **Prefix sum**: `prefix[i+1] = prefix[i] + a[i]`; subarray sum = k via `count[sum-k]` map.
- **Backtracking**: append, recurse, undo; save with `slices.Clone(path)`.
- **DP**: 1D/2D table or memoized closure with a map.
- **Intervals**: sort by start, merge when `cur[0] <= last[1]`.

## Bit tricks
`x&1` odd, `x&(x-1)` clear lowest set bit, `x&-x` lowest set bit, `1<<i` mask, `x^x == 0` (XOR cancels pairs), `bits.OnesCount(uint(x))`.

## Go gotchas
- No built-in set/stack/queue/heap; use maps, slices, `container/heap`.
- Declare recursive closures first: `var dfs func(int)`.
- `%` can be negative: `((x % m) + m) % m`.
- Use `strings.Builder`, not `+=`, in loops.
- Beware shadowing with `:=` in inner blocks.
- `for i := range n` works in Go 1.22+.
- Common imports: `sort, slices, strings, strconv, math, math/bits, container/heap, container/list`.

## Which tool for which problem

| Smell | Reach for |
|---|---|
| Pair / complement lookup | Hash map |
| Sorted array target/pair | Binary search, two pointers |
| Contiguous subarray/substring | Sliding window, prefix sum |
| Next greater/smaller | Monotonic stack |
| Top K, K-th, merge K | Heap |
| Shortest path unweighted / weighted | BFS / Dijkstra |
| Combinations, permutations, subsets | Backtracking |
| Overlapping subproblems | DP |
| Connected components | Union-Find |
| Prefix / dictionary | Trie |
| Dependency order | Topological sort |
| Linked list cycle / middle | Fast/slow pointers |
| Intervals | Sort by start, sweep |
