# mission_coordinator.py — REV A (Ground + Drone Mission Layer)

import time

class MissionCoordinator:
    def __init__(self, swarm):
        self.swarm = swarm
        self.active = False

    # ---------------- BASIC MISSION ----------------

    def scout_and_hold(self, lat, lon, alt=3.0):
        """
        Phase 1:
        - Drone takes off
        - Moves to target location
        - Holds position

        Ground robot does NOT move yet
        """
        print("[MISSION] Starting scout mission")

        self.active = True

        # Step 1 — Takeoff
        print("[MISSION] Drone takeoff")
        self.swarm.takeoff_all(alt)

        time.sleep(8)

        # Step 2 — Move to target
        print("[MISSION] Drone moving to waypoint")
        self.swarm.goto_all(lat, lon, alt)

        print("[MISSION] Drone holding position")

    # ---------------- STOP ----------------

    def stop(self):
        print("[MISSION] Stopping mission")
        self.swarm.land_all()
        self.active = False
