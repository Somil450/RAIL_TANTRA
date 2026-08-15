"""
03_BODY_SHELL — Locomotive body shell.
Hollow shell with side windows, ventilation grilles, coupler openings,
and roof seat with clip recesses.
"""
import cadquery as cq
import os, sys, math
sys.path.insert(0, os.path.dirname(__file__))
import parameters as P


def build_body_shell() -> cq.Assembly:
    L  = P.BODY_LENGTH
    W  = P.BODY_WIDTH
    H  = P.BODY_HEIGHT
    T  = P.BODY_WALL_THICKNESS
    CR = P.BODY_CORNER_R
    WW = P.WINDOW_W
    WH = P.WINDOW_H
    WR = P.WINDOW_CORNER_R

    # ── Outer shell ──────────────────────────────────────────
    outer = (
        cq.Workplane("XY")
        .box(L, W, H)
        .edges("|Z").fillet(CR)
        .edges(">Z").fillet(2)
    )

    # ── Hollow interior ──────────────────────────────────────
    inner_cut = (
        cq.Workplane("XY")
        .box(L - 2 * T, W - 2 * T, H)
        .translate((0, 0, T))
        .edges("|Z").fillet(max(CR - T, 1))
    )
    body = outer.cut(inner_cut)

    # ── Side windows (×4 per side) ───────────────────────────
    win_z_center = H * 0.60  # window height from bottom
    win_x_positions = [-L * 0.30, -L * 0.10, L * 0.10, L * 0.30]
    for side_sign in [1, -1]:
        for wx in win_x_positions:
            win = (
                cq.Workplane("XZ")
                .center(wx, win_z_center - H / 2)
                .rect(WW, WH)
                .extrude(W)
            )
            body = body.cut(win)

    # ── Ventilation grilles (×6 per side, lower body) ────────
    grille_w  = 8.0
    grille_h  = 12.0
    grille_z  = H * 0.25
    grille_xs = [L * x for x in (-0.42, -0.28, -0.14, 0.14, 0.28, 0.42)]
    for side_sign in [1, -1]:
        for gx in grille_xs:
            for slot_dy in range(3):   # 3 horizontal slots per grille
                slot_z = grille_z + slot_dy * 4 - H / 2
                slot = (
                    cq.Workplane("XZ")
                    .center(gx, slot_z)
                    .rect(grille_w, 1.5)
                    .extrude(T + 0.5)
                    .translate((0, side_sign * (W / 2 - T / 2), 0))
                )
                body = body.cut(slot)

    # ── Coupler openings (front & rear, centred low) ──────────
    coupler_cut = (
        cq.Workplane("YZ")
        .rect(P.COUPLER_W + 2, P.COUPLER_H + 2)
        .extrude(T + 2)
    )
    body = body.cut(coupler_cut.translate(( L / 2 - T - 1, 0, P.COUPLER_H / 2 - H / 2 + 6)))
    body = body.cut(coupler_cut.translate((-L / 2 + T + 1, 0, P.COUPLER_H / 2 - H / 2 + 6)))

    # ── Roof seat — recessed ledge for roof panel ─────────────
    roof_recess = (
        cq.Workplane("XY")
        .box(L - 2, W - 2, T)
        .translate((0, 0, H / 2 - T / 2))
    )
    body = body.cut(roof_recess)

    # ── Clip receiver pockets (4 per side for roof clips) ─────
    clip_xs = [-L * 0.35, -L * 0.12, L * 0.12, L * 0.35]
    for cx in clip_xs:
        for sy in [1, -1]:
            pocket = (
                cq.Workplane("XY")
                .center(cx, sy * (W / 2 - T))
                .rect(P.ROOF_CLIP_W, P.ROOF_CLIP_DEPTH)
                .extrude(P.ROOF_CLIP_DEPTH + 1)
                .translate((0, 0, H / 2 - P.ROOF_CLIP_DEPTH - 1))
            )
            body = body.cut(pocket)

    # ── Body screw counterbores (match chassis bosses) ────────
    boss_xy = [
        ( L / 2 - 20,  P.CHASSIS_WIDTH / 2 - 10),
        ( L / 2 - 20, -P.CHASSIS_WIDTH / 2 + 10),
        (-L / 2 + 20,  P.CHASSIS_WIDTH / 2 - 10),
        (-L / 2 + 20, -P.CHASSIS_WIDTH / 2 + 10),
        ( 0,  P.CHASSIS_WIDTH / 2 - 10),
        ( 0, -P.CHASSIS_WIDTH / 2 + 10),
    ]
    for bx, by in boss_xy:
        hole = (
            cq.Workplane("XY")
            .center(bx, by)
            .circle(P.SCREW_D_M3 / 2)
            .extrude(T + P.BOSS_H)
            .translate((0, 0, -H / 2))
        )
        body = body.cut(hole)

    asm = cq.Assembly()
    asm.add(body, name="body_shell", color=cq.Color("steelblue"))
    return asm


def export(out_dir: str = P.OUTPUT_DIR):
    os.makedirs(out_dir, exist_ok=True)
    asm = build_body_shell()
    wp = asm.toCompound()
    if P.EXPORT_STEP:
        cq.exporters.export(wp, os.path.join(out_dir, "03_body_shell.step"))
    if P.EXPORT_STL:
        cq.exporters.export(
            wp, os.path.join(out_dir, "03_body_shell.stl"),
            exportType="STL", tolerance=P.STL_TOLERANCE,
            angularTolerance=P.STL_ANGULAR_TOL,
        )
    print("  [03] Body shell exported.")


if __name__ == "__main__":
    export()
