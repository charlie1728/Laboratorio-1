
class HashEntry:


    EMPTY = "EMPTY"
    OCCUPIED = "OCCUPIED"
    DELETED = "DELETED"

    def __init__(self, key: str = None, value=None):
        self.key = key
        self.value = value
        self.state = HashEntry.EMPTY if key is None else HashEntry.OCCUPIED

    def mark_deleted(self):
        self.key = None
        self.value = None
        self.state = HashEntry.DELETED

    def is_empty(self) -> bool:
        return self.state == HashEntry.EMPTY

    def is_occupied(self) -> bool:
        return self.state == HashEntry.OCCUPIED

    def is_tombstone(self) -> bool:
        return self.state == HashEntry.DELETED

    def __repr__(self):
        return f"HashEntry(key={self.key!r}, value={self.value!r}, state={self.state})"
