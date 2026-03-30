"""
object_detection.py
OBSIDIAN-8 V3 — REV D
Performs real-time object detection on preprocessed frames
"""

import cv2
import torch
import numpy as np

class ObjectDetector:
    def __init__(self, model_path="yolov8n.pt", device="cuda"):
        """
        model_path: path to YOLOv8 model
        device: "cuda" for GPU or "cpu"
        """
        self.device = device
        self.model = torch.hub.load("ultralytics/yolov8", "custom", path=model_path, force_reload=True)
        self.model.to(self.device)
        self.model.eval()

    def detect(self, frame):
        """
        frame: np.array (preprocessed, RGB, 0-1 normalized)
        Returns: list of detections with [x1, y1, x2, y2, confidence, class_id]
        """
        # YOLO expects HWC 0-255
        input_frame = (frame * 255).astype(np.uint8)

        # Convert to torch tensor, add batch dimension, HWC -> CHW
        img_tensor = torch.from_numpy(input_frame).permute(2, 0, 1).unsqueeze(0).float().to(self.device)

        with torch.no_grad():
            results = self.model(img_tensor)[0]

        detections = []
        for det in results.cpu().numpy():
            x1, y1, x2, y2, conf, cls = det
            detections.append([x1, y1, x2, y2, conf, int(cls)])

        return detections

# -------------------- TEST LOOP --------------------
if __name__ == "__main__":
    from image_preprocessing import ImagePreprocessor

    cap = cv2.VideoCapture(0)
    preprocessor = ImagePreprocessor(target_size=(640, 480))
    detector = ObjectDetector(model_path="yolov8n.pt", device="cuda")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        processed = preprocessor.preprocess(frame)
        detections = detector.detect(processed)

        # Draw bounding boxes
        display_frame = (processed * 255).astype(np.uint8)
        display_frame = cv2.cvtColor(display_frame, cv2.COLOR_RGB2BGR)
        for det in detections:
            x1, y1, x2, y2, conf, cls = det
            cv2.rectangle(display_frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
            cv2.putText(display_frame, f"{cls}:{conf:.2f}", (int(x1), int(y1)-5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        cv2.imshow("Object Detection", display_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
