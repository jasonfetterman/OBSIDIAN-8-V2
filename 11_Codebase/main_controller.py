# main_controller.py — REV C (Thermal Latch-Aware Integration)

import time
import threading
import serial

from motion_planner import run_motion_loop, set_pose
from motion_scheduler import run_scheduler, reset_gait

# ---------------- CONFIG ----------------

SERIAL_PORT = "COM3"   # UPDATE if needed
BAUD_RATE = 115200

HEARTBEAT_INTERVAL = 0.02  # 50 Hz

BASE_POSE = [90.0] * 16

# ---------------- STATE ----------------

running = True
thermal_state = "NORMAL"   # NORMAL / WARNING / LATCHED

ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.01)

# ---------------- SERIAL ----------------

def send_servo_command(servo_id, angle, speed):
    cmd = f"{servo_id},{angle:.2f},{speed}\n"
    ser.write(cmd.encode())

def send_pose(pose, speed):
    for i, angle in enumerate(pose):
        send_servo_command(i, angle, speed)

# ---------------- THERMAL HANDLING ----------------

def handle_thermal_message(msg):
    global thermal_state

    if "THERMAL_WARNING" in msg:
        if thermal_state != "WARNING":
            print("[THERMAL] WARNING — throttling")
        thermal_state = "WARNING"

    elif "THERMAL_SHUTDOWN_LATCHED" in msg:
        print("[THERMAL] CRITICAL — LATCHED SHUTDOWN")
        thermal_state = "LATCHED"
        emergency_stop(latched=True)

    elif "THERMAL_MANUAL_RESET" in msg:
        print("[THERMAL] MANUAL RESET — awaiting operator restart")
        thermal_state = "NORMAL"

# ---------------- SERIAL LISTENER ----------------

def serial_listener():
    global running
    while running:
        try:
            line = ser.readline().decode(errors="ignore").strip()
            if line:
                handle_thermal_message(line)
        except:
            pass

# ---------------- HEARTBEAT ----------------

def heartbeat_loop():
    while running:
        try:
            ser.write(b"HB\n")
        except:
            pass
        time.sleep(HEARTBEAT_INTERVAL)

# ---------------- MOTION CALLBACK ----------------

def motion_send_callback(servo_id, angle):
    # Block all motion if latched
    if thermal_state == "LATCHED":
        return

    speed = 80
    if thermal_state == "WARNING":
        speed = 40

    send_servo_command(servo_id, angle, speed)

# ---------------- BASE POSE ----------------

def get_base_pose():
    return BASE_POSE.copy()

# ---------------- SAFETY ----------------

def emergency_stop(latched=False):
    global running

    print("[SYSTEM] Emergency stop")

    # Freeze motion immediately
    set_pose(BASE_POSE)
    reset_gait()

    # If latched, we halt everything until manual restart (new process run)
    if latched:
        print("[SYSTEM] Latched state — restart required")
        running = False

# ---------------- THREAD CONTROL ----------------

def start_threads():
    threading.Thread(target=serial_listener, daemon=True).start()
    threading.Thread(target=heartbeat_loop, daemon=True).start()
    threading.Thread(
        target=run_motion_loop,
        args=(motion_send_callback,),
        daemon=True
    ).start()
    threading.Thread(
        target=run_scheduler,
        args=(get_base_pose, set_pose),
        daemon=True
    ).start()

# ---------------- MAIN ----------------

def main():
    global running

    print("=== OBSIDIAN-8 CONTROL START ===")

    start_threads()

    try:
        while running:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n[USER] Shutdown requested")
        emergency_stop()

    finally:
        ser.close()
        print("=== SYSTEM STOPPED ===")

# ---------------- ENTRY ----------------

if __name__ == "__main__":
    main()
