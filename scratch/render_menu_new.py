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

def main():
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

    # Step forward 2 seconds so swimming kinematics and turtle positions update
    for _ in range(60):
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
    out_path = os.path.join(OUT_DIR, "menu_original_turtle_no_manta.png")
    pygame.image.save(screen, out_path)
    print(f"Saved: {out_path}")

if __name__ == "__main__":
    main()
