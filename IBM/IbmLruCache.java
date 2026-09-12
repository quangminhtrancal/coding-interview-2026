import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Optional;

public class IbmLruCache<K, V> {
    private final int capacity;
    private final Map<K, V> map;

    public IbmLruCache(int capacity) {
        if (capacity <= 0) throw new IllegalArgumentException("capacity must be positive");
        this.capacity = capacity;
        this.map = new LinkedHashMap<>(capacity, 0.75f, true) {
            @Override
            protected boolean removeEldestEntry(Map.Entry<K, V> e) {
                return size() > IbmLruCache.this.capacity;
            }
        };
    }

    public synchronized void put(K key, V value) {
        map.put(key, value);
    }

    public synchronized Optional<V> get(K key) {
        return Optional.ofNullable(map.get(key));
    }

    public synchronized int size() {
        return map.size();
    }

    public static void main(String[] args) {
        IbmLruCache<Integer, String> c = new IbmLruCache<>(2);
        c.put(1, "one");
        c.put(2, "two");
        c.get(1);
        c.put(3, "three");
        if (c.get(2).isPresent()) throw new AssertionError("2 should be evicted");
        if (!c.get(1).orElse("").equals("one")) throw new AssertionError("1 should remain");
        if (c.size() != 2) throw new AssertionError("size should be 2");
        System.out.println("IbmLruCache OK");
    }
}
