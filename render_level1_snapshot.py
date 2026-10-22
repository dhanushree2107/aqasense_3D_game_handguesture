import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
import pygame

from game.game_manager import GameManager, GameState

def main():
    gm = GameManager()
    gm.start_new_expedition()
    # Step forward 2 seconds of gameplay so animations, fish positions, etc. are populated
    for _ in range(120):
        gm._update(0.016)
    gm._render()
    
    out_path = os.path.join(os.path.dirname(__file__), "level1_current_view.png")
    pygame.image.save(gm.screen, out_path)
    print(f"Saved snapshot to {out_path}")
    gm.hand_detector.stop()
    pygame.quit()

if __name__ == "__main__":
    main()
