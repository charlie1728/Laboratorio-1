"""
recovery.py
Reconstruye la tabla hash desde data.log cuando index.bin se pierde o corrompe.
Garantiza que siempre se conserve el último valor por clave.
"""

from persistence.hash_table import HashTable
from persistence.storage.record_store import RecordStore


def rebuild_index(record_store: RecordStore) -> HashTable:
    """
    Lee data.log de inicio a fin y reconstruye la tabla hash.

    Para cada clave solo se conserva el offset del registro más reciente,
    de modo que get() siempre retorna el estado más actualizado.

    Returns:
        HashTable con todos los offsets actualizados.
    """
    table = HashTable()

    for offset, record in record_store.iterate_all():
        key = record.get("key")
        if key:
            table.put(key, offset)

    return table
