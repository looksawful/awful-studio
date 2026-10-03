# MacBook G2 overlay calibration checkpoint — 2026-10-03

Base checkpoint: `2f95ad1` on `agent/129-geometry-calibration`
Stack branch: `fix/macbook-g2-overlay-calibration`
Issue: #129

## Why this delta exists

Technical review of the eight actual-model -> Apple overlays found two false-confidence defects in the overlay evidence code, not in Blender geometry:

1. side-port source pixels were divided by two even though `port_layout.py` stores native coordinates from the cached ~409 px Apple side images;
2. front/side Z mapping normalized the model's own `zmin..zmax` into the image bounds, so a wrong model height could still appear to fit.

## Fix

- native Apple side pixels are used directly;
- front and side Z use a fixed 15.5 mm Apple closed-height scale;
- a too-tall model now projects outside the Apple silhouette instead of being normalized back into it;
- side-port values are reported as **reprojection consistency**, not independent geometry truth;
- calibration provenance and limitations are documented in:
  `docs/asset-library/research/2026-10-03-macbook-g2-overlay-calibration.md`.

## Fresh evidence

Focused overlay regression:
- native side-pixel mapping GREEN;
- fixed-height Z mapper GREEN;
- deliberately too-tall model stays RED-capable;
- bottom-foot matching remains order-independent and displaced geometry remains RED-capable.

Fresh G2 verification run in the source worktree before extracting this delta:
- 22/22 focused G2 tests GREEN;
- Blender 5.2.1 construction PASS;
- closed assembly: 312.5999868 × 221.2000042 × 15.5039959 mm;
- deck/ports PASS, 78 keys and all seven ports;
- hinge clearance: 103/103 states GREEN, 0..102°, max checked intersection 0.0 mm³.

Current overlay report after the fix:
- top bbox residual: 0 px;
- front silhouette bbox residual: 0 px;
- left/right Z silhouette residual: 0 px;
- left port reprojection: 0.5 px;
- right port reprojection: 0 px;
- feet: 0.877 / 1.567 / 1.239 / 0.555 mm;
- display notch bbox: 0 px;
- camera center: 0.5 px.

## Gate status

The user accepted the corrected eight model-to-Apple overlays on 2026-10-03.

Canonical v1 was then rebuilt from the accepted source state. Continue from:
`docs/agents/handoffs/2026-10-03-macbook-g2-runtime-rebuild-checkpoint.md`.

Do not reopen already-green Blender geometry unless new evidence produces a RED.
