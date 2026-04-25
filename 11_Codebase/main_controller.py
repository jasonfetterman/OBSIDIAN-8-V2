# main_controller.py — REV G (Mission Coordinator Integrated)

import time
import threading
import serial

from motion_planner import run_motion_loop, set_pose
from motion_scheduler import run_scheduler, reset_gait

from system_logger import log_system, log_fault, log_motion, log_thermal, log_temp
from swarm_comms import SwarmController
from mission_coordinator import MissionCoordinator

SERIAL_PORT = "COM3"
BAUD_RATE = 115200

HEARTBEAT_INTERVAL = 0.02
BASE_POSE = [90.0] * 16

running = True
thermal_state = "NORMAL"

ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.01)

# ---------------- SWARM ----------------

swarm = SwarmController()

# SITL default connection
swarm.add_drone("drone1", "udp:127.0.0.1:14550")

# ---------------- MISSION ----------------

mission = MissionCoordinator(swarm, set_pose)

# Test coordinate (ArduPilot default area)
MISSION_LAT = -35.363261
MISSION_LON = 149.165230

# ---------------- SERIAL ----------------

def send_servo_command(servo_id, angle, speed):
    ser.write(f"{servo_id},{angle:.2f},{speed}\n".encode())

# ---------------- SERIAL HANDLER ----------------

def handle_serial_message(msg):
    global thermal_state

    if msg.startswith("TEMP:"):
        try:
            s, b, c = map(float, msg.replace("TEMP:", "").split(","))
            log_temp(s, b, c)
        except:
            pass

    elif "THERMAL_WARNING" in msg:
        thermal_state = "WARNING"
        log_thermal("WARNING")

    elif "THERMAL_SHUTDOWN_LATCHED" in msg:
        thermal_state = "LATCHED"
        log_thermal("SHUTDOWN_LATCHED")
        emergency_stop(latched=True)

    elif "THERMAL_MANUAL_RESET" in msg:
        thermal_state = "NORMAL"
        log_thermal("MANUAL_RESET")

# ---------------- THREADS ----------------

def serial_listener():
    while running:
        try:
            line = ser.readline().decode(errors="ignore").strip()
            if line:
                handle_serial_message(line)
        except:
            pass

def heartbeat_loop():
    while running:
        ser.write(b"HB\n")
        time.sleep(HEARTBEAT_INTERVAL)

def motion_send_callback(servo_id, angle):
    if thermal_state == "LATCHED":
        return

    speed = 80 if thermal_state == "NORMAL" else 40
    send_servo_command(servo_id, angle, speed)
    log_motion(servo_id, angle, speed)

# ---------------- SAFETY ----------------

def emergency_stop(latched=False):
    global running

    log_fault("Emergency stop triggered")

    set_pose(BASE_POSE)
    reset_gait()

    # Stop mission + land drones
    try:
        mission.stop()
    except:
        pass

    if latched:
        running = False
        log_fault("Latched shutdown — restart required")

# ---------------- THREAD START ----------------

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
        args=(lambda: BASE_POSE.copy(), set_pose),
        daemon=True
    ).start()

# ---------------- MAIN ----------------

def main():
    global running

    print("=== OBSIDIAN-8 MISSION START ===")
    log_system("Mission system start")

    start_threads()

    # ---- RUN MISSION (TEST) ----
    time.sleep(3)

    print("[MAIN] Starting scout mission")
    mission.scout_and_hold(MISSION_LAT, MISSION_LON)

    try:
        while running:
            time.sleep(1)

    except KeyboardInterrupt:
        emergency_stop()

    finally:
        ser.close()
        log_system("System stopped")
        print("=== STOPPED ===")

# ---------------- ENTRY ----------------

if __name__ == "__main__":
    main()
