import math
import hashlib


class BloomFilter:
    def __init__(self, capacity: int, error_rate: float):
        self.capacity = capacity
        self.error_rate = error_rate

        self.bit_array_size = self._calculate_bit_array_size()
        self.hash_count = self._calculate_hash_count()
        self.bits = 0

    def _set_bit(self, index: int):
        self.bits |= 1 << index

    def _get_bit(self, index: int) -> bool:
        return bool(self.bits & (1 << index))

    def _calculate_bit_array_size(self) -> int:
        return math.ceil(
            -(self.capacity * math.log(self.error_rate))
            / (math.log(2) ** 2)
        )

    def _calculate_hash_count(self) -> int:
        return round(
            (self.bit_array_size / self.capacity) * math.log(2)
        )

    def _hashes(self, item: str):
        digest = hashlib.sha256(item.encode()).digest()

        h1 = int.from_bytes(digest[:16])
        h2 = int.from_bytes(digest[16:])

        positions = []

        for i in range(self.hash_count):
            position = (h1 + i * h2) % self.bit_array_size
            positions.append(position)

        return positions

    def add(self, item: str):
        positions = self._hashes(item)

        for position in positions:
            self._set_bit(position)

    def contains(self, item: str) -> bool:
        positions = self._hashes(item)

        for position in positions:
            if not self._get_bit(position):
                return False

        return True
