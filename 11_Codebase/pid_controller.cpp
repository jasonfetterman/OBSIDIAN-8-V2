//
// pid_controller.cpp
// OBSIDIAN-8 V3 — REV D
// Implements PID control for precise servo angle tracking
//

#include <iostream>
#include <vector>
#include <chrono>
#include <thread>
#include "servo_interface.h"

struct PID {
    double kp;
    double ki;
    double kd;

    double integral;
    double last_error;

    PID(double _kp, double _ki, double _kd)
        : kp(_kp), ki(_ki), kd(_kd), integral(0.0), last_error(0.0) {}
};

class ServoPIDController {
public:
    ServoPIDController(size_t num_servos) {
        servos.resize(num_servos);
        pid_loops.resize(num_servos);
        for (size_t i = 0; i < num_servos; i++) {
            pid_loops[i] = PID(2.0, 0.01, 0.1);  // example gains
        }
    }

    void set_target(size_t index, double angle) {
        if (index < servos.size())
            servos[index] = angle;
    }

    void update() {
        for (size_t i = 0; i < servos.size(); i++) {
            double current_angle = ServoInterface::getAngle(i);  // read current servo
            double error = servos[i] - current_angle;

            PID &pid = pid_loops[i];
            pid.integral += error * dt();
            double derivative = (error - pid.last_error) / dt();

            double output = pid.kp * error + pid.ki * pid.integral + pid.kd * derivative;

            // Clamp output to servo limits
            if (output > 1.0) output = 1.0;
            if (output < -1.0) output = -1.0;

            ServoInterface::setAngle(i, current_angle + output);  // incremental adjustment

            pid.last_error = error;
        }
    }

private:
    std::vector<double> servos;       // target angles
    std::vector<PID> pid_loops;

    double dt() {
        return 0.02;  // 50 Hz
    }
};

// -------------------- TEST LOOP --------------------
int main() {
    ServoInterface::init();
    ServoPIDController controller(24);  // 24 servos for 8 legs

    // Example: all servos to 30 degrees (~0.5236 radians)
    for (size_t i = 0; i < 24; i++) {
        controller.set_target(i, 0.5236);
    }

    while (true) {
        controller.update();
        std::this_thread::sleep_for(std::chrono::milliseconds(20));
    }

    return 0;
}
