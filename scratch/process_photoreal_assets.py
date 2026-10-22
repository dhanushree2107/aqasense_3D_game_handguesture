"""
Process generated photorealistic assets:
Extract white background to smooth alpha transparency, defringe edges,
and save to assets/ directory for AquaSense game.
"""

import os
import numpy as np
from PIL import Image, ImageFilter

BRAIN_DIR = r"C:\Users\VINU\.gemini\antigravity-ide\brain\6ec96780-482b-4dbe-b496-e4fb63d29adb"
ASSETS_DIR = r"c:\project 1\underwater trrasure hand guesture game\assets"

def remove_white_bg(img_path, tolerance=240, feather_radius=1.5):
    img = Image.open(img_path).convert("RGBA")
    arr = np.array(img, dtype=np.float32)
    
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    # Brightness / distance from white (255, 255, 255)
    # White background check
    min_val = np.minimum(np.minimum(r, g), b)
    # Soft alpha ramp between tolerance and 255
    alpha = np.clip((255.0 - min_val) / (255.0 - tolerance) * 255.0, 0, 255).astype(np.uint8)
    
    # Simple flood-fill mask from top-left and borders to avoid removing white highlights inside object
    from collections import deque
    h, w = alpha.shape
    is_bg = np.zeros((h, w), dtype=bool)
    
    # Check pixels near white
    near_white = (min_val >= tolerance)
    
    q = deque()
    # Add border pixels that are near white
    for x in range(w):
        if near_white[0, x]: q.append((0, x)); is_bg[0, x] = True
        if near_white[h-1, x]: q.append((h-1, x)); is_bg[h-1, x] = True
    for y in range(h):
        if near_white[y, 0]: q.append((y, 0)); is_bg[y, 0] = True
        if near_white[y, w-1]: q.append((y, w-1)); is_bg[y, w-1] = True
        
    while q:
        cy, cx = q.popleft()
        for dy, dx in [(-1,0), (1,0), (0,-1), (0,1)]:
            ny, nx = cy + dy, cx + dx
            if 0 <= ny < h and 0 <= nx < w and not is_bg[ny, nx]:
                if near_white[ny, nx]:
                    is_bg[ny, nx] = True
                    q.append((ny, nx))
                    
    # For pixels identified as background, compute smooth alpha
    final_alpha = np.ones((h, w), dtype=np.uint8) * 255
    final_alpha[is_bg] = 0
    
    # Soft feathering at transition border
    mask_img = Image.fromarray(final_alpha, mode="L")
    mask_blurred = mask_img.filter(ImageFilter.GaussianBlur(feather_radius))
    
    # Combine with original RGB
    img.putalpha(mask_blurred)
    return img

def main():
    os.makedirs(ASSETS_DIR, exist_ok=True)
    
    # 1. Scuba Diver
    diver_path = os.path.join(BRAIN_DIR, "photoreal_scuba_diver_1792043808301.jpg")
    if os.path.exists(diver_path):
        print("Processing Diver...")
        diver_img = remove_white_bg(diver_path, tolerance=232, feather_radius=1.8)
        # Crop tight bounding box
        bbox = diver_img.getbbox()
        if bbox:
            diver_img = diver_img.crop(bbox)
        out_diver = os.path.join(ASSETS_DIR, "scuba_diver_hd.png")
        diver_img.save(out_diver)
        print(f"Saved: {out_diver} ({diver_img.size})")

    # 2. Seabed Oxygen Vent
    vent_path = os.path.join(BRAIN_DIR, "seabed_oxygen_vent_1792043837575.jpg")
    if os.path.exists(vent_path):
        print("Processing Oxygen Vent...")
        vent_img = remove_white_bg(vent_path, tolerance=205, feather_radius=1.8)
        bbox = vent_img.getbbox()
        if bbox:
            vent_img = vent_img.crop(bbox)
        out_vent = os.path.join(ASSETS_DIR, "seabed_oxygen_vent.png")
        vent_img.save(out_vent)
        print(f"Saved: {out_vent} ({vent_img.size})")

    # 3. Ancient Stone Pedestal
    ped_path = os.path.join(BRAIN_DIR, "ancient_stone_pedestal_1792043896666.jpg")
    if os.path.exists(ped_path):
        print("Processing Stone Pedestal...")
        ped_img = remove_white_bg(ped_path, tolerance=235, feather_radius=1.5)
        bbox = ped_img.getbbox()
        if bbox:
            ped_img = ped_img.crop(bbox)
        out_ped = os.path.join(ASSETS_DIR, "ancient_stone_pedestal.png")
        ped_img.save(out_ped)
        print(f"Saved: {out_ped} ({ped_img.size})")

    # 4. Ocean Kelp Fronds
    kelp_path = os.path.join(BRAIN_DIR, "ocean_kelp_frond_1792043866350.jpg")
    if os.path.exists(kelp_path):
        print("Processing Kelp Frond...")
        k_img = Image.open(kelp_path).convert("RGBA")
        k_arr = np.array(k_img, dtype=np.float32)
        r, g, b = k_arr[:, :, 0], k_arr[:, :, 1], k_arr[:, :, 2]
        
        # Identify white background and light-cyan sunlight patch
        is_bg_color = (np.minimum(np.minimum(r, g), b) >= 225) | ((b >= 160) & (g >= 170) & (b - r >= 15))
        
        from collections import deque
        h, w = is_bg_color.shape
        is_bg = np.zeros((h, w), dtype=bool)
        q = deque()
        for x in range(w):
            if is_bg_color[0, x]: q.append((0, x)); is_bg[0, x] = True
            if is_bg_color[h-1, x]: q.append((h-1, x)); is_bg[h-1, x] = True
        for y in range(h):
            if is_bg_color[y, 0]: q.append((y, 0)); is_bg[y, 0] = True
            if is_bg_color[y, w-1]: q.append((y, w-1)); is_bg[y, w-1] = True

        while q:
            cy, cx = q.popleft()
            for dy, dx in [(-1,0), (1,0), (0,-1), (0,1)]:
                ny, nx = cy + dy, cx + dx
                if 0 <= ny < h and 0 <= nx < w and not is_bg[ny, nx]:
                    if is_bg_color[ny, nx]:
                        is_bg[ny, nx] = True
                        q.append((ny, nx))

        final_alpha = np.ones((h, w), dtype=np.float32) * 255.0
        final_alpha[is_bg] = 0.0
        mask_img = Image.fromarray(final_alpha.astype(np.uint8), mode="L")
        mask_blurred = mask_img.filter(ImageFilter.GaussianBlur(1.8))
        mask_arr = np.array(mask_blurred, dtype=np.float32)

        # Smooth fade on top 40px to taper tips seamlessly
        for y in range(40):
            factor = (y / 40.0) ** 1.5
            mask_arr[y, :] *= factor

        k_img.putalpha(Image.fromarray(mask_arr.astype(np.uint8), mode="L"))
        bbox = k_img.getbbox()
        if bbox:
            k_img = k_img.crop(bbox)
        out_kelp = os.path.join(ASSETS_DIR, "ocean_kelp_frond.png")
        k_img.save(out_kelp)
        print(f"Saved: {out_kelp} ({k_img.size})")

if __name__ == "__main__":
    main()
