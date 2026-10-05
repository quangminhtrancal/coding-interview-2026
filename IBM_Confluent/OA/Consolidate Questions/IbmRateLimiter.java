import java.util.ArrayDeque;
import java.util.Deque;
import java.util.HashMap;
import java.util.Map;

public class IbmRateLimiter {
    private final int maxRequests;
    private final long windowMillis;
    private final Map<String, Deque<Long>> hits = new HashMap<>();

    public IbmRateLimiter(int maxRequests, long windowMillis) {
        if (maxRequests <= 0 || windowMillis <= 0) throw new IllegalArgumentException("positive limits required");
        this.maxRequests = maxRequests;
        this.windowMillis = windowMillis;
    }

    public synchronized boolean allow(String clientId, long nowMillis) {
        Deque<Long> q = hits.computeIfAbsent(clientId, k -> new ArrayDeque<>());
        while (!q.isEmpty() && nowMillis - q.peekFirst() >= windowMillis) q.pollFirst();
        if (q.size() >= maxRequests) return false;
        q.addLast(nowMillis);
        return true;
    }

    public static void main(String[] args) {
        IbmRateLimiter r = new IbmRateLimiter(2, 1000);
        check(r.allow("a", 0));
        check(r.allow("a", 100));
        check(!r.allow("a", 200));
        check(r.allow("a", 1000));
        check(r.allow("b", 200));
        System.out.println("IbmRateLimiter OK");
    }

    private static void check(boolean v) {
        if (!v) throw new AssertionError("check failed");
    }
}
