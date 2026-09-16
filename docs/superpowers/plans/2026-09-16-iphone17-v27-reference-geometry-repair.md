# iPhone 17 v27 Reference + Geometry Repair Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild the iPhone 17 master asset from verified references, remove display z-fighting, repair the rear camera plateau, and produce a visually reviewable v27 before any website promotion.

**Architecture:** Blender remains the source of truth. PureRef stores engineering and visual references; Photoshop/Painter provide 2D/PBR assets only. GLB is generated from the accepted Blender master and validated separately in Three.js.

**Tech Stack:** Blender 5.2.1 LTS, PureRef 2.1.1, Photoshop 2025, Substance 3D Painter, Python, glTF/GLB, Three.js/Storybook, Playwright.

**Spec:** Apple iPhone 17 Dimensional Drawings 2025-09-09 plus visual references collected under `assets/device_mockups/iphone_17/reference/`.

## Global Constraints
- Do not promote a GLB to looksawful.ru before explicit visual acceptance.
- Official dimensions beat visual estimates; visual estimates must be labeled as such.
- Keep one Blender master; do not maintain divergent web geometry.
- Screen artwork and screen glass must not be coplanar.
- Write a failing regression test before each geometry/validation fix.
- Preserve existing v26 as diagnostic history.

---
### Task 1: Reference board and dimensional ledger
- [ ] Keep the official Apple PDF and five rendered drawing pages in `reference/pure_ref/`.
- [ ] Add official Apple product-bezel/product-view references and clearly label photographic vs engineering sources.
- [ ] Arrange front/back/left/right/top/bottom/camera/screen sections in PureRef and save the `.pur` scene.
- [ ] Create a machine-readable dimensional ledger with source, reference value, model value, delta, confidence, and status.

### Task 2: Display architecture
- [ ] Add RED tests rejecting `SCREEN_UI_DECAL` and coplanar display/glass surfaces.
- [ ] Replace the three-layer display with one image-bearing display surface plus physically separated cover glass.
- [ ] Use a high-resolution neutral/mockup screen source with correct active-area aspect ratio.
- [ ] Verify front, oblique, and grazing-angle renders for z-fighting and shading artifacts.

### Task 3: Rear camera system
- [ ] Add RED tests for camera centers, plateau bounds/edge attachment, flash, mic, and stack ordering.
- [ ] Rebuild the plateau profile from the engineering drawing instead of a generic floating rounded prism.
- [ ] Rebuild lens/ring/glass stack and verify no intersections or occlusion.
- [ ] Compare orthographic back and camera macro against the reference board.

### Task 4: Remaining physical audit
- [ ] Audit body corner profile, cover/back glass seats, Dynamic Island, buttons, Camera Control, USB-C, screws, speaker/mic apertures, logo.
- [ ] Fix the Camera Control validation bug so negative protrusion cannot pass.
- [ ] Fix only proven discrepancies; record unavailable microdimensions as visual/internal estimates.

### Task 5: Materials and delivery QA
- [ ] Stabilize Blender normals/bevels before Painter work.
- [ ] Create/verify PBR materials for aluminum, back glass, camera glass, lenses, and display.
- [ ] Export v27 GLB and run glTF validation/asset audit.
- [ ] Run Storybook/Three.js and Playwright rotational visual QA at multiple angles.
- [ ] Present v27 locally for visual acceptance; only then commit/promote the website GLB.
