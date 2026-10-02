# Hybrid MacBook deck tracer slice — 2026-10-02

Issue: #128
Parent spec: #127
Fixed point: `1bd34530686dd2d00a78cf08231e49c2bac2320d`
Authoritative source commit used for the final build: `cdc35a1e49edacb83c576a2438750e37d1081f9b`

## Result

The first hybrid master → runtime tracer slice is implemented and verified.

- The current M5 parametric skeleton remains authoritative for dimensions, hinge mechanics, ports and runtime anchors.
- Trackpad presentation is now a profiled glass surface with weighted normals rather than the prior thin rounded slab.
- Keycaps retain family-specific perimeter profiles and now have real shallow concave top geometry. Representative runtime families are regular, modifier, space, arrow, function and Touch ID.
- The master retains physical speaker apertures. Runtime delivery swaps the perforated master body for the clean pre-speaker body plus two deterministic alpha+normal speaker proxies generated from the same aperture pattern. This strategy is named `derived_alpha_normal_proxy`; it is not claimed to be a literal texture bake.
- Runtime visibility changes are scoped to the MacBook root hierarchy rather than global `bpy.data.objects`.

## Runtime metrics

| Metric | prior current-AWFUL baseline | hybrid #128 |
| --- | ---: | ---: |
| visible triangles | 198,785 | 154,623 |
| render meshes | n/a in prior manifest | 389 |
| materials | 16 | 16 |
| compatibility GLB | 8,971,360 B | 4,572,992 B |
| Meshopt GLB | 2,247,728 B | 1,728,516 B |

The keycap dish increases local keyboard geometry while the speaker runtime substitution removes the much larger live perforation cost. The candidate remains below the previous runtime triangle budget. The wider spec target of fewer than 50 render meshes is **not** claimed here; that remains later optimization work.

## Structural/runtime verification

- Blender: 5.2.1 LTS.
- Base validation: PASS; 312.599987 × 221.200004 × 8.3 mm base.
- Hinge clearance: PASS for every integer angle 0–102° (103 states).
- Hybrid deck Blender validator: PASS.
- Targeted MacBook contracts: 9/9 PASS.
- Preview tests: 12/12 PASS.
- Full fast suite: 176/177 PASS. The sole failure is the pre-existing independent iPad v6 manifest drift: `source hash mismatch: assets/device_mockups/ipad_pro/generate_low_v6.py` / `source_revision mismatch`. No iPad source was changed in this branch.
- Storybook static build: PASS after the final GLB build.
- MacBook browser helper: PASS, reporting asset `macbook-pro-14-m5-v1`, 77 keys, and required HDMI/Thunderbolt/Touch ID details.
- Runtime GLB SHA-256: `1837643b1c4dc3ce3e7f93b3417f68e55c2208f0ce6f4e6b36cf71c8c94937f9`.
- Storybook-served GLB SHA-256: same value, proving browser evidence used the exact rebuilt asset.

## Visual evidence

`hybrid128-deck-comparison.png` uses the same comparison rig for:

1. May Jestei visual reference;
2. the pre-hybrid AWFUL baseline;
3. the final #128 hybrid deck.

The May file is used only as a perceptual/construction reference. Its dimensions and third-party-derived source mesh are not reused.

## Remaining scope

This tracer slice proves the architecture, not final LOW acceptance. The candidate still has 389 render meshes and the full-keyboard/speaker consolidation target belongs to #130. Display/lid/glass fidelity belongs to #129. Final assembly/runtime optimization and human LOW gate belong to #131.
