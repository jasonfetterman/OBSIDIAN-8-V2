# OBSIDIAN-8 V3

OBSIDIAN-8 is a large-format autonomous octopod robotics platform designed to function as a command unit for a distributed swarm of smaller robotic agents.

Primary capabilities:

• Autonomous terrain traversal  
• Environmental mapping (SLAM)  
• Swarm coordination  
• Autonomous docking and charging  
• AI perception and navigation  

---

# System Overview

The system is divided into several major subsystems:

Mechanical Platform  
Electrical Power System  
Compute Stack  
Sensor Suite  
Swarm Communication Network  

Full architecture documentation:

docs/architecture_overview.md  
docs/system_architecture_diagram.md  

---

# Hardware Summary

Full Bill of Materials:

00_System_Definition/OBSIDIAN8_MASTER_BOM_REV_B.md

Major components:

Compute:
- NVIDIA Jetson Orin NX 16GB
- Raspberry Pi 5
- Teensy 4.1

Actuation:
- 24 × AGFRC A86BHMW brushless HV servos

Battery:
- 24V 30Ah LiFePO4

Sensors:
- Intel RealSense D455
- Luxonis OAK-D Pro
- Slamtec RPLidar S2
- VectorNav VN-100 IMU
- 6 × Sony IMX477 cameras

Networking:
- Ubiquiti UniFi U6 Mesh

---

# Mechanical Design

Mechanical architecture:

01_Mechanical/OBSIDIAN8_MECHANICAL_LAYOUT.md

Leg geometry:

03_Control_Architecture/LEG_KINEMATICS_SPEC.md

Key parameters:

Coxa: 70 mm  
Femur: 210 mm  
Tibia: 260 mm  

---

# Electrical System

Power architecture:

02_Electrical/POWER_DISTRIBUTION_DIAGRAM.md

Power analysis:

02_Electrical/Power_Budget_Analysis.txt

Battery:

24V 30Ah LiFePO4

Power rails:

• 8V servo rail  
• 12V sensor rail  
• 5V logic rail  

---

# Perception System

Sensor architecture:

05_Perception/HEAD_MODULE_V1.md

Sensors include:

Depth camera  
AI vision camera  
360° lidar  
IMU  
6 situational awareness cameras  

---

# Swarm Architecture

Swarm coordination:

04_Autonomy/SWARM_CONTROL_ARCHITECTURE.md

Communication:

WiFi 6 mesh network

Software framework:

ROS2 DDS messaging

---

# Build Guide

Assembly instructions:

docs/build_guide.md

Build phases:

1 Mechanical assembly  
2 Electrical integration  
3 Sensor installation  
4 Software deployment  

---

# Repository Structure

Repository structure documentation:

docs/repository_structure.md

---

# Project Roadmap

docs/project_roadmap.md