import os
import pygame
from PIL import Image, ImageFilter
import numpy as np

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")

def defringe_image(filename: str):
    path = os.path.join(ASSETS_DIR, filename)
    if not os.path.isfile(path):
        return
    
    img = Image.open(path).convert("RGBA")
    arr = np.array(img, dtype=np.uint8)
    
    # Red, Green, Blue, Alpha
    r = arr[:, :, 0].astype(np.float32)
    g = arr[:, :, 1].astype(np.float32)
    b = arr[:, :, 2].astype(np.float32)
    a = arr[:, :, 3].astype(np.float32)
    
    # Detect white/light fringe on semi-transparent or edge pixels
    brightness = (r + g + b) / 3.0
    
    # Halo criteria: semi-transparent (a < 240) and high brightness (brightness > 190)
    # Also if a < 40 and brightness > 150, it is pure background bleed
    is_fringe = (a > 0) & (a < 235) & (brightness > 170)
    
    # Erode fringe alpha and tint towards interior
    arr[:, :, 3][(a < 65) & (brightness > 160)] = 0
    
    # For remaining fringe, suppress the white brightness by blending with deep ocean cyan/blue
    mod_mask = (arr[:, :, 3] > 0) & (arr[:, :, 3] < 220) & (brightness > 180)
    arr[:, :, 0][mod_mask] = (arr[:, :, 0][mod_mask] * 0.45).astype(np.uint8)
    arr[:, :, 1][mod_mask] = (arr[:, :, 1][mod_mask] * 0.70).astype(np.uint8)
    arr[:, :, 2][mod_mask] = np.minimum(255, (arr[:, :, 2][mod_mask] * 1.15)).astype(np.uint8)
    
    cleaned = Image.fromarray(arr)
    backup_name = os.path.join(ASSETS_DIR, filename.replace(".png", "_fringe_backup.png"))
    if not os.path.exists(backup_name):
        img.save(backup_name)
    cleaned.save(path)
    print(f"De-fringed {filename} and backed up.")

if __name__ == "__main__":
    for f in ["clownfish.png", "blue_tang.png", "yellow_tang.png", "manta_ray.png", "shark.png"]:
        defringe_image(f)
