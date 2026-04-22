// servo_driver.cpp — REV C (16-Channel, Non-Blocking, Timer-Based PWM)

#include <Arduino.h>
#include <IntervalTimer.h>

// ---------------- CONFIG ----------------

#define SERVO_COUNT 16

// Pulse range (microseconds)
#define PWM_MIN 1000
#define PWM_MAX 2000

// Safety limits
#define ANGLE_MIN 10.0
#define ANGLE_MAX 170.0

// PWM timing
#define PWM_PERIOD_US 20000  // 50Hz
#define PWM_RESOLUTION_US 10 // timer step

// Watchdog
#define COMMAND_TIMEOUT 200  // ms

// Servo pins (Teensy PWM-capable pins)
const int servoPins[SERVO_COUNT] = {
    2,3,4,5,6,7,8,9,
    10,11,12,13,14,15,16,17
};

// ---------------- STATE ----------------

struct ServoState {
    float currentAngle;
    float targetAngle;
    float speed; // deg/sec
};

ServoState servos[SERVO_COUNT];

volatile int pulseWidths[SERVO_COUNT];

IntervalTimer pwmTimer;

unsigned long lastCommandTime = 0;

// ---------------- UTIL ----------------

int angleToPulse(float angle) {
    if (angle < ANGLE_MIN) angle = ANGLE_MIN;
    if (angle > ANGLE_MAX) angle = ANGLE_MAX;
    return (int)(PWM_MIN + (angle - ANGLE_MIN) * (PWM_MAX - PWM_MIN) / (ANGLE_MAX - ANGLE_MIN));
}

// ---------------- PWM ENGINE ----------------

volatile int currentChannel = 0;
volatile int pwmPhase = 0;

void pwmISR() {
    static unsigned long lastCycleStart = 0;

    if (pwmPhase == 0) {
        // Start of pulse
        digitalWrite(servoPins[currentChannel], HIGH);
        pwmPhase = 1;
    } else {
        // End of pulse
        digitalWrite(servoPins[currentChannel], LOW);

        currentChannel++;
        if (currentChannel >= SERVO_COUNT) {
            currentChannel = 0;

            // Wait remaining frame time
            unsigned long now = micros();
            unsigned long elapsed = now - lastCycleStart;
            if (elapsed < PWM_PERIOD_US) {
                delayMicroseconds(PWM_PERIOD_US - elapsed);
            }
            lastCycleStart = micros();
        }

        pwmPhase = 0;
    }

    pwmTimer.update(pulseWidths[currentChannel]);
}

// ---------------- INIT ----------------

void initServos() {
    for (int i = 0; i < SERVO_COUNT; i++) {
        pinMode(servoPins[i], OUTPUT);
        servos[i].currentAngle = 90.0;
        servos[i].targetAngle = 90.0;
        servos[i].speed = 80.0;
        pulseWidths[i] = angleToPulse(90.0);
    }

    pwmTimer.begin(pwmISR, PWM_RESOLUTION_US);
    lastCommandTime = millis();
}

// ---------------- COMMAND PARSER ----------------
// Format: ID,ANGLE,SPEED\n

String inputBuffer = "";

void handleCommand(String cmd) {
    int id;
    float angle, speed;

    if (sscanf(cmd.c_str(), "%d,%f,%f", &id, &angle, &speed) == 3) {
        if (id >= 0 && id < SERVO_COUNT) {
            servos[id].targetAngle = angle;
            servos[id].speed = max(1.0f, speed);
            lastCommandTime = millis();
        }
    }
}

// ---------------- MOTION UPDATE ----------------

void updateMotion(float dt) {
    for (int i = 0; i < SERVO_COUNT; i++) {
        float diff = servos[i].targetAngle - servos[i].currentAngle;
        float step = servos[i].speed * dt;

        if (abs(diff) <= step) {
            servos[i].currentAngle = servos[i].targetAngle;
        } else {
            servos[i].currentAngle += (diff > 0 ? step : -step);
        }

        pulseWidths[i] = angleToPulse(servos[i].currentAngle);
    }
}

// ---------------- WATCHDOG ----------------

void checkWatchdog() {
    if (millis() - lastCommandTime > COMMAND_TIMEOUT) {
        for (int i = 0; i < SERVO_COUNT; i++) {
            servos[i].targetAngle = servos[i].currentAngle;
        }
    }
}

// ---------------- MAIN ----------------

unsigned long lastUpdate = 0;

void setup() {
    Serial.begin(115200);
    initServos();
}

void loop() {
    unsigned long now = millis();
    float dt = (now - lastUpdate) / 1000.0;
    lastUpdate = now;

    // Read serial
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
    updateMotion(dt);
}
