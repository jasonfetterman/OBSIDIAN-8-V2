# main_controller.py
# OBSIDIAN-8 V3 — REV D
# Central controller orchestrating all subsystems: autonomous, teleop, vision, swarm, and motion

import threading
import time
from autonomous_mode import AutonomousMode
from teleop_interface import TeleopInterface
from motion_planner import MotionPlanner
from swarm_comms import SwarmComms

class MainController:
    def __init__(self, node_id="OB8-Node1"):
        # Mode: "autonomous" or "teleop"
        self.mode = "autonomous"

        # Subsystems
        self.autonomous = AutonomousMode(node_id=node_id)
        self.teleop = TeleopInterface()
        self.motion_planner = MotionPlanner()
        self.swarm = self.autonomous.swarm  # Shared with autonomous mode

        self.running = True

    def mode_switch_loop(self):
        """
        Monitors input to switch between autonomous and teleop
        """
        while self.running:
            # Example: check teleop flag (could be joystick input)
            new_mode = self.teleop.get_mode()
            if new_mode != self.mode:
                print(f"[MainController] Switching mode: {self.mode} -> {new_mode}")
                self.mode = new_mode
            time.sleep(0.1)

    def control_loop(self):
        """
        Main control loop: runs at 50 Hz
        """
        while self.running:
            if self.mode == "autonomous":
                # Get perception data
                tracked_objects = self.autonomous.process_vision()
                foot_state = self.autonomous.foot_state

                # Compute motion commands
                commands = self.motion_planner.compute_gait(tracked_objects, foot_state)

                # Send commands to servo driver
                # TODO: integrate with servo_driver.cpp interface
                # e.g., self.servo_driver.send_commands(commands)

            elif self.mode == "teleop":
                # Get teleop commands
                commands = self.teleop.get_commands()
                # Send commands to servo driver
                # TODO: integrate with servo_driver.cpp interface

            # Optional: handle swarm messages
            messages = self.swarm.get_messages()
            for msg in messages:
                print("[Swarm] Received:", msg)

            time.sleep(0.02)  # 50 Hz

    def run(self):
        """
        Starts main controller
        """
        # Mode switch thread
        mode_thread = threading.Thread(target=self.mode_switch_loop)
        mode_thread.start()

        # Main control loop
        try:
            self.control_loop()
        finally:
            self.shutdown()
            mode_thread.join()

    def shutdown(self):
        self.running = False
        self.autonomous.shutdown()
        self.teleop.shutdown()
        print("[MainController] Shutdown complete.")


# -------------------- TEST LOOP --------------------
if __name__ == "__main__":
    controller = MainController(node_id="OB8-Node1")
    controller.run()
