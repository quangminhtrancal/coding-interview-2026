import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.PriorityQueue;

public class HeapTopKPatterns {
    public static List<Integer> kLargest(int[] nums, int k) {
        PriorityQueue<Integer> heap = new PriorityQueue<>();
        for (int num : nums) {
            if (heap.size() < k) heap.add(num);
            else if (num > heap.peek()) {
                heap.poll();
                heap.add(num);
            }
        }
        return new ArrayList<>(heap);
    }

    public static List<Integer> topKFrequent(int[] nums, int k) {
        Map<Integer, Integer> counts = new HashMap<>();
        for (int num : nums) counts.merge(num, 1, Integer::sum);
        PriorityQueue<Map.Entry<Integer, Integer>> heap = new PriorityQueue<>(Comparator.comparingInt(Map.Entry::getValue));
        for (Map.Entry<Integer, Integer> e : counts.entrySet()) {
            heap.add(e);
            if (heap.size() > k) heap.poll();
        }
        List<Integer> result = new ArrayList<>();
        while (!heap.isEmpty()) result.add(heap.poll().getKey());
        return result;
    }

    public static int[][] kClosest(int[][] points, int k) {
        PriorityQueue<int[]> heap = new PriorityQueue<>(Comparator.comparingInt(p -> p[0] * p[0] + p[1] * p[1]));
        for (int[] p : points) {
            heap.add(p);
        }
        int[][] result = new int[k][];
        for (int i = 0; i < k; i++) result[i] = heap.poll();
        return result;
    }

    public static int[][] mergeKSortedArrays(int[][] arrays) {
        PriorityQueue<int[]> heap = new PriorityQueue<>(Comparator.comparingInt(a -> a[0]));
        for (int i = 0; i < arrays.length; i++) {
            if (arrays[i].length > 0) heap.add(new int[]{arrays[i][0], i, 0});
        }
        List<Integer> merged = new ArrayList<>();
        while (!heap.isEmpty()) {
            int[] top = heap.poll();
            merged.add(top[0]);
            int arrayIdx = top[1];
            int elemIdx = top[2] + 1;
            if (elemIdx < arrays[arrayIdx].length) heap.add(new int[]{arrays[arrayIdx][elemIdx], arrayIdx, elemIdx});
        }
        return new int[][]{merged.stream().mapToInt(Integer::intValue).toArray()};
    }

    public static class MedianFinder {
        PriorityQueue<Integer> low = new PriorityQueue<>(Comparator.reverseOrder());
        PriorityQueue<Integer> high = new PriorityQueue<>();

        public void addNum(int num) {
            if (low.isEmpty() || num <= low.peek()) low.add(num);
            else high.add(num);
            if (low.size() > high.size() + 1) high.add(low.poll());
            else if (high.size() > low.size()) low.add(high.poll());
        }

        public double findMedian() {
            if (low.size() == high.size()) return (low.peek() + high.peek()) / 2.0;
            return low.peek();
        }
    }

    public static void main(String[] args) {
        if (kLargest(new int[]{3, 2, 1, 5, 6, 4}, 2).size() != 2) throw new AssertionError();
        if (topKFrequent(new int[]{1, 1, 1, 2, 2, 3}, 2).size() != 2) throw new AssertionError();
        if (kClosest(new int[][]{{1, 3}, {-2, 2}}, 1).length != 1) throw new AssertionError();
        MedianFinder finder = new MedianFinder();
        finder.addNum(1);
        finder.addNum(2);
        if (finder.findMedian() != 1.5) throw new AssertionError();
        finder.addNum(3);
        if (finder.findMedian() != 2.0) throw new AssertionError();
    }
}
