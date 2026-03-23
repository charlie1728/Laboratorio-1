"""
profile_repository.py
Repositorio de perfiles de jugador.
"""

from persistence.engine import PersistenceEngine


class ProfileRepository:
    """Gestiona perfiles de jugadores en el sistema de persistencia."""

    RECORD_TYPE = "profile"

    def __init__(self, engine: PersistenceEngine):
        self._engine = engine

    def _key(self, player_id: str) -> str:
        return f"player:{player_id}"

    def save(self, player_id: str, profile: dict) -> None:
        self._engine.save(self._key(player_id), profile, self.RECORD_TYPE)

    def get(self, player_id: str) -> dict | None:
        return self._engine.get(self._key(player_id))

    def exists(self, player_id: str) -> bool:
        return self._engine.exists(self._key(player_id))

    def default_profile(self, player_id: str) -> dict:
        return {
            "player_id": player_id,
            "name": player_id,
            "best_score": 0,
            "total_distance": 0,
            "games_played": 0,
            "powerups_collected": 0,
            "total_play_time": 0,
        }

    def update_after_run(self, player_id: str, score: int, distance: int,
                         powerups: int, play_time: float) -> dict:
        profile = self.get(player_id) or self.default_profile(player_id)
        profile["games_played"] = profile.get("games_played", 0) + 1
        profile["total_distance"] = profile.get("total_distance", 0) + distance
        profile["powerups_collected"] = profile.get("powerups_collected", 0) + powerups
        profile["total_play_time"] = profile.get("total_play_time", 0) + play_time
        if score > profile.get("best_score", 0):
            profile["best_score"] = score
        self.save(player_id, profile)
        return profile
