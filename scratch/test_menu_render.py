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

OUT_DIR = r"C:\Users\VINU\.gemini\antigravity-ide\brain\c4f442f1-2477-4917-8514-fc8478138646"

def capture_timeline():
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
    # Capture at: 1s, 3s, 6s
    checkpoints = {
        30: "menu_frame_t1.png",
        90: "menu_frame_t3.png",
        180: "menu_frame_t6.png"
    }

    for frame in range(1, 181):
        menu.update(640, 360, False, dt, is_hand_detected=True, num_hands=1)
        if frame in checkpoints:
            menu.draw(screen)
            out_path = os.path.join(OUT_DIR, checkpoints[frame])
            pygame.image.save(screen, out_path)
            print(f"Captured: {out_path} at frame {frame}")

if __name__ == "__main__":
    capture_timeline()
