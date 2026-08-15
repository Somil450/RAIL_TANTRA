"""
09_BEARING_HOUSING — Split cylindrical bearing housing that accepts
a 10mm OD × 6mm ID miniature ball bearing.
Designed to press into the bogie axle saddle pockets.
"""
import cadquery as cq
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import parameters as P


def build_bearing_housing() -> cq.Assembly:
    OD  = P.BEARING_OD          # housing outer diameter
    ID  = P.BEARING_ID          # axle clearance bore
    H   = P.BEARING_H           # housing height
    CD  = P.BEARING_CAVITY_D    # bearing insert cavity diameter
    CH  = P.BEARING_CAVITY_H    # bearing insert cavity depth
    FT  = 2.0                   # flange thickness
    FD  = OD + 4                # flange outer diameter

    # ── Outer cylinder ────────────────────────────────────────
    outer = (
        cq.Workplane("XY")
        .circle(OD / 2)
        .extrude(H)
    )

    # ── Flange ────────────────────────────────────────────────
    flange = (
        cq.Workplane("XY")
        .circle(FD / 2)
        .extrude(FT)
        .translate((0, 0, H - FT))
    )
    housing = outer.union(flange)

    # ── Bearing cavity (from flange end) ─────────────────────
    cavity = (
        cq.Workplane("XY")
        .circle(CD / 2)
        .extrude(CH)
        .translate((0, 0, H - CH))
    )
    housing = housing.cut(cavity)

    # ── Axle bore through entire housing ─────────────────────
    bore = (
        cq.Workplane("XY")
        .circle(ID / 2)
        .extrude(H + FT + 1)
    )
    housing = housing.cut(bore)

    # ── Retention lip (slight undercut for snap-in) ───────────
    lip = (
        cq.Workplane("XY")
        .circle(CD / 2 + 0.6)
        .extrude(1)
        .translate((0, 0, H - CH - 1))
    )
    housing = housing.cut(lip)

    # ── Anti-rotation flat on outer ──────────────────────────
    flat = (
        cq.Workplane("YZ")
        .rect(OD, H)
        .extrude(1.0)
        .translate((OD / 2 - 0.2, 0, H / 2))
    )
    housing = housing.cut(flat)

    asm = cq.Assembly()
    asm.add(housing, name="bearing_housing", color=cq.Color("lightgray"))
    return asm


def export(out_dir: str = P.OUTPUT_DIR):
    os.makedirs(out_dir, exist_ok=True)
    asm = build_bearing_housing()
    wp = asm.toCompound()
    if P.EXPORT_STEP:
        cq.exporters.export(wp, os.path.join(out_dir, "09_bearing_housing.step"))
    if P.EXPORT_STL:
        cq.exporters.export(
            wp, os.path.join(out_dir, "09_bearing_housing.stl"),
            exportType="STL", tolerance=P.STL_TOLERANCE,
            angularTolerance=P.STL_ANGULAR_TOL,
        )
    print("  [09] Bearing housing exported.")


if __name__ == "__main__":
    export()
