import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.concurrent.ConcurrentHashMap;

public class IbmIdempotentOrders {
    public record Order(String idempotencyKey, String item, int qty, long createdAt) {}

    private final ConcurrentHashMap<String, Order> store = new ConcurrentHashMap<>();

    public boolean place(Order order) {
        if (order == null || order.idempotencyKey() == null) throw new IllegalArgumentException("key required");
        if (order.qty() <= 0) throw new IllegalArgumentException("qty must be positive");
        return store.putIfAbsent(order.idempotencyKey(), order) == null;
    }

    public List<Order> historyNewestFirst() {
        ArrayList<Order> out = new ArrayList<>(store.values());
        out.sort(Comparator.comparingLong(Order::createdAt).reversed());
        return out;
    }

    public static void main(String[] args) {
        IbmIdempotentOrders s = new IbmIdempotentOrders();
        if (!s.place(new Order("k1", "book", 1, 100))) throw new AssertionError("first k1 accepted");
        if (s.place(new Order("k1", "book", 1, 101))) throw new AssertionError("retry k1 rejected");
        if (!s.place(new Order("k2", "pen", 2, 200))) throw new AssertionError("k2 accepted");
        List<Order> h = s.historyNewestFirst();
        if (!h.get(0).idempotencyKey().equals("k2")) throw new AssertionError("newest first");
        System.out.println("IbmIdempotentOrders OK");
    }
}
