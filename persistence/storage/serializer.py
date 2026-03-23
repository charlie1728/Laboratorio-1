"""
serializer.py
Serialización y deserialización de registros en formato JSON Lines.
"""

import json


class Serializer:
    """Convierte registros a JSON Lines y viceversa."""

    @staticmethod
    def encode(record_type: str, key: str, data: dict) -> str:
        """
        Serializa un registro a una línea JSON.
        Formato: {"type":"...", "key":"...", "data":{...}}\n
        """
        payload = {"type": record_type, "key": key, "data": data}
        return json.dumps(payload, separators=(",", ":")) + "\n"

    @staticmethod
    def decode(line: str) -> dict:
        """
        Deserializa una línea JSON a dict.
        Retorna None si la línea está vacía o malformada.
        """
        line = line.strip()
        if not line:
            return None
        try:
            return json.loads(line)
        except json.JSONDecodeError:
            return None
