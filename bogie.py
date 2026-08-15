"""
06_BOGIE — Bogie frame with integrated axle housings, suspension seats,
brake mounts, and central pivot post.
One bogie module produces a single bogie; call twice for front and rear.
"""
import cadquery as cq
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import parameters as P


def build_bogie() -> cq.Assembly:
    BL  = P.BOGIE_LENGTH
    BW  = P.BOGIE_WIDTH
    BH  = P.BOGIE_HEIGHT
    FT  = P.BOGIE_FRAME_T
    WB  = P.BOGIE_WHEELBASE   # centre-to-centre axle distance
    PD  = P.BOGIE_PIVOT_D
    PL  = P.BOGIE_PIVOT_L
    BD  = P.BEARING_OD + 2    # bearing pocket outer boss

    # ── Main frame (hollow rectangular) ───────────────────────
    outer = (
        cq.Workplane("XY")
        .box(BL, BW, BH)
        .edges("|Z").fillet(3)
        .edges(">Z or <Z").fillet(1.5)
    )
    inner = (
        cq.Workplane("XY")
        .box(BL - 2*FT, BW - 2*FT, BH - FT)
        .translate((0, 0, FT/2))
        .edges("|Z").fillet(max(2, 1))
    )
    frame = outer.cut(inner)

    # ── Axle saddles (2× at ±WB/2) ────────────────────────────
    axle_saddle_w  = P.AXLE_LENGTH + 2        # slightly wider than axle
    axle_saddle_h  = P.BEARING_OD + 3         # enough to hold bearing boss

    for ax in [-WB/2, WB/2]:
        saddle = (
            cq.Workplane("XY")
            .center(ax, 0)
            .box(FT + 2, axle_saddle_w, axle_saddle_h)
            .translate((0, 0, -BH/2 + axle_saddle_h/2))
        )
        # Bearing cylindrical recesses on both ends
        for by in [-axle_saddle_w/2 + P.BEARING_H/2,
                    axle_saddle_w/2 - P.BEARING_H/2]:
            brg = (
                cq.Workplane("XY")
                .center(ax, by)
                .circle(P.BEARING_OD/2 + 1.5)
                .extrude(P.BEARING_H + 1)
                .translate((0, 0, -BH/2 - P.BEARING_H/2))
            )
            frame = frame.union(brg)
            # Cavity for bearing insert
            cavity = (
                cq.Workplane("XY")
                .center(ax, by)
                .circle(P.BEARING_CAVITY_D/2)
                .extrude(P.BEARING_CAVITY_H + 0.2)
                .translate((0, 0, -BH/2 - P.BEARING_CAVITY_H - 0.1))
            )
            frame = frame.cut(cavity)
            # Axle through-hole
            axle_hole = (
                cq.Workplane("XY")
                .center(ax, by)
                .circle((P.AXLE_DIAMETER + P.PRINT_CLEARANCE)/2)
                .extrude(BH + 10)
                .translate((0, 0, -BH/2 - 5))
            )
            frame = frame.cut(axle_hole)

    # ── Central pivot post (male, engages chassis boss) ───────
    pivot = (
        cq.Workplane("XY")
        .circle((PD - P.PRINT_CLEARANCE)/2)
        .extrude(PL + 2)
        .translate((0, 0, BH/2))
    )
    # Head flange to retain
    flange = (
        cq.Workplane("XY")
        .circle(PD/2 + 2)
        .extrude(2)
        .translate((0, 0, BH/2 + PL))
    )
    frame = frame.union(pivot).union(flange)

    # ── Suspension towers (×2 per side, 4 total) ──────────────
    susp_xs = [-WB/2, WB/2]
    susp_ys = [-BW/2 + FT, BW/2 - FT]
    for sx in susp_xs:
        for sy_sign, sy in zip([-1, 1], susp_ys):
            tower = (
                cq.Workplane("XY")
                .center(sx, sy)
                .box(P.SUSPENSION_W, FT + 2, P.SUSPENSION_H)
                .translate((0, 0, BH/2 - P.SUSPENSION_H/2 + FT))
            )
            # Spring seat hole
            seat = (
                cq.Workplane("XY")
                .center(sx, sy)
                .circle(P.SUSPENSION_SPRING_D/2 + 0.3)
                .extrude(P.SUSPENSION_H * 0.6)
                .translate((0, 0, BH/2 + FT))
            )
            frame = frame.union(tower).cut(seat)

    # ── Brake bracket mounts (×4) ────────────────────────────
    for bx in susp_xs:
        for by in [-BW/4, BW/4]:
            bm = (
                cq.Workplane("XY")
                .center(bx, by)
                .box(P.BRAKE_BRACKET_T + 1, 4, 8)
                .translate((0, 0, -BH/2 + 4))
            )
            # M2 bolt hole
            bhole = (
                cq.Workplane("XY")
                .center(bx, by)
                .circle(1.2)
                .extrude(6)
                .translate((0, 0, -BH/2 + 1))
            )
            frame = frame.union(bm).cut(bhole)

    asm = cq.Assembly()
    asm.add(frame, name="bogie_frame", color=cq.Color(0.42, 0.42, 0.42))
    return asm


def export(out_dir: str = P.OUTPUT_DIR):
    os.makedirs(out_dir, exist_ok=True)
    asm = build_bogie()
    wp = asm.toCompound()
    if P.EXPORT_STEP:
        cq.exporters.export(wp, os.path.join(out_dir, "06_bogie.step"))
    if P.EXPORT_STL:
        cq.exporters.export(
            wp, os.path.join(out_dir, "06_bogie.stl"),
            exportType="STL", tolerance=P.STL_TOLERANCE,
            angularTolerance=P.STL_ANGULAR_TOL,
        )
    print("  [06] Bogie exported.")


if __name__ == "__main__":
    export()
