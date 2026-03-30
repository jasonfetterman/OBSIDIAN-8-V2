# teleop_interface.py
# OBSIDIAN-8 V3 — REV D
# Handles teleoperation commands from joystick or remote controller

import pygame
import numpy as np

# -------------------- CONFIG --------------------
JOYSTICK_DEADZONE = 0.1
JOINT_DELTA_SCALE = 2.0  # degrees per input unit
UPDATE_RATE_HZ = 50

# Mapping axes to joints
AXIS_TO_JOINT = {
    0: 'coxa',   # X-axis left/right
    1: 'femur',  # Y-axis forward/back
    2: 'tibia',  # Z-axis up/down
}

# -------------------- CLASS --------------------
class TeleopInterface:
    def __init__(self):
        pygame.init()
        pygame.joystick.init()
        self.joystick = None
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            print(f"[TeleopInterface] Joystick detected: {self.joystick.get_name()}")
        else:
            print("[TeleopInterface] No joystick detected. Teleop disabled.")

    def get_input(self):
        """
        Poll joystick axes and buttons to generate joint delta commands
        Returns dict: {'coxa': delta, 'femur': delta, 'tibia': delta}
        """
        delta_cmds = {'coxa': 0.0, 'femur': 0.0, 'tibia': 0.0}
        if self.joystick is None:
            return delta_cmds

        pygame.event.pump()  # Process event queue

        for axis_index, joint_name in AXIS_TO_JOINT.items():
            value = self.joystick.get_axis(axis_index)
            if abs(value) < JOYSTICK_DEADZONE:
                value = 0.0
            delta_cmds[joint_name] = value * JOINT_DELTA_SCALE

        return delta_cmds

    def shutdown(self):
        """
        Cleanup joystick
        """
        if self.joystick:
            self.joystick.quit()
        pygame.quit()
        print("[TeleopInterface] Teleop interface shutdown complete.")


# -------------------- TEST LOOP --------------------
if __name__ == "__main__":
    teleop = TeleopInterface()
    try:
        while True:
            commands = teleop.get_input()
            print(f"[Teleop] Commands: {commands}")
            pygame.time.wait(int(1000 / UPDATE_RATE_HZ))
    except KeyboardInterrupt:
        teleop.shutdown()
