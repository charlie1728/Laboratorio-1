
from persistence.hash_table import HashTable
from persistence.storage.record_store import RecordStore
from persistence.storage.index_store import IndexStore
from persistence.recovery import rebuild_index

class PersistenceEngine:

    def __init__(self, data_path: str = "data.log", index_path: str = "index.bin"):
        self._record_store = RecordStore(data_path)
        self._index_store = IndexStore(index_path)
        self._table: HashTable = self._load_or_rebuild()


    def _load_or_rebuild(self) -> HashTable:
        table = self._index_store.load()
        if table is not None:
            return table
        # Reconstrucción automática
        table = rebuild_index(self._record_store)
        self._index_store.save(table)
        return table


    def save(self, key: str, data: dict, record_type: str = "generic") -> None:

        offset = self._record_store.append(record_type, key, data)
        self._table.put(key, offset)
        self._index_store.save(self._table)

    def get(self, key: str) -> dict | None:

        offset = self._table.get(key)
        if offset is None:
            return None
        record = self._record_store.read_at(offset)
        if record is None:
            return None
        return record.get("data")

    def delete(self, key: str) -> bool:
        result = self._table.delete(key)
        if result:
            self._index_store.save(self._table)
        return result

    def exists(self, key: str) -> bool:
        return self._table.contains(key)

    def all_keys(self) -> list[str]:
        return self._table.keys()

    def stats(self) -> dict:
        s = self._table.stats()
        s["data_file_size_bytes"] = self._record_store.file_size()
        return s

    def bucket_distribution(self) -> list[int]:
        return self._table.bucket_distribution()

    def force_rebuild(self) -> None:
        self._table = rebuild_index(self._record_store)
        self._index_store.save(self._table)


    @property
    def table(self) -> HashTable:
        return self._table
