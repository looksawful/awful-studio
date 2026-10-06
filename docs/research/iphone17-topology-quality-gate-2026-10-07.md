# iPhone 17 v30 topology quality gate research — 2026-10-07

## Question

Why the exact #146 Human Gate wireframe still looks structurally poor after the viewer x-ray bug was fixed, and what quality gate should replace the current topology checks.

## Primary external sources

### Blender glTF export

Blender's official glTF documentation states that quads and n-gons are automatically converted to triangles on export because glTF is organized around GPU-ready primitives:

- https://docs.blender.org/manual/en/5.0/addons/import_export/scene_gltf2.html

Implication: a long diagonal in the GLB can be the export tessellation of a Blender quad. The GLB triangle view is therefore not, by itself, proof that the Blender source was authored as triangles.

### Blender triangulation

The Blender manual documents the Triangulate modifier/tool and its methods. `Beauty` is explicitly intended to arrange new triangles more cleanly than fixed splitting:

- https://docs.blender.org/manual/en/4.5/modeling/modifiers/generate/triangulate.html

Implication: when the delivery needs deterministic triangles, triangulation method is part of the production decision. "No n-gons" alone is not a triangle-quality criterion.

### glTF geometry

The glTF 2.0 specification defines mesh primitives as GPU draw-call data and triangle primitives as consecutive triplets of vertices. It also states that geometry should not contain degenerate triangles:

- https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html#geometry

Implication: runtime correctness is about valid triangle primitives, but the glTF spec does not claim that a valid triangle layout is artistically or topologically well designed.

### meshoptimizer

meshoptimizer's official repository documents that cache/overdraw/fetch optimization can reorder triangle and vertex data without intending to change visual appearance; topology-changing simplification is a separate operation. It also notes that irregular topology and many seams reduce simplification quality:

- https://github.com/zeux/meshoptimizer

Implication: the already-passing compat/Meshopt semantic identity is useful delivery evidence, but it is not a source-topology quality gate.

## Primary repository evidence

### Authored source is not simply "bad because glTF triangulates it"

Read-only Blender 5.2.1 audit of the exact v30 generated blend:

- `BODY_ALUMINUM`: 2,944 vertices, 3,250 faces, 2,618 quads + 632 authored triangles, no n-gons, no non-manifold edges.
- `BACK_GLASS`: 136 vertices, 134 quads, no authored triangles, no n-gons, no non-manifold edges.
- `CAMERA_HOUSING`: 136 vertices, 107 quads + 54 triangles.
- `USB_C_CAVITY`: 108 authored triangles.
- `USB_C_TONGUE`: 188 authored triangles.
- controls such as `CAMERA_CONTROL`: 40 quads + 4 triangles.

Raw audit: `F:\Temp\iphone17-ticket146\authored-topology-audit.json`.

Therefore the Human Gate problem is mixed:
1. some ugly GLB diagonals are exporter tessellation of source quads;
2. some source quads/cells are themselves so stretched that any triangulation is visually poor;
3. several delivery parts are deliberately authored as triangles.

### Back glass directly reproduces the visible giant-diagonal problem

The source `BACK_GLASS` is all quads, but its major Y-facing surface triangulates to:
- 132 triangles;
- minimum angle ~0.071°;
- maximum edge-ratio ~58.97;
- maximum triangle edge ~141.78 mm on a 147.61 mm-tall panel.

This explains why a diagonal can run across nearly the whole rear panel in the exported wireframe. It is not only a viewer artifact.

### BODY_ALUMINUM local-cell strategy is the root of the star/radial pattern

`assets/device_mockups/iphone_17/body_topology_v30.py` constructs controls and bottom apertures using `_matched_annulus_loops`. The function projects rays from a hole/capsule center out to rectangular cell bounds, then `_shell_faces` connects matched inner/outer rings.

That is exactly the topology family visible in the Human Gate around:
- USB-C;
- speaker/mic apertures;
- side controls.

The topology is manifold and deterministic, but it naturally produces long radial cells when the feature is small relative to its rectangular outer cell.

The current body rail contract already records:
- min cap angle ~1.98°;
- max aspect ~23.18;
and accepts them under thresholds of 1° / 25.

Those thresholds prove that the mesh is not degenerate. They do not prove professional topology flow.

### USB triangulation is authored on purpose

`generate_low_v30.py` applies the physical USB bevel and then explicitly triangulates the complete USB cavity/tongue using Blender `BEAUTY` triangulation before saving.

So the USB radial appearance cannot be blamed on an accidental glTF-only triangulation step. It is delivery topology.

### Existing good internal benchmark

The display-frame cap contract is much cleaner:
- minimum triangle angle ~7.39°;
- maximum aspect ~7.77.

This is a useful project-local quality benchmark because it is already produced by the same asset pipeline and accepted without the dramatic radial/needle pattern seen on the body/panels.

## Diagnosis

The whole-device #146 Human Gate should be considered topology-quality REJECT pending owner confirmation.

The problem is not one bug:
- the old viewer x-ray mode exaggerated the mess and is now fixed;
- Blender glTF export necessarily triangulates source quads;
- but the authored geometry also contains extremely stretched visible quads and deliberate radial cell layouts;
- current automated contracts are mostly manifold/count/dimension/preservation contracts and allow triangle-quality values that are much looser than the visual bar the owner expects.

The core gap is therefore **acceptance criteria**, followed by generator topology.

## Proposed test seams

These are the seams to confirm before creating the corrective spec/tickets.

### Seam A — authored visible-surface topology

Test the saved Blender mesh after all production modifiers are materialized, at named visible surface classes rather than indiscriminately across thin thickness walls.

Candidate criteria:
- no n-gons or non-manifold geometry;
- no degenerate/zero-length elements;
- major visible planar/cap regions should target min triangle angle >= 5° and aspect <= 10;
- deliberate bevel/thickness strips are exempt from that shape threshold when their physical-surface-error contract passes;
- no major-panel triangulation edge may span nearly the full panel merely to resolve one quad/cell.

The 5° / 10 limits are a proposed project quality bar, not a Blender/glTF standard. They are deliberately close to the already-good display-frame result (~7.39° / ~7.77) and substantially stricter than the current body allowance (1° / 25).

### Seam B — exported exact-candidate triangle quality

Check the exact compat GLB that the Human Gate loads:
- the same named visible regions must satisfy the approved shape criteria;
- exported triangles must preserve source surface/silhouette within existing error bounds;
- Meshopt may reorder data, but compat/Meshopt visible topology and bounds must remain semantically equivalent.

### Seam C — matched visual topology review

Use the existing Storybook only:
- render;
- clay;
- hidden-line actual GLB triangle wireframe;
- matched cameras for whole device, bottom, side controls, rear panel/cameras;
- exact candidate SHA shown in the review surface.

Static contact sheets remain supporting evidence only.

### Seam D — preservation

Any topology repair must keep:
- Apple dimensional-drawing constraints;
- silhouette/bounds;
- material identities and finish behavior;
- UV/bake provenance;
- normals/tangents within existing runtime tolerances;
- 51 exported node identity;
- frozen appearance reference separate and unchanged.

## Recommended workflow

AskMatt route for this finding:

`diagnosing-bugs -> to-spec -> to-tickets -> per-ticket implement/TDD -> code-review -> Human Gate`.

The diagnosis phase is now largely complete because the source/output distinction and the radial-cell generator cause have been reproduced. The next required decision is to approve the test seams above, especially the visible-surface shape limits, before TDD tests are written.

## omgskills discovery

Relevant public catalog records were found:
- `sixtysevenlf/dsh-skill-blender-modeling`
- `omer-metin/skills-for-antigravity:3d-modeling`
- `freshtechbro/claudedesignskills:blender-web-pipeline`
- `sfkislev/flue:blender`

All surfaced as `discovery_only`, not pinned reproducible installs. Per omgskills policy they were **not installed from mutable GitHub branches**. The existing repository/Blender pipeline plus official primary sources are sufficient for this diagnosis.
