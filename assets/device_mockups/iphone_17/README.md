# iPhone 17 device asset

Current geometry candidate: **v21** (`aca3652`). Current packaged web/runtime delivery remains **v15** until it is rebuilt from v21 and revalidated.

Use `generate_low_v21.py`, `generated/iphone_17_low_v21.blend`, `evidence/low_v21_validation.json`, and `previews/low_v21/` as the authoritative geometry/look source. Do not use v15 geometry for new renders or modeling work.

## Current geometry files

- `generate_low_v21.py` — current Blender geometry generator.
- `generated/iphone_17_low_v21.blend` — current generated Blender scene.
- `evidence/low_v21_validation.json` — dimensional/topology validation; currently `passed: true`.
- `previews/low_v21/` — current diagnostic and presentation renders.

## Runtime delivery status

- `runtime/v15/` is the last packaged runtime delivery, but its geometry is stale relative to v21.
- `export_runtime_v15.py` and `optimize_runtime_v15.py` document the previous export/meshopt pipeline only.
- Runtime promotion must be rebuilt from the current geometry source and must not silently fall back to v15.

## Geometry contract

Nominal body dimensions are 71.5 × 149.6 × 7.95 mm. Validation must remain within 0.01 mm and report zero non-manifold body edges.

The rear camera assembly follows the Apple dimensional drawing: a narrow vertical two-camera housing on the left side of the rear view, with flash and rear mic separate to its right. The front sensor composition is one Dynamic Island surface with a single visible front camera.

## Build and QA

1. Generate v21 with Blender 5.2.1 LTS.
2. Confirm `passed: true` in `low_v21_validation.json`.
3. Review front, rear, three-quarter, both side views, camera macro and front-sensor macro.
4. Before runtime promotion, rebuild Blender delivery + GLB from v21 and validate node set, dimensions, materials and triangle budget.
5. Run Khronos glTF validation and browser/Three.js QA before replacing the existing runtime package.

Tracked delivery/source-drift work: issue #70.

## Reference

Dimensional source: Apple iPhone 17 Dimensional Drawings, 2025-09-09. The source reference is used for dimensions and placement; runtime behavior and web contracts are AWFUL STUDIO-specific.
