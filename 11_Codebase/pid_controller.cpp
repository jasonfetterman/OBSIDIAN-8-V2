 // pid_controller.cpp
 // OBSIDIAN-8 V3 — REV D
 // PID controller implementation for joint control

#include <iostream>
#include <chrono>

class PIDController {
private:
    double kp;
    double ki;
    double kd;

    double integral;
    double last_error;
    std::chrono::steady_clock::time_point last_time;

public:
    PIDController(double kp_, double ki_, double kd_)
        : kp(kp_), ki(ki_), kd(kd_), integral(0.0), last_error(0.0) {
        last_time = std::chrono::steady_clock::now();
    }

    double compute(double setpoint, double measured) {
        auto now = std::chrono::steady_clock::now();
        std::chrono::duration<double> elapsed = now - last_time;
        double dt = elapsed.count();

        double error = setpoint - measured;
        integral += error * dt;
        double derivative = (dt > 0) ? (error - last_error) / dt : 0.0;

        double output = kp * error + ki * integral + kd * derivative;

        last_error = error;
        last_time = now;

        return output;
    }

    void reset() {
        integral = 0.0;
        last_error = 0.0;
        last_time = std::chrono::steady_clock::now();
    }
};

// -------------------- TEST LOOP --------------------
#ifdef TEST_PID
int main() {
    PIDController pid(1.0, 0.01, 0.05);
    double target = 30.0;
    double measured = 0.0;

    for(int i=0; i<100; i++) {
        double output = pid.compute(target, measured);
        measured += output * 0.1; // simulate response
        std::cout << "Step " << i << ": output=" << output << ", measured=" << measured << std::endl;
        std::this_thread::sleep_for(std::chrono::milliseconds(50));
    }
    return 0;
}
#endif
