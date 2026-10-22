import os
import shutil
import cv2
import numpy as np

def clean_backdrop(filename, fish_boxes):
    path = os.path.join("assets", filename)
    if not os.path.exists(path):
        return
    bak = os.path.join("assets", f"{os.path.splitext(filename)[0]}_baked_fish_backup.jpg")
    if not os.path.exists(bak):
        shutil.copyfile(path, bak)
    
    img = cv2.imread(path)
    mask = np.zeros(img.shape[:2], dtype=np.uint8)
    
    for (x1, y1, x2, y2) in fish_boxes:
        # Create mask around fish
        roi = img[y1:y2, x1:x2]
        # Detect local contrast/color anomalies against background
        gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        med = np.median(gray_roi)
        diff = cv2.absdiff(gray_roi, int(med))
        _, local_mask = cv2.threshold(diff, 18, 255, cv2.THRESH_BINARY)
        # Dilate slightly
        kernel = np.ones((5, 5), np.uint8)
        local_mask = cv2.dilate(local_mask, kernel, iterations=2)
        mask[y1:y2, x1:x2] = cv2.bitwise_or(mask[y1:y2, x1:x2], local_mask)
        
    cleaned = cv2.inpaint(img, mask, inpaintRadius=5, flags=cv2.INPAINT_TELEA)
    cv2.imwrite(path, cleaned, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
    print(f"Cleaned {filename} successfully!")

if __name__ == "__main__":
    # Level 3: shipwreck_ruins_cinematic.jpg
    clean_backdrop("shipwreck_ruins_cinematic.jpg", [
        (20, 280, 340, 540),    # left orange fish
        (560, 360, 840, 520),   # center small fish
        (1020, 530, 1340, 640), # right blue/yellow fish
    ])
    
    # Level 4: shipwreck.jpg
    clean_backdrop("shipwreck.jpg", [
        (140, 140, 360, 260),   # top left blue fish
        (560, 340, 820, 500),   # center small fish
        (1160, 520, 1340, 620), # right small fish
    ])
    
    # Level 5: ruins.jpg
    clean_backdrop("ruins.jpg", [
        (20, 280, 340, 540),    # left orange fish
        (500, 480, 600, 600),   # center school
        (1020, 530, 1340, 640), # right blue/yellow fish
    ])
