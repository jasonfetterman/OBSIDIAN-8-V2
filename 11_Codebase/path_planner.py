# path_planner.py
# OBSIDIAN-8 V3 — REV D
# Generates footstep and body trajectories for autonomous motion

import math
import numpy as np

# -------------------- CONFIG --------------------
STEP_HEIGHT = 0.05        # meters
STEP_LENGTH = 0.10        # meters
BODY_HEIGHT = 0.30        # meters
GAIT_CYCLE_TIME = 1.0     # seconds per gait cycle
NUM_LEGS = 8

# -------------------- GAIT PATTERNS --------------------
# Example tripod gait for octopod
TRIPOD_GROUPS = [
    [0, 3, 4, 7],  # First group of legs
    [1, 2, 5, 6]   # Second group of legs
]

# -------------------- CLASS --------------------
class PathPlanner:
    def __init__(self):
        self.step_phase = 0.0
        self.current_foot_positions = [np.array([0.0, 0.0, -BODY_HEIGHT]) for _ in range(NUM_LEGS)]

    def plan(self, robot_state):
        """
        Generate next foot positions for each leg based on current robot state.
        robot_state: dict with keys 'velocity', 'orientation', 'terrain_map' (optional)
        Returns: list of dicts [{'coxa': x, 'femur': y, 'tibia': z}, ...]
        """
        velocity = robot_state.get('velocity', np.array([0.0, 0.0, 0.0]))
        orientation = robot_state.get('orientation', np.array([0.0, 0.0, 0.0]))

        # Update gait phase
        self.step_phase += 0.05  # Increment phase, adjust for control loop timing
        if self.step_phase > GAIT_CYCLE_TIME:
            self.step_phase -= GAIT_CYCLE_TIME

        foot_positions = []
        for leg_index in range(NUM_LEGS):
            group = 0 if leg_index in TRIPOD_GROUPS[0] else 1
            phase_offset = (group * GAIT_CYCLE_TIME / 2)  # staggered gait
            phase = (self.step_phase + phase_offset) % GAIT_CYCLE_TIME
            foot_pos = self._compute_foot_trajectory(leg_index, phase, velocity)
            foot_positions.append(foot_pos)

        return foot_positions

    def _compute_foot_trajectory(self, leg_index, phase, velocity):
        """
        Compute the X, Y, Z foot position relative to the body for this leg
        """
        # X: forward/backward
        x = velocity[0] * phase
        # Y: lateral offset (static)
        y = 0.1 * (1 if leg_index % 2 == 0 else -1)
        # Z: sinusoidal step for swing phase
        z = -BODY_HEIGHT
        swing_phase = phase / GAIT_CYCLE_TIME
        if swing_phase < 0.5:
            z += STEP_HEIGHT * math.sin(math.pi * swing_phase)
        return {'x': x, 'y': y, 'z': z}
