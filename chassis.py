"""
01_CHASSIS — Main structural chassis for the smart train.
Includes floor plate, perimeter walls, longitudinal/transverse ribs,
bogie mounting bosses, body mounting bosses, and screw holes.
"""
import cadquery as cq
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import parameters as P


def build_chassis() -> cq.Assembly:
    L  = P.CHASSIS_LENGTH
    W  = P.CHASSIS_WIDTH
    T  = P.CHASSIS_THICKNESS
    RH = P.CHASSIS_RIB_H
    RT = P.CHASSIS_RIB_T
    BD = P.BOGIE_PIVOT_D + 2 * 3        # boss outer diameter
    BH = P.BOGIE_PIVOT_L + 2            # boss height
    BS = P.BOGIE_SPACING / 2            # ±distance from centre

    # ── Floor plate ──────────────────────────────────────────
    floor = (
        cq.Workplane("XY")
        .box(L, W, T)
        .edges("|Z").fillet(3)
    )

    # ── Perimeter walls (upward) ─────────────────────────────
    wall_h = RH + T
    outer_box = (
        cq.Workplane("XY")
        .box(L, W, wall_h)
        .edges("|Z").fillet(3)
        .shell(-P.BODY_WALL_THICKNESS)
    )
    # Trim bottom flush with floor
    cutter = cq.Workplane("XY").box(L + 10, W + 10, wall_h).translate((0, 0, -(wall_h / 2 + T / 2)))
    walls = outer_box.cut(cutter)

    # ── Longitudinal ribs (4 ribs along X axis) ──────────────
    rib_positions_y = [-W / 4, W / 4]
    rib_shapes = []
    for yp in rib_positions_y:
        r = (
            cq.Workplane("XY")
            .center(0, yp)
            .box(L - 10, RT, RH)
            .translate((0, 0, T / 2 + RH / 2))
        )
        rib_shapes.append(r)

    # ── Transverse ribs (every ~60 mm) ───────────────────────
    n_trans = int(L / 60)
    trans_positions = [
        -L / 2 + (i + 0.5) * (L / n_trans)
        for i in range(n_trans)
    ]
    trans_ribs = []
    for xp in trans_positions:
        r = (
            cq.Workplane("XY")
            .center(xp, 0)
            .box(RT, W - 4, RH)
            .translate((0, 0, T / 2 + RH / 2))
        )
        trans_ribs.append(r)

    # ── Bogie pivot bosses (2×, with central through-hole) ───
    boss_front = (
        cq.Workplane("XY")
        .circle(BD / 2)
        .extrude(BH)
        .translate(( BS, 0, T / 2))
        .faces(">Z")
        .workplane()
        .hole(P.BOGIE_PIVOT_D + P.PRINT_CLEARANCE)
    )
    boss_rear = (
        cq.Workplane("XY")
        .circle(BD / 2)
        .extrude(BH)
        .translate((-BS, 0, T / 2))
        .faces(">Z")
        .workplane()
        .hole(P.BOGIE_PIVOT_D + P.PRINT_CLEARANCE)
    )

    # ── Body screw bosses (4 corners + 2 centre) ─────────────
    boss_xy = [
        ( L / 2 - 20,  W / 2 - 10),
        ( L / 2 - 20, -W / 2 + 10),
        (-L / 2 + 20,  W / 2 - 10),
        (-L / 2 + 20, -W / 2 + 10),
        ( 0,  W / 2 - 10),
        ( 0, -W / 2 + 10),
    ]
    body_bosses = []
    for bx, by in boss_xy:
        b = (
            cq.Workplane("XY")
            .center(bx, by)
            .circle(P.BOSS_D / 2)
            .extrude(P.BOSS_H)
            .translate((0, 0, T / 2))
            .faces(">Z")
            .workplane()
            .hole(P.SCREW_D_M3)
        )
        body_bosses.append(b)

    # ── Merge everything ─────────────────────────────────────
    result = floor.union(walls)
    for s in rib_shapes + trans_ribs:
        result = result.union(s)
    result = result.union(boss_front).union(boss_rear)
    for b in body_bosses:
        result = result.union(b)

    asm = cq.Assembly()
    asm.add(result, name="chassis", color=cq.Color("gray"))
    return asm


def export(out_dir: str = P.OUTPUT_DIR):
    os.makedirs(out_dir, exist_ok=True)
    asm = build_chassis()
    wp = asm.toCompound()
    if P.EXPORT_STEP:
        cq.exporters.export(wp, os.path.join(out_dir, "01_chassis.step"))
    if P.EXPORT_STL:
        cq.exporters.export(
            wp,
            os.path.join(out_dir, "01_chassis.stl"),
            exportType="STL",
            tolerance=P.STL_TOLERANCE,
            angularTolerance=P.STL_ANGULAR_TOL,
        )
    print("  [01] Chassis exported.")


if __name__ == "__main__":
    export()
