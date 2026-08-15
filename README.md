# Smart Train 3D Model — README

## Overview

A complete, fully parametric, FDM-3D-printable model of a modern electric locomotive.
Built with **CadQuery** (Python CAD library). Exports STEP + STL files for every component.

---

## Project Structure

```
smart_train_3d/
├── parameters.py          ← Master parameters (edit here to resize everything)
├── build_all.py           ← Run this to build all components
├── chassis.py             ← 01: Main chassis
├── internal_frame.py      ← 02: Internal sub-frame
├── body_shell.py          ← 03: Main body shell
├── front_cab.py           ← 04: Front cab with windshield
├── roof.py                ← 05: Removable roof with HVAC
├── bogie.py               ← 06: Bogie frame (×2)
├── wheel.py               ← 07: Railway wheel (×8)
├── axle.py                ← 08: Axle with D-flat (×4)
├── bearing_housing.py     ← 09: Bearing housing (×8)
├── suspension.py          ← 10: Suspension tower (×8)
├── brakes.py              ← 11: Brake assembly (×4)
├── coupler.py             ← 12: Front/rear coupler (×2)
├── pantograph.py          ← 13: Roof pantograph (×1)
├── requirements.txt
└── output/                ← Generated STEP + STL files go here
```

---

## Master Dimensions

| Parameter            | Default  | Description                    |
|----------------------|----------|--------------------------------|
| TRAIN_LENGTH         | 420 mm   | Overall locomotive length      |
| TRAIN_WIDTH          | 70 mm    | Overall width                  |
| TRAIN_HEIGHT         | 95 mm    | Overall height (inc. roof eq.) |
| WHEEL_DIAMETER       | 22 mm    | Wheel tread diameter           |
| AXLE_DIAMETER        | 6 mm     | Axle shaft diameter            |
| BOGIE_WHEELBASE      | 60 mm    | Axle spacing within bogie      |
| BOGIE_SPACING        | 280 mm   | Bogie-to-bogie centre distance |
| BODY_WALL_THICKNESS  | 2.0 mm   | Shell wall thickness           |
| CHASSIS_THICKNESS    | 5.0 mm   | Chassis floor thickness        |

Edit `parameters.py` to change any value — all dependent geometry updates automatically.

---

## Installation

### Option 1 — pip (easiest on Windows Python 3.12)

```powershell
pip install cadquery
```

### Option 2 — Conda (most reliable, all platforms)

```bash
conda install -c cadquery cadquery
```

### Option 3 — Mamba (fast conda alternative)

```bash
mamba install -c cadquery cadquery
```

---

## Building the Model

```powershell
cd C:\Users\anand\.gemini\antigravity-ide\scratch\smart_train_3d
python build_all.py
```

Output files appear in `output/`:
- `01_chassis.step` / `.stl`
- `02_internal_frame.step` / `.stl`
- ... (all 13 components)

---

## Importing into Onshape

1. Open your Onshape document
2. **Insert → Upload** (or drag-and-drop) each `.step` file
3. Onshape converts STEP to native parts automatically
4. Create an Assembly and position each part
5. Add mates:
   - **Bogie pivot** → Revolute mate (vertical axis) for bogie rotation
   - **Wheels** → Revolute mate (horizontal axis) for rotation
   - **Roof** → Fasten mate (removable via edit)
   - **Couplers** → Fasten mate

---

## 3D Printing Guide

### Recommended Settings

| Part             | Material | Infill | Supports   | Orientation      |
|------------------|----------|--------|------------|------------------|
| Chassis          | PETG     | 30%    | None       | Flat (XY)        |
| Body shell       | PLA/PETG | 20%    | Yes (sides)| Right-side up    |
| Front cab        | PLA/PETG | 25%    | Yes        | Windshield up    |
| Roof             | PLA      | 15%    | None       | Crown up         |
| Bogie frame      | PETG     | 40%    | Yes        | Flat             |
| Wheels (×8)      | PLA      | 50%    | None       | Flat (spoke face)|
| Axles (×4)       | PETG     | 100%   | None       | Horizontal       |
| Bearing housing  | PLA      | 60%    | None       | Flange down      |
| Suspension       | TPU/PLA  | 40%    | None       | Vertical         |
| Brakes           | PLA      | 30%    | None       | Flat             |
| Couplers (×2)    | PETG     | 60%    | None       | Flat             |
| Pantograph       | PLA      | 25%    | None       | Base down        |

### Hardware Required

| Item                          | Qty | Size    |
|-------------------------------|-----|---------|
| M3 × 8mm screws (body–chassis)| 6   | M3      |
| M3 × 6mm screws (roof clips)  | 8   | M3      |
| M3 × 6mm screws (pantograph)  | 4   | M3      |
| M3 hex nuts                   | 18  | M3      |
| Miniature ball bearings       | 8   | 10×6×3mm|
| Compression springs (6mm OD)  | 8   | 6mm OD  |

---

## Assembly Order

1. Press bearings into bogie bearing saddle pockets
2. Slide axles through bearings
3. Press wheels onto axles (D-flat alignment)
4. Attach suspension towers to bogie frame
5. Mount bogie to chassis via pivot post
6. Attach brake assemblies to bogie mounting points
7. Place internal frame on chassis (screw M3×8)
8. Lower body shell onto chassis (screw M3×8)
9. Attach couplers (front/rear pin-in-pocket)
10. Clip roof panel onto body
11. Screw pantograph to roof pad

---

## License

This parametric train model is designed for personal/educational 3D printing.
No real-world railway branding or intellectual property is reproduced.
