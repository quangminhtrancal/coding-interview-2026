import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class TreeGraphPatterns {
    public static class TreeNode {
        int val;
        TreeNode left;
        TreeNode right;
        TreeNode(int val) { this.val = val; }
    }

    public static List<List<Integer>> levelOrder(TreeNode root) {
        List<List<Integer>> result = new ArrayList<>();
        if (root == null) return result;
        Deque<TreeNode> queue = new ArrayDeque<>(List.of(root));
        while (!queue.isEmpty()) {
            int size = queue.size();
            List<Integer> level = new ArrayList<>();
            for (int i = 0; i < size; i++) {
                TreeNode node = queue.poll();
                level.add(node.val);
                if (node.left != null) queue.add(node.left);
                if (node.right != null) queue.add(node.right);
            }
            result.add(level);
        }
        return result;
    }

    public static int maxDepth(TreeNode root) {
        if (root == null) return 0;
        return 1 + Math.max(maxDepth(root.left), maxDepth(root.right));
    }

    public static boolean hasPathSum(TreeNode root, int target) {
        if (root == null) return false;
        if (root.left == null && root.right == null) return root.val == target;
        return hasPathSum(root.left, target - root.val) || hasPathSum(root.right, target - root.val);
    }

    public static List<Integer> topologicalSort(int vertices, int[][] edges) {
        Map<Integer, List<Integer>> graph = new HashMap<>();
        int[] inDegree = new int[vertices];
        for (int[] e : edges) {
            graph.computeIfAbsent(e[0], k -> new ArrayList<>()).add(e[1]);
            inDegree[e[1]]++;
        }
        Deque<Integer> queue = new ArrayDeque<>();
        for (int i = 0; i < vertices; i++) if (inDegree[i] == 0) queue.add(i);
        List<Integer> result = new ArrayList<>();
        while (!queue.isEmpty()) {
            int v = queue.poll();
            result.add(v);
            for (int n : graph.getOrDefault(v, List.of())) {
                if (--inDegree[n] == 0) queue.add(n);
            }
        }
        return result.size() == vertices ? result : List.of();
    }

    public static class UnionFind {
        int[] parent;
        int[] rank;
        UnionFind(int size) {
            parent = new int[size];
            rank = new int[size];
            for (int i = 0; i < size; i++) parent[i] = i;
        }
        int find(int x) {
            if (parent[x] != x) parent[x] = find(parent[x]);
            return parent[x];
        }
        boolean union(int x, int y) {
            int rx = find(x);
            int ry = find(y);
            if (rx == ry) return false;
            if (rank[rx] < rank[ry]) parent[rx] = ry;
            else if (rank[rx] > rank[ry]) parent[ry] = rx;
            else {
                parent[ry] = rx;
                rank[rx]++;
            }
            return true;
        }
    }

    public static int nextGreaterElementCount(int[] nums) {
        int[] result = new int[nums.length];
        Deque<Integer> stack = new ArrayDeque<>();
        for (int i = 0; i < nums.length; i++) {
            while (!stack.isEmpty() && nums[i] > nums[stack.peek()]) result[stack.pop()] = nums[i];
            stack.push(i);
        }
        for (int idx : stack) result[idx] = -1;
        return result.length;
    }

    public static void main(String[] args) {
        TreeNode root = new TreeNode(1);
        root.left = new TreeNode(2);
        root.right = new TreeNode(3);
        if (levelOrder(root).size() != 2) throw new AssertionError();
        if (maxDepth(root) != 2) throw new AssertionError();
        if (!hasPathSum(root, 3)) throw new AssertionError();
        if (topologicalSort(3, new int[][]{{0, 1}, {1, 2}}).size() != 3) throw new AssertionError();
        UnionFind uf = new UnionFind(3);
        if (!uf.union(0, 1)) throw new AssertionError();
        if (uf.union(0, 1)) throw new AssertionError();
    }
}
