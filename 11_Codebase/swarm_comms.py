# swarm_comms.py — REV B (Ground + Drone Integration)

from drone_interface import DroneInterface

class SwarmController:
    def __init__(self):
        self.drones = {}

    # ---------------- DRONE MANAGEMENT ----------------

    def add_drone(self, drone_id, connection):
        drone = DroneInterface(connection)
        self.drones[drone_id] = drone
        print(f"[SWARM] Drone {drone_id} added")

    # ---------------- COMMANDS ----------------

    def takeoff_all(self, altitude=2.0):
        for drone in self.drones.values():
            drone.takeoff(altitude)

    def land_all(self):
        for drone in self.drones.values():
            drone.land()

    def goto_all(self, lat, lon, alt):
        for drone in self.drones.values():
            drone.goto(lat, lon, alt)

    # ---------------- STATUS ----------------

    def get_positions(self):
        positions = {}
        for drone_id, drone in self.drones.items():
            pos = drone.get_position()
            if pos:
                positions[drone_id] = pos
        return positions
