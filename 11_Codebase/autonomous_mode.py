"""
autonomous_mode.py
OBSIDIAN-8 V3 — REV D
Coordinates sensors, vision, path planning, and motion execution for autonomous operation
"""

import time
import threading
from sensor_fusion import SensorFusion
from vision_interface import VisionInterface
from object_detection import ObjectDetection
from object_tracking import ObjectTracker
from stereo_depth import StereoDepth
from motion_planner import MotionPlanner
from path_planner import PathPlanner

class AutonomousMode:
    def __init__(self, camera_sources=[0,1]):
        # Initialize modules
        self.vision = VisionInterface(camera_sources=camera_sources)
        self.detector = ObjectDetection(model_path="yolov8n.pt", device="cuda")
        self.tracker = ObjectTracker(max_distance=50.0)
        self.stereo = StereoDepth()
        self.sensors = SensorFusion()
        self.motion_planner = MotionPlanner()
        self.path_planner = PathPlanner()

        self.running = False
        self.state_lock = threading.Lock()
        self.robot_state = {}

    def start(self):
        """Start autonomous loop in a separate thread"""
        self.running = True
        self.vision.start()
        self.thread = threading.Thread(target=self.autonomous_loop)
        self.thread.start()

    def stop(self):
        """Stop autonomous loop"""
        self.running = False
        self.thread.join()
        self.vision.stop()

    def autonomous_loop(self):
        """Main autonomous control loop"""
        while self.running:
            # 1. Get camera frames
            frames = self.vision.get_all_frames()

            # 2. Object detection and tracking
            all_detections = []
            for frame in frames:
                if frame is not None:
                    detections = self.detector.detect(frame)
                    all_detections.extend(detections)
            tracked_objects = self.tracker.update(all_detections)

            # 3. Sensor fusion
            fused_state = self.sensors.update(frames[0] if frames else None, tracked_objects)

            # 4. Depth map
            depth_map = self.stereo.get_oakd_depth() or self.stereo.get_realsense_depth()

            # 5. Path planning
            planned_path = self.path_planner.plan(fused_state, depth_map)

            # 6. Motion planning
            joint_commands = self.motion_planner.compute_trajectory(fused_state, planned_path)

            # 7. Send commands to servos (via servo_driver / motion executor)
            self.motion_planner.execute_trajectory(joint_commands)

            # 8. Update robot state
            with self.state_lock:
                self.robot_state = fused_state

            # Loop rate ~30 Hz
            time.sleep(0.033)

    def get_robot_state(self):
        with self.state_lock:
            return self.robot_state

# -------------------- TEST LOOP --------------------
if __name__ == "__main__":
    auto = AutonomousMode(camera_sources=[0,1])
    auto.start()
    print("[AutonomousMode] Started autonomous loop")

    try:
        while True:
            state = auto.get_robot_state()
            if state:
                print(f"Orientation: {state['orientation']}, Foot Contact: {state['foot_contact']}")
            time.sleep(0.5)
    except KeyboardInterrupt:
        auto.stop()
        print("[AutonomousMode] Stopped")
