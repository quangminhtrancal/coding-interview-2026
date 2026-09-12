import java.util.ArrayList;
import java.util.List;

public class BinarySearchPatterns {
    public static int binarySearch(int[] arr, int target) {
        int left = 0;
        int right = arr.length - 1;
        while (left <= right) {
            int mid = left + (right - left) / 2;
            if (arr[mid] == target) return mid;
            if (arr[mid] < target) left = mid + 1;
            else right = mid - 1;
        }
        return -1;
    }

    public static int firstOccurrence(int[] arr, int target) {
        int left = 0;
        int right = arr.length - 1;
        int result = -1;
        while (left <= right) {
            int mid = left + (right - left) / 2;
            if (arr[mid] == target) {
                result = mid;
                right = mid - 1;
            } else if (arr[mid] < target) left = mid + 1;
            else right = mid - 1;
        }
        return result;
    }

    public static int searchInsert(int[] arr, int target) {
        int left = 0;
        int right = arr.length - 1;
        while (left <= right) {
            int mid = left + (right - left) / 2;
            if (arr[mid] == target) return mid;
            if (arr[mid] < target) left = mid + 1;
            else right = mid - 1;
        }
        return left;
    }

    public static int searchRotated(int[] arr, int target) {
        int left = 0;
        int right = arr.length - 1;
        while (left <= right) {
            int mid = left + (right - left) / 2;
            if (arr[mid] == target) return mid;
            if (arr[left] <= arr[mid]) {
                if (arr[left] <= target && target < arr[mid]) right = mid - 1;
                else left = mid + 1;
            } else {
                if (arr[mid] < target && target <= arr[right]) left = mid + 1;
                else right = mid - 1;
            }
        }
        return -1;
    }

    public static int findMinRotated(int[] arr) {
        int left = 0;
        int right = arr.length - 1;
        while (left < right) {
            int mid = left + (right - left) / 2;
            if (arr[mid] > arr[right]) left = mid + 1;
            else right = mid;
        }
        return arr[left];
    }

    public static int findPeak(int[] arr) {
        int left = 0;
        int right = arr.length - 1;
        while (left < right) {
            int mid = left + (right - left) / 2;
            if (arr[mid] < arr[mid + 1]) left = mid + 1;
            else right = mid;
        }
        return left;
    }

    public static boolean searchMatrix(int[][] matrix, int target) {
        if (matrix.length == 0 || matrix[0].length == 0) return false;
        int m = matrix.length;
        int n = matrix[0].length;
        int left = 0;
        int right = m * n - 1;
        while (left <= right) {
            int mid = left + (right - left) / 2;
            int val = matrix[mid / n][mid % n];
            if (val == target) return true;
            if (val < target) left = mid + 1;
            else right = mid - 1;
        }
        return false;
    }

    public static Long latestValueAtOrBefore(List<long[]> history, long timestamp) {
        int left = 0;
        int right = history.size() - 1;
        int result = -1;
        while (left <= right) {
            int mid = left + (right - left) / 2;
            if (history.get(mid)[0] <= timestamp) {
                result = mid;
                left = mid + 1;
            } else right = mid - 1;
        }
        return result < 0 ? null : history.get(result)[1];
    }

    public static void main(String[] args) {
        if (binarySearch(new int[]{1, 2, 3, 4}, 3) != 2) throw new AssertionError();
        if (firstOccurrence(new int[]{1, 2, 2, 3}, 2) != 1) throw new AssertionError();
        if (searchInsert(new int[]{1, 3, 5}, 4) != 2) throw new AssertionError();
        if (searchRotated(new int[]{4, 5, 6, 7, 0, 1, 2}, 0) != 4) throw new AssertionError();
        if (findMinRotated(new int[]{4, 5, 6, 7, 0, 1, 2}) != 0) throw new AssertionError();
        if (!searchMatrix(new int[][]{{1, 3}, {5, 7}}, 5)) throw new AssertionError();
        List<long[]> h = new ArrayList<>(List.of(new long[]{10, 100}, new long[]{20, 200}));
        if (!latestValueAtOrBefore(h, 15).equals(100L)) throw new AssertionError();
    }
}
