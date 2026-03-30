# motion_planner.py
# OBSIDIAN-8 V3 — REV D
# Converts perception and sensor data into leg gait commands

import numpy as np
from path_planner import PathPlanner

class MotionPlanner:
    def __init__(self):
        # Initialize path planner
        self.path_planner = PathPlanner()
        # Gait parameters
        self.step_height = 0.05  # meters
        self.step_length = 0.1   # meters
        self.swing_time = 0.3    # seconds per leg
        self.num_legs = 8
        self.current_leg_phase = np.zeros(self.num_legs)

    def compute_gait(self, tracked_objects, foot_state):
        """
        tracked_objects: dict {object_id: centroid}
        foot_state: list of bools indicating which foot is in contact
        Returns: dict of leg target positions / velocities
        """
        # Placeholder: simple forward motion with obstacle avoidance
        path_adjustment = self.path_planner.plan(tracked_objects)

        leg_commands = {}
        for leg in range(self.num_legs):
            # Determine swing or stance
            if foot_state[leg]:
                # stance phase: apply ground contact adjustments
                leg_commands[leg] = {
                    "phase": "stance",
                    "x": path_adjustment[leg][0],
                    "y": path_adjustment[leg][1],
                    "z": 0.0
                }
            else:
                # swing phase: lift leg
                leg_commands[leg] = {
                    "phase": "swing",
                    "x": path_adjustment[leg][0],
                    "y": path_adjustment[leg][1],
                    "z": self.step_height
                }
            # Increment leg phase for timing
            self.current_leg_phase[leg] += 0.02  # assumes 50 Hz update

        return leg_commands
