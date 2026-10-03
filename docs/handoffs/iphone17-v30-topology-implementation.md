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

## Checkpoint — Codex quota stop, 2026-10-03

Long Codex work was stopped to preserve quota. All useful work is being committed/pushed for chat handoff.

### Completed and committed before checkpoint
- `8c3e610` — productionized frozen low-poly camera topology in canonical v30.
- `48b271a` — regenerated v30 delivery/runtime artifacts after camera migration.
- Camera eight-mesh runtime scope: 1288 tris; frozen Human Gate remains PASS.
- Camera bake assets/provenance, topology fast/runtime contracts, and topology evidence tooling are in Git.

### Body/rail checkpoint
- `BODY_ALUMINUM` cap/rail patching implemented as interior strip/diagonal cleanup without moving original physical boundary vertices.
- Current Blender 5.2.1 check: 4056 source verts, 4692 source faces, 0 source n-gons, 0 evaluated n-gons, 0 non-manifold edges.
- Baseline comparison: original boundary vertices unchanged; original edges preserved; max normal displacement 0.003337 mm; volume delta 2.42e-12.
- Fast topology contract: 2/2 PASS, including frozen camera 1288 tris and body exported source-topology metadata.
- This body work is a WIP checkpoint, not a visual PASS. Rail fixed-condition render / Human Gate is still pending.

### Remaining work, in order
1. Finish body/rail visual evidence and either retain this checkpoint or revise it.
2. Side controls + Camera Control topology cleanup.
3. Bottom I/O + acoustic openings + screw carrier cleanup.
4. Back glass / display / front hardware cleanup.
5. Flash / rear mic / inner optics / remaining runtime meshes.
6. Full fast suite, Blender reopen, exact GLB Khronos 0/0, meshopt, five finishes, whole-device Human Gate.
7. Two-axis code review against baseline `117546a`.

### Resume point
- Branch: `agent/118-camera-productionize`
- Worktree: `F:\Temp\iphone17-v30-codex-impl`
- Baseline snapshot: `117546a`
- Original dirty WIP remains untouched: `F:\Temp\iphone17-v30-dimfix`
- Issue ledger: GitHub #118
- PR #119 remains DRAFT/HOLD; do not merge.
- Implementation contract: `docs/handoffs/codex-implementation-contract.md`
- Body runtime checkpoint report: `reports/iphone_body_topology_checkpoint.json`

## Slice 2 — body / rail — verified source candidate
- Baseline: pushed Slice 1 `48b271a`; immutable local snapshot `evidence/topology-v30/slice2/baseline.blend` and `.glb`.
- `generate_low_v30.py::patch_body_rail_caps`: connect existing boundary rows into strips; irregular junctions use safe interior diagonals, excluding existing edges and near-collinear ears. No boundary vertex, original edge, Apple profile function or modifier setting changed.
- Source: 4,056 vertices retained; faces 2,830 -> 4,692; n-gons 65 -> 0; non-manifold edges 0 -> 0.
- Runtime: 8,108 triangles retained. Reduction was not prioritized over exact cut/profile preservation.
- Evaluated Blender geometry: 24,620 triangles retained; zero n-gons/non-manifold. Source and live modifier output are distinct seams.
- Preservation: exact original source vertex and edge sets; evaluated normal displacement <= 0.003338 mm; volume delta 2.42e-12 m³. Closest-point distance includes up to 0.045420 mm tangential gaps in old large-cap tessellation; this is recorded, not claimed zero.
- Fixed EEVEE 1000² / unchanged cameras / KEY-only shadows: rail, right controls and bottom beauty+wire under `evidence/topology-v30/slice2/{before,after}/`. Image RMS differences below 0.15 RGB levels/channel. No material visible regression observed.
- RED: Blender rejected 65 n-gons; exact-GLB contract rejected missing authored-topology evidence. GREEN checks actual GLB welded edge incidence plus exporter inspection before triangulation.
- Commands: `python tools/build_iphone17_v30.py --blender <Blender-5.2.1> --skip-previews`; `python -m unittest discover -s tests/fast -v`; Blender factory-startup/reopen `tests/runtime/iphone_v30_body_topology_contract.py -- --baseline <baseline.blend> --report <after.json>`; existing geometry/camera runtime checks; Khronos compat+meshopt 0/0.
- Build driver now uses `--python-exit-code 1` so failed generation cannot silently export stale artifacts.
- Evidence tools resolve frozen blend relative textures against canonical generated asset paths.
- Source commit SHA will be recorded in the separate rebuild commit after source commit. Next: Slice 3 side controls / Camera Control.

## Slice 2 final verification — BODY_ALUMINUM / rail — GREEN
- Fresh verification performed after Codex handoff, without Codex.
- Blender 5.2.1 source/evaluated topology: 0 n-gons, 0 non-manifold edges.
- Original source boundary vertices unchanged; all original edges preserved.
- Max evaluated normal displacement vs frozen Slice 1 baseline: 0.003337 mm.
- Runtime BODY_ALUMINUM remains 8,108 tris; this slice fixes authored topology, not triangle count.
- Fresh fixed-condition EEVEE visual deltas (0–255 RGB RMS): rail 0.062062; controls 0.130266; bottom 0.148897.
- Fresh full fast suite: 209/209 PASS.
- Fresh git diff --check: PASS.
- Local before/after images are intentionally ignored evidence under `evidence/topology-v30/slice2/fresh/`; they are reproducible from baseline commit `48b271a` using `tools/iphone_topology_evidence.py`.
- Tracked verification summary: `reports/iphone_body_topology_final.json`.
- Decision: retain repair. Slice 2 closed. Next: Slice 3 side controls + Camera Control.

