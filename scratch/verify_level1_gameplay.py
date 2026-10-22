import os
import sys

# Ensure workspace root is in python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
import time

# Set headless SDL dummy driver
os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()

from game.game_manager import GameManager, GameState
from config import SCREEN_WIDTH, SCREEN_HEIGHT

OUT_DIR = r"C:\Users\VINU\.gemini\antigravity-ide\brain\c4f442f1-2477-4917-8514-fc8478138646"

def render_level1_frames():
    gm = GameManager()
    gm.start_new_expedition()
    gm.hand_detector.stop()  # Stop webcam background thread for deterministic snapshot

    # Run for several seconds to capture fish movement, burst-and-glide, and turtle swimming
    dt = 0.033  # ~30fps
    for sec in [1.0, 3.0, 5.0]:
        target_frames = int(sec / dt)
        for _ in range(target_frames):
            gm._update_gameplay(
                dt=dt,
                target_x=640,
                target_y=360,
                pinch_triggered=False,
                palm_triggered=False,
                sonar_triggered=False,
                shield_active=False,
            )

        gm.screen.fill((0, 0, 0))
        gm._render()

        out_path = os.path.join(OUT_DIR, f"level1_gameplay_t{int(sec)}s.png")
        pygame.image.save(gm.screen, out_path)
        print(f"Saved: {out_path}")

if __name__ == "__main__":
    render_level1_frames()
