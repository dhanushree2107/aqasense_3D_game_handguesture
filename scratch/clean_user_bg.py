import cv2
import numpy as np

img = cv2.imread(r'C:\Users\VINU\.gemini\antigravity-ide\brain\1e5f1edf-a9e3-4689-8e98-1f3d6d44d199\.user_uploaded\media_1792305493977.png')
h, w = img.shape[:2]

# Bounding boxes for the 7 UI stickers
# Format: (center_x, center_y, radius)
stickers = [
    (202, 154, 11),  # icon 1: top left target
    (368, 247, 18),  # icon 2: cyan radar circle
    (401, 271, 15),  # icon 3: yellow chest badge
    (513, 214, 25),  # icon 4: cyan target in archway
    (541, 258, 14),  # icon 5: yellow urn badge
    (674, 224, 16),  # icon 6: yellow diamond above crystal
    (871, 338, 16),  # icon 7: bottom right yellow target
]

mask = np.zeros((h, w), dtype=np.uint8)

for cx, cy, r in stickers:
    cv2.circle(mask, (cx, cy), r + 2, 255, -1)

# Inpaint using Telea & Navier-Stokes blend
cleaned = cv2.inpaint(img, mask, inpaintRadius=4, flags=cv2.INPAINT_TELEA)

cv2.imwrite('scratch/cleaned_temple_panorama.png', cleaned)
print('Inpainted all 7 stickers and saved scratch/cleaned_temple_panorama.png')
