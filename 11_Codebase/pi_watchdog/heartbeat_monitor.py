"""
OBSIDIAN-8 V3
heartbeat_monitor.py
Revision: V3.2
Status: Authoritative

Purpose:
Python module for Pi Watchdog service to monitor system heartbeat signals,
verify process health, and enforce reactive safety kill-line if
heartbeat fails.

Dependencies:
- Python 3.10+
- threading
- time
- logging
- duet_io_interface (for emergency halt)
"""

import threading
import time
import logging
from duet_bridge.duet_io_interface import DuetIOInterface

# -------------------------
# Logging Configuration
# -------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("HeartbeatMonitor")

# -------------------------
# Heartbeat Monitor Class
# -------------------------
class HeartbeatMonitor:
    def __init__(self, timeout=1.0):
        """
        :param timeout: Maximum allowed time (s) between heartbeats
        """
        self.timeout = timeout
        self.last_heartbeat = time.time()
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._watchdog_thread = threading.Thread(target=self._monitor_loop)
        self._watchdog_thread.daemon = True
        self.duet = DuetIOInterface()
        self._watchdog_thread.start()
        logger.info(f"Heartbeat Monitor initialized with {timeout}s timeout.")

    # ---------------------
    # Heartbeat API
    # ---------------------
    def ping(self):
        """
        Called by monitored processes to reset heartbeat timer.
        """
        with self._lock:
            self.last_heartbeat = time.time()
        logger.debug("Heartbeat received.")

    # ---------------------
    # Monitoring Loop
    # ---------------------
    def _monitor_loop(self):
        while not self._stop_event.is_set():
            with self._lock:
                elapsed = time.time() - self.last_heartbeat
            if elapsed > self.timeout:
                logger.warning(f"Heartbeat timeout exceeded ({elapsed:.2f}s)! Triggering safety halt.")
                self._trigger_emergency()
            time.sleep(0.05)

    # ---------------------
    # Emergency Actions
    # ---------------------
    def _trigger_emergency(self):
        """
        Executes fail-safe procedures on heartbeat failure.
        """
        try:
            self.duet.halt_all_actuators()
            logger.error("Emergency halt executed due to heartbeat failure.")
        except Exception as e:
            logger.critical(f"Emergency halt failed: {e}")

    # ---------------------
    # Shutdown
    # ---------------------
    def shutdown(self):
        logger.info("Shutting down Heartbeat Monitor.")
        self._stop_event.set()
        self._watchdog_thread.join()
        self.duet.shutdown()


# -------------------------
# Example Usage
# -------------------------
if __name__ == "__main__":
    monitor = HeartbeatMonitor(timeout=1.5)
    try:
        # Simulate heartbeat
        for i in range(5):
            monitor.ping()
            logger.info(f"Heartbeat ping {i+1}")
            time.sleep(1.0)
        # Simulate heartbeat failure
        logger.info("Simulating heartbeat failure...")
        time.sleep(2.0)
    finally:
        monitor.shutdown()
