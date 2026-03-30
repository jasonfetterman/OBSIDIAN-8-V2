"""
image_preprocessing.py
OBSIDIAN-8 V3 — REV D
Prepares camera frames for object detection / tracking
"""

import cv2
import numpy as np

class ImagePreprocessor:
    def __init__(self, target_size=(640, 480)):
        self.target_size = target_size

    def preprocess(self, frame):
        """
        frame: np.array (BGR image)
        Returns: processed frame ready for object detection
        """
        # Resize to model input size
        frame_resized = cv2.resize(frame, self.target_size)

        # Convert to RGB
        frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)

        # Histogram equalization for lighting normalization
        ycrcb = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2YCrCb)
        ycrcb[:,:,0] = cv2.equalizeHist(ycrcb[:,:,0])
        frame_eq = cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2RGB)

        # Apply Gaussian blur to reduce noise
        frame_blur = cv2.GaussianBlur(frame_eq, (3, 3), 0)

        # Normalize pixel values to 0-1
        frame_norm = frame_blur.astype(np.float32) / 255.0

        return frame_norm

# -------------------- TEST LOOP --------------------
if __name__ == "__main__":
    cap = cv2.VideoCapture(0)  # Camera index 0
    preprocessor = ImagePreprocessor(target_size=(640, 480))

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        processed = preprocessor.preprocess(frame)
        # Convert back to 0-255 for display
        display_frame = (processed * 255).astype(np.uint8)
        cv2.imshow("Processed Frame", cv2.cvtColor(display_frame, cv2.COLOR_RGB2BGR))

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
