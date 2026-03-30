// emergency_stop.cpp
// OBSIDIAN-8 V3 — REV D
// Monitors E-Stop button and triggers immediate servo bank shutdown

#include <Arduino.h>

// -------------------- HARDWARE CONFIG --------------------
// Emergency Stop button input (normally closed)
const int ESTOP_PIN = 2;  // Digital input, NC switch
const int ESTOP_REMOTE_PIN = 3; // Optional remote E-Stop signal

// Servo bank contactors
const int CONTACTOR_BANK_A = 5;
const int CONTACTOR_BANK_B = 6;

// Fault LED
const int LED_FAULT = 13;

// -------------------- SETUP --------------------
void setup() {
    Serial.begin(115200);

    // Inputs
    pinMode(ESTOP_PIN, INPUT_PULLUP); // NC button, pulled HIGH when released
    pinMode(ESTOP_REMOTE_PIN, INPUT_PULLUP);

    // Outputs
    pinMode(CONTACTOR_BANK_A, OUTPUT);
    pinMode(CONTACTOR_BANK_B, OUTPUT);
    pinMode(LED_FAULT, OUTPUT);

    // Enable servo banks initially
    digitalWrite(CONTACTOR_BANK_A, HIGH);
    digitalWrite(CONTACTOR_BANK_B, HIGH);
    digitalWrite(LED_FAULT, LOW);

    Serial.println("Emergency Stop Monitor Initialized — OBSIDIAN-8 V3");
}

// -------------------- FUNCTIONS --------------------
void triggerEmergencyStop() {
    digitalWrite(CONTACTOR_BANK_A, LOW);
    digitalWrite(CONTACTOR_BANK_B, LOW);
    digitalWrite(LED_FAULT, HIGH);
    Serial.println("EMERGENCY STOP ACTIVATED! Servo power cut.");
}

// -------------------- LOOP --------------------
void loop() {
    // Read E-Stop buttons (NC logic)
    bool estopPressed = (digitalRead(ESTOP_PIN) == LOW);
    bool remotePressed = (digitalRead(ESTOP_REMOTE_PIN) == LOW);

    if (estopPressed || remotePressed) {
        triggerEmergencyStop();
    }

    delay(50); // 20 Hz check rate
}
