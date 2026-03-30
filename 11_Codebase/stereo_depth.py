"""
stereo_depth.py
OBSIDIAN-8 V3 — REV D
Provides real-time depth maps from stereo cameras (OAK-D Pro / RealSense D455)
"""

import cv2
import numpy as np
from open3d import geometry, visualization
import depthai as dai
import pyrealsense2 as rs

class StereoDepth:
    def __init__(self):
        # Initialize OAK-D pipeline
        self.pipeline = dai.Pipeline()
        self.stereo = self.pipeline.createStereoDepth()
        self.stereo.setConfidenceThreshold(200)
        self.stereo.setMedianFilter(dai.StereoDepthProperties.MedianFilter.KERNEL_7x7)

        self.cam_left = self.pipeline.createMonoCamera()
        self.cam_right = self.pipeline.createMonoCamera()
        self.cam_left.setBoardSocket(dai.CameraBoardSocket.LEFT)
        self.cam_right.setBoardSocket(dai.CameraBoardSocket.RIGHT)
        self.cam_left.setResolution(dai.MonoCameraProperties.SensorResolution.THE_720_P)
        self.cam_right.setResolution(dai.MonoCameraProperties.SensorResolution.THE_720_P)

        self.stereo.initialConfig.setMedianFilter(dai.StereoDepthProperties.MedianFilter.KERNEL_7x7)

        self.cam_left.out.link(self.stereo.left)
        self.cam_right.out.link(self.stereo.right)

        self.depth_queue = None
        self.device = dai.Device(self.pipeline)
        self.depth_queue = self.device.getOutputQueue(name="depth", maxSize=4, blocking=False)

        # RealSense D455 setup
        self.rs_pipeline = rs.pipeline()
        config = rs.config()
        config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        self.rs_pipeline.start(config)

    def get_oakd_depth(self):
        frame = self.depth_queue.get()  # type: dai.ImgFrame
        depth_frame = frame.getFrame()  # numpy array
        depth_frame = depth_frame.astype(np.float32) / 1000.0  # convert mm to meters
        return depth_frame

    def get_realsense_depth(self):
        frames = self.rs_pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        if not depth_frame:
            return None
        depth_image = np.asanyarray(depth_frame.get_data()) / 1000.0
        return depth_image

    def shutdown(self):
        self.rs_pipeline.stop()
        self.device.close()


# -------------------- TEST LOOP --------------------
if __name__ == "__main__":
    stereo = StereoDepth()
    try:
        while True:
            oak_depth = stereo.get_oakd_depth()
            rs_depth = stereo.get_realsense_depth()

            if oak_depth is not None:
                cv2.imshow("OAK-D Depth", oak_depth / np.max(oak_depth))
            if rs_depth is not None:
                cv2.imshow("RealSense Depth", rs_depth / np.max(rs_depth))

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        stereo.shutdown()
        cv2.destroyAllWindows()
