
    # iPhone 17 — asset dossier

    ## Identity and production role
    - Asset ID: `iphone_17`
    - Category: `DEVICE_MOCKUP`
    - Identity class: `PROJECT_VERIFIED`
    - Current stage: `LOW_DRAFT`
    - Quality tier: `HERO`
    - Variants: `Space Black`, `Silver`
    - `production_ready=true` means this dossier is complete enough to enter the next modeling gate; it does not mean the 3D asset is released.

    ## Dimensional contract
    - **body_mm**: `[71.5, 149.6, 7.95]`; confidence `VERIFIED`.
    - Blender scale is metric: `1 Blender unit = 1 metre`.
    - `DESIGN_STANDARD` dimensions are frozen representative production targets, not historical manufacturer claims.

    ## Reference and provenance
    - `iphone17_current` [PROJECT_VERIFIED_SOURCE]: assets/device_mockups/iphone_17/README.md — Current iPhone 17 geometry and runtime contract.
    - Identity claims must not be upgraded beyond the evidence class without a new primary source.

    ## Component decomposition
    - `unibody`
- `display_stack`
- `dynamic_island`
- `front_camera`
- `rear_camera_system`
- `buttons`
- `ports`
- `logo`
    - Hidden construction may be simplified only when it does not affect articulation, silhouette, shadows, mount compatibility or bake results.

    ## Geometry plan
    Build primary enclosure from verified envelope; keep glass, optics, controls and seams separate; use real bevel widths and non-destructive modifiers until runtime bake.
    - Blockout must match every frozen dimensional field before secondary detail begins.
    - MID preserves silhouette, control placement, seams, pivots and mount interfaces; HIGH is source-only detail for baking where useful.

    ## Materials and surface response
    - `anodized_aluminum`: keep a distinct physical surface role; do not collapse unlike materials merely to reduce slots.
- `display_glass`: keep a distinct physical surface role; do not collapse unlike materials merely to reduce slots.
- `optical_glass`: keep a distinct physical surface role; do not collapse unlike materials merely to reduce slots.
- `matte_black`: keep a distinct physical surface role; do not collapse unlike materials merely to reduce slots.
- `decal`: keep a distinct physical surface role; do not collapse unlike materials merely to reduce slots.
    - Master shaders remain editable in Blender; runtime shaders must be glTF-friendly and bounded in cost.

    ## UV and texture plan
    - Target: `4K authoring / 2K runtime`; hidden surfaces may receive lower density, but visible hero surfaces keep consistent texel density.
    - UV0 carries PBR surfaces; UV1 or decals may carry labels, legends, logos and non-repeating identification marks.
    - Unique wear belongs only where reference evidence or product use justifies it.

    ## Bake plan
    - Bake `Normal`, `AO`, `Curvature`, `Thickness`, `Position` and material/object ID from HIGH to MID/LOW only where geometry warrants it.
    - Runtime outputs use BaseColor, Roughness, Metallic, Normal, AO, Opacity/Transmission and Emission as applicable.
    - Master masks stay separate; packed ORM is allowed only for delivery/runtime optimization.

    ## LOD, collision and runtime
    - Shipping format: `GLB`.
    - LOD contract: LOD0, LOD1, LOD2.
    - Collision contract: `simple_proxy`; collision geometry must stay separate from hero/render geometry.
    - LOD1 target is at most 75% of LOD0 triangles; LOD2 target is at most 35% while preserving silhouette and mounts.
    - Export excludes preview cameras, lights, reference envelopes and authoring-only helpers.

    ## Rigging, variants and mounts
    **Articulation**
    - static
    **Semantic mounts / origins**
    - `SCREEN_PLANE`
- `FLOOR_CONTACT`
    - Origins must be deterministic and useful for placement, animation and Auto Fit.

## QA and acceptance gates
- Dimensional validation passes for every frozen measurement and origin/mount coordinate.
- Zero unintended non-manifold geometry, duplicate surfaces, z-fighting, broken normals or absolute texture paths.
- Diagnostic renders include front, rear, left/right side, top/bottom when useful, three-quarter and required macro views.
- Visual approval compares silhouette, proportion, material response and labeled controls against the cited references.
- Blender 5.2.1 save/reopen, spawn/delete/respawn, LOD export and GLB validation pass before release approval.

## Production handoff
- Next gate: `LOW_DRAFT` → blockout/review unless the current stage is already further advanced.
- Modeling starts from this dossier and the shared contracts; new facts update `registry.json` and regenerate this file.
- Evidence class remains `PROJECT_VERIFIED` until a stronger source explicitly justifies an upgrade.
**Asset-specific constraints**
- No asset-specific exception beyond the contracts below.
- A model is `FINAL` only after geometry, material, runtime and visual gates all pass; a complete dossier is preparation, not release approval.
