# iPhone 17 front-layer depth conflict — 2026-10-02

## Question

Why do the new physical front sensor/camera masks produce shading/depth conflicts when light or view angle changes, and what is the smallest source-level fix?

## Current source facts

- `SCREEN_CONTENT` is a 0.325 mm-thick prism centered at `front_y + 0.010 mm`; its outward face is therefore about 3.9525 mm from model center.
  Source: `assets/device_mockups/iphone_17/generate_low_v30.py`, screen-content construction.
- `FRONT_SENSOR_MASK` and `FRONT_CAMERA_MASK` are only 0.008 mm thick and centered at `front_surface + 0.012 mm`. Their back face is only about **0.0065 mm (6.5 µm)** away from the outward screen face.
  Source: `assets/device_mockups/iphone_17/generate_low_v30.py`, `front_hardware_y` and mask construction.
- `FRONT_CAMERA_GLASS` is likewise only roughly 0.01 mm away from the screen surface.
  Source: same generator, `front_optics_y`.
- The current exported web GLB intentionally omits `SCREEN_GLASS`.
  Source: `assets/device_mockups/iphone_17/export_runtime_v30.py`: exported objects exclude `obj.name == "SCREEN_GLASS"`.
- In the Blender source, the active center of `SCREEN_GLASS` is boolean-cut by `SCREEN_ACTIVE_CUTTER`, so the active display is not covered by a full glass surface there either.
  Source: `generate_low_v30.py`, `CUT_ACTIVE_AREA`.
- `MAT_UNDER_GLASS_BLACK` already exports with near-black base color and `KHR_materials_specular.specularFactor = 0`; material gloss is therefore not the primary remaining cause.
  Source: current `iphone_17_v30_web.glb`.

## Renderer facts

Three.js materials default to depth testing and depth writing. Three.js exposes `polygonOffset` specifically to offset fragment depth before the depth test, including decal-like cases, but this is a renderer workaround rather than a geometry fix.

Primary source:
- Three.js Material docs: https://threejs.org/docs/pages/Material.html

Khronos documents that coplanar or very-near-coplanar primitives can produce stitching/bleeding/Z-fighting because finite depth-buffer precision maps nearby surfaces to the same or adjacent depth values. Precision gets worse as the far/near ratio grows.

Primary sources:
- Khronos Depth Buffer Precision: https://wikis.khronos.org/opengl/Depth_Buffer_Precision
- Khronos Basics of Polygon Offset: https://wikis.khronos.org/opengl/Basics_Of_Polygon_Offset

The current viewer starts with `near=0.001, far=1000`; after perspective fit it uses `near=max(distance/1000, 0.001)` and `far=distance*100`.
Source: `preview/src/model-viewer.mjs`.

For an iPhone-sized object (~149.61 mm tall), the current fit formula places the camera at roughly 0.344 m. That gives approximately `near=0.001`, `far=34.4`. Assuming a common 24-bit depth buffer, the depth quantization near the phone is on the order of **0.007 mm**, essentially the same scale as the current **0.0065 mm** screen-to-mask gap. At grazing view angles the projected separation shrinks further. This makes depth conflict plausible and expected, not mysterious.

The orthographic camera keeps its initial `0.001 .. 1000` clip range, so its linear depth resolution is even less friendly to micrometer-separated layers.

Three.js also warns that intersecting/overlapping transparent geometry has unavoidable sorting trade-offs. Reintroducing a full transparent cover-glass mesh would therefore create a second artifact class rather than solve this one.

Primary source:
- Three.js transparency manual: https://threejs.org/manual/pages/transparency.html

## Diagnosis

**Leading root cause:** the physical front masks/camera were added as separate meshes almost on top of the emissive screen surface. The remaining defect is a layer/topology problem, not a roughness problem.

The current representation asks the depth buffer to distinguish surfaces separated by only a few microns while the viewer uses a broad clip range. Light/view changes expose the ambiguity as stitching, edge halos, or apparent shading overlap.

## Minimal source-level fix

Prefer removing the overlap rather than compensating for it in Three.js:

1. Keep the orange privacy dot as screen-state raster artwork.
2. Keep the two black hardware regions and camera optic as physical objects.
3. **Cut matching openings out of `SCREEN_CONTENT`** using the existing boolean-difference helper.
4. Place the black masks and camera optic slightly behind the screen front plane, visible through those openings.
5. Rebuild UVs/material face ownership after the booleans using the generator's existing planar UV logic.

This produces mutually exclusive projected surfaces: screen pixels exist around the hardware, not underneath it. The depth buffer no longer has to arbitrate nearly coincident screen/mask fragments.

## Explicit non-solutions for the first pass

- Do **not** tune roughness again; the black-mask specular factor is already zero.
- Do **not** add `polygonOffset`, `renderOrder`, or disable `depthWrite` first. Those are renderer-specific symptom treatments.
- Do **not** reintroduce a transparent full-screen cover-glass mesh in the web GLB; Three.js transparent sorting introduces another failure mode.
- Do **not** change Camera Control; the reported regression is isolated to the front sensor/camera stack.
- Do **not** globally retune viewer near/far until source geometry is non-overlapping. Clip-plane tightening is a useful second-line hardening step only if a residual depth issue remains.

## Verification seam

The durable regression should inspect the exported GLB, not Blender internals:

- sample the front `SCREEN_CONTENT` triangles at the known sensor-mask and camera-mask footprints;
- assert there is **no screen front-face coverage** at those coordinates;
- assert `FRONT_SENSOR_MASK`, `FRONT_CAMERA_MASK`, and `FRONT_CAMERA_GLASS` still exist and remain behind the screen front datum;
- assert the orange privacy pixel remains in the screen-state raster.

Then repeat the exact grazing-angle visual gate in Blender and Three.js.
