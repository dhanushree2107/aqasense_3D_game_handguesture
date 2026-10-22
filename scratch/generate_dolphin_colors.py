import os
import cv2
import numpy as np

ASSETS_DIR = r"c:\project 1\underwater trrasure hand guesture game\assets"
SRC_PATH = os.path.join(ASSETS_DIR, "dolphin.png")

def create_color_graded_dolphins():
    img = cv2.imread(SRC_PATH, cv2.IMREAD_UNCHANGED)
    if img is None:
        print("Error: Could not load source dolphin!")
        return

    b, g, r, a = cv2.split(img)

    # Calculate luminance of skin
    gray = cv2.cvtColor(cv2.merge([b, g, r]), cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0

    # High-frequency texture (skin wrinkles, pores, folds)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    high_freq = (gray - blurred)

    # Specular highlight detection (wet skin reflections)
    spec = np.clip((gray - 0.65) / 0.35, 0.0, 1.0) ** 1.8

    # 1. OCEAN SAPPHIRE & AQUAMARINE BLUE DOLPHIN
    # Dorsal cape: Deep oceanic navy (0, 70, 160)
    # Flanks: Vibrant cerulean / aqua blue (20, 150, 255)
    # Belly: Soft pearl cyan (180, 240, 255)
    # BGR order:
    blue_b = np.clip(160.0 + gray * 95.0 + high_freq * 120.0, 0, 255)
    blue_g = np.clip(50.0 + gray * 175.0 + high_freq * 100.0, 0, 255)
    blue_r = np.clip(5.0 + (gray ** 1.4) * 160.0 + high_freq * 60.0, 0, 255)

    # Apply wet skin specular gleam
    blue_r = np.clip(blue_r * (1.0 - spec) + 245.0 * spec, 0, 255).astype(np.uint8)
    blue_g = np.clip(blue_g * (1.0 - spec) + 252.0 * spec, 0, 255).astype(np.uint8)
    blue_b = np.clip(blue_b * (1.0 - spec) + 255.0 * spec, 0, 255).astype(np.uint8)

    blue_dolphin = cv2.merge([blue_b, blue_g, blue_r, a])
    blue_path = os.path.join(ASSETS_DIR, "dolphin_blue.png")
    cv2.imwrite(blue_path, blue_dolphin)
    print(f"Created: {blue_path}")

    # 2. INDO-PACIFIC ROSY PINK DOLPHIN (Sousa chinensis / Amazon River Boto)
    # Dorsal cape: Rich rose-coral (210, 60, 115)
    # Flanks: Vibrant glowing rose-pink (255, 115, 175)
    # Belly: Pearlescent blush-white (255, 225, 240)
    # BGR order:
    pink_b = np.clip(100.0 + gray * 145.0 + high_freq * 80.0, 0, 255)
    pink_g = np.clip(45.0 + gray * 170.0 + high_freq * 90.0, 0, 255)
    pink_r = np.clip(190.0 + gray * 65.0 + high_freq * 100.0, 0, 255)

    # Apply pearlescent wet skin specular gleam
    pink_r = np.clip(pink_r * (1.0 - spec) + 255.0 * spec, 0, 255).astype(np.uint8)
    pink_g = np.clip(pink_g * (1.0 - spec) + 240.0 * spec, 0, 255).astype(np.uint8)
    pink_b = np.clip(pink_b * (1.0 - spec) + 248.0 * spec, 0, 255).astype(np.uint8)

    pink_dolphin = cv2.merge([pink_b, pink_g, pink_r, a])
    pink_path = os.path.join(ASSETS_DIR, "dolphin_pink.png")
    cv2.imwrite(pink_path, pink_dolphin)
    print(f"Created: {pink_path}")

if __name__ == "__main__":
    create_color_graded_dolphins()
