"""
leaderboard_repository.py
Repositorio del leaderboard global.
"""

from persistence.engine import PersistenceEngine
import time


class LeaderboardRepository:
    """Gestiona las puntuaciones del leaderboard."""

    RECORD_TYPE = "score"
    BOARD_KEY = "leaderboard:global"
    MAX_ENTRIES = 10

    def __init__(self, engine: PersistenceEngine):
        self._engine = engine

    def _score_key(self, run_id: str) -> str:
        return f"score:{run_id}"

    def submit_score(self, player_id: str, player_name: str, score: int, distance: int) -> None:
        """Guarda un puntaje individual y actualiza el leaderboard global."""
        run_id = f"{player_id}_{int(time.time())}"
        score_data = {
            "run_id": run_id,
            "player_id": player_id,
            "player_name": player_name,
            "score": score,
            "distance": distance,
            "timestamp": time.time(),
        }
        self._engine.save(self._score_key(run_id), score_data, self.RECORD_TYPE)
        self._update_board(score_data)

    def _update_board(self, new_entry: dict) -> None:
        """Mantiene el top MAX_ENTRIES ordenado por puntaje."""
        board = self._engine.get(self.BOARD_KEY) or {"entries": []}
        entries = board["entries"]

        # Comprobar si el jugador ya tiene una entrada
        existing = [e for e in entries if e.get("player_id") == new_entry["player_id"]]
        if existing:
            if new_entry["score"] > existing[0]["score"]:
                entries = [e for e in entries if e.get("player_id") != new_entry["player_id"]]
                entries.append(new_entry)
        else:
            entries.append(new_entry)

        entries = sorted(entries, key=lambda e: e["score"], reverse=True)[:self.MAX_ENTRIES]
        self._engine.save(self.BOARD_KEY, {"entries": entries}, "leaderboard")

    def get_top(self, n: int = 10) -> list[dict]:
        board = self._engine.get(self.BOARD_KEY) or {"entries": []}
        return board["entries"][:n]

    def get_rank(self, player_id: str) -> int | None:
        """Retorna la posición del jugador en el leaderboard (1-indexed)."""
        top = self.get_top(self.MAX_ENTRIES)
        for i, entry in enumerate(top):
            if entry.get("player_id") == player_id:
                return i + 1
        return None
