"""
build_movable_wheels.py

Generates SEPARATE printable STL parts so wheels physically spin:

  OUTPUT FILES:
  ┌─────────────────────────────────────────────────────────┐
  │ TRAIN_BODY.stl     - Full body (loco+wagons+bogies)    │
  │                      Print: 1×                          │
  │ WHEEL_15mm.stl     - Single 15mm wheel with bore       │
  │                      Print: 24× (8 wheels per vehicle) │
  │ AXLE.stl           - Single axle shaft                 │
  │                      Print: 12× (4 axles per vehicle)  │
  └─────────────────────────────────────────────────────────┘

CLEARANCES (FDM-safe):
  Axle shaft = 5.0 mm
  Axle hole in bogie (press fit) = 5.0 mm nominal  → tight grip
  Wheel bore (spinning fit) = 5.8 mm → 0.4mm clearance per side → spins freely

ASSEMBLY:
  1. Print all parts
  2. Press axle into bogie axle-box holes (tight fit)
  3. Slide 2 wheels onto each axle end (spin freely)
  4. Secure wheel with a tiny drop of CA glue on outer end if needed
"""
import cadquery as cq
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
os.makedirs(OUT, exist_ok=True)

# ═══════════════════════════════════════════════════════════
# PARAMETERS
# ═══════════════════════════════════════════════════════════
TW   = 102     # body width
WD   = 15      # ← wheel diameter 1.5 cm
FLD  = 2.0     # flange extra radius
WW   = 9       # wheel width (Y)
AD   = 5.0     # axle shaft diameter
BORE = 5.8     # wheel bore diameter (spinning clearance: +0.4mm per side)
GA   = 62      # track gauge (wheel inner face to inner face)
WALL = 3.0

# Y positions:
#   left wheel inner face  at Y = +GA/2 = +31
#   right wheel inner face at Y = -(GA/2) = -31
#   axle total Y span      = GA + WW*2 + 8 = 88mm

# Bogie heights (Z axis, Z=0 = chassis bottom)
BOGIE_TOP_Z = -2    # just below chassis
BOGIE_H     = 10    # main bogie frame height
BOGIE_BOT_Z = BOGIE_TOP_Z - BOGIE_H   # = -12

# Axle-box legs (hang from bogie down to axle level)
AZ          = -24   # axle centre Z (wheel radius 7.5 + 2mm clearance below bogie bottom)
# → wheel bottom (rail) = AZ - WD/2 = -24 - 7.5 = -31.5 mm below chassis

# Locomotive
LL   = 200
LBGX = 62    # loco bogie X offset from loco centre
LBWB = 44    # loco bogie wheelbase (X between 2 axles)

# Wagon
WL   = 180
WBGX = 50
WBWB = 38

GAP  = 10
CL   = 16
LOX  = 190.0
W1X  = LOX - LL/2 - GAP - WL/2
W2X  = W1X - WL/2 - GAP - WL/2
TOTAL_LEN = 580

# ═══════════════════════════════════════════════════════════
# PART A: SINGLE WHEEL (separate printable part)
#   axis along Y, disc in XZ plane
# ═══════════════════════════════════════════════════════════
def mk_wheel_part():
    """
    Single 15 mm diameter wheel.
    Bore = 5.8 mm (spins on 5 mm axle).
    Print 24× total.
    """
    # Rim disc
    rim  = cq.Workplane("XZ").circle(WD/2).extrude(WW)
    # Flange on inner side (at Y=0, the assembly-inner face)
    flng = (cq.Workplane("XZ")
            .workplane(offset=-FLD)
            .circle(WD/2 + FLD)
            .extrude(FLD))
    # Hub reinforcement
    hub  = (cq.Workplane("XZ")
            .circle(BORE/2 + 2)
            .extrude(WW))
    # Bore hole (spinning fit on axle)
    bore = (cq.Workplane("XZ")
            .workplane(offset=-FLD - 0.5)
            .circle(BORE/2)
            .extrude(WW + FLD + 1.5))  # goes full depth incl. flange
    wheel = rim.union(flng).union(hub).cut(bore)
    return wheel


# ═══════════════════════════════════════════════════════════
# PART B: SINGLE AXLE (separate printable part)
#   shaft fits in bogie axle-box holes (press fit)
#   wheels slide on each end (spinning)
# ═══════════════════════════════════════════════════════════
def mk_axle_part():
    """
    Single axle shaft + retaining caps.
    Shaft diam = 5 mm.  Length = GA + WW*2 + 8 = 88 mm.
    Caps (diam 7 mm) at each end stop wheels from sliding off.
    Print 12× total.
    """
    shaft_len  = GA + WW * 2 + 8    # 88 mm total
    cap_r      = AD/2 + 1.0          # 3.5 mm radius cap (> BORE/2=2.9 → retains wheel)

    shaft = (cq.Workplane("XZ")
             .circle(AD/2)
             .extrude(shaft_len)
             .translate((0, -shaft_len/2, 0)))

    # Retaining caps at both ends
    cap_l = (cq.Workplane("XZ")
              .circle(cap_r)
              .extrude(2.5)
              .translate((0, shaft_len/2, 0)))
    cap_r_part = (cq.Workplane("XZ")
                  .circle(cap_r)
                  .extrude(2.5)
                  .translate((0, -shaft_len/2 - 2.5, 0)))

    return shaft.union(cap_l).union(cap_r_part)


# ═══════════════════════════════════════════════════════════
# BOGIE FRAME WITH AXLE-BOX HOLES (no wheels, no axles)
# ═══════════════════════════════════════════════════════════
def mk_bogie_frame(cx, bwb):
    """
    Bogie frame with two axle-box pairs.
    Each axle-box has a 5.0 mm bore for press-fit axle.
    """
    bL  = bwb + 28
    bY  = TW + 6
    bH  = BOGIE_H

    # Main frame box (just below chassis)
    frame = (cq.Workplane("XY")
             .box(bL, bY, bH)
             .translate((cx, 0, BOGIE_BOT_Z + bH/2)))

    # Cross members (visual detail)
    for ax_x in [cx + bwb/2, cx - bwb/2]:
        cm = (cq.Workplane("XY")
              .box(10, bY - 8, bH - 4)
              .translate((ax_x, 0, BOGIE_BOT_Z + bH/2)))
        frame = frame.union(cm)

    # Axle-box legs: hang from bogie bottom down to axle level
    leg_h  = abs(AZ) - abs(BOGIE_BOT_Z) + WD/2 - 1   # reach just above wheel top
    leg_h  = max(leg_h, 6)
    leg_w  = AD + 8   # enough material around the bore
    leg_bY = 10       # leg Y thickness

    for ax_x in [cx + bwb/2, cx - bwb/2]:
        # Left axle box
        lleg = (cq.Workplane("XY")
                .box(leg_w, leg_bY, leg_h)
                .translate((ax_x, GA/2 + WW/2, BOGIE_BOT_Z - leg_h/2)))
        # Right axle box
        rleg = (cq.Workplane("XY")
                .box(leg_w, leg_bY, leg_h)
                .translate((ax_x, -(GA/2 + WW/2), BOGIE_BOT_Z - leg_h/2)))
        frame = frame.union(lleg).union(rleg)

        # Cut axle bore through both axle boxes (Y direction, at Z=AZ)
        bore_len = GA + WW * 2 + leg_bY * 2 + 10
        axle_bore = (cq.Workplane("XZ")
                     .circle(AD/2)          # 5 mm nominal → press fit
                     .extrude(bore_len)
                     .translate((ax_x, -bore_len/2, AZ)))
        frame = frame.cut(axle_bore)

    # Pivot post (connects bogie to chassis)
    pivot = (cq.Workplane("XY")
             .circle(11)
             .extrude(18)
             .translate((cx, 0, 0)))
    frame = frame.union(pivot)

    return frame


# ═══════════════════════════════════════════════════════════
# COUPLER
# ═══════════════════════════════════════════════════════════
def mk_coupler(face_x, sign):
    cz = AZ + WD/2 + 12
    arm  = cq.Workplane("XY").box(CL, 14, 16).translate((face_x + sign*CL/2, 0, cz))
    head = cq.Workplane("XY").box(10, 20, 14).translate((face_x + sign*(CL+5), 0, cz))
    return arm.union(head)


# ═══════════════════════════════════════════════════════════
# LOCOMOTIVE CHASSIS
# ═══════════════════════════════════════════════════════════
def mk_loco_chassis(ox):
    base = cq.Workplane("XY").box(LL, TW, 7).translate((ox, 0, 3.5))
    for bx in [ox+LBGX, ox-LBGX]:
        cut = cq.Workplane("XY").box(LBWB+30, TW-16, 5).translate((bx, 0, 1))
        base = base.cut(cut)
    for ys in [0.28, -0.28]:
        rib = cq.Workplane("XY").box(LL-24, 5, 5).translate((ox, ys*TW, 6.5))
        base = base.union(rib)
    return base


# ═══════════════════════════════════════════════════════════
# LOCOMOTIVE BODY (open top)
# ═══════════════════════════════════════════════════════════
def mk_loco_body(ox):
    H=74; BZ=7
    main_l=LL-46; main_cx=ox-23
    # Open-top shell
    outer = cq.Workplane("XY").box(main_l, TW, H).translate((main_cx, 0, H/2+BZ))
    inner = cq.Workplane("XY").box(main_l-6, TW-WALL*2, H+6).translate(
        (main_cx, 0, H/2+BZ+WALL/2+3))
    shell = outer.cut(inner)
    # Cab
    cab_l=48; cab_cx=ox+LL/2-cab_l/2; cab_h=H+12
    cab_o = cq.Workplane("XY").box(cab_l, TW, cab_h).translate((cab_cx, 0, cab_h/2+BZ))
    cab_i = cq.Workplane("XY").box(cab_l-6, TW-WALL*2, cab_h+6).translate(
        (cab_cx, 0, cab_h/2+BZ+WALL/2+3))
    cab = cab_o.cut(cab_i)
    # Nose slope
    nose_cut = cq.Workplane("XY").box(cab_l, TW+4, cab_h*0.42).translate(
        (cab_cx+cab_l*0.13, 0, cab_h*0.80+BZ))
    cab = cab.cut(nose_cut)
    shell = shell.union(cab)
    # Windshield
    ws = cq.Workplane("XY").box(WALL+4, TW-20, H*0.30).translate(
        (ox+LL/2-WALL/2-1, 0, H*0.68+BZ))
    shell = shell.cut(ws)
    # Side windows
    for xi in [-96,-68,-40,-12,16]:
        for ys in [1,-1]:
            w = cq.Workplane("XY").box(22, WALL+4, 20).translate(
                (ox+xi, ys*TW/2, H*0.56+BZ))
            shell = shell.cut(w)
    # Headlights
    for ys in [1,-1]:
        hl = cq.Workplane("XZ").circle(5).extrude(WALL+3).translate(
            (ox+LL/2, ys*(TW/2-16), H*0.22+BZ))
        shell = shell.union(hl)
    # Vents
    for xi in [-132,-115]:
        for ys in [1,-1]:
            g = cq.Workplane("XY").box(12, WALL+4, 14).translate(
                (ox+xi, ys*TW/2, H*0.30+BZ))
            shell = shell.cut(g)
    return shell


# ═══════════════════════════════════════════════════════════
# PANTOGRAPH
# ═══════════════════════════════════════════════════════════
def mk_pantograph(ox):
    H=74; BZ=7; base_z=H+BZ+4
    base = cq.Workplane("XY").box(52, 30, 5).translate((ox+28, 0, base_z+2.5))
    for xs in [1,-1]:
        a = cq.Workplane("XZ").box(3, 28, 3).translate((ox+28+xs*9, 10, base_z+16))
        b = cq.Workplane("XZ").box(3, 28, 3).translate((ox+28+xs*9, -10, base_z+16))
        base = base.union(a).union(b)
    strip = cq.Workplane("XY").box(68, 5, 4).translate((ox+28, 0, base_z+30))
    return base.union(strip)


# ═══════════════════════════════════════════════════════════
# WAGON CHASSIS
# ═══════════════════════════════════════════════════════════
def mk_wagon_chassis(wx):
    base = cq.Workplane("XY").box(WL, TW, 6).translate((wx, 0, 3))
    for bx in [wx+WBGX, wx-WBGX]:
        cut = cq.Workplane("XY").box(WBWB+26, TW-16, 4).translate((bx, 0, 0.5))
        base = base.cut(cut)
    for xi in [-40,0,40]:
        rib = cq.Workplane("XY").box(6, TW-14, 5).translate((wx+xi, 0, 5.5))
        base = base.union(rib)
    return base


# ═══════════════════════════════════════════════════════════
# WAGON BODY (open top)
# ═══════════════════════════════════════════════════════════
def mk_wagon_body(wx):
    H=70; BZ=6
    outer = cq.Workplane("XY").box(WL, TW, H).translate((wx, 0, H/2+BZ))
    inner = cq.Workplane("XY").box(WL-6, TW-WALL*2, H+6).translate(
        (wx, 0, H/2+BZ+WALL/2+3))
    shell = outer.cut(inner)
    # Windows (6 per side)
    for xi in [-65,-39,-13,13,39,65]:
        for ys in [1,-1]:
            w = cq.Workplane("XY").box(24, WALL+4, 26).translate(
                (wx+xi, ys*TW/2, H*0.60+BZ))
            shell = shell.cut(w)
    # End doors
    for xs in [1,-1]:
        d = cq.Workplane("XY").box(WALL+4, 32, 44).translate(
            (wx+xs*WL/2, 0, H*0.38+BZ))
        shell = shell.cut(d)
    # Side doors
    for ys in [1,-1]:
        sd = cq.Workplane("XY").box(24, WALL+4, 44).translate(
            (wx, ys*TW/2, H*0.38+BZ))
        shell = shell.cut(sd)
    # Blue stripe
    for ys in [1,-1]:
        stripe = cq.Workplane("XY").box(WL-8, WALL, 8).translate(
            (wx, ys*(TW/2+WALL/2), H*0.26+BZ))
        shell = shell.union(stripe)
    return shell


# ═══════════════════════════════════════════════════════════
# EXPORT PART A: WHEEL
# ═══════════════════════════════════════════════════════════
print("=" * 60)
print("  BUILDING MOVABLE WHEELS TRAIN")
print(f"  Wheel diameter: {WD} mm (1.5 cm)")
print(f"  Axle diameter:  {AD} mm (press-fit in bogie)")
print(f"  Wheel bore:     {BORE} mm (0.4mm clearance → spins)")
print("=" * 60)

print("\n[PART 1] Single Wheel (15mm diam)...")
wheel = mk_wheel_part()
WHEEL_STL = os.path.join(OUT, "WHEEL_15mm.stl")
cq.exporters.export(wheel, WHEEL_STL)
print(f"  → {WHEEL_STL}")
print(f"  Print 24× (8 per vehicle × 3 vehicles)")

# ═══════════════════════════════════════════════════════════
# EXPORT PART B: AXLE
# ═══════════════════════════════════════════════════════════
print("\n[PART 2] Single Axle...")
axle = mk_axle_part()
AXLE_STL = os.path.join(OUT, "AXLE_88mm.stl")
cq.exporters.export(axle, AXLE_STL)
print(f"  → {AXLE_STL}")
print(f"  Print 12× (4 per vehicle × 3 vehicles)")

# ═══════════════════════════════════════════════════════════
# EXPORT PART C: FULL BODY ASSEMBLY (no wheels/axles)
# ═══════════════════════════════════════════════════════════
print("\n[PART 3] Train Body Assembly (no wheels)...")
parts = []

print("  Loco chassis...")
parts.append(mk_loco_chassis(LOX))
print("  Loco body...")
parts.append(mk_loco_body(LOX))
print("  Pantograph...")
parts.append(mk_pantograph(LOX))
print("  Loco front bogie frame...")
parts.append(mk_bogie_frame(LOX+LBGX, LBWB))
print("  Loco rear bogie frame...")
parts.append(mk_bogie_frame(LOX-LBGX, LBWB))
print("  Loco couplers...")
parts.append(mk_coupler(LOX+LL/2, +1))
parts.append(mk_coupler(LOX-LL/2, -1))

print("  Wagon 1 chassis...")
parts.append(mk_wagon_chassis(W1X))
print("  Wagon 1 body...")
parts.append(mk_wagon_body(W1X))
print("  Wagon 1 bogies...")
parts.append(mk_bogie_frame(W1X+WBGX, WBWB))
parts.append(mk_bogie_frame(W1X-WBGX, WBWB))
print("  Wagon 1 couplers...")
parts.append(mk_coupler(W1X+WL/2, +1))
parts.append(mk_coupler(W1X-WL/2, -1))

print("  Wagon 2 chassis...")
parts.append(mk_wagon_chassis(W2X))
print("  Wagon 2 body...")
parts.append(mk_wagon_body(W2X))
print("  Wagon 2 bogies...")
parts.append(mk_bogie_frame(W2X+WBGX, WBWB))
parts.append(mk_bogie_frame(W2X-WBGX, WBWB))
print("  Wagon 2 couplers...")
parts.append(mk_coupler(W2X+WL/2, +1))
parts.append(mk_coupler(W2X-WL/2, -1))

print(f"\n  Merging {len(parts)} body parts...")
body = parts[0]
for i, p in enumerate(parts[1:], 1):
    print(f"    [{i+1}/{len(parts)}]...")
    try:
        body = body.union(p)
    except Exception as e:
        print(f"    WARNING: skipped — {e}")

BODY_STL  = os.path.join(OUT, "TRAIN_BODY.stl")
BODY_STEP = os.path.join(OUT, "TRAIN_BODY.step")
print("  Exporting body STL...")
cq.exporters.export(body, BODY_STL)
print("  Exporting body STEP...")
cq.exporters.export(body, BODY_STEP)

# Print summary
bk  = os.path.getsize(BODY_STL)/1024
wk  = os.path.getsize(WHEEL_STL)/1024
ak  = os.path.getsize(AXLE_STL)/1024

print(f"\n{'='*60}")
print(f"  TRAIN_BODY.stl      {bk:>8.1f} KB  →  Print 1×")
print(f"  WHEEL_15mm.stl      {wk:>8.1f} KB  →  Print 24×")
print(f"  AXLE_88mm.stl       {ak:>8.1f} KB  →  Print 12×")
print(f"{'='*60}")
print(f"\n  Assembly instructions:")
print(f"  1. Press each axle into the bogie axle-box holes")
print(f"  2. Slide 2 wheels (bore=5.8mm) onto each axle end")
print(f"  3. Wheels spin freely — the 0.4mm clearance allows rotation")
print(f"  4. Optional: tiny CA glue drop on axle tip to retain wheels")
print(f"\nDONE!")
