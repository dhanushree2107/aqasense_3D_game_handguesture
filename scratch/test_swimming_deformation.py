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

OUT_DIR = r"C:\Users\VINU\.gemini\antigravity-ide\brain\1e5f1edf-a9e3-4689-8e98-1f3d6d44d199"

def deform_fish(surface: pygame.Surface, target_w: int, target_h: int, swim_phase: float, tail_amp: float, facing_left: bool, turn_scale_x: float, pitch: float) -> pygame.Surface:
    """
    Renders realistic subcarangiform swimming deformation:
    - Head stays rigid and stable
    - Mid-body and caudal fin articulate in a traveling hydrodynamic wave
    - 3D turn foreshortening and pitch banking
    """
    eff_w = max(12, int(target_w * abs(turn_scale_x)))
    eff_h = max(8, target_h)
    
    scaled = pygame.transform.smoothscale(surface, (eff_w, eff_h))
    current_facing_left = facing_left if turn_scale_x >= 0 else not facing_left
    if not current_facing_left:
        scaled = pygame.transform.flip(scaled, True, False)
        
    num_slices = 20
    slice_step = eff_w / num_slices
    slice_w = int(math.ceil(slice_step)) + 1
    max_pad_y = int(tail_amp * 1.5) + 10
    
    bent_surf = pygame.Surface((eff_w + 10, eff_h + max_pad_y * 2), pygame.SRCALPHA)
    
    for i in range(num_slices):
        # 0 = snout/head, 1 = caudal tail tip
        ratio = (i / (num_slices - 1)) if current_facing_left else (1.0 - i / (num_slices - 1))
        
        # Subcarangiform wave: head (ratio < 0.28) is firm, trunk & caudal fin flex
        if ratio < 0.28:
            amp = 0.0
        else:
            amp = (((ratio - 0.28) / 0.72) ** 2.2) * tail_amp
            
        phase_lag = ratio * 3.2
        offset_y = math.sin(swim_phase - phase_lag) * amp
        
        sx = int(i * slice_step)
        cur_sw = slice_w if sx + slice_w <= eff_w else (eff_w - sx)
        
        if cur_sw > 0:
            rect = pygame.Rect(sx, 0, cur_sw, eff_h)
            bent_surf.blit(scaled, (sx + 5, max_pad_y + offset_y), rect)
            
    if abs(pitch) > 0.5:
        final_surf = pygame.transform.rotate(bent_surf, pitch)
    else:
        final_surf = bent_surf
        
    return final_surf

def run_test():
    pygame.display.set_mode((400, 300))
    clown_path = os.path.join(PROJECT_ROOT, "assets", "clownfish.png")
    clown_surf = pygame.image.load(clown_path).convert_alpha()
    
    test_screen = pygame.Surface((400, 300), pygame.SRCALPHA)
    test_screen.fill((10, 40, 70))
    
    # Render at peak tail stroke left, center, right
    s1 = deform_fish(clown_surf, 90, 52, 0.0, 7.0, True, 1.0, 0.0)
    s2 = deform_fish(clown_surf, 90, 52, math.pi / 2, 7.0, True, 1.0, -8.0)
    s3 = deform_fish(clown_surf, 90, 52, math.pi, 7.0, True, 0.4, 12.0) # mid-turn
    
    test_screen.blit(s1, (20, 100))
    test_screen.blit(s2, (140, 100))
    test_screen.blit(s3, (260, 100))
    
    out_path = os.path.join(OUT_DIR, "test_fish_deformation.png")
    pygame.image.save(test_screen, out_path)
    print("Saved deformation test to", out_path)

if __name__ == "__main__":
    run_test()
