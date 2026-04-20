#include <iostream>
#include <chrono>
#include <thread>
#include <cstdlib>

float read_voltage() {
    // TODO: replace with real ADC read
    return 12.5f + static_cast<float>(rand() % 100) / 100.0f;
}

float read_current() {
    // TODO: replace with real sensor
    return 2.0f + static_cast<float>(rand() % 50) / 100.0f;
}

int main() {
    while (true) {
        float voltage = read_voltage();
        float current = read_current();

        std::cout << "{";
        std::cout << "\"voltage\":" << voltage << ",";
        std::cout << "\"current\":" << current;
        std::cout << "}" << std::endl;

        std::this_thread::sleep_for(std::chrono::milliseconds(200));
    }
}
