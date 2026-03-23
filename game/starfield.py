"""
starfield.py
Fondo de estrellas con efecto parallax.
"""

import random
from game.constants import WIDTH, HEIGHT


class Starfield:
    """
    Tres capas de estrellas con velocidades distintas (parallax).
    """

    def __init__(self, n_stars=120, seed=42):
        random.seed(seed)
        self.stars = []
        for _ in range(n_stars):
            x = random.uniform(0, WIDTH)
            y = random.uniform(0, HEIGHT)
            brightness = random.uniform(0.2, 1.0)
            speed_factor = random.uniform(0.05, 0.4)   # relativo a la velocidad del juego
            self.stars.append([x, y, brightness, speed_factor])

    def update(self, game_speed: float, dt: float):
        for star in self.stars:
            star[0] -= game_speed * star[3] * dt
            if star[0] < 0:
                star[0] = WIDTH
                star[1] = __import__("random").uniform(0, HEIGHT)

    def get_stars(self):
        return [tuple(s) for s in self.stars]
