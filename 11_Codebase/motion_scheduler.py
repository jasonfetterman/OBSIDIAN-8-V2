# motion_scheduler.py
# OBSIDIAN-8 V3 — REV D
# Schedules gait cycles and coordinates leg motion

import time
import numpy as np
from path_planner import PathPlanner
from motion_planner import MotionPlanner

# -------------------- CONFIG --------------------
CONTROL_RATE_HZ = 200  # Low-level update rate
NUM_LEGS = 8

# -------------------- INITIALIZE --------------------
path_planner = PathPlanner()
motion_planner = MotionPlanner()

# Tracks phase of each leg
leg_phases = [0.0 for _ in range(NUM_LEGS)]

# Gait timing configuration
GAIT_CYCLE_TIME = 1.0  # seconds
PHASE_OFFSETS = [0.0, 0.5, 0.0, 0.5, 0.0, 0.5, 0.0, 0.5]  # stagger tripod gait

# -------------------- FUNCTIONS --------------------
def update_leg_phases(delta_time):
    """
    Increment the phase of each leg and wrap around the gait cycle
    """
    global leg_phases
    for i in range(NUM_LEGS):
        leg_phases[i] += delta_time / GAIT_CYCLE_TIME
        if leg_phases[i] > 1.0:
            leg_phases[i] -= 1.0

def schedule_motion(robot_state):
    """
    Compute next joint targets for all legs based on gait timing
    """
    foot_targets = path_planner.plan(robot_state)
    joint_commands = motion_planner.generate(foot_targets, robot_state)
    return joint_commands

# -------------------- MAIN LOOP --------------------
if __name__ == "__main__":
    print("[MotionScheduler] Starting motion scheduling loop...")
    loop_delay = 1.0 / CONTROL_RATE_HZ
    robot_state = {'velocity': np.array([0.0, 0.0, 0.0]), 'orientation': np.array([0.0, 0.0, 0.0])}

    try:
        while True:
            start_time = time.time()

            # Update leg phases
            update_leg_phases(loop_delay)

            # Generate joint commands
            joint_commands = schedule_motion(robot_state)

            # TODO: send joint_commands to servo driver
            # Example: servo_driver.send(joint_commands)

            elapsed = time.time() - start_time
            sleep_time = max(0, loop_delay - elapsed)
            time.sleep(sleep_time)

    except KeyboardInterrupt:
        print("[MotionScheduler] Exiting scheduler loop...")
        motion_planner.halt_motion()
