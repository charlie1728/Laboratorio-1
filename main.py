"""
main.py
Punto de entrada de VOID RUNNER.
Gestiona el loop principal de Pygame y la máquina de estados de escenas.

Escenas:
  menu        → Menú principal
  game        → Partida nueva
  continue    → Continuar (misma lógica, distinto flag)
  leaderboard → Top scores
  settings    → Configuración
  hash_viz    → Visualizador tabla hash (bonus)
  quit        → Salir
"""

import sys
import os

# Pygbag requiere que el loop sea una corrutina asíncrona
import asyncio

import pygame

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

# ── Importaciones del proyecto ────────────────────────────────────────────────
from game.constants import WIDTH, HEIGHT, FPS, TITLE, DEEP_SPACE
from game.starfield import Starfield

from persistence.engine import PersistenceEngine

from repositories.profile_repository    import ProfileRepository
from repositories.leaderboard_repository import LeaderboardRepository
from repositories.settings_repository   import SettingsRepository

from game.scenes.menu        import MenuScene
from game.scenes.game_scene  import GameScene
from game.scenes.leaderboard import LeaderboardScene
from game.scenes.settings    import SettingsScene
from game.scenes.hash_viz    import HashVizScene


# ─────────────────────────────────────────────────────────────────────────────
#  Inicialización
# ─────────────────────────────────────────────────────────────────────────────

def init_engine() -> PersistenceEngine:
    """Crea el motor de persistencia apuntando a los archivos del proyecto."""
    data_path  = os.path.join(BASE_DIR, "data.csv")
    index_path = os.path.join(BASE_DIR, "index.bin")
    return PersistenceEngine(data_path, index_path)


def build_repos(engine: PersistenceEngine):
    profile_repo    = ProfileRepository(engine)
    leaderboard_repo = LeaderboardRepository(engine)
    settings_repo   = SettingsRepository(engine)
    return profile_repo, leaderboard_repo, settings_repo


# ─────────────────────────────────────────────────────────────────────────────
#  Loop principal (compatible con Pygbag vía asyncio)
# ─────────────────────────────────────────────────────────────────────────────

async def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(TITLE)
    clock  = pygame.time.Clock()

    # Persistencia
    engine       = init_engine()
    profile_repo, leaderboard_repo, settings_repo = build_repos(engine)

    # Fondo de estrellas compartido entre escenas
    starfield = Starfield(n_stars=140)

    # Escena inicial
    current_scene_name = "menu"
    current_scene = MenuScene(profile_repo, settings_repo)

    def load_scene(name: str, **kwargs):
        """Fábrica de escenas."""
        if name == "menu":
            return MenuScene(profile_repo, settings_repo)
        elif name in ("game", "continue"):
            return GameScene(profile_repo, leaderboard_repo, settings_repo,
                             continue_game=(name == "continue"))
        elif name == "leaderboard":
            return LeaderboardScene(leaderboard_repo, settings_repo)
        elif name == "settings":
            return SettingsScene(settings_repo)
        elif name == "hash_viz":
            return HashVizScene(engine, settings_repo)
        return None

    running = True

    while running:
        dt = clock.tick(FPS) / 1000.0
        dt = min(dt, 0.05)   # clamp para evitar saltos por lag

        # ── Eventos ───────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            # Tecla especial para abrir visualizador hash desde cualquier lugar
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F1:
                if current_scene_name != "hash_viz":
                    current_scene_name = "hash_viz"
                    current_scene = load_scene("hash_viz")
                    continue

            result = current_scene.handle_event(event)
            if result is not None:
                if result == "quit":
                    running = False
                    break
                new_scene = load_scene(result)
                if new_scene is not None:
                    current_scene_name = result
                    current_scene = new_scene

        if not running:
            break

        # ── Actualización ─────────────────────────────────────────────────
        current_scene.update(dt, starfield)

        # ── Dibujo ───────────────────────────────────────────────────────
        screen.fill(DEEP_SPACE)
        current_scene.draw(screen, starfield)

        # Watermark de escena actual (debug ligero, visible solo en desarrollo)
        # Descomentar si se desea:
        # pygame.draw.rect(screen, (20,20,40), pygame.Rect(0, HEIGHT-16, 200, 16))
        # font_sm = pygame.font.SysFont("courier", 11)
        # screen.blit(font_sm.render(f"scene:{current_scene_name}  F1=HashViz", True, (60,60,80)), (4, HEIGHT-14))

        pygame.display.flip()

        # Pygbag requiere yield para no bloquear el event loop del navegador
        await asyncio.sleep(0)

    pygame.quit()


# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    asyncio.run(main())
