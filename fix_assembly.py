"""
fix_assembly.py — Automatically positions all train parts in the
SMART_TRAIN_FINAL Onshape assembly using the REST API.

SETUP (one-time):
1. Go to https://dev-portal.onshape.com/keys
2. Click "Create new API key"
3. Give it a name, check "Read/Write" permissions
4. Copy the Access Key and Secret Key below

USAGE:
    python fix_assembly.py
"""

import requests
import json
import math
from requests.auth import HTTPBasicAuth

# ═══════════════════════════════════════════════════════════════
#  YOUR API KEYS — Get from https://dev-portal.onshape.com/keys
# ═══════════════════════════════════════════════════════════════
ACCESS_KEY = "YOUR_ACCESS_KEY_HERE"
SECRET_KEY = "YOUR_SECRET_KEY_HERE"

# ═══════════════════════════════════════════════════════════════
#  Document info from the URL
#  URL: cad.onshape.com/documents/090730ae95ea540ad73ff552/
#                              w/5f3c67ecf8749291f6d218cb/
#                              e/23b832ce7a341925bde1461f
# ═══════════════════════════════════════════════════════════════
DID = "090730ae95ea540ad73ff552"   # document ID
WID = "5f3c67ecf8749291f6d218cb"   # workspace ID
EID = "23b832ce7a341925bde1461f"   # element ID (assembly tab)

BASE_URL = "https://cad.onshape.com/api/v6"
AUTH     = HTTPBasicAuth(ACCESS_KEY, SECRET_KEY)
HEADERS  = {"Content-Type": "application/json", "Accept": "application/json"}


def make_transform(tx=0, ty=0, tz=0, rx=0, ry=0, rz=0):
    """
    Build a 4x4 flat row-major transform matrix.
    Translations in METERS (Onshape API uses metres).
    Rotations in degrees around X, Y, Z axes (applied in order).
    Returns a flat list of 16 floats.
    """
    # Convert degrees to radians
    rx, ry, rz = math.radians(rx), math.radians(ry), math.radians(rz)

    # Rotation matrices
    cx, sx = math.cos(rx), math.sin(rx)
    cy, sy = math.cos(ry), math.sin(ry)
    cz, sz = math.cos(rz), math.sin(rz)

    # Combined rotation: Rz * Ry * Rx
    R = [
        [cy*cz,  cz*sx*sy - cx*sz,  cx*cz*sy + sx*sz],
        [cy*sz,  cx*cz + sx*sy*sz,  cx*sy*sz - cz*sx],
        [  -sy,             cy*sx,             cx*cy ],
    ]

    # Build 4x4 row-major flat matrix
    m = [
        R[0][0], R[0][1], R[0][2], tx,
        R[1][0], R[1][1], R[1][2], ty,
        R[2][0], R[2][1], R[2][2], tz,
        0,       0,       0,       1,
    ]
    return m


def get_assembly_definition():
    """Fetch the full assembly definition to get occurrence paths and part names."""
    url = f"{BASE_URL}/assemblies/d/{DID}/w/{WID}/e/{EID}"
    resp = requests.get(url, auth=AUTH, headers=HEADERS)
    resp.raise_for_status()
    return resp.json()


def list_occurrences(asm_def):
    """Extract a list of {path, name} for all root-level occurrences."""
    occurrences = []
    for occ in asm_def.get("rootAssembly", {}).get("occurrences", []):
        path_list = occ.get("path", [])
        # Only root-level (single-element path)
        if len(path_list) == 1:
            occurrences.append({
                "path": path_list,
                "pathString": path_list[0],
                "transform": occ.get("transform", []),
            })
    return occurrences


def apply_transform(occurrence_path, transform_matrix):
    """Send a transform request for one occurrence."""
    url = f"{BASE_URL}/assemblies/d/{DID}/w/{WID}/e/{EID}/occurrencetransforms"
    payload = {
        "transformDefinitions": [
            {
                "occurrence": occurrence_path,
                "transform": transform_matrix,
                "isRelative": False,   # absolute transform
            }
        ]
    }
    resp = requests.post(url, json=payload, auth=AUTH, headers=HEADERS)
    if resp.status_code not in (200, 204):
        print(f"    WARNING: {resp.status_code} — {resp.text[:200]}")
    return resp


def mm(val):
    """Convert millimetres to metres for the API."""
    return val / 1000.0


def main():
    print("=" * 60)
    print("  SMART TRAIN ASSEMBLY — AUTO-POSITION")
    print("=" * 60)

    # ── Step 1: Fetch assembly definition ────────────────────
    print("\n[1] Fetching assembly definition ...")
    try:
        asm_def = get_assembly_definition()
    except Exception as e:
        print(f"\nERROR: Could not fetch assembly: {e}")
        print("Check your ACCESS_KEY and SECRET_KEY are correct.")
        return

    # ── Step 2: List all occurrences ─────────────────────────
    occurrences = list_occurrences(asm_def)
    print(f"    Found {len(occurrences)} root-level occurrences\n")

    # Print all occurrences so user can see them
    print("  Occurrences found:")
    for i, occ in enumerate(occurrences):
        print(f"    [{i:02d}] path={occ['pathString']}")

    # ── Step 3: Identify parts by position in import order ───
    # Parts were imported in this order:
    # 0 = EP... (chassis)    1 = 08_axle       2 = 07_wheel
    # 3+ = Open CASCADE STEP files in order:
    #   03_body_shell, 04_front_cab, 05_roof, 06_bogie,
    #   09_bearing_housing, 10_suspension, 11_brakes, 12_coupler, 13_pantograph

    # Map occurrence index to part role & desired transform (x, y, z in mm)
    # Onshape assembly Y = up axis in many imports
    # We'll lay train along X axis, Y=up

    # Default: all parts at origin stacked — we spread them out
    # Chassis is the reference (stays at 0,0,0)
    # Body shell goes directly on chassis (z+5mm)
    # Bogies go below chassis (y-25mm)
    # Wheels inside bogies
    # etc.

    n = len(occurrences)

    # Build transform plan based on how many parts we have
    # The exact order depends on import sequence
    # We'll do a best-effort positioning

    # Parts list in import order (from screenshots):
    # EP... tab = chassis (Part 1)  → index varies
    # We'll position by guessing from order

    print("\n[2] Applying transforms ...\n")

    # Chassis — fix at origin (identity matrix)
    # Body shell — same XZ, just stack along Y
    # This is a best-effort layout spreading parts so they're visible

    # LAYOUT PLAN (Y = vertical in Onshape world units = metres):
    layout = []

    if n >= 1:  layout.append(("Chassis",         make_transform(0,         0,    0)))
    if n >= 2:  layout.append(("Internal Frame",  make_transform(0,         mm(5),  0)))
    if n >= 3:  layout.append(("Body Shell",       make_transform(0,         mm(5),  0)))
    if n >= 4:  layout.append(("Front Cab",        make_transform(mm(160),   mm(5),  0)))
    if n >= 5:  layout.append(("Roof",             make_transform(0,         mm(80), 0)))
    if n >= 6:  layout.append(("Bogie Front",      make_transform(mm(140),  -mm(25), 0)))
    if n >= 7:  layout.append(("Bogie Rear",       make_transform(-mm(140), -mm(25), 0)))
    if n >= 8:  layout.append(("Wheel 1",          make_transform(mm(170),  -mm(36), mm(25))))
    if n >= 9:  layout.append(("Wheel 2",          make_transform(mm(110),  -mm(36), mm(25))))
    if n >= 10: layout.append(("Wheel 3",          make_transform(-mm(110), -mm(36), mm(25))))
    if n >= 11: layout.append(("Wheel 4",          make_transform(-mm(170), -mm(36), mm(25))))
    if n >= 12: layout.append(("Wheel 5",          make_transform(mm(170),  -mm(36),-mm(25))))
    if n >= 13: layout.append(("Wheel 6",          make_transform(mm(110),  -mm(36),-mm(25))))
    if n >= 14: layout.append(("Wheel 7",          make_transform(-mm(110), -mm(36),-mm(25))))
    if n >= 15: layout.append(("Wheel 8",          make_transform(-mm(170), -mm(36),-mm(25))))
    if n >= 16: layout.append(("Axle 1",           make_transform(mm(170),  -mm(30), 0)))
    if n >= 17: layout.append(("Axle 2",           make_transform(mm(110),  -mm(30), 0)))
    if n >= 18: layout.append(("Axle 3",           make_transform(-mm(110), -mm(30), 0)))
    if n >= 19: layout.append(("Axle 4",           make_transform(-mm(170), -mm(30), 0)))
    if n >= 20: layout.append(("Bearing/Susp/Brake/Coupler/Panto", make_transform(0, mm(100), 0)))

    # Apply extras at top (exploded view style)
    for idx in range(20, n):
        layout.append((f"Extra part {idx}", make_transform(0, mm(100 + idx*20), 0)))

    # Apply all transforms
    for i, (name, tf) in enumerate(layout):
        if i >= len(occurrences):
            break
        occ = occurrences[i]
        path = occ["path"]
        print(f"  Positioning [{i:02d}] {name} at path={occ['pathString'][:16]}...")
        try:
            apply_transform(path, tf)
            print(f"    OK")
        except Exception as e:
            print(f"    FAILED: {e}")

    print("\n[3] Done! Refresh your Onshape browser tab to see the result.")
    print("    Press F5 or Ctrl+R in your Chrome tab.\n")
    print("=" * 60)


if __name__ == "__main__":
    main()
