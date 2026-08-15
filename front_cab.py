"""
04_FRONT_CAB — Streamlined locomotive front cab with sloped windshield,
cab windows, headlight housings, and front bumper.
"""
import cadquery as cq
import os, sys, math
sys.path.insert(0, os.path.dirname(__file__))
import parameters as P


def build_front_cab() -> cq.Assembly:
    L  = P.CAB_LENGTH
    W  = P.BODY_WIDTH
    H  = P.BODY_HEIGHT
    T  = P.BODY_WALL_THICKNESS
    ang = math.radians(P.CAB_WINDSHIELD_ANGLE)

    # ── Base box for cab ──────────────────────────────────────
    cab_box = (
        cq.Workplane("XY")
        .box(L, W, H)
        .edges("|Z").fillet(P.BODY_CORNER_R)
    )

    # ── Slope the front face (windshield angle) ────────────────
    #  Cut a wedge from the front top corner
    slope_depth = H * math.tan(ang)
    wedge = (
        cq.Workplane("YZ")
        .moveTo(-W / 2, H / 2)
        .lineTo( W / 2, H / 2)
        .lineTo( W / 2, H / 2 - 0.1)
        .lineTo(-W / 2, H / 2 - 0.1)
        .close()
        .extrude(slope_depth)
    )
    # A proper slope via vertices
    slope_pts = [
        (-W/2, H/2 - slope_depth),
        ( W/2, H/2 - slope_depth),
        ( W/2, H/2),
        (-W/2, H/2),
    ]
    slope_solid = (
        cq.Workplane("YZ")
        .polyline(slope_pts).close()
        .extrude(slope_depth + 2)
        .translate((L/2 - slope_depth - 2, 0, 0))
    )
    cab = cab_box.cut(slope_solid)

    # ── Hollow interior ──────────────────────────────────────
    inner = (
        cq.Workplane("XY")
        .box(L - 2*T, W - 2*T, H - T)
        .translate((0, 0, T/2))
        .edges("|Z").fillet(max(P.BODY_CORNER_R - T, 1))
    )
    cab = cab.cut(inner)

    # ── Windshield opening ───────────────────────────────────
    ws_w = W * 0.60
    ws_h = H * 0.30
    windshield = (
        cq.Workplane("YZ")
        .center(0, H * 0.65 - H/2)
        .rect(ws_w, ws_h)
        .extrude(T + 2)
        .translate((L/2 - T - 1, 0, 0))
    )
    cab = cab.cut(windshield)

    # ── Cab side windows (×2 each side) ──────────────────────
    for side_sign in [1, -1]:
        for wx in [L*0.20, L*0.45]:
            win = (
                cq.Workplane("XZ")
                .center(L/2 - wx, H*0.60 - H/2)
                .rect(P.WINDOW_W * 0.8, P.WINDOW_H)
                .extrude(T + 2)
                .translate((0, side_sign * (W/2 - T/2), 0))
            )
            cab = cab.cut(win)

    # ── Headlight housings (2×, front face) ──────────────────
    for hy in [-W * 0.25, W * 0.25]:
        hl = (
            cq.Workplane("XY")
            .center(L/2 - 2, hy)
            .circle(5)
            .extrude(3)
            .translate((0, 0, -H/2 + 12))
        )
        cab = cab.union(hl)
        # lens recess
        recess = (
            cq.Workplane("XY")
            .center(L/2 + 0.5, hy)
            .circle(3.5)
            .extrude(2)
            .translate((0, 0, -H/2 + 12))
        )
        cab = cab.cut(recess)

    # ── Front bumper ─────────────────────────────────────────
    bumper = (
        cq.Workplane("XY")
        .box(6, W * 0.80, 8)
        .translate((L/2 + 3, 0, -H/2 + 4))
    )
    cab = cab.union(bumper)

    # ── Coupler mount hole (front) ────────────────────────────
    coupler_hole = (
        cq.Workplane("XY")
        .center(L/2 + 2, 0)
        .circle(P.COUPLER_PIN_D / 2 + 0.2)
        .extrude(8)
        .translate((0, 0, -H/2 + 5))
    )
    cab = cab.cut(coupler_hole)

    asm = cq.Assembly()
    asm.add(cab, name="front_cab", color=cq.Color("steelblue"))
    return asm


def export(out_dir: str = P.OUTPUT_DIR):
    os.makedirs(out_dir, exist_ok=True)
    asm = build_front_cab()
    wp = asm.toCompound()
    if P.EXPORT_STEP:
        cq.exporters.export(wp, os.path.join(out_dir, "04_front_cab.step"))
    if P.EXPORT_STL:
        cq.exporters.export(
            wp, os.path.join(out_dir, "04_front_cab.stl"),
            exportType="STL", tolerance=P.STL_TOLERANCE,
            angularTolerance=P.STL_ANGULAR_TOL,
        )
    print("  [04] Front cab exported.")


if __name__ == "__main__":
    export()
