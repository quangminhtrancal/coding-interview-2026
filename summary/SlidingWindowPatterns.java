import java.util.HashMap;
import java.util.Map;

public class SlidingWindowPatterns {
    public static int maxSumSubarraySizeK(int[] arr, int k) {
        int windowSum = 0;
        for (int i = 0; i < k; i++) windowSum += arr[i];
        int maxSum = windowSum;
        for (int i = 0; i < arr.length - k; i++) {
            windowSum = windowSum - arr[i] + arr[i + k];
            maxSum = Math.max(maxSum, windowSum);
        }
        return maxSum;
    }

    public static int longestSubstringKDistinct(String s, int k) {
        if (k == 0) return 0;
        Map<Character, Integer> counts = new HashMap<>();
        int left = 0;
        int maxLen = 0;
        for (int right = 0; right < s.length(); right++) {
            counts.merge(s.charAt(right), 1, Integer::sum);
            while (counts.size() > k) {
                char c = s.charAt(left);
                counts.merge(c, -1, Integer::sum);
                if (counts.get(c) == 0) counts.remove(c);
                left++;
            }
            maxLen = Math.max(maxLen, right - left + 1);
        }
        return maxLen;
    }

    public static String minWindowSubstring(String s, String t) {
        if (s.isEmpty() || t.isEmpty()) return "";
        Map<Character, Integer> target = new HashMap<>();
        for (char c : t.toCharArray()) target.merge(c, 1, Integer::sum);
        int required = target.size();
        Map<Character, Integer> window = new HashMap<>();
        int formed = 0;
        int left = 0;
        int minLen = Integer.MAX_VALUE;
        int minLeft = 0;
        for (int right = 0; right < s.length(); right++) {
            char c = s.charAt(right);
            window.merge(c, 1, Integer::sum);
            if (target.containsKey(c) && window.get(c).intValue() == target.get(c).intValue()) formed++;
            while (left <= right && formed == required) {
                if (right - left + 1 < minLen) {
                    minLen = right - left + 1;
                    minLeft = left;
                }
                char lc = s.charAt(left);
                window.merge(lc, -1, Integer::sum);
                if (target.containsKey(lc) && window.get(lc) < target.get(lc)) formed--;
                left++;
            }
        }
        return minLen == Integer.MAX_VALUE ? "" : s.substring(minLeft, minLeft + minLen);
    }

    public static int longestSubstringWithoutRepeating(String s) {
        Map<Character, Integer> index = new HashMap<>();
        int maxLen = 0;
        int start = 0;
        for (int end = 0; end < s.length(); end++) {
            char c = s.charAt(end);
            if (index.containsKey(c) && index.get(c) >= start) start = index.get(c) + 1;
            index.put(c, end);
            maxLen = Math.max(maxLen, end - start + 1);
        }
        return maxLen;
    }

    public static void main(String[] args) {
        if (maxSumSubarraySizeK(new int[]{2, 1, 5, 1, 3, 2}, 3) != 9) throw new AssertionError();
        if (longestSubstringKDistinct("araaci", 2) != 4) throw new AssertionError();
        if (!minWindowSubstring("ADOBECODEBANC", "ABC").equals("BANC")) throw new AssertionError();
        if (longestSubstringWithoutRepeating("abcabcbb") != 3) throw new AssertionError();
    }
}
