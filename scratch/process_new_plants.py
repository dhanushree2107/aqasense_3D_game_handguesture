import os
import numpy as np
from PIL import Image, ImageFilter
from collections import deque

BRAIN_DIR = r"C:\Users\VINU\.gemini\antigravity-ide\brain\a789893e-10cd-48ad-af3f-1b1215f7da27"
ASSETS_DIR = r"c:\project 1\underwater trrasure hand guesture game\assets"

def process_botanical_asset(img_path, out_path, tolerance=230, defringe=True):
    print(f"Processing {img_path} -> {out_path}...")
    img = Image.open(img_path).convert("RGBA")
    arr = np.array(img, dtype=np.float32)
    
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    # White background detection
    min_rgb = np.minimum(np.minimum(r, g), b)
    h, w = min_rgb.shape
    
    near_white = (min_rgb >= tolerance)
    
    # Flood fill from boundaries
    is_bg = np.zeros((h, w), dtype=bool)
    q = deque()
    for x in range(w):
        if near_white[0, x]: q.append((0, x)); is_bg[0, x] = True
        if near_white[h-1, x]: q.append((h-1, x)); is_bg[h-1, x] = True
    for y in range(h):
        if near_white[y, 0]: q.append((y, 0)); is_bg[y, 0] = True
        if near_white[y, w-1]: q.append((y, w-1)); is_bg[y, w-1] = True
        
    while q:
        cy, cx = q.popleft()
        for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            ny, nx = cy + dy, cx + dx
            if 0 <= ny < h and 0 <= nx < w and not is_bg[ny, nx]:
                if near_white[ny, nx]:
                    is_bg[ny, nx] = True
                    q.append((ny, nx))
                    
    # Initialize alpha
    alpha = np.ones((h, w), dtype=np.float32) * 255.0
    alpha[is_bg] = 0.0
    
    # For pixels near the background edge that have high brightness, fade alpha smoothly
    # Find background boundary
    bg_dilated = Image.fromarray(is_bg.astype(np.uint8) * 255).filter(ImageFilter.MaxFilter(7))
    is_near_edge = (np.array(bg_dilated) > 0) & (~is_bg)
    
    # Smooth edge alpha
    for y in range(h):
        for x in range(w):
            if is_near_edge[y, x]:
                val = min_rgb[y, x]
                if val > 200:
                    alpha[y, x] = max(0.0, min(255.0, (255.0 - val) / (255.0 - 200.0) * 255.0))
                    
    mask_img = Image.fromarray(alpha.astype(np.uint8), mode="L")
    mask_blurred = mask_img.filter(ImageFilter.GaussianBlur(1.2))
    final_alpha = np.array(mask_blurred, dtype=np.float32) / 255.0
    
    # Defringe: remove white halo by un-mixing white background
    res_arr = arr.copy()
    if defringe:
        for c in range(3):
            # c_unmixed = (c_composite - (1 - alpha)*255) / max(alpha, 0.01)
            c_val = res_arr[:, :, c]
            unmixed = (c_val - (1.0 - final_alpha) * 255.0) / np.maximum(final_alpha, 0.05)
            # Clip between 0 and 255
            res_arr[:, :, c] = np.clip(unmixed, 0, 255)
            
    res_arr[:, :, 3] = final_alpha * 255.0
    res_img = Image.fromarray(res_arr.astype(np.uint8), mode="RGBA")
    
    # Crop to bounding box
    bbox = res_img.getbbox()
    if bbox:
        res_img = res_img.crop(bbox)
        
    res_img.save(out_path)
    print(f"Saved {out_path} ({res_img.size}) successfully!")

if __name__ == "__main__":
    kelp_in = os.path.join(BRAIN_DIR, "realistic_kelp_plant_1792070953667.jpg")
    seagrass_in = os.path.join(BRAIN_DIR, "realistic_seagrass_plant_1792070978249.jpg")
    
    kelp_out = os.path.join(ASSETS_DIR, "ocean_kelp_frond.png")
    seagrass_out = os.path.join(ASSETS_DIR, "ocean_seagrass.png")
    
    process_botanical_asset(kelp_in, kelp_out, tolerance=235)
    process_botanical_asset(seagrass_in, seagrass_out, tolerance=235)
