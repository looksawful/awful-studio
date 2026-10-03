# iPhone 17 topology review

Date: 2026-10-03  
Scope: current v30 authoring mesh and exported compat GLB.  
Question: why the model looks acceptable shaded but the wireframe/topology looks poor, and what topology strategy should replace it.

## Primary references

- Blender Manual, Retopology / Remeshing:
  https://docs.blender.org/manual/en/4.5/modeling/meshes/retopology.html
- Blender Manual, Boolean Modifier:
  https://docs.blender.org/manual/en/4.5/modeling/modifiers/generate/booleans.html
- Blender Manual, Bevel Modifier:
  https://docs.blender.org/manual/en/latest/modeling/modifiers/generate/bevel.html
- Blender Manual, Weighted Normal Modifier:
  https://docs.blender.org/manual/en/latest/modeling/modifiers/normals/weighted_normal.html
- Blender Manual, Triangulate Modifier:
  https://docs.blender.org/manual/en/4.5/modeling/modifiers/generate/triangulate.html
- Khronos glTF 2.0 specification, mesh primitives:
  https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html

## Current mesh audit

The current Blender source is mostly quad-dominant on side walls, but many flat caps are very large n-gons. That looks tolerable in Blender shading because bevels and weighted normals hide the structural ugliness. It becomes visibly poor in runtime wireframe because glTF represents render geometry as triangle primitives.

### Authoring mesh

| Object | Verts | Faces | Quads | N-gons | Largest n-gon |
|---|---:|---:|---:|---:|---:|
| BODY_ALUMINUM | 4056 | 2830 | 2765 | 65 | 244 |
| CAMERA_HOUSING | 5272 | 4758 | 4756 | 2 | 516 |
| CAMERA_HOUSING_SEAT | 5272 | 4758 | 4756 | 2 | 516 |
| CAMERA_1_RING | 1920 | 1730 | 1728 | 2 | 192 |
| CAMERA_1_BEVEL | 1536 | 1346 | 1344 | 2 | 192 |
| CAMERA_1_GLASS | 1536 | 1346 | 1344 | 2 | 192 |
| ACTION_BUTTON | 168 | 86 | 84 | 2 | 84 |
| VOL_UP | 168 | 86 | 84 | 2 | 84 |
| SIDE_BUTTON | 168 | 86 | 84 | 2 | 84 |
| BOTTOM_SCREW_L | 96 | 50 | 48 | 2 | 48 |

The body is the main boolean victim. Repeated button / port / acoustic / screw cuts leave 65 n-gons, including very large planar faces.

The camera assembly has a different problem: extreme circular/profile segmentation. 192 segments are used for several camera cylinders and 128 outline segments are used for the camera housing. Bevel application multiplies this density.

### Runtime GLB

The exporter triangulates render geometry. Current triangle counts include:

| Object | Runtime triangles |
|---|---:|
| BODY_ALUMINUM | 8108 |
| CAMERA_HOUSING | 10540 |
| CAMERA_HOUSING_SEAT | 10540 |
| CAMERA_1_RING | 3836 |
| CAMERA_1_BEVEL | 3068 |
| CAMERA_1_GLASS | 3068 |
| ACTION_BUTTON | 332 |
| VOL_UP | 332 |
| SIDE_BUTTON | 332 |
| BOTTOM_SCREW_L | 188 |

This explains the visual complaint: a 516-sided planar camera-housing cap becomes a conspicuous triangle field in wireframe even though it shades as a flat surface.

## Review findings

### Required: separate authoring topology from runtime triangulation

The current generator implicitly treats "renders correctly" as sufficient topology quality. That is acceptable for a disposable generated render mesh, but not for a reusable production asset expected to survive wireframe inspection, manual editing, material work, or future topology-dependent operations.

The target should be:

1. **clean authoring mesh**
   - readable edge flow
   - predictable loops around silhouette / bevel / openings
   - controlled poles
   - no huge planar n-gon caps on hero parts
   - topology density proportional to curvature

2. **runtime mesh**
   - derived from the authoring mesh
   - triangulated only at export
   - Meshopt / delivery optimization remains downstream
   - exact dimensions and silhouette remain locked by tests

glTF itself is triangle-oriented, so an exported web mesh will always end up triangulated. The goal is not to eliminate triangles from runtime; the goal is to make the triangulation derive from sane topology instead of giant n-gons and over-segmented primitives.

### Required: rebuild the hero hard-surface primitives instead of auto-remeshing the whole phone

Do **not** run Voxel Remesh / Quadriflow over the complete model as the final solution.

Blender's own documentation positions remeshing as useful for sculpting cleanup or generating topology for subdivision/multires workflows, and explicitly notes the trade-offs. A precision industrial asset with authoritative Apple dimensions should not surrender its exact profile to a global remesher.

Recommended approach is deterministic hard-surface retopology / regeneration from the same dimensional datums.

### Required: camera assembly first

Camera topology is the worst density offender.

Recommended:
- camera rings: reduce radial segments from 192 to roughly 64–96 after silhouette-error testing;
- glass / bevel rings: same shared radial count so loops correspond cleanly;
- camera housing: build as a low-count closed 2D perimeter with deliberate corner arcs, then extrude / bevel;
- replace 516-gon caps with a structured planar fill;
- avoid stacking separately over-segmented cylinders when a shared radial topology can be reused.

Because the phone is static, every surface does not need subdivision-friendly animation topology. It does need consistent, editable, visually readable topology.

### Required: body should use designed topology around openings

Current body topology is a boolean accumulation surface.

Better:
- generate the Apple perimeter as a clean loop;
- create front / rear perimeter loops;
- bridge them into the rail;
- establish support/bevel loops once;
- add localized topology patches only around:
  - Action / Volume / Side button recesses
  - Camera Control
  - USB-C
  - bottom acoustic ports
  - screws
- keep large flat regions deliberately sparse.

Boolean can remain a construction tool, but its raw result should not be the final authoring topology. Blender's Exact Boolean is appropriate for robust construction; it does not guarantee good downstream edge flow.

### Required: buttons and small controls

Current buttons have 84-sided planar cap n-gons. Replace them with rounded-rectangle grids where:
- corner segments are only as dense as needed for silhouette;
- straight runs remain one or a few quads;
- front caps use a small structured grid, not one 84-gon.

### Consider: keep Weighted Normals / Bevel, but stop using them as topology camouflage

Blender documents Weighted Normal as a shading technique for keeping broad faces visually flat. It is useful here and can remain. Bevel Harden Normals can also preserve surrounding flats.

But neither should be used to justify arbitrary n-gon topology on hero components.

## Proposed topology target

Not an "all quads at any cost" target.

A good v30 authoring mesh should be:
- mostly quads on curved / beveled surfaces;
- deliberate tris allowed on small planar transition regions;
- small controlled n-gons acceptable only on fully planar, non-deforming, non-wireframe-critical surfaces;
- no 100–500 vertex n-gon hero caps;
- no 192-segment circles unless silhouette testing proves they are necessary;
- uniform radial segment counts across related camera components;
- sparse flat regions;
- dense geometry only where curvature or silhouette requires it.

## Suggested implementation order

1. Camera assembly topology prototype
2. Compare silhouette / shading / dimensions against current approved model
3. Body perimeter + rail clean mesh
4. Localized bottom and side-control topology
5. Screen / back-glass / button cap cleanup
6. Export-time triangulation
7. Re-run dimensional contracts, Blender geometry checks, Khronos, Storybook and visual gate

## Key constraint

Do not change the already-approved visible model while cleaning topology.

The clean mesh should be validated against the current approved surface:
- dimensional drawing datums
- object bounds
- camera protrusions
- silhouette deviation
- render comparison

Topology cleanup is successful only if the visible product stays the same while the wireframe becomes substantially simpler and more legible.
