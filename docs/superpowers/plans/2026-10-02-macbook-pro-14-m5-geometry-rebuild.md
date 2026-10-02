# Implementation Plan: MacBook Pro 14 M5 metric geometry rebuild

Date: 2026-10-02
Tracker: GitHub issues #127, #129, #130, #131
Status: G1 calibration evidence generated; awaiting human overlay approval. Product geometry remains unchanged.

## Objective

Replace hand-tuned internal placement with a traceable metric geometry contract derived from Apple primary sources, then rebuild display and deck geometry from that contract before resuming visual/material optimization.

## Architecture decisions

1. Chassis envelope is the global datum. No key, trackpad, speaker or camera is an independent origin.
2. Geometry truth lives in one deep module: a small interface exposing frozen measurements and derived transforms.
3. Every frozen value carries provenance, method and tolerance.
4. Current internal coordinates are PROVISIONAL until revalidated.
5. Master and runtime consume the same geometry contract.
6. Tests assert geometry mathematics. Storybook/render review is the human perceptual gate.
7. Do not create a second modeling pipeline; keep the existing Blender -> GLB -> Meshopt -> Storybook delivery path.

## Revised dependency graph

    Apple primary sources
            |
            v
    reference register + calibration transforms
            |
            v
    metric geometry contract + math tests
          /   \
         v     v
    #129 display   #130 deck
         \       /
          v     v
            #131 integration/runtime/final LOW gate

Because #129 is already the active work item, its first checkpoint becomes the shared calibration foundation. #130 may start after that checkpoint; it does not need to wait for #129's final glass polish.

## Phase 1 — freeze and establish references (#129 calibration checkpoint)

### Task 1: Freeze current WIP as comparison baseline
Description:
Preserve the current #129 Storybook/runtime state as a visual baseline. Stop adding visual geometry until calibration is approved.

Acceptance:
- current runtime asset remains viewable in Storybook;
- baseline commit/hash and asset sizes are recorded;
- no existing geometry is promoted to truth merely by being current.

Verification:
- Storybook loads MacBook story;
- git diff/status captured;
- existing hinge/envelope gates remain known-good.

Scope: S

### Task 2: Register Apple primary-source set
Description:
Create a source register for Apple tech specs, Product Bezel, model-specific keyboard/dimension/display/port imagery and repair/service pages.

Acceptance:
- every source has URL, local asset path if downloaded, source class and intended measurement use;
- sources are separated into exact / calibrated / relational;
- non-authoritative May/Jestei reference is explicitly marked visual-only.

Verification:
- all URLs resolve;
- local files have hashes/dimensions where applicable.

Scope: S

### Task 3: Build reproducible 2D calibration transforms
Description:
For each accepted planar Apple image, derive pixel -> millimetre calibration from a Tier-A datum and record residual error.

Acceptance:
- transformation is reproducible from source image + known datum;
- bilateral/known-dimension residual is below a declared tolerance;
- perspective-distorted references are rejected for metric measurement.

Verification:
- a script/report reproduces transform and residuals;
- human overlay shows calibrated reference over model coordinate plane.

Scope: M

## Checkpoint G1 — Human calibration review

Human reviews:
- chassis datum orientation;
- accepted Apple images;
- overlays;
- tolerance policy;
- whether any source is visibly unsuitable.

Do not rebuild geometry before G1 approval.

Current G1 implementation intentionally includes the provisional geometry-contract schema plus deck/display source-pixel measurements and overlays, per issue #129. G1 approves the calibration method/evidence; it does not freeze those provisional values.

## Phase 2 — promote approved measurements and complete the metric geometry contract

### Task 4: Promote the G1 geometry-contract scaffold
Description:
The schema scaffold exists during G1. After approval, promote accepted provisional measurements into calibrated/frozen facts and extend the same module for unresolved anchors.

Interface categories:
- chassis
- deck
- keyboard
- speakers
- trackpad
- touch_id
- finger_recess
- display
- camera_notch
- hinge
- ports
- edge_profile

Acceptance:
- no measurement is represented as an unexplained naked coordinate;
- every frozen measurement has source class + tolerance;
- derived values are formulas over stronger datums.

Verification:
- schema validation tests;
- source/provenance completeness tests.

Scope: M

### Task 5: Solve keyboard lattice
Description:
Fit keyboard origin, 1x1 pitch and row pitch using many repeated keys from Apple imagery. Encode Apple service families 1x1, 1x0.5 and link-bar.

Acceptance:
- repeated 1x1 keys share one fitted size/pitch;
- rows close against calibrated bounds;
- function row, arrows and Touch ID satisfy measured alignment constraints.

Verification:
- numerical lattice tests;
- overlay of generated key bounds on Apple keyboard reference.

Scope: M

### Task 6: Solve deck anchors
Description:
Calibrate trackpad, speaker fields, Touch ID, finger recess and their relations to chassis/keyboard.

Acceptance:
- trackpad center/gaps and corner radius are explicit;
- speaker field bounds/lattice are explicit;
- finger recess is chassis-profile geometry;
- Touch ID is a black/default control with measured placement.

Verification:
- math tests for symmetry, gaps and alignments;
- calibrated deck overlay.

Scope: M

### Task 7: Complete display anchors
Description:
Promote the approved G1 Product Bezel display/notch/camera measurements, then complete lid/glass/lower-rail geometry from the same calibrated references.

Acceptance:
- all key display relationships derive from calibrated datums;
- lid/glass corner radii and notch/camera positions are explicit;
- disputed current values are removed from the frozen set.

Verification:
- math tests;
- front-view overlay residual within tolerance.

Scope: M

## Checkpoint G2 — Geometry contract human review

Human reviews Apple overlay against:
- keyboard/deck;
- display/notch/camera;
- finger recess;
- speaker fields;
- side/chamfer silhouette.

Only approved values become frozen.

## Phase 3 — rebuild from contract

### #129 Display/lid slice
Rebuild:
- lid profile;
- glass stack;
- bezel;
- notch/camera;
- lower rail;
- hinge-to-display visual junction.

Acceptance:
- consumes geometry contract only;
- no new unexplained spatial constants;
- 103-angle hinge gate remains green;
- Storybook human review passes geometry before material polish.

### #130 Deck slice
Rebuild:
- keyboard from lattice;
- Touch ID;
- trackpad;
- speakers;
- finger recess;
- edge/chamfer profile;
- baked/runtime speaker representation from same pattern contract.

Acceptance:
- consumes geometry contract only;
- no hand-placed individual keys;
- speaker master/runtime share one lattice;
- mathematical tests green before visual review.

## Checkpoint G3 — Full geometry human review

Storybook review at fixed neutral material/lighting:
- top/deck view;
- low front edge;
- left/right side;
- display front;
- hinge/lower rail;
- macro keyboard/speaker/trackpad.

Do not proceed to final material polish if proportions are still disputed.

## Phase 4 — #131 integration and runtime

Only after G3:
- final normals/material hierarchy;
- texture/legend atlases;
- mesh/material consolidation;
- runtime performance;
- May/current/hybrid comparison;
- final LOW visual gate.

## Test strategy

### Exact
Use very tight tolerance for Apple-stated envelope values.

### Calibrated
Tolerance comes from source resolution and calibration residual. Never fake precision beyond the raster.

### Relational
Test equality, symmetry, ordering and alignment when Apple documentation establishes a relationship without public metric values.

### Runtime
Existing hinge, GLB, Meshopt, Storybook and browser tests remain downstream gates.

## Risks

### Risk: product imagery is perspective-rendered
Mitigation:
reject it for metric measurement; use only silhouette/reference or solve a homography when enough exact datums exist.

### Risk: raster anti-aliasing creates fake precision
Mitigation:
fit repeated structures statistically; declare tolerance from residual, not decimal places.

### Risk: Apple imagery differs between ANSI/ISO variants
Mitigation:
freeze one keyboard layout variant explicitly; do not mix maps.

### Risk: edge highlights are mistaken for physical chamfers
Mitigation:
measure silhouette for geometry; treat highlight shape as lower-confidence shading evidence.

### Risk: current tests lock wrong geometry
Mitigation:
classify old constants as PROVISIONAL and replace tests with source-backed contracts, not merely loosen them.

## Definition of done for the calibration effort

- every visible macro element has traceable source/provenance;
- every repeated layout follows shared mathematical invariants;
- no unexplained placement constant is introduced in the generator;
- calibrated overlays pass human review;
- existing mechanical/runtime contracts remain green;
- only then resume high-fidelity shading/material optimization.
