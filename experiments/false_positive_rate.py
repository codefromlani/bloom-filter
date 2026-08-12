from bloomfilter.bloom import BloomFilter


def measure_false_positive_rate(
    capacity: int,
    error_rate: float,
    inserted_count: int,
    query_count: int,
) -> float:
    bf = BloomFilter(capacity, error_rate)

    for i in range(inserted_count):
        bf.add(f"item-{i}")

    false_positives = 0

    for i in range(query_count):
        item = f"query-{i}"

        if bf.contains(item):
            false_positives += 1

    return false_positives / query_count