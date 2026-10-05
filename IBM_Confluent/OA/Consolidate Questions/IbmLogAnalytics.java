import java.time.Instant;
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

public class IbmLogAnalytics {
    public record Entry(Instant ts, String level, String service, String msg) {}

    public static Entry parse(String line) {
        String[] p = line.split(" ", 4);
        return new Entry(Instant.parse(p[0]), p[1], p[2], p.length > 3 ? p[3] : "");
    }

    public static Map<String, Long> errorCountByService(List<String> lines, Instant from, Instant to) {
        return lines.stream()
                .map(IbmLogAnalytics::parse)
                .filter(e -> !e.ts().isBefore(from) && !e.ts().isAfter(to))
                .filter(e -> e.level().equals("ERROR"))
                .collect(Collectors.groupingBy(Entry::service, Collectors.counting()));
    }

    public static List<String> topK(Map<String, Long> counts, int k) {
        return counts.entrySet().stream()
                .sorted(Map.Entry.<String, Long>comparingByValue(Comparator.reverseOrder())
                        .thenComparing(Map.Entry.comparingByKey()))
                .limit(k)
                .map(Map.Entry::getKey)
                .toList();
    }

    public static void main(String[] args) {
        List<String> lines = List.of(
                "2026-09-01T10:00:00Z ERROR checkout timeout",
                "2026-09-01T11:00:00Z ERROR checkout fail",
                "2026-09-01T12:00:00Z ERROR search oom",
                "2026-09-01T13:00:00Z INFO checkout ok");
        Map<String, Long> c = errorCountByService(lines,
                Instant.parse("2026-09-01T00:00:00Z"), Instant.parse("2026-09-01T23:59:59Z"));
        if (c.get("checkout") != 2L || c.get("search") != 1L) throw new AssertionError("counts wrong");
        if (!topK(c, 1).equals(List.of("checkout"))) throw new AssertionError("topK wrong");
        System.out.println("IbmLogAnalytics OK");
    }
}
