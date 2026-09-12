import java.util.ArrayList;
import java.util.Arrays;
import java.util.Comparator;
import java.util.List;

public class IntervalPatterns {
    public static int[][] mergeIntervals(int[][] intervals) {
        if (intervals.length == 0) return new int[0][];
        Arrays.sort(intervals, Comparator.comparingInt(a -> a[0]));
        List<int[]> merged = new ArrayList<>();
        merged.add(intervals[0]);
        for (int i = 1; i < intervals.length; i++) {
            int[] last = merged.get(merged.size() - 1);
            if (intervals[i][0] <= last[1]) last[1] = Math.max(last[1], intervals[i][1]);
            else merged.add(intervals[i]);
        }
        return merged.toArray(new int[0][]);
    }

    public static int[][] insertInterval(int[][] intervals, int[] newInterval) {
        List<int[]> result = new ArrayList<>();
        int i = 0;
        while (i < intervals.length && intervals[i][1] < newInterval[0]) result.add(intervals[i++]);
        while (i < intervals.length && intervals[i][0] <= newInterval[1]) {
            newInterval[0] = Math.min(newInterval[0], intervals[i][0]);
            newInterval[1] = Math.max(newInterval[1], intervals[i][1]);
            i++;
        }
        result.add(newInterval);
        while (i < intervals.length) result.add(intervals[i++]);
        return result.toArray(new int[0][]);
    }

    public static int[][] intervalIntersection(int[][] a, int[][] b) {
        List<int[]> result = new ArrayList<>();
        int i = 0;
        int j = 0;
        while (i < a.length && j < b.length) {
            int start = Math.max(a[i][0], b[j][0]);
            int end = Math.min(a[i][1], b[j][1]);
            if (start <= end) result.add(new int[]{start, end});
            if (a[i][1] < b[j][1]) i++;
            else j++;
        }
        return result.toArray(new int[0][]);
    }

    public static int findMissingNumber(int[] nums) {
        int i = 0;
        int n = nums.length;
        while (i < n) {
            int correct = nums[i];
            if (nums[i] < n && nums[i] != nums[correct]) {
                int tmp = nums[i];
                nums[i] = nums[correct];
                nums[correct] = tmp;
            } else i++;
        }
        for (int k = 0; k < n; k++) if (nums[k] != k) return k;
        return n;
    }

    public static int singleNumber(int[] nums) {
        int result = 0;
        for (int num : nums) result ^= num;
        return result;
    }

    public static void main(String[] args) {
        if (mergeIntervals(new int[][]{{1, 3}, {2, 6}, {8, 10}}).length != 2) throw new AssertionError();
        if (insertInterval(new int[][]{{1, 3}, {6, 9}}, new int[]{2, 5})[0][1] != 5) throw new AssertionError();
        if (findMissingNumber(new int[]{3, 0, 1}) != 2) throw new AssertionError();
        if (singleNumber(new int[]{2, 2, 1}) != 1) throw new AssertionError();
    }
}
