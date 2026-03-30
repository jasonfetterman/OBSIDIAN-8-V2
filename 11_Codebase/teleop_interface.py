"""
teleop_interface.py
OBSIDIAN-8 V3 — REV D
Provides manual control over the robot via gamepad or network commands
"""

import threading
import time

# Optional libraries for gamepad
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

class TeleopInterface:
    def __init__(self, motion_planner, control_rate=50):
        """
        motion_planner: instance of MotionPlanner to send joint commands
        control_rate: loop frequency in Hz
        """
        self.motion_planner = motion_planner
        self.running = False
        self.control_rate = control_rate
        self.command_queue = []
        self.lock = threading.Lock()

        # Initialize gamepad if available
        if PYGAME_AVAILABLE:
            pygame.init()
            pygame.joystick.init()
            self.joystick_count = pygame.joystick.get_count()
            if self.joystick_count > 0:
                self.joystick = pygame.joystick.Joystick(0)
                self.joystick.init()
                print(f"[TeleopInterface] Gamepad detected: {self.joystick.get_name()}")
            else:
                self.joystick = None
                print("[TeleopInterface] No gamepad detected")
        else:
            self.joystick = None
            print("[TeleopInterface] Pygame not installed, gamepad disabled")

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self.control_loop)
        self.thread.start()

    def stop(self):
        self.running = False
        self.thread.join()

    def control_loop(self):
        """Main teleoperation loop"""
        while self.running:
            # 1. Process gamepad input
            if self.joystick:
                pygame.event.pump()
                # Example mapping: left stick = forward/backward, right stick = turn
                forward = self.joystick.get_axis(1)  # -1 to 1
                turn = self.joystick.get_axis(0)     # -1 to 1

                # Convert to joint commands (placeholder mapping)
                joint_commands = self.convert_to_joint_commands(forward, turn)

                # Execute trajectory
                self.motion_planner.execute_trajectory(joint_commands)

            # 2. Process queued network commands
            with self.lock:
                while self.command_queue:
                    cmd = self.command_queue.pop(0)
                    self.motion_planner.execute_trajectory(cmd)

            time.sleep(1.0 / self.control_rate)

    def convert_to_joint_commands(self, forward, turn):
        """
        Convert joystick input to joint trajectory commands.
        Returns list of joint positions or velocities
        """
        # Example simple mapping for demonstration
        joint_positions = [forward*0.1 + turn*0.05]*24  # 24-leg joints
        return joint_positions

    def enqueue_command(self, joint_command):
        with self.lock:
            self.command_queue.append(joint_command)

# -------------------- TEST LOOP --------------------
if __name__ == "__main__":
    # Mock motion planner for testing
    class MockMotionPlanner:
        def execute_trajectory(self, joint_positions):
            print(f"[MockMotionPlanner] Executing: {joint_positions[:4]}...")

    teleop = TeleopInterface(MockMotionPlanner())
    teleop.start()
    print("[TeleopInterface] Teleop loop started. Press Ctrl+C to stop.")

    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        teleop.stop()
        print("[TeleopInterface] Stopped")
