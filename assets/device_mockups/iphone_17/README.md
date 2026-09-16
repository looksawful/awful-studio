# iPhone 17 device asset

Current reference-geometry and runtime checkpoint: **v29**.

v29 is generated and validated in Blender 5.2.1 LTS from `generate_low_v29.py`. It supersedes the earlier v15/v20/v21 geometry checkpoints. It is a publishable runtime candidate, not the final premium/baked asset.

## Authoritative v29 files

- `generate_low_v29.py` — canonical reference-geometry generator.
- `generated/iphone_17_low_v29.blend` — generated Blender scene.
- `evidence/low_v29_validation.json` — dimensional/manifold validation.
- `previews/low_v29/` — ten QA views including front/rear camera and screen-edge macros.
- `export_runtime_v29.py` — canonical GLB/delivery Blender exporter.
- `optimize_runtime_v29.py` — Meshopt web post-process.
- `runtime/v29/iphone_17_v29_delivery.blend` — runtime-oriented Blender package.
- `runtime/v29/iphone_17_v29_web.glb` — compatibility GLB.
- `runtime/v29/iphone_17_v29_web_meshopt.glb` — preferred compressed GLB.
- `runtime/v29/iphone_17_v29.asset.json` — runtime manifest.

## Geometry contract

Reference body dimensions are 71.45 × 149.61 × 7.95 mm. v29 validation reports 71.450002 × 149.609998 × 7.95 mm, zero non-manifold body edges, 19 boolean cuts, no missing mandatory parts and no forbidden front sensor nodes.

The front sensor composition is explicit: one black outer Dynamic Island, a darker elongated sensor pill on the left and exactly one visible round camera on the right. Do not add a second visible circular sensor on the left.

The rear reference block is a narrow vertical camera pill with two optics; flash and rear mic remain separate to the right.

## Runtime verification

Both GLBs are glTF 2.0. Fresh `gltf-transform inspect` must succeed before delivery. The checked-in Khronos validator reports for v29 currently contain zero errors and zero warnings for both compatibility and Meshopt variants; informational messages are retained rather than hidden.

The compatibility asset requires no decoder. The preferred Meshopt variant requires `MeshoptDecoder` and uses `EXT_meshopt_compression` plus `KHR_mesh_quantization`.

The runtime root is `CTRL_IPHONE_17`. Required anchors are `ANCHOR_CENTER`, `ANCHOR_BOTTOM_CENTER`, `ANCHOR_SCREEN_CENTER` and `ANCHOR_REAR_CAMERA`. `SCREEN_CONTENT` remains the replaceable screen object.

## Remaining premium delivery work

v29 deliberately freezes the corrected reference geometry before the final look-development pass. The final premium asset still requires the approved material/bake pass, final transparent presentation renders, texture atlas delivery where appropriate, and final website integration QA. Those steps must build on v29 or a later verified geometry revision, never regress to an older draft.

## Reference

Dimensional source: Apple iPhone 17 Dimensional Drawings, 2025-09-09. The source reference governs physical dimensions and placement; runtime behavior and web contracts are AWFUL STUDIO-specific.
