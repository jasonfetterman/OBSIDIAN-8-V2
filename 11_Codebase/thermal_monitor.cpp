// thermal_monitor.cpp — REV D (Manual Reset Required After Thermal Shutdown)

#include <Arduino.h>

// ---------------- CONFIG ----------------

// Temp sensors (LM35 or equivalent)
#define TEMP_SERVO_PIN A0
#define TEMP_BATTERY_PIN A1
#define TEMP_BUCK_PIN A2

// Kill control
#define KILL_PIN 22

// Manual reset button (physical)
#define RESET_BUTTON_PIN 23  // pull-down or pull-up depending on wiring

// Thresholds (°C)
#define TEMP_WARNING 60.0
#define TEMP_CRITICAL 70.0

// Filtering
#define FILTER_ALPHA 0.2

// Timing
#define UPDATE_INTERVAL_MS 100

// ---------------- STATE ----------------

float filteredServo = 25.0;
float filteredBattery = 25.0;
float filteredBuck = 25.0;

bool thermalShutdownLatched = false;

// ---------------- UTIL ----------------

float readTemperature(int pin) {
    int raw = analogRead(pin);
    float voltage = (raw / 1023.0) * 3.3;
    return voltage * 100.0;
}

float filterTemp(float prev, float current) {
    return prev + FILTER_ALPHA * (current - prev);
}

// ---------------- KILL CONTROL ----------------

void enableServos() {
    digitalWrite(KILL_PIN, HIGH);  // ACTIVE HIGH = ON
}

void disableServos() {
    digitalWrite(KILL_PIN, LOW);   // OFF
}

// ---------------- ACTIONS ----------------

void thermalThrottle() {
    Serial.println("THERMAL_WARNING");
}

void triggerThermalShutdown() {
    disableServos();
    thermalShutdownLatched = true;
    Serial.println("THERMAL_SHUTDOWN_LATCHED");
}

// ---------------- RESET HANDLING ----------------

void checkManualReset() {
    if (thermalShutdownLatched) {
        // Button press = HIGH (adjust if using pull-up)
        if (digitalRead(RESET_BUTTON_PIN) == HIGH) {
            thermalShutdownLatched = false;
            enableServos();
            Serial.println("THERMAL_MANUAL_RESET");
            delay(500); // debounce + prevent rapid re-trigger
        }
    }
}

// ---------------- CORE ----------------

void updateThermal() {
    float tServo = readTemperature(TEMP_SERVO_PIN);
    float tBattery = readTemperature(TEMP_BATTERY_PIN);
    float tBuck = readTemperature(TEMP_BUCK_PIN);

    filteredServo = filterTemp(filteredServo, tServo);
    filteredBattery = filterTemp(filteredBattery, tBattery);
    filteredBuck = filterTemp(filteredBuck, tBuck);

    float maxTemp = filteredServo;
    if (filteredBattery > maxTemp) maxTemp = filteredBattery;
    if (filteredBuck > maxTemp) maxTemp = filteredBuck;

    // If already latched, do nothing except wait for reset
    if (thermalShutdownLatched) {
        checkManualReset();
        return;
    }

    // Critical shutdown (latching)
    if (maxTemp >= TEMP_CRITICAL) {
        triggerThermalShutdown();
        return;
    }

    // Warning
    if (maxTemp >= TEMP_WARNING) {
        thermalThrottle();
    }

    // Debug
    Serial.print("TEMP | S:");
    Serial.print(filteredServo);
    Serial.print(" B:");
    Serial.print(filteredBattery);
    Serial.print(" C:");
    Serial.print(filteredBuck);
    Serial.print(" MAX:");
    Serial.println(maxTemp);
}

// ---------------- SETUP ----------------

void setupThermal() {
    analogReadResolution(10);

    pinMode(KILL_PIN, OUTPUT);
    pinMode(RESET_BUTTON_PIN, INPUT);

    // SAFE DEFAULT
    disableServos();
}

// ---------------- LOOP ----------------

void loopThermal() {
    static unsigned long lastUpdate = 0;

    if (millis() - lastUpdate >= UPDATE_INTERVAL_MS) {
        lastUpdate = millis();
        updateThermal();
    }
}
