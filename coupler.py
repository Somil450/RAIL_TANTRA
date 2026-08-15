"""
12_COUPLER — NEM-pocket-style coupler with mounting pin and head.
Separate front and rear — both are identical geometrically.
The mounting pin fits into a pocket on the body/chassis.
"""
import cadquery as cq
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import parameters as P


def build_coupler() -> cq.Assembly:
    CL  = P.COUPLER_L       # arm length
    CW  = P.COUPLER_W       # head width
    CH  = P.COUPLER_H       # head height
    CPD = P.COUPLER_PIN_D   # mounting pin diameter
    T   = 3.0               # arm thickness
    HL  = 5.0               # hook arm protrusion

    # ── Arm ───────────────────────────────────────────────────
    arm = (
        cq.Workplane("XY")
        .box(CL, T, T)
        .edges("|Z").fillet(0.5)
    )

    # ── Head block ────────────────────────────────────────────
    head = (
        cq.Workplane("XY")
        .box(T + 4, CW, CH)
        .translate((CL / 2 + T/2 + 2, 0, 0))
        .edges("|Z").fillet(1.5)
    )

    # ── Hook pocket opening in head ───────────────────────────
    hook_slot = (
        cq.Workplane("XZ")
        .center(CL/2 + T + 3, 0)
        .rect(T + 2, CH * 0.5)
        .extrude(CW / 2)
        .translate((0, CW/4, 0))
    )
    head = head.cut(hook_slot)

    # ── Draft hook (loop style) ───────────────────────────────
    hook_outer = (
        cq.Workplane("XY")
        .center(CL/2 + T + 4, CW/4)
        .circle(4.0)
        .extrude(T * 0.8)
        .translate((0, 0, -T * 0.4))
    )
    hook_inner = (
        cq.Workplane("XY")
        .center(CL/2 + T + 4, CW/4)
        .circle(2.5)
        .extrude(T * 0.8 + 1)
        .translate((0, 0, -T * 0.4 - 0.1))
    )
    hook = hook_outer.cut(hook_inner)

    # ── Mounting pin (at rear of arm) ─────────────────────────
    pin = (
        cq.Workplane("XY")
        .circle((CPD - P.PRINT_CLEARANCE) / 2)
        .extrude(8)
        .translate((-CL/2, 0, 0))
    )
    # Retention flange at top of pin
    pin_flange = (
        cq.Workplane("XY")
        .circle(CPD / 2 + 1.5)
        .extrude(2)
        .translate((-CL/2, 0, 7))
    )

    # ── Assemble ──────────────────────────────────────────────
    coupler = arm.union(head).union(hook).union(pin).union(pin_flange)
    # (no fillet on compound — individual parts are already chamfered)

    asm = cq.Assembly()
    asm.add(coupler, name="coupler", color=cq.Color("orange"))
    return asm


def export(out_dir: str = P.OUTPUT_DIR):
    os.makedirs(out_dir, exist_ok=True)
    asm = build_coupler()
    wp = asm.toCompound()
    if P.EXPORT_STEP:
        cq.exporters.export(wp, os.path.join(out_dir, "12_coupler.step"))
    if P.EXPORT_STL:
        cq.exporters.export(
            wp, os.path.join(out_dir, "12_coupler.stl"),
            exportType="STL", tolerance=P.STL_TOLERANCE,
            angularTolerance=P.STL_ANGULAR_TOL,
        )
    print("  [12] Coupler exported.")


if __name__ == "__main__":
    export()
