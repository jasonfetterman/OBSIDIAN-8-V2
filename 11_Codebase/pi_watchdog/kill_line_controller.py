"""
OBSIDIAN-8 V3
kill_line_controller.py
Revision: V3.2
Status: Authoritative

Purpose:
Python module for controlling the OBSIDIAN-8 kill-line hardware.
Ensures reactive safety dominance by immediately halting actuators
under emergency conditions, watchdog triggers, or software-defined stops.

Dependencies:
- Python 3.10+
- RPi.GPIO or similar GPIO library for Raspberry Pi
- threading
- time
- logging
- duet_bridge.duet_io_interface (optional integration)
"""

import threading
import time
import logging

try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False
    logging.warning("RPi.GPIO not available; kill-line will be simulated.")

from duet_bridge.duet_io_interface import DuetIOInterface

# -------------------------
# Logging Configuration
# -------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("KillLineController")

# -------------------------
# Kill-Line Controller Class
# -------------------------
class KillLineController:
    def __init__(self, gpio_pin=17, active_high=True):
        """
        :param gpio_pin: GPIO pin connected to kill-line relay
        :param active_high: True if HIGH signal triggers kill
        """
        self.gpio_pin = gpio_pin
        self.active_high = active_high
        self._lock = threading.Lock()
        self.duet = DuetIOInterface()

        if GPIO_AVAILABLE:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.gpio_pin, GPIO.OUT)
            # Ensure kill-line is safe on startup
            GPIO.output(self.gpio_pin, not self.active_high)

        logger.info(f"KillLineController initialized on GPIO {self.gpio_pin}, active_high={self.active_high}.")

    # ---------------------
    # Trigger Kill-Line
    # ---------------------
    def engage(self):
        """
        Activate the kill-line immediately.
        """
        with self._lock:
            if GPIO_AVAILABLE:
                GPIO.output(self.gpio_pin, self.active_high)
            # Ensure actuators also halted
            self.duet.halt_all_actuators()
            logger.warning("Kill-line engaged! All actuators halted.")

    # ---------------------
    # Disengage Kill-Line
    # ---------------------
    def release(self):
        """
        Reset kill-line to allow normal operation.
        """
        with self._lock:
            if GPIO_AVAILABLE:
                GPIO.output(self.gpio_pin, not self.active_high)
            logger.info("Kill-line released. Normal operation allowed.")

    # ---------------------
    # Emergency Stop Helper
    # ---------------------
    def emergency_stop(self):
        """
        Convenience method for safety-critical shutdown.
        Engages kill-line and logs event.
        """
        logger.error("Emergency stop invoked!")
        self.engage()

    # ---------------------
    # Shutdown Controller
    # ---------------------
    def shutdown(self):
        logger.info("Shutting down KillLineController.")
        self.release()
        if GPIO_AVAILABLE:
            GPIO.cleanup()
        self.duet.shutdown()


# -------------------------
# Example Usage
# -------------------------
if __name__ == "__main__":
    kill_ctrl = KillLineController(gpio_pin=17)
    try:
        logger.info("Engaging kill-line for 3 seconds...")
        kill_ctrl.engage()
        time.sleep(3)
        logger.info("Releasing kill-line...")
        kill_ctrl.release()
    finally:
        kill_ctrl.shutdown()
