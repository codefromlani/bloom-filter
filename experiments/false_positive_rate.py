import math

from bloomfilter.bloom import BloomFilter


def measure_false_positive_rate(
    capacity: int,
    error_rate: float,
    inserted_count: int,
    query_count: int,
) -> tuple[float, float]:
    bf = BloomFilter(capacity, error_rate)

    for i in range(inserted_count):
        bf.add(f"item-{i}")

    false_positives = 0

    for i in range(query_count):
        item = f"query-{i}"

        if bf.contains(item):
            false_positives += 1

    observed_rate = false_positives / query_count

    theoretical_rate = theoretical_false_positive_rate(
        bit_array_size=bf.bit_array_size,
        hash_count=bf.hash_count,
        inserted_count=inserted_count,
    )

    return observed_rate, theoretical_rate


# This answer: What happens to the false-positive rate when we insert more 
# items into a filter with fixed capacity?
def experiment_inserted_count():
    for inserted_count in [5_000, 10_000, 15_000, 20_000]:
        observed_rate, theoretical_rate = measure_false_positive_rate(
            capacity=10_000,
            error_rate=0.01,
            inserted_count=inserted_count,
            query_count=100_000,
        )

        print(
            f"inserted={inserted_count:,} "
            f"observed={observed_rate:.4%} "
            f"theoretical={theoretical_rate:.4%}"
        )


# This answer: What happens when we request increasingly strict false-positive rates?
def experiment_error_rate():
    for error_rate in [0.1, 0.01, 0.001]:
        observed_rate, theoretical_rate = measure_false_positive_rate(
            capacity=10_000,
            error_rate=error_rate,
            inserted_count=10_000,
            query_count=100_000,
        )

        print(
            f"error_rate={error_rate} "
            f"observed={observed_rate:.4%} "
            f"theoretical={theoretical_rate:.4%}"
        )


# This answer: How does the number of queries affect the stability of our observed estimate?
def experiment_query_count():
    for query_count in [1_000, 10_000, 100_000]:
        observed_rate, theoretical_rate = measure_false_positive_rate(
                capacity=10_000,
                error_rate=0.01,
                inserted_count=10_000,
                query_count=query_count,
            )
        
        print(
            f"query_count={query_count} "
            f"observed={observed_rate:.4%} "
            f"theoretical={theoretical_rate:.4%}"
        )


def theoretical_false_positive_rate(
        bit_array_size: int,
        hash_count: int,
        inserted_count: int,
) -> float:

    p = (
        1 - math.exp(-(hash_count * inserted_count) / bit_array_size)
        ) ** hash_count
    
    return p


def main():
    print("=== Effect of inserted items ===")
    experiment_inserted_count()

    print("=== Effect of target error rate ===")
    experiment_error_rate()

    print("=== Effect of query count ===")
    experiment_query_count()

if __name__ == "__main__":
    main()
