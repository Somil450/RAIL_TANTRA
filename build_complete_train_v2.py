"""
build_complete_train_v2.py
Complete modern electric train: LOCOMOTIVE + WAGON 1 + WAGON 2
Total assembled length: 580 mm (within 600 mm limit)
All parts pre-positioned. Single STEP + STL output.

Coordinate system:
  X = train length (front = +X)
  Y = train width  (left = +Y, right = -Y, center = 0)
  Z = vertical     (up = +Z, Z=0 = chassis bottom face)
"""
import cadquery as cq
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
os.makedirs(OUT, exist_ok=True)

# ═══════════════════════════════════════════════════════════
# MASTER PARAMETERS
# ═══════════════════════════════════════════════════════════
TW   = 72      # train body width (Y)
WD   = 20      # wheel diameter
WW   = 8       # wheel width (Y thickness)
FLD  = 2.5     # flange extra radius
AD   = 4       # axle shaft diameter
GA   = 46      # track gauge (distance between wheel inner faces)
AZ   = -20     # axle centre Z (below chassis bottom Z=0)
WALL = 2.5     # body wall thickness

# Locomotive
LL   = 200     # loco length
LBGX = 62      # loco bogie X offset from loco centre
LBWB = 44      # loco bogie wheelbase

# Wagon
WL   = 180     # wagon length
WBGX = 50      # wagon bogie X offset from wagon centre
WBWB = 38      # wagon bogie wheelbase

# Assembly
GAP  = 10      # inter-vehicle gap
CL   = 16      # coupler arm length

# Global X centres  (total = 200+10+180+10+180 = 580 mm)
LOX  = 190.0   # loco centre
W1X  = LOX - LL/2 - GAP - WL/2   # = -10.0
W2X  = W1X - WL/2 - GAP - WL/2   # = -200.0
TOTAL_LEN = LL + GAP + WL + GAP + WL  # 580 mm

# ═══════════════════════════════════════════════════════════
# WHEEL  (axis along Y, hub at X=0, Z=axle centre)
# ═══════════════════════════════════════════════════════════
def mk_wheel():
    """Wheel disc+flange, axis along Y, from Y=0 to Y=WW."""
    rim  = cq.Workplane("XZ").circle(WD/2).extrude(WW)
    flng = cq.Workplane("XZ").workplane(offset=-FLD).circle(WD/2 + FLD).extrude(FLD)
    hub  = cq.Workplane("XZ").circle(AD/2 + 1.5).extrude(WW)
    return rim.union(flng).union(hub)

# ═══════════════════════════════════════════════════════════
# AXLE + WHEEL PAIR
# ═══════════════════════════════════════════════════════════
def mk_axle_pair(cx, az=AZ):
    """Axle shaft + left (positive Y) + right (negative Y) wheels."""
    tot_y = GA + WW * 2 + 6          # total axle length in Y  = 68 mm
    shaft = (cq.Workplane("XZ")
             .circle(AD / 2)
             .extrude(tot_y)
             .translate((cx, -tot_y / 2, az)))
    lw = mk_wheel().translate((cx,  GA / 2,          az))  # left
    rw = mk_wheel().translate((cx, -(GA / 2 + WW),   az))  # right
    return shaft.union(lw).union(rw)

# ═══════════════════════════════════════════════════════════
# BOGIE FRAME + 2 AXLE PAIRS
# ═══════════════════════════════════════════════════════════
def mk_bogie(cx, bwb, az=AZ):
    bL = bwb + 24   # frame X extent
    bY = TW + 4     # frame Y extent (slightly wider than body)
    bH = 10         # frame Z height
    # Frame sits just below chassis (Z=-1 to Z=-11)
    frame = (cq.Workplane("XY")
             .box(bL, bY, bH)
             .translate((cx, 0, -bH / 2 - 1)))
    # Side bolster beams
    for ys in [1, -1]:
        beam = (cq.Workplane("XY")
                .box(bL - 6, 5, bH - 4)
                .translate((cx, ys * bY / 2, -bH / 2 - 1)))
        frame = frame.union(beam)
    # Pivot post going up into chassis
    pivot = (cq.Workplane("XY")
             .circle(8)
             .extrude(14)
             .translate((cx, 0, 0)))
    frame = frame.union(pivot)
    # Axle pairs
    a1 = mk_axle_pair(cx + bwb / 2, az)
    a2 = mk_axle_pair(cx - bwb / 2, az)
    return frame.union(a1).union(a2)

# ═══════════════════════════════════════════════════════════
# COUPLER
# ═══════════════════════════════════════════════════════════
def mk_coupler(face_x, sign):
    """Draft coupler extending sign*CL from face_x."""
    coupler_z = AZ + WD / 2 + 10          # Z centre of coupler body
    arm  = (cq.Workplane("XY")
            .box(CL, 12, 14)
            .translate((face_x + sign * CL / 2, 0, coupler_z)))
    head = (cq.Workplane("XY")
            .box(8, 18, 12)
            .translate((face_x + sign * (CL + 4), 0, coupler_z)))
    pin  = (cq.Workplane("XZ")
            .circle(3)
            .extrude(8)
            .translate((face_x + sign * CL, -4, coupler_z)))
    return arm.union(head).union(pin)

# ═══════════════════════════════════════════════════════════
# LOCOMOTIVE CHASSIS
# ═══════════════════════════════════════════════════════════
def mk_loco_chassis(ox):
    """Ribbed underframe."""
    base = (cq.Workplane("XY")
            .box(LL, TW, 6)
            .translate((ox, 0, 3)))
    # Bogie cutouts (pockets for bogies to swing)
    for bx in [ox + LBGX, ox - LBGX]:
        cut = (cq.Workplane("XY")
               .box(LBWB + 26, TW - 10, 4)
               .translate((bx, 0, 0)))
        base = base.cut(cut)
    # Longitudinal ribs
    for ys in [0.25, -0.25]:
        rib = (cq.Workplane("XY")
               .box(LL - 20, 4, 4)
               .translate((ox, ys * TW, 5)))
        base = base.union(rib)
    return base

# ═══════════════════════════════════════════════════════════
# LOCOMOTIVE BODY SHELL
# ═══════════════════════════════════════════════════════════
def mk_loco_body(ox):
    H  = 70     # body height above chassis
    BZ = 6      # chassis top Z

    # ── Main body (rear section) ─────────────────────────
    main_l  = LL - 44        # 156 mm
    main_cx = ox - 22        # shifted toward rear
    outer = (cq.Workplane("XY")
             .box(main_l, TW, H)
             .translate((main_cx, 0, H / 2 + BZ)))
    inner = (cq.Workplane("XY")
             .box(main_l - 5, TW - WALL * 2, H - WALL)
             .translate((main_cx, 0, H / 2 + BZ + WALL / 2)))
    shell = outer.cut(inner)

    # ── Aerodynamic front cab ─────────────────────────────
    cab_l  = 46
    cab_cx = ox + LL / 2 - cab_l / 2
    cab_h  = H + 10
    cab_outer = (cq.Workplane("XY")
                 .box(cab_l, TW, cab_h)
                 .translate((cab_cx, 0, cab_h / 2 + BZ)))
    cab_inner = (cq.Workplane("XY")
                 .box(cab_l - 5, TW - WALL * 2, cab_h - WALL)
                 .translate((cab_cx, 0, cab_h / 2 + BZ + WALL / 2)))
    cab = cab_outer.cut(cab_inner)

    # Nose slope: cut upper-front triangle from cab
    nose_cut = (cq.Workplane("XY")
                .box(cab_l, TW + 4, cab_h * 0.45)
                .translate((cab_cx + cab_l * 0.12, 0, cab_h * 0.78 + BZ)))
    cab = cab.cut(nose_cut)
    shell = shell.union(cab)

    # ── Windshield ────────────────────────────────────────
    ws = (cq.Workplane("XY")
          .box(WALL + 4, TW - 16, H * 0.32)
          .translate((ox + LL / 2 - WALL / 2 - 1, 0, H * 0.68 + BZ)))
    shell = shell.cut(ws)

    # ── Side windows (main body) ──────────────────────────
    win_xi = [-100, -74, -48, -22, 4]
    for xi in win_xi:
        for ys in [1, -1]:
            w = (cq.Workplane("XY")
                 .box(20, WALL + 4, 17)
                 .translate((ox + xi, ys * TW / 2, H * 0.58 + BZ)))
            shell = shell.cut(w)

    # ── Ventilation grilles ───────────────────────────────
    for xi in [-128, -112]:
        for ys in [1, -1]:
            g = (cq.Workplane("XY")
                 .box(10, WALL + 4, 12)
                 .translate((ox + xi, ys * TW / 2, H * 0.3 + BZ)))
            shell = shell.cut(g)

    # ── Headlights (front) ────────────────────────────────
    for ys in [1, -1]:
        hl = (cq.Workplane("XZ")
              .circle(4)
              .extrude(WALL + 3)
              .translate((ox + LL / 2, ys * (TW / 2 - 12), H * 0.22 + BZ)))
        shell = shell.union(hl)

    # ── Side door (each side) ─────────────────────────────
    for xi in [20]:
        for ys in [1, -1]:
            door = (cq.Workplane("XY")
                    .box(WALL + 4, 22, 36)
                    .translate((ox + xi, ys * TW / 2, H * 0.3 + BZ)))
            shell = shell.cut(door)

    return shell

# ═══════════════════════════════════════════════════════════
# LOCOMOTIVE ROOF
# ═══════════════════════════════════════════════════════════
def mk_loco_roof(ox):
    H = 70; BZ = 6; RH = 14
    roof_z = H + BZ + RH / 2
    roof = (cq.Workplane("XY")
            .box(LL - 28, TW - 4, RH)
            .translate((ox - 14, 0, roof_z)))
    # Equipment housings
    for xi, lx, ly in [(-55, 34, 24), (20, 28, 20)]:
        eq = (cq.Workplane("XY")
              .box(lx, ly, RH - 2)
              .translate((ox + xi, 0, roof_z + RH - 2)))
        roof = roof.union(eq)
    return roof

# ═══════════════════════════════════════════════════════════
# PANTOGRAPH
# ═══════════════════════════════════════════════════════════
def mk_pantograph(ox):
    H = 70; BZ = 6; RH = 14
    base_z = H + BZ + RH * 2 - 2
    # Base insulators
    base = (cq.Workplane("XY")
            .box(48, 26, 5)
            .translate((ox + 30, 0, base_z + 2.5)))
    # Lower diamond arms
    for xs in [1, -1]:
        arm = (cq.Workplane("XZ")
               .box(3, 24, 3)
               .translate((ox + 30 + xs * 8, 10, base_z + 15)))
        base = base.union(arm)
        arm2 = (cq.Workplane("XZ")
                .box(3, 24, 3)
                .translate((ox + 30 + xs * 8, -10, base_z + 15)))
        base = base.union(arm2)
    # Upper contact strip
    strip = (cq.Workplane("XY")
             .box(64, 5, 4)
             .translate((ox + 30, 0, base_z + 28)))
    # Strip support horns
    for xs in [1, -1]:
        horn = (cq.Workplane("XY")
                .box(4, 5, 8)
                .translate((ox + 30 + xs * 30, 0, base_z + 24)))
        strip = strip.union(horn)
    return base.union(strip)

# ═══════════════════════════════════════════════════════════
# WAGON CHASSIS
# ═══════════════════════════════════════════════════════════
def mk_wagon_chassis(wx):
    base = (cq.Workplane("XY")
            .box(WL, TW, 5)
            .translate((wx, 0, 2.5)))
    for bx in [wx + WBGX, wx - WBGX]:
        cut = (cq.Workplane("XY")
               .box(WBWB + 22, TW - 10, 3)
               .translate((bx, 0, 0.5)))
        base = base.cut(cut)
    # Cross-ribs
    for xi in [-40, 0, 40]:
        rib = (cq.Workplane("XY")
               .box(5, TW - 12, 4)
               .translate((wx + xi, 0, 4.5)))
        base = base.union(rib)
    return base

# ═══════════════════════════════════════════════════════════
# WAGON BODY SHELL
# ═══════════════════════════════════════════════════════════
def mk_wagon_body(wx):
    H  = 66    # body height
    BZ = 5     # chassis top Z

    outer = (cq.Workplane("XY")
             .box(WL, TW, H)
             .translate((wx, 0, H / 2 + BZ)))
    inner = (cq.Workplane("XY")
             .box(WL - 4, TW - WALL * 2, H - WALL)
             .translate((wx, 0, H / 2 + BZ + WALL / 2)))
    shell = outer.cut(inner)

    # Passenger windows (6 per side, evenly spaced)
    win_xs = [-65, -39, -13, 13, 39, 65]
    for xi in win_xs:
        for ys in [1, -1]:
            w = (cq.Workplane("XY")
                 .box(22, WALL + 4, 24)
                 .translate((wx + xi, ys * TW / 2, H * 0.62 + BZ)))
            shell = shell.cut(w)

    # End doors (each end, centred)
    for xs in [1, -1]:
        door = (cq.Workplane("XY")
                .box(WALL + 4, 28, 38)
                .translate((wx + xs * WL / 2, 0, H * 0.38 + BZ)))
        shell = shell.cut(door)

    # Side doors (centre of wagon)
    for ys in [1, -1]:
        sdoor = (cq.Workplane("XY")
                 .box(20, WALL + 4, 38)
                 .translate((wx, ys * TW / 2, H * 0.38 + BZ)))
        shell = shell.cut(sdoor)

    # Blue accent stripe (raised feature on side)
    for ys in [1, -1]:
        stripe = (cq.Workplane("XY")
                  .box(WL - 6, WALL, 6)
                  .translate((wx, ys * (TW / 2 + WALL / 2), H * 0.28 + BZ)))
        shell = shell.union(stripe)

    return shell

# ═══════════════════════════════════════════════════════════
# WAGON ROOF
# ═══════════════════════════════════════════════════════════
def mk_wagon_roof(wx):
    H = 66; BZ = 5; RH = 12
    roof_z = H + BZ + RH / 2
    roof = (cq.Workplane("XY")
            .box(WL - 4, TW - 4, RH)
            .translate((wx, 0, roof_z)))
    # AC units
    for xi in [-55, -18, 18, 55]:
        ac = (cq.Workplane("XY")
              .box(20, 18, 9)
              .translate((wx + xi, 0, roof_z + RH - 1)))
        roof = roof.union(ac)
    return roof

# ═══════════════════════════════════════════════════════════
# ASSEMBLE COMPLETE TRAIN
# ═══════════════════════════════════════════════════════════
print("=" * 60)
print("  BUILDING COMPLETE TRAIN ASSEMBLY")
print(f"  Configuration: LOCO ({LL}mm) + WAGON1 ({WL}mm) + WAGON2 ({WL}mm)")
print(f"  Total length:  {TOTAL_LEN} mm (limit: 600 mm)")
print(f"  Width: {TW} mm  |  Height: ~100 mm")
print("=" * 60)
print(f"  LOCO  centre X = {LOX}")
print(f"  W1    centre X = {W1X}")
print(f"  W2    centre X = {W2X}")
print()

parts = []

# ── LOCOMOTIVE ────────────────────────────────────────────
print(" [01] Locomotive chassis...")
parts.append(mk_loco_chassis(LOX))

print(" [02] Locomotive body shell...")
parts.append(mk_loco_body(LOX))

print(" [03] Locomotive roof...")
parts.append(mk_loco_roof(LOX))

print(" [04] Pantograph...")
parts.append(mk_pantograph(LOX))

print(" [05] Locomotive front bogie + wheels...")
parts.append(mk_bogie(LOX + LBGX, LBWB))

print(" [06] Locomotive rear bogie + wheels...")
parts.append(mk_bogie(LOX - LBGX, LBWB))

print(" [07] Locomotive front coupler...")
parts.append(mk_coupler(LOX + LL / 2, +1))

print(" [08] Locomotive rear coupler...")
parts.append(mk_coupler(LOX - LL / 2, -1))

# ── WAGON 1 ───────────────────────────────────────────────
print(" [09] Wagon 1 chassis...")
parts.append(mk_wagon_chassis(W1X))

print(" [10] Wagon 1 body shell...")
parts.append(mk_wagon_body(W1X))

print(" [11] Wagon 1 roof...")
parts.append(mk_wagon_roof(W1X))

print(" [12] Wagon 1 front bogie + wheels...")
parts.append(mk_bogie(W1X + WBGX, WBWB))

print(" [13] Wagon 1 rear bogie + wheels...")
parts.append(mk_bogie(W1X - WBGX, WBWB))

print(" [14] Wagon 1 front coupler...")
parts.append(mk_coupler(W1X + WL / 2, +1))

print(" [15] Wagon 1 rear coupler...")
parts.append(mk_coupler(W1X - WL / 2, -1))

# ── WAGON 2 ───────────────────────────────────────────────
print(" [16] Wagon 2 chassis...")
parts.append(mk_wagon_chassis(W2X))

print(" [17] Wagon 2 body shell...")
parts.append(mk_wagon_body(W2X))

print(" [18] Wagon 2 roof...")
parts.append(mk_wagon_roof(W2X))

print(" [19] Wagon 2 front bogie + wheels...")
parts.append(mk_bogie(W2X + WBGX, WBWB))

print(" [20] Wagon 2 rear bogie + wheels...")
parts.append(mk_bogie(W2X - WBGX, WBWB))

print(" [21] Wagon 2 front coupler...")
parts.append(mk_coupler(W2X + WL / 2, +1))

print(" [22] Wagon 2 rear coupler...")
parts.append(mk_coupler(W2X - WL / 2, -1))

# ── MERGE ALL PARTS ───────────────────────────────────────
print(f"\nMerging {len(parts)} parts into single solid...")
train = parts[0]
for i, p in enumerate(parts[1:], 1):
    print(f"  [{i + 1:02d}/{len(parts)}] merging...")
    try:
        train = train.union(p)
    except Exception as e:
        print(f"    WARNING: skipped part {i + 1} — {e}")

# ── EXPORT ────────────────────────────────────────────────
STEP = os.path.join(OUT, "COMPLETE_TRAIN_V2.step")
STL  = os.path.join(OUT, "COMPLETE_TRAIN_V2.stl")

print("\nExporting STEP...")
cq.exporters.export(train, STEP)
print(f"  → {STEP}")

print("Exporting STL...")
cq.exporters.export(train, STL)
print(f"  → {STL}")

step_kb = os.path.getsize(STEP) / 1024
stl_kb  = os.path.getsize(STL)  / 1024

print()
print("=" * 60)
print(f"  COMPLETE_TRAIN_V2.step   {step_kb:>8.1f} KB")
print(f"  COMPLETE_TRAIN_V2.stl    {stl_kb:>8.1f} KB")
print(f"  Total length:  {TOTAL_LEN} mm")
print(f"  Parts merged:  {len(parts)}")
print("=" * 60)
print("DONE! Copy to Desktop and open in Windows 3D Viewer.")
