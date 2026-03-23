"""
draw_utils.py
Funciones de dibujo procedural para VOID RUNNER.
Todo el arte se genera en código: no hay assets externos.
"""

import pygame
import math
from game.constants import *


def draw_text(surface, text, size, color, x, y, anchor="topleft", font=None):
    """Renderiza texto con fuente monoespaciada del sistema."""
    if font is None:
        font = pygame.font.SysFont("courier", size, bold=True)
    surf = font.render(str(text), True, color)
    rect = surf.get_rect()
    setattr(rect, anchor, (x, y))
    surface.blit(surf, rect)
    return rect


def draw_panel(surface, rect, border_color=CYAN_DIM, bg_color=DARK_PANEL, alpha=220):
    """Panel semitransparente con borde."""
    s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    s.fill((*bg_color, alpha))
    surface.blit(s, rect.topleft)
    pygame.draw.rect(surface, border_color, rect, 1)


def draw_glow_rect(surface, color, rect, width=2, glow_passes=3):
    """Rectángulo con efecto de brillo neón."""
    for i in range(glow_passes, 0, -1):
        r = rect.inflate(i * 4, i * 4)
        dim = tuple(max(0, c // (i + 1)) for c in color)
        pygame.draw.rect(surface, dim, r, 1)
    pygame.draw.rect(surface, color, rect, width)


def draw_ship(surface, x, y, w=SHIP_W, h=SHIP_H, color=CYAN, engine_t=0):
    """
    Dibuja la nave espacial proceduralmente.
    x, y = centro de la nave.
    engine_t = tiempo para animar el exhaust.
    """
    cx, cy = int(x), int(y)

    # Cuerpo principal (trapezoide)
    body = [
        (cx - w//2,      cy),
        (cx + w//2 - 6,  cy - h//4),
        (cx + w//2,      cy),
        (cx + w//2 - 6,  cy + h//4),
    ]
    pygame.draw.polygon(surface, color, body)

    # Cabina
    cockpit = [
        (cx + w//4,  cy - 2),
        (cx + w//2 - 4, cy),
        (cx + w//4,  cy + 2),
    ]
    pygame.draw.polygon(surface, WHITE, cockpit)

    # Ala superior
    wing_top = [
        (cx - w//4,  cy - 2),
        (cx + w//4,  cy - 2),
        (cx + w//6,  cy - h//2),
        (cx - w//3,  cy - h//2 + 4),
    ]
    pygame.draw.polygon(surface, CYAN_DIM, wing_top)

    # Ala inferior
    wing_bot = [
        (cx - w//4,  cy + 2),
        (cx + w//4,  cy + 2),
        (cx + w//6,  cy + h//2),
        (cx - w//3,  cy + h//2 - 4),
    ]
    pygame.draw.polygon(surface, CYAN_DIM, wing_bot)

    # Motor exhaust animado
    flicker = abs(math.sin(engine_t * 8)) * 0.5 + 0.5
    ex = cx - w//2
    ey = cy
    for i, (col, size) in enumerate([(CYAN, 18), (WHITE, 10), (YELLOW, 6)]):
        length = int((size + i * 4) * flicker)
        dim_col = tuple(int(c * flicker) for c in col)
        pygame.draw.line(surface, dim_col, (ex, ey - size//4), (ex - length, ey - size//4), 2)
        pygame.draw.line(surface, dim_col, (ex, ey + size//4), (ex - length, ey + size//4), 2)

    # Borde brillante
    pygame.draw.polygon(surface, WHITE, body, 1)


def draw_asteroid(surface, x, y, size=ASTEROID_W, rotation=0.0):
    """Dibuja un asteroide irregular procedural."""
    cx, cy = int(x), int(y)
    r = size // 2
    points = []
    n_pts = 8
    for i in range(n_pts):
        angle = (2 * math.pi * i / n_pts) + rotation
        # Variación pseudo-aleatoria basada en índice
        vary = 0.75 + 0.25 * math.sin(i * 2.3 + 1.7)
        pr = r * vary
        points.append((cx + pr * math.cos(angle), cy + pr * math.sin(angle)))
    pygame.draw.polygon(surface, (80, 60, 50), points)
    pygame.draw.polygon(surface, (130, 100, 80), points, 2)
    # Cráter
    cr = max(4, r // 3)
    pygame.draw.circle(surface, (50, 40, 30), (cx - r//4, cy - r//4), cr)
    pygame.draw.circle(surface, (100, 80, 60), (cx - r//4, cy - r//4), cr, 1)


def draw_powerup(surface, x, y, ptype="energy", t=0.0):
    """Dibuja un powerup animado."""
    cx, cy = int(x), int(y)
    r = POWERUP_SIZE // 2
    pulse = abs(math.sin(t * 3)) * 0.3 + 0.7

    colors = {
        "energy":  YELLOW,
        "shield":  CYAN,
        "multiplier": MAGENTA,
    }
    color = colors.get(ptype, GREEN)
    dim = tuple(int(c * pulse) for c in color)

    # Outer glow
    pygame.draw.circle(surface, tuple(c//4 for c in color), (cx, cy), r + 4)
    pygame.draw.circle(surface, dim, (cx, cy), r, 2)

    # Símbolo interior
    if ptype == "energy":
        # Rayo
        bolt = [(cx-3, cy-r+4), (cx+2, cy-2), (cx-2, cy+2), (cx+3, cy+r-4)]
        pygame.draw.lines(surface, dim, False, bolt, 2)
    elif ptype == "shield":
        # Escudo
        pygame.draw.arc(surface, dim, (cx-r+4, cy-r+4, (r-4)*2, (r-4)*2),
                        math.radians(30), math.radians(150), 2)
        pygame.draw.line(surface, dim, (cx-r+6, cy+2), (cx+r-6, cy+2), 2)
    else:
        # X2
        draw_text(surface, "x2", 12, dim, cx, cy, anchor="center")


def draw_stars(surface, stars):
    """
    stars = lista de (x, y, brightness, speed_factor)
    Dibuja estrellas con parallax.
    """
    for (sx, sy, br, _) in stars:
        c = int(br * 200)
        size = 1 if br < 0.5 else 2
        pygame.draw.circle(surface, (c, c, c + 30), (int(sx), int(sy)), size)


def draw_lane_guides(surface):
    """Líneas guía de los carriles, estilo cyberpunk."""
    for ly in LANE_Y:
        pygame.draw.line(surface, PANEL_BORDER, (0, ly), (WIDTH, ly), 1)


def draw_hud(surface, score, distance, speed, shield_active, multiplier, time_sec):
    """HUD superior del juego."""
    # Fondo HUD
    hud_rect = pygame.Rect(0, 0, WIDTH, 40)
    draw_panel(surface, hud_rect, CYAN_DIM, DARK_PANEL, 200)

    # Score
    draw_text(surface, f"SCORE  {score:07d}", 16, CYAN, 10, 10)
    # Distancia
    draw_text(surface, f"DIST  {distance:05d}m", 16, GRAY, 210, 10)
    # Velocidad
    draw_text(surface, f"SPD  {int(speed)}", 16, YELLOW, 390, 10)
    # Tiempo
    mins = int(time_sec) // 60
    secs = int(time_sec) % 60
    draw_text(surface, f"TIME  {mins:02d}:{secs:02d}", 16, GRAY, 540, 10)
    # Multiplicador
    if multiplier > 1:
        draw_text(surface, f"x{multiplier}", 18, MAGENTA, 720, 8)
    # Escudo
    if shield_active:
        draw_text(surface, "[ SHIELD ]", 14, CYAN, 810, 12)


def draw_shield_effect(surface, x, y):
    """Halo de escudo alrededor de la nave."""
    t = pygame.time.get_ticks() / 1000.0
    r = SHIP_W // 2 + 12
    alpha = int(abs(math.sin(t * 4)) * 120 + 60)
    s = pygame.Surface((r*2+4, r*2+4), pygame.SRCALPHA)
    pygame.draw.circle(s, (*CYAN, alpha), (r+2, r+2), r, 3)
    surface.blit(s, (int(x) - r - 2, int(y) - r - 2))


def draw_explosion(surface, x, y, progress):
    """
    Explosión procedural.
    progress: 0.0 → 1.0 (0 = inicio, 1 = final)
    """
    cx, cy = int(x), int(y)
    max_r = 50
    r = int(max_r * progress)
    alpha = int(255 * (1 - progress))
    colors = [RED, ORANGE, YELLOW, WHITE]
    for i, col in enumerate(colors):
        rr = max(1, r - i * 6)
        s = pygame.Surface((rr*2+2, rr*2+2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*col, alpha), (rr+1, rr+1), rr)
        surface.blit(s, (cx - rr - 1, cy - rr - 1))


def draw_bar(surface, x, y, w, h, value, max_value, color, bg_color=GRAY_DIM, label=""):
    """Barra de progreso genérica."""
    bg = pygame.Rect(x, y, w, h)
    pygame.draw.rect(surface, bg_color, bg)
    fill_w = int(w * (value / max_value)) if max_value > 0 else 0
    fill = pygame.Rect(x, y, fill_w, h)
    pygame.draw.rect(surface, color, fill)
    pygame.draw.rect(surface, GRAY, bg, 1)
    if label:
        draw_text(surface, label, 12, WHITE, x + w + 6, y + h//2 - 6)
