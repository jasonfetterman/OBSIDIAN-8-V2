// servo_driver.cpp — REV B (Teensy High-Torque Servo Control)

#include <Arduino.h>

// ---------------- CONFIG ----------------

#define SERVO_COUNT 8

// PWM timing (microseconds)
#define PWM_MIN 1000
#define PWM_MAX 2000

// Safety limits (adjust per joint later)
#define ANGLE_MIN 0
#define ANGLE_MAX 180

// Watchdog timeout (ms)
#define COMMAND_TIMEOUT 200

// PWM pins (update to match your wiring)
const int servoPins[SERVO_COUNT] = {2, 3, 4, 5, 6, 7, 8, 9};

// ---------------- STATE ----------------

struct ServoState {
    float currentAngle;
    float targetAngle;
    float speed; // degrees per second
};

ServoState servos[SERVO_COUNT];

unsigned long lastCommandTime = 0;

// ---------------- UTIL ----------------

int angleToPulse(float angle) {
    angle = constrain(angle, ANGLE_MIN, ANGLE_MAX);
    return map(angle, 0, 180, PWM_MIN, PWM_MAX);
}

void writeServo(int pin, int pulseWidth) {
    digitalWrite(pin, HIGH);
    delayMicroseconds(pulseWidth);
    digitalWrite(pin, LOW);
}

// ---------------- INIT ----------------

void initServos() {
    for (int i = 0; i < SERVO_COUNT; i++) {
        pinMode(servoPins[i], OUTPUT);
        servos[i].currentAngle = 90;
        servos[i].targetAngle = 90;
        servos[i].speed = 60; // default deg/sec
    }
}

// ---------------- COMMAND PARSER ----------------
// Format: ID,ANGLE,SPEED\n
// Example: 0,120,50

void handleCommand(String cmd) {
    int id, angle, speed;

    if (sscanf(cmd.c_str(), "%d,%d,%d", &id, &angle, &speed) == 3) {
        if (id >= 0 && id < SERVO_COUNT) {
            servos[id].targetAngle = constrain(angle, ANGLE_MIN, ANGLE_MAX);
            servos[id].speed = max(1, speed);
            lastCommandTime = millis();
        }
    }
}

// ---------------- MOTION UPDATE ----------------

void updateMotion(float deltaTime) {
    for (int i = 0; i < SERVO_COUNT; i++) {
        float diff = servos[i].targetAngle - servos[i].currentAngle;
        float step = servos[i].speed * deltaTime;

        if (abs(diff) <= step) {
            servos[i].currentAngle = servos[i].targetAngle;
        } else {
            servos[i].currentAngle += (diff > 0 ? step : -step);
        }
    }
}

// ---------------- OUTPUT ----------------

void updateServos() {
    for (int i = 0; i < SERVO_COUNT; i++) {
        int pulse = angleToPulse(servos[i].currentAngle);
        writeServo(servoPins[i], pulse);
    }
}

// ---------------- WATCHDOG ----------------

void checkWatchdog() {
    if (millis() - lastCommandTime > COMMAND_TIMEOUT) {
        // Hold position (no sudden drop)
        for (int i = 0; i < SERVO_COUNT; i++) {
            servos[i].targetAngle = servos[i].currentAngle;
        }
    }
}

// ---------------- MAIN LOOP ----------------

String inputBuffer = "";
unsigned long lastUpdate = 0;

void setup() {
    Serial.begin(115200);
    initServos();
    lastCommandTime = millis();
}

void loop() {
    unsigned long now = millis();
    float deltaTime = (now - lastUpdate) / 1000.0;
    lastUpdate = now;

    // Read serial input
    while (Serial.available()) {
        char c = Serial.read();
        if (c == '\n') {
            handleCommand(inputBuffer);
            inputBuffer = "";
        } else {
            inputBuffer += c;
        }
    }

    checkWatchdog();
    updateMotion(deltaTime);
    updateServos();
}
