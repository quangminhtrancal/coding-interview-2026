import java.util.*;

public class JavaInterviewSummary {

    // 1. CORE DATA STRUCTURES
    static class ListNode { int val; ListNode next; ListNode(int v) { val = v; } }
    static class TreeNode { int val; TreeNode left, right; TreeNode(int v) { val = v; } }

    // Map‑based Trie (supports Unicode)
    static class TrieNode { Map<Character, TrieNode> children = new HashMap<>(); boolean isWord; }
    static class Trie {
        TrieNode root = new TrieNode();
        void insert(String w) {
            TrieNode n = root;
            for (char c : w.toCharArray()) n = n.children.computeIfAbsent(c, k -> new TrieNode());
            n.isWord = true;
        }

        boolean search(String w) {
            TrieNode n = root;
            for (char c : w.toCharArray()) {
                n = n.children.get(c);
                if (n == null) return false;
            }
            return n.isWord;
        }

        boolean startsWith(String p) {
            TrieNode n = root;
            for (char c : p.toCharArray()) {
                n = n.children.get(c);
                if (n == null) return false;
            }
            return true;
        }
    }

    // Union‑Find with path compression + union by rank
    static class DSU {
        int[] parent, rank;
        DSU(int n) {
            parent = new int[n]; rank = new int[n];
            for (int i = 0; i < n; i++) parent[i] = i;
        }
        int find(int x) {
            if (parent[x] != x) parent[x] = find(parent[x]);
            return parent[x];
        }
        void union(int a, int b) {
            int ra = find(a), rb = find(b);
            if (ra == rb) return;
            if (rank[ra] < rank[rb]) parent[ra] = rb;
            else if (rank[ra] > rank[rb]) parent[rb] = ra;
            else { parent[rb] = ra; rank[ra]++; }
        }
    }

    // Two‑heap median
    static class MedianFinder {
        PriorityQueue<Integer> lo = new PriorityQueue<>(Collections.reverseOrder()); // max‑heap
        PriorityQueue<Integer> hi = new PriorityQueue<>(); // min‑heap
        void addNum(int x) {
            lo.offer(x); hi.offer(lo.poll());
            if (lo.size() < hi.size()) lo.offer(hi.poll());
        }
        double findMedian() {
            return lo.size() > hi.size() ? lo.peek() : (lo.peek() + hi.peek()) / 2.0;
        }
    }

    // LRU Cache (HashMap + Doubly Linked List)
    static class LRUCache {
        class Node { int key, val; Node prev, next; }

        Map<Integer, Node> map = new HashMap<>();
        Node head = new Node(), tail = new Node();
        int cap;
        LRUCache(int capacity) {
            cap = capacity;
            head.next = tail; tail.prev = head;
        }

        int get(int key) {
            if (!map.containsKey(key)) return -1;
            Node node = map.get(key);
            moveToFront(node);
            return node.val;
        }

        void put(int key, int val) {
            if (map.containsKey(key)) {
                Node node = map.get(key);
                node.val = val;
                moveToFront(node);
                return;
            }

            if (map.size() == cap) evictLast();
            Node node = new Node();
            node.key = key; node.val = val;
            map.put(key, node);
            addToFront(node);
        }

        private void addToFront(Node n) {
            n.next = head.next; n.prev = head;
            head.next.prev = n; head.next = n;
        }

        private void moveToFront(Node n) {
            n.prev.next = n.next;
            n.next.prev = n.prev;
            addToFront(n);
        }

        private void evictLast() {
            Node last = tail.prev;
            last.prev.next = tail; tail.prev = last.prev;
            map.remove(last.key);
        }
    }

    // Min Stack
    static class MinStack {
        Deque<Integer> stack = new ArrayDeque<>(), mins = new ArrayDeque<>();
        void push(int x) {
            stack.push(x);
            mins.push(mins.isEmpty() ? x : Math.min(mins.peek(), x));
        }

        void pop() { stack.pop(); mins.pop(); }

        int top() { return stack.peek(); }

        int getMin() { return mins.peek(); }
    }

    // 2. PATTERN TEMPLATES
    // 2.1 Sliding Window (variable)
    static int longestNoRepeat(String s) {
        Map<Character, Integer> cnt = new HashMap<>();

        int l = 0, best = 0;
        for (int r = 0; r < s.length(); r++) {
            cnt.put(s.charAt(r), cnt.getOrDefault(s.charAt(r), 0) + 1);

            while (cnt.get(s.charAt(r)) > 1) {
                char leftCh = s.charAt(l);
                cnt.put(leftCh, cnt.get(leftCh) - 1);
                l++;
            }

            best = Math.max(best, r - l + 1);
        }

        return best;
    }

    // 2.2 Sliding Window Max (monotonic deque)
    static List<Integer> slidingMax(int[] a, int k) {
        Deque<Integer> dq = new ArrayDeque<>();
        List<Integer> out = new ArrayList<>();

        for (int i = 0; i < a.length; i++) {
            while (!dq.isEmpty() && dq.peekFirst() <= i - k) dq.pollFirst();
            while (!dq.isEmpty() && a[dq.peekLast()] <= a[i]) dq.pollLast();
            dq.offerLast(i);
            if (i >= k - 1) out.add(a[dq.peekFirst()]);
        }
        return out;
    }

    // 2.3 Two Pointers (sorted array pair)
    static int[] twoSumSorted(int[] nums, int t) {
        int l = 0, r = nums.length - 1;
        while (l < r) {
            int s = nums[l] + nums[r];
            if (s == t) return new int[]{l, r};
            else if (s < t) l++; else r--;
        }
        return new int[]{-1, -1};
    }

    // 2.4 Fast & Slow (cycle detection)
    static boolean hasCycle(ListNode h) {
        ListNode s = h, f = h;
        while (f != null && f.next != null) {
            s = s.next; f = f.next.next;
            if (s == f) return true;
        }
        return false;
    }

    static ListNode middle(ListNode h) {
        ListNode s = h, f = h;
        while (f != null && f.next != null) {
            s = s.next; f = f.next.next;
        }
        return s;
    }

    // 2.5 Merge Intervals
    static List<int[]> merge(int[][] iv) {
        Arrays.sort(iv, (a, b) -> Integer.compare(a[0], b[0]));

        List<int[]> ans = new ArrayList<>();
        int[] cur = iv[0];

        for (int i = 1; i < iv.length; i++) {
            if (iv[i][0] <= cur[1]) cur[1] = Math.max(cur[1], iv[i][1]);
            else { ans.add(cur); cur = iv[i]; }
        }
        
        ans.add(cur);
        return ans;
    }

    // 2.6 Cyclic Sort (1..n)
    static void cyclicSort(int[] a) {
        int i = 0;
        while (i < a.length) {
            int j = a[i] - 1;
            if (a[i] > 0 && a[i] <= a.length && a[i] != a[j]) {
                int t = a[i]; a[i] = a[j]; a[j] = t;
            } else i++;
        }
    }

    // 2.7 Linked List Reversal
    static ListNode reverse(ListNode h) {
        ListNode p = null, c = h;
        while (c != null) {
            ListNode n = c.next;
            c.next = p;
            p = c;
            c = n;
        }
        return p;
    }

    // 2.8 Tree BFS (level order)
    static List<List<Integer>> levelOrder(TreeNode root) {
        List<List<Integer>> ans = new ArrayList<>();
        if (root == null) return ans;
        Queue<TreeNode> q = new LinkedList<>();
        q.offer(root);
        while (!q.isEmpty()) {
            int s = q.size();
            List<Integer> lvl = new ArrayList<>();
            for (int i = 0; i < s; i++) {
                TreeNode n = q.poll();
                lvl.add(n.val);
                if (n.left != null) q.offer(n.left);
                if (n.right != null) q.offer(n.right);
            }
            ans.add(lvl);
        }
        return ans;
    }

    // 2.9 Tree DFS
    static boolean hasPath(TreeNode n, int sum) {
        if (n == null) return false;
        if (n.left == null && n.right == null) return n.val == sum;
        return hasPath(n.left, sum - n.val) || hasPath(n.right, sum - n.val);
    }

    static int diameter(TreeNode r) {
        int[] max = {0};
        height(r, max);
        return max[0];
    }
    
    static int height(TreeNode n, int[] m) {
        if (n == null) return 0;
        int l = height(n.left, m), r = height(n.right, m);
        m[0] = Math.max(m[0], l + r);
        return 1 + Math.max(l, r);
    }

    static TreeNode lca(TreeNode r, TreeNode p, TreeNode q) {
        if (r == null || r == p || r == q) return r;
        TreeNode left = lca(r.left, p, q), right = lca(r.right, p, q);
        return left != null && right != null ? r : (left != null ? left : right);
    }

    static boolean isValidBST(TreeNode n, long lo, long hi) {
        if (n == null) return true;
        if (n.val <= lo || n.val >= hi) return false;
        return isValidBST(n.left, lo, n.val) && isValidBST(n.right, n.val, hi);
    }

    // 2.10 Heap (Top‑K, Merge K)
    static List<Integer> topK(int[] nums, int k) {
        PriorityQueue<Integer> h = new PriorityQueue<>();
        for (int x : nums) { h.offer(x); if (h.size() > k) h.poll(); }
        return new ArrayList<>(h);
    }

    static ListNode mergeKLists(ListNode[] lists) {
        PriorityQueue<ListNode> pq = new PriorityQueue<>((a, b) -> a.val - b.val);
        for (ListNode l : lists) if (l != null) pq.offer(l);
        ListNode d = new ListNode(0), t = d;
        while (!pq.isEmpty()) {
            ListNode n = pq.poll();
            t.next = n; t = n;
            if (n.next != null) pq.offer(n.next);
        }
        return d.next;
    }

    // 2.11 Backtracking (subsets)
    static void subsets(List<List<Integer>> res, List<Integer> cur, int[] nums, int start) {
        res.add(new ArrayList<>(cur));
        for (int i = start; i < nums.length; i++) {
            cur.add(nums[i]);
            subsets(res, cur, nums, i + 1);
            cur.remove(cur.size() - 1);
        }
    }

    // 2.12 Binary Search (rotated)
    static int searchRotated(int[] a, int t) {
        int l = 0, r = a.length - 1;
        while (l <= r) {
            int m = l + (r - l) / 2;
            if (a[m] == t) return m;
            if (a[l] <= a[m]) {
                if (a[l] <= t && t < a[m]) r = m - 1; else l = m + 1;
            } else {
                if (a[m] < t && t <= a[r]) l = m + 1; else r = m - 1;
            }
        }
        return -1;
    }

    // 2.13 Monotonic Stack
    static int[] dailyTemps(int[] t) {
        int[] ans = new int[t.length];
        Deque<Integer> st = new ArrayDeque<>();
        for (int i = 0; i < t.length; i++) {
            while (!st.isEmpty() && t[i] > t[st.peek()]) {
                int idx = st.pop();
                ans[idx] = i - idx;
            }
            st.push(i);
        }
        // remaining indices have 0 (default)
        return ans;
    }

    static int largestRect(int[] h) {
        Deque<Integer> st = new ArrayDeque<>();
        int mx = 0;
        for (int i = 0; i <= h.length; i++) {
            int cur = i == h.length ? 0 : h[i];
            while (!st.isEmpty() && cur < h[st.peek()]) {
                int height = h[st.pop()];
                int w = st.isEmpty() ? i : i - st.peek() - 1;
                mx = Math.max(mx, height * w);
            }
            st.push(i);
        }
        return mx;
    }

    // 2.14 Prefix Sum + HashMap (subarray sum = k)
    static int subarraySum(int[] nums, int k) {
        Map<Integer, Integer> pref = new HashMap<>();
        pref.put(0, 1);
        int sum = 0, cnt = 0;
        for (int x : nums) {
            sum += x;
            cnt += pref.getOrDefault(sum - k, 0);
            pref.put(sum, pref.getOrDefault(sum, 0) + 1);
        }
        return cnt;
    }

    // 2.15 DP (0/1 knapsack, coin change, LCS)
    static boolean canPartition(int[] nums) {
        int s = Arrays.stream(nums).sum();
        if (s % 2 == 1) return false;
        boolean[] dp = new boolean[s / 2 + 1];
        dp[0] = true;
        for (int x : nums) for (int j = s / 2; j >= x; j--) dp[j] |= dp[j - x];
        return dp[s / 2];
    }

    static int coinChange(int[] coins, int amt) {
        int[] dp = new int[amt + 1];
        Arrays.fill(dp, amt + 1);
        dp[0] = 0;
        for (int i = 1; i <= amt; i++)
            for (int c : coins)
                if (c <= i) dp[i] = Math.min(dp[i], dp[i - c] + 1);
        return dp[amt] > amt ? -1 : dp[amt];
    }

    static int lcs(String a, String b) {
        int[][] dp = new int[a.length() + 1][b.length() + 1];
        for (int i = 1; i <= a.length(); i++)
            for (int j = 1; j <= b.length(); j++)
                dp[i][j] = a.charAt(i - 1) == b.charAt(j - 1) ? dp[i - 1][j - 1] + 1
                        : Math.max(dp[i - 1][j], dp[i][j - 1]);
        return dp[a.length()][b.length()];
    }

    // 2.16 Graph (BFS/DFS, Topo, Dijkstra, UF)
    static void dfsIslands(char[][] g, int i, int j) {
        if (i < 0 || j < 0 || i >= g.length || j >= g[0].length || g[i][j] != '1') return;
        g[i][j] = '0';
        dfsIslands(g, i + 1, j); dfsIslands(g, i - 1, j);
        dfsIslands(g, i, j + 1); dfsIslands(g, i, j - 1);
    }

    static boolean canFinish(int n, int[][] pre) {
        List<List<Integer>> g = new ArrayList<>();
        for (int i = 0; i < n; i++) g.add(new ArrayList<>());
        int[] in = new int[n];
        for (int[] e : pre) { g.get(e[1]).add(e[0]); in[e[0]]++; }
        Queue<Integer> q = new LinkedList<>();
        for (int i = 0; i < n; i++) if (in[i] == 0) q.offer(i);
        int visited = 0;
        while (!q.isEmpty()) {
            int u = q.poll(); visited++;
            for (int v : g.get(u)) if (--in[v] == 0) q.offer(v);
        }
        return visited == n;
    }

    static int[] dijkstra(List<int[]>[] g, int s) {
        int n = g.length;
        int[] d = new int[n];
        Arrays.fill(d, Integer.MAX_VALUE);
        d[s] = 0;
        PriorityQueue<int[]> pq = new PriorityQueue<>((a, b) -> a[1] - b[1]);
        pq.offer(new int[]{s, 0});
        while (!pq.isEmpty()) {
            int[] cur = pq.poll();
            int u = cur[0], du = cur[1];
            if (du > d[u]) continue;
            for (int[] e : g[u]) {
                int v = e[0], w = e[1];
                if (d[v] > du + w) {
                    d[v] = du + w;
                    pq.offer(new int[]{v, d[v]});
                }
            }
        }
        return d;
    }

    // 2.17 Fenwick Tree (Binary Indexed Tree)
    static class FenwickTree {
        int[] bit;
        int n;
        FenwickTree(int n) { this.n = n; bit = new int[n + 1]; }
        void add(int i, int delta) {
            i++;
            while (i <= n) { bit[i] += delta; i += i & -i; }
        }
        int sum(int i) {
            int s = 0; i++;
            while (i > 0) { s += bit[i]; i -= i & -i; }
            return s;
        }
        int rangeSum(int l, int r) { return sum(r) - sum(l - 1); }
    }

    // 2.18 KMP
    static int[] kmp(String p) {
        int[] lps = new int[p.length()];
        int len = 0, i = 1;
        while (i < p.length()) {
            if (p.charAt(i) == p.charAt(len)) lps[i++] = ++len;
            else if (len != 0) len = lps[len - 1];
            else lps[i++] = 0;
        }
        return lps;
    }

    static List<Integer> searchKMP(String txt, String pat) {
        List<Integer> ans = new ArrayList<>();
        int[] lps = kmp(pat);
        int i = 0, j = 0;
        while (i < txt.length()) {
            if (txt.charAt(i) == pat.charAt(j)) { i++; j++; }
            if (j == pat.length()) {
                ans.add(i - j);
                j = lps[j - 1];
            } else if (i < txt.length() && txt.charAt(i) != pat.charAt(j)) {
                if (j != 0) j = lps[j - 1]; else i++;
            }
        }
        return ans;
    }

    // 3. UTILITY SHORTCUTS
    static boolean isValid(String s) {
        Deque<Character> st = new ArrayDeque<>();
        for (char c : s.toCharArray()) {
            if (c == '(' || c == '[' || c == '{') st.push(c);
            else {
                if (st.isEmpty()) return false;
                char open = st.pop();
                if ((c == ')' && open != '(') || (c == ']' && open != '[') || (c == '}' && open != '{')) return false;
            }
        }
        return st.isEmpty();
    }

    static int[] twoSum(int[] nums, int t) {
        Map<Integer, Integer> m = new HashMap<>();
        for (int i = 0; i < nums.length; i++) {
            if (m.containsKey(t - nums[i])) return new int[]{m.get(t - nums[i]), i};
            m.put(nums[i], i);
        }
        return new int[]{-1, -1};
    }

    // 4. MAIN DEMO
    public static void main(String[] args) {
        System.out.println("longestNoRepeat(\"abcabcbb\") → " + longestNoRepeat("abcabcbb"));
        System.out.println("slidingMax([1,3,-1,-3,5,3,6,7],3) → " + slidingMax(new int[]{1, 3, -1, -3, 5, 3, 6, 7}, 3));
        System.out.println("dailyTemps([73,74,75,71,69,72,76,73]) → " + Arrays.toString(dailyTemps(new int[]{73, 74, 75, 71, 69, 72, 76, 73})));
        System.out.println("subarraySum([1,1,1],2) → " + subarraySum(new int[]{1, 1, 1}, 2));
        System.out.println("isValid(\"()[]{}\") → " + isValid("()[]{}"));
        System.out.println("twoSum([2,7,11,15],9) → " + Arrays.toString(twoSum(new int[]{2, 7, 11, 15}, 9)));
        LRUCache lru = new LRUCache(2);
        lru.put(1, 1); lru.put(2, 2);
        System.out.println("LRU get(1) → " + lru.get(1));
        lru.put(3, 3);
        System.out.println("LRU get(2) → " + lru.get(2));
        System.out.println("KMP search(\"abababcababc\",\"ababc\") → " + searchKMP("abababcababc", "ababc"));
        System.out.println("---");
        System.out.println("Merge K lists example omitted (needs actual ListNode arrays).");
    }
}