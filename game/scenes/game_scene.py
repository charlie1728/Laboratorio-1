"""
game_scene.py
Escena principal de juego: Endless Runner espacial.

Mecánicas:
- Nave en posición X fija, cambia de carril con ↑↓
- Asteroides generados aleatoriamente en carriles
- Powerups: energy (+score), shield (invulnerabilidad temporal), multiplier (x2)
- Velocidad incrementa con el tiempo
- Al morir → guardado automático del puntaje y perfil
"""

import pygame
import math
import random
from game.constants import *
from game.draw_utils import (
    draw_text, draw_panel, draw_ship, draw_asteroid, draw_powerup,
    draw_stars, draw_lane_guides, draw_hud, draw_shield_effect,
    draw_explosion, draw_bar, draw_glow_rect
)


class Asteroid:
    def __init__(self, lane: int, speed: float):
        self.lane = lane
        self.x = float(WIDTH + ASTEROID_W)
        self.y = float(LANE_Y[lane])
        self.speed = speed
        self.rotation = 0.0
        self.rot_speed = random.uniform(-2.0, 2.0)
        self.size = random.randint(32, 52)
        self.dodged = False  # para dar puntos al esquivar

    def update(self, dt: float):
        self.x -= self.speed * dt
        self.rotation += self.rot_speed * dt

    def is_offscreen(self) -> bool:
        return self.x < -self.size

    def get_rect(self) -> pygame.Rect:
        r = self.size // 2 - 4
        return pygame.Rect(self.x - r, self.y - r, r * 2, r * 2)


class Powerup:
    TYPES = ["energy", "shield", "multiplier"]

    def __init__(self, lane: int, speed: float):
        self.lane = lane
        self.x = float(WIDTH + POWERUP_SIZE)
        self.y = float(LANE_Y[lane])
        self.speed = speed * 0.85
        self.ptype = random.choice(self.TYPES)
        self.collected = False

    def update(self, dt: float):
        self.x -= self.speed * dt

    def is_offscreen(self) -> bool:
        return self.x < -POWERUP_SIZE

    def get_rect(self) -> pygame.Rect:
        r = POWERUP_SIZE // 2
        return pygame.Rect(self.x - r, self.y - r, r * 2, r * 2)


class GameScene:
    """Escena principal de juego."""

    SHIELD_DURATION    = 5.0    # segundos
    MULTIPLIER_DURATION= 8.0
    LANE_CHANGE_TIME   = 0.12   # segundos para cambiar carril

    def __init__(self, profile_repo, leaderboard_repo, settings_repo, continue_game=False):
        self._profile_repo    = profile_repo
        self._leaderboard_repo= leaderboard_repo
        self._settings        = settings_repo.get()
        self._player_name     = self._settings.get("player_name", "PILOT")
        self._player_id       = self._player_name.lower().replace(" ", "_")
        self._diff_mult       = DIFFICULTY_MULT.get(self._settings.get("difficulty", "Normal"), 1.0)

        self._reset()

    def _reset(self):
        self._lane        = 1               # carril actual (0,1,2)
        self._target_lane = 1
        self._ship_y      = float(LANE_Y[1])
        self._lane_t      = 0.0             # tiempo interpolando cambio de carril

        self._speed       = BASE_SPEED * self._diff_mult
        self._score       = 0
        self._distance    = 0               # metros
        self._time        = 0.0
        self._powerups_collected = 0

        self._asteroids: list[Asteroid] = []
        self._powerups: list[Powerup]   = []
        self._explosions = []             # (x, y, progress)

        self._spawn_timer    = 0.0
        self._spawn_interval = 1.6
        self._speed_timer    = 0.0

        self._shield_timer   = 0.0
        self._mult_timer     = 0.0
        self._multiplier     = 1

        self._alive   = True
        self._t       = 0.0

        # Para screen de game over
        self._game_over_t  = 0.0
        self._saved        = False
        self._final_score  = 0
        self._final_dist   = 0

    def handle_event(self, event):
        """Retorna 'menu' para volver al menú, None si continúa."""
        if not self._alive:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self._reset()
                elif event.key == pygame.K_ESCAPE:
                    return "menu"
            return None

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w) and self._target_lane > 0:
                self._target_lane -= 1
                self._lane_t = 0.0
            elif event.key in (pygame.K_DOWN, pygame.K_s) and self._target_lane < LANE_COUNT - 1:
                self._target_lane += 1
                self._lane_t = 0.0
            elif event.key == pygame.K_ESCAPE:
                return "menu"
        return None

    def update(self, dt: float, stars):
        self._t += dt
        stars.update(self._speed, dt)

        if not self._alive:
            self._game_over_t += dt
            self._auto_save()
            # Explosión
            self._explosions = [(x, y, p + dt * 1.5) for x, y, p in self._explosions if p < 1.0]
            return

        # ── Velocidad creciente ──────────────────────────────────────────
        self._speed_timer += dt
        if self._speed_timer >= 5.0:
            self._speed_timer = 0.0
            self._speed = min(self._speed + SPEED_INC * self._diff_mult, MAX_SPEED)
            self._spawn_interval = max(0.55, self._spawn_interval - 0.07)

        # ── Score y distancia ────────────────────────────────────────────
        self._time     += dt
        self._score    += int(SCORE_PER_SEC * dt * self._multiplier)
        self._distance  = int(self._time * self._speed * 0.05)

        # ── Timers de powerup ────────────────────────────────────────────
        if self._shield_timer > 0:
            self._shield_timer -= dt
        if self._mult_timer > 0:
            self._mult_timer -= dt
        else:
            self._multiplier = 1

        # ── Movimiento de carril ─────────────────────────────────────────
        if self._lane != self._target_lane:
            self._lane_t += dt / self.LANE_CHANGE_TIME
            if self._lane_t >= 1.0:
                self._lane_t = 1.0
                self._lane  = self._target_lane
            # Interpolación suave (ease-in-out)
            t = self._lane_t
            ease = t * t * (3 - 2 * t)
            src = LANE_Y[self._lane if self._lane_t == 1.0 else
                         (self._target_lane + (1 if self._target_lane < self._lane else -1))]
            dst = LANE_Y[self._target_lane]
            # Recalcular desde el carril original
            orig_lane = self._target_lane + (1 if self._target_lane < self._lane else -1)
            orig_y = LANE_Y[min(max(orig_lane, 0), LANE_COUNT-1)]
            self._ship_y = orig_y + (LANE_Y[self._target_lane] - orig_y) * ease
        else:
            self._ship_y = float(LANE_Y[self._lane])

        # ── Spawn de asteroides ──────────────────────────────────────────
        self._spawn_timer += dt
        if self._spawn_timer >= self._spawn_interval:
            self._spawn_timer = 0.0
            self._spawn_asteroid()
            if random.random() < 0.25:
                self._spawn_powerup()

        # ── Actualizar objetos ───────────────────────────────────────────
        for a in self._asteroids:
            a.update(dt)
        for p in self._powerups:
            p.update(dt)
        self._explosions = [(x, y, pr + dt * 1.5) for x, y, pr in self._explosions if pr < 1.0]

        # Eliminar fuera de pantalla
        self._asteroids = [a for a in self._asteroids if not a.is_offscreen()]
        self._powerups  = [p for p in self._powerups  if not p.is_offscreen()]

        # Puntos por esquivar
        for a in self._asteroids:
            if not a.dodged and a.x < SHIP_X - SHIP_W:
                a.dodged = True
                self._score += SCORE_PER_DODGE * self._multiplier

        # ── Colisiones ───────────────────────────────────────────────────
        ship_rect = pygame.Rect(
            SHIP_X - SHIP_W // 2 + 6,
            int(self._ship_y) - SHIP_H // 2 + 4,
            SHIP_W - 12, SHIP_H - 8
        )

        for a in self._asteroids:
            if ship_rect.colliderect(a.get_rect()):
                if self._shield_timer > 0:
                    self._asteroids.remove(a)
                    self._explosions.append((a.x, a.y, 0.0))
                    break
                else:
                    self._die()
                    return

        for p in self._powerups:
            if not p.collected and ship_rect.colliderect(p.get_rect()):
                p.collected = True
                self._collect_powerup(p.ptype)

        self._powerups = [p for p in self._powerups if not p.collected]

    def _spawn_asteroid(self):
        # Nunca llenar todos los carriles al mismo tiempo consecutivo
        lanes = list(range(LANE_COUNT))
        random.shuffle(lanes)
        count = random.randint(1, 2)
        for lane in lanes[:count]:
            self._asteroids.append(Asteroid(lane, self._speed))

    def _spawn_powerup(self):
        lane = random.randint(0, LANE_COUNT - 1)
        self._powerups.append(Powerup(lane, self._speed))

    def _collect_powerup(self, ptype: str):
        self._powerups_collected += 1
        if ptype == "energy":
            self._score += SCORE_PER_POWERUP * self._multiplier
        elif ptype == "shield":
            self._shield_timer = self.SHIELD_DURATION
        elif ptype == "multiplier":
            self._multiplier = 2
            self._mult_timer = self.MULTIPLIER_DURATION

    def _die(self):
        self._alive = False
        self._final_score = self._score
        self._final_dist  = self._distance
        self._explosions.append((SHIP_X, int(self._ship_y), 0.0))

    def _auto_save(self):
        if self._saved:
            return
        if self._game_over_t >= 0.5:  # pequeño delay para que cargue bien
            self._leaderboard_repo.submit_score(
                self._player_id, self._player_name,
                self._final_score, self._final_dist
            )
            self._profile_repo.update_after_run(
                self._player_id, self._final_score, self._final_dist,
                self._powerups_collected, self._time
            )
            self._saved = True

    def draw(self, surface, stars):
        surface.fill(DEEP_SPACE)
        draw_stars(surface, stars.get_stars())
        draw_lane_guides(surface)

        # Asteroides
        for a in self._asteroids:
            draw_asteroid(surface, a.x, a.y, a.size, a.rotation)

        # Powerups
        for p in self._powerups:
            draw_powerup(surface, p.x, p.y, p.ptype, self._t)

        # Nave
        if self._alive:
            if self._shield_timer > 0:
                draw_shield_effect(surface, SHIP_X, int(self._ship_y))
            draw_ship(surface, SHIP_X, int(self._ship_y), engine_t=self._t)

        # Explosiones
        for (ex, ey, ep) in self._explosions:
            draw_explosion(surface, ex, ey, min(ep, 1.0))

        # HUD
        draw_hud(surface, self._score, self._distance, self._speed,
                 self._shield_timer > 0, self._multiplier, self._time)

        # Barra de escudo
        if self._shield_timer > 0:
            draw_bar(surface, 10, HEIGHT - 24, 120, 10,
                     self._shield_timer, self.SHIELD_DURATION, CYAN, label="SHIELD")

        # Barra de multiplicador
        if self._mult_timer > 0:
            draw_bar(surface, 150, HEIGHT - 24, 120, 10,
                     self._mult_timer, self.MULTIPLIER_DURATION, MAGENTA, label="x2")

        # Velocidad visual (barra)
        spd_ratio = (self._speed - BASE_SPEED) / (MAX_SPEED - BASE_SPEED)
        draw_bar(surface, WIDTH - 140, HEIGHT - 24, 120, 10,
                 spd_ratio, 1.0, ORANGE, label="SPD")

        # ── GAME OVER ────────────────────────────────────────────────────
        if not self._alive:
            self._draw_game_over(surface)

    def _draw_game_over(self, surface):
        # Overlay oscuro
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        alpha = min(180, int(self._game_over_t * 120))
        overlay.fill((0, 0, 0, alpha))
        surface.blit(overlay, (0, 0))

        cx = WIDTH // 2
        cy = HEIGHT // 2

        panel = pygame.Rect(cx - 220, cy - 150, 440, 300)
        from game.draw_utils import draw_panel
        draw_panel(surface, panel, MAGENTA_DIM, DARK_PANEL, 230)

        draw_text(surface, "SHIP DESTROYED", 32, MAGENTA, cx, cy - 120, anchor="center")

        # Línea separadora
        pygame.draw.line(surface, MAGENTA_DIM, (cx - 160, cy - 82), (cx + 160, cy - 82), 1)

        draw_text(surface, f"SCORE    {self._final_score:>8}", 22, CYAN,    cx, cy - 60, anchor="center")
        draw_text(surface, f"DISTANCE {self._final_dist:>6}m", 22, YELLOW,  cx, cy - 28, anchor="center")
        draw_text(surface, f"TIME     {int(self._time)//60:02d}:{int(self._time)%60:02d}", 22, GRAY, cx, cy + 4, anchor="center")

        if self._saved:
            draw_text(surface, "✓  SCORE SAVED", 16, GREEN, cx, cy + 44, anchor="center")
        else:
            draw_text(surface, "SAVING...", 16, GRAY, cx, cy + 44, anchor="center")

        pygame.draw.line(surface, CYAN_DIM, (cx - 160, cy + 68), (cx + 160, cy + 68), 1)

        blink = int(self._game_over_t * 2) % 2 == 0
        if blink:
            draw_text(surface, "[R] RETRY    [ESC] MENU", 17, GRAY, cx, cy + 86, anchor="center")

    def get_score(self) -> int:
        return self._score
