
    # Avenger A2025F C-Stand Reference — asset dossier

    ## Identity and production role
    - Asset ID: `avenger_a2025f_cstand`
    - Category: `LIGHT_SUPPORT`
    - Identity class: `REFERENCE_STANDARD`
    - Current stage: `MID`
    - Quality tier: `HERO`
    - Variants: `canonical`
    - `production_ready=true` means this dossier is complete enough to enter the next modeling gate; it does not mean the 3D asset is released.

    ## Dimensional contract
    - **footprint_mm**: `[941, 911]`; confidence `PROJECT_VERIFIED`.
- **riser_diameters_mm**: `[35, 30, 25]`; confidence `VERIFIED`.
- **leg_diameter_mm**: `25`; confidence `VERIFIED`.
    - Blender scale is metric: `1 Blender unit = 1 metre`.
    - `DESIGN_STANDARD` dimensions are frozen representative production targets, not historical manufacturer claims.

    ## Reference and provenance
    - `avenger_a2025f` [MANUFACTURER_PRODUCT_PAGE]: https://www.manfrotto.com/global-en/c-stand-25-a2025f/ — A2025F fixed-base dimensions and tube standards.
    - Identity claims must not be upgraded beyond the evidence class without a new primary source.

    ## Component decomposition
    - `turtle_base`
- `three_legs`
- `three_risers`
- `collars`
- `baby_pin`
- `hinges`
    - Hidden construction may be simplified only when it does not affect articulation, silhouette, shadows, mount compatibility or bake results.

    ## Geometry plan
    Build floor contact and load path first; telescoping tubes, collars, hinges and pins are separate mechanical parts with physical pivots.
    - Blockout must match every frozen dimensional field before secondary detail begins.
    - MID preserves silhouette, control placement, seams, pivots and mount interfaces; HIGH is source-only detail for baking where useful.

    ## Materials and surface response
    - `chrome_steel`: keep a distinct physical surface role; do not collapse unlike materials merely to reduce slots.
- `cast_aluminum`: keep a distinct physical surface role; do not collapse unlike materials merely to reduce slots.
- `black_polymer`: keep a distinct physical surface role; do not collapse unlike materials merely to reduce slots.
- `rubber`: keep a distinct physical surface role; do not collapse unlike materials merely to reduce slots.
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
    - stand_height
- leg_spread
    **Semantic mounts / origins**
    - `FLOOR_CONTACT`
- `MOUNT_SUPPORT`
    - Origins must be deterministic and useful for placement, animation and Auto Fit.

## QA and acceptance gates
- Dimensional validation passes for every frozen measurement and origin/mount coordinate.
- Zero unintended non-manifold geometry, duplicate surfaces, z-fighting, broken normals or absolute texture paths.
- Diagnostic renders include front, rear, left/right side, top/bottom when useful, three-quarter and required macro views.
- Visual approval compares silhouette, proportion, material response and labeled controls against the cited references.
- Blender 5.2.1 save/reopen, spawn/delete/respawn, LOD export and GLB validation pass before release approval.

## Production handoff
- Next gate: `MID` → blockout/review unless the current stage is already further advanced.
- Modeling starts from this dossier and the shared contracts; new facts update `registry.json` and regenerate this file.
- Evidence class remains `REFERENCE_STANDARD` until a stronger source explicitly justifies an upgrade.
**Asset-specific constraints**
- No asset-specific exception beyond the contracts below.
- A model is `FINAL` only after geometry, material, runtime and visual gates all pass; a complete dossier is preparation, not release approval.
