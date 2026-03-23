"""
record_store.py
Gestiona el archivo de datos data.log.
- Escritura append-only
- Lectura por offset
- Iteración secuencial para reconstrucción
"""

import os
from persistence.storage.serializer import Serializer


class RecordStore:
    """
    Almacén de registros basado en archivo append-only (data.log).

    Cada registro ocupa una línea JSON.
    El offset de inicio de cada línea sirve como referencia en la tabla hash.
    """

    def __init__(self, filepath: str = "data.log"):
        self._filepath = filepath
        self._ensure_file()

    def _ensure_file(self):
        if not os.path.exists(self._filepath):
            open(self._filepath, "w", encoding="utf-8").close()

    # ─────────────────────────── ESCRITURA ───────────────────────────────

    def append(self, record_type: str, key: str, data: dict) -> int:
        """
        Agrega un registro al final del archivo.
        Retorna el offset (posición de bytes) donde inicia el registro.
        """
        line = Serializer.encode(record_type, key, data)
        with open(self._filepath, "a", encoding="utf-8") as f:
            offset = f.tell()
            # Para obtener el offset real antes de escribir:
            # usamos el tamaño actual del archivo
        offset = os.path.getsize(self._filepath)
        with open(self._filepath, "a", encoding="utf-8") as f:
            f.write(line)
        return offset

    # ─────────────────────────── LECTURA ─────────────────────────────────

    def read_at(self, offset: int) -> dict:
        """
        Lee y deserializa el registro que comienza en el offset dado.
        """
        with open(self._filepath, "r", encoding="utf-8") as f:
            f.seek(offset)
            line = f.readline()
        return Serializer.decode(line)

    # ─────────────────────────── ITERACIÓN ───────────────────────────────

    def iterate_all(self):
        """
        Genera tuplas (offset, record) para cada línea válida del archivo.
        Útil para reconstrucción del índice.
        """
        if not os.path.exists(self._filepath):
            return
        with open(self._filepath, "r", encoding="utf-8") as f:
            while True:
                offset = f.tell()
                line = f.readline()
                if not line:
                    break
                record = Serializer.decode(line)
                if record is not None:
                    yield offset, record

    def file_size(self) -> int:
        return os.path.getsize(self._filepath) if os.path.exists(self._filepath) else 0

    def clear(self):
        """Vacía el archivo de datos (uso en tests)."""
        open(self._filepath, "w", encoding="utf-8").close()
