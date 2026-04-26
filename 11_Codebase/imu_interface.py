# imu_interface.py — REV A (Simple Heading Interface)

import serial
import threading

class IMUInterface:
    def __init__(self, port="COM4", baud=115200):
        self.ser = serial.Serial(port, baud, timeout=0.01)
        self.heading = 0.0
        self.running = True

        threading.Thread(target=self._read_loop, daemon=True).start()

    def _read_loop(self):
        while self.running:
            try:
                line = self.ser.readline().decode(errors="ignore").strip()

                # Expected format: HEADING:123.45
                if line.startswith("HEADING:"):
                    val = float(line.split(":")[1])
                    self.heading = val
            except:
                pass

    def get_heading(self):
        return self.heading
