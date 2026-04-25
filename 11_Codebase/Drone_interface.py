# drone_interface.py — REV A (MAVLink Drone Control via UDP)

from pymavlink import mavutil
import time

class DroneInterface:
    def __init__(self, connection_string="udp:127.0.0.1:14550"):
        print(f"[DRONE] Connecting to {connection_string}")
        self.master = mavutil.mavlink_connection(connection_string)

        print("[DRONE] Waiting for heartbeat...")
        self.master.wait_heartbeat()
        print("[DRONE] Connected")

    # ---------------- BASIC CONTROL ----------------

    def arm(self):
        print("[DRONE] Arming")
        self.master.arducopter_arm()
        self.master.motors_armed_wait()

    def disarm(self):
        print("[DRONE] Disarming")
        self.master.arducopter_disarm()

    def takeoff(self, altitude=2.0):
        print(f"[DRONE] Takeoff to {altitude}m")

        self.master.set_mode_apm("GUIDED")

        self.arm()

        self.master.mav.command_long_send(
            self.master.target_system,
            self.master.target_component,
            mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
            0,
            0, 0, 0, 0,
            0, 0, altitude
        )

        time.sleep(5)

    def land(self):
        print("[DRONE] Landing")
        self.master.set_mode_apm("LAND")

    # ---------------- NAVIGATION ----------------

    def goto(self, lat, lon, alt):
        print(f"[DRONE] Goto {lat}, {lon}, {alt}")

        self.master.mav.set_position_target_global_int_send(
            0,
            self.master.target_system,
            self.master.target_component,
            mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
            int(0b110111111000),
            int(lat * 1e7),
            int(lon * 1e7),
            alt,
            0, 0, 0,
            0, 0, 0,
            0, 0
        )

    # ---------------- TELEMETRY ----------------

    def get_position(self):
        msg = self.master.recv_match(type="GLOBAL_POSITION_INT", blocking=False)
        if msg:
            lat = msg.lat / 1e7
            lon = msg.lon / 1e7
            alt = msg.relative_alt / 1000.0
            return lat, lon, alt
        return None
