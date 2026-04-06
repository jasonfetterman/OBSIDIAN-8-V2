OBSIDIAN‑8 V3
01_Mechanical/Mechanical_Layout.txt
Revision: V3.4
Status: Authoritative
Units: Metric (mm / kg)

------------------------------------------------------------
1. OVERVIEW
------------------------------------------------------------

Defines the physical mechanical layout of the OBSIDIAN‑8 octopod platform
(hybrid aluminum extrusion + 3D‑printed modular architecture).  
Serves as the master reference for CAD assembly, component placement, and mass alignment.

Target Footprint: 1143 mm (45 inches)  
Target Mass Range: 24 – 26 kg (operational configuration)  
Primary Structure: 3030 extrusion backbone + 2020 cross braces  
Reference Documents: /00_System_Definition/Geometry_Model.txt, Frame_Architecture.txt, Mass_and_CG_Model.txt  

------------------------------------------------------------
2. CHASSIS GEOMETRY
------------------------------------------------------------

Outer Diameter: ≈ 700 mm  
Coxa Mount Radius: ≈ 350 mm from center  
Foot Radius (Neutral Pose): ≈ 550 mm from center  

Leg Mount Positions — Eight equally spaced at 45° intervals:  
0° Front Leg1  45° Front‑Right Leg2  90° Right Leg3  135° Rear‑Right Leg4  
180° Rear Leg5  225° Rear‑Left Leg6  270° Left Leg7  315° Front‑Left Leg8  

Attachment: Printed CF Nylon leg brackets clamped to 3030 backbone rail using M6 fasteners and gusset plates.  

------------------------------------------------------------
3. STRUCTURAL FRAME
------------------------------------------------------------

Primary Load Ring: 3030 aluminum extrusion backbone (12‑segment ring).  
Cross Bracing: 2020 extrusion spokes forming rigid octagonal core.  
Top Plate: 3 mm aluminum sheet mounting battery and compute modules.  
Battery Tray: 3D‑printed or CNC‑aluminum tray center‑mounted for low Cg.  

Reinforcements: Printed and metal gussets at high‑torque leg brackets.  
Goal: maximize torsional stiffness while preserving modularity and low mass.  

------------------------------------------------------------
4. SERVO ORIENTATION
------------------------------------------------------------

Each leg uses a 3‑servo stack (Coxa, Femur, Tibia):  
- **Coxa Servo:** Horizontally mounted in printed coxa bracket (rotation around Z)  
- **Femur Servo:** Vertically mounted in printed beam (rotation around Y)  
- **Tibia Servo:** Inline mount in printed tibia section (extension control)  

Access Ports: Printed service holes permit horn and sensor access without major disassembly.  
Cable paths through brackets use strain‑relief mid‑segments.  

------------------------------------------------------------
5. CENTER OF GRAVITY AND MASS PLACEMENT
------------------------------------------------------------

Major Mass Elements: Battery, Compute modules, Power electronics.  
All placed centrally along X/Y axes and as low as practical (Z ≈ 0.42 m).  
Target Cg location within ± 50 mm of geometric center for neutral pose.  

Stable low Cg improves tripod gait, stair‑climbing performance, and roll margin.  
Reference: /01_Mechanical/Mass_and_CG_Model.txt  

------------------------------------------------------------
6. BATTERY PLACEMENT
------------------------------------------------------------

Battery Model: 24 V 30 Ah LiFePO₄ module.  
Mounting Tray: Under top chassis plate, centered in frame core.  
Isolation: Shock‑mounted QD tray with rubber bushings.  
Trunk Cable Route: through lower extrusion channel to Power Distribution Board.  

------------------------------------------------------------
7. HEAD MAST MOUNT
------------------------------------------------------------

Location: Chassis centerline.  
Height: 300 – 400 mm above backbone plane.  
Mount: 3D‑printed or aluminum mast column bolted to central plate.  
Isolation: Rubber grommets or bushings for vibration control.  

Carries: Sensor cluster (IMU + RGB/Depth Cameras + RTK Antenna).  

------------------------------------------------------------
8. ELECTRONICS BAY
------------------------------------------------------------

Location: Central interior of frame beneath top plate.  
Includes: Jetson Orin NX, Raspberry Pi 5, Teensy 4.1, Duet 3 6HC, and power modules.  

Mounting: Stacked electronics plates (printed or aluminum); ensure ≥ 5 mm air gap for airflow.  
Fasteners: M3 × 12 stainless bolts and M3 inserts per electronics spec.  

------------------------------------------------------------
9. COOLING SYSTEM
------------------------------------------------------------

Active cooling via two 80 mm PWM fans (Noctua or equivalent).  
Airflow: Bottom intake through electronic bay → top vent.  
Directed flow channels avoid dead zones around DC‑DC converters and Duet board.  
Temperature Cutoffs: warn at 55 °C, shutdown at 65 °C (based on Sensor Suite).  

------------------------------------------------------------
10. CABLE ROUTING
------------------------------------------------------------

Main Power Harness: Battery → BMS → DC‑DC converters → servo rails.  
Cable gauges: 6 AWG battery trunk, 8 AWG converter feeds, 10–12 AWG servo leads.  

Leg Harness Routing: through printed Coxa housings with strain‑relief loops.  
Use high‑flex silicone‑insulated robotics wire; avoid tight bend radii (< 30 mm).  
Reference: /02_Electrical/Wiring_Harness_Specification.txt  

------------------------------------------------------------
11. CAD ASSEMBLY SEQUENCE
------------------------------------------------------------

Recommended order:  
1. 3030 backbone ring assembly  
2. 2020 cross braces  
3. Printed leg brackets  
4. Coxa assemblies  
5. Femur assemblies  
6. Tibia assemblies  
7. Battery tray installation  
8. Electronics stack installation  
9. Head mast mount and sensor suite  

Sequence minimizes interference and alignment errors.  
All printed modules interchangeable without main chassis modification.  

------------------------------------------------------------
12. DESIGN NOTES (V3.4)
------------------------------------------------------------

- Hybrid extrusion/printed frame reduces mass and boosts torsional stiffness.  
- Modular printed parts allow rapid upgrade and field replacement.  
- All load points reinforced with gussets and corner brackets.  
- Verified neutral stance and Cg for tripod gait and stair stability.  
- Integration validated through FMEA, CM, and simulation testing.  

------------------------------------------------------------
END OF FILE
------------------------------------------------------------
