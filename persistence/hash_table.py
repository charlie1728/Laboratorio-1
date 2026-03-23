
from persistence.hash_entry import HashEntry


class HashTable:

    DEFAULT_CAPACITY = 16
    DEFAULT_THRESHOLD = 0.7

    def __init__(self, capacity: int = DEFAULT_CAPACITY, threshold: float = DEFAULT_THRESHOLD):
        self._capacity = capacity
        self._threshold = threshold
        self._size = 0
        self._buckets: list[list[HashEntry]] = [[] for _ in range(self._capacity)]

        self.total_collisions = 0
        self.rehash_count = 0
        self.total_puts = 0
        self.total_gets = 0

    def _hash(self, key: str) -> int:
        h = 5381
        for ch in key:
            h = ((h << 5) + h) ^ ord(ch)
        return h % self._capacity

    # ─────────────────────────────── CRUD ────────────────────────────────

    def put(self, key: str, value) -> None:
        self.total_puts += 1
        idx = self._hash(key)
        bucket = self._buckets[idx]

        for entry in bucket:
            if entry.is_occupied() and entry.key == key:
                entry.value = value
                return

        if len(bucket) > 0:
            self.total_collisions += 1

        bucket.append(HashEntry(key, value))
        self._size += 1

        if self.load_factor() > self._threshold:
            self._rehash()

    def get(self, key: str):
        self.total_gets += 1
        idx = self._hash(key)
        bucket = self._buckets[idx]

        for entry in bucket:
            if entry.is_occupied() and entry.key == key:
                return entry.value

        return None

    def delete(self, key: str) -> bool:
        idx = self._hash(key)
        bucket = self._buckets[idx]

        for i, entry in enumerate(bucket):
            if entry.is_occupied() and entry.key == key:
                bucket.pop(i)
                self._size -= 1
                return True

        return False

    def contains(self, key: str) -> bool:
        return self.get(key) is not None

    def keys(self) -> list[str]:
        result = []
        for bucket in self._buckets:
            for entry in bucket:
                if entry.is_occupied():
                    result.append(entry.key)
        return result

    def items(self) -> list[tuple]:
        result = []
        for bucket in self._buckets:
            for entry in bucket:
                if entry.is_occupied():
                    result.append((entry.key, entry.value))
        return result

    def load_factor(self) -> float:
        return self._size / self._capacity if self._capacity > 0 else 0.0
    
    def _rehash(self) -> None:
        old_buckets = self._buckets
        self._capacity *= 2
        self._buckets = [[] for _ in range(self._capacity)]
        self._size = 0
        self.rehash_count += 1

        for bucket in old_buckets:
            for entry in bucket:
                if entry.is_occupied():
                    self.put(entry.key, entry.value)

    def to_dict(self) -> dict:

        return {
            "capacity": self._capacity,
            "threshold": self._threshold,
            "size": self._size,
            "entries": [
                {"key": key, "value": value}
                for key, value in self.items()
            ],
            "stats": {
                "total_collisions": self.total_collisions,
                "rehash_count": self.rehash_count,
                "total_puts": self.total_puts,
                "total_gets": self.total_gets,
            }
        }

    @classmethod
    def from_dict(cls, data: dict) -> "HashTable":
        ht = cls(capacity=data["capacity"], threshold=data["threshold"])
        ht.total_collisions = data["stats"]["total_collisions"]
        ht.rehash_count = data["stats"]["rehash_count"]
        ht.total_puts = data["stats"]["total_puts"]
        ht.total_gets = data["stats"]["total_gets"]
        for entry in data["entries"]:
            ht.put(entry["key"], entry["value"])
        return ht

    def stats(self) -> dict:
        bucket_lengths = [len(b) for b in self._buckets]
        max_chain = max(bucket_lengths) if bucket_lengths else 0
        occupied_buckets = sum(1 for b in bucket_lengths if b > 0)

        return {
            "capacity": self._capacity,
            "size": self._size,
            "load_factor": round(self.load_factor(), 4),
            "threshold": self._threshold,
            "total_collisions": self.total_collisions,
            "rehash_count": self.rehash_count,
            "max_chain_length": max_chain,
            "occupied_buckets": occupied_buckets,
            "empty_buckets": self._capacity - occupied_buckets,
            "total_puts": self.total_puts,
            "total_gets": self.total_gets,
        }

    def bucket_distribution(self) -> list[int]:

        return [len(b) for b in self._buckets]

    def __len__(self):
        return self._size

    def __repr__(self):
        return (f"HashTable(capacity={self._capacity}, size={self._size}, "
                f"load_factor={self.load_factor():.3f})")
