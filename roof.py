"""
05_ROOF — Removable roof panel with crown curvature,
ventilation equipment housings, and clip tabs.
"""
import cadquery as cq
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import parameters as P


def build_roof() -> cq.Assembly:
    L   = P.BODY_LENGTH - 2          # slight clearance
    W   = P.BODY_WIDTH  - 2 * P.BODY_WALL_THICKNESS - P.PRINT_CLEARANCE
    T   = P.ROOF_THICKNESS
    CH  = P.ROOF_CROWN_H
    EH  = P.ROOF_EQUIP_H
    CD  = P.ROOF_CLIP_DEPTH
    CW  = P.ROOF_CLIP_W

    # ── Flat base panel ───────────────────────────────────────
    base = (
        cq.Workplane("XY")
        .box(L, W, T)
        .edges("|Z").fillet(3)
    )

    # ── Crown profile (curved top) — approximate with 3 steps
    for i, hz in enumerate([CH * 0.4, CH * 0.75, CH]):
        ww = W - (i + 1) * 4
        strip = (
            cq.Workplane("XY")
            .box(L - 2, ww, T * 0.6)
            .translate((0, 0, T/2 + hz - T * 0.3))
            .edges("|Z").fillet(2)
        )
        base = base.union(strip)

    # ── Rooftop HVAC / equipment box ─────────────────────────
    equip_positions = [
        (-L * 0.25, 0, EH),
        ( L * 0.20, 0, EH * 0.7),
    ]
    for ex, ey, eh in equip_positions:
        box = (
            cq.Workplane("XY")
            .center(ex, ey)
            .box(30, 18, eh)
            .edges("|Z").fillet(2)
            .translate((0, 0, T/2 + CH + eh/2 - 1))
        )
        base = base.union(box)
        # Grille slits on the side
        for slot_z in range(3):
            slit = (
                cq.Workplane("YZ")
                .center(ey, T/2 + CH + 4 + slot_z * 3)
                .rect(14, 1.2)
                .extrude(2)
                .translate((ex + 16, 0, 0))
            )
            base = base.cut(slit)

    # ── Pantograph mount pad ──────────────────────────────────
    panto_pad = (
        cq.Workplane("XY")
        .center(L * 0.30, 0)
        .box(P.PANTO_BASE_L + 4, P.PANTO_BASE_W + 4, 3)
        .translate((0, 0, T/2 + CH + 1.5))
        .edges("|Z").fillet(1)
    )
    base = base.union(panto_pad)
    # M3 mounting holes for pantograph
    for px, py in [( L*0.30 + 15, 6), (L*0.30 + 15, -6),
                   ( L*0.30 - 15, 6), (L*0.30 - 15, -6)]:
        mh = (
            cq.Workplane("XY")
            .center(px, py)
            .circle(P.SCREW_D_M3 / 2)
            .extrude(T + CH + 4)
        )
        base = base.cut(mh)

    # ── Clip tabs (×4 per side snapping into body wall) ───────
    clip_xs = [-L * 0.35, -L * 0.12, L * 0.12, L * 0.35]
    for cx in clip_xs:
        for sy in [1, -1]:
            tab = (
                cq.Workplane("XY")
                .center(cx, sy * (W / 2))
                .box(CW, CD + 2, 8)
                .translate((0, 0, -4 - T/2))
                .edges("|Z").fillet(1)
            )
            # Snap lip
            lip = (
                cq.Workplane("XY")
                .center(cx, sy * (W / 2 + CD / 2 + 0.5))
                .box(CW, 1.5, 2)
                .translate((0, 0, -8))
            )
            base = base.union(tab).union(lip)

    asm = cq.Assembly()
    asm.add(base, name="roof", color=cq.Color("darkslategray"))
    return asm


def export(out_dir: str = P.OUTPUT_DIR):
    os.makedirs(out_dir, exist_ok=True)
    asm = build_roof()
    wp = asm.toCompound()
    if P.EXPORT_STEP:
        cq.exporters.export(wp, os.path.join(out_dir, "05_roof.step"))
    if P.EXPORT_STL:
        cq.exporters.export(
            wp, os.path.join(out_dir, "05_roof.stl"),
            exportType="STL", tolerance=P.STL_TOLERANCE,
            angularTolerance=P.STL_ANGULAR_TOL,
        )
    print("  [05] Roof exported.")


if __name__ == "__main__":
    export()
