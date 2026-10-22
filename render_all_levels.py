import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
import pygame

from game.game_manager import GameManager

def main():
    gm = GameManager()
    
    for lvl in [2, 3, 4, 5]:
        print(f"Generating snapshot for Level {lvl}...", flush=True)
        gm.select_level_and_play(lvl)
        # Advance 60 frames for physics / positions
        for _ in range(60):
            gm._update(0.016)
        gm._render()
        
        out_path = os.path.join(os.path.dirname(__file__), f"level{lvl}_current_view.png")
        pygame.image.save(gm.screen, out_path)
        print(f"Saved: {out_path}", flush=True)
        
    gm.hand_detector.stop()
    pygame.quit()
    print("All level snapshots completed!")

if __name__ == "__main__":
    main()
