import os
import sys
import math
import random
from typing import Optional, Tuple, List
import pygame

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()

from config import SCREEN_WIDTH, SCREEN_HEIGHT

def run_simulation_benchmark():
    screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    
    # Load all textures
    assets = [
        "mermaid.png",
        "sea_angel_nudibranch.png",
        "tiered_silk_betta.png",
        "white_halfmoon_betta.png",
        "golden_seahorse.png",
        "dolphin_blue.png",
        "dolphin_pink.png",
    ]
    for a in assets:
        p = os.path.join(PROJECT_ROOT, "assets", a)
        assert os.path.isfile(p), f"Missing asset: {p}"
        surf = pygame.image.load(p)
        print(f"Asset OK: {a} -> {surf.get_size()}")
    
    print("All textures loaded successfully for simulation test!")

if __name__ == "__main__":
    run_simulation_benchmark()
