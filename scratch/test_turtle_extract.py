import cv2
import numpy as np

img = cv2.imread('assets/sea_turtle.jpg')
h, w = img.shape[:2]

# Bounding box of turtle in image roughly (exclude background borders)
# Let's inspect where the turtle is located
mask = np.zeros((h, w), np.uint8)
bgdModel = np.zeros((1, 65), np.float64)
fgdModel = np.zeros((1, 65), np.float64)

# Margin around turtle
rect = (int(w * 0.05), int(h * 0.10), int(w * 0.88), int(h * 0.80))
cv2.grabCut(img, mask, rect, bgdModel, fgdModel, 6, cv2.GC_INIT_WITH_RECT)

mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')

# Check area
print("Segmented pixels:", mask2.sum())

# Smooth edges with GaussianBlur
alpha = (cv2.GaussianBlur(mask2.astype(np.float32) * 255, (7, 7), 2)).clip(0, 255).astype(np.uint8)

# Remove any dark background bleed around edges by color-keying dark ocean pixels outside foreground
b, g, r = cv2.split(img)
rgba = cv2.merge([b, g, r, alpha])
cv2.imwrite('scratch/test_extracted_turtle.png', rgba)
print("Saved scratch/test_extracted_turtle.png")
