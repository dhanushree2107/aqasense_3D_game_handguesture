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

def render_dolphin_snapshots():
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

    # Snapshot 1: At 0.8 second
    for _ in range(24):
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
    shot1 = os.path.join(OUT_DIR, "menu_dolphins_ocean_1s.png")
    pygame.image.save(screen, shot1)
    print(f"Saved: {shot1}")

    # Snapshot 2: At 2.2 seconds (undulating cruise)
    for _ in range(42):
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
    shot2 = os.path.join(OUT_DIR, "menu_dolphins_ocean_2s.png")
    pygame.image.save(screen, shot2)
    print(f"Saved: {shot2}")

    # Snapshot 3: At 4.0 seconds (gliding through right ocean reef)
    for _ in range(54):
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
    shot3 = os.path.join(OUT_DIR, "menu_dolphins_ocean_3s.png")
    pygame.image.save(screen, shot3)
    print(f"Saved: {shot3}")

if __name__ == "__main__":
    render_dolphin_snapshots()
