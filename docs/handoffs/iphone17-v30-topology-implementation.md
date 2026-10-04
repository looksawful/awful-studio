# iPhone 17 v30 topology rebuild — implementation handoff

Date: 2026-10-04
Repository: looksawful/awful-studio
Branch: `agent/118-topology-rebuild-v2`
Shared ledger: GitHub issue #118
PR #119 remains DRAFT/HOLD. Do not merge it.

## Goal

Finish production topology for the entire canonical iPhone 17 v30, not only the camera. Preserve Apple datums, materials, finishes, names, roles, anchors and v30 identity while replacing dense, n-gon-heavy or brittle source/runtime meshes with intentional low-poly hard-surface topology.

## Frozen principles

- Geometry owns silhouette, openings/cavities, physical depth transitions, contact edges and profile-visible forms.
- Tangent normal / roughness owns shallow microdetail only.
- No global remesh and no generic topology framework.
- Exported GLB is the shipping seam.
- Changed runtime-visible hard-surface meshes must have intentional triangles/quads, zero n-gons and zero non-manifold edges.
- Triangle reduction is secondary to shape/shading correctness.
- Camera Human Gate is already PASS and remains frozen.

## Camera — frozen PASS

- 8 visible camera meshes: 1,288 tris total.
- 40-class visible silhouette.
- Housing/seat horizontal quad-strip caps.
- 0 n-gons / 0 non-manifold.
- Frozen silhouette error: 0.038348 mm.
- Deterministic 512 bake maps, 24 px margin.
- Housing/ring/bevel normals retained; glass normal omitted.
- Camera Human Gate remains PASS and is not reopened by later body work.

## Completed whole-model topology slices

Relevant commits on the rebuild line:

- `337e79e` — clean low-poly side-control bake.
- `532d393` — bottom hardware topology.
- `346f127` — back glass and front hardware topology.
- `4bb11b8` — rear optics topology.
- `2dd3903` — side-control bake/topology contract.
- `48fa798` — authored v30 body topology.
- `a88b70d` — body-cell angle normalization / contour preservation.
- `a474117` — rebuilt canonical v30 delivery artifacts.

### BODY_ALUMINUM

Current runtime body on the verified generated blend:

- 2,832 vertices.
- 2,822 faces.
- 5,644 triangles.
- 0 n-gons.
- 0 non-manifold edges.
- 0 zero-length edges.
- 0 tiny/degenerate faces.
- 1 UV layer.
- no runtime bevel or weighted-normal modifier.

The old authored body baseline was 7,308 source triangles; current body is ~22.77% lower. The old evaluated body was ~20,620 triangles; current authored runtime body is ~72.63% lower.

Apple Detail A uses 28 samples per quarter in the current builder. A Wolfram numerical check of the canonical quintic corner Bezier gives a maximum polyline deviation of about 0.01060 mm at 28 segments/quarter. For comparison, 24 segments/quarter is ~0.01436 mm and 16 segments/quarter is ~0.03225 mm.

The body cutout architecture is local manifold cells:
- side controls use capsule cells;
- bottom USB/mic/speaker/screw openings use local cells;
- corner acoustic cells follow the actual Apple bottom curve;
- no global boolean-derived runtime rail topology.

A regression contract now preserves every authored capsule contour direction. This fixed the pointed/diamond-like control recess regression while keeping the mesh manifold.

### Body shading / bake decision

The clean low body retains the existing anodized-aluminum normal and roughness maps on the metal material.

A dedicated high→low macro-normal experiment tested metal-only bake targets at 0.15 / 0.25 / 0.35 mm ray distance. Those maps were effectively flat and produced no meaningful visual improvement. This is expected because the remaining high/low differences are primarily silhouette/contact-edge geometry, which a normal map must not be asked to repair.

Therefore:
- do not commit the rejected experimental body macro-normal maps;
- keep silhouette/contact edge improvements geometric;
- keep the existing subtle anodized micro-normal + roughness material detail;
- camera and side controls remain the places where committed tangent-normal bakes materially carry accepted high→low detail.

Primary-source bake notes are in:
`docs/research/iphone17-body-bake-primary-sources-2026-10-04.md`.

## Current runtime totals

From `assets/device_mockups/iphone_17/runtime/v30/iphone_17_v30.asset.json`:

- runtime triangle count: 11,538.
- old pre-rebuild runtime baseline: 64,554 triangles.
- reduction: ~82.13%.
- compat GLB: 4,748,960 bytes.
- meshopt GLB: 4,224,172 bytes, ~11.05% smaller than compat.
- old compat baseline: 6,192,648 bytes, so current compat is ~23.31% smaller.

## Fresh verification on 2026-10-04

Blender 5.2.1 runtime contracts on the same generated candidate:

- `iphone_v30_body_topology_contract.py` — GREEN.
- `iphone_v30_body_visible_material_contract.py` — GREEN.
- `iphone_v30_body_cell_shape_contract.py` — GREEN.
- `iphone_v30_topology_contract.py` — GREEN.
- `iphone_v30_screen_topology_contract.py` — GREEN.
- `iphone_v30_controls_topology_contract.py` — GREEN.
- `iphone_v30_bottom_topology_contract.py` — GREEN.
- `iphone_v30_surface_topology_contract.py` — GREEN.
- `iphone_v30_rear_optics_topology_contract.py` — GREEN.

Fast suite:
- 208 / 208 PASS.

Khronos glTF Validator `2.0.0-dev.3.10`:
- compat: 0 errors / 0 warnings / 49 infos / 0 hints.
- meshopt: 0 errors / 0 warnings / 50 infos / 0 hints.
- retained evidence hashes were refreshed to the current GLBs.

## Review evidence

Current generated previews are the canonical review surfaces:
`assets/device_mockups/iphone_17/previews/low_v30/`

The side-control recess regression that appeared as pointed/diamond-like openings is fixed in the latest generated source and guarded by `tests/runtime/iphone_v30_body_cell_shape_contract.py`.

Do not use the untracked `assets/device_mockups/iphone_17/prototypes/` directory as source of truth. It contains iterative diagnostics, including rejected body-bake experiments. Source modules, runtime contracts, generated delivery artifacts and issue #118 are authoritative.

## Next work

### Resume verification on 2026-10-04

The requested rebuild had already reached `ad0d8b2` before this continuation.
This session retained the exact delivery rather than regenerating unchanged binaries.
Fresh checks: Blender 5.2.1 (9e2066aef7ef), nine topology/material contracts
plus `iphone_v30_geometry_contract.py` PASS; full fast suite 209/209 PASS;
compat and meshopt Khronos 2.0.0-dev.3.10 both 0 errors/0 warnings;
manifest hashes, GLB provenance and structural round-trip checks PASS.
These round-trip checks are structural; they are not a browser visual test.

Added pure fast regression `test_iphone_body_cell_contour.py`, exercising
8/12/16 capsule arc samples. Removing authored hole angle insertion in an
isolated function copy reproduces RED (2.1496046 mm contour loss); current
function is GREEN (about 1.65e-14 m loss). Production geometry is unchanged.

Durable evidence in `assets/device_mockups/iphone_17/evidence/`:
- `topology_resume_verification_2026_10_04.json` (nine contracts).
- `topology_resume_delivery_2026_10_04.json` (exact GLB hashes and Khronos).
- `body_bake_ab_2026_10_04/` (prototype A/B images, rejected map, measured deltas).
- `topology_resume_clay_wire/` (fresh left/right/bottom diagnostic renders).

Bake qualification: existing metal-only prototype renders were remeasured,
not rebaked on the final candidate. Side RMS on 0-255 RGB is 0.1166 left /
0.1848 right; bottom 8.5084 and three-quarter 3.2807. Thus the earlier
"no material visual gain" statement must not be read as zero delta everywhere.
The retained map is mostly flat but has a conspicuous magenta artifact.
No evidence justifies promoting that macro-normal to production. Keep the
accepted micro-normal/roughness and clean geometry. Experimental target
nonmanifold counts do not describe the production body.

Review: focused contour test/evidence diff has no blocking Standards finding;
it tests observable vertex preservation and changes no runtime behavior.
Spec/#118: body remains 2,832 verts / 2,822 faces / 5,644 tris, clean topology,
no runtime modifiers. Latest material side previews show rounded recesses.
The dark bottom material preview and orthographic diagnostic sheets are
insufficient to approve whole-device appearance. Human Gate remains pending.
No fresh browser interaction or five-finish visual gate was executed in this
continuation. Do not claim release/ship approval. PR #119 remains draft/HOLD.

Resume from this Git branch and issue #118. Inspect the whole-device candidate
in material/clay/wire and record the owner's decision; fix any exact reported
defect before final acceptance. ArtifactBridge room instrumentation was
unavailable (`agent_connector_required`); Git/issue remain the handoff source.

Technical implementation is at release-candidate quality. The remaining owner-facing gate is a whole-device Human Gate using render / clay / wire views from the latest generated model.

If that Human Gate passes:
1. record PASS in issue #118 and the owning project/task system;
2. run final review against the rebuild baseline;
3. keep PR #119 on HOLD unless the owner separately authorizes its landing;
4. do not reopen the frozen camera aesthetics unless a real production-equivalence deviation is found.

If the Human Gate finds a defect, fix only the exact affected topology slice and rerun its focused contract plus the full runtime/fast gates.
