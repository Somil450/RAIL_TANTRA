"""
02_INTERNAL_FRAME — Secondary internal frame / sub-chassis.
Provides an inner structural skeleton with wire routing channels
and equipment bays between the chassis and body shell.
"""
import cadquery as cq
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import parameters as P


def build_internal_frame() -> cq.Assembly:
    L   = P.CHASSIS_LENGTH - 10
    W   = P.CHASSIS_WIDTH - 4
    H   = 20.0           # frame height (sits on chassis, under body floor)
    T   = 2.0            # frame wall thickness

    # ── Perimeter frame ───────────────────────────────────────
    outer = (
        cq.Workplane("XY")
        .box(L, W, H)
        .edges("|Z").fillet(2)
    )
    inner = (
        cq.Workplane("XY")
        .box(L - 2*T, W - 2*T, H)
        .edges("|Z").fillet(max(1, 2 - T))
    )
    frame = outer.cut(inner)

    # ── Cross-braces (every ~80 mm) ───────────────────────────
    n = int(L / 80)
    for i in range(1, n):
        xp = -L/2 + i * (L / n)
        brace = (
            cq.Workplane("XY")
            .center(xp, 0)
            .box(T, W - 2*T, H)
        )
        frame = frame.union(brace)

    # ── Floor mounting holes (match chassis bosses) ───────────
    boss_xy = [
        ( L/2 - 15,  W/2 - 6),
        ( L/2 - 15, -W/2 + 6),
        (-L/2 + 15,  W/2 - 6),
        (-L/2 + 15, -W/2 + 6),
        ( 0,  W/2 - 6),
        ( 0, -W/2 + 6),
    ]
    for bx, by in boss_xy:
        mh = (
            cq.Workplane("XY")
            .center(bx, by)
            .circle(P.SCREW_D_M3 / 2)
            .extrude(H + 1)
        )
        frame = frame.cut(mh)

    # ── Wire/cable routing channels (bottom cutouts) ──────────
    for channel_y in [-W/4, W/4]:
        ch = (
            cq.Workplane("XY")
            .center(0, channel_y)
            .box(L - 20, 4, T + 1)
            .translate((0, 0, -H/2 + T/2))
        )
        frame = frame.cut(ch)

    asm = cq.Assembly()
    asm.add(frame, name="internal_frame", color=cq.Color("slategray"))
    return asm


def export(out_dir: str = P.OUTPUT_DIR):
    os.makedirs(out_dir, exist_ok=True)
    asm = build_internal_frame()
    wp = asm.toCompound()
    if P.EXPORT_STEP:
        cq.exporters.export(wp, os.path.join(out_dir, "02_internal_frame.step"))
    if P.EXPORT_STL:
        cq.exporters.export(
            wp, os.path.join(out_dir, "02_internal_frame.stl"),
            exportType="STL", tolerance=P.STL_TOLERANCE,
            angularTolerance=P.STL_ANGULAR_TOL,
        )
    print("  [02] Internal frame exported.")


if __name__ == "__main__":
    export()
