import pytest

from bloomfilter.bloom import BloomFilter


def test_no_false_negative():
    bf = BloomFilter(100, 0.01)

    items = [
        "alice",
        "bob",
        "charlie",
        "david",
        "eve",
    ]

    for item in items:
        bf.add(item)

    for item in items:
        assert bf.contains(item) is True


def test_hashes_are_deterministic():
    bf = BloomFilter(100, 0.01)

    assert bf._hashes("alice") == bf._hashes("alice")
    assert bf._hashes("bob") == bf._hashes("bob")


def test_hash_positions_are_within_bit_array():
    bf = BloomFilter(100, 0.01)

    items = [
        "alice",
        "bob",
        "charlie",
        "david",
        "eve",
    ]

    for item in items:
        for position in bf._hashes(item):
            assert 0 <= position < bf.bit_array_size


def test_capacity_must_be_positive():
    with pytest.raises(ValueError):
        BloomFilter(0, 0.01)

    with pytest.raises(ValueError):
        BloomFilter(-1, 0.01)


def test_error_rate_must_be_between_zero_and_one():
    with pytest.raises(ValueError):
        BloomFilter(100, 0)

    with pytest.raises(ValueError):
        BloomFilter(100, 1)

    with pytest.raises(ValueError):
        BloomFilter(100, -0.1)

    with pytest.raises(ValueError):
        BloomFilter(100, 1.1)
