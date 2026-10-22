import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame
pygame.init()

from config import SCREEN_WIDTH, SCREEN_HEIGHT
from ui.menu import MainMenu

OUT_DIR = r"C:\Users\VINU\.gemini\antigravity-ide\brain\1e5f1edf-a9e3-4689-8e98-1f3d6d44d199"

def render_progression():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    menu = MainMenu(
        on_play=lambda: None,
        on_level_select=lambda: None,
        on_challenges=lambda: None,
        on_instructions=lambda: None,
        on_camera_check=lambda: None,
        on_quit=lambda: None,
        on_museum=lambda: None,
    )

    # 1. Update 30 frames (~1.0s: Downstroke power surge)
    for _ in range(30):
        menu.update(
            cursor_x=640,
            cursor_y=360,
            is_clicked=False,
            dt=0.033,
            is_hand_detected=True,
            num_hands=1,
            is_pinching=False
        )
    menu.draw(screen)
    shot1_path = os.path.join(OUT_DIR, "menu_turtle_stroke_1s.png")
    pygame.image.save(screen, shot1_path)
    print(f"Saved: {shot1_path}")

    # 2. Update another 45 frames (~2.5s: Extended graceful glide)
    for _ in range(45):
        menu.update(
            cursor_x=640,
            cursor_y=360,
            is_clicked=False,
            dt=0.033,
            is_hand_detected=True,
            num_hands=1,
            is_pinching=False
        )
    menu.draw(screen)
    shot2_path = os.path.join(OUT_DIR, "menu_turtle_glide_2s.png")
    pygame.image.save(screen, shot2_path)
    print(f"Saved: {shot2_path}")

if __name__ == "__main__":
    render_progression()
