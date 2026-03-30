# dock_manager.py
# OBSIDIAN-8 V3 — REV D
# Manages autonomous docking, charging, and safe power handoff

import RPi.GPIO as GPIO
import time
import serial

# -------------------- HARDWARE CONFIG --------------------
# GPIO pins
DOCK_DETECT_PIN = 17      # Dock contact sensor
CHARGING_RELAY_PIN = 27   # Relay to enable charging
SERVO_ENABLE_PIN = 22     # Signal to Teensy/Duet to enable/disable servo bank power
LED_STATUS_PIN = 5        # Status LED

# Serial for Teensy/Duet communication
SERIAL_PORT = '/dev/ttyACM0'  # Adjust to your setup
BAUD_RATE = 115200

# Docking parameters
DOCK_APPROACH_DELAY = 2.0  # Seconds to wait after contact detected before enabling charging

# -------------------- SETUP --------------------
GPIO.setmode(GPIO.BCM)
GPIO.setup(DOCK_DETECT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP) # NC contact
GPIO.setup(CHARGING_RELAY_PIN, GPIO.OUT)
GPIO.setup(SERVO_ENABLE_PIN, GPIO.OUT)
GPIO.setup(LED_STATUS_PIN, GPIO.OUT)

# Ensure everything starts in safe state
GPIO.output(CHARGING_RELAY_PIN, False)
GPIO.output(SERVO_ENABLE_PIN, True)  # Servo power enabled by default
GPIO.output(LED_STATUS_PIN, False)

# Serial connection to Teensy/Duet
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
time.sleep(2)  # Wait for serial port to initialize

print("Dock Manager Initialized — OBSIDIAN-8 V3")

# -------------------- FUNCTIONS --------------------
def send_servo_enable(enable: bool):
    """Send servo enable/disable command to Teensy/Duet"""
    cmd = f"SERVO_ENABLE:{int(enable)}\n"
    ser.write(cmd.encode('utf-8'))
    print(f"Sent command to servo controller: {cmd.strip()}")

def enable_charging():
    GPIO.output(CHARGING_RELAY_PIN, True)
    GPIO.output(LED_STATUS_PIN, True)
    print("Charging enabled.")

def disable_charging():
    GPIO.output(CHARGING_RELAY_PIN, False)
    GPIO.output(LED_STATUS_PIN, False)
    print("Charging disabled.")

def is_docked():
    """Check dock contact sensor"""
    return GPIO.input(DOCK_DETECT_PIN) == GPIO.LOW  # NC switch: LOW when contact

# -------------------- MAIN LOOP --------------------
try:
    while True:
        if is_docked():
            print("Dock detected. Preparing for charging...")
            # Disable servo power
            send_servo_enable(False)
            GPIO.output(SERVO_ENABLE_PIN, False)
            # Wait briefly to allow current to settle
            time.sleep(DOCK_APPROACH_DELAY)
            # Enable charging
            enable_charging()
        else:
            # Not docked, ensure charging is off and servo power is on
            disable_charging()
            send_servo_enable(True)
            GPIO.output(SERVO_ENABLE_PIN, True)

        time.sleep(0.2)  # 5 Hz loop

except KeyboardInterrupt:
    print("Dock Manager exiting...")
    disable_charging()
    send_servo_enable(True)
    GPIO.output(SERVO_ENABLE_PIN, True)
    GPIO.cleanup()
    ser.close()
