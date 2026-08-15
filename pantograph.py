"""
13_PANTOGRAPH — Scissor-type pantograph (raised position).
Two crossed diamond arms with a contact strip on top.
Designed for FDM printing; mounts to roof via 4× M3 screws.
"""
import cadquery as cq
import os, sys, math
sys.path.insert(0, os.path.dirname(__file__))
import parameters as P


def build_pantograph() -> cq.Assembly:
    BL  = P.PANTO_BASE_L
    BW  = P.PANTO_BASE_W
    BH  = P.PANTO_BASE_H
    AW  = P.PANTO_ARM_W
    AT  = P.PANTO_ARM_T
    PH  = P.PANTO_HEIGHT
    CL  = P.PANTO_CONTACT_L

    # ── Base plate ────────────────────────────────────────────
    base = (
        cq.Workplane("XY")
        .box(BL, BW, BH)
        .edges("|Z").fillet(2)
        .edges(">Z").fillet(1)
    )
    # M3 mounting holes
    for mx, my in [(BL/2 - 5, BW/2 - 5), (BL/2 - 5, -BW/2 + 5),
                   (-BL/2 + 5, BW/2 - 5), (-BL/2 + 5, -BW/2 + 5)]:
        mh = (
            cq.Workplane("XY")
            .center(mx, my)
            .circle(P.SCREW_D_M3 / 2)
            .extrude(BH + 1)
        )
        base = base.cut(mh)

    # Pivot post stubs on base top
    pivot_sep = BL * 0.30      # pivot separation along X
    for px in [-pivot_sep, pivot_sep]:
        post = (
            cq.Workplane("XY")
            .center(px, 0)
            .circle(2.5)
            .extrude(3)
            .translate((0, 0, BH / 2))
        )
        base = base.union(post)

    # ── Lower arms (2× slanted outward) ──────────────────────
    # We model as flat bars leaning inward
    arm_angle = math.radians(30)   # lean angle from vertical
    arm_len = PH / math.cos(arm_angle) * 0.65   # lower arm length

    lower_arms = []
    for side_sign in [-1, 1]:
        start_x = side_sign * pivot_sep
        # Arm goes from base pivot to mid-point
        end_x  = -side_sign * pivot_sep * 0.5
        end_z  = PH * 0.55
        dx = end_x - start_x
        dz = end_z
        length = math.sqrt(dx**2 + dz**2)
        angle  = math.degrees(math.atan2(dx, dz))

        arm = (
            cq.Workplane("XZ")
            .center(start_x + dx/2, dz/2 + BH/2)
            .rect(AW, length)
            .extrude(AT)
            .translate((0, 0, 0))
            .rotate((start_x + dx/2, 0, BH/2 + dz/2),
                    (start_x + dx/2, 1, BH/2 + dz/2), angle)
        )
        lower_arms.append(arm)

    # ── Upper arms (cross from mid to contact strip) ──────────
    upper_arms = []
    for side_sign in [-1, 1]:
        # Upper arm mirrors lower arm pattern
        start_x = -side_sign * pivot_sep * 0.5
        start_z =  PH * 0.55
        end_x   = -side_sign * pivot_sep * 0.10
        end_z   =  PH

        dx = end_x - start_x
        dz = end_z - start_z
        length = math.sqrt(dx**2 + dz**2)
        angle  = math.degrees(math.atan2(dx, dz))

        arm = (
            cq.Workplane("XZ")
            .center(start_x + dx/2, start_z + dz/2)
            .rect(AW, length)
            .extrude(AT)
            .rotate((start_x + dx/2, 0, start_z + dz/2),
                    (start_x + dx/2, 1, start_z + dz/2), angle)
        )
        upper_arms.append(arm)

    # ── Contact strip (top horizontal beam) ───────────────────
    contact = (
        cq.Workplane("XY")
        .box(CL, AW, AT)
        .translate((0, 0, PH + AT/2 + BH/2))
        .edges("|Y").fillet(0.5)
    )
    # Insulators (small cylinders at ends)
    for cx in [-CL/2, CL/2]:
        ins = (
            cq.Workplane("XY")
            .center(cx, 0)
            .circle(AW / 2 + 0.5)
            .extrude(4)
            .translate((0, 0, PH + BH/2))
        )
        contact = contact.union(ins)

    # ── Build full pantograph ─────────────────────────────────
    panto = base.union(contact)
    for a in lower_arms + upper_arms:
        panto = panto.union(a)

    asm = cq.Assembly()
    asm.add(panto, name="pantograph", color=cq.Color("black"))
    return asm


def export(out_dir: str = P.OUTPUT_DIR):
    os.makedirs(out_dir, exist_ok=True)
    asm = build_pantograph()
    wp = asm.toCompound()
    if P.EXPORT_STEP:
        cq.exporters.export(wp, os.path.join(out_dir, "13_pantograph.step"))
    if P.EXPORT_STL:
        cq.exporters.export(
            wp, os.path.join(out_dir, "13_pantograph.stl"),
            exportType="STL", tolerance=P.STL_TOLERANCE,
            angularTolerance=P.STL_ANGULAR_TOL,
        )
    print("  [13] Pantograph exported.")


if __name__ == "__main__":
    export()
