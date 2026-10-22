import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame
pygame.init()

from game.game_manager import GameManager
from config import SCREEN_WIDTH, SCREEN_HEIGHT

OUT_DIR = r"C:\Users\VINU\.gemini\antigravity-ide\brain\1e5f1edf-a9e3-4689-8e98-1f3d6d44d199"

def test_render():
    gm = GameManager()
    gm.start_new_expedition()
    gm.hand_detector.stop()

    # Step simulation forward so fish swim and undulate
    for _ in range(60):
        gm._update_gameplay(
            dt=0.033,
            target_x=640,
            target_y=360,
            pinch_triggered=False,
            palm_triggered=False,
            sonar_triggered=False,
            shield_active=False
        )

    gm._render()
    out_path = os.path.join(OUT_DIR, "gameplay_realistic_swimming.png")
    pygame.image.save(gm.screen, out_path)
    print(f"Saved: {out_path}")

if __name__ == "__main__":
    test_render()
