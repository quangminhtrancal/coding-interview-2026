public class LinkedListPatterns {
    public static class ListNode {
        int val;
        ListNode next;
        ListNode(int val) { this.val = val; }
        ListNode(int val, ListNode next) { this.val = val; this.next = next; }
    }

    public static boolean hasCycle(ListNode head) {
        ListNode slow = head;
        ListNode fast = head;
        while (fast != null && fast.next != null) {
            slow = slow.next;
            fast = fast.next.next;
            if (slow == fast) return true;
        }
        return false;
    }

    public static ListNode findCycleStart(ListNode head) {
        ListNode slow = head;
        ListNode fast = head;
        while (fast != null && fast.next != null) {
            slow = slow.next;
            fast = fast.next.next;
            if (slow == fast) break;
        }
        if (fast == null || fast.next == null) return null;
        slow = head;
        while (slow != fast) {
            slow = slow.next;
            fast = fast.next;
        }
        return slow;
    }

    public static ListNode middleNode(ListNode head) {
        ListNode slow = head;
        ListNode fast = head;
        while (fast != null && fast.next != null) {
            slow = slow.next;
            fast = fast.next.next;
        }
        return slow;
    }

    public static ListNode reverseList(ListNode head) {
        ListNode prev = null;
        ListNode current = head;
        while (current != null) {
            ListNode next = current.next;
            current.next = prev;
            prev = current;
            current = next;
        }
        return prev;
    }

    public static boolean isHappyNumber(int n) {
        int slow = n;
        int fast = n;
        do {
            slow = nextHappy(slow);
            fast = nextHappy(nextHappy(fast));
            if (fast == 1) return true;
        } while (slow != fast);
        return false;
    }

    private static int nextHappy(int num) {
        int total = 0;
        while (num > 0) {
            int d = num % 10;
            total += d * d;
            num /= 10;
        }
        return total;
    }

    private static ListNode build(int... values) {
        ListNode dummy = new ListNode(0);
        ListNode current = dummy;
        for (int v : values) {
            current.next = new ListNode(v);
            current = current.next;
        }
        return dummy.next;
    }

    public static void main(String[] args) {
        if (middleNode(build(1, 2, 3, 4, 5)).val != 3) throw new AssertionError();
        if (reverseList(build(1, 2, 3)).val != 3) throw new AssertionError();
        if (!isHappyNumber(19)) throw new AssertionError();
        if (isHappyNumber(2)) throw new AssertionError();
        ListNode cycled = build(1, 2, 3);
        cycled.next.next.next = cycled.next;
        if (!hasCycle(cycled)) throw new AssertionError();
        if (findCycleStart(cycled).val != 2) throw new AssertionError();
    }
}
