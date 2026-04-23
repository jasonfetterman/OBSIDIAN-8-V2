# system_logger.py — REV A (Structured Runtime Logger)

import os
import time
from datetime import datetime

LOG_DIR = "logs"

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_FILE = os.path.join(LOG_DIR, f"obsidian8_log_{timestamp}.csv")

# Create file with headers
with open(LOG_FILE, "w") as f:
    f.write("time,event_type,details\n")

def log_event(event_type, details):
    now = datetime.now().strftime("%H:%M:%S.%f")
    line = f"{now},{event_type},{details}\n"

    with open(LOG_FILE, "a") as f:
        f.write(line)

# Convenience wrappers

def log_thermal(state, temps=None):
    detail = state
    if temps:
        detail += f" | {temps}"
    log_event("THERMAL", detail)

def log_motion(servo_id, angle, speed):
    log_event("MOTION", f"id={servo_id} angle={angle:.2f} speed={speed}")

def log_system(msg):
    log_event("SYSTEM", msg)

def log_fault(msg):
    log_event("FAULT", msg)
