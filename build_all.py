"""
BUILD_ALL — Master build script for the Smart Train 3D Model.
Runs every component module and exports STEP + STL files.

Usage:
    python build_all.py

Requires: cadquery  (pip install cadquery)
    or via conda:  conda install -c cadquery cadquery
"""

import os
import sys
import time

# ── Ensure this directory is on the path ─────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

import parameters as P

OUTPUT_DIR = os.path.join(BASE_DIR, P.OUTPUT_DIR)
os.makedirs(OUTPUT_DIR, exist_ok=True)

MODULES = [
    ("02_internal_frame", "internal_frame",   "export"),
    ("03_body_shell",     "body_shell",        "export"),
    ("04_front_cab",      "front_cab",         "export"),
    ("05_roof",           "roof",              "export"),
    ("06_bogie",          "bogie",             "export"),
    ("07_wheel",          "wheel",             "export"),
    ("08_axle",           "axle",              "export"),
    ("09_bearing_housing","bearing_housing",   "export"),
    ("10_suspension",     "suspension",        "export"),
    ("11_brakes",         "brakes",            "export"),
    ("12_coupler",        "coupler",           "export"),
    ("13_pantograph",     "pantograph",        "export"),
    ("01_chassis",        "chassis",           "export"),
]


def build_all():
    print("=" * 60)
    print("  SMART TRAIN 3D MODEL — FULL BUILD")
    print(f"  Output: {OUTPUT_DIR}")
    print("=" * 60)

    failed = []
    t_start = time.time()

    for label, module_name, fn_name in MODULES:
        print(f"\n>> Building {label} ...")
        t0 = time.time()
        try:
            mod = __import__(module_name)
            # Re-load to pick up any changes
            import importlib
            mod = importlib.reload(mod)
            getattr(mod, fn_name)(out_dir=OUTPUT_DIR)
            print(f"    OK Done in {time.time()-t0:.1f}s")
        except Exception as e:
            print(f"    FAILED: {e}")
            import traceback
            traceback.print_exc()
            failed.append((label, str(e)))

    # ── Print summary ─────────────────────────────────────────
    elapsed = time.time() - t_start
    print("\n" + "=" * 60)
    print(f"  BUILD COMPLETE in {elapsed:.1f}s")

    files = sorted(os.listdir(OUTPUT_DIR))
    step_files = [f for f in files if f.endswith(".step")]
    stl_files  = [f for f in files if f.endswith(".stl")]

    print(f"\n  STEP files ({len(step_files)}):")
    for f in step_files:
        sz = os.path.getsize(os.path.join(OUTPUT_DIR, f)) / 1024
        print(f"    {f:45s}  {sz:8.1f} KB")

    print(f"\n  STL files ({len(stl_files)}):")
    for f in stl_files:
        sz = os.path.getsize(os.path.join(OUTPUT_DIR, f)) / 1024
        print(f"    {f:45s}  {sz:8.1f} KB")

    if failed:
        print(f"\n  WARNING: {len(failed)} component(s) FAILED:")
        for label, err in failed:
            print(f"    - {label}: {err}")
    else:
        print("\n  All components built successfully.")

    print("=" * 60)
    print(f"\n  Output directory: {OUTPUT_DIR}")
    print("  Import .step files into Onshape, Fusion 360, FreeCAD, etc.")
    print("  Slice .stl files with PrusaSlicer / Cura for FDM printing.")
    print("=" * 60)


if __name__ == "__main__":
    build_all()
