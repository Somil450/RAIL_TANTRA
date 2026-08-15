"""
10_SUSPENSION — Coil-spring-style suspension tower component.
Provides a guide post and seat for a real 6mm OD compression spring.
One per axle end, 8 total per locomotive.
"""
import cadquery as cq
import os, sys, math
sys.path.insert(0, os.path.dirname(__file__))
import parameters as P


def build_suspension() -> cq.Assembly:
    SH   = P.SUSPENSION_H
    SW   = P.SUSPENSION_W
    SD   = P.SUSPENSION_SPRING_D   # spring outer diameter
    SW2  = P.SUSPENSION_SPRING_WIRE
    T    = P.BODY_WALL_THICKNESS

    # ── Outer guide cylinder ──────────────────────────────────
    outer = (
        cq.Workplane("XY")
        .circle(SW / 2)
        .extrude(SH)
    )

    # ── Spring seat bore (accepts spring) ─────────────────────
    bore = (
        cq.Workplane("XY")
        .circle(SD / 2 + 0.2)
        .extrude(SH - 3)          # 3mm solid base
        .translate((0, 0, 3))
    )
    outer = outer.cut(bore)

    # ── Inner locating post (inside spring) ───────────────────
    post_r = SD / 2 - SW2 - 0.5  # post radius < spring ID
    if post_r > 1.5:
        post = (
            cq.Workplane("XY")
            .circle(post_r)
            .extrude(SH * 0.55)
            .translate((0, 0, 3))
        )
        outer = outer.union(post)

    # ── Mounting tab (flat with M2 bolt hole for bogie) ───────
    tab = (
        cq.Workplane("XY")
        .rect(SW + 6, 4)
        .extrude(3)
        .translate((0, 0, -1.5))
    )
    outer = outer.union(tab)

    # ── Mounting holes in tab ────────────────────────────────
    for hx in [-SW/2 - 1.5, SW/2 + 1.5]:
        h = (
            cq.Workplane("XY")
            .center(hx, 0)
            .circle(1.2)
            .extrude(4)
        )
        outer = outer.cut(h)

    # ── Decorative coil representation on outside ─────────────
    # Not strictly necessary but adds visual detail
    coil_turns = 6
    for i in range(coil_turns):
        z = 5 + i * (SH - 8) / coil_turns
        ring = (
            cq.Workplane("XY")
            .translate((0, 0, z))
            .circle(SW / 2 + 0.8)
            .extrude(SW2 * 0.8)
        )
        ring_inner = (
            cq.Workplane("XY")
            .translate((0, 0, z))
            .circle(SW / 2 - 0.1)
            .extrude(SW2 * 0.8)
        )
        coil = ring.cut(ring_inner)
        outer = outer.union(coil)

    asm = cq.Assembly()
    asm.add(outer, name="suspension", color=cq.Color("goldenrod"))
    return asm


def export(out_dir: str = P.OUTPUT_DIR):
    os.makedirs(out_dir, exist_ok=True)
    asm = build_suspension()
    wp = asm.toCompound()
    if P.EXPORT_STEP:
        cq.exporters.export(wp, os.path.join(out_dir, "10_suspension.step"))
    if P.EXPORT_STL:
        cq.exporters.export(
            wp, os.path.join(out_dir, "10_suspension.stl"),
            exportType="STL", tolerance=P.STL_TOLERANCE,
            angularTolerance=P.STL_ANGULAR_TOL,
        )
    print("  [10] Suspension exported.")


if __name__ == "__main__":
    export()
