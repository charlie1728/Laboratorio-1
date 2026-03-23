"""
hash_viz.py
Visualizador interno de la tabla hash (requerimiento bonus).
Muestra en tiempo real:
  - Buckets y sus cadenas (chaining)
  - Factor de carga
  - Estadísticas de rendimiento
  - Distribución visual de colisiones
"""

import pygame
import math
from game.constants import *
from game.draw_utils import draw_text, draw_panel, draw_stars, draw_bar, draw_glow_rect


class HashVizScene:
    """
    Visualización educativa de la tabla hash en uso.
    Accesible desde el menú principal (bonus).
    """

    def __init__(self, engine, settings_repo):
        self._engine   = engine
        self._settings = settings_repo.get()
        self._t        = 0.0
        self._scroll   = 0
        self._max_scroll = 0
        self._selected_bucket = -1
        self._highlight_t = {}   # bucket_idx -> tiempo de highlight

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                return "menu"
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self._scroll = min(self._scroll + 1, self._max_scroll)
            elif event.key in (pygame.K_UP, pygame.K_w):
                self._scroll = max(self._scroll - 1, 0)
            elif event.key == pygame.K_r:
                # Forzar reconstrucción del índice
                self._engine.force_rebuild()
        return None

    def update(self, dt: float, stars):
        self._t += dt
        stars.update(80, dt)

    def draw(self, surface, stars):
        surface.fill(DEEP_SPACE)
        draw_stars(surface, stars.get_stars())

        stats = self._engine.stats()
        distribution = self._engine.bucket_distribution()
        capacity = stats["capacity"]

        cx = WIDTH // 2

        # ── Título ────────────────────────────────────────────────────────
        draw_text(surface, "HASH TABLE VISUALIZER", 28, CYAN, cx, 10, anchor="center")
        pygame.draw.line(surface, CYAN_DIM, (10, 42), (WIDTH - 10, 42), 1)

        # ── Panel de estadísticas (izquierda) ──────────────────────────────
        stats_panel = pygame.Rect(10, 50, 280, 340)
        draw_panel(surface, stats_panel, CYAN_DIM, DARK_PANEL, 210)

        draw_text(surface, "STATISTICS", 16, CYAN, 20, 58)
        pygame.draw.line(surface, PANEL_BORDER, (20, 78), (280, 78), 1)

        stat_lines = [
            ("Capacity",     str(stats["capacity"]),        WHITE),
            ("Size",         str(stats["size"]),            WHITE),
            ("Load Factor",  f"{stats['load_factor']:.4f}", self._lf_color(stats["load_factor"])),
            ("Threshold",    f"{stats['threshold']:.2f}",   GRAY),
            ("Collisions",   str(stats["total_collisions"]),ORANGE if stats["total_collisions"] > 0 else GREEN),
            ("Rehashes",     str(stats["rehash_count"]),    YELLOW if stats["rehash_count"] > 0 else GRAY),
            ("Max Chain",    str(stats["max_chain_length"]),RED if stats["max_chain_length"] > 3 else GREEN),
            ("Occ. Buckets", str(stats["occupied_buckets"]),CYAN),
            ("Empty Buckets",str(stats["empty_buckets"]),   GRAY),
            ("Total PUTs",   str(stats["total_puts"]),      GRAY),
            ("Total GETs",   str(stats["total_gets"]),      GRAY),
            ("Data File",    f"{stats['data_file_size_bytes']} B", GRAY),
        ]

        for j, (label, value, color) in enumerate(stat_lines):
            y = 86 + j * 23
            draw_text(surface, label + ":", 13, GRAY_DIM, 20, y)
            draw_text(surface, value, 13, color, 270, y, anchor="topright")

        # Barra de load factor
        lf = stats["load_factor"]
        lf_col = self._lf_color(lf)
        y_lf = 362
        draw_text(surface, "LOAD FACTOR", 13, GRAY, 20, y_lf)
        draw_bar(surface, 20, y_lf + 18, 250, 14, lf, 1.0, lf_col)
        # Línea de umbral
        thresh_x = 20 + int(250 * stats["threshold"])
        pygame.draw.line(surface, RED, (thresh_x, y_lf + 16), (thresh_x, y_lf + 34), 2)
        draw_text(surface, "↑ threshold", 11, RED, thresh_x - 30, y_lf + 36)

        # ── Leyenda / Claves activas ───────────────────────────────────────
        keys_panel = pygame.Rect(10, 400, 280, 160)
        draw_panel(surface, keys_panel, MAGENTA_DIM, DARK_PANEL, 200)
        draw_text(surface, "ACTIVE KEYS", 15, MAGENTA, 20, 408)
        pygame.draw.line(surface, PANEL_BORDER, (20, 426), (280, 426), 1)

        keys = self._engine.all_keys()
        for j, k in enumerate(keys[:8]):
            draw_text(surface, k[:30], 12, GRAY, 20, 430 + j * 16)
        if len(keys) > 8:
            draw_text(surface, f"... +{len(keys)-8} more", 11, GRAY_DIM, 20, 430 + 8 * 16)

        # ── Visualización de buckets (derecha) ───────────────────────────
        bv_x = 305
        bv_y = 50
        bv_w = WIDTH - bv_x - 10
        bv_h = HEIGHT - bv_y - 50

        bv_panel = pygame.Rect(bv_x, bv_y, bv_w, bv_h)
        draw_panel(surface, bv_panel, CYAN_DIM, DARK_PANEL, 200)
        draw_text(surface, f"BUCKETS  [0 – {capacity-1}]", 15, CYAN, bv_x + 10, bv_y + 8)
        pygame.draw.line(surface, PANEL_BORDER, (bv_x + 10, bv_y + 28), (bv_x + bv_w - 10, bv_y + 28), 1)

        # Cuántos buckets mostrar
        visible_h   = bv_h - 40
        bucket_h    = 18
        visible_n   = visible_h // bucket_h
        self._max_scroll = max(0, capacity - visible_n)

        # Escala de colores por longitud de cadena
        max_chain = max(distribution) if distribution else 1
        max_chain = max(max_chain, 1)

        for j in range(visible_n):
            idx = j + self._scroll
            if idx >= capacity:
                break
            length = distribution[idx] if idx < len(distribution) else 0
            by = bv_y + 34 + j * bucket_h

            # Número de bucket
            draw_text(surface, f"{idx:>3}", 12, GRAY_DIM, bv_x + 12, by)

            # Color según occupación
            if length == 0:
                box_col = PANEL_BORDER
            elif length == 1:
                box_col = CYAN_DIM
            elif length == 2:
                box_col = YELLOW
            else:
                box_col = RED

            # Barra del bucket
            bar_x = bv_x + 50
            bar_w = min(length * 40, bv_w - 90)
            if bar_w > 0:
                bar_rect = pygame.Rect(bar_x, by + 2, bar_w, bucket_h - 4)
                pygame.draw.rect(surface, box_col, bar_rect)
                pygame.draw.rect(surface, WHITE, bar_rect, 1)
                if length > 0:
                    draw_text(surface, str(length), 11, WHITE, bar_x + 4, by + 2)
            else:
                pygame.draw.rect(surface, PANEL_BORDER,
                                 pygame.Rect(bar_x, by + 2, 8, bucket_h - 4))

        # Instrucciones
        draw_text(surface, "↑↓ SCROLL BUCKETS   [R] REBUILD INDEX   [ESC] BACK",
                  12, GRAY_DIM, cx, HEIGHT - 22, anchor="center")

    def _lf_color(self, lf: float):
        if lf < 0.5:
            return GREEN
        elif lf < 0.7:
            return YELLOW
        else:
            return RED
