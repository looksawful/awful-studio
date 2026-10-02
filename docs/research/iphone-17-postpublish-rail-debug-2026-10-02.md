# iPhone 17 post-publish rail / corner debug — 2026-10-02

Status: IN PROGRESS. Current source head is PR #126 `6098ffa6128fbac6c1cbdb90d53e6fc927a35ea5`. Do not resume from PR #119 for production fixes.

## Authority correction

- The production Gallery loads `/media/models/devices/iphone-17-v30.web.meshopt.glb`.
- Production `.web.glb` and `.web.meshopt.glb` SHA-256 hashes match the PR #126 AWFUL STUDIO artifacts exactly.
- Therefore the live model is not a stale pre-#126 GLB.
- Dynamic Island ownership is already corrected on PR #126: active texture is `ios26_home_screen_clean_1206x2622.png`; original Apple screen image remains reference/provenance; the visible island is geometry.

## Reproduced defect

The current PR #126 deterministic Blender `CAM_SCREEN_EDGE_MACRO` still shows a visible highlight kink / surface discontinuity around the outer top-right aluminium rail transition. The same production asset can be loaded in the live Three.js Gallery and rotated through side / three-quarter angles.

This is the current RED visual symptom. Existing fast tests (13/13 focused front + web-shading) do not assert this defect.

## Hypothesis probes already executed

All probes use the current PR #126 generated blend, the same `CAM_SCREEN_EDGE_MACRO`, same scene and lighting unless noted.

1. Bevel segments 4 → 12: no material visual improvement.
2. Disable BODY `WEIGHTED_NORMAL`: no material visual improvement.
3. Disable weighted normals + `EDGE_BEVEL.harden_normals = False`: no material improvement.
4. Add triangulation before/after bevel with the above normal policy: no material improvement.
5. Increase BODY rounded-outline sampling 48 → 128 in a temporary generator: no material improvement; structural validation remains GREEN.

These falsify the simple explanations “too few bevel segments”, “Weighted Normal alone”, and “outline tessellation alone”.

## Stronger source finding

Current source uses a generic circular rounded rectangle:
- `BODY_R = 13.6 mm`
- `foundation_common.rounded_outline()` joins straight edges to constant-radius circular arcs.

The 13.6 mm value originates in the early generator history and is not traced to the official Apple dimensional drawing.

Apple publishes an explicit **CORNER PROFILE (ALL FOUR CORNERS), DETAIL A** for iPhone 17 rather than a single housing radius. The official drawing also specifies product size 71.45 × 149.61 × 7.95 mm. The current generic circular profile is therefore an approximation, not a source-locked housing contour.

Primary sources:
- Apple Dimensional Drawings index: https://developer.apple.com/accessories/dimensional-drawings/
- Apple iPhone 17 Dimensional Drawings (2025-09-09): https://developer.apple.com/download/files/accessories/dimensional-drawings/iphone-17.pdf
- Apple iPhone 17 technical specs: https://support.apple.com/en-gb/125089

Local official PDF:
`assets/device_mockups/iphone_17/reference/pure_ref/apple_iphone_17_dimensional_drawings_2025.pdf`

## Current hypothesis ranking

1. **Housing corner-profile mismatch**: generic constant-radius `BODY_R=13.6` does not reproduce Apple's explicit corner profile; metallic highlights expose the curvature mismatch. Highest confidence.
2. Depth/bevel cross-section still differs from Apple detail even after silhouette correction.
3. Boolean topology could locally perturb normals, but current kink survives normal-policy changes and higher outline tessellation.
4. Three.js lighting/runtime is not primary: the defect class is visible in canonical Blender evidence before runtime.

## Next RED seam

Use the canonical source → generated BODY_ALUMINUM geometry / deterministic edge render seam.

Before a source fix:
1. encode the Apple corner profile as reference data derived from Detail A;
2. add a regression that compares generated housing corner coordinates/profile against that reference, rather than checking a source literal;
3. keep the deterministic Blender screen-edge macro as visual evidence.

Then apply the smallest iPhone-local geometry change. Do not change shared `foundation_common.rounded_outline` unless another asset actually needs the same Apple-specific profile.

## Scope guard

- Keep canonical identity `iphone_17 v30`; no v31/v32.
- No frontend normal hacks.
- No OpenCV/NumPy screen-processing branch from the old PR #119-based experiment.
- Do not touch unrelated dirty worktrees.
- Site asset sync happens only after AWFUL STUDIO source + export gates are green.
