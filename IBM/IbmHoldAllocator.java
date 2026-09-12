import java.time.Instant;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class IbmHoldAllocator {
    public record Hold(long id, long patronId, long itemId, Instant createdAt) {}
    public record Notification(long id, long patronId, long holdId, Instant createdAt) {}

    private final List<Hold> holds = new ArrayList<>();
    private final List<Notification> sent = new ArrayList<>();
    private final Set<Long> notifiedHoldIds = new HashSet<>();
    private long seq = 0;

    public synchronized void addHold(Hold h) {
        holds.add(h);
    }

    public synchronized List<Notification> allocate(long itemId, int copies, Instant now) {
        if (copies < 0) throw new IllegalArgumentException("copies cannot be negative");
        List<Hold> waiting = holds.stream()
                .filter(h -> h.itemId() == itemId && !notifiedHoldIds.contains(h.id()))
                .sorted(Comparator.comparing(Hold::createdAt).thenComparingLong(Hold::id))
                .limit(copies)
                .toList();
        List<Notification> out = new ArrayList<>();
        for (Hold h : waiting) {
            notifiedHoldIds.add(h.id());
            Notification n = new Notification(++seq, h.patronId(), h.id(), now);
            sent.add(n);
            out.add(n);
        }
        return out;
    }

    public synchronized List<Notification> forPatronNewestFirst(long patronId) {
        return sent.stream()
                .filter(n -> n.patronId() == patronId)
                .sorted(Comparator.comparing(Notification::createdAt).thenComparingLong(Notification::id).reversed())
                .toList();
    }

    public static void main(String[] args) {
        IbmHoldAllocator a = new IbmHoldAllocator();
        Instant t = Instant.parse("2026-09-08T12:00:00Z");
        a.addHold(new Hold(2, 20, 7, t.minusSeconds(7200)));
        a.addHold(new Hold(1, 10, 7, t.minusSeconds(7200)));
        a.addHold(new Hold(3, 30, 7, t.minusSeconds(3600)));
        if (!a.allocate(7, 2, t).stream().map(Notification::holdId).toList().equals(List.of(1L, 2L)))
            throw new AssertionError("FIFO wrong");
        if (a.allocate(7, 2, t).stream().map(Notification::holdId).toList().equals(List.of(1L, 2L)))
            throw new AssertionError("must be idempotent");
        System.out.println("IbmHoldAllocator OK");
    }
}
