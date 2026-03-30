# path_planner.py
# OBSIDIAN-8 V3 — REV D
# Generates collision-free paths using tracked objects and persistent maps

import numpy as np
from map_manager import MapManager

class PathPlanner:
    def __init__(self, map_manager=None):
        """
        map_manager: instance of MapManager for occupancy grid
        """
        self.map_manager = map_manager
        self.num_legs = 8
        self.max_step = 0.1   # meters per step

        # Default leg positions relative to body
        self.default_leg_positions = np.array([
            [0.25, 0.15], [0.25, -0.15],
            [0.0, 0.2], [0.0, -0.2],
            [-0.25, 0.15], [-0.25, -0.15],
            [-0.5, 0.1], [-0.5, -0.1]
        ])

    def plan(self, tracked_objects):
        """
        tracked_objects: dict {object_id: (x, y)}
        Returns: adjusted leg positions (num_legs x 2)
        """
        leg_positions = self.default_leg_positions.copy()

        # Shift legs away from tracked objects (real-time obstacles)
        for obj_id, centroid in tracked_objects.items():
            obj_x, obj_y = centroid
            for i in range(self.num_legs):
                dx = leg_positions[i][0] - obj_x
                dy = leg_positions[i][1] - obj_y
                distance = np.hypot(dx, dy)
                safe_distance = 0.15  # meters
                if distance < safe_distance:
                    shift = (safe_distance - distance) * 0.5
                    leg_positions[i][0] += (dx / distance) * shift
                    leg_positions[i][1] += (dy / distance) * shift

        # Use map_manager to avoid remembered obstacles
        if self.map_manager:
            for i in range(self.num_legs):
                x, y = leg_positions[i]
                cell_value = self.map_manager.query_cell(x, y)
                if cell_value == 1:  # occupied
                    # Push leg away from occupied cell
                    leg_positions[i][0] += np.sign(x) * self.max_step
                    leg_positions[i][1] += np.sign(y) * self.max_step

        # Clamp step size
        deltas = leg_positions - self.default_leg_positions
        deltas = np.clip(deltas, -self.max_step, self.max_step)
        leg_positions = self.default_leg_positions + deltas

        return leg_positions
