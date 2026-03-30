"""
stereo_depth.py
OBSIDIAN-8 V3 — REV D
Generates depth maps from OAK-D and RealSense cameras
"""

import numpy as np
import cv2

# For OAK-D
try:
    import depthai as dai
    OAKD_AVAILABLE = True
except ImportError:
    print("[StereoDepth] depthai not installed, OAK-D disabled")
    OAKD_AVAILABLE = False

# For RealSense
try:
    import pyrealsense2 as rs
    REALSENSE_AVAILABLE = True
except ImportError:
    print("[StereoDepth] pyrealsense2 not installed, RealSense disabled")
    REALSENSE_AVAILABLE = False

class StereoDepth:
    def __init__(self):
        self.oakd_pipeline = None
        self.oakd_depth = None
        self.rs_pipeline = None
        self.rs_depth = None

        if OAKD_AVAILABLE:
            self.init_oakd()
        if REALSENSE_AVAILABLE:
            self.init_realsense()

    # ---------------- OAK-D ----------------
    def init_oakd(self):
        self.oakd_pipeline = dai.Pipeline()
        cam_left = self.oakd_pipeline.createMonoCamera()
        cam_right = self.oakd_pipeline.createMonoCamera()
        stereo = self.oakd_pipeline.createStereoDepth()
        cam_left.setBoardSocket(dai.CameraBoardSocket.LEFT)
        cam_right.setBoardSocket(dai.CameraBoardSocket.RIGHT)
        stereo.setOutputDepth(True)
        cam_left.out.link(stereo.left)
        cam_right.out.link(stereo.right)
        self.oakd_device = dai.Device(self.oakd_pipeline)
        self.oakd_q = self.oakd_device.getOutputQueue(name="depth", maxSize=4, blocking=False)
        print("[StereoDepth] OAK-D initialized")

    def get_oakd_depth(self):
        if not OAKD_AVAILABLE:
            return None
        frame = self.oakd_q.get().getFrame()
        self.oakd_depth = frame
        return frame

    # ---------------- RealSense ----------------
    def init_realsense(self):
        self.rs_pipeline = rs.pipeline()
        config = rs.config()
        config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        self.rs_pipeline.start(config)
        print("[StereoDepth] RealSense initialized")

    def get_realsense_depth(self):
        if not REALSENSE_AVAILABLE:
            return None
        frames = self.rs_pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        if not depth_frame:
            return None
        self.rs_depth = np.asanyarray(depth_frame.get_data())
        return self.rs_depth

# -------------------- TEST LOOP --------------------
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    depth_module = StereoDepth()

    try:
        while True:
            oak_depth = depth_module.get_oakd_depth()
            rs_depth = depth_module.get_realsense_depth()

            if oak_depth is not None:
                cv2.imshow("OAK-D Depth", cv2.normalize(oak_depth, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8))
            if rs_depth is not None:
                cv2.imshow("RealSense Depth", cv2.normalize(rs_depth, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8))

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        pass
    finally:
        cv2.destroyAllWindows()
        if REALSENSE_AVAILABLE:
            depth_module.rs_pipeline.stop()
        print("[StereoDepth] Stopped")
