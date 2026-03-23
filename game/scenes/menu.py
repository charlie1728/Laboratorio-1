"""
menu.py
Pantalla de menú principal de VOID RUNNER.
"""

import pygame
import math
from game.constants import *
from game.draw_utils import draw_text, draw_panel, draw_ship, draw_stars, draw_glow_rect


class MenuScene:
    """
    Menú principal con opciones:
    - Start Game (nueva partida)
    - Continue   (si hay perfil guardado)
    - Leaderboard
    - Settings
    - Quit
    """

    OPTIONS = ["START GAME", "CONTINUE", "LEADERBOARD", "SETTINGS", "QUIT"]
    ACTIONS  = ["game",      "game",     "leaderboard", "settings", "quit"]

    def __init__(self, profile_repo, settings_repo):
        self._profile_repo = profile_repo
        self._settings_repo = settings_repo
        self._selected = 0
        self._t = 0.0
        self._ship_y = HEIGHT // 2
        self._ship_vy = 0.0
        self._particles = []
        self._settings = settings_repo.get()
        self._player_name = self._settings.get("player_name", "PILOT")

    def handle_event(self, event):
        """
        Retorna la acción a ejecutar como string, o None.
        """
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self._selected = (self._selected - 1) % len(self.OPTIONS)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self._selected = (self._selected + 1) % len(self.OPTIONS)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return self._confirm()
        return None

    def _confirm(self):
        action = self.ACTIONS[self._selected]
        if action == "game" and self.OPTIONS[self._selected] == "CONTINUE":
            return "continue"
        return action

    def update(self, dt: float, stars):
        self._t += dt
        stars.update(200, dt)

        # Nave flotante animada
        self._ship_y = HEIGHT // 2 - 60 + math.sin(self._t * 1.2) * 18

        # Partículas de exhaust
        if len(self._particles) < 30:
            import random
            px = SHIP_X - SHIP_W // 2 - 5
            py = self._ship_y
            self._particles.append({
                "x": px, "y": py,
                "vx": random.uniform(-60, -20),
                "vy": random.uniform(-10, 10),
                "life": 1.0,
                "size": random.randint(2, 5),
            })

        for p in self._particles:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["life"] -= dt * 1.5
        self._particles = [p for p in self._particles if p["life"] > 0]

    def draw(self, surface, stars):
        surface.fill(DEEP_SPACE)
        draw_stars(surface, stars.get_stars())

        # Líneas de carril decorativas
        for ly in LANE_Y:
            pygame.draw.line(surface, PANEL_BORDER, (0, ly), (WIDTH, ly), 1)

        # Partículas
        for p in self._particles:
            alpha = int(p["life"] * 180)
            c = int(p["life"] * 200)
            s = pygame.Surface((p["size"]*2, p["size"]*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (c, int(c*0.8), 0, alpha), (p["size"], p["size"]), p["size"])
            surface.blit(s, (int(p["x"]), int(p["y"])))

        # Nave demo
        draw_ship(surface, SHIP_X, int(self._ship_y), engine_t=self._t)

        # Título
        title_x = WIDTH // 2
        title_y = 60
        # Sombra
        draw_text(surface, "VOID", 72, CYAN_DIM, title_x - 3, title_y + 3, anchor="center")
        draw_text(surface, "RUNNER", 72, MAGENTA_DIM, title_x - 3, title_y + 70 + 3, anchor="center")
        # Texto principal con pulso
        pulse = abs(math.sin(self._t * 2)) * 30
        c1 = (0, min(255, 200 + int(pulse)), min(255, 200 + int(pulse)))
        c2 = (min(255, 200 + int(pulse)), 0, min(255, 180 + int(pulse)))
        draw_text(surface, "VOID",   72, c1, title_x, title_y,      anchor="center")
        draw_text(surface, "RUNNER", 72, c2, title_x, title_y + 70, anchor="center")

        # Línea decorativa
        lx = WIDTH // 2 - 160
        pygame.draw.line(surface, CYAN_DIM, (lx, title_y + 145), (lx + 320, title_y + 145), 1)

        # Menú de opciones
        menu_x = WIDTH // 2
        menu_y = 280
        for i, option in enumerate(self.OPTIONS):
            is_selected = i == self._selected
            color = CYAN if is_selected else GRAY
            prefix = "▶  " if is_selected else "   "

            if is_selected:
                # Fondo resaltado
                rect = pygame.Rect(menu_x - 130, menu_y + i * 44 - 4, 260, 32)
                draw_glow_rect(surface, CYAN_DIM, rect, width=1, glow_passes=2)

            draw_text(surface, prefix + option, 22, color, menu_x, menu_y + i * 44, anchor="center")

        # Player name
        draw_text(surface, f"PILOT: {self._player_name}", 14, GRAY_DIM, WIDTH - 10, HEIGHT - 24, anchor="topright")

        # Instrucciones
        blink = int(self._t * 2) % 2 == 0
        if blink:
            draw_text(surface, "↑↓ NAVIGATE   ENTER SELECT", 13, GRAY_DIM, WIDTH//2, HEIGHT - 24, anchor="center")
