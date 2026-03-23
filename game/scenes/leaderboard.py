"""
leaderboard.py
Pantalla de leaderboard — muestra los mejores puntajes desde la tabla hash.
"""

import pygame
import math
from game.constants import *
from game.draw_utils import draw_text, draw_panel, draw_stars, draw_glow_rect


class LeaderboardScene:
    """Visualización del top 10 de puntajes."""

    def __init__(self, leaderboard_repo, settings_repo):
        self._repo     = leaderboard_repo
        self._settings = settings_repo.get()
        self._player_id = self._settings.get("player_name", "PILOT").lower().replace(" ", "_")
        self._t = 0.0
        self._entries = []
        self._player_rank = None
        self._reload()

    def _reload(self):
        self._entries = self._repo.get_top(10)
        self._player_rank = self._repo.get_rank(self._player_id)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_BACKSPACE):
                return "menu"
        return None

    def update(self, dt: float, stars):
        self._t += dt
        stars.update(150, dt)

    def draw(self, surface, stars):
        surface.fill(DEEP_SPACE)
        draw_stars(surface, stars.get_stars())

        cx = WIDTH // 2

        # ── Título ────────────────────────────────────────────────────────
        pulse = abs(math.sin(self._t * 1.5)) * 0.3 + 0.7
        c = tuple(int(v * pulse) for v in CYAN)
        draw_text(surface, "TOP SCORES", 42, c, cx, 28, anchor="center")
        pygame.draw.line(surface, CYAN_DIM, (cx - 220, 80), (cx + 220, 80), 1)

        # ── Panel principal ───────────────────────────────────────────────
        panel = pygame.Rect(cx - 270, 90, 540, 400)
        draw_panel(surface, panel, CYAN_DIM, DARK_PANEL, 200)

        # Cabecera
        draw_text(surface, "#", 16, GRAY_DIM, cx - 220, 100)
        draw_text(surface, "PILOT", 16, GRAY_DIM, cx - 180, 100)
        draw_text(surface, "SCORE", 16, GRAY_DIM, cx + 60, 100)
        draw_text(surface, "DIST", 16, GRAY_DIM, cx + 160, 100)
        pygame.draw.line(surface, PANEL_BORDER, (cx - 240, 120), (cx + 240, 120), 1)

        # Entradas
        if not self._entries:
            draw_text(surface, "NO SCORES YET — PLAY FIRST!", 18, GRAY, cx, 240, anchor="center")
        else:
            for i, entry in enumerate(self._entries):
                y = 130 + i * 34
                is_player = entry.get("player_id") == self._player_id

                # Fondo resaltado para el jugador actual
                if is_player:
                    row_rect = pygame.Rect(cx - 245, y - 2, 490, 30)
                    draw_glow_rect(surface, CYAN_DIM, row_rect, width=1, glow_passes=1)

                # Colores por posición
                if i == 0:
                    rank_color = YELLOW
                elif i == 1:
                    rank_color = (200, 200, 200)
                elif i == 2:
                    rank_color = ORANGE
                else:
                    rank_color = GRAY

                name_color = CYAN if is_player else WHITE
                score_color = YELLOW if i == 0 else (CYAN if is_player else GRAY)

                draw_text(surface, f"{i+1:>2}.", 18, rank_color, cx - 220, y)
                name = str(entry.get("player_name", "???"))[:12].upper()
                draw_text(surface, name, 18, name_color, cx - 180, y)
                draw_text(surface, f"{entry.get('score', 0):>8}", 18, score_color, cx + 60, y)
                draw_text(surface, f"{entry.get('distance', 0):>5}m", 16, GRAY, cx + 160, y)

        pygame.draw.line(surface, PANEL_BORDER, (cx - 240, 468), (cx + 240, 468), 1)

        # Rango del jugador actual
        if self._player_rank:
            draw_text(surface, f"YOUR RANK: #{self._player_rank}", 16, CYAN, cx, 478, anchor="center")
        else:
            draw_text(surface, "YOUR RANK: UNRANKED", 16, GRAY_DIM, cx, 478, anchor="center")

        # Instrucción
        blink = int(self._t * 2) % 2 == 0
        if blink:
            draw_text(surface, "[ESC] BACK TO MENU", 14, GRAY_DIM, cx, HEIGHT - 22, anchor="center")
