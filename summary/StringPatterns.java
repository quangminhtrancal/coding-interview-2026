import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class StringPatterns {
    public static boolean isAnagram(String a, String b) {
        if (a.length() != b.length()) return false;
        int[] counts = new int[256];
        for (char c : a.toCharArray()) counts[c]++;
        for (char c : b.toCharArray()) {
            if (--counts[c] < 0) return false;
        }
        return true;
    }

    public static boolean validParentheses(String s) {
        Deque<Character> stack = new ArrayDeque<>();
        Map<Character, Character> mapping = Map.of(')', '(', '}', '{', ']', '[');
        for (char c : s.toCharArray()) {
            if (mapping.containsKey(c)) {
                if (stack.isEmpty() || stack.pop() != mapping.get(c)) return false;
            } else stack.push(c);
        }
        return stack.isEmpty();
    }

    public static String reverseWords(String s) {
        String[] words = s.trim().split("\\s+");
        StringBuilder out = new StringBuilder();
        for (int i = words.length - 1; i >= 0; i--) {
            out.append(words[i]);
            if (i > 0) out.append(' ');
        }
        return words.length == 1 && words[0].isEmpty() ? "" : out.toString();
    }

    public static String compressString(String s) {
        if (s.isEmpty()) return "";
        StringBuilder out = new StringBuilder();
        int count = 1;
        for (int i = 1; i < s.length(); i++) {
            if (s.charAt(i) == s.charAt(i - 1)) count++;
            else {
                out.append(s.charAt(i - 1)).append(count);
                count = 1;
            }
        }
        out.append(s.charAt(s.length() - 1)).append(count);
        return out.length() < s.length() ? out.toString() : s;
    }

    public static String longestCommonPrefix(String[] strs) {
        if (strs.length == 0) return "";
        String prefix = strs[0];
        for (int i = 1; i < strs.length; i++) {
            while (!strs[i].startsWith(prefix)) {
                prefix = prefix.substring(0, prefix.length() - 1);
                if (prefix.isEmpty()) return "";
            }
        }
        return prefix;
    }

    public static int levenshtein(String a, String b) {
        int m = a.length();
        int n = b.length();
        int[][] dp = new int[m + 1][n + 1];
        for (int i = 0; i <= m; i++) dp[i][0] = i;
        for (int j = 0; j <= n; j++) dp[0][j] = j;
        for (int i = 1; i <= m; i++) {
            for (int j = 1; j <= n; j++) {
                if (a.charAt(i - 1) == b.charAt(j - 1)) dp[i][j] = dp[i - 1][j - 1];
                else dp[i][j] = 1 + Math.min(dp[i - 1][j - 1], Math.min(dp[i - 1][j], dp[i][j - 1]));
            }
        }
        return dp[m][n];
    }

    public static Map<String, List<String>> groupAnagrams(String[] strs) {
        Map<String, List<String>> groups = new HashMap<>();
        for (String s : strs) {
            char[] chars = s.toCharArray();
            java.util.Arrays.sort(chars);
            groups.computeIfAbsent(new String(chars), k -> new ArrayList<>()).add(s);
        }
        return groups;
    }

    public static int kmpSearch(String text, String pattern) {
        if (pattern.isEmpty()) return 0;
        int[] lps = new int[pattern.length()];
        int len = 0;
        for (int i = 1; i < pattern.length();) {
            if (pattern.charAt(i) == pattern.charAt(len)) lps[i++] = ++len;
            else if (len != 0) len = lps[len - 1];
            else lps[i++] = 0;
        }
        int i = 0;
        int j = 0;
        while (i < text.length()) {
            if (text.charAt(i) == pattern.charAt(j)) {
                i++;
                j++;
                if (j == pattern.length()) return i - j;
            } else if (j != 0) j = lps[j - 1];
            else i++;
        }
        return -1;
    }

    public static void main(String[] args) {
        if (!isAnagram("listen", "silent")) throw new AssertionError();
        if (!validParentheses("()[]{}")) throw new AssertionError();
        if (validParentheses("(]")) throw new AssertionError();
        if (!reverseWords("hello world").equals("world hello")) throw new AssertionError();
        if (!longestCommonPrefix(new String[]{"flower", "flow", "flight"}).equals("fl")) throw new AssertionError();
        if (levenshtein("kitten", "sitting") != 3) throw new AssertionError();
        if (kmpSearch("hello world", "world") != 6) throw new AssertionError();
    }
}
