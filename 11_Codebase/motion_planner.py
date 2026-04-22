# motion_planner.py — REV C (16-Channel Octopod Motion Control)

import time

# ---------------- CONFIG ----------------

SERVO_COUNT = 16  # 8 legs × 2 DOF

# Physical limits (realistic for most high-torque servos)
ANGLE_MIN = 10.0
ANGLE_MAX = 170.0

# Motion constraints (tuned for 150KG servos)
MAX_SPEED = 80.0            # degrees per second
MAX_ACCEL = 160.0           # degrees per second^2

UPDATE_HZ = 50
DT = 1.0 / UPDATE_HZ

# ---------------- STATE ----------------

class ServoState:
    def __init__(self):
        self.current = 90.0
        self.target = 90.0
        self.velocity = 0.0

servos = [ServoState() for _ in range(SERVO_COUNT)]

# ---------------- CORE ----------------

def clamp(value, min_val, max_val):
    return max(min_val, min(max_val, value))

def set_target(servo_id, angle):
    if 0 <= servo_id < SERVO_COUNT:
        servos[servo_id].target = clamp(angle, ANGLE_MIN, ANGLE_MAX)

def set_pose(pose):
    for i in range(min(len(pose), SERVO_COUNT)):
        set_target(i, pose[i])

# ---------------- MOTION ENGINE ----------------

def update_servo(servo: ServoState):
    error = servo.target - servo.current

    # Proportional velocity target
    desired_velocity = clamp(error * 2.5, -MAX_SPEED, MAX_SPEED)

    # Acceleration limiting
    accel = desired_velocity - servo.velocity
    accel = clamp(accel, -MAX_ACCEL * DT, MAX_ACCEL * DT)

    servo.velocity += accel

    # Apply velocity
    servo.current += servo.velocity * DT

    # Snap if close
    if abs(error) < 0.3:
        servo.current = servo.target
        servo.velocity = 0.0

# ---------------- LOOP ----------------

def run_motion_loop(send_callback):
    """
    send_callback(servo_id, angle)
    """
    while True:
        start = time.time()

        for i in range(SERVO_COUNT):
            update_servo(servos[i])
            send_callback(i, servos[i].current)

        elapsed = time.time() - start
        time.sleep(max(0, DT - elapsed))

# ---------------- SAFETY ----------------

def emergency_stop():
    for s in servos:
        s.target = s.current
        s.velocity = 0.0

# ---------------- TEST ----------------

if __name__ == "__main__":
    def debug_send(i, angle):
        print(f"{i}:{angle:.1f}", end=" ")
    
    set_pose([110.0] * SERVO_COUNT)
    run_motion_loop(debug_send)
