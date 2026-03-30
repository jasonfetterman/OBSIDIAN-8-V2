//
// kinematics.h
// OBSIDIAN-8 V3 — REV D
// Centralized forward and inverse kinematics for 3-DOF legs
//

#ifndef KINEMATICS_H
#define KINEMATICS_H

#include <vector>
#include <cmath>

namespace Kinematics {

// Leg dimensions (meters)
constexpr double COXA = 0.05;
constexpr double FEMUR = 0.15;
constexpr double TIBIA = 0.15;

// Inverse Kinematics (x, y, z in meters)
// Returns vector of angles: [coxa, femur, tibia] in radians
inline std::vector<double> inverse_kinematics(double x, double y, double z) {
    std::vector<double> angles(3, 0.0);

    // Coxa angle
    angles[0] = atan2(y, x);

    // Distance from coxa joint
    double r = sqrt(x*x + y*y) - COXA;
    double s = z;

    // Law of cosines for tibia
    double D = (r*r + s*s - FEMUR*FEMUR - TIBIA*TIBIA) / (2 * FEMUR * TIBIA);
    if (D > 1.0) D = 1.0;
    if (D < -1.0) D = -1.0;

    angles[2] = acos(D);  // tibia

    // Femur angle
    angles[1] = atan2(s, r) - atan2(TIBIA * sin(angles[2]), FEMUR + TIBIA * cos(angles[2]));

    return angles;
}

// Forward Kinematics
// Input: joint angles [coxa, femur, tibia] in radians
// Returns: end effector position [x, y, z] in meters
inline std::vector<double> forward_kinematics(double coxa, double femur, double tibia) {
    double xh = COXA + FEMUR * cos(femur) + TIBIA * cos(femur + tibia);
    double zh = FEMUR * sin(femur) + TIBIA * sin(femur + tibia);

    double x = xh * cos(coxa);
    double y = xh * sin(coxa);
    double z = zh;

    return {x, y, z};
}

}  // namespace Kinematics

#endif // KINEMATICS_H
