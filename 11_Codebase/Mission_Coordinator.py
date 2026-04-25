# mission_coordinator.py — REV B (Drone → Ground Coordination)

import time
import threading
import math

class MissionCoordinator:
    def __init__(self, swarm, set_pose_callback):
        self.swarm = swarm
        self.set_pose = set_pose_callback

        self.active = False
        self.follow_thread = None

        # Simple movement tuning
        self.step_forward_pose = [95.0] * 16
        self.base_pose = [90.0] * 16

        # Target tracking
        self.target_lat = None
        self.target_lon = None

    # ---------------- BASIC MISSION ----------------

    def scout_and_follow(self, lat, lon, alt=3.0):
        """
        Drone scouts → ground robot follows directionally
        """
        print("[MISSION] Scout + Follow")

        self.active = True
        self.target_lat = lat
        self.target_lon = lon

        # Drone actions
        self.swarm.takeoff_all(alt)
        time.sleep(8)
        self.swarm.goto_all(lat, lon, alt)

        # Start follow loop
        self.follow_thread = threading.Thread(target=self._follow_loop, daemon=True)
        self.follow_thread.start()

    # ---------------- FOLLOW LOOP ----------------

    def _follow_loop(self):
        print("[MISSION] Ground follow loop started")

        while self.active:
            positions = self.swarm.get_positions()

            if not positions:
                time.sleep(0.2)
                continue

            # Use first drone
            drone_id = list(positions.keys())[0]
            lat, lon, alt = positions[drone_id]

            # Compute distance to target
            dist = self._distance(lat, lon, self.target_lat, self.target_lon)

            print(f"[MISSION] Drone dist to target: {dist:.2f}")

            # Simple logic:
            # If drone is still far → move forward
            # If close → stop

            if dist > 1.5:
                self.set_pose(self.step_forward_pose)
            else:
                self.set_pose(self.base_pose)

            time.sleep(0.2)

    # ---------------- UTIL ----------------

    def _distance(self, lat1, lon1, lat2, lon2):
        # Rough flat-earth approximation (fine for SITL)
        dx = (lat2 - lat1) * 111000
        dy = (lon2 - lon1) * 111000
        return math.sqrt(dx*dx + dy*dy)

    # ---------------- STOP ----------------

    def stop(self):
        print("[MISSION] Stopping mission")

        self.active = False

        try:
            self.swarm.land_all()
        except:
            pass

        self.set_pose(self.base_pose)
