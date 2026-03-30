"""
object_tracking.py
OBSIDIAN-8 V3 — REV D
Tracks detected objects over frames using SORT / simple centroid tracking
"""

import numpy as np
from collections import deque

class TrackedObject:
    def __init__(self, object_id, bbox, max_history=30):
        self.id = object_id
        self.bbox = bbox  # [x1, y1, x2, y2]
        self.history = deque(maxlen=max_history)
        self.history.append(bbox)

    def update(self, bbox):
        self.bbox = bbox
        self.history.append(bbox)

class ObjectTracker:
    def __init__(self, max_distance=50):
        self.next_id = 0
        self.objects = []
        self.max_distance = max_distance  # pixels

    def _iou(self, bbox1, bbox2):
        # Intersection over Union
        xA = max(bbox1[0], bbox2[0])
        yA = max(bbox1[1], bbox2[1])
        xB = min(bbox1[2], bbox2[2])
        yB = min(bbox1[3], bbox2[3])
        interArea = max(0, xB - xA) * max(0, yB - yA)
        boxAArea = (bbox1[2]-bbox1[0])*(bbox1[3]-bbox1[1])
        boxBArea = (bbox2[2]-bbox2[0])*(bbox2[3]-bbox2[1])
        iou = interArea / float(boxAArea + boxBArea - interArea + 1e-5)
        return iou

    def update(self, detections):
        """
        detections: list of [x1, y1, x2, y2, conf, class_id]
        """
        updated_objects = []
        for det in detections:
            x1, y1, x2, y2, conf, cls = det
            matched = False
            for obj in self.objects:
                iou = self._iou(obj.bbox, [x1, y1, x2, y2])
                if iou > 0.3:  # match threshold
                    obj.update([x1, y1, x2, y2])
                    updated_objects.append(obj)
                    matched = True
                    break
            if not matched:
                new_obj = TrackedObject(self.next_id, [x1, y1, x2, y2])
                updated_objects.append(new_obj)
                self.next_id += 1
        self.objects = updated_objects
        return self.objects

# -------------------- TEST LOOP --------------------
if __name__ == "__main__":
    from image_preprocessing import ImagePreprocessor
    from object_detection import ObjectDetector
    import cv2

    cap = cv2.VideoCapture(0)
    preprocessor = ImagePreprocessor()
    detector = ObjectDetector(model_path="yolov8n.pt", device="cuda")
    tracker = ObjectTracker()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        processed = preprocessor.preprocess(frame)
        detections = detector.detect(processed)
        tracked = tracker.update(detections)

        # Draw tracked objects
        display_frame = (processed * 255).astype(np.uint8)
        display_frame = cv2.cvtColor(display_frame, cv2.COLOR_RGB2BGR)
        for obj in tracked:
            x1, y1, x2, y2 = obj.bbox
            cv2.rectangle(display_frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
            cv2.putText(display_frame, f"ID:{obj.id}", (int(x1), int(y1)-5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        cv2.imshow("Tracked Objects", display_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
