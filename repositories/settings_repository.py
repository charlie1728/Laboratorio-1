"""
settings_repository.py
Repositorio de configuración del juego.
"""

from persistence.engine import PersistenceEngine


class SettingsRepository:
    """Gestiona la configuración global del juego."""

    RECORD_TYPE = "settings"
    SETTINGS_KEY = "config:global"

    DEFAULT_SETTINGS = {
        "volume": 80,
        "difficulty": "Normal",     # Easy / Normal / Hard
        "fullscreen": False,
        "show_particles": True,
        "show_hash_viz": False,     # Visualización de tabla hash (bonus)
        "player_name": "PILOT",
    }

    def __init__(self, engine: PersistenceEngine):
        self._engine = engine

    def get(self) -> dict:
        data = self._engine.get(self.SETTINGS_KEY)
        if data is None:
            return dict(self.DEFAULT_SETTINGS)
        # Mezclar con defaults para claves nuevas
        merged = dict(self.DEFAULT_SETTINGS)
        merged.update(data)
        return merged

    def save(self, settings: dict) -> None:
        self._engine.save(self.SETTINGS_KEY, settings, self.RECORD_TYPE)

    def update(self, **kwargs) -> dict:
        settings = self.get()
        settings.update(kwargs)
        self.save(settings)
        return settings
