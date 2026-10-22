import os
import cv2
import numpy as np

ASSETS = r"c:\project 1\underwater trrasure hand guesture game\assets"

def clean_asset(filename, out_name=None, crop_speck=False):
    path = os.path.join(ASSETS, filename)
    img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if img is None:
        print("Missing:", filename)
        return
    
    b, g, r, a = cv2.split(img)
    
    if crop_speck:
        # Connected components on alpha to remove small isolated disconnected specks
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats((a > 20).astype(np.uint8))
        if num_labels > 2:
            # Keep only the largest foreground component
            largest_label = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
            mask = (labels == largest_label).astype(np.uint8) * 255
            a = cv2.bitwise_and(a, mask)

    # De-fringe: remove light halo bleed into transparent border
    # Semi-transparent pixels (0 < a < 250)
    semi = (a > 0) & (a < 240)
    # Erode alpha slightly if needed or color clamp
    cleaned = cv2.merge([b, g, r, a])
    
    target = os.path.join(ASSETS, out_name or filename)
    cv2.imwrite(target, cleaned)
    print(f"Refined {filename} -> {target}")

if __name__ == "__main__":
    clean_asset("golden_seahorse.png", crop_speck=True)
    clean_asset("sea_angel_nudibranch.png")
    clean_asset("tiered_silk_betta.png")
    clean_asset("white_halfmoon_betta.png")
