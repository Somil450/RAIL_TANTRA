"""
11_BRAKES — Simplified railway brake assembly.
Includes brake pad, mounting bracket, and actuator arm.
Positioned close to wheel tread without colliding.
"""
import cadquery as cq
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import parameters as P


def build_brake_assembly() -> cq.Assembly:
    PL = P.BRAKE_PAD_L
    PW = P.BRAKE_PAD_W
    PT = P.BRAKE_PAD_T
    BT = P.BRAKE_BRACKET_T
    WR = P.WHEEL_DIAMETER / 2   # wheel radius
    WT = P.WHEEL_THICKNESS

    # ── Brake pad ─────────────────────────────────────────────
    # Curved face matching wheel radius
    pad = (
        cq.Workplane("XY")
        .box(PL, PW, PT)
        .edges("|Y").fillet(0.5)
    )

    # ── Mounting bracket ──────────────────────────────────────
    bracket_h = 16.0
    bracket = (
        cq.Workplane("XY")
        .box(BT + 2, PW, bracket_h)
        .translate((-PL/2 - BT/2 - 1, 0, -bracket_h/2 + PT/2))
    )

    # ── Bracket cross-member ──────────────────────────────────
    cross = (
        cq.Workplane("XY")
        .box(PL + BT + 4, BT + 1, BT)
        .translate((-1, 0, -bracket_h/2 + BT/2))
    )

    # ── Bolt holes in bracket ────────────────────────────────
    for bz in [-bracket_h/2 + 3, -bracket_h/2 + 12]:
        bh = (
            cq.Workplane("YZ")
            .center(0, bz + bracket_h/2 - PT/2)
            .circle(1.2)
            .extrude(BT + 4)
            .translate((-PL/2 - BT - 2, 0, 0))
        )
        bracket = bracket.cut(bh)

    # ── Actuator arm ─────────────────────────────────────────
    arm_l = 18.0
    arm = (
        cq.Workplane("XZ")
        .center(0, -bracket_h / 2 - arm_l / 2 + PT/2)
        .rect(BT + 1, arm_l)
        .extrude(BT)
        .translate((-PL/2 - BT/2 - 1, 0, 0))
    )
    arm_hole = (
        cq.Workplane("XY")
        .center(-PL/2 - BT - 1, 0)
        .circle(1.5)
        .extrude(8)
        .translate((0, 0, -bracket_h/2 - arm_l + 5))
    )
    arm = arm.cut(arm_hole)

    # ── Assemble ──────────────────────────────────────────────
    full = pad.union(bracket).union(cross).union(arm)

    asm = cq.Assembly()
    asm.add(full, name="brake_assembly", color=cq.Color(0.55, 0.0, 0.0))
    return asm


def export(out_dir: str = P.OUTPUT_DIR):
    os.makedirs(out_dir, exist_ok=True)
    asm = build_brake_assembly()
    wp = asm.toCompound()
    if P.EXPORT_STEP:
        cq.exporters.export(wp, os.path.join(out_dir, "11_brakes.step"))
    if P.EXPORT_STL:
        cq.exporters.export(
            wp, os.path.join(out_dir, "11_brakes.stl"),
            exportType="STL", tolerance=P.STL_TOLERANCE,
            angularTolerance=P.STL_ANGULAR_TOL,
        )
    print("  [11] Brakes exported.")


if __name__ == "__main__":
    export()
