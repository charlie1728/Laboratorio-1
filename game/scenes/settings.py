"""
settings.py
Pantalla de configuración del juego.
Cambios se guardan en tiempo real en el sistema de persistencia.
"""

import pygame
import math
from game.constants import *
from game.draw_utils import draw_text, draw_panel, draw_stars, draw_glow_rect, draw_bar


class SettingsScene:
    """
    Configuración del juego:
    - Player Name
    - Volume
    - Difficulty
    - Show Particles
    - Show Hash Visualizer (bonus)
    """

    DIFFICULTIES = ["Easy", "Normal", "Hard"]

    def __init__(self, settings_repo):
        self._repo     = settings_repo
        self._settings = settings_repo.get()
        self._selected = 0
        self._t        = 0.0
        self._message  = ""
        self._msg_t    = 0.0
        self._editing_name = False
        self._name_buf     = self._settings.get("player_name", "PILOT")

        self._options = [
            "player_name",
            "volume",
            "difficulty",
            "show_particles",
            "show_hash_viz",
        ]
        self._labels = {
            "player_name":   "PILOT NAME",
            "volume":        "VOLUME",
            "difficulty":    "DIFFICULTY",
            "show_particles":"PARTICLES",
            "show_hash_viz": "HASH VISUALIZER",
        }

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            # Modo edición de nombre
            if self._editing_name:
                if event.key == pygame.K_RETURN:
                    name = self._name_buf.strip().upper()
                    if name:
                        self._settings["player_name"] = name
                        self._repo.save(self._settings)
                        self._show_message("NAME SAVED")
                    self._editing_name = False
                elif event.key == pygame.K_BACKSPACE:
                    self._name_buf = self._name_buf[:-1]
                elif event.key == pygame.K_ESCAPE:
                    self._editing_name = False
                    self._name_buf = self._settings.get("player_name", "PILOT")
                elif len(self._name_buf) < 12 and event.unicode.isalpha():
                    self._name_buf += event.unicode.upper()
                return None

            key = event.key
            if key == pygame.K_ESCAPE:
                return "menu"
            elif key in (pygame.K_UP, pygame.K_w):
                self._selected = (self._selected - 1) % len(self._options)
            elif key in (pygame.K_DOWN, pygame.K_s):
                self._selected = (self._selected + 1) % len(self._options)
            elif key in (pygame.K_LEFT, pygame.K_a, pygame.K_RIGHT, pygame.K_d, pygame.K_RETURN, pygame.K_SPACE):
                self._handle_change(key)

        return None

    def _handle_change(self, key):
        opt = self._options[self._selected]
        right = key in (pygame.K_RIGHT, pygame.K_d)

        if opt == "player_name":
            self._editing_name = True
            self._name_buf = self._settings.get("player_name", "PILOT")
            return

        elif opt == "volume":
            delta = 5 if right else -5
            self._settings["volume"] = max(0, min(100, self._settings.get("volume", 80) + delta))

        elif opt == "difficulty":
            idx = self.DIFFICULTIES.index(self._settings.get("difficulty", "Normal"))
            if right:
                idx = (idx + 1) % len(self.DIFFICULTIES)
            else:
                idx = (idx - 1) % len(self.DIFFICULTIES)
            self._settings["difficulty"] = self.DIFFICULTIES[idx]

        elif opt in ("show_particles", "show_hash_viz"):
            self._settings[opt] = not self._settings.get(opt, True)

        self._repo.save(self._settings)
        self._show_message("SAVED")

    def _show_message(self, msg: str):
        self._message = msg
        self._msg_t   = 2.0

    def update(self, dt: float, stars):
        self._t += dt
        stars.update(120, dt)
        if self._msg_t > 0:
            self._msg_t -= dt

    def draw(self, surface, stars):
        surface.fill(DEEP_SPACE)
        draw_stars(surface, stars.get_stars())

        cx = WIDTH // 2

        # Título
        pulse = abs(math.sin(self._t * 1.5)) * 0.3 + 0.7
        c = tuple(int(v * pulse) for v in CYAN)
        draw_text(surface, "SETTINGS", 42, c, cx, 28, anchor="center")
        pygame.draw.line(surface, CYAN_DIM, (cx - 200, 80), (cx + 200, 80), 1)

        panel = pygame.Rect(cx - 280, 90, 560, 390)
        draw_panel(surface, panel, CYAN_DIM, DARK_PANEL, 200)

        for i, opt in enumerate(self._options):
            y = 110 + i * 64
            is_sel = i == self._selected
            label_color = CYAN if is_sel else GRAY
            prefix = "▶ " if is_sel else "  "

            # Fondo seleccionado
            if is_sel:
                rect = pygame.Rect(cx - 260, y - 4, 520, 56)
                draw_glow_rect(surface, CYAN_DIM, rect, width=1, glow_passes=1)

            draw_text(surface, prefix + self._labels[opt], 18, label_color, cx - 240, y + 6)

            # Valor
            val_x = cx + 80
            val_y = y + 6

            if opt == "player_name":
                if self._editing_name:
                    blink = int(self._t * 3) % 2 == 0
                    cursor = "_" if blink else " "
                    draw_text(surface, f"[ {self._name_buf}{cursor} ]", 18, YELLOW, val_x, val_y)
                else:
                    name = self._settings.get("player_name", "PILOT")
                    draw_text(surface, name, 18, WHITE, val_x, val_y)
                    if is_sel:
                        draw_text(surface, "ENTER to edit", 13, GRAY_DIM, val_x, val_y + 22)

            elif opt == "volume":
                vol = self._settings.get("volume", 80)
                draw_bar(surface, val_x, val_y + 8, 140, 12, vol, 100, CYAN)
                draw_text(surface, f"{vol}%", 16, WHITE, val_x + 150, val_y + 4)
                if is_sel:
                    draw_text(surface, "← →", 13, GRAY_DIM, val_x, val_y + 22)

            elif opt == "difficulty":
                diff = self._settings.get("difficulty", "Normal")
                diff_colors = {"Easy": GREEN, "Normal": YELLOW, "Hard": RED}
                draw_text(surface, diff, 18, diff_colors.get(diff, WHITE), val_x, val_y)
                if is_sel:
                    draw_text(surface, "← →", 13, GRAY_DIM, val_x, val_y + 22)

            elif opt in ("show_particles", "show_hash_viz"):
                val = self._settings.get(opt, True)
                col = GREEN if val else RED
                draw_text(surface, "ON" if val else "OFF", 18, col, val_x, val_y)
                if is_sel:
                    draw_text(surface, "ENTER to toggle", 13, GRAY_DIM, val_x, val_y + 22)

        # Mensaje de guardado
        if self._msg_t > 0:
            alpha = min(1.0, self._msg_t) * 255
            a = int(alpha)
            s = pygame.Surface((160, 30), pygame.SRCALPHA)
            s.fill((0, 255, 120, min(a//2, 100)))
            surface.blit(s, (cx - 80, HEIGHT - 60))
            draw_text(surface, f"✓  {self._message}", 18, GREEN, cx, HEIGHT - 54, anchor="center")

        blink = int(self._t * 2) % 2 == 0
        if blink:
            draw_text(surface, "[ESC] BACK", 14, GRAY_DIM, cx, HEIGHT - 22, anchor="center")
