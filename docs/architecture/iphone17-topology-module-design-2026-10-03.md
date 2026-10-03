# iPhone 17 topology module design

Date: 2026-10-03  
Status: accepted design direction for prototype  
Scope: v30 authoring topology only. Preserve approved visible geometry, Apple datums, PBR, colorways and runtime delivery.

## Problem

The current iPhone 17 generator mixes several concerns in one large script:

- authoritative Apple dimensions and datums;
- hard-surface geometry construction;
- Boolean cutting;
- bevel and normal handling;
- UV generation and PBR map generation;
- materials;
- preview cameras / studio;
- validation metadata;
- delivery/export orchestration.

The geometry part is especially shallow. Callers directly choose implementation details such as:

- `outline_segments=128`;
- `vertices=192`;
- raw Boolean construction;
- bevel widths / segment counts;
- cap shapes inherited from Blender primitives.

This leaks topology policy into the caller and gives poor locality. Changing topology safely currently means editing many scattered construction calls and re-learning how they interact.

The observed result is a visually acceptable shaded asset with poor authoring topology and ugly runtime wireframe:
- `BODY_ALUMINUM`: 65 n-gons, largest 244 vertices;
- `CAMERA_HOUSING`: 516-gon cap, 10,540 runtime triangles;
- camera rings: 192 radial segments and 3,836 runtime triangles each;
- buttons: 84-gon caps.

## External seam

The external seam remains the existing v30 build/delivery flow.

Callers should not need to know topology policy.

Conceptually:

```python
assembly = build_iphone17_geometry(
    spec=IPHONE17_V30_SPEC,
    materials=materials,
    collections=collections,
)
```

The returned `IPhone17Assembly` exposes only named product parts needed by the rest of the pipeline:

- body;
- back glass;
- display glass/content;
- camera housing and camera stacks;
- side controls;
- bottom I/O;
- front hardware;
- anchors / named objects required by validation and runtime.

It does **not** expose:
- radial segment counts;
- cap-fill strategy;
- support-loop layout;
- Boolean implementation;
- triangulation policy.

Those are implementation details behind the seam.

## Recommended module shape

### 1. `iphone17_geometry_spec.py`

Purpose: authoritative product facts only.

Interface:
- immutable `IPhone17GeometrySpec`;
- one canonical `IPHONE17_V30_SPEC`.

Contains:
- envelope dimensions;
- Apple corner profile;
- cover glass / active display dimensions;
- camera XY / diameters / protrusion datums;
- side-control positions and visible dimensions;
- bottom-port / screw / USB-C datums;
- front hardware keepout;
- regional variant choice when resolved.

Does not contain:
- Blender objects;
- topology density;
- bevel implementation;
- materials;
- preview setup.

This keeps source-of-truth facts separate from construction tactics.

### 2. `iphone17_topology.py`

Purpose: deep module that turns `IPhone17GeometrySpec` into clean Blender authoring geometry.

Public interface:

```python
def build_iphone17_geometry(
    spec: IPhone17GeometrySpec,
    *,
    materials: IPhone17Materials,
    collections: IPhone17Collections,
) -> IPhone17Assembly:
    ...
```

Everything topology-specific is internal.

Internal seams may include:

- `_build_profiled_shell(...)`
- `_build_structured_panel(...)`
- `_build_radial_stack(...)`
- `_build_control(...)`
- `_build_bottom_patch(...)`
- `_build_opening_patch(...)`

These helpers are implementation details, not interfaces for the rest of the repo.

### 3. `generate_low_v30.py`

Becomes orchestration, not topology.

Responsibilities:
1. scene setup;
2. create collections;
3. build material set;
4. call `build_iphone17_geometry(...)`;
5. attach PBR maps / presentation metadata;
6. setup studio + diagnostic cameras;
7. run validation;
8. save source asset.

The script should stop knowing whether a camera ring uses 64, 72 or 96 radial segments.

### 4. export/runtime

Runtime triangulation remains downstream.

Authoring topology is clean and readable.
GLB is allowed to triangulate because glTF delivery is triangle-oriented.

Export does not own product topology decisions.

## Design alternatives considered

### A. Generic topology primitive library

Example interface:

```python
profile_prism(profile, depth, cap_mode, segments, ...)
radial_stack(radius, depth, radial_segments, ...)
patch_boolean(target, opening, patch_policy, ...)
```

Pros:
- reusable across devices;
- compact implementation.

Cons:
- caller still must understand topology policy;
- interface becomes nearly as complex as the implementation;
- segment counts, fill modes and patch strategies leak everywhere;
- shallow module.

Verdict: reject as the main interface.

Some private helpers may look like this internally.

### B. Device-specific deep topology module

Example:

```python
build_iphone17_geometry(spec, materials, collections)
```

Pros:
- small interface;
- Apple geometry and topology decisions stay local;
- one change point for future topology work;
- tests naturally target generated product geometry;
- callers get high leverage.

Cons:
- less directly reusable across devices;
- some internal helpers may later be duplicated.

Verdict: **recommended**.

If a second device later needs exactly the same topology algorithm, extract the proven common helper then. One adapter is not evidence for a general seam.

### C. Data-driven topology compiler

Example:

```python
build_device(recipe_json)
```

where JSON describes profiles, patches, cap strategies, material slots and topology density.

Pros:
- potentially very reusable;
- very declarative.

Cons:
- invents a topology DSL before a second real use case exists;
- large interface hidden inside data;
- harder debugging;
- speculative generality.

Verdict: reject for v30.

## Deep-module assessment

### Current shape

Caller knowledge:
- product dimensions;
- Blender primitive behavior;
- segment counts;
- bevel policy;
- Boolean behavior;
- normal repair;
- UV strategy;
- export consequences.

That is a shallow module arrangement.

### Proposed shape

Caller knowledge:
- product spec;
- materials;
- output assembly.

The topology module absorbs:
- perimeter construction;
- cap fill;
- radial density;
- local opening topology;
- bevel support strategy;
- normal consistency;
- editability constraints.

This is substantially deeper.

## Test seam

The interface is the test surface.

Do not unit-test private helpers or assert implementation-specific edge sequences.

Persistent tests should observe generated artifacts:

### Product contract
- Apple dimensions and datums;
- object naming required by runtime;
- camera protrusion;
- control positions;
- bottom I/O positions.

### Surface contract
- silhouette deviation from approved v30 surface within tolerance;
- object bounds remain within tolerance;
- render/shading comparison does not regress.

### Topology contract
For hero authoring meshes:
- no very-large n-gon caps;
- topology density proportional to curvature;
- bounded vertex/triangle counts;
- no accidental non-manifold geometry;
- related camera rings share radial topology;
- flat regions stay sparse.

Exact thresholds should be set by the camera prototype, not guessed here.

### Runtime contract
- export succeeds;
- Khronos validation remains clean;
- Meshopt delivery remains valid;
- Storybook renders identically at normal viewing distance.

## Prototype question

The first prototype should answer exactly one question:

> What camera-assembly topology gives the cleanest editable wireframe while remaining visually indistinguishable from the approved v30 camera geometry?

Prototype variants:
- 64 radial segments;
- 72 radial segments;
- 96 radial segments.

For each:
- structured cap instead of 192/516-gon hero caps;
- shared radial count across ring / bevel / glass;
- preserve Apple diameters and 1.78 / 3.45 mm protrusion datums;
- render same diagnostic camera;
- measure silhouette deviation;
- report authoring verts/faces and runtime tris.

The prototype decides internal policy. Its segment count does not become part of the public interface.

## Stop conditions for prototype

Reject a candidate if:
- silhouette deviation is visible or exceeds agreed tolerance;
- camera shading worsens;
- dimensions move;
- topology still requires giant caps;
- reduction is cosmetic only.

Prefer the lowest-density candidate that preserves the approved visible result.

## Migration order

1. camera assembly behind new topology module;
2. body / rail;
3. side controls;
4. bottom I/O;
5. back glass / display surfaces;
6. delete superseded geometry paths after review;
7. keep runtime/export seam unchanged.

Do not rewrite all geometry in one change.

## Decision

Adopt **device-specific deep topology module**.

The v30 topology cleanup will deepen the geometry construction around a single device-level seam. Generic reusable primitives may exist privately, but no new public topology framework or DSL will be introduced until a second concrete device proves the seam is real.
