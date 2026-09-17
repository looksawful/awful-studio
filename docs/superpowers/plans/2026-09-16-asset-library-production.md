# Asset Library Production Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce every asset in `docs/assets/registry.json` to release-approved Blender and runtime quality without re-researching the production contract.

**Architecture:** `registry.json` and per-asset dossiers define frozen identity, dimensions, materials, mounts and runtime requirements. Blender source remains canonical; GLB/LOD/collision files are derived artifacts. Each production wave is independently reviewable and must pass geometry, material, runtime and visual gates before merge.

**Tech Stack:** Blender 5.2.1 LTS, Python, Cycles/Eevee diagnostics, glTF/GLB 2.0, Meshopt, optional KTX2, Three.js runtime validation.

**Spec:** `docs/assets/README.md`, `docs/assets/contracts/`, and individual `docs/assets/dossiers/*.md`.

## Global Constraints

- 1 Blender unit = 1 metre.
- Do not upgrade identity evidence without a cited source.
- Preserve semantic mounts and deterministic origins.
- Source/modifier/support remain separate layers.
- No absolute texture paths or eager network dependencies.
- `FINAL` requires geometry, material, runtime and visual approval.

---
### Task 1: Current device assets

**Files:** `assets/device_mockups/**`, `extension/awful_studio/assets/devices/**`, `docs/assets/dossiers/{iphone_17,ipad_pro_11_m5,ipad_pro_13_m5,macbook_pro_14_m5}.md`

**Produces:** reviewed Blender source, current diagnostic previews, runtime GLB and evidence for each device.

- [ ] Rebuild each device from the canonical generator with Blender 5.2.1.
- [ ] Validate dimensions, screen/camera/button geometry, origins and named parts against its dossier.
- [ ] Apply the shared Apple material stack and render front/back/side/three-quarter plus macro views.
- [ ] Export runtime GLB/LOD/collision where specified and run structural validation.
- [ ] Commit only after visual approval and package/runtime tests pass.

### Task 2: Studio rig core

**Files:** `assets/studio_equipment/**`, dossiers for D1, Magnum, A2025F and sandbag.

**Produces:** the first fully approved support → fixture → modifier slice.

- [ ] Bring D1 rear panel, vents, yoke, decals and optical parts to final fidelity.
- [ ] Finish Magnum rim/collar/label material zones and reflector profile.
- [ ] Finish C-Stand base, grip mechanics, collars and bends to the reference contract.
- [ ] Finish sandbag seams, soft deformation and webbing without changing its envelope.
- [ ] Complete UV/bake/runtime materials, LOD0/1/2 and collision exports; run Blender 5.2.1 and visual gates.
### Task 3: Remaining fixtures and hard modifiers

**Files:** dossiers for Acute/D4, Acute2, Dedolight, ARRI, Zoom and both Softlight variants.

**Produces:** dimensionally verified hard-lighting family with shared mounting semantics.

- [ ] Build blockout from frozen envelopes and manufacturer component decomposition.
- [ ] Add controls, vents, optical parts, cables and articulation only after blockout validation.
- [ ] Reuse shared Profoto mount semantics without merging distinct product geometry.
- [ ] Author decals/labels as textures or masks instead of unnecessary text geometry.
- [ ] Export LOD/runtime/collision and run deterministic diagnostic renders.

### Task 4: Soft modifiers and umbrellas

**Files:** dossiers for Grifon, RFi, Fotokvant and Lumifor modifiers plus RFi speedring.

**Produces:** reusable rod/rib/fabric system with open/collapsed states.

- [ ] Implement reusable speedring, rod/rib and textile construction primitives.
- [ ] Match every frozen front diameter/rectangle and rod/rib count before fabric shaping.
- [ ] Keep modifier shell and mount adapter independent.
- [ ] Validate diffusion, reflective lining, open/collapsed state and runtime simplification.
- [ ] Release each family only after silhouette and material-transmission review.
### Task 5: Support, grip and studio accessories

**Files:** all `LIGHT_SUPPORT` and `LIGHT_ACCESSORY` dossiers.

**Produces:** reusable support mechanics, mounting pieces, flags, frames, cables and weights.

- [ ] Build shared 16 mm mount and grip primitives first.
- [ ] Build stands from floor contact upward with correct telescoping/pivot mechanics.
- [ ] Use instancing for repeated knobs, fasteners, casters and rib hardware.
- [ ] Keep cables curve-based in authoring and use simplified collision/runtime representations.
- [ ] Validate compatibility against `docs/assets/COMPATIBILITY_MATRIX.md`.

### Task 6: Props and furniture

**Files:** all `PROP` and `FURNITURE` dossiers.

**Produces:** dimensionally consistent studio staging library with believable upholstery and surface variation.

- [ ] Generate hard props parametrically from the frozen dimensions in the registry.
- [ ] Build simple furniture before upholstered hero furniture to validate wood/metal material families.
- [ ] Build sofa/armchairs with frame, cushion contacts, seams, piping and deformation before microfolds.
- [ ] Bake only detail that materially improves runtime silhouette or close-up response.
- [ ] Validate floor contact, scale with a human reference, material response and LOD budgets.
### Task 7: Canon body and lens system

**Files:** `canon_eos_5d_mark_iv.md`, `canon_ef_24_70_f28l_ii.md` and their future Blender/runtime asset folders.

**Produces:** a representative production camera/lens pair with stable EF mount, sensor plane and optical axis.

- [ ] Build camera body from the frozen envelope with separate grip, controls, doors, displays, ports, hotshoe and mount.
- [ ] Build lens concentrically around `OPTICAL_AXIS` and `EF_MOUNT_PLANE` with separate zoom/focus groups.
- [ ] Add engravings/scales as decal/mask assets and preserve zoom-position variants.
- [ ] Validate body/lens attach-detach behavior, screen/controls and optical-glass material stack.
- [ ] Export camera, lens and assembled pair through the same LOD/runtime/visual gates.

### Task 8: Library release integration

**Files:** Extension asset catalog, thumbnails/previews, registry metadata, runtime manifests and release documentation.

**Produces:** one discoverable, lazy-loaded AWFUL STUDIO asset library.

- [ ] Add only release-approved assets to the Extension catalog; base build keeps lightweight metadata/thumbnails.
- [ ] Verify lazy loading, offline behavior, rebuild ownership and user-scene preservation.
- [ ] Run full fast suite and exact Blender 5.2.1 packaged runtime verification.
- [ ] Audit names, dimensions, materials, texture paths, LODs, collision, previews and provenance across the complete registry.
- [ ] Update `docs/assets/registry.json` stages only from captured evidence and merge after CI is green.
