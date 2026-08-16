"""
build_assembly_kit.py
═══════════════════════════════════════════════════════════════
COMPLETE 3D-PRINT ASSEMBLY KIT — Separate parts for everything

OUTPUT FILES (in output/kit/):
  01_LOCO_BODY.stl        Print: 1×
  02_WAGON_BODY.stl       Print: 2×  (both wagons are identical)
  03_BOGIE_FRAME.stl      Print: 6×  (2 per vehicle)
  04_WHEEL_15mm.stl       Print: 24× (8 per vehicle)
  05_AXLE.stl             Print: 12× (4 per vehicle)
  06_PIVOT_BRACKET.stl    Print: 4×  (inner ends only)
  07_DRAWBAR.stl          Print: 2×  (one per inter-vehicle gap)

BOGIE ROTATION:
  Each bogie has a 12mm pivot pin sticking up through a 12.4mm
  hole in the chassis floor → bogie rotates freely for curves.

PIVOT COUPLER:
  LOCO──[bracket]──[drawbar]──[bracket]──WAGON1
  Each bracket has a vertical pivot pin; drawbar has matching
  fork holes at each end → 2-axis articulation on curves.

CLEARANCES (FDM-tuned):
  Bogie pivot pin  = 12.0 mm shaft → chassis hole = 12.4 mm (rotates)
  Drawbar pin      = 5.0 mm  → bracket fork hole = 5.4 mm  (rotates)
  Axle shaft       = 5.0 mm  → bogie axle-box    = 5.0 mm  (press-fit)
  Wheel bore       = 5.8 mm  → spins on 5.0 mm axle
"""
import cadquery as cq, os

KIT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", "kit")
os.makedirs(KIT, exist_ok=True)

# ═══════════════════════════════════════════════════════════
# GLOBAL PARAMETERS
# ═══════════════════════════════════════════════════════════
TW    = 102    # body width (Y)
TH_B  = 7      # chassis slab height
WALL  = 3.0    # body wall thickness

WD    = 15     # wheel diameter (1.5 cm)
WW    = 9      # wheel width
FLD   = 2.0    # flange extra radius
AD    = 5.0    # axle shaft diameter
BORE  = 5.8    # wheel bore (spinning fit)
GA    = 62     # track gauge
AZ    = -24    # axle centre Z

# Bogie pivot
BP_D  = 12.0   # bogie pivot pin diameter
BP_H  = 22     # pin height
CH_D  = 12.4   # chassis pivot hole diameter (0.2 mm clearance → rotates)

# Coupler pivot
CP_D  = 5.0    # coupler pivot pin diameter
CF_D  = 5.4    # fork hole diameter (rotates)

# Locomotive
LL    = 200
LBGX  = 62     # bogie X offset from loco centre
LBWB  = 44     # bogie wheelbase

# Wagon
WL    = 180
WBGX  = 50
WBWB  = 38

GAP   = 14     # inter-vehicle gap (drawbar fits here)

LOX   = 190.0
W1X   = LOX - LL/2 - GAP - WL/2
W2X   = W1X - WL/2 - GAP - WL/2
TOTAL = LL + GAP + WL + GAP + WL    # 588 mm


# ═══════════════════════════════════════════════════════════
# PART 04: WHEEL  (standalone, axis = Y)
# ═══════════════════════════════════════════════════════════
def mk_wheel():
    rim  = cq.Workplane("XZ").circle(WD/2).extrude(WW)
    flng = cq.Workplane("XZ").workplane(offset=-FLD).circle(WD/2+FLD).extrude(FLD)
    hub  = cq.Workplane("XZ").circle(BORE/2+1.5).extrude(WW)
    bore = cq.Workplane("XZ").workplane(offset=-FLD-0.5).circle(BORE/2).extrude(WW+FLD+1.5)
    return rim.union(flng).union(hub).cut(bore)


# ═══════════════════════════════════════════════════════════
# PART 05: AXLE (standalone)
# ═══════════════════════════════════════════════════════════
def mk_axle():
    L      = GA + WW*2 + 8    # 88 mm
    cap_r  = AD/2 + 1.0       # 3.5 mm > BORE/2 → retains wheel
    shaft  = cq.Workplane("XZ").circle(AD/2).extrude(L).translate((0,-L/2,0))
    cap_a  = cq.Workplane("XZ").circle(cap_r).extrude(2.5).translate((0, L/2, 0))
    cap_b  = cq.Workplane("XZ").circle(cap_r).extrude(2.5).translate((0,-L/2-2.5,0))
    return shaft.union(cap_a).union(cap_b)


# ═══════════════════════════════════════════════════════════
# PART 03: BOGIE FRAME  (standalone, pivot pin on top)
#   Origin at bogie pivot centre (X=0, Y=0, Z=0)
#   Pivot pin sticks UP from Z=0
# ═══════════════════════════════════════════════════════════
def mk_bogie_standalone(bwb):
    """
    Single bogie at local origin (0,0,0).
    Pivot pin (dia=12mm) sticks up 22mm → goes into chassis hole.
    Axle-box holes on the legs (dia=5mm, press-fit for axle).
    """
    bL = bwb + 28; bY = TW + 4; bH = 12
    BOGIE_BOT_Z = -bH - 1   # = -13

    # Main frame slab
    frame = cq.Workplane("XY").box(bL, bY, bH).translate((0, 0, -bH/2 - 1))

    # Bolster cross-beams
    for ys in [1, -1]:
        beam = cq.Workplane("XY").box(bL-6, 6, bH-4).translate((0, ys*bY/2, -bH/2-1))
        frame = frame.union(beam)

    # Pivot pin (sticks up into chassis)
    pin = cq.Workplane("XY").circle(BP_D/2).extrude(BP_H).translate((0, 0, 0))
    frame = frame.union(pin)

    # Pivot collar (retaining flange at top of pin)
    collar = cq.Workplane("XY").circle(BP_D/2+3).extrude(3).translate((0, 0, BP_H-3))
    frame = frame.union(collar)

    # Axle-box legs (hang down from bogie bottom to axle level)
    leg_h = abs(AZ) - bH - 2
    for ax_x in [bwb/2, -bwb/2]:
        for ys in [1, -1]:
            leg = cq.Workplane("XY").box(12, 9, leg_h).translate(
                (ax_x, ys*(GA/2+WW/2+1), BOGIE_BOT_Z - leg_h/2))
            frame = frame.union(leg)
            # Axle hole through leg in Y direction (press-fit)
            bore_len = GA + WW*2 + 24
            axle_hole = (cq.Workplane("XZ").circle(AD/2)
                         .extrude(bore_len)
                         .translate((ax_x, -bore_len/2, AZ)))
            frame = frame.cut(axle_hole)

    return frame


# ═══════════════════════════════════════════════════════════
# PART 06: PIVOT BRACKET  (mounts on inner vehicle ends)
#   A fork bracket with a 5mm pivot pin.
#   Mounts flush against the vehicle end face.
# ═══════════════════════════════════════════════════════════
def mk_pivot_bracket():
    """
    Coupler mounting bracket. Print 4×.
    Has a fork opening (Y-direction) with a 5mm vertical pin.
    The drawbar's fork slides over this pin.
    """
    hz = AZ + WD/2 + 16   # vertical centre of coupler

    # Mounting plate (attaches to vehicle end)
    plate = cq.Workplane("XY").box(5, 22, 28).translate((2.5, 0, hz))

    # Fork arms (two prongs extending out in X)
    fork_l = 12
    for ys in [1, -1]:
        arm = cq.Workplane("XY").box(fork_l, 5, 6).translate((5+fork_l/2, ys*6, hz))
        plate = plate.union(arm)

    # Pivot pin (vertical, between fork prongs)
    pin = (cq.Workplane("XY").circle(CP_D/2).extrude(16)
           .translate((5+fork_l/2, 0, hz-4)))
    plate = plate.union(pin)

    # Gusset for strength
    gusset = cq.Workplane("XY").box(5, 22, 5).translate((2.5, 0, hz-14))
    plate = plate.union(gusset)

    return plate


# ═══════════════════════════════════════════════════════════
# PART 07: DRAWBAR  (connects two vehicles)
#   Fork holes at each end accept the bracket pivot pins.
#   Thin middle section provides slight flex (acts as spring).
#   Total length ~50mm (extends 5mm into each vehicle gap end)
# ═══════════════════════════════════════════════════════════
def mk_drawbar():
    """
    Articulating drawbar. Print 2×.
    Each end has a fork with 5.4mm holes (rotates on bracket pin).
    Thin midsection (3mm wide) provides flex like a spring.
    """
    hz = AZ + WD/2 + 16   # same vertical centre as bracket

    # Main bar body
    bar = cq.Workplane("XY").box(44, 8, 6).translate((0, 0, hz))

    # Thin flex section in middle (spring effect)
    flex_cut = cq.Workplane("XY").box(10, 3.5, 2).translate((0, 2.25, hz))
    flex_cut2= cq.Workplane("XY").box(10, 3.5, 2).translate((0,-2.25, hz))
    bar = bar.cut(flex_cut).cut(flex_cut2)

    # Fork end A (+X)
    for ys in [1, -1]:
        fork_a = cq.Workplane("XY").box(8, 4, 10).translate((26, ys*6, hz))
        bar = bar.union(fork_a)
    # Pivot hole in fork A (Y-direction)
    hole_a = (cq.Workplane("XZ").circle(CF_D/2).extrude(30)
              .translate((26, -15, hz)))
    bar = bar.cut(hole_a)

    # Fork end B (-X)
    for ys in [1, -1]:
        fork_b = cq.Workplane("XY").box(8, 4, 10).translate((-26, ys*6, hz))
        bar = bar.union(fork_b)
    # Pivot hole in fork B
    hole_b = (cq.Workplane("XZ").circle(CF_D/2).extrude(30)
              .translate((-26, -15, hz)))
    bar = bar.cut(hole_b)

    return bar


# ═══════════════════════════════════════════════════════════
# CHASSIS HELPER (pivot holes punched in underframe)
# ═══════════════════════════════════════════════════════════
def punch_bogie_holes(chassis, cx_list):
    """Cut bogie pivot holes into chassis underframe."""
    for bx in cx_list:
        hole = (cq.Workplane("XY").circle(CH_D/2)
                .extrude(TH_B + 5)
                .translate((bx, 0, -2)))
        chassis = chassis.cut(hole)
    return chassis


# ═══════════════════════════════════════════════════════════
# PART 01: LOCOMOTIVE BODY (separate, no bogies)
# ═══════════════════════════════════════════════════════════
def mk_loco_body():
    H=74; BZ=TH_B

    # Chassis slab
    chassis = cq.Workplane("XY").box(LL, TW, TH_B).translate((LOX, 0, TH_B/2))
    # Bogie pivot holes
    chassis = punch_bogie_holes(chassis, [LOX+LBGX, LOX-LBGX])
    # Bracket screw-boss (for pivot bracket mounting) — rear inner end
    boss_rear = cq.Workplane("XY").box(6,22,10).translate((LOX-LL/2+3,0,TH_B+5))
    chassis = chassis.union(boss_rear)

    # Main body shell (open top)
    main_l=LL-46; main_cx=LOX-23
    outer = cq.Workplane("XY").box(main_l,TW,H).translate((main_cx,0,H/2+BZ))
    inner = cq.Workplane("XY").box(main_l-6,TW-WALL*2,H+6).translate(
        (main_cx,0,H/2+BZ+WALL/2+3))
    shell = outer.cut(inner)

    # Cab with aero nose
    cab_l=48; cab_cx=LOX+LL/2-cab_l/2; cab_h=H+12
    cab_o = cq.Workplane("XY").box(cab_l,TW,cab_h).translate((cab_cx,0,cab_h/2+BZ))
    cab_i = cq.Workplane("XY").box(cab_l-6,TW-WALL*2,cab_h+6).translate(
        (cab_cx,0,cab_h/2+BZ+WALL/2+3))
    cab = cab_o.cut(cab_i)
    nose = cq.Workplane("XY").box(cab_l,TW+4,cab_h*0.42).translate(
        (cab_cx+cab_l*0.13,0,cab_h*0.80+BZ))
    cab = cab.cut(nose)
    shell = shell.union(cab)

    # Windshield
    ws = cq.Workplane("XY").box(WALL+4,TW-20,H*0.30).translate(
        (LOX+LL/2-WALL/2-1,0,H*0.68+BZ))
    shell = shell.cut(ws)

    # Side windows
    for xi in [-96,-68,-40,-12,16]:
        for ys in [1,-1]:
            w = cq.Workplane("XY").box(22,WALL+4,20).translate(
                (LOX+xi,ys*TW/2,H*0.56+BZ))
            shell = shell.cut(w)

    # Headlights
    for ys in [1,-1]:
        hl = cq.Workplane("XZ").circle(5).extrude(WALL+3).translate(
            (LOX+LL/2,ys*(TW/2-16),H*0.22+BZ))
        shell = shell.union(hl)

    # Vents
    for xi in [-132,-115]:
        for ys in [1,-1]:
            g = cq.Workplane("XY").box(12,WALL+4,14).translate(
                (LOX+xi,ys*TW/2,H*0.30+BZ))
            shell = shell.cut(g)

    # Pantograph
    bz2=H+BZ+4
    pbase = cq.Workplane("XY").box(52,30,5).translate((LOX+28,0,bz2+2.5))
    for xs in [1,-1]:
        a = cq.Workplane("XZ").box(3,28,3).translate((LOX+28+xs*9,10,bz2+16))
        b = cq.Workplane("XZ").box(3,28,3).translate((LOX+28+xs*9,-10,bz2+16))
        pbase=pbase.union(a).union(b)
    strip = cq.Workplane("XY").box(68,5,4).translate((LOX+28,0,bz2+30))
    pbase = pbase.union(strip)

    return chassis.union(shell).union(pbase)


# ═══════════════════════════════════════════════════════════
# PART 02: WAGON BODY (separate, no bogies, print 2×)
# ═══════════════════════════════════════════════════════════
def mk_wagon_body_part(wx):
    H=70; BZ=TH_B

    # Chassis slab
    chassis = cq.Workplane("XY").box(WL,TW,TH_B).translate((wx,0,TH_B/2))
    chassis = punch_bogie_holes(chassis, [wx+WBGX, wx-WBGX])
    # Bracket bosses (both inner ends for this generic body)
    for xs in [1,-1]:
        boss = cq.Workplane("XY").box(6,22,10).translate((wx+xs*WL/2-xs*3,0,TH_B+5))
        chassis = chassis.union(boss)

    # Body shell (open top)
    outer = cq.Workplane("XY").box(WL,TW,H).translate((wx,0,H/2+BZ))
    inner = cq.Workplane("XY").box(WL-6,TW-WALL*2,H+6).translate(
        (wx,0,H/2+BZ+WALL/2+3))
    shell = outer.cut(inner)

    # Passenger windows
    for xi in [-65,-39,-13,13,39,65]:
        for ys in [1,-1]:
            w = cq.Workplane("XY").box(24,WALL+4,26).translate(
                (wx+xi,ys*TW/2,H*0.60+BZ))
            shell = shell.cut(w)

    # End doors
    for xs2 in [1,-1]:
        d = cq.Workplane("XY").box(WALL+4,32,44).translate(
            (wx+xs2*WL/2,0,H*0.38+BZ))
        shell = shell.cut(d)

    # Side doors
    for ys in [1,-1]:
        sd = cq.Workplane("XY").box(24,WALL+4,44).translate(
            (wx,ys*TW/2,H*0.38+BZ))
        shell = shell.cut(sd)

    # Blue accent stripe
    for ys in [1,-1]:
        stripe = cq.Workplane("XY").box(WL-8,WALL,8).translate(
            (wx,ys*(TW/2+WALL/2),H*0.26+BZ))
        shell = shell.union(stripe)

    return chassis.union(shell)


# ═══════════════════════════════════════════════════════════
# GENERATE ALL PARTS
# ═══════════════════════════════════════════════════════════
def export(part, name):
    path = os.path.join(KIT, name)
    cq.exporters.export(part, path)
    kb = os.path.getsize(path)/1024
    print(f"  → {name}  ({kb:.0f} KB)")
    return path

print("=" * 62)
print("  BUILDING COMPLETE ASSEMBLY KIT")
print(f"  Total train length: {TOTAL} mm  (limit: 600 mm)")
print(f"  Width: {TW} mm  |  Wheel: {WD} mm (1.5 cm)")
print(f"  Bogies: rotating pivot-pin type")
print(f"  Couplers: pivot-bracket + articulating drawbar")
print("=" * 62)

print("\n[PART 04] Wheel 15mm — print 24×")
export(mk_wheel(), "04_WHEEL_15mm.stl")

print("\n[PART 05] Axle — print 12×")
export(mk_axle(), "05_AXLE.stl")

print("\n[PART 03] Bogie frame (with pivot pin) — print 6×")
export(mk_bogie_standalone(LBWB), "03_BOGIE_FRAME.stl")

print("\n[PART 06] Pivot bracket — print 4×")
export(mk_pivot_bracket(), "06_PIVOT_BRACKET.stl")

print("\n[PART 07] Drawbar (articulating) — print 2×")
export(mk_drawbar(), "07_DRAWBAR.stl")

print("\n[PART 01] Locomotive body (with pivot holes) — print 1×")
export(mk_loco_body(), "01_LOCO_BODY.stl")

print("\n[PART 02] Wagon body — print 2× (both identical)")
export(mk_wagon_body_part(0), "02_WAGON_BODY.stl")   # centred at 0 for standalone

# Final summary
print(f"\n{'='*62}")
files = [(f, os.path.getsize(os.path.join(KIT,f))//1024) for f in sorted(os.listdir(KIT))]
total_kb = sum(s for _,s in files)
for f,s in files:
    count = {
        "01_LOCO_BODY.stl":1,"02_WAGON_BODY.stl":2,
        "03_BOGIE_FRAME.stl":6,"04_WHEEL_15mm.stl":24,
        "05_AXLE.stl":12,"06_PIVOT_BRACKET.stl":4,
        "07_DRAWBAR.stl":2
    }.get(f,1)
    print(f"  {f:<28}  {s:>5} KB   print {count}×")
print(f"  {'─'*50}")
print(f"  Total kit size: {total_kb} KB")
print(f"{'='*62}")
print("""
ASSEMBLY GUIDE:
  Step 1 — Press axle into bogie axle-box holes (tight fit)
  Step 2 — Slide 2 wheels onto each axle end (spinning fit)
  Step 3 — Insert bogie pivot pin UP into chassis hole
            (12mm pin → 12.4mm hole, bogie rotates freely)
  Step 4 — Attach pivot brackets to inner vehicle ends
  Step 5 — Clip drawbar onto bracket pins (5mm → 5.4mm hole)
            Vehicles can now pivot for curves!
  Step 6 — Repeat for both inter-vehicle junctions
""")
print("DONE!")
