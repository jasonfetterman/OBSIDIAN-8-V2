# path_planner.py
# OBSIDIAN-8 V3 — REV D
# Generates collision-free paths for multi-legged locomotion

import numpy as np

class PathPlanner:
    def __init__(self):
        # Workspace parameters
        self.max_step = 0.1   # meters per step
        self.safe_distance = 0.15  # minimum distance from obstacles
        self.num_legs = 8

        # Initialize leg positions relative to body
        self.default_leg_positions = np.array([
            [0.25, 0.15], [0.25, -0.15],
            [0.0, 0.2], [0.0, -0.2],
            [-0.25, 0.15], [-0.25, -0.15],
            [-0.5, 0.1], [-0.5, -0.1]
        ])  # x, y offsets in meters

    def plan(self, tracked_objects):
        """
        tracked_objects: dict {object_id: (cX, cY)}
        Returns: adjusted leg positions as numpy array (num_legs x 2)
        """
        leg_positions = self.default_leg_positions.copy()

        # Simple avoidance: shift legs away from nearest obstacles
        for obj_id, centroid in tracked_objects.items():
            obj_x, obj_y = centroid
            for i in range(self.num_legs):
                dx = leg_positions[i][0] - obj_x
                dy = leg_positions[i][1] - obj_y
                distance = np.hypot(dx, dy)
                if distance < self.safe_distance:
                    # push leg away
                    shift = (self.safe_distance - distance) * 0.5
                    leg_positions[i][0] += (dx / distance) * shift
                    leg_positions[i][1] += (dy / distance) * shift

        # Clamp step size
        deltas = leg_positions - self.default_leg_positions
        deltas = np.clip(deltas, -self.max_step, self.max_step)
        leg_positions = self.default_leg_positions + deltas

        return leg_positions
