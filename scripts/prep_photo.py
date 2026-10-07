import sys
import os
import shutil
import cv2
import numpy as np
from PIL import Image

def prep_photo(input_path="source-photo.jpg"):
    print(f"Processing photo: {input_path}")
    if not os.path.exists(input_path):
        print(f"Error: File '{input_path}' not found.")
        return

    # Read image with OpenCV
    img_bgr = cv2.imread(input_path)
    if img_bgr is None:
        print(f"Error: Could not read image at '{input_path}'")
        return

    # 1. Background removal (detect bright yellow / solid background)
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    
    # Yellow background thresholding (Hue ~ 15-40 in OpenCV 0-180 scale)
    lower_yellow = np.array([15, 80, 80])
    upper_yellow = np.array([40, 255, 255])
    yellow_mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
    
    # Try rembg if available, otherwise use color thresholding
    bg_removed = False
    try:
        import importlib.util
        if importlib.util.find_spec("rembg") is not None:
            from rembg import remove
            with open(input_path, 'rb') as f:
                input_bytes = f.read()
            output_bytes = remove(input_bytes)
            nparr = np.frombuffer(output_bytes, np.uint8)
            img_rgba = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)
            if img_rgba is not None and img_rgba.shape[2] == 4:
                # Composite over white
                alpha = img_rgba[:, :, 3] / 255.0
                bg_white = np.ones_like(img_bgr) * 255
                for c in range(3):
                    bg_white[:, :, c] = img_rgba[:, :, c] * alpha + 255 * (1 - alpha)
                img_bgr = bg_white.astype(np.uint8)
                bg_removed = True
    except Exception as e:
        print(f"rembg notice: {e}")

    if not bg_removed:
        # Replace detected yellow background with pure white (255, 255, 255)
        img_bgr[yellow_mask > 0] = [255, 255, 255]

    # Convert to grayscale
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    # 2. Boost local contrast with OpenCV CLAHE
    clahe = cv2.createCLAHE(clipLimit=3.5, tileGridSize=(8, 8))
    prepped = clahe.apply(gray)

    # Ensure pure white background remains pure white (255) so it maps to spaces
    prepped[gray >= 250] = 255

    output_path = "source-prepped.png"
    cv2.imwrite(output_path, prepped)
    print(f"Saved prepped portrait to '{output_path}'")

if __name__ == "__main__":
    photo_file = sys.argv[1] if len(sys.argv) > 1 else "source-photo.jpg"
    prep_photo(photo_file)
