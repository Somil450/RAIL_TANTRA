"""
08_AXLE — Stepped axle with journal ends for bearing seats and
flat/D-cut for wheel press-fit or keyed connection.
"""
import cadquery as cq
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import parameters as P


def build_axle() -> cq.Assembly:
    AD  = P.AXLE_DIAMETER
    AEL = P.AXLE_END_D          # journal (smaller) diameter
    AL  = P.AXLE_LENGTH
    JL  = 6.0                   # journal length each side

    # ── Main shaft ───────────────────────────────────────────
    shaft = (
        cq.Workplane("YZ")
        .circle(AD / 2)
        .extrude(AL)
        .translate((0, 0, 0))
    )

    # ── Journals (reduced diameter at ends for bearing seats) ─
    for side in [-1, 1]:
        cx = side * (AL / 2 + JL / 2)
        journal = (
            cq.Workplane("YZ")
            .circle(AEL / 2)
            .extrude(JL)
            .translate((cx - side * JL / 2, 0, 0))
        )
        shaft = shaft.union(journal)

    # ── D-flat on shaft ends for wheel anti-rotation ──────────
    # Cut a small flat on each side of the shaft where wheel sits
    flat_depth = AD / 2 - AD * 0.25   # leaves ~half-circle
    for side in [-1, 1]:
        flat = (
            cq.Workplane("XZ")
            .center(0, 0)
            .rect(AD * 2, AL * 0.3)
            .extrude(flat_depth)
            .translate((0, side * (AD / 2), 0))
            .translate((side * (AL * 0.35), 0, 0))
        )
        shaft = shaft.cut(flat)

    # ── Retention rings (integral snap ring grooves) ──────────
    for side in [-1, 1]:
        groove_x = side * (AL / 2 - 3)
        groove = (
            cq.Workplane("YZ")
            .circle(AD / 2 + 0.01)   # just outside shaft
            .extrude(2)
            .translate((groove_x - 1, 0, 0))
        )
        groove_cut = (
            cq.Workplane("YZ")
            .circle(AD / 2 - 0.8)
            .extrude(2)
            .translate((groove_x - 1, 0, 0))
        )
        ring = groove.cut(groove_cut)
        shaft = shaft.union(ring)

    asm = cq.Assembly()
    asm.add(shaft, name="axle", color=cq.Color(0.75, 0.75, 0.75))
    return asm


def export(out_dir: str = P.OUTPUT_DIR):
    os.makedirs(out_dir, exist_ok=True)
    asm = build_axle()
    wp = asm.toCompound()
    if P.EXPORT_STEP:
        cq.exporters.export(wp, os.path.join(out_dir, "08_axle.step"))
    if P.EXPORT_STL:
        cq.exporters.export(
            wp, os.path.join(out_dir, "08_axle.stl"),
            exportType="STL", tolerance=P.STL_TOLERANCE,
            angularTolerance=P.STL_ANGULAR_TOL,
        )
    print("  [08] Axle exported.")


if __name__ == "__main__":
    export()
