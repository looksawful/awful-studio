# MacBook Pro 14 M5 — G1 calibration evidence

Date: 2026-10-02
Issue: #129
Branch: `agent/129-geometry-calibration`
Gate: G1 — awaiting human overlay approval

## Scope

This checkpoint establishes source-backed geometry measurement infrastructure only.
No Blender product geometry, runtime GLB, hinge, ports, or screen-state source was changed.

Global datum remains the exact Apple chassis envelope:
- width 312.6 mm
- depth 221.2 mm
- closed height 15.5 mm
- origin at chassis plan center

Only Apple exact datums are frozen. All new internal measurements remain
`PROVISIONAL` / `frozen=false` until the owner accepts the overlays.

## Source register

`calibration_sources.json` records Apple URLs, cache keys, SHA-256,
pixel dimensions, authority class and intended measurement use.
Apple artwork itself is not committed.

Pinned local evidence includes:
- keyboard/spec image: `bbe7b727…759788`
- Product Bezel Space Black PNG: `1863c54d…8c6d57`
- dimension/display/port images: individually SHA-256 pinned in the register.
## RED → GREEN

First RED:
- `test_macbook_geometry_calibration_contract` failed because
  `geometry_contract.py` did not exist.

First GREEN:
- source register + geometry schema added;
- exact chassis facts are traceable/freezable;
- keyboard lattice, trackpad X and speaker periodicity are explicit but provisional.

Second RED:
- trackpad Y, Touch ID and Product Bezel calibration fields were absent.

Second GREEN:
- trackpad front seam separated from chassis edge;
- Touch ID geometry recorded;
- Product Bezel native display/notch/camera metrics recorded.

CLI regression RED:
- direct `python tools/calibrate_macbook_m5_geometry.py` failed to import repo modules.

CLI regression GREEN:
- direct CLI execution now passes and generates evidence.

Review-finding GREEN:
- every provisional measurement now carries source/method/tolerance/frame/confidence;
- source pixels are the single measurement truth; metric values are derived;
- deck homography records manual-pick uncertainty separately from zero-by-construction fit residual;
- report and overlays consume the same contract coordinates;
- calibration-only dependencies are pinned in `tools/requirements-calibration.txt`.

## Deck calibration

Perspective keyboard image is rectified from:
`(119,28) (1020,32) (1017,667) (113,662)`
onto the 312.6 × 221.2 mm chassis plane at nominal 4 px/mm.

Preliminary measurements:
- standard key outer: ~16.75 × 16.25 mm
- pitch X: ~19.25 mm
- row pitch: ~18.958 mm
- trackpad X seams: ~-65.389 / +66.552 mm
- trackpad X residual from chassis center: ~+0.581 mm
- trackpad top seam: 542.647 px on the exact 4 px/mm rectified plane
- trackpad bottom seam: 873.905 px
- physical chassis front edge: 884.8 px
- trackpad height: ~82.814 mm
- front trackpad gap: ~2.724 mm
- trackpad center Y: ~-66.469 mm
- Touch ID outer key: ~16.75 × 16.75 mm
- Touch ID sensor: ~9.0 mm diameter
- Touch ID default appearance contract: black
- speaker periodicity: ~1.0 mm X/Y
- observed left speaker field: ~13.5 × 108.75 mm
- speaker row/column counts deliberately remain unfrozen.

## Display calibration

Product Bezel transparent opening is exactly 3024 × 1964 px.
At Apple 254 ppi this is exactly 10 px/mm:
- active display: 302.4 × 196.4 mm
- notch top width: ~38.6 mm
- notch height: ~6.4 mm
- display-opening corner radius fit: ~4.10 mm; RMS ~0.064 mm
- notch lower-radius fit: ~2.19 mm; RMS ~0.030 mm
- camera center: ~0.10 mm left of display center, ~1.65 mm from display top.

Outer lid is not promoted to metric truth from Product Bezel:
- observed width at display scale: 313.5 mm
- Apple exact chassis width: 312.6 mm
- residual: +0.9 mm
- fitted outer radius ~8.99 mm remains provisional.

## Generated evidence

`evidence/g1_calibration/calibration_report.json`
`evidence/g1_calibration/deck_calibration_overlay.png`
`evidence/g1_calibration/display_calibration_overlay.png`

Generator:
`python tools/calibrate_macbook_m5_geometry.py --cache-root F:\Temp`

Output SHA-256:
- report: `a73978bf65c971e0339bfdb3735dceafe4af7175bee0fcfef50af31ce07b3a97`
- deck overlay: `e4f75aa3b9bf5534bb8afb67fda091feaf218266459f3c1aae875909a1ad9d83`
- display overlay: `e10a056f6dc2e34af9597dbaf35574ee7a41270b5f9afb897ff0e72e6dafb5c4`

## Verification

Targeted calibration tests:
- 19/19 PASS

MacBook-focused fast slice:
- 30/30 PASS

Repository full fast suite:
- 196 tests executed
- 195 PASS
- 1 FAIL: pre-existing iPad v6 delivery drift
  (`generate_low_v6.py` source hash mismatch + source_revision mismatch)
- this failure is outside #129 and matches the prior handoff.

`git diff --check`: PASS

## Stop condition

Do not rebuild or polish MacBook geometry yet.

Human G1 must approve:
1. chassis datum orientation;
2. deck homography / overlays;
3. trackpad seam interpretation;
4. Touch ID bounds;
5. speaker field interpretation;
6. Product Bezel display/notch/camera method;
7. provisional tolerance policy.

After approval, promote accepted measurements to calibrated contract values and
continue #129 / #130 from the same contract.
