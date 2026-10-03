# iPhone 17 v30 topology implementation handoff
Date: 2026-10-03
Branch: agent/118-camera-productionize
Issue: #118
PR #119 remains DRAFT/HOLD.

## Goal
Finish topology cleanup for the entire canonical iPhone 17 v30 model, not only the camera. Rendering is already visually acceptable; the problem is dense, fragile, n-gon-heavy or otherwise poor production topology across the model.

## Proven pipeline from camera
- preserve Apple dimensions/datums and visible silhouette;
- use geometry only for silhouette/contact/depth/openings;
- use tangent normal/roughness for shallow microdetail;
- explicit low-poly topology rather than dense clean-grid remesh;
- no central fan poles on visible hard-surface caps;
- no global remesh;
- exported GLB/runtime is the shipping seam;
- technical gates plus visual equivalence;
- camera policy is frozen after Human PASS.

## Frozen camera policy
- eight visible meshes total: 1288 tris;
- 40-class silhouette;
- horizontal quad-strip housing/seat caps;
- deterministic UV; 512 maps; 24 px margin;
- cage 0.18 mm; max ray 0.30 mm;
- housing/ring/bevel normals retained;
- glass normal omitted;
- 0 n-gons / 0 non-manifold edges;
- silhouette error 0.038348 mm;
- Khronos 0 errors / 0 warnings.

## Whole-model implementation scope
1. Productionize frozen camera into canonical v30.
2. BODY_ALUMINUM / rail: replace poor cap/cutout topology without changing Apple Detail A or datums.
3. Side controls + Camera Control: intentional capsule/recess topology; preserve dimensions/contact edges.
4. Bottom I/O: USB-C, 3 mic, 5 speaker, screw recesses; keep openings geometric, microdetail mapped.
5. Screws/fasteners: preserve carrier/recess geometry; socket microdetail remains maps.
6. BACK_GLASS / display/front surfaces: clean planar/contact topology; preserve runtime screen policy.
7. FRONT_SENSOR_MASK / FRONT_CAMERA_MASK / flash / rear mic: keep physical openings/datums, clean topology.
8. Inner camera optics and other repeated round details: reduce only where silhouette/runtime visibility proves safe.

## Required implementation discipline
- TDD / RED -> GREEN where behavior can be asserted.
- Existing dimensional/shading tests are preservation gates.
- Add topology/runtime contracts at exported GLB and Blender seams.
- Changed curved/beveled/normal-mapped meshes: 0 n-gons, 0 non-manifold edges.
- Do not invent universal triangle budgets; use per-part baseline-relative reductions while preserving silhouette/contact.
- Do not touch unrelated product/runtime architecture.
- One canonical v30, five finishes, same names/roles/anchors.
- Commit each verified slice separately and push branch after each GREEN slice.
- After each slice, comment issue #118 with commit SHA, objects changed, tests, Blender/Khronos/runtime evidence, and next slice.
- Keep this file current so another chat can resume from Git alone.

## Current source worktree
F:\Temp\iphone17-v30-codex-impl
Original dirty WIP remains preserved at:
F:\Temp\iphone17-v30-dimfix

## Slice 1 — camera productionization — GREEN
- Frozen 8-mesh camera policy migrated into canonical v30 source.
- New durable topology module: `assets/device_mockups/iphone_17/camera_topology_v30.py`.
- Production bake inputs committed under `reference/camera_bake_v30/`; glass normal remains intentionally absent.
- Exact exported camera scope: 1,288 tris.
- Housing/seat: 164 tris each; rings/bevels/glass: 160 tris each.
- Blender 5.2.1: 0 source/evaluated n-gons and 0 non-manifold edges for all eight meshes.
- Apple dimensional contracts: 4/4 PASS.
- Web shading contracts: 17/17 PASS after migrating the obsolete dense depth-plane assertion to the accepted low-poly + tangent-normal representation.
- Full fast suite: 208/208 PASS.
- Khronos glTF Validator 2.0.0-dev.3.10: 0 errors / 0 warnings.
- Compat GLB: 5,243,192 bytes; meshopt GLB: 4,154,140 bytes.
- Previous compat GLB baseline: 6,192,648 bytes.
- Human camera gate remains frozen PASS.
- Next slice: BODY_ALUMINUM / rail source topology while preserving Apple Detail A and all cutout datums.
