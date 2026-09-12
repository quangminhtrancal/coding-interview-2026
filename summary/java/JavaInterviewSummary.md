# Java Data Structures + Coding Interview Patterns - Complete Summary

> Java 17+ focused. Copy-paste ready for interviews.

## Table of Contents
1. [Core Data Structures - Java API](#1-core-data-structures)
2. [Interview Patterns Master Table](#2-patterns)
3. [Pattern Details + Java Templates](#3-templates)

---

## 1. Core Data Structures

### 1.1 Array / ArrayList
```java
int[] a = new int[n];
Arrays.sort(a);
Arrays.fill(a, -1);
int[][] grid = new int[m][n];
List<Integer> list = new ArrayList<>();
Collections.sort(list);
Collections.reverse(list);
list.toArray(new Integer[0]);
// sort 2D by col 0
Arrays.sort(intervals, (x,y) -> Integer.compare(x[0], y[0]));
// sort desc
Arrays.sort(a, Collections.reverseOrder()); // Integer[] only
```
When: sorting, binary search, two pointers, sliding window, prefix sum, cyclic sort.

### 1.2 String / StringBuilder
```java
String s = "abc";
s.charAt(i); s.length(); s.substring(l,r); // r exclusive
s.toCharArray();
StringBuilder sb = new StringBuilder();
sb.append(c); sb.reverse(); sb.toString();
sb.deleteCharAt(sb.length()-1);
Character.isDigit(c); Character.isLetter(c);
String.join(",", list);
s.split(",");
```
When: sliding window, two pointers palindrome, anagram (freq[26]), stack for parentheses/decode.

### 1.3 Stack (use Deque, NOT legacy Stack)
```java
Deque<Integer> st = new ArrayDeque<>();
st.push(x); st.pop(); st.peek(); st.isEmpty(); st.size();
// Monotonic increasing (e.g. Next Greater, Daily Temps, Largest Rectangle)
for (int i = 0; i < n; i++) {
  while (!st.isEmpty() && a[st.peek()] >= a[i]) st.pop();
  // process
  st.push(i);
}
```
When: valid parentheses, min stack, eval RPN, monotonic stack, DFS iterative, decode string.

### 1.4 Queue / Deque / PriorityQueue
```java
Queue<Integer> q = new LinkedList<>(); // BFS
q.offer(x); q.poll(); q.peek();
Deque<Integer> dq = new ArrayDeque<>(); // sliding window max, palindrome
dq.offerFirst(x); dq.offerLast(x); dq.pollFirst(); dq.pollLast();
// Heap
PriorityQueue<Integer> minH = new PriorityQueue<>();
PriorityQueue<Integer> maxH = new PriorityQueue<>(Collections.reverseOrder());
PriorityQueue<int[]> pq = new PriorityQueue<>((a,b)->a[0]-b[0]);
pq.offer(x); pq.poll(); pq.peek(); pq.size();
```
When: Tree/Graph BFS, sliding window max (monotonic deque), Top-K, K-way merge, two heaps median, Dijkstra.

### 1.5 LinkedList
```java
class ListNode { int val; ListNode next; ListNode(int v){val=v;} }
ListNode dummy = new ListNode(0); dummy.next = head;
// Fast-slow
ListNode slow=head, fast=head;
while(fast!=null && fast.next!=null){ slow=slow.next; fast=fast.next.next; }
// Reverse iterative
ListNode prev=null, cur=head;
while(cur!=null){ ListNode nxt=cur.next; cur.next=prev; prev=cur; cur=nxt; }
// Java built-in (rarely used in interviews)
LinkedList<Integer> ll = new LinkedList<>();
ll.addFirst(x); ll.addLast(x); ll.removeFirst();
```
Patterns: reversal, cycle detection, merge, reorder, remove nth, LRU (see HashMap).

### 1.6 HashMap / HashSet
```java
Map<Integer,Integer> m = new HashMap<>();
m.put(k,v); m.get(k); m.getOrDefault(k,0); m.containsKey(k);
m.put(k, m.getOrDefault(k,0)+1);
for(var e: m.entrySet()){ e.getKey(); e.getValue(); }
m.computeIfAbsent(k, x->new ArrayList<>()).add(v);
Set<Integer> s = new HashSet<>();
s.add(x); s.contains(x); s.remove(x);
Map<String,Integer> freq = new HashMap<>();
// freq array faster for lowercase:
int[] f = new int[26]; f[c-'a']++;
// LinkedHashMap preserves insertion order (LRU base)
Map<Integer,Integer> lru = new LinkedHashMap<>(16,0.75f,true){
  protected boolean removeEldestEntry(Map.Entry e){ return size()>capacity; }
};
```
When: two-sum, anagram, prefix-sum subarray, longest substring w/o repeat, top-k freq, union-find complement.

### 1.7 Tree / BST
```java
class TreeNode { int val; TreeNode left,right; TreeNode(int v){val=v;} }
// BFS
Queue<TreeNode> q=new LinkedList<>(); q.offer(root);
while(!q.isEmpty()){ int sz=q.size(); for(int i=0;i<sz;i++){ TreeNode n=q.poll(); if(n.left!=null)q.offer(n.left); if(n.right!=null)q.offer(n.right);} }
// DFS iterative
Stack<TreeNode> st=new Stack<>(); st.push(root);
while(!st.isEmpty()){ TreeNode n=st.pop(); /*preorder*/ if(n.right!=null)st.push(n.right); if(n.left!=null)st.push(n.left); }
// BST: left<root<right, inorder sorted
// TreeMap = ordered map (BST), TreeSet = ordered set
TreeMap<Integer,Integer> tm=new TreeMap<>();
tm.firstKey(); tm.lastKey(); tm.floorKey(k); tm.ceilingKey(k);
```
When: LCA, validate BST (bounds), kth smallest (inorder), serialize, diameter, path sum, invert.

### 1.8 Heap / Top-K
```java
// Top K largest -> min-heap size K
PriorityQueue<Integer> h=new PriorityQueue<>(); // min
for(int x: nums){ h.offer(x); if(h.size()>k) h.poll(); }
// Kth largest stream / median: two heaps
PriorityQueue<Integer> lo=new PriorityQueue<>(Collections.reverseOrder()); // max
PriorityQueue<Integer> hi=new PriorityQueue<>(); // min
// add: offer to lo, move top to hi, rebalance |lo|>=|hi|
```
When: K largest/smallest, frequent, merge K lists, median, meeting rooms II.

### 1.9 Trie
```java
class TrieNode { TrieNode[] next=new TrieNode[26]; boolean isWord; }
class Trie {
  TrieNode root=new TrieNode();
  void insert(String w){ TrieNode n=root; for(char c:w.toCharArray()){ int i=c-'a'; if(n.next[i]==null)n.next[i]=new TrieNode(); n=n.next[i]; } n.isWord=true; }
  boolean search(String w){ TrieNode n=find(w); return n!=null&&n.isWord; }
  boolean startsWith(String p){ return find(p)!=null; }
  TrieNode find(String s){ TrieNode n=root; for(char c:s.toCharArray()){ n=n.next[c-'a']; if(n==null)return null; } return n; }
}
```
When: word search II, prefix replace, autocomplete, max XOR.

### 1.10 Graph + Union-Find
```java
// Adj list
Map<Integer,List<Integer>> g=new HashMap<>();
g.computeIfAbsent(u,x->new ArrayList<>()).add(v);
// BFS / DFS / Topo (Kahn) / Dijkstra
int[] indeg=new int[n]; Queue<Integer> qq=new LinkedList<>();
// Union-Find
class DSU { int[] p,r; DSU(int n){p=new int[n];r=new int[n]; for(int i=0;i<n;i++)p[i]=i;}
 int find(int x){ return p[x]==x?x:(p[x]=find(p[x])); }
 void union(int a,int b){ a=find(a);b=find(b); if(a==b)return; if(r[a]<r[b])p[a]=b; else if(r[a]>r[b])p[b]=a; else{p[b]=a;r[a]++;} } }
```

### 1.11 Sorting / Binary Search / Bit
```java
Arrays.sort(nums);
int lo=0, hi=n-1;
while(lo<=hi){ int mid=lo+(hi-lo)/2; if(a[mid]==t)break; else if(a[mid]<t)lo=mid+1; else hi=mid-1; }
// lower_bound: first >= t
int l=0,h=n; while(l<h){int m=l+(h-l)/2; if(a[m]<t)l=m+1; else h=m;}
// bit: n&(n-1) clears lowest 1, Integer.bitCount(n)
```

---

## 2. Patterns Master Table

| # | Pattern | Signal Keywords | Core DS | Template |
|---|---------|-----------------|---------|----------|
| 1 | Sliding Window | longest/shortest subarray with K, substring | HashMap, Deque | expand r, shrink l |
| 2 | Two Pointers | sorted array, palindrome, pair | Array | l=0,r=n-1 |
| 3 | Fast & Slow | cycle, middle, happy number | LinkedList | slow+1, fast+2 |
| 4 | Merge Intervals | intervals overlap, meeting | Sort+List | sort by start |
| 5 | Cyclic Sort | 1..n, missing, duplicate | Array | i<->nums[i]-1 swap |
| 6 | LinkedList Reversal | reverse, reorder, palindrome LL | LL | prev/cur/nxt |
| 7 | Tree BFS | level order, zigzag, min depth | Queue | size-loop |
| 8 | Tree DFS | path sum, diameter, LCA | Stack/Rec | preorder/in/post |
| 9 | Two Heaps | median, sliding median | 2x PQ | max+min balance |
| 10 | Backtracking/Subsets | all subsets/perms/combos | Rec+List | choose/explore/unchoose |
| 11 | Modified Binary Search | rotated, first/last, peak | Array | lo<=hi, mid |
| 12 | Top-K | kth, most frequent, closest | Heap | heap size K |
| 13 | K-way Merge | K sorted lists/arrays | Heap | push heads |
| 14 | Monotonic Stack | next greater, histogram, temps | Stack | decreasing stack |
| 15 | Prefix Sum + HashMap | subarray sum=K, equilibrium | HashMap | pref -> map |
| 16 | DP: 0/1 Knapsack | subset sum, partition | dp[] | dp[i][w] |
| 17 | DP: Unbounded | coin change, rod cutting | dp[] | reuse i |
| 18 | DP: Palindrome/LCS | LPS, LCS, edit distance | dp[l][r] | interval/lcs table |
| 19 | Graph: BFS/DFS/Topo | islands, course, clone | Queue/Set | visited+queue |
| 20 | Trie / XOR | prefix search, max XOR | Trie | 26-array node |
| 21 | Bitwise XOR | single number, missing | int | a^a=0 |

---

## 3. Templates

### P1 Sliding Window (variable)
```java
// Longest substring without repeating, min window, max sum K distinct
int l=0; Map<Character,Integer> m=new HashMap<>(); int best=0;
for(int r=0;r<s.length();r++){
  m.put(s.charAt(r), m.getOrDefault(s.charAt(r),0)+1);
  while(!valid(m)){ // shrink condition
    m.put(s.charAt(l), m.get(s.charAt(l))-1);
    if(m.get(s.charAt(l))==0) m.remove(s.charAt(l));
    l++;
  }
  best=Math.max(best, r-l+1);
}
// Fixed K: sum/max
int sum=0,best2=0;
for(int i=0;i<nums.length;i++){ sum+=nums[i]; if(i>=k) sum-=nums[i-k]; if(i>=k-1) best2=Math.max(best2,sum); }
// Sliding Window Maximum -> monotonic deque
Deque<Integer> dq=new ArrayDeque<>(); List<Integer> out=new ArrayList<>();
for(int i=0;i<nums.length;i++){
  while(!dq.isEmpty()&&dq.peekFirst()<=i-k) dq.pollFirst();
  while(!dq.isEmpty()&&nums[dq.peekLast()]<=nums[i]) dq.pollLast();
  dq.offerLast(i);
  if(i>=k-1) out.add(nums[dq.peekFirst()]);
}
```

### P2 Two Pointers
```java
Arrays.sort(nums); // 2Sum sorted, 3Sum, container water, trapping rain
int l=0,r=nums.length-1;
while(l<r){ int s=nums[l]+nums[r]; if(s==target) break; else if(s<target) l++; else r--; }
// Palindrome
boolean ok(String s){ int i=0,j=s.length()-1; while(i<j){ if(s.charAt(i++)!=s.charAt(j--)) return false; } return true; }
// Remove duplicates sorted: slow index
int j=0; for(int i=1;i<n;i++) if(nums[i]!=nums[j]) nums[++j]=nums[i];
```

### P3 Fast & Slow
```java
boolean hasCycle(ListNode h){ ListNode s=h,f=h; while(f!=null&&f.next!=null){s=s.next;f=f.next.next; if(s==f)return true;} return false; }
ListNode cycleStart(ListNode h){ ListNode s=h,f=h; while(f!=null&&f.next!=null){s=s.next;f=f.next.next; if(s==f){ s=h; while(s!=f){s=s.next;f=f.next;} return s;}} return null; }
ListNode middle(ListNode h){ ListNode s=h,f=h; while(f!=null&&f.next!=null){s=s.next;f=f.next.next;} return s; }
```

### P4 Merge Intervals
```java
Arrays.sort(iv,(a,b)->Integer.compare(a[0],b[0]));
List<int[]> out=new ArrayList<>(); int[] cur=iv[0];
for(int i=1;i<iv.length;i++){ if(iv[i][0]<=cur[1]) cur[1]=Math.max(cur[1],iv[i][1]); else {out.add(cur); cur=iv[i];} }
out.add(cur);
// Meeting rooms II: min-heap of ends
Arrays.sort(iv,(a,b)->a[0]-b[0]); PriorityQueue<Integer> h=new PriorityQueue<>();
for(int[] in:iv){ if(!h.isEmpty()&&h.peek()<=in[0]) h.poll(); h.offer(in[1]); } // h.size()=rooms
```

### P5 Cyclic Sort (values 1..n or 0..n)
```java
int i=0; while(i<nums.length){ int j=nums[i]-1; // for 0..n: j=nums[i]
 if(nums[i]>0&&nums[i]<=nums.length&&nums[i]!=nums[j]){ int t=nums[i];nums[i]=nums[j];nums[j]=t; } else i++; }
// then scan for nums[i]!=i+1 -> missing/duplicate
```

### P6 LinkedList Reversal
```java
ListNode reverse(ListNode h){ ListNode p=null,c=h; while(c!=null){ListNode n=c.next;c.next=p;p=c;c=n;} return p; }
// Reverse sublist / K-group: dummy + prev + loop
// Palindrome LL: find mid, reverse 2nd half, compare
```

### P7 Tree BFS
```java
List<List<Integer>> levelOrder(TreeNode r){ List<List<Integer>> o=new ArrayList<>(); if(r==null)return o; Queue<TreeNode> q=new LinkedList<>(); q.offer(r); while(!q.isEmpty()){ int s=q.size(); List<Integer> lvl=new ArrayList<>(); for(int i=0;i<s;i++){ TreeNode n=q.poll(); lvl.add(n.val); if(n.left!=null)q.offer(n.left); if(n.right!=null)q.offer(n.right);} o.add(lvl);} return o; }
```

### P8 Tree DFS
```java
boolean hasPath(TreeNode n,int sum){ if(n==null)return false; if(n.left==null&&n.right==null)return n.val==sum; return hasPath(n.left,sum-n.val)||hasPath(n.right,sum-n.val); }
int diameter(TreeNode r){ int[] m={0}; h(r,m); return m[0]; } int h(TreeNode n,int[] m){ if(n==null)return 0; int l=h(n.left,m),rr=h(n.right,m); m[0]=Math.max(m[0],l+rr); return 1+Math.max(l,rr); }
TreeNode lca(TreeNode r,TreeNode p,TreeNode q){ if(r==null||r==p||r==q)return r; TreeNode l=lca(r.left,p,q),rr=lca(r.right,p,q); return l!=null&&rr!=null?r:(l!=null?l:rr); }
boolean isValid(TreeNode n,long lo,long hi){ if(n==null)return true; if(n.val<=lo||n.val>=hi)return false; return isValid(n.left,lo,n.val)&&isValid(n.right,n.val,hi); }
```

### P9 Two Heaps Median
```java
class MedianFinder{
 PriorityQueue<Integer> lo=new PriorityQueue<>(Collections.reverseOrder()), hi=new PriorityQueue<>();
 void addNum(int x){ lo.offer(x); hi.offer(lo.poll()); if(lo.size()<hi.size()) lo.offer(hi.poll()); }
 double findMedian(){ return lo.size()>hi.size()?lo.peek():(lo.peek()+hi.peek())/2.0; }
}
```

### P10 Backtracking
```java
void backtrack(List<List<Integer>> o, List<Integer> cur, int[] nums, int start){
 o.add(new ArrayList<>(cur));
 for(int i=start;i<nums.length;i++){ cur.add(nums[i]); backtrack(o,cur,nums,i+1); cur.remove(cur.size()-1); }
}
// Permutations: if(cur.size()==nums.length) o.add(...); + boolean[] used
// CombSum: backtrack(..., target-nums[i], i) allow reuse; i+1 no reuse
```

### P11 Modified Binary Search
```java
int search(int[] a,int t){ int l=0,r=a.length-1; while(l<=r){int m=l+(r-l)/2; if(a[m]==t)return m; if(a[l]<=a[m]){ if(a[l]<=t&&t<a[m])r=m-1; else l=m+1; } else { if(a[m]<t&&t<=a[r])l=m+1; else r=m-1; }} return -1; }
// First/last pos: two lower_bounds. Peak: if(a[m]<a[m+1])l=m+1 else r=m.
```

### P12/P13 Top-K & K-way Merge
```java
// K frequent: bucket or heap
Map<Integer,Integer> m=new HashMap<>(); for(int x:nums)m.put(x,m.getOrDefault(x,0)+1);
PriorityQueue<int[]> h=new PriorityQueue<>((a,b)->a[1]-b[1]);
for(var e:m.entrySet()){ h.offer(new int[]{e.getKey(),e.getValue()}); if(h.size()>k)h.poll(); }
// Merge K lists
PriorityQueue<ListNode> pq=new PriorityQueue<>((a,b)->a.val-b.val);
for(ListNode l:lists) if(l!=null)pq.offer(l);
ListNode d=new ListNode(0),c=d; while(!pq.isEmpty()){ ListNode n=pq.poll(); c.next=n; c=n; if(n.next!=null)pq.offer(n.next); }
```

### P14 Monotonic Stack
```java
// Next Greater Element, Daily Temperatures, Stock Span, Largest Rectangle
int[] daily(int[] t){ int n=t.length; int[] o=new int[n]; Deque<Integer> s=new ArrayDeque<>(); for(int i=0;i<n;i++){ while(!s.isEmpty()&&t[i]>t[s.peek()]){ int j=s.pop(); o[j]=i-j; } s.push(i);} return o; }
int largest(int[] h){ Deque<Integer> s=new ArrayDeque<>(); int mx=0; for(int i=0;i<=h.length;i++){ int cur=i==h.length?0:h[i]; while(!s.isEmpty()&&cur<h[s.peek()]){ int hh=h[s.pop()]; int w=s.isEmpty()?i:i-s.peek()-1; mx=Math.max(mx,hh*w);} s.push(i);} return mx; }
```

### P15 Prefix Sum + HashMap
```java
int subarraySum(int[] n,int k){ Map<Integer,Integer> m=new HashMap<>(); m.put(0,1); int s=0,c=0; for(int x:n){ s+=x; c+=m.getOrDefault(s-k,0); m.put(s,m.getOrDefault(s,0)+1);} return c; }
// Prefix + suffix product except self, difference array for range updates
```

### P16-18 DP Cheatsheet
```java
// 0/1 Knapsack: subset sum / partition
boolean canPartition(int[] n){ int s=Arrays.stream(n).sum(); if(s%2==1)return false; boolean[] dp=new boolean[s/2+1]; dp[0]=true; for(int x:n) for(int j=s/2;j>=x;j--) dp[j]|=dp[j-x]; return dp[s/2]; }
// Unbounded: coin change min coins
int coinChange(int[] c,int amt){ int[] dp=new int[amt+1]; Arrays.fill(dp,amt+1); dp[0]=0; for(int i=1;i<=amt;i++) for(int coin:c) if(coin<=i) dp[i]=Math.min(dp[i],dp[i-coin]+1); return dp[amt]>amt?-1:dp[amt]; }
// LCS / Edit / LPS
int lcs(String a,String b){ int[][] dp=new int[a.length()+1][b.length()+1]; for(int i=1;i<=a.length();i++) for(int j=1;j<=b.length();j++) dp[i][j]=a.charAt(i-1)==b.charAt(j-1)?dp[i-1][j-1]+1:Math.max(dp[i-1][j],dp[i][j-1]); return dp[a.length()][b.length()]; }
// LIS O(n log n)
int lis(int[] n){ List<Integer> d=new ArrayList<>(); for(int x:n){ int i=Collections.binarySearch(d,x); if(i<0)i=-(i+1); if(i==d.size())d.add(x); else d.set(i,x);} return d.size(); }
// House robber / climbing stairs: dp[i]=max(dp[i-1],dp[i-2]+n[i])
```

### P19 Graph Templates
```java
// Islands (DFS)
void dfs(char[][] g,int i,int j){ if(i<0||j<0||i>=g.length||j>=g[0].length||g[i][j]!='1')return; g[i][j]='0'; dfs(g,i+1,j);dfs(g,i-1,j);dfs(g,i,j+1);dfs(g,i,j-1);}
// Course Schedule (Kahn topo)
boolean canFinish(int n,int[][] pre){ List<List<Integer>> g=new ArrayList<>(); for(int i=0;i<n;i++)g.add(new ArrayList<>()); int[] in=new int[n]; for(int[] p:pre){g.get(p[1]).add(p[0]); in[p[0]]++;} Queue<Integer> q=new LinkedList<>(); for(int i=0;i<n;i++)if(in[i]==0)q.offer(i); int c=0; while(!q.isEmpty()){int u=q.poll();c++; for(int v:g.get(u))if(--in[v]==0)q.offer(v);} return c==n; }
// Dijkstra
int[] dijk(List<int[]>[] g,int s){ int n=g.length; int[] d=new int[n]; Arrays.fill(d,Integer.MAX_VALUE); d[s]=0; PriorityQueue<int[]> pq=new PriorityQueue<>((a,b)->a[1]-b[1]); pq.offer(new int[]{s,0}); while(!pq.isEmpty()){int[] cur=pq.poll(); int u=cur[0],w=cur[1]; if(w>d[u])continue; for(int[] e:g[u]){int v=e[0],nw=w+e[1]; if(nw<d[v]){d[v]=nw; pq.offer(new int[]{v,nw});}}} return d; }
```

### Extras: Must-know one-liners
```java
// Two Sum
Map<Integer,Integer> m=new HashMap<>(); for(int i=0;i<n;i++){ if(m.containsKey(t-nums[i]))return new int[]{m.get(t-nums[i]),i}; m.put(nums[i],i); }
// Anagram: int[26] freq compare. Valid parens: map closer->opener + stack.
// LRU Cache: HashMap + DoublyLinkedList OR LinkedHashMap. MinStack: two stacks.
// Serialize tree: preorder with # null marker + queue rebuild.
// Trie + DFS: Word Search II.
```

## How to Pick Pattern (30s)
1. Sorted / pair / palindrome -> Two Pointers
2. Subarray/substring + K/longest -> Sliding Window / PrefixSum
3. LL cycle/middle -> Fast&Slow
4. Intervals -> sort by start + merge
5. 1..n misplaced -> Cyclic Sort
6. Levels -> BFS, Paths -> DFS
7. Kth/largest/smallest/median -> Heap
8. Next greater / histogram -> Monotonic Stack
9. All combos/perms -> Backtracking
10. Search in sorted/rotated -> Binary Search
11. Partition/subset/coin/palindrome count -> DP
12. Islands/courses/graph -> BFS/DFS/UnionFind/Topo
13. Prefix strings -> Trie
14. Single number -> XOR
