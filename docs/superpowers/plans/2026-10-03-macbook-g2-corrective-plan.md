# MacBook Pro 14 M5 вЂ” G2 corrective plan after G1 rejection

Date: 2026-10-03
Tracker: #52, #127, #128, #129; PR #121 remains draft
Fixed audit point: `518bb25`
Current branch: `agent/129-geometry-calibration`

## Goal

Finish the MacBook Pro 14 M5 geometry rebuild without repeating the G1 failure mode: no provisional or merely convenient constants may become authoritative geometry just because they are parametric or because a screenshot looks plausible.

The architecture stays:

`Apple primary sources -> geometry contract -> authoritative Blender master -> automatically derived GLB/Meshopt runtime -> Storybook/Three.js -> human visual gate`.

No second manually maintained model, no parallel exporter, no direct May-model geometry reuse.

## Evidence-based progress

Percentages describe completion of each phase, not elapsed time.

- [100%] Primary-source inventory and research
- [65%] G2 metric/provenance geometry contract
- [45%] Authoritative master rebuild
- [75%] Derived runtime packaging
- [20%] True model-to-reference orthographic overlays
- [70%] Browser/Storybook verification
- [0%] Final human visual acceptance

Weighted project progress for this corrective path: **57.25%**. This is a planning indicator only; it is not a release-readiness score.

## Phase 1 вЂ” provenance correction

### [65%] Task 1: replace aggregate G2_EXTERNAL_FACTS with per-fact provenance

Problem:
`G2_EXTERNAL_FACTS` currently freezes a mixed bag of calibrated, relational and weakly inferred values under one `APPLE_RELATIONAL / MEDIUM_HIGH / frozen=True` label.

Required:
- represent each external fact as a `GeometryFact` or equivalent typed record;
- every value gets its own source, method, tolerance, frame, confidence and frozen flag;
- dimensions such as hinge-cover depth/thickness remain PROVISIONAL unless supported by defensible calibration;
- relationships such as вЂњclosed display assembly flush with top caseвЂќ remain relational invariants, not invented millimetre dimensions.

Acceptance:
- no grouped provenance that upgrades weaker evidence;
- `validate_fact` rejects frozen provisional values;
- generator can query only explicitly freezable values.

Verification:
- unit contract tests;
- source-register completeness test;
- review against G2 audit.

## Phase 2 вЂ” convert tests from constant checks to model checks

### [35%] Task 2: world-space Blender geometry assertions

Current problem:
some G2 tests prove that a constant equals the same expected constant. They do not prove that the generated Blender object implements it.

Required runtime assertions:
- keyboard aggregate bounds and lattice from actual generated key objects;
- trackpad mesh and recess share X datum and calibrated dimensions/gaps;
- Touch ID world-space center/bounds;
- speaker proxy/grid relation and side inset;
- front finger recess actual cut width/profile;
- feet actual diameter and center positions;
- eight screw world-space centers;
- hinge-cover identities, bounds, placement and relationship to rear chassis;
- closed external display assembly silhouette relation to top case.

Acceptance:
a deliberate wrong generated object must fail even when the geometry-contract constant remains unchanged.

## Phase 3 вЂ” display/lid authority cleanup

### [25%] Task 3: remove provisional display magic from production geometry

Current generator still consumes provisional values for:
- bezel 307.2 Г— 204.2 mm;
- gasket 309.3 Г— 207 mm;
- lower rail 3.4 mm;
- glass 307.6 Г— 204.6 mm;
- several display/lid radii and offsets;
- base/lid vertical split assumptions.

Required:
- keep exact active matrix 302.4 Г— 196.4 mm;
- derive/freezes only Product-Bezel facts whose calibration residual and tolerance are recorded;
- keep unsupported outer dimensions provisional;
- model flush/ordering/containment as relational constraints where Apple repair documentation is authoritative but metric values are absent;
- do not require `LID_UNIBODY` itself to equal the complete 312.6 Г— 221.2 plan unless evidence proves that specific part dimension.

Acceptance:
no production geometry consumes `PROVISIONAL` display facts.
## Phase 4 вЂ” actual model overlays

### [20%] Task 4: Blender projection -> Apple orthographic evidence

Current `build_macbook_g2_surface_overlays.py` mostly draws contract coordinates directly on references. That validates the contract drawing, not the generated model.

Replace/extend it with:
1. open generated candidate in Blender 5.2.1;
2. set deterministic closed/open state;
3. project actual world-space geometry into calibrated orthographic planes;
4. map those projected points/silhouettes into the official raster;
5. emit residuals and overlays.

Required views:
- closed top;
- closed front;
- left;
- right;
- bottom;
- open deck;
- display face;
- hinge/rear macro.

Acceptance:
- overlays are generated from actual model vertices/bounds, not duplicate contract constants;
- residual thresholds are source-resolution-aware;
- unsupported geometry is visibly labelled UNVERIFIED rather than painted green.

## Phase 5 вЂ” rebuild master geometry

### [45%] Task 5: rebuild only from accepted datums

Already mathematically validated:
- chassis 312.6 Г— 221.2 Г— 15.5 mm;
- active matrix 302.4 Г— 196.4 mm;
- corrected deck raster scale;
- keyboard aggregate/well;
- trackpad bounds/center/front gap;
- Touch ID placement;
- speaker 15 Г— 114 lattice and pitch.

Rebuild/repair:
- keyboard geometry from corrected transform;
- trackpad/recess;
- Touch ID;
- speaker pattern/proxies;
- finger recess;
- bottom feet/screws;
- hinge semantic decomposition;
- closed display/rear silhouette;
- display stack only where facts are freezable.

Preserve:
- 103-angle collision behavior;
- port work unless a calibrated side reference disproves a centerline;
- screen anchors and screen on/off behavior;
- ownership-safe export behavior.

## Phase 6 вЂ” runtime delivery integrity

### [75%] Task 6: restore v1 delivery contract

Current state:
candidate G2 manifest has an internally current source revision, but the canonical v1 delivery test fails because the source files changed while the v1 manifest remains stale.

Required:
- keep G2 candidate isolated while geometry is under review;
- once source set is accepted, rebuild canonical compatibility GLB, Meshopt GLB and manifest from one source state;
- verify source hash/source revision contract;
- preserve required anchors, animations and screen states;
- do not manually patch manifest hashes.

Acceptance:
`test_v1_runtime_manifest_is_current_and_matches_plugin_source` GREEN for a deliberately rebuilt canonical delivery, not by weakening the drift guard.

## Phase 7 вЂ” browser + human gate

### [70%] Task 7: Storybook/Three.js verification

Automated:
- preview tests;
- production Storybook build;
- exact G2/canonical GLB loads;
- screen on/off;
- lid animation;
- Meshopt and compatibility variants;
- clean browser console/network where available;
- portrait/mobile camera fit.

Human:
- phone review of live model;
- top/front/side/bottom/open-deck/hinge/display views;
- explicit accept/reject notes.

Final acceptance requires human approval. A green structural suite cannot substitute for proportion/surface review.

## Final Definition of Done

The MacBook LOW/G2 geometry effort is DONE only when all are true:

1. Apple exact envelope and active display are preserved.
2. Every frozen geometric fact has traceable provenance, method, tolerance and coordinate frame.
3. No PROVISIONAL/UNVERIFIED value is consumed as authoritative production geometry.
4. World-space Blender tests prove the generated model, not merely constants.
5. All 103 hinge angles are collision-safe after the final geometry rebuild.
6. Existing port/anchor/screen-state contracts remain green.
7. Actual model-to-Apple orthographic overlays pass declared residual tolerances for all usable views.
8. Master -> runtime remains a single-source derivation.
9. Canonical v1 GLB/Meshopt/manifest are regenerated and drift guards are green.
10. Storybook/Three.js loads the exact rebuilt runtime asset.
11. Runtime payload/triangle/render-mesh/material metrics are recorded.
12. Fixed May reference | previous AWFUL | G2 candidate comparison exists for perceptual review.
13. Human phone/desktop visual gate explicitly accepts geometry and surface read.
14. PR #121 remains draft until that gate; no merge/deploy beforehand.

## Explicit non-goals

- no direct May mesh copy;
- no invented factory-CAD precision;
- no new GLB pipeline;
- no manual second runtime model;
- no iPad/iPhone rework;
- no material-polish detour before geometry truth is accepted;
- no weakening tests to manufacture GREEN.
