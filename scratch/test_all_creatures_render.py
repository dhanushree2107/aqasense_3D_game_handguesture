import os
import sys
import math
import pygame

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()

from config import SCREEN_WIDTH, SCREEN_HEIGHT

def test_load_all():
    assets = [
        "dolphin_blue.png",
        "dolphin_pink.png",
        "golden_seahorse.png",
        "sea_angel_nudibranch.png",
        "tiered_silk_betta.png",
        "white_halfmoon_betta.png"
    ]
    for a in assets:
        path = os.path.join(PROJECT_ROOT, "assets", a)
        surf = pygame.image.load(path)
        print(f"Loaded {a}: {surf.get_size()}")

if __name__ == "__main__":
    test_load_all()
