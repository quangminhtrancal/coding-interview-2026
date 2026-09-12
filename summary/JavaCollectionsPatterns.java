import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;
import java.util.stream.Collectors;

public class JavaCollectionsPatterns {
    public record FileRow(String name, int size, int expiry) {}

    public static List<FileRow> topNBySize(List<FileRow> rows, int n) {
        return rows.stream()
                .sorted(Comparator.comparingInt(FileRow::size).reversed())
                .limit(n)
                .toList();
    }

    public static List<FileRow> sortBySizeDescThenName(List<FileRow> rows) {
        return rows.stream()
                .sorted(Comparator.comparingInt(FileRow::size).reversed().thenComparing(FileRow::name))
                .toList();
    }

    public static Map<String, Integer> wordCount(String text) {
        Map<String, Integer> counts = new HashMap<>();
        for (String word : text.split("\\s+")) {
            if (!word.isEmpty()) counts.merge(word, 1, Integer::sum);
        }
        return counts;
    }

    public static Map<String, List<String>> groupByFirstLetter(List<String> words) {
        return words.stream().collect(Collectors.groupingBy(w -> w.substring(0, 1)));
    }

    public static String latestValueAtOrBefore(TreeMap<Long, String> map, long timestamp) {
        Map.Entry<Long, String> entry = map.floorEntry(timestamp);
        return entry == null ? null : entry.getValue();
    }

    public static List<String[]> readCsv(Path path) throws IOException {
        List<String[]> rows = new ArrayList<>();
        try (BufferedReader reader = Files.newBufferedReader(path)) {
            String line;
            boolean first = true;
            while ((line = reader.readLine()) != null) {
                if (line.isBlank()) continue;
                if (first) {
                    first = false;
                    continue;
                }
                rows.add(line.split(",", -1));
            }
        }
        return rows;
    }

    public static void writeCsv(Path path, String[] headers, List<String[]> rows) throws IOException {
        try (BufferedWriter writer = Files.newBufferedWriter(path)) {
            writer.write(String.join(",", headers));
            writer.newLine();
            for (String[] row : rows) {
                writer.write(String.join(",", row));
                writer.newLine();
            }
        }
    }

    public static void main(String[] args) throws IOException {
        List<FileRow> files = new ArrayList<>(List.of(
                new FileRow("z", 1, 3),
                new FileRow("t", 9, 9),
                new FileRow("a", 10, 10)));
        if (!topNBySize(files, 2).get(0).name().equals("a")) throw new AssertionError();
        if (!sortBySizeDescThenName(files, 10).get(0).name().equals("a")) throw new AssertionError();
        if (wordCount("a b a").get("a") != 2) throw new AssertionError();
        TreeMap<Long, String> map = new TreeMap<>(Map.of(10L, "A", 20L, "B", 30L, "C"));
        if (!latestValueAtOrBefore(map, 25L).equals("B")) throw new AssertionError();
        Path tmp = Files.createTempFile("ids", ".csv");
        try {
            writeCsv(tmp, new String[]{"Name", "Age"}, List.of(new String[][]{{"Alice", "30"}}));
            if (readCsv(tmp).size() != 1) throw new AssertionError();
        } finally {
            Files.deleteIfExists(tmp);
        }
    }

    private static List<FileRow> sortBySizeDescThenName(List<FileRow> files, int ignored) {
        return sortBySizeDescThenName(files);
    }
}
