"""
sensor_fusion.py
OBSIDIAN-8 V3 — REV D
Fuses IMU, foot sensors, stereo depth, and object tracking for a unified robot state
"""

import numpy as np
from imu_reader import IMUReader
from foot_sensor import FootSensor
from stereo_depth import StereoDepth
from object_tracking import ObjectTracker

class SensorFusion:
    def __init__(self):
        self.imu = IMUReader()
        self.foot_sensors = FootSensor()
        self.stereo = StereoDepth()
        self.tracker = ObjectTracker()

        self.robot_state = {
            "position": np.zeros(3),  # x, y, z
            "orientation": np.array([1,0,0,0]),  # quaternion
            "foot_contact": [False]*8,
            "tracked_objects": [],
            "depth_map": None
        }

    def update(self, frame, detections=None):
        """
        frame: current RGB frame from camera
        detections: optional pre-detected objects
        """
        # Update IMU
        self.imu.update()
        self.robot_state["orientation"] = self.imu.getQuaternion()
        self.robot_state["acceleration"] = self.imu.getAccel()
        self.robot_state["gyro"] = self.imu.getGyro()

        # Update foot sensors
        self.robot_state["foot_contact"] = self.foot_sensors.read()

        # Update depth
        depth_oak = self.stereo.get_oakd_depth()
        depth_rs = self.stereo.get_realsense_depth()
        self.robot_state["depth_map"] = depth_oak if depth_oak is not None else depth_rs

        # Update object tracking
        if detections is not None:
            tracked = self.tracker.update(detections)
            self.robot_state["tracked_objects"] = [
                {"id": obj.id, "bbox": obj.bbox, "history": list(obj.history)} for obj in tracked
            ]

        return self.robot_state

# -------------------- TEST LOOP --------------------
if __name__ == "__main__":
    from image_preprocessing import ImagePreprocessor
    from object_detection import ObjectDetector
    import cv2

    cap = cv2.VideoCapture(0)
    preprocessor = ImagePreprocessor()
    detector = ObjectDetector(model_path="yolov8n.pt", device="cuda")
    fusion = SensorFusion()

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            processed = preprocessor.preprocess(frame)
            detections = detector.detect(processed)
            state = fusion.update(frame, detections)

            # Print robot orientation and foot contact for debugging
            print(f"Orientation: {state['orientation']}, Foot Contact: {state['foot_contact']}")
            print(f"Tracked Objects: {[obj['id'] for obj in state['tracked_objects']]}")

    except KeyboardInterrupt:
        cap.release()
        cv2.destroyAllWindows()
        print("[SensorFusion] Stopped")
