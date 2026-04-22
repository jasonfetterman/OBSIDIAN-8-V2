# motion_scheduler.py — REV B (Stable Gait Scheduling for High-Torque System)

import time

# ---------------- CONFIG ----------------

UPDATE_HZ = 50
DT = 1.0 / UPDATE_HZ

# Leg grouping (Quadruped)
# Index mapping (example):
# 0,1 = Front Left (hip, knee)
# 2,3 = Front Right
# 4,5 = Rear Left
# 6,7 = Rear Right

TRIPOD_GROUP_A = [0, 1, 6, 7]  # Front Left + Rear Right
TRIPOD_GROUP_B = [2, 3, 4, 5]  # Front Right + Rear Left

STEP_DURATION = 0.5  # seconds per phase

# Lift parameters
LIFT_ANGLE_OFFSET = -20  # degrees (knee bend for lift)
FORWARD_OFFSET = 15      # hip movement

# ---------------- STATE ----------------

phase = 0
phase_time = 0.0

# ---------------- INTERFACE ----------------

def apply_offsets(base_pose, indices, hip_offset=0, knee_offset=0):
    pose = base_pose.copy()
    for i in indices:
        if i % 2 == 0:
            pose[i] += hip_offset
        else:
            pose[i] += knee_offset
    return pose

# ---------------- GAIT ENGINE ----------------

def generate_tripod_pose(base_pose):
    global phase

    if phase == 0:
        # Group A moves, Group B supports
        pose = apply_offsets(base_pose, TRIPOD_GROUP_A,
                             hip_offset=FORWARD_OFFSET,
                             knee_offset=LIFT_ANGLE_OFFSET)
    else:
        # Group B moves, Group A supports
        pose = apply_offsets(base_pose, TRIPOD_GROUP_B,
                             hip_offset=FORWARD_OFFSET,
                             knee_offset=LIFT_ANGLE_OFFSET)

    return pose

# ---------------- SCHEDULER LOOP ----------------

def run_scheduler(get_base_pose, send_pose_callback):
    global phase, phase_time

    while True:
        start = time.time()

        base_pose = get_base_pose()

        # Generate gait pose
        pose = generate_tripod_pose(base_pose)

        # Send to motion planner
        send_pose_callback(pose)

        # Phase timing
        phase_time += DT
        if phase_time >= STEP_DURATION:
            phase = 1 - phase
            phase_time = 0.0

        elapsed = time.time() - start
        time.sleep(max(0, DT - elapsed))

# ---------------- SAFETY ----------------

def reset_gait():
    global phase, phase_time
    phase = 0
    phase_time = 0.0

# ---------------- EXAMPLE ----------------

if __name__ == "__main__":
    def mock_base_pose():
        return [90.0] * 8

    def debug_send(pose):
        print(["{:.1f}".format(p) for p in pose])

    run_scheduler(mock_base_pose, debug_send)
