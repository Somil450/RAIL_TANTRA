"""
07_WHEEL — Railway-style wheel with tread, flange, hub, and decorative spokes.
Suitable for FDM printing; each wheel is a separate part.
"""
import cadquery as cq
import os, sys, math
sys.path.insert(0, os.path.dirname(__file__))
import parameters as P


def build_wheel() -> cq.Assembly:
    OD   = P.WHEEL_DIAMETER       # tread outer diameter
    FD   = P.WHEEL_FLANGE_D       # flange outer diameter
    FH   = P.WHEEL_FLANGE_H       # flange axial height
    TW   = P.WHEEL_THICKNESS      # tread face width
    HD   = P.WHEEL_HUB_D          # hub outer diameter
    AD   = P.AXLE_DIAMETER        # axle hole diameter
    NS   = P.WHEEL_SPOKE_COUNT    # number of spokes
    SW   = 2.5                    # spoke width
    ST   = 2.0                    # spoke thickness

    # ── Tread cylinder ────────────────────────────────────────
    tread = (
        cq.Workplane("XY")
        .circle(OD / 2)
        .extrude(TW)
    )

    # ── Flange ────────────────────────────────────────────────
    flange = (
        cq.Workplane("XY")
        .circle(FD / 2)
        .extrude(FH)
    )
    wheel = tread.union(flange)

    # ── Hub cylinder ──────────────────────────────────────────
    hub = (
        cq.Workplane("XY")
        .circle(HD / 2)
        .extrude(TW + 2)      # slightly proud of tread face
    )
    wheel = wheel.union(hub)

    # ── Axle hole ─────────────────────────────────────────────
    axle_hole = (
        cq.Workplane("XY")
        .circle((AD + P.PRINT_CLEARANCE) / 2)
        .extrude(TW + 3)
    )
    wheel = wheel.cut(axle_hole)

    # ── Decorative spokes ─────────────────────────────────────
    spoke_r_inner = HD / 2 + 1
    spoke_r_outer = OD / 2 - 2
    spoke_z       = TW / 2

    for i in range(NS):
        angle = i * 360 / NS
        ang_r = math.radians(angle)
        cx = math.cos(ang_r) * (spoke_r_inner + spoke_r_outer) / 2
        cy = math.sin(ang_r) * (spoke_r_inner + spoke_r_outer) / 2
        length = spoke_r_outer - spoke_r_inner

        spoke = (
            cq.Workplane("XY")
            .center(cx, cy)
            .box(length, SW, ST)
            .rotate((0, 0, 0), (0, 0, 1), angle)
            .translate((0, 0, spoke_z - ST/2))
        )
        wheel = wheel.cut(spoke)          # cutout style spoke (open web)

    # ── Light chamfer on tread edges ─────────────────────────
    wheel = wheel.edges(
        cq.selectors.NearestToPointSelector((0, 0, TW))
    ).chamfer(0.5)

    asm = cq.Assembly()
    asm.add(wheel, name="wheel", color=cq.Color("black"))
    return asm


def export(out_dir: str = P.OUTPUT_DIR):
    os.makedirs(out_dir, exist_ok=True)
    asm = build_wheel()
    wp = asm.toCompound()
    if P.EXPORT_STEP:
        cq.exporters.export(wp, os.path.join(out_dir, "07_wheel.step"))
    if P.EXPORT_STL:
        cq.exporters.export(
            wp, os.path.join(out_dir, "07_wheel.stl"),
            exportType="STL", tolerance=P.STL_TOLERANCE,
            angularTolerance=P.STL_ANGULAR_TOL,
        )
    print("  [07] Wheel exported.")


if __name__ == "__main__":
    export()
