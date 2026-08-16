/*
  SMART TRAIN ASSEMBLY LAYOUT — FeatureScript
  ============================================
  Paste this into an Onshape Feature Studio tab to
  automatically position all train parts in the assembly.
  
  HOW TO USE:
  1. In your SMART_TRAIN_FINAL document, click the "+" tab at bottom
  2. Select "Feature Studio"
  3. Name it "TrainLayout"
  4. Delete all default code and paste this entire script
  5. Click "Commit"
  6. Go to your Assembly tab
  7. In the assembly toolbar, click "Custom features" and run "layoutTrain"
*/

FeatureScript 1948;
import(path : "onshape/std/geometry.fs", version : "1948.0");
import(path : "onshape/std/assemblyQuery.fs", version : "1948.0");

// ── Master layout feature ─────────────────────────────────────
annotation { "Feature Type Name" : "Layout Train Assembly" }
export const layoutTrain = defineFeature(function(context is Context, id is Id, definition is map)
    precondition
    {
        // No user inputs needed
    }
    {
        // All transforms in mm, then converted to metres inside
        const MM = 0.001 * meter;

        // Query all instances in the assembly
        const allParts = qEverything(EntityType.BODY);
        const bodies   = evaluateQuery(context, allParts);
        const n        = size(bodies);

        // Define target positions [x, y, z] in mm for each part by index
        // Order matches the import order seen in the assembly panel:
        // Part 1 (chassis), Part 1 (internal frame), body shell, front cab,
        // roof, bogie x2, wheel x8, axle x4, bearing x4, suspension, brakes, coupler x2, pantograph
        const positions = [
            vector(0,     0,    0)    * MM,   // 00 chassis
            vector(0,     5,    0)    * MM,   // 01 internal frame
            vector(0,     5,    0)    * MM,   // 02 body shell
            vector(160,   5,    0)    * MM,   // 03 front cab
            vector(0,     80,   0)    * MM,   // 04 roof
            vector(140,  -25,   0)    * MM,   // 05 bogie front
            vector(-140, -25,   0)    * MM,   // 06 bogie rear
            vector(170,  -36,  25)    * MM,   // 07 wheel 1
            vector(110,  -36,  25)    * MM,   // 08 wheel 2
            vector(-110, -36,  25)    * MM,   // 09 wheel 3
            vector(-170, -36,  25)    * MM,   // 10 wheel 4
            vector(170,  -36, -25)    * MM,   // 11 wheel 5
            vector(110,  -36, -25)    * MM,   // 12 wheel 6
            vector(-110, -36, -25)    * MM,   // 13 wheel 7
            vector(-170, -36, -25)    * MM,   // 14 wheel 8
            vector(170,  -30,   0)    * MM,   // 15 axle 1
            vector(110,  -30,   0)    * MM,   // 16 axle 2
            vector(-110, -30,   0)    * MM,   // 17 axle 3
            vector(-170, -30,   0)    * MM,   // 18 axle 4
            vector(0,     95,   0)    * MM,   // 19 pantograph / extra
        ];

        for (var i = 0; i < n && i < size(positions); i += 1)
        {
            const body  = bodies[i];
            const pos   = positions[i];

            // Get current centroid of this body
            const bbox  = evBox3d(context, { "topology" : body });
            const cen   = box3dCenter(bbox);

            // Translate from current centroid to target position
            const delta = pos - cen;
            const xform = transform(identityMatrix(3), delta);

            opTransform(context, id + unstableIdComponent(i), {
                "bodies"    : body,
                "transform" : xform
            });
        }
    });
