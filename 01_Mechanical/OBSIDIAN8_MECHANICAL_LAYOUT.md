# OBSIDIAN-8 MECHANICAL LAYOUT (V1)

## Overview

This document defines the physical mechanical layout of the OBSIDIAN‑8
octopod platform. It establishes the core geometry used when assembling
the robot in CAD.

Target Platform Size: 45 inch footprint (1143 mm)

Target Mass: 27--30 kg

Primary Structure: 3030 aluminum extrusion ring chassis.

------------------------------------------------------------------------

# Chassis Geometry

Outer Diameter: \~700 mm

Coxa Mount Radius: \~350 mm from center

Foot Radius (neutral stance): \~550 mm from center

Leg Mount Positions: 8 equally spaced positions at 45° intervals.

Example layout:

Front Leg1 -- 0°

Front‑Right Leg2 -- 45°

Right Leg3 -- 90°

Rear‑Right Leg4 -- 135°

Rear Leg5 -- 180°

Rear‑Left Leg6 -- 225°

Left Leg7 -- 270°

Front‑Left Leg8 -- 315°

------------------------------------------------------------------------

# Structural Frame

Primary Load Ring: 3030 aluminum extrusion

Cross Bracing: 2020 aluminum extrusion

Top Plate: 3 mm aluminum sheet

Battery Tray: 3 mm aluminum plate mounted centrally.

Purpose: Keeps center of gravity low.

------------------------------------------------------------------------

# Servo Orientation

Each leg uses:

Coxa Servo: Mounted horizontally inside coxa housing.

Femur Servo: Mounted vertically inside femur box beam.

Tibia Servo: Mounted inline with tibia segment.

Servo Access: Design service openings so horns can be accessed without
full disassembly.

------------------------------------------------------------------------

# Center of Gravity

Major mass components:

Battery Compute hardware Power electronics

These should be mounted close to the center of the chassis.

Target CG position: Within 50 mm of chassis center.

Low CG improves stability when walking.

------------------------------------------------------------------------

# Battery Placement

Battery: 24V 30Ah LiFePO4

Recommended Location: Directly under the main chassis plate.

Mounting: Shock‑isolated battery tray.

------------------------------------------------------------------------

# Head Mast Mount

Location: Center of robot body.

Height: 300--400 mm above chassis.

Mounting Method:

Aluminum mast column Bolted to central frame plate.

Vibration Isolation: Rubber bushings recommended.

------------------------------------------------------------------------

# Electronics Bay

Location: Central interior chassis area.

Components:

Jetson Orin NX Raspberry Pi 5 Teensy 4.1 Duet 3 6HC DC‑DC converters

Recommended Mounting:

Stacked electronics plates.

Ensure airflow between layers.

------------------------------------------------------------------------

# Cooling System

Active Cooling:

2 × 80 mm Noctua fans

Airflow Path:

Bottom intake Top exhaust vents

Purpose:

Prevent heat buildup from: servos DC‑DC converters compute modules

------------------------------------------------------------------------

# Cable Routing

Main Power Harness:

Battery → DC‑DC converters → servo rails.

Recommended cable gauges:

6 AWG main battery trunk 8 AWG converter feeds 10‑12 AWG servo leads

Leg Cable Routing:

Route wires through coxa housing. Add strain relief at rotating joints.

Recommended wire:

High‑flex silicone robotics cable.

------------------------------------------------------------------------

# CAD Assembly Notes

Model order recommended:

1.  Chassis ring
2.  Leg mount brackets
3.  Coxa assemblies
4.  Femur assemblies
5.  Tibia assemblies
6.  Battery tray
7.  Electronics stack
8.  Head mast

This order prevents interference errors during assembly.
