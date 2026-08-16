"""
build_final_train.py
=================================================
FINAL SINGLE-FILE COMPLETE TRAIN
  - Locomotive + Wagon 1 + Wagon 2 (580 mm total)
  - Width: 102 mm  |  Height: ~102 mm
  - Wheels: 15 mm diameter, built-in
  - Hook-style couplers between wagons
  - Open roof
  - One STL + one STEP output
=================================================
"""
import cadquery as cq
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
os.makedirs(OUT, exist_ok=True)

# ═══════════════════════════════════════════════════════════
# PARAMETERS
# ═══════════════════════════════════════════════════════════
TW   = 102     # body width (Y)
WD   = 15      # wheel diameter
WW   = 9       # wheel width (Y)
FLD  = 2.0     # flange extra radius
AD   = 5.0     # axle diameter
GA   = 62      # track gauge
AZ   = -24     # axle centre Z
WALL = 3.0

LL   = 200     # loco length
LBGX = 62
LBWB = 44

WL   = 180     # wagon length
WBGX = 50
WBWB = 38

GAP  = 10

LOX  = 190.0
W1X  = LOX - LL/2 - GAP - WL/2   # = -10
W2X  = W1X - WL/2 - GAP - WL/2   # = -200
TOTAL_LEN = 580

# Hook coupler Z centre
HOOK_Z = AZ + WD/2 + 14   # just above bogie, below body


# ═══════════════════════════════════════════════════════════
# WHEEL  (axis = Y, disc in XZ plane)
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
    shaft = (cq.Workplane("XZ").circle(AD/2).extrude(tot_y)
             .translate((cx, -tot_y/2, az)))
    lw = mk_wheel().translate((cx,  GA/2,        az))
    rw = mk_wheel().translate((cx, -(GA/2 + WW), az))
    return shaft.union(lw).union(rw)


# ═══════════════════════════════════════════════════════════
# BOGIE (frame + 2 axle pairs)
# ═══════════════════════════════════════════════════════════
def mk_bogie(cx, bwb):
    bL = bwb + 28; bY = TW + 4; bH = 12
    frame = (cq.Workplane("XY").box(bL, bY, bH)
             .translate((cx, 0, -bH/2 - 1)))
    # Bolster beams
    for ys in [1, -1]:
        beam = (cq.Workplane("XY").box(bL-6, 6, bH-4)
                .translate((cx, ys*bY/2, -bH/2-1)))
        frame = frame.union(beam)
    # Axle-box legs (hang down to axle level)
    leg_h = abs(AZ) - bH - 3
    for ax_x in [cx+bwb/2, cx-bwb/2]:
        for ys in [1, -1]:
            leg = (cq.Workplane("XY").box(10, 8, leg_h)
                   .translate((ax_x, ys*(GA/2+WW/2+1), -bH-1-leg_h/2)))
            frame = frame.union(leg)
    # Pivot post
    pivot = (cq.Workplane("XY").circle(11).extrude(18)
             .translate((cx, 0, 0)))
    frame = frame.union(pivot)
    # Axle pairs
    a1 = mk_axle_pair(cx + bwb/2)
    a2 = mk_axle_pair(cx - bwb/2)
    return frame.union(a1).union(a2)


# ═══════════════════════════════════════════════════════════
# HOOK COUPLER  — replaces the old box-joint coupler
#
#  Each wagon/loco end gets ONE hook (J-shaped).
#  Adjacent hooks face each other and interlock:
#
#  Wagon1-rear        Wagon2-front
#    ___                  ___
#   |   |                |   |
#   |   |__ arm  arm __ |   |
#   |hook_down|    |hook_up |
#       ↑ interlocked ↑
#
# ═══════════════════════════════════════════════════════════
def mk_hook(face_x, sign, hook_up=True):
    """
    Hook coupler extending 'sign' direction from face_x.
    hook_up=True  → hook opening faces upward  (+Z)
    hook_up=False → hook opening faces downward (-Z)
    Adjacent ends always alternate so they interlock.

    Parameters:
      face_x  – X coordinate of the vehicle end face
      sign    – +1 (front) or -1 (rear)
      hook_up – orientation of the hook opening
    """
    hz  = HOOK_Z          # vertical centre
    hup = 1 if hook_up else -1

    # ── Mounting shank (at vehicle face) ──────────────
    shank = (cq.Workplane("XY")
             .box(6, 18, 24)
             .translate((face_x + sign*3, 0, hz)))

    # ── Horizontal arm ────────────────────────────────
    arm_l = 10
    arm   = (cq.Workplane("XY")
             .box(arm_l, 12, 8)
             .translate((face_x + sign*(6 + arm_l/2), 0, hz)))

    # ── Vertical hook post ────────────────────────────
    post_h = 13
    post   = (cq.Workplane("XY")
              .box(8, 12, post_h)
              .translate((face_x + sign*(6 + arm_l), 0,
                          hz + hup*(post_h/2 + 4))))

    # ── Hook lip (closes the J at the open end) ───────
    lip   = (cq.Workplane("XY")
             .box(12, 12, 5)
             .translate((face_x + sign*(6 + arm_l - 3), 0,
                         hz + hup*(post_h + 4 + 2.5))))

    # ── Chain link pin (detail at arm tip) ───────────
    pin   = (cq.Workplane("XZ")
             .circle(3)
             .extrude(16)
             .translate((face_x + sign*(6 + arm_l), -8, hz)))

    return shank.union(arm).union(post).union(lip).union(pin)


# ═══════════════════════════════════════════════════════════
# LOCOMOTIVE CHASSIS
# ═══════════════════════════════════════════════════════════
def mk_loco_chassis(ox):
    base = (cq.Workplane("XY").box(LL, TW, 7)
            .translate((ox, 0, 3.5)))
    for bx in [ox+LBGX, ox-LBGX]:
        cut = (cq.Workplane("XY").box(LBWB+30, TW-16, 5)
               .translate((bx, 0, 1)))
        base = base.cut(cut)
    for ys in [0.28, -0.28]:
        rib = (cq.Workplane("XY").box(LL-24, 5, 5)
               .translate((ox, ys*TW, 6.5)))
        base = base.union(rib)
    return base


# ═══════════════════════════════════════════════════════════
# LOCOMOTIVE BODY (open top)
# ═══════════════════════════════════════════════════════════
def mk_loco_body(ox):
    H=74; BZ=7
    main_l=LL-46; main_cx=ox-23
    outer = (cq.Workplane("XY").box(main_l, TW, H)
             .translate((main_cx, 0, H/2+BZ)))
    inner = (cq.Workplane("XY").box(main_l-6, TW-WALL*2, H+6)
             .translate((main_cx, 0, H/2+BZ+WALL/2+3)))
    shell = outer.cut(inner)

    cab_l=48; cab_cx=ox+LL/2-cab_l/2; cab_h=H+12
    cab_o = (cq.Workplane("XY").box(cab_l, TW, cab_h)
             .translate((cab_cx, 0, cab_h/2+BZ)))
    cab_i = (cq.Workplane("XY").box(cab_l-6, TW-WALL*2, cab_h+6)
             .translate((cab_cx, 0, cab_h/2+BZ+WALL/2+3)))
    cab = cab_o.cut(cab_i)
    nose_cut = (cq.Workplane("XY").box(cab_l, TW+4, cab_h*0.42)
                .translate((cab_cx+cab_l*0.13, 0, cab_h*0.80+BZ)))
    cab = cab.cut(nose_cut)
    shell = shell.union(cab)

    # Windshield
    ws = (cq.Workplane("XY").box(WALL+4, TW-20, H*0.30)
          .translate((ox+LL/2-WALL/2-1, 0, H*0.68+BZ)))
    shell = shell.cut(ws)
    # Side windows
    for xi in [-96,-68,-40,-12,16]:
        for ys in [1,-1]:
            w = (cq.Workplane("XY").box(22, WALL+4, 20)
                 .translate((ox+xi, ys*TW/2, H*0.56+BZ)))
            shell = shell.cut(w)
    # Headlights
    for ys in [1,-1]:
        hl = (cq.Workplane("XZ").circle(5).extrude(WALL+3)
              .translate((ox+LL/2, ys*(TW/2-16), H*0.22+BZ)))
        shell = shell.union(hl)
    # Vents
    for xi in [-132,-115]:
        for ys in [1,-1]:
            g = (cq.Workplane("XY").box(12, WALL+4, 14)
                 .translate((ox+xi, ys*TW/2, H*0.30+BZ)))
            shell = shell.cut(g)
    return shell


# ═══════════════════════════════════════════════════════════
# PANTOGRAPH
# ═══════════════════════════════════════════════════════════
def mk_pantograph(ox):
    H=74; BZ=7; bz=H+BZ+4
    base = (cq.Workplane("XY").box(52,30,5)
            .translate((ox+28, 0, bz+2.5)))
    for xs in [1,-1]:
        a = (cq.Workplane("XZ").box(3,28,3)
             .translate((ox+28+xs*9, 10, bz+16)))
        b = (cq.Workplane("XZ").box(3,28,3)
             .translate((ox+28+xs*9,-10, bz+16)))
        base = base.union(a).union(b)
    strip = (cq.Workplane("XY").box(68,5,4)
             .translate((ox+28, 0, bz+30)))
    return base.union(strip)


# ═══════════════════════════════════════════════════════════
# WAGON CHASSIS
# ═══════════════════════════════════════════════════════════
def mk_wagon_chassis(wx):
    base = (cq.Workplane("XY").box(WL, TW, 6)
            .translate((wx, 0, 3)))
    for bx in [wx+WBGX, wx-WBGX]:
        cut = (cq.Workplane("XY").box(WBWB+26, TW-16, 4)
               .translate((bx, 0, 0.5)))
        base = base.cut(cut)
    for xi in [-40,0,40]:
        rib = (cq.Workplane("XY").box(6, TW-14, 5)
               .translate((wx+xi, 0, 5.5)))
        base = base.union(rib)
    return base


# ═══════════════════════════════════════════════════════════
# WAGON BODY (open top)
# ═══════════════════════════════════════════════════════════
def mk_wagon_body(wx):
    H=70; BZ=6
    outer = (cq.Workplane("XY").box(WL, TW, H)
             .translate((wx, 0, H/2+BZ)))
    inner = (cq.Workplane("XY").box(WL-6, TW-WALL*2, H+6)
             .translate((wx, 0, H/2+BZ+WALL/2+3)))
    shell = outer.cut(inner)
    # Windows
    for xi in [-65,-39,-13,13,39,65]:
        for ys in [1,-1]:
            w = (cq.Workplane("XY").box(24, WALL+4, 26)
                 .translate((wx+xi, ys*TW/2, H*0.60+BZ)))
            shell = shell.cut(w)
    # End doors
    for xs in [1,-1]:
        d = (cq.Workplane("XY").box(WALL+4, 32, 44)
             .translate((wx+xs*WL/2, 0, H*0.38+BZ)))
        shell = shell.cut(d)
    # Side doors
    for ys in [1,-1]:
        sd = (cq.Workplane("XY").box(24, WALL+4, 44)
              .translate((wx, ys*TW/2, H*0.38+BZ)))
        shell = shell.cut(sd)
    # Blue stripe
    for ys in [1,-1]:
        stripe = (cq.Workplane("XY").box(WL-8, WALL, 8)
                  .translate((wx, ys*(TW/2+WALL/2), H*0.26+BZ)))
        shell = shell.union(stripe)
    return shell


# ═══════════════════════════════════════════════════════════
# BUILD COMPLETE ASSEMBLY
# ═══════════════════════════════════════════════════════════
print("=" * 62)
print("  FINAL COMPLETE TRAIN — SINGLE FILE")
print(f"  Length: {TOTAL_LEN}mm | Width: {TW}mm | Wheel: {WD}mm dia")
print(f"  Couplers: HOOK style (interlocking J-hooks)")
print(f"  Roof: OPEN")
print("=" * 62)

parts = []

# ── LOCOMOTIVE ────────────────────────────────────────────
print(" [01] Loco chassis...")
parts.append(mk_loco_chassis(LOX))
print(" [02] Loco body (open top)...")
parts.append(mk_loco_body(LOX))
print(" [03] Pantograph...")
parts.append(mk_pantograph(LOX))
print(" [04] Loco front bogie + wheels...")
parts.append(mk_bogie(LOX + LBGX, LBWB))
print(" [05] Loco rear bogie + wheels...")
parts.append(mk_bogie(LOX - LBGX, LBWB))

# Loco front: box coupler (outer end, faces forward — no interlocking needed)
print(" [06] Loco front buffer hook...")
parts.append(mk_hook(LOX + LL/2, +1, hook_up=True))

# Loco rear → Wagon 1 front: interlocked hooks
# Loco rear hook goes DOWN, Wagon1 front hook goes UP → they interlock
print(" [07] Loco rear hook (down) ↔ Wagon1 front hook (up) — interlocked...")
parts.append(mk_hook(LOX - LL/2, -1, hook_up=False))   # loco rear: hook down
parts.append(mk_hook(W1X + WL/2, +1, hook_up=True))    # wagon1 front: hook up

# ── WAGON 1 ───────────────────────────────────────────────
print(" [08] Wagon 1 chassis...")
parts.append(mk_wagon_chassis(W1X))
print(" [09] Wagon 1 body (open top)...")
parts.append(mk_wagon_body(W1X))
print(" [10] Wagon 1 front bogie + wheels...")
parts.append(mk_bogie(W1X + WBGX, WBWB))
print(" [11] Wagon 1 rear bogie + wheels...")
parts.append(mk_bogie(W1X - WBGX, WBWB))

# Wagon1 rear → Wagon2 front: interlocked hooks
# Wagon1 rear: hook UP, Wagon2 front: hook DOWN
print(" [12] Wagon1 rear hook (up) ↔ Wagon2 front hook (down) — interlocked...")
parts.append(mk_hook(W1X - WL/2, -1, hook_up=True))    # wagon1 rear: hook up
parts.append(mk_hook(W2X + WL/2, +1, hook_up=False))   # wagon2 front: hook down

# ── WAGON 2 ───────────────────────────────────────────────
print(" [13] Wagon 2 chassis...")
parts.append(mk_wagon_chassis(W2X))
print(" [14] Wagon 2 body (open top)...")
parts.append(mk_wagon_body(W2X))
print(" [15] Wagon 2 front bogie + wheels...")
parts.append(mk_bogie(W2X + WBGX, WBWB))
print(" [16] Wagon 2 rear bogie + wheels...")
parts.append(mk_bogie(W2X - WBGX, WBWB))

# Wagon 2 rear: simple buffer hook (outer end)
print(" [17] Wagon 2 rear buffer hook...")
parts.append(mk_hook(W2X - WL/2, -1, hook_up=True))

# ── MERGE ─────────────────────────────────────────────────
print(f"\nMerging {len(parts)} parts into ONE solid...")
train = parts[0]
for i, p in enumerate(parts[1:], 1):
    print(f"  [{i+1:02d}/{len(parts)}] merging...")
    try:
        train = train.union(p)
    except Exception as e:
        print(f"    WARNING: skipped — {e}")

# ── EXPORT ────────────────────────────────────────────────
STEP = os.path.join(OUT, "FINAL_TRAIN.step")
STL  = os.path.join(OUT, "FINAL_TRAIN.stl")

print("\nExporting STEP (for Onshape / Fusion 360)...")
cq.exporters.export(train, STEP)

print("Exporting STL (for 3D printing / 3D Viewer)...")
cq.exporters.export(train, STL)

sk = os.path.getsize(STEP)/1024
stk = os.path.getsize(STL)/1024

print(f"\n{'='*62}")
print(f"  FINAL_TRAIN.step    {sk:>8.1f} KB   ← import to Onshape")
print(f"  FINAL_TRAIN.stl     {stk:>8.1f} KB   ← open in 3D Viewer / slicer")
print(f"{'='*62}")
print(f"  Config  : LOCO + WAGON1 + WAGON2")
print(f"  Length  : {TOTAL_LEN} mm (58 cm)")
print(f"  Width   : {TW} mm (10.2 cm)")
print(f"  Wheels  : {WD} mm diameter (1.5 cm) — built-in")
print(f"  Couplers: J-hook style (interlocked between wagons)")
print(f"  Roof    : OPEN")
print(f"{'='*62}")
print("\nDONE! Files are in output/ folder.")
