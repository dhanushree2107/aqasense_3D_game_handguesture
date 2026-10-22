import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
import time

os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()

from game.game_manager import GameManager, GameState

OUT_DIR = r"C:\Users\VINU\.gemini\antigravity-ide\brain\c4f442f1-2477-4917-8514-fc8478138646"

def render_level_frames():
    gm = GameManager()
    gm.hand_detector.stop()

    for lvl in [1, 2, 3]:
        gm.load_level(lvl)
        gm.set_state(GameState.PLAYING)
        # Advance simulation by 2 seconds so fish and marine life swim across the scene
        dt = 0.033
        for _ in range(60):
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

        out_path = os.path.join(OUT_DIR, f"clean_gameplay_lvl{lvl}.png")
        pygame.image.save(gm.screen, out_path)
        print(f"Rendered and saved Level {lvl}: {out_path}")

if __name__ == "__main__":
    render_level_frames()
