"""
build_assembled_train.py
Builds the complete train as a SINGLE pre-assembled STEP + STL file.
All parts are already positioned correctly — just import one file into Onshape.
"""
import cadquery as cq
import os, sys

OUTPUT = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(OUTPUT, exist_ok=True)

# ── Master Dimensions (mm) ────────────────────────────────────
TL  = 420   # train length
TW  = 70    # train width
TH  = 95    # train height

WD  = 22    # wheel diameter
WW  = 10    # wheel width
AD  = 6     # axle diameter
BW  = TW + 16  # bogie width (outside wheels)

FLOOR_Y    = 0      # chassis top face Y
AXLE_Y     = -28    # axle centre below chassis floor
BOGIE_Y    = -18    # bogie frame centre Y

FRONT_BOGIE_X =  150
REAR_BOGIE_X  = -150
AXLE_SPACING  =  52   # between two axles in one bogie

# ── Helper: make_wheel ────────────────────────────────────────
def make_wheel(x, z):
    """Spoked railway wheel centred at (x, AXLE_Y, z)."""
    rim = (cq.Workplane("YZ")
           .circle(WD/2).extrude(WW)
           .faces(">X").workplane()
           .circle(WD/2 - 3).cutBlind(-2))
    hub = (cq.Workplane("YZ")
           .circle(AD/2 + 2).extrude(WW))
    w = rim.union(hub)
    # translate to position
    return w.translate((x - WW/2, AXLE_Y, z))

# ── Helper: make_axle ─────────────────────────────────────────
def make_axle(x):
    ax = (cq.Workplane("YZ")
          .circle(AD/2).extrude(BW)
          .translate((x - BW/2, AXLE_Y, 0)))
    return ax

# ── Helper: make_bogie ────────────────────────────────────────
def make_bogie(cx):
    """Simple bogie frame at cx along X axis."""
    frame_l = AXLE_SPACING + 20
    frame_w = BW - 4
    frame_h = 12

    frame = (cq.Workplane("XZ")
             .box(frame_l, frame_w, frame_h)
             .translate((cx, BOGIE_Y - frame_h/2, 0)))

    # side beams
    beam_h = 10
    sb = (cq.Workplane("XZ")
          .box(frame_l - 4, 4, beam_h)
          .translate((cx, BOGIE_Y - frame_h - beam_h/2, frame_w/2 - 2)))
    sb2 = sb.translate((0, 0, -(frame_w - 4)))

    # pivot post (connects to chassis)
    pivot = (cq.Workplane("XY")
             .circle(8).extrude(10)
             .translate((cx, BOGIE_Y, 0)))

    return frame.union(sb).union(sb2).union(pivot)

# ── Helper: make_chassis ─────────────────────────────────────
def make_chassis():
    base = (cq.Workplane("XY")
            .box(TL, TW, 5)
            .translate((0, -2.5, 0)))
    # bogie cutouts
    for bx in [FRONT_BOGIE_X, REAR_BOGIE_X]:
        cut = (cq.Workplane("XY")
               .box(60, 50, 8)
               .translate((bx, -4, 0)))
        base = base.cut(cut)
    return base

# ── Helper: make_body ────────────────────────────────────────
def make_body():
    wall = 2.5
    body_h = 55

    outer = (cq.Workplane("XY")
             .box(TL - 20, TW, body_h)
             .translate((0, body_h/2, 0)))
    inner = (cq.Workplane("XY")
             .box(TL - 25, TW - wall*2, body_h - wall)
             .translate((0, body_h/2 + wall/2, 0)))
    shell = outer.cut(inner)

    # side windows (4 per side)
    for xi in [-140, -50, 50, 140]:
        for zs in [1, -1]:
            win = (cq.Workplane("XZ")
                   .box(30, 22, wall + 4)
                   .translate((xi, body_h/2 + 20, zs * (TW/2))))
            shell = shell.cut(win)

    # ventilation grilles
    for xi in [-160, -100, 100, 160]:
        for zs in [1, -1]:
            grill = (cq.Workplane("XZ")
                     .box(15, 10, wall + 4)
                     .translate((xi, body_h/2 + 5, zs * (TW/2))))
            shell = shell.cut(grill)
    return shell

# ── Helper: make_cab ─────────────────────────────────────────
def make_cab():
    body_h = 55
    cab_l  = 40
    cab    = (cq.Workplane("XY")
              .box(cab_l, TW, body_h + 5)
              .translate((TL/2 - cab_l/2 - 10, body_h/2 + 2.5, 0)))
    # windshield cutout
    ws = (cq.Workplane("YZ")
          .box(TW - 6, 22, 20)
          .translate((TL/2 - 12, body_h/2 + 22, 0)))
    cab = cab.cut(ws)
    return cab

# ── Helper: make_roof ────────────────────────────────────────
def make_roof():
    body_h = 55
    roof_h = 12
    roof   = (cq.Workplane("XY")
              .box(TL - 20, TW - 4, roof_h)
              .translate((0, body_h + roof_h/2, 0)))
    # HVAC boxes
    for xi in [-80, 0, 80]:
        hvac = (cq.Workplane("XY")
                .box(30, 20, roof_h - 2)
                .translate((xi, body_h + roof_h + (roof_h-2)/2, 0)))
        roof = roof.union(hvac)
    return roof

# ── Helper: make_coupler ─────────────────────────────────────
def make_coupler(x_sign):
    arm  = (cq.Workplane("XY")
            .box(20, 12, 12)
            .translate((x_sign * (TL/2 + 10), 6, 0)))
    hook = (cq.Workplane("YZ")
            .box(12, 8, 8)
            .translate((x_sign * (TL/2 + 22), 6, 0)))
    return arm.union(hook)

# ── Helper: make_pantograph ──────────────────────────────────
def make_pantograph():
    body_h = 55
    roof_h = 12
    base_y = body_h + roof_h
    base = (cq.Workplane("XY")
            .box(50, 30, 4)
            .translate((0, base_y + 4, 0)))
    # lower arms
    arm1 = (cq.Workplane("XZ")
            .box(4, 28, 4)
            .rotate((0,0,0), (0,0,1), 30)
            .translate((-10, base_y + 18, 8)))
    arm2 = arm1.mirror("YZ")
    # contact strip
    strip = (cq.Workplane("XY")
             .box(60, 4, 3)
             .translate((0, base_y + 32, 0)))
    return base.union(arm1).union(arm2).union(strip)

# ═════════════════════════════════════════════════════════════
# BUILD THE COMPLETE ASSEMBLED TRAIN
# ═════════════════════════════════════════════════════════════
print("Building complete assembled train ...")
print("  [1/9] Chassis ...")
train = make_chassis()

print("  [2/9] Body shell ...")
train = train.union(make_body())

print("  [3/9] Front cab ...")
train = train.union(make_cab())

print("  [4/9] Roof ...")
train = train.union(make_roof())

print("  [5/9] Couplers ...")
train = train.union(make_coupler(+1)).union(make_coupler(-1))

print("  [6/9] Bogies ...")
train = train.union(make_bogie(FRONT_BOGIE_X))
train = train.union(make_bogie(REAR_BOGIE_X))

print("  [7/9] Axles ...")
for bx in [FRONT_BOGIE_X, REAR_BOGIE_X]:
    for ax in [bx + AXLE_SPACING/2, bx - AXLE_SPACING/2]:
        train = train.union(make_axle(ax))

print("  [8/9] Wheels (8x) ...")
for bx in [FRONT_BOGIE_X, REAR_BOGIE_X]:
    for ax in [bx + AXLE_SPACING/2, bx - AXLE_SPACING/2]:
        for zpos in [BW/2, -BW/2]:
            train = train.union(make_wheel(ax, zpos))

print("  [9/9] Pantograph ...")
train = train.union(make_pantograph())

# ── Export ────────────────────────────────────────────────────
step_path = os.path.join(OUTPUT, "SMART_TRAIN_COMPLETE.step")
stl_path  = os.path.join(OUTPUT, "SMART_TRAIN_COMPLETE.stl")

print("\nExporting STEP ...")
cq.exporters.export(train, step_path)
print(f"  Saved: {step_path}")

print("Exporting STL ...")
cq.exporters.export(train, stl_path)
print(f"  Saved: {stl_path}")

step_kb = os.path.getsize(step_path) / 1024
stl_kb  = os.path.getsize(stl_path)  / 1024
print(f"\n{'='*50}")
print(f"  SMART_TRAIN_COMPLETE.step  {step_kb:>8.1f} KB")
print(f"  SMART_TRAIN_COMPLETE.stl   {stl_kb:>8.1f} KB")
print(f"{'='*50}")
print("\nDone! Import SMART_TRAIN_COMPLETE.step into Onshape.")
print("All parts are pre-positioned — wheels, bogies, roof, couplers included.")
