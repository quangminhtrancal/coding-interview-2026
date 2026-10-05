import java.util.concurrent.Callable;

public class IbmCircuitBreaker {
    public enum State { CLOSED, OPEN, HALF_OPEN }

    private final int failureThreshold;
    private final long recoveryMillis;
    private State state = State.CLOSED;
    private int failures = 0;
    private long openedAt = 0;

    public IbmCircuitBreaker(int failureThreshold, long recoveryMillis) {
        if (failureThreshold <= 0 || recoveryMillis <= 0) throw new IllegalArgumentException("positive config required");
        this.failureThreshold = failureThreshold;
        this.recoveryMillis = recoveryMillis;
    }

    public synchronized <T> T call(Callable<T> op, long nowMillis) throws Exception {
        if (state == State.OPEN && nowMillis - openedAt >= recoveryMillis) {
            state = State.HALF_OPEN;
        }
        if (state == State.OPEN) throw new IllegalStateException("circuit open");
        try {
            T out = op.call();
            onSuccess();
            return out;
        } catch (Exception e) {
            onFailure(nowMillis);
            throw e;
        }
    }

    private void onSuccess() {
        failures = 0;
        state = State.CLOSED;
    }

    private void onFailure(long now) {
        failures++;
        if (state == State.HALF_OPEN || failures >= failureThreshold) {
            state = State.OPEN;
            openedAt = now;
        }
    }

    public synchronized State state() {
        return state;
    }

    public static void main(String[] args) throws Exception {
        IbmCircuitBreaker b = new IbmCircuitBreaker(2, 1000);
        try { b.call(() -> { throw new RuntimeException("x"); }, 0); } catch (Exception ignored) {}
        try { b.call(() -> { throw new RuntimeException("x"); }, 10); } catch (Exception ignored) {}
        if (b.state() != State.OPEN) throw new AssertionError("should be open");
        try {
            b.call(() -> "ok", 20);
            throw new AssertionError("should reject while open");
        } catch (IllegalStateException expected) {}
        if (!b.call(() -> "ok", 2000).equals("ok")) throw new AssertionError("half-open recovery");
        if (b.state() != State.CLOSED) throw new AssertionError("should close after success");
        System.out.println("IbmCircuitBreaker OK");
    }
}
