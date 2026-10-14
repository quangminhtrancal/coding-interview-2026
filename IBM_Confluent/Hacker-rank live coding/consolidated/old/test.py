from collections import Counter

def count_event_bytes(filename):
    counts = Counter()

    with open(filename, "rb") as file:
        for line in file:
            line = line.rstrip(b"\r\n")

            if not line:
                continue

            event_type = line.partition(b",")[0]
            counts[event_type] += 1

    return counts

if __name__ == "__main__":
    counts = count_event_bytes("events.log")
