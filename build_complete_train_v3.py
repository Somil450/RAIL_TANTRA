"""
build_complete_train_v3.py
Complete modern electric train: LOCOMOTIVE + WAGON 1 + WAGON 2

UPDATED DIMENSIONS:
  Length : 580 mm (58 cm)  — loco 200 + gap 10 + wagon 180 + gap 10 + wagon 180
  Width  : 102 mm (10.2 cm)
  Height : ~102 mm (10.2 cm)
  Roof   : OPEN (no roof panels — interior accessible from top)
"""
import cadquery as cq
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
os.makedirs(OUT, exist_ok=True)

# ═══════════════════════════════════════════════════════════
# MASTER PARAMETERS
# ═══════════════════════════════════════════════════════════
TW   = 102     # ← UPDATED: train body width (Y) = 10.2 cm
WD   = 24      # wheel diameter (scaled up for wider body)
WW   = 10      # wheel width
FLD  = 3       # flange extra radius
AD   = 5       # axle shaft diameter
GA   = 60      # track gauge (wider for 102mm body)
AZ   = -24     # axle centre Z (below chassis bottom Z=0)
WALL = 3.0     # body wall thickness (slightly thicker for wider body)

# Locomotive
LL   = 200     # loco length (unchanged)
LBGX = 62      # loco bogie X offset from loco centre
LBWB = 44      # loco bogie wheelbase

# Wagon
WL   = 180     # wagon length (unchanged)
WBGX = 50      # wagon bogie X offset from wagon centre
WBWB = 38      # wagon bogie wheelbase

# Assembly
GAP  = 10      # inter-vehicle gap
CL   = 16      # coupler arm length

# Global X centres  (total = 200+10+180+10+180 = 580 mm)
LOX  = 190.0
W1X  = LOX - LL/2 - GAP - WL/2   # = -10.0
W2X  = W1X - WL/2 - GAP - WL/2   # = -200.0
TOTAL_LEN = LL + GAP + WL + GAP + WL  # 580 mm

# ═══════════════════════════════════════════════════════════
# WHEEL
# ═══════════════════════════════════════════════════════════
def mk_wheel():
    rim  = cq.Workplane("XZ").circle(WD/2).extrude(WW)
    flng = cq.Workplane("XZ").workplane(offset=-FLD).circle(WD/2 + FLD).extrude(FLD)
    hub  = cq.Workplane("XZ").circle(AD/2 + 2).extrude(WW)
    return rim.union(flng).union(hub)

# ═══════════════════════════════════════════════════════════
# AXLE + WHEEL PAIR
# ═══════════════════════════════════════════════════════════
def mk_axle_pair(cx, az=AZ):
    tot_y = GA + WW * 2 + 8
    shaft = (cq.Workplane("XZ")
             .circle(AD / 2)
             .extrude(tot_y)
             .translate((cx, -tot_y / 2, az)))
    lw = mk_wheel().translate((cx,  GA / 2,        az))
    rw = mk_wheel().translate((cx, -(GA / 2 + WW), az))
    return shaft.union(lw).union(rw)

# ═══════════════════════════════════════════════════════════
# BOGIE FRAME + 2 AXLE PAIRS
# ═══════════════════════════════════════════════════════════
def mk_bogie(cx, bwb, az=AZ):
    bL = bwb + 26
    bY = TW + 4
    bH = 12
    frame = (cq.Workplane("XY")
             .box(bL, bY, bH)
             .translate((cx, 0, -bH / 2 - 1)))
    for ys in [1, -1]:
        beam = (cq.Workplane("XY")
                .box(bL - 6, 6, bH - 4)
                .translate((cx, ys * bY / 2, -bH / 2 - 1)))
        frame = frame.union(beam)
    pivot = (cq.Workplane("XY")
             .circle(10)
             .extrude(16)
             .translate((cx, 0, 0)))
    frame = frame.union(pivot)
    a1 = mk_axle_pair(cx + bwb / 2, az)
    a2 = mk_axle_pair(cx - bwb / 2, az)
    return frame.union(a1).union(a2)

# ═══════════════════════════════════════════════════════════
# COUPLER
# ═══════════════════════════════════════════════════════════
def mk_coupler(face_x, sign):
    cz = AZ + WD / 2 + 12
    arm  = cq.Workplane("XY").box(CL, 14, 16).translate((face_x + sign * CL / 2, 0, cz))
    head = cq.Workplane("XY").box(10, 20, 14).translate((face_x + sign * (CL + 5), 0, cz))
    pin  = cq.Workplane("XZ").circle(4).extrude(10).translate((face_x + sign * CL, -5, cz))
    return arm.union(head).union(pin)

# ═══════════════════════════════════════════════════════════
# LOCOMOTIVE CHASSIS
# ═══════════════════════════════════════════════════════════
def mk_loco_chassis(ox):
    base = cq.Workplane("XY").box(LL, TW, 7).translate((ox, 0, 3.5))
    for bx in [ox + LBGX, ox - LBGX]:
        cut = cq.Workplane("XY").box(LBWB + 28, TW - 14, 5).translate((bx, 0, 0.5))
        base = base.cut(cut)
    for ys in [0.28, -0.28]:
        rib = cq.Workplane("XY").box(LL - 24, 5, 5).translate((ox, ys * TW, 6))
        base = base.union(rib)
    return base

# ═══════════════════════════════════════════════════════════
# LOCOMOTIVE BODY SHELL  (OPEN TOP)
# ═══════════════════════════════════════════════════════════
def mk_loco_body(ox):
    H  = 74     # body height above chassis
    BZ = 7      # chassis top Z

    # Main body
    main_l  = LL - 46
    main_cx = ox - 23
    outer = cq.Workplane("XY").box(main_l, TW, H).translate((main_cx, 0, H/2 + BZ))
    # Inner cut goes full height — makes top OPEN
    inner = cq.Workplane("XY").box(main_l - 6, TW - WALL*2, H + 4).translate((main_cx, 0, H/2 + BZ + WALL/2 + 2))
    shell = outer.cut(inner)

    # Front cab (aerodynamic)
    cab_l = 48; cab_cx = ox + LL/2 - cab_l/2; cab_h = H + 12
    cab_o = cq.Workplane("XY").box(cab_l, TW, cab_h).translate((cab_cx, 0, cab_h/2 + BZ))
    # Open top cab
    cab_i = cq.Workplane("XY").box(cab_l - 6, TW - WALL*2, cab_h + 4).translate((cab_cx, 0, cab_h/2 + BZ + WALL/2 + 2))
    cab = cab_o.cut(cab_i)

    # Nose slope cut
    nose_cut = cq.Workplane("XY").box(cab_l, TW + 4, cab_h * 0.42).translate(
        (cab_cx + cab_l * 0.13, 0, cab_h * 0.80 + BZ))
    cab = cab.cut(nose_cut)
    shell = shell.union(cab)

    # Windshield
    ws = cq.Workplane("XY").box(WALL + 4, TW - 20, H * 0.30).translate(
        (ox + LL/2 - WALL/2 - 1, 0, H * 0.68 + BZ))
    shell = shell.cut(ws)

    # Side windows
    for xi in [-96, -68, -40, -12, 16]:
        for ys in [1, -1]:
            w = cq.Workplane("XY").box(22, WALL + 4, 20).translate(
                (ox + xi, ys * TW/2, H * 0.56 + BZ))
            shell = shell.cut(w)

    # Ventilation grilles
    for xi in [-132, -115]:
        for ys in [1, -1]:
            g = cq.Workplane("XY").box(12, WALL + 4, 14).translate(
                (ox + xi, ys * TW/2, H * 0.30 + BZ))
            shell = shell.cut(g)

    # Headlights
    for ys in [1, -1]:
        hl = cq.Workplane("XZ").circle(5).extrude(WALL + 3).translate(
            (ox + LL/2, ys * (TW/2 - 16), H * 0.22 + BZ))
        shell = shell.union(hl)

    # Side door indent
    for ys in [1, -1]:
        door = cq.Workplane("XY").box(WALL + 4, 28, 42).translate(
            (ox + 18, ys * TW/2, H * 0.30 + BZ))
        shell = shell.cut(door)

    # Blue stripe (raised on sides)
    for ys in [1, -1]:
        stripe = cq.Workplane("XY").box(main_l - 6, WALL, 8).translate(
            (main_cx, ys * (TW/2 + WALL/2), H * 0.28 + BZ))
        shell = shell.union(stripe)

    return shell

# ═══════════════════════════════════════════════════════════
# PANTOGRAPH (stays — visible from open top)
# ═══════════════════════════════════════════════════════════
def mk_pantograph(ox):
    H = 74; BZ = 7
    base_z = H + BZ + 2
    base  = cq.Workplane("XY").box(52, 30, 5).translate((ox + 28, 0, base_z + 2.5))
    for xs in [1, -1]:
        a = cq.Workplane("XZ").box(3, 28, 3).translate((ox + 28 + xs * 9, 10, base_z + 16))
        b = cq.Workplane("XZ").box(3, 28, 3).translate((ox + 28 + xs * 9, -10, base_z + 16))
        base = base.union(a).union(b)
    strip = cq.Workplane("XY").box(68, 5, 4).translate((ox + 28, 0, base_z + 30))
    for xs in [1, -1]:
        horn = cq.Workplane("XY").box(4, 5, 9).translate((ox + 28 + xs * 32, 0, base_z + 26))
        strip = strip.union(horn)
    return base.union(strip)

# ═══════════════════════════════════════════════════════════
# WAGON CHASSIS
# ═══════════════════════════════════════════════════════════
def mk_wagon_chassis(wx):
    base = cq.Workplane("XY").box(WL, TW, 6).translate((wx, 0, 3))
    for bx in [wx + WBGX, wx - WBGX]:
        cut = cq.Workplane("XY").box(WBWB + 24, TW - 14, 4).translate((bx, 0, 0.5))
        base = base.cut(cut)
    for xi in [-40, 0, 40]:
        rib = cq.Workplane("XY").box(6, TW - 14, 5).translate((wx + xi, 0, 5.5))
        base = base.union(rib)
    return base

# ═══════════════════════════════════════════════════════════
# WAGON BODY SHELL  (OPEN TOP)
# ═══════════════════════════════════════════════════════════
def mk_wagon_body(wx):
    H  = 70    # body height
    BZ = 6     # chassis top Z

    outer = cq.Workplane("XY").box(WL, TW, H).translate((wx, 0, H/2 + BZ))
    # Inner cut taller than outer → OPEN TOP
    inner = cq.Workplane("XY").box(WL - 6, TW - WALL*2, H + 4).translate(
        (wx, 0, H/2 + BZ + WALL/2 + 2))
    shell = outer.cut(inner)

    # Passenger windows — 6 per side, evenly spaced
    for xi in [-65, -39, -13, 13, 39, 65]:
        for ys in [1, -1]:
            w = cq.Workplane("XY").box(24, WALL + 4, 26).translate(
                (wx + xi, ys * TW/2, H * 0.60 + BZ))
            shell = shell.cut(w)

    # End doors
    for xs in [1, -1]:
        d = cq.Workplane("XY").box(WALL + 4, 32, 44).translate(
            (wx + xs * WL/2, 0, H * 0.38 + BZ))
        shell = shell.cut(d)

    # Side doors (centre)
    for ys in [1, -1]:
        sd = cq.Workplane("XY").box(24, WALL + 4, 44).translate(
            (wx, ys * TW/2, H * 0.38 + BZ))
        shell = shell.cut(sd)

    # Blue accent stripe
    for ys in [1, -1]:
        stripe = cq.Workplane("XY").box(WL - 8, WALL, 8).translate(
            (wx, ys * (TW/2 + WALL/2), H * 0.26 + BZ))
        shell = shell.union(stripe)

    return shell

# ═══════════════════════════════════════════════════════════
# BUILD COMPLETE ASSEMBLY
# ═══════════════════════════════════════════════════════════
print("=" * 62)
print("  COMPLETE TRAIN V3 — OPEN ROOF EDITION")
print(f"  Length : {TOTAL_LEN} mm ({TOTAL_LEN/10:.1f} cm)")
print(f"  Width  : {TW} mm ({TW/10:.1f} cm)")
print(f"  Height : ~102 mm (10.2 cm)")
print(f"  Roof   : OPEN (no roof panels)")
print("=" * 62)

parts = []

# LOCOMOTIVE
print(" [01] Loco chassis...")
parts.append(mk_loco_chassis(LOX))
print(" [02] Loco body (open top)...")
parts.append(mk_loco_body(LOX))
print(" [03] Pantograph (visible from open top)...")
parts.append(mk_pantograph(LOX))
print(" [04] Loco front bogie + wheels...")
parts.append(mk_bogie(LOX + LBGX, LBWB))
print(" [05] Loco rear bogie + wheels...")
parts.append(mk_bogie(LOX - LBGX, LBWB))
print(" [06] Loco front coupler...")
parts.append(mk_coupler(LOX + LL/2, +1))
print(" [07] Loco rear coupler...")
parts.append(mk_coupler(LOX - LL/2, -1))

# WAGON 1
print(" [08] Wagon 1 chassis...")
parts.append(mk_wagon_chassis(W1X))
print(" [09] Wagon 1 body (open top)...")
parts.append(mk_wagon_body(W1X))
print(" [10] Wagon 1 front bogie + wheels...")
parts.append(mk_bogie(W1X + WBGX, WBWB))
print(" [11] Wagon 1 rear bogie + wheels...")
parts.append(mk_bogie(W1X - WBGX, WBWB))
print(" [12] Wagon 1 front coupler...")
parts.append(mk_coupler(W1X + WL/2, +1))
print(" [13] Wagon 1 rear coupler...")
parts.append(mk_coupler(W1X - WL/2, -1))

# WAGON 2
print(" [14] Wagon 2 chassis...")
parts.append(mk_wagon_chassis(W2X))
print(" [15] Wagon 2 body (open top)...")
parts.append(mk_wagon_body(W2X))
print(" [16] Wagon 2 front bogie + wheels...")
parts.append(mk_bogie(W2X + WBGX, WBWB))
print(" [17] Wagon 2 rear bogie + wheels...")
parts.append(mk_bogie(W2X - WBGX, WBWB))
print(" [18] Wagon 2 front coupler...")
parts.append(mk_coupler(W2X + WL/2, +1))
print(" [19] Wagon 2 rear coupler...")
parts.append(mk_coupler(W2X - WL/2, -1))

print(f"\nMerging {len(parts)} parts...")
train = parts[0]
for i, p in enumerate(parts[1:], 1):
    print(f"  [{i+1:02d}/{len(parts)}]...")
    try:
        train = train.union(p)
    except Exception as e:
        print(f"    WARNING: skipped — {e}")

STEP = os.path.join(OUT, "COMPLETE_TRAIN_V3_OPENROOF.step")
STL  = os.path.join(OUT, "COMPLETE_TRAIN_V3_OPENROOF.stl")

print("\nExporting STEP..."); cq.exporters.export(train, STEP)
print("Exporting STL..."); cq.exporters.export(train, STL)

sk = os.path.getsize(STEP)/1024; stk = os.path.getsize(STL)/1024
print(f"\n{'='*62}")
print(f"  COMPLETE_TRAIN_V3_OPENROOF.step   {sk:>8.1f} KB")
print(f"  COMPLETE_TRAIN_V3_OPENROOF.stl    {stk:>8.1f} KB")
print(f"  Length : {TOTAL_LEN} mm | Width: {TW} mm | Open Roof: YES")
print(f"{'='*62}")
print("DONE!")
