# MacBook G2 canonical runtime rebuild checkpoint — 2026-10-03

Parent stack commit: `0d25c1f` / draft PR #132
Base source checkpoint: `agent/129-geometry-calibration`
Issue: #129

## Gate change

The user accepted the corrected eight model-to-Apple overlays, so the canonical runtime rebuild gate is now open.

Before rebuild, the canonical drift test was intentionally RED:

`test_v1_runtime_manifest_is_current_and_matches_plugin_source`

It reported six source-hash mismatches plus a `source_revision mismatch`. No drift guard or manifest validation was weakened.

## Canonical writer used

Only the existing canonical writer was used:

`python tools/build_macbook_v1_web.py --blender "D:\Blender Foundation\Blender 5.2\blender.exe"`

That pipeline performs:

1. fresh G2 source generation;
2. hinge/deck/construction/hybrid structural validation;
3. authoritative extension blend packaging;
4. loader source-revision update;
5. compatibility GLB export;
6. Meshopt GLB derivation;
7. manifest/source hash/artifact hash/runtime QA write.

No second writer and no manual manifest/hash patch was introduced.

## Fresh rebuild evidence

Source revision:
`e0a105f4c83fa6695437e7bfb2c8f917b61d102da4bda4a9084a63a683693840`

Source commit:
`0d25c1ffba30dbc53c75b4879dffb8e348638613`

Blender 5.2.1:

- generation validation: PASS
- deck/ports: PASS, 78 keys, all seven ports
- construction: PASS
- closed assembly: 312.5999868 × 221.2000042 × 15.5039959 mm
- hybrid deck: PASS
- hinge: 103/103 states, 0..102°, max checked intersection 0.0 mm³

Canonical runtime:

- compat GLB: 4,551,912 bytes
- Meshopt GLB: 2,054,096 bytes
- Meshopt ratio: 0.4513
- required extensions: `EXT_meshopt_compression`, `KHR_mesh_quantization`
- required nodes preserved in both variants
- compatibility GLB remains the default variant
- Meshopt remains the preferred variant

Runtime QA:

- triangles: 153,909
- nodes: 394
- render meshes: 387
- materials: 16
- runtime bounds recorded: 312.6 × 227.187 × 271.787 mm in the exported open-lid runtime state

Artifact hashes are recorded in the rebuilt manifest for:

- delivery blend
- compatibility GLB
- Meshopt GLB

## Post-rebuild tests

`tests.fast.test_macbook_web_delivery_contract`: GREEN

`tests.fast.test_macbook_hybrid_deck_contract`: GREEN

Combined result: **6/6 GREEN**.

The formerly RED drift test is now GREEN due to the rebuild itself.

## Performance note

153,909 triangles are within the current approximate visible runtime budget, but 387 render meshes and 16 materials are above the preferred long-term target (<50 meshes, ideally 20–30, ~10 materials).

This is recorded as runtime optimization debt for the browser/performance and downstream #130/#131 work. Do not rewrite geometry or collapse semantic nodes before browser acceptance merely to chase a prettier count.

## Next stage

Phase 6 canonical delivery integrity is complete.

Next stage is browser/runtime acceptance on the exact rebuilt artifacts:

1. production Storybook build;
2. load exact compat and Meshopt variants;
3. screen on/off;
4. lid animation;
5. required anchors and node hierarchy;
6. browser console/network cleanliness;
7. portrait/mobile camera fit;
8. record actual runtime performance/render metrics;
9. final visual gate.

Do not claim final release completion before that browser/human stage.
