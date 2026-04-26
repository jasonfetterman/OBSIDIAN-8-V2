"""
drone_controller.py
MAVLink Drone Interface for OBSIDIAN-8
"""

import time
from pymavlink import mavutil


class DroneController:
    def __init__(self, connection_string="udp:127.0.0.1:14550"):
        print("[DRONE] Connecting to MAVLink...")

        self.master = mavutil.mavlink_connection(connection_string)
        self.master.wait_heartbeat()

        print("[DRONE] Connected")

    # =========================
    # BASIC CONTROL
    # =========================
    def arm(self):
        print("[DRONE] Arming")
        self.master.arducopter_arm()
        self.master.motors_armed_wait()

    def disarm(self):
        print("[DRONE] Disarming")
        self.master.arducopter_disarm()

    def takeoff(self, altitude=10):
        print(f"[DRONE] Takeoff to {altitude}m")

        self.master.set_mode_apm("GUIDED")
        self.arm()

        self.master.mav.command_long_send(
            self.master.target_system,
            self.master.target_component,
            mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
            0,
            0, 0, 0, 0, 0, 0,
            altitude
        )

    def land(self):
        print("[DRONE] Landing")

        self.master.set_mode_apm("LAND")

    # =========================
    # SIMPLE RECON MISSION
    # =========================
    def recon_scan(self, altitude=10, duration=10):
        print("[DRONE] Starting recon scan")

        self.takeoff(altitude)

        time.sleep(duration)

        self.land()

    # =========================
    # TELEMETRY
    # =========================
    def get_position(self):
        msg = self.master.recv_match(type='GLOBAL_POSITION_INT', blocking=False)

        if msg:
            return {
                "lat": msg.lat / 1e7,
                "lon": msg.lon / 1e7,
                "alt": msg.alt / 1000
            }

        return None
