"""
index_store.py
Serializa y deserializa la tabla hash en index.bin (formato JSON).
Si el archivo se pierde, el sistema puede reconstruirlo desde data.log.
"""

import json
import os
from persistence.hash_table import HashTable


class IndexStore:
    """
    Gestiona la persistencia de la tabla hash en disk (index.bin).
    """

    def __init__(self, filepath: str = "index.bin"):
        self._filepath = filepath

    def save(self, table: HashTable) -> None:
        """Serializa la tabla hash completa al archivo."""
        data = table.to_dict()
        with open(self._filepath, "w", encoding="utf-8") as f:
            json.dump(data, f)

    def load(self) -> HashTable:
        """
        Carga la tabla hash desde el archivo.
        Retorna None si el archivo no existe o está corrupto.
        """
        if not os.path.exists(self._filepath):
            return None
        try:
            with open(self._filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            return HashTable.from_dict(data)
        except (json.JSONDecodeError, KeyError, TypeError):
            return None

    def exists(self) -> bool:
        return os.path.exists(self._filepath)

    def delete(self) -> None:
        """Elimina el archivo de índice (para forzar reconstrucción en tests)."""
        if self.exists():
            os.remove(self._filepath)
