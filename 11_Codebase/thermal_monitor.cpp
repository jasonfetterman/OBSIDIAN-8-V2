// thermal_monitor.cpp — REV B (Multi-Zone Thermal Protection System)

#include <Arduino.h>

// ---------------- CONFIG ----------------

// Analog temperature sensors (e.g., LM35 or similar)
#define TEMP_SERVO_PIN A0
#define TEMP_BATTERY_PIN A1
#define TEMP_BUCK_PIN A2

// Thresholds (°C)
#define TEMP_WARNING 60.0
#define TEMP_CRITICAL 70.0

// Filtering
#define FILTER_ALPHA 0.2

// ---------------- STATE ----------------

float tempServo = 25.0;
float tempBattery = 25.0;
float tempBuck = 25.0;

float filteredServo = 25.0;
float filteredBattery = 25.0;
float filteredBuck = 25.0;

// ---------------- UTIL ----------------

// Convert analog reading to temperature
// Assumes LM35: 10mV per °C, Teensy ADC 3.3V reference
float readTemperature(int pin) {
    int raw = analogRead(pin);
    float voltage = (raw / 1023.0) * 3.3;
    float tempC = voltage * 100.0;
    return tempC;
}

// Simple low-pass filter
float filterTemp(float prev, float current) {
    return prev + FILTER_ALPHA * (current - prev);
}

// ---------------- SAFETY HOOKS ----------------

// These should connect to your system logic
void thermalThrottle() {
    // Placeholder: integrate with motion system to reduce speed
    Serial.println("THERMAL WARNING: Throttling motion");
}

void thermalShutdown() {
    // Placeholder: trigger kill line or stop commands
    Serial.println("THERMAL CRITICAL: SHUTDOWN");
}

// ---------------- MAIN UPDATE ----------------

void updateThermal() {
    // Read sensors
    tempServo = readTemperature(TEMP_SERVO_PIN);
    tempBattery = readTemperature(TEMP_BATTERY_PIN);
    tempBuck = readTemperature(TEMP_BUCK_PIN);

    // Filter
    filteredServo = filterTemp(filteredServo, tempServo);
    filteredBattery = filterTemp(filteredBattery, tempBattery);
    filteredBuck = filterTemp(filteredBuck, tempBuck);

    // Determine max temp
    float maxTemp = filteredServo;
    if (filteredBattery > maxTemp) maxTemp = filteredBattery;
    if (filteredBuck > maxTemp) maxTemp = filteredBuck;

    // Safety logic
    if (maxTemp >= TEMP_CRITICAL) {
        thermalShutdown();
    } else if (maxTemp >= TEMP_WARNING) {
        thermalThrottle();
    }

    // Debug output
    Serial.print("Temps | Servo: ");
    Serial.print(filteredServo);
    Serial.print("C Battery: ");
    Serial.print(filteredBattery);
    Serial.print("C Buck: ");
    Serial.print(filteredBuck);
    Serial.println("C");
}

// ---------------- SETUP ----------------

void setupThermal() {
    analogReadResolution(10);
}

// ---------------- LOOP EXAMPLE ----------------

void loopThermal() {
    static unsigned long lastUpdate = 0;

    if (millis() - lastUpdate >= 100) {
        lastUpdate = millis();
        updateThermal();
    }
}
