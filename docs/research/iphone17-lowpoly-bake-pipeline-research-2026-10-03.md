# iPhone 17 low-poly + bake pipeline research

Date: 2026-10-03  
Scope: research only; no production implementation.  
Question: how far can iPhone 17 camera/body detail move from geometry into normal/roughness/height maps while keeping a lightweight, realistic, interoperable glTF asset?

## Executive finding

The production direction should change from "clean dense topology" to **silhouette-first low poly + baked surface detail**.

Use geometry for:
- outer silhouette;
- large depth changes and physical layer separation;
- openings / cavities that remain visible in profile;
- contact geometry that must cast or receive real shadows.

Use tangent-space normal maps for:
- shallow bevel appearance;
- pentalobe recesses;
- fine grooves / machining detail;
- small chamfers that do not alter silhouette;
- micro-surface shape.

Use roughness / metallic / AO maps for optical response, not extra polygons.

Do **not** make runtime displacement the foundation of the web asset.

Core glTF 2.0 has tangent-space normal textures, metallic-roughness textures and occlusion textures, but no core displacement-map field. [Khronos glTF 2.0 Specification](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html)

Three.js has a `displacementMap` on `MeshStandardMaterial`, but it moves existing vertices; it does not add tessellation. A coarse circular silhouette therefore remains coarse unless enough vertices already exist. [Three.js MeshStandardMaterial](https://threejs.org/docs/pages/MeshStandardMaterial.html)

Blender likewise distinguishes bump, which changes shading only, from true displacement, which changes the surface and requires finely subdivided geometry. [Blender 5.2 Displacement](https://docs.blender.org/manual/en/latest/render/materials/components/displacement.html)

## What the current delivery stack supports

The repo currently uses Three.js `^0.185.1` and `GLTFLoader` with Meshopt support:
- `preview/package.json`
- `preview/src/model-viewer.mjs`

The installed Three.js loader explicitly supports:
- glTF normal textures;
- `KHR_texture_basisu`;
- experimental `EXT_materials_bump`;
- Meshopt compression.

The current iPhone generator already creates normal + roughness material maps, so the next prototype can extend an existing path rather than inventing a new renderer.

## Normal-map requirements

glTF normal textures are tangent-space maps. The glTF convention is +X right, +Y up, +Z toward the viewer. [Khronos glTF 2.0 Specification](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html)

Blender's glTF exporter expects:
- Image Texture set to Non-Color;
- Normal Map node in Tangent Space;
- matching UVs;
- tangent-space bake using +X / +Y / +Z.

Blender explicitly documents Cycles tangent-space normal baking for glTF. [Blender glTF exporter manual](https://docs.blender.org/manual/en/4.5/addons/import_export/scene_gltf2.html)

If a glTF primitive has a normal texture but no explicit tangents, the glTF spec says clients should calculate tangents using MikkTSpace from positions, normals and the normal texture's UVs. For deterministic Blender/Three parity, exporting stable UVs and validating tangents remains preferable. [Khronos glTF Specification, primitive data](https://github.com/KhronosGroup/glTF/blob/main/specification/2.0/Specification.adoc)

## High-poly to low-poly bake

Blender Cycles supports **Selected to Active** baking from high-poly source geometry to the active low-poly mesh.

The bake can use:
- ray extrusion / max ray distance;
- an explicit cage object for tighter projection control.

This is directly appropriate for camera rings, glass bevels, button chamfers and screw recess detail. [Blender Render Baking](https://docs.blender.org/manual/en/latest/render/cycles/baking.html)

Project implication: high-poly becomes a **bake source**, not the delivery mesh.

The delivery mesh should not inherit high-poly radial segment counts merely because the source used them to make smooth normals.

## Bump and displacement

Three.js 0.185.x supports `EXT_materials_bump` in GLTFLoader, but this extension is not part of the ratified Khronos extension list as of this research. The current Khronos registry lists ratified extensions such as `KHR_texture_basisu`, `KHR_materials_variants` and `EXT_meshopt_compression`, but not `EXT_materials_bump`. [Khronos extension registry](https://github.com/KhronosGroup/glTF/blob/main/extensions/README.md)

Therefore:
- normal map is the portable default;
- experimental bump may be tested later as an optional viewer-specific enhancement;
- it should not become a required production dependency.

A generic displacement proposal has existed in Khronos discussion for years, but displacement is still not a core glTF material feature. [Khronos displacement proposal issue](https://github.com/KhronosGroup/glTF/issues/948)

## What maps cannot replace

Normal maps alter lighting, not mesh position. Three.js states this explicitly. [Three.js MeshStandardMaterial](https://threejs.org/docs/pages/MeshStandardMaterial.html)

So maps cannot replace:
- the circular camera-ring silhouette;
- the camera plateau outer outline;
- actual 1.78 mm / 3.45 mm depth layers;
- USB-C cavity silhouette;
- button projections visible from side views.

They **can** replace most detail inside those silhouettes.

## Camera-specific geometry policy

### Keep as geometry
- camera housing outer capsule silhouette;
- camera ring outer circumference;
- major ring / glass layer depths;
- camera glass plane;
- physically visible gaps between stacked parts.

### Bake to normal
- fine ring chamfers beyond the primary silhouette bevel;
- tiny edge roll-off;
- subtle lens-seat curvature;
- pentalobe screw recess;
- machining / stamped micro-detail;
- shallow groove detail.

### Put in roughness
- anodized aluminum microvariation;
- glass finish variation;
- ring polish differences;
- screw finish.

### AO
Use only restrained cavity AO for static recesses. Do not bake directional lighting into exposed product surfaces.

## Segment-count research target

A normal map cannot repair polygonal silhouette error, so the prototype should choose radial count by measurable silhouette tolerance, not by a generic "all curves need N segments" rule.

For an n-sided approximation to a circular arc, maximum chord sagitta is:

`error = radius * (1 - cos(pi / n))`

Project calculations for the largest camera-related radii:

| radial segments | 8 mm camera ring error | 12.44 mm housing-end error |
|---:|---:|---:|
| 16 | 0.154 mm | 0.239 mm |
| 24 | 0.068 mm | 0.106 mm |
| 32 | 0.039 mm | 0.060 mm |
| 40 | 0.025 mm | 0.038 mm |
| 48 | 0.017 mm | 0.027 mm |
| 64 | 0.010 mm | 0.015 mm |

These are geometric calculations, not visual acceptance thresholds.

Interpretation:
- 16 is useful as a deliberate low-quality control;
- 24 may be adequate at ordinary viewing distance but is likely risky for macro;
- 32 and 40 are the serious candidates;
- 48 should be a rescue candidate only if 40 visibly fails;
- 64 should no longer be the default.

The correct final count should be selected in screen space at the **closest supported product-viewer macro**, not from millimetres alone.

## Flat caps and wireframe

The previous prototype proved another point: replacing n-gons with dense quad grids solves the wrong problem.

For static product geometry, a flat cap does not need a chessboard of quads.

The new prototype should prefer:
- sparse, deliberate planar triangulation;
- a small center fan where appropriate;
- localized loops only where geometry actually changes;
- no dense interior grid whose only purpose is "all quads".

glTF delivery will be triangulated anyway; the goal is a small, understandable triangulation.

## Texture transport

Normal and roughness maps add texture bandwidth, so polygon reduction should not simply trade a few kilobytes of geometry for huge uncompressed maps.

`KHR_texture_basisu` is ratified and allows KTX2 / Basis Universal textures for more efficient transmission and reduced GPU memory footprint. Khronos specifically notes UASTC as the general choice for non-color data such as normal and roughness-metallic textures. [KHR_texture_basisu](https://github.com/KhronosGroup/glTF/blob/main/extensions/2.0/Khronos/KHR_texture_basisu/README.md)

Three.js supports KTX2 / Basis Universal through `KTX2Loader`, and the repo's installed GLTFLoader advertises `KHR_texture_basisu` support. [Three.js KTX2Loader](https://threejs.org/docs/pages/KTX2Loader.html)

Prototype implication:
- bake PNG first for unambiguous source comparison;
- measure 512 and 1024 normal-map variants;
- only after visual choice, test KTX2/UASTC delivery;
- do not add compression while judging bake quality.

## Recommended next prototype

The next prototype should supersede the rejected 64/72/96 dense-topology experiment.

Variants:
1. 16 radial segments, baked normals: negative control.
2. 24 radial segments, baked normals.
3. 32 radial segments, baked normals.
4. 40 radial segments, baked normals.
5. Optional 48 only if 40 fails macro review.

Each variant must use the **same high-poly source** and the same bake settings.

For each variant capture:
- shaded macro;
- wireframe;
- normals debug;
- silhouette overlay against approved v30;
- 3/4 camera view;
- side view showing protrusion;
- geometry vertex / triangle count;
- GLB byte size;
- normal/ORM texture byte size;
- closest-view silhouette error in pixels;
- console / Khronos validation result.

Bake source should retain the already-correct Apple dimensions:
- camera housing XY outline;
- 16.00 mm outer ring diameter;
- 13.62 mm camera glass diameter;
- 1.78 mm plateau protrusion;
- 3.45 mm camera-glass protrusion.

## Prototype acceptance rule

Select the **lowest polygon count** for which all are true:
- no visible faceting at the closest supported viewer distance;
- silhouette overlay remains within the agreed screen-space tolerance;
- baked bevels do not show projection seams;
- normal map survives glTF export and Three.js loading;
- camera remains dimensionally identical to the approved source;
- texture cost does not outweigh the geometry savings.

Do not judge the candidate by "quad cleanliness". Judge:
1. silhouette;
2. shading;
3. dimensional fidelity;
4. runtime cost;
5. editability of the low-poly source.

## Research conclusion

The correct production architecture is:

`high-poly dimensional source -> bake -> sparse low-poly silhouette mesh -> tangent normal + ORM -> glTF/Three.js`

not:

`dense clean quads -> triangulate everything -> ship`

The next stage should therefore be a new throwaway low-poly+bake prototype, not a production retopology pass.

## Primary sources

1. Khronos, glTF 2.0 Specification: https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html
2. Khronos glTF source specification: https://github.com/KhronosGroup/glTF/blob/main/specification/2.0/Specification.adoc
3. Khronos glTF Extension Registry: https://github.com/KhronosGroup/glTF/blob/main/extensions/README.md
4. Khronos KHR_texture_basisu: https://github.com/KhronosGroup/glTF/blob/main/extensions/2.0/Khronos/KHR_texture_basisu/README.md
5. Blender Manual, glTF 2.0 exporter: https://docs.blender.org/manual/en/4.5/addons/import_export/scene_gltf2.html
6. Blender Manual, Render Baking: https://docs.blender.org/manual/en/latest/render/cycles/baking.html
7. Blender Manual, Displacement: https://docs.blender.org/manual/en/latest/render/materials/components/displacement.html
8. Blender Manual, Normal Map node: https://docs.blender.org/manual/en/dev/render/shader_nodes/displacement/normal_map.html
9. Three.js MeshStandardMaterial: https://threejs.org/docs/pages/MeshStandardMaterial.html
10. Three.js GLTFLoader: https://threejs.org/docs/pages/GLTFLoader.html
11. Three.js KTX2Loader: https://threejs.org/docs/pages/KTX2Loader.html

Project-local primary sources:
- `preview/package.json` — Three.js 0.185.1 dependency.
- `preview/src/model-viewer.mjs` — GLTFLoader + Meshopt runtime.
- installed `preview/node_modules/three/examples/jsm/loaders/GLTFLoader.js` — confirms this exact Three.js version recognizes normal textures, KHR_texture_basisu and EXT_materials_bump.
- `assets/device_mockups/iphone_17/generate_low_v30.py` — current PBR-map and geometry construction path.

