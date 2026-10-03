# MacBook G2 checkpoint — 2026-10-03

Branch: `agent/129-geometry-calibration`
Audit fixed point / parent before this checkpoint: `518bb25`
Primary issue: #129
PR #121 remains draft. No merge or deploy.

## What is implemented

- Corrected G2 chassis/deck calibration is the active datum. Rejected G1 inset-corner homography is not reused.
- Typed per-fact provenance replaces aggregate authority for G2 external facts.
- Unsupported hinge cover depth/thickness are demoted to PROVISIONAL / UNVERIFIED_VISUAL.
- Relational visual facts are separated from metric facts.
- Production geometry accessors reject non-freezable facts.
- Real Blender world-space assertions cover keyboard, keyboard well, trackpad, Touch ID, speakers, feet and bottom screws.
- The generated 78-key aggregate is reconciled to the independent G2 target.
- Guessed display physical stack dimensions were removed from production geometry. Active display / Product Bezel notch-camera facts are individually sourced; unsupported outer surround stays RELATIONAL_VISUAL.
- Actual evaluated Blender geometry is exported through `tools/export_macbook_g2_model_projection.py` and consumed by `tools/build_macbook_g2_surface_overlays.py`.
- Bottom-foot overlay matching no longer independently sorts target/model points by noisy raster Y. It performs a four-point one-to-one metric assignment.

## Foot-overlay root cause and fix

The previous report contained residuals:
`270.685 / 272.252 / 0.877 / 1.567 mm`.

Root cause: point correspondence, not Blender geometry. The two rear model feet round to the same raster Y, while Apple detections differ by two Y pixels. Lexicographic `(y, x)` sorting swapped rear left/right.

Correct correspondence after the fix:

- model (97,524) -> Apple (95,523): 0.877 mm
- model (789,524) -> Apple (785,524): 1.567 mm
- model (97,78) -> Apple (94,79): 1.239 mm
- model (789,78) -> Apple (788,77): 0.555 mm

Regression contract:
`tests/fast/test_macbook_g2_overlay_pairing.py`

It verifies:
- pairing is input-order independent;
- max correct residual stays <2 mm;
- a deliberate +100 px geometry displacement remains RED (>20 mm).

An independent GPT-6.1 Sol read-only Codex review reproduced the same root cause and correspondence.

## Fresh verification at shutdown

Fast G2 contract subset:
`python -m unittest -v tests.fast.test_macbook_g2_external_contract tests.fast.test_macbook_g2_geometry_contract tests.fast.test_macbook_g2_model_overlay_contract tests.fast.test_macbook_g2_overlay_pairing tests.fast.test_macbook_g2_provenance_contract`

Result: **20/20 GREEN**.

`git diff --check`: GREEN.

Fresh model-to-Apple overlay report after pairing fix:

- closed top bbox: 0 px
- left port centers: <=0.5 px
- right port centers: <=0.5 px
- foot centers: 0.877 / 1.567 / 1.239 / 0.555 mm
- display notch bbox: 0 px
- display camera center: 0.5 px

Fresh Blender 5.2.1 hinge gate on current G2 candidate:
**103/103 states GREEN, 0..102 degrees**, all checked intersection volumes 0.0 mm^3.

Earlier in the same current geometry state, before the overlay-only point-matching change:
- closed assembly ~312.5999868 × 221.2000042 × 15.5039959 mm
- construction gate GREEN
- deck/ports gate GREEN
- 78 keys and all seven port checks GREEN

The point-matching change does not modify Blender geometry.

## Current gate

Do **not** rebuild canonical v1 yet.

Strict continuation order:

1. Human/visual inspect all eight current actual-model -> Apple overlays:
   - `01_top_closed_overlay.png`
   - `02_front_overlay.png`
   - `03_left_ports_overlay.png`
   - `04_right_ports_overlay.png`
   - `05_bottom_overlay.png`
   - `06_deck_overlay.png`
   - `07_hinge_cover_overlay.png`
   - `08_display_overlay.png`
   Evidence directory is intentionally gitignored.
2. If the overlays expose a real geometry defect, return to RED-capable G2 tests and fix only that defect.
3. If overlays are accepted, rerun final structural gates on the accepted source.
4. Rebuild G2 candidate + canonical compatibility/Meshopt/manifest from that one accepted source state.
5. Restore canonical drift guard to GREEN by rebuild, never by weakening hashes/manifests/tests.
6. Run Storybook/browser against the exact rebuilt runtime asset.
7. Final human visual gate.
8. Only after the above may PR #121 / downstream delivery be considered.

## iPad read-only findings recovered while Codex limits were being conserved

PR #122 / issue #51 was inspected read-only. Do not edit the iPad branch from this worktree.

Highest-confidence Required follow-ups:

1. Separate TOP_BUTTON provenance from volume-button provenance. Apple M5 drawings support the 2.26 mm VOLUME BUTTON profile, but no equivalent proof was established for TOP_BUTTON. The current Blender contract falsely gives all three controls the same Apple-backed authority.
2. Rear camera/housing/rings/glass/pupil/flash/LiDAR/mic remain estimated LOW geometry. Build source-backed calibrated silhouette/dimension RED tests before changing those constants.
3. Screen `sw/sh/sr` values remain project/derived geometry until calibrated against an actual active-edge/Product Bezel source. Do not promote ppi-derived display envelopes to exact physical active-edge authority. Native screen UI/site-resume variants remain unfinished.

Do not reopen already verified iPad optical depth, USB-C recess/tongue, normals, emission-only screen content, browser depth behavior, or the intentional single-surface web export unless new visual evidence fails.

## Skills / process

For continuation:
- use AskMatt only to route from this implementation state; do not create another spec/ticket cycle;
- unexplained RED -> diagnosing-bugs first;
- implementation -> TDD;
- final diff -> code-review against fixed point `518bb25` and #127/#129;
- repo-local 3D hard-surface review skill was installed locally from `omer-metin/skills-for-antigravity` source commit `e8dcf4e8...`; it is not authoritative over repo evidence;
- preserve dirty/foreign work and keep one writer per problem domain.

## Deliberately not completed

- no canonical v1 rebuild
- no canonical drift claim
- no Storybook/browser rebuild check after G2 acceptance
- no human visual acceptance
- no merge
- no deploy
