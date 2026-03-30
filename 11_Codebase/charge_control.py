# charge_control.py
# OBSIDIAN-8 V3 — REV D
# Monitors and controls LiFePO4 charging safely

import time
import board
import busio
import adafruit_ina219  # Current / Voltage monitor library
from dock_comm import DockComm  # Integration with dock communication

# -------------------- HARDWARE CONFIG --------------------
I2C_SCL = board.SCL
I2C_SDA = board.SDA

# ACS712 or INA219 current sensor addresses
INA219_ADDR_BANK_A = 0x40
INA219_ADDR_BANK_B = 0x41

# Battery temperature analog input (if using ADC)
BATTERY_TEMP_PIN = 0  # example, use ADC setup as needed

# Safety limits
MAX_BATTERY_VOLTAGE = 28.0  # V
MIN_BATTERY_VOLTAGE = 20.0  # V
MAX_CHARGE_CURRENT = 15.0    # A
MAX_BATTERY_TEMP = 60.0      # °C

# -------------------- SETUP --------------------
# Initialize I2C and INA219 sensors
i2c = busio.I2C(I2C_SCL, I2C_SDA)
ina_a = adafruit_ina219.INA219(i2c, address=INA219_ADDR_BANK_A)
ina_b = adafruit_ina219.INA219(i2c, address=INA219_ADDR_BANK_B)

# Dock communication
dock = DockComm()

print("Charge Control Initialized — OBSIDIAN-8 V3")

# -------------------- HELPER FUNCTIONS --------------------
def read_battery_voltage():
    """Read battery voltage from bank A (primary)"""
    return ina_a.bus_voltage

def read_charge_current():
    """Read total current flowing into battery"""
    current_a = ina_a.current / 1000.0  # mA -> A
    current_b = ina_b.current / 1000.0
    return current_a + current_b

def read_battery_temperature():
    """Placeholder for ADC temperature reading; integrate actual NTC reading"""
    # TODO: Replace with ADC read of BATTERY_TEMP_PIN and NTC formula
    return 35.0  # example, safe default for testing

def stop_charging():
    dock.send_charge_enable(False)
    dock.send_servo_enable(True)
    print("Charging stopped due to safety limit.")

# -------------------- MAIN LOOP --------------------
try:
    while True:
        voltage = read_battery_voltage()
        current = read_charge_current()
        temp = read_battery_temperature()

        print(f"Battery Voltage: {voltage:.2f} V | Current: {current:.2f} A | Temp: {temp:.1f} °C")

        # Safety checks
        if voltage > MAX_BATTERY_VOLTAGE:
            print("Overvoltage detected!")
            stop_charging()
        elif voltage < MIN_BATTERY_VOLTAGE:
            print("Undervoltage detected! Check battery health.")
            stop_charging()
        elif current > MAX_CHARGE_CURRENT:
            print("Overcurrent detected during charging!")
            stop_charging()
        elif temp > MAX_BATTERY_TEMP:
            print("Battery overheating!")
            stop_charging()
        else:
            # Safe to charge
            dock.send_charge_enable(True)
            dock.send_servo_enable(False)

        time.sleep(0.5)  # 2 Hz monitoring

except KeyboardInterrupt:
    print("Charge Control exiting...")
    dock.send_charge_enable(False)
    dock.send_servo_enable(True)
    dock.ser.close()
