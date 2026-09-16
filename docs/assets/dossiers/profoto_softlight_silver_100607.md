
    # Profoto Softlight Reflector Silver 100607 — asset dossier

    ## Identity and production role
    - Asset ID: `profoto_softlight_silver_100607`
    - Category: `LIGHT_MODIFIER`
    - Identity class: `HISTORICAL_CONFIRMED`
    - Current stage: `SPEC_READY`
    - Quality tier: `HERO`
    - Variants: `silver`
    - `production_ready=true` means this dossier is complete enough to enter the next modeling gate; it does not mean the 3D asset is released.

    ## Dimensional contract
    - **front_diameter_mm**: `525`; confidence `VERIFIED`.
- **depth_mm**: `190`; confidence `SHARED_GEOMETRY_VERIFIED`.
- **mass_kg**: `1.25`; confidence `VERIFIED`.
    - Blender scale is metric: `1 Blender unit = 1 metre`.
    - `DESIGN_STANDARD` dimensions are frozen representative production targets, not historical manufacturer claims.

    ## Reference and provenance
    - `sensetique_current` [HISTORICAL_INVENTORY]: https://www.looksawful.ru/work/sensetique/ — Confirms Sensetique equipment families; manufacturer data controls technical geometry.
- `profoto_softlight_silver` [MANUFACTURER_PRODUCT_PAGE]: https://www.profoto.com/de/de/shop/products/light-shaping-tools/beauty-dishes/softlight-reflector-silver/ — Softlight Silver 100607 product data.
    - Identity claims must not be upgraded beyond the evidence class without a new primary source.

    ## Component decomposition
    - `shallow_dish`
- `central_deflector_mount`
- `rubber_collar`
- `front_rim`
    - Hidden construction may be simplified only when it does not affect articulation, silhouette, shadows, mount compatibility or bake results.

    ## Geometry plan
    Build mount interface first, then profile/rod skeleton and fabric or reflector surface; preserve source/modifier separation and open/collapsed states when applicable.
    - Blockout must match every frozen dimensional field before secondary detail begins.
    - MID preserves silhouette, control placement, seams, pivots and mount interfaces; HIGH is source-only detail for baking where useful.

    ## Materials and surface response
    - `painted_outer_metal`: keep a distinct physical surface role; do not collapse unlike materials merely to reduce slots.
- `silver_reflective_inner`: keep a distinct physical surface role; do not collapse unlike materials merely to reduce slots.
- `rubber_collar`: keep a distinct physical surface role; do not collapse unlike materials merely to reduce slots.
- `aluminum_fasteners`: keep a distinct physical surface role; do not collapse unlike materials merely to reduce slots.
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
- `MOUNT_MODIFIER`
- Origins must be deterministic and useful for placement, animation and Auto Fit.

## QA and acceptance gates
- Dimensional validation passes for every frozen measurement and origin/mount coordinate.
- Zero unintended non-manifold geometry, duplicate surfaces, z-fighting, broken normals or absolute texture paths.
- Diagnostic renders include front, rear, left/right side, top/bottom when useful, three-quarter and required macro views.
- Visual approval compares silhouette, proportion, material response and labeled controls against the cited references.
- Blender 5.2.1 save/reopen, spawn/delete/respawn, LOD export and GLB validation pass before release approval.

## Production handoff
- Next gate: `SPEC_READY` → blockout/review unless the current stage is already further advanced.
- Modeling starts from this dossier and the shared contracts; new facts update `registry.json` and regenerate this file.
- Evidence class remains `HISTORICAL_CONFIRMED` until a stronger source explicitly justifies an upgrade.
**Asset-specific constraints**
- No asset-specific exception beyond the contracts below.
- A model is `FINAL` only after geometry, material, runtime and visual gates all pass; a complete dossier is preparation, not release approval.
