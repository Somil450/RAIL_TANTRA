# 🚂 Smart Train 3D — Complete Electric Locomotive Assembly Kit

> A fully parametric, 3D-printable modern electric train designed with **CadQuery**.
> The complete 3-car configuration (Locomotive + 2 Wagons) fits within **588 mm** total length.

---

## 📸 Preview
<img width="1470" height="605" alt="image" src="https://github.com/user-attachments/assets/02c6a729-359e-472d-a50d-48947c595f4f" />

> present in output/SMART_TRAIN_FINAL.step

<img width="1190" height="518" alt="image" src="https://github.com/user-attachments/assets/c39c046d-9162-4883-aa4f-ee6fff020535" />

> present in output/COMPLETE_TRAIN_V3_OPENROOF.step

![FINAL TRAIN — 3 Views](https://raw.githubusercontent.com/Somil450/smart_train_3d/main/output/FINAL_TRAIN.stl)


---

## 🎯 Design Goals

| Goal | Value |
|------|-------|
| Total assembled length | ≤ 600 mm → **588 mm** ✅ |
| Locomotive length | 200 mm |
| Each wagon length | 180 mm |
| Inter-vehicle gap | 14 mm (coupler space) |
| Body width | **102 mm (10.2 cm)** |
| Body height | **~102 mm (10.2 cm)** |
| Wheel diameter | **15 mm (1.5 cm)** |
| Roof | **OPEN** (accessible interior) |
| Wheel motion | Spinning (free on axle) |
| Bogie motion | Rotating pivot-pin (for curves) |
| Vehicle connection | Articulated drawbar + pivot bracket |

---

## 🏗️ Design & Architecture

### How we built it

The train was designed **iteratively** using Python + [CadQuery](https://cadquery.readthedocs.io/) — a parametric 3D CAD scripting library. All geometry is defined through master parameters at the top of each script, making it easy to resize any part.

#### Evolution of the design:

```
v1  →  Individual component files (chassis.py, wheel.py, etc.)
v2  →  Merged single-file assembly (COMPLETE_TRAIN_V2)
v3  →  Open roof, wider body (102mm) — COMPLETE_TRAIN_V3
v4  →  Separate movable-wheel files (TRAIN_BODY + WHEEL + AXLE)
v5  →  J-hook couplers, single merged file (FINAL_TRAIN)
v6  →  Full assembly kit: rotating bogies + pivot-drawbar couplers
```

### Key mechanical decisions

#### 1. Rotating Bogies (for cornering)
Each bogie has a **12 mm pivot pin** that sticks up through a **12.4 mm hole** in the chassis underframe. The 0.2 mm clearance per side lets the bogie swivel freely, so the train can navigate curves.

```
Chassis floor (Z = 0)
   ┌──────[12.4mm hole]──────┐
   │                         │
   └─────────────────────────┘
              ↕ swivels
   ┌──────[12.0mm pin]───────┐   ← bogie pivot pin
   │       BOGIE FRAME       │
   │  ┌─leg─┐         ┌─leg─┐│
   │  │axle │ ← → axle│     ││
   │  └─────┘         └─────┘│
   └─────────────────────────┘
        O   O           O   O    ← wheels (15mm dia)
```

#### 2. Articulated Drawbar Coupler (instead of rigid joints)
Between each pair of vehicles:

```
LOCO end ──[pivot bracket]──[drawbar]──[pivot bracket]── WAGON end
              ↑ 5mm pin                  ↑ 5mm pin
              ↓ 5.4mm fork hole          ↓ 5.4mm fork hole
```

- The **pivot bracket** mounts on the inner vehicle face with a 5 mm vertical pin
- The **drawbar** has fork holes (5.4 mm = 0.2 mm clearance → rotates freely)
- A thin mid-section on the drawbar acts as a **flex spring** for slight buffer action

#### 3. Spinning Wheels (FDM clearance)

| Component | Diameter | Fit type |
|-----------|----------|----------|
| Axle shaft | 5.0 mm | — |
| Bogie axle-box hole | 5.0 mm nominal | Press-fit (tight) |
| Wheel bore | 5.8 mm | +0.4 mm clearance → **spins freely** |
| Bogie pivot pin | 12.0 mm | — |
| Chassis pivot hole | 12.4 mm | +0.2 mm → **rotates freely** |

---

## 📁 File Structure

```
smart_train_3d/
│
├── 📄 README.md                  ← This file
├── 📄 requirements.txt           ← Python dependencies
│
├── 🐍 SCRIPTS — Build scripts (run these to generate STL/STEP)
│   ├── build_assembly_kit.py     ← ⭐ RECOMMENDED: Generates all 7 separate parts
│   ├── build_final_train.py      ← Single merged file (J-hooks, open roof)
│   ├── build_movable_wheels.py   ← Body + separate wheel + axle files
│   ├── build_complete_train_v3.py← Open roof, 102mm wide, single file
│   ├── build_complete_train_v2.py← Full closed train, single merged file
│   └── build_assembled_train.py  ← Earlier assembled version
│
├── 🐍 COMPONENT MODULES (used by early build scripts)
│   ├── parameters.py             ← All master dimensions
│   ├── chassis.py                ← Chassis underframe
│   ├── body_shell.py             ← Main body shell
│   ├── front_cab.py              ← Aerodynamic cab nose
│   ├── roof.py                   ← Roof panels + HVAC housings
│   ├── bogie.py                  ← Bogie frame geometry
│   ├── wheel.py                  ← Wheel disc + flange
│   ├── axle.py                   ← Axle shaft
│   ├── bearing_housing.py        ← Axle bearing blocks
│   ├── suspension.py             ← Suspension bolster
│   ├── brakes.py                 ← Brake shoe geometry
│   ├── coupler.py                ← Coupler head geometry
│   ├── pantograph.py             ← Roof pantograph structure
│   ├── internal_frame.py         ← Internal structural frame
│   └── TrainLayout.fs            ← Onshape FeatureScript (alternative CAD)
│
└── 📦 output/                    ← All generated STL and STEP files
    │
    ├── 🏆 FINAL / RECOMMENDED FILES
    │   ├── FINAL_TRAIN.stl       ← Complete train, J-hooks, open roof, 15mm wheels
    │   ├── FINAL_TRAIN.step      ← Same, in STEP format (Onshape/Fusion 360)
    │   ├── TRAIN_BODY.stl        ← Body only (no wheels) — for separate-parts printing
    │   ├── WHEEL_15mm.stl        ← Single 15mm wheel — print 24×
    │   └── AXLE_88mm.stl         ← Single axle — print 12×
    │
    ├── 🔄 VERSION HISTORY
    │   ├── COMPLETE_TRAIN_V3_OPENROOF.stl  ← V3: open roof, 102mm wide
    │   ├── COMPLETE_TRAIN_V3_OPENROOF.step
    │   ├── COMPLETE_TRAIN_V2.stl           ← V2: closed roof, 22 parts merged
    │   ├── COMPLETE_TRAIN_V2.step
    │   ├── SMART_TRAIN_COMPLETE.stl        ← V1: original assembled train
    │   └── SMART_TRAIN_COMPLETE.step
    │
    └── 🔩 INDIVIDUAL LOCO COMPONENTS (V1 separate parts)
        ├── 01_chassis.stl / .step
        ├── 02_internal_frame.stl / .step
        ├── 03_body_shell.stl / .step
        ├── 04_front_cab.stl / .step
        ├── 05_roof.stl / .step
        ├── 06_bogie.stl / .step
        ├── 07_wheel.stl / .step
        ├── 08_axle.stl / .step
        ├── 09_bearing_housing.stl / .step
        ├── 10_suspension.stl / .step
        ├── 11_brakes.stl / .step
        ├── 12_coupler.stl / .step
        └── 13_pantograph.stl / .step
```

---

## 🚀 How to Run It Yourself

### Prerequisites

- **Python 3.9+**  (tested on 3.10 and 3.11)
- **CadQuery 2.3+**

### Step 1 — Clone the repo

```bash
git clone https://github.com/Somil450/smart_train_3d.git
cd smart_train_3d
```

### Step 2 — Install dependencies

**Option A — pip (simplest):**
```bash
pip install -r requirements.txt
```

**Option B — conda (if pip fails on Windows):**
```bash
conda install -c conda-forge -c cadquery cadquery
```

### Step 3 — Generate the STL files

**To get the full final train in one file:**
```bash
python build_final_train.py
```
→ Outputs `output/FINAL_TRAIN.stl` and `output/FINAL_TRAIN.step`

**To get separate printable parts (recommended for assembly):**
```bash
python build_assembly_kit.py
```
→ Outputs `output/kit/` with 7 separate part files

**To get body + separate spinning wheels:**
```bash
python build_movable_wheels.py
```
→ Outputs `TRAIN_BODY.stl`, `WHEEL_15mm.stl`, `AXLE_88mm.stl`

### Step 4 — Open in 3D Viewer

On **Windows**, just double-click any `.stl` file — Windows 3D Viewer opens automatically.

Or import the `.step` file into:
- [Onshape](https://www.onshape.com) (free, browser-based)
- [Fusion 360](https://www.autodesk.com/products/fusion-360)
- [FreeCAD](https://www.freecad.org) (free, desktop)

---

## 🖨️ 3D Printing Guide

### Which file to print?

| Use case | File | Count |
|----------|------|-------|
| Quick single-piece print | `FINAL_TRAIN.stl` | 1× |
| Full assembly with spinning wheels | `TRAIN_BODY.stl` + `WHEEL_15mm.stl` + `AXLE_88mm.stl` | 1× + 24× + 12× |
| Full articulated kit (rotating bogies) | Run `build_assembly_kit.py` → print all 7 parts | See table below |

### Assembly kit print counts

| File | Part | Print |
|------|------|-------|
| `01_LOCO_BODY.stl` | Locomotive body (open top) | 1× |
| `02_WAGON_BODY.stl` | Wagon body (identical for both wagons) | 2× |
| `03_BOGIE_FRAME.stl` | Rotating bogie with pivot pin | 6× |
| `04_WHEEL_15mm.stl` | 15 mm wheel disc | 24× |
| `05_AXLE.stl` | 88 mm axle shaft | 12× |
| `06_PIVOT_BRACKET.stl` | Coupler mounting bracket | 4× |
| `07_DRAWBAR.stl` | Articulating drawbar (flex spring) | 2× |

### Recommended print settings

| Setting | Value |
|---------|-------|
| Layer height | 0.2 mm |
| Infill | 20–30 % |
| Perimeters | 3 |
| Material | PLA or PETG |
| Supports | Required for bogie legs and coupler brackets |
| Bed adhesion | Brim recommended |

### Assembly order

```
Step 1 → Press axle into bogie axle-box holes        (5mm shaft → 5mm hole, tight grip)
Step 2 → Slide 2 wheels onto each axle end            (5.8mm bore → spins on 5mm axle)
Step 3 → Insert bogie pivot pin up into chassis hole  (12mm pin → 12.4mm hole, swivels)
Step 4 → Mount pivot brackets on inner vehicle ends
Step 5 → Clip drawbar fork holes onto bracket pins    (5.4mm hole → 5mm pin, rotates)
Step 6 → Repeat for both inter-vehicle junctions
```

---

## 🔧 Customising Dimensions

All master parameters are at the top of each build script. Key ones:

```python
TW   = 102     # Body width (Y), mm
WD   = 15      # Wheel diameter, mm
GA   = 62      # Track gauge (wheel inner face to inner face), mm
LL   = 200     # Locomotive length, mm
WL   = 180     # Wagon length, mm
GAP  = 14      # Inter-vehicle gap, mm
WALL = 3.0     # Body wall thickness, mm
AZ   = -24     # Axle centre Z (below chassis), mm
```

Change any of these and re-run the script — all geometry rebuilds automatically.

---

## 📐 Final Dimensions

```
┌───────────────────────────────────────────────────────────────┐
│  LOCO (200mm)  │ 14mm │  WAGON 1 (180mm)  │ 14mm │  WAGON 2  │
│                │      │                   │      │  (180mm)  │
└───────────────────────────────────────────────────────────────┘
                         ◄────────── 588 mm total ────────────►

Width:  102 mm (10.2 cm)
Height: ~102 mm (10.2 cm)
Wheel:   15 mm diameter (1.5 cm)
```

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| [Python 3.10](https://www.python.org/) | Scripting language |
| [CadQuery 2.3](https://cadquery.readthedocs.io/) | Parametric 3D CAD kernel |
| [OCC (OpenCASCADE)](https://www.opencascade.com/) | Underlying BREP geometry engine |
| [Onshape](https://www.onshape.com) | Cloud CAD viewer / assembly |
| Windows 3D Viewer | Quick STL preview |

---

## 📋 GitHub Repo

🔗 **[https://github.com/Somil450/smart_train_3d](https://github.com/Somil450/smart_train_3d)**

---

## 📜 License

This project is open source — use, modify, and 3D-print freely. Attribution appreciated!
