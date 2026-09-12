import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class TwoPointersPatterns {
    public static int[] twoSumSorted(int[] arr, int target) {
        int left = 0;
        int right = arr.length - 1;
        while (left < right) {
            int sum = arr[left] + arr[right];
            if (sum == target) return new int[]{left, right};
            if (sum < target) left++;
            else right--;
        }
        return new int[]{-1, -1};
    }

    public static int removeDuplicatesSorted(int[] arr) {
        if (arr.length == 0) return 0;
        int write = 1;
        for (int i = 1; i < arr.length; i++) {
            if (arr[i] != arr[i - 1]) arr[write++] = arr[i];
        }
        return write;
    }

    public static List<List<Integer>> threeSum(int[] arr) {
        Arrays.sort(arr);
        List<List<Integer>> result = new ArrayList<>();
        for (int i = 0; i < arr.length - 2; i++) {
            if (i > 0 && arr[i] == arr[i - 1]) continue;
            int left = i + 1;
            int right = arr.length - 1;
            while (left < right) {
                int sum = arr[i] + arr[left] + arr[right];
                if (sum == 0) {
                    result.add(List.of(arr[i], arr[left], arr[right]));
                    while (left < right && arr[left] == arr[left + 1]) left++;
                    while (left < right && arr[right] == arr[right - 1]) right--;
                    left++;
                    right--;
                } else if (sum < 0) left++;
                else right--;
            }
        }
        return result;
    }

    public static int containerWithMostWater(int[] heights) {
        int left = 0;
        int right = heights.length - 1;
        int maxArea = 0;
        while (left < right) {
            int width = right - left;
            maxArea = Math.max(maxArea, Math.min(heights[left], heights[right]) * width);
            if (heights[left] < heights[right]) left++;
            else right--;
        }
        return maxArea;
    }

    public static boolean isPalindrome(String s) {
        int left = 0;
        int right = s.length() - 1;
        while (left < right) {
            while (left < right && !Character.isLetterOrDigit(s.charAt(left))) left++;
            while (left < right && !Character.isLetterOrDigit(s.charAt(right))) right--;
            if (Character.toLowerCase(s.charAt(left)) != Character.toLowerCase(s.charAt(right))) return false;
            left++;
            right--;
        }
        return true;
    }

    public static void main(String[] args) {
        if (!Arrays.equals(twoSumSorted(new int[]{2, 7, 11, 15}, 9), new int[]{0, 1})) throw new AssertionError();
        if (removeDuplicatesSorted(new int[]{1, 1, 2}) != 2) throw new AssertionError();
        if (threeSum(new int[]{-1, 0, 1, 2, -1, -4}).size() != 2) throw new AssertionError();
        if (containerWithMostWater(new int[]{1, 8, 6, 2, 5, 4, 8, 3, 7}) != 49) throw new AssertionError();
        if (!isPalindrome("A man, a plan, a canal: Panama")) throw new AssertionError();
    }
}
