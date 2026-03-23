"""
constants.py
Constantes globales del juego VOID RUNNER.
Paleta cyberpunk oscura: negro profundo, cian eléctrico, magenta neón, blanco frío.
"""

# ─── Ventana ────────────────────────────────────────────────────────────────
WIDTH = 900
HEIGHT = 600
FPS = 60
TITLE = "VOID RUNNER"

# ─── Colores ─────────────────────────────────────────────────────────────────
BLACK       = (0,   0,   0)
DEEP_SPACE  = (5,   5,  15)
DARK_PANEL  = (10,  10,  25)
PANEL_BORDER= (20,  20,  50)

CYAN        = (0,  255, 255)
CYAN_DIM    = (0,  120, 140)
CYAN_DARK   = (0,   40,  60)

MAGENTA     = (255,  0, 200)
MAGENTA_DIM = (140,  0, 110)

WHITE       = (255, 255, 255)
GRAY        = (150, 150, 170)
GRAY_DIM    = (60,  60,  80)

YELLOW      = (255, 220,  0)
GREEN       = (0,  255, 120)
RED         = (255,  60,  60)
ORANGE      = (255, 140,  0)

# ─── Fuentes ─────────────────────────────────────────────────────────────────
FONT_MONO = None          # Se inicializa en main.py tras pygame.init()
FONT_SIZES = {
    "xs":   14,
    "sm":   18,
    "md":   24,
    "lg":   32,
    "xl":   48,
    "xxl":  72,
}

# ─── Juego ───────────────────────────────────────────────────────────────────
LANE_COUNT   = 3
LANE_Y       = [150, 300, 450]     # posición Y de cada carril
SHIP_X       = 120                 # posición X fija de la nave
BASE_SPEED   = 280                 # px/s velocidad inicial de obstáculos
SPEED_INC    = 15                  # px/s incremento cada 5 segundos
MAX_SPEED    = 700

ASTEROID_W   = 44
ASTEROID_H   = 44
SHIP_W       = 52
SHIP_H       = 32

POWERUP_SIZE = 26

SCORE_PER_SEC    = 10
SCORE_PER_DODGE  = 5
SCORE_PER_POWERUP= 50

# Dificultad → multiplicador de velocidad
DIFFICULTY_MULT = {
    "Easy":   0.75,
    "Normal": 1.0,
    "Hard":   1.4,
}
