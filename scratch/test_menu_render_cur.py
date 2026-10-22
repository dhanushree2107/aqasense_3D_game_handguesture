import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import pygame
os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()

from ui.menu import MainMenu
from config import SCREEN_WIDTH, SCREEN_HEIGHT

OUT_DIR = r"C:\Users\VINU\.gemini\antigravity-ide\brain\1e5f1edf-a9e3-4689-8e98-1f3d6d44d199"

def render_menu_shots():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    menu = MainMenu(
        on_play=lambda: None,
        on_level_select=lambda: None,
        on_challenges=lambda: None,
        on_instructions=lambda: None,
        on_camera_check=lambda: None,
        on_quit=lambda: None,
    )

    dt = 0.033  # ~30 fps
    # Simulate 3 seconds
    for f in range(1, 91):
        menu.update(640, 360, False, dt, is_hand_detected=True, num_hands=1)
        if f == 1:
            menu.draw(screen)
            pygame.image.save(screen, os.path.join(OUT_DIR, "menu_initial_render.png"))
        elif f == 60:
            menu.draw(screen)
            pygame.image.save(screen, os.path.join(OUT_DIR, "menu_2s_render.png"))

    print("Rendered snapshots to artifact dir successfully.")

if __name__ == "__main__":
    render_menu_shots()
