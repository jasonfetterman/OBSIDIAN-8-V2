# mission_coordinator.py — REV E (Heading-Aligned Coordination)

import time
import threading
import math

class MissionCoordinator:
    def __init__(self, swarm, set_pose_callback, imu):
        self.swarm = swarm
        self.set_pose = set_pose_callback
        self.imu = imu

        self.active = False
        self.follow_thread = None

        self.current_pose = [90.0] * 16
        self.target_pose = [90.0] * 16

        self.base_pose = [90.0] * 16

        self.step_strength = 6.0
        self.turn_strength = 5.0
        self.smoothing = 0.2

        self.thermal_scale = 1.0

    # ---------------- MISSION ----------------

    def scout_and_follow(self, lat, lon, alt=3.0):
        print("[MISSION] Heading-Aligned Follow")

        self.active = True

        self.swarm.takeoff_all(alt)
        time.sleep(8)
        self.swarm.goto_all(lat, lon, alt)

        self.follow_thread = threading.Thread(target=self._follow_loop, daemon=True)
        self.follow_thread.start()

    # ---------------- FOLLOW LOOP ----------------

    def _follow_loop(self):
        print("[MISSION] Heading control active")

        while self.active:
            positions = self.swarm.get_positions()

            if not positions:
                time.sleep(0.1)
                continue

            drone_id = list(positions.keys())[0]
            lat, lon, _ = positions[drone_id]

            # Convert to local vector (approx)
            target_angle = math.degrees(math.atan2(lon, lat))

            # Get robot heading
            current_heading = self.imu.get_heading()

            # Compute error
            error = self._angle_diff(target_angle, current_heading)

            print(f"[MISSION] Heading error: {error:.2f}")

            # Normalize error
            turn = max(min(error / 45.0, 1.0), -1.0)

            forward = (1.0 - abs(turn)) * self.step_strength * self.thermal_scale
            turn *= self.turn_strength * self.thermal_scale

            # Build pose
            self.target_pose = []

            for i in range(16):
                base = 90.0

                if i % 2 == 0:
                    angle = base + forward
                else:
                    angle = base - forward

                if i < 8:
                    angle += turn
                else:
                    angle -= turn

                self.target_pose.append(angle)

            self.current_pose = self._blend(self.current_pose, self.target_pose)
            self.set_pose(self.current_pose)

            time.sleep(0.05)

    # ---------------- UTIL ----------------

    def _angle_diff(self, a, b):
        diff = (a - b + 180) % 360 - 180
        return diff

    def _blend(self, current, target):
        return [c + self.smoothing * (t - c) for c, t in zip(current, target)]

    def set_thermal_state(self, state):
        if state == "NORMAL":
            self.thermal_scale = 1.0
        elif state == "WARNING":
            self.thermal_scale = 0.5
        else:
            self.thermal_scale = 0.0

    def stop(self):
        print("[MISSION] Stopping")

        self.active = False

        try:
            self.swarm.land_all()
        except:
            pass

        self.set_pose(self.base_pose)
