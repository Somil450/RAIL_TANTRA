"""
=============================================================
  SMART TRAIN 3D MODEL — MASTER PARAMETERS
  All dimensions in millimetres.
  Edit these values to resize the entire model.
=============================================================
"""

# ── Overall dimensions ────────────────────────────────────
TRAIN_LENGTH        = 420.0   # total length of locomotive
TRAIN_WIDTH         = 70.0    # overall width
TRAIN_HEIGHT        = 95.0    # overall height including roof equip

# ── Chassis ───────────────────────────────────────────────
CHASSIS_LENGTH      = 395.0   # internal chassis length
CHASSIS_WIDTH       = 52.0    # chassis width
CHASSIS_THICKNESS   = 5.0     # floor plate thickness
CHASSIS_RIB_H       = 8.0     # reinforcement rib height
CHASSIS_RIB_T       = 2.5     # rib thickness

# ── Body shell ────────────────────────────────────────────
BODY_WALL_THICKNESS = 2.0     # shell wall thickness
BODY_LENGTH         = 400.0   # body external length
BODY_WIDTH          = 68.0    # body external width
BODY_HEIGHT         = 75.0    # body height (below roof line)
BODY_CORNER_R       = 6.0     # corner fillet radius

# ── Cab / front section ───────────────────────────────────
CAB_LENGTH          = 80.0    # cab module length
CAB_WINDSHIELD_ANGLE= 25.0    # windshield slope angle (deg)
WINDOW_W            = 20.0    # side window width
WINDOW_H            = 14.0    # side window height
WINDOW_CORNER_R     = 2.0     # window corner fillet

# ── Roof ──────────────────────────────────────────────────
ROOF_THICKNESS      = 2.0     # roof shell thickness
ROOF_CROWN_H        = 8.0     # roof curvature rise
ROOF_EQUIP_H        = 15.0    # rooftop equipment height
ROOF_CLIP_DEPTH     = 3.0     # clip engagement depth
ROOF_CLIP_W         = 5.0     # clip width

# ── Bogies ────────────────────────────────────────────────
BOGIE_LENGTH        = 90.0    # bogie frame length
BOGIE_WIDTH         = 50.0    # bogie frame width
BOGIE_HEIGHT        = 22.0    # bogie frame height
BOGIE_FRAME_T       = 3.0     # bogie frame wall thickness
BOGIE_WHEELBASE     = 60.0    # centre-to-centre axle spacing
BOGIE_SPACING       = 280.0   # centre-to-centre bogie spacing on chassis
BOGIE_PIVOT_D       = 12.0    # pivot pin diameter
BOGIE_PIVOT_L       = 10.0    # pivot pin height

# ── Wheels ────────────────────────────────────────────────
WHEEL_DIAMETER      = 22.0    # wheel outer diameter
WHEEL_FLANGE_D      = 24.0    # flange outer diameter
WHEEL_FLANGE_H      = 2.5     # flange height
WHEEL_THICKNESS     = 7.0     # wheel tread width
WHEEL_HUB_D         = 8.0     # hub outer diameter
WHEEL_SPOKE_COUNT   = 8       # decorative spokes
WHEELS_PER_BOGIE    = 4       # wheels per bogie

# ── Axles ─────────────────────────────────────────────────
AXLE_DIAMETER       = 6.0     # axle shaft diameter
AXLE_LENGTH         = 56.0    # axle total length (between flanges)
AXLE_END_D          = 5.0     # axle journal (bearing seat) diameter

# ── Bearing housings ──────────────────────────────────────
BEARING_OD          = 14.0    # bearing housing outer diameter
BEARING_ID          = 6.2     # bearing bore (clearance for axle)
BEARING_H           = 7.0     # housing height
BEARING_CAVITY_D    = 10.0    # cavity for 10mm OD miniature bearing
BEARING_CAVITY_H    = 4.0     # cavity depth

# ── Suspension ────────────────────────────────────────────
SUSPENSION_H        = 12.0    # suspension tower height
SUSPENSION_W        = 8.0     # spring seat width
SUSPENSION_SPRING_D = 6.0     # spring coil outer diameter
SUSPENSION_SPRING_WIRE= 1.0   # spring wire diameter

# ── Brakes ────────────────────────────────────────────────
BRAKE_PAD_L         = 14.0    # brake pad length
BRAKE_PAD_W         = 5.0     # brake pad width
BRAKE_PAD_T         = 3.0     # brake pad thickness
BRAKE_BRACKET_T     = 2.0     # bracket thickness

# ── Couplers ──────────────────────────────────────────────
COUPLER_L           = 22.0    # coupler arm length
COUPLER_W           = 14.0    # coupler head width
COUPLER_H           = 10.0    # coupler head height
COUPLER_PIN_D       = 4.0     # coupler mounting pin diameter
COUPLER_POCKET_D    = 4.2     # pin hole clearance

# ── Pantograph ────────────────────────────────────────────
PANTO_BASE_L        = 40.0    # pantograph base length
PANTO_BASE_W        = 20.0    # pantograph base width
PANTO_BASE_H        = 4.0     # base plate height
PANTO_ARM_W         = 2.5     # arm cross-section width
PANTO_ARM_T         = 2.0     # arm thickness
PANTO_HEIGHT        = 35.0    # pantograph raised height
PANTO_CONTACT_L     = 30.0    # contact strip length

# ── Print / clearances ────────────────────────────────────
PRINT_CLEARANCE     = 0.3     # fit clearance between moving parts
MIN_WALL            = 1.5     # minimum printable wall
SCREW_D_M3          = 3.2     # M3 screw clearance hole
SCREW_HEAD_D_M3     = 6.5     # M3 countersink head diameter
BOSS_D              = 7.0     # screw boss outer diameter
BOSS_H              = 5.0     # screw boss height

# ── Output ────────────────────────────────────────────────
OUTPUT_DIR          = "output"
EXPORT_STEP         = True
EXPORT_STL          = True
STL_TOLERANCE       = 0.05    # mm — mesh quality
STL_ANGULAR_TOL     = 0.5     # degrees
