You are the implementation agent for the complete iPhone 17 v30 topology cleanup.

WORKSPACE
- Writable implementation worktree: F:\Temp\iphone17-v30-codex-impl
- Branch: agent/118-camera-productionize
- Baseline snapshot commit: 117546a
- Shared GitHub ledger: looksawful/awful-studio issue #118
- Existing PR #119 remains DRAFT/HOLD and must not be merged.
- Frozen camera prototype (read-only evidence): F:\Temp\iphone17-camera-bake-prototype

READ FIRST
1. docs/handoffs/iphone17-v30-topology-implementation.md
2. docs/research/iphone17-v30-workstream-report-2026-10-03.md
3. F:\Temp\iphone17-camera-bake-prototype\assets\device_mockups\iphone_17\prototypes\camera_lowpoly_bake_2026_10_03\README.md
4. F:\Temp\iphone17-camera-bake-prototype\assets\device_mockups\iphone_17\prototypes\camera_lowpoly_bake_2026_10_03\out_topofix40\metrics.json

PROCESS SKILLS TO FOLLOW
- $CODEX_HOME/skills/implement\SKILL.md
- $CODEX_HOME/skills/tdd\SKILL.md
- $CODEX_HOME/skills/code-review\SKILL.md
- $CODEX_HOME/skills/codebase-design\SKILL.md
- $CODEX_HOME/skills/3d-modeling\SKILL.md
- $CODEX_HOME/skills/web-3d-asset-pipeline\SKILL.md
- $CODEX_HOME/skills/verification-before-completion\SKILL.md
- .skills\awful-tdd\SKILL.md
- .skills\awful-verification\SKILL.md
- .skills\blender-runtime-qa\SKILL.md
- .skills\blender-evidence-loop\SKILL.md
- .skills\git-change-isolation\SKILL.md
- .skills\release-readiness\SKILL.md

GOAL
Implement production-quality topology for the ENTIRE canonical iPhone 17 v30 model. The current rendering is visually acceptable, but much of the source/runtime topology is dense, n-gon-heavy, brittle, or otherwise poor. The camera prototype proved the method; now apply the method systematically to the whole model while preserving visual form, Apple datums, materials, finishes, names, runtime roles, anchors, and v30 identity.

AUTHORITATIVE PRINCIPLES
- Preserve Apple dimensions and Detail A profile exactly.
- Geometry is required for silhouette, physical depth transitions, openings/cavities, contact edges, and profile-visible features.
- Tangent normal/roughness is preferred for shallow microdetail.
- No global remesh.
- No 64/72/96 dense-camera remake.
- No generic topology framework unless a second concrete need forces it.
- Runtime/exported GLB is the shipping seam.
- For changed runtime-visible hard-surface meshes: intentional triangles/quads, zero n-gons, zero non-manifold edges.
- Do not lower topology quality merely to hit an arbitrary triangle count.
- Preserve rendering; improvements to topology must not regress silhouette or visible shading.
- Camera Human Gate is already PASS and frozen. Production must reproduce it, not redesign it.

IMPLEMENT IN THESE VERIFIED SLICES, ONE AT A TIME
SLICE 1 — Camera productionization
- Replace the eight dense production meshes with the frozen camera policy:
  CAMERA_HOUSING_SEAT, CAMERA_HOUSING,
  CAMERA_1_RING, CAMERA_2_RING,
  CAMERA_1_BEVEL, CAMERA_2_BEVEL,
  CAMERA_1_GLASS, CAMERA_2_GLASS.
- Exact accepted scope: 1288 tris total for those eight meshes.
- 40-class visible silhouette; housing/seat horizontal quad-strip caps.
- deterministic UVs; 512 bake maps; 24 px margin; cage 0.18 mm; max ray 0.30 mm.
- housing/seat/ring/bevel normals retained; glass normal omitted.
- Keep inner optics unchanged in this slice.
- RED first at exported GLB / Blender seams.

SLICE 2 — BODY_ALUMINUM / rail
- Preserve APPLE_CORNER_BEZIER, iphone17_corner_profile, iphone17_body_outline, iphone17_body_prism and all Apple datums.
- Replace n-gon/fragile cap and cutout topology with intentional strips/patches around rail and cutout junctions.
- Preserve exact physical cutouts/recess mouths/walls.
- Current runtime BODY_ALUMINUM baseline is 8108 tris; reduction is desirable but topology + silhouette + shading correctness are mandatory.
- Do not repeat previously falsified modifier toggles or global remesh.
- Produce fixed-condition before/after rail renders and topology evidence.

SLICE 3 — Side controls + Camera Control
- ACTION button, volume/power controls, Camera Control and recesses.
- Preserve capsule silhouettes, thicknesses, contact edges, Apple elevations, 0.10 mm Camera Control recess and material policy.
- Remove unnecessary n-gon caps / dense circular construction where safe.

SLICE 4 — Bottom I/O + fasteners
- USB-C mouth/cavity/tongue.
- 3 mic + 5 speaker openings.
- two screw/recess carriers.
- Keep actual openings geometric.
- Keep grille weave and pentalobe microdetail in normal/roughness maps.
- Preserve dimensions/positions exactly.

SLICE 5 — Back glass / display / front hardware
- BACK_GLASS, SCREEN_CONTENT physical mesh, FRONT_SENSOR_MASK, FRONT_CAMERA_MASK and relevant contact surfaces.
- Preserve Dynamic Island ownership model and SCREEN_GLASS web exclusion.
- Clean planar/contact topology; no visible silhouette or depth regressions.

SLICE 6 — Flash / rear mic / inner camera optics / remaining runtime meshes
- Preserve physical opening datums and optical materials.
- Only reduce round-detail density where exported silhouette/runtime visibility proves equivalence.
- Finish any remaining runtime-visible source n-gons/non-manifold defects.

TDD / VERIFICATION
For each slice:
1. Capture baseline metrics for only that slice.
2. Add one or more meaningful RED contracts at existing public seams (generator -> Blender -> exact exported GLB). Do not test private helper implementation.
3. Watch RED fail for the intended reason.
4. Implement the smallest production change.
5. Run focused tests repeatedly until GREEN.
6. Run Blender --factory-startup generation/reopen checks.
7. Export exact runtime GLB through export_runtime_v30.py.
8. Validate Khronos: 0 errors / 0 warnings.
9. Run meshopt and ensure critical nodes/roles/anchors survive.
10. Produce fixed-condition evidence render/wireframe when appearance/topology is materially changed.
11. Update docs/handoffs/iphone17-v30-topology-implementation.md with:
    - completed slice
    - files/symbols changed
    - before/after metrics
    - tests and commands
    - artifact paths
    - exact commit SHA
    - next slice
12. Commit the verified slice with a narrow commit message.
13. Continue to next slice. Do NOT wait for user unless a genuine Human Gate is required because appearance changed materially or an authoritative datum is ambiguous.

FINAL GATES
- targeted tests all green
- full fast suite green
- git diff --check
- Blender factory-startup generation/reopen
- exact compat GLB Khronos 0/0
- meshopt GLB valid and smaller
- five finishes preserved
- canonical object names/roles/anchors preserved
- no unintended runtime-visible n-gons or non-manifold edges
- before/after visual evidence for camera, rail, controls, bottom, back/front
- code-review against baseline 117546a on Standards + Spec axes
- do not merge #119
- do not ship until owner final whole-device Human Gate

GIT / HANDOFF
- Work only on agent/118-camera-productionize.
- Never reset/clean/stash/rebase the original F:\Temp\iphone17-v30-dimfix worktree.
- Commit every verified slice.
- Do not squash.
- Keep the handoff file current after every slice so another ChatGPT/Codex session can resume from Git without chat history.
- Push may be attempted after each commit; if credentials/network block it, continue locally and record the SHA. The supervisor will push.

Start implementation now. Do not return a plan. Execute Slice 1, then continue through the model.