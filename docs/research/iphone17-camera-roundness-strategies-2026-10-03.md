# iPhone 17 camera roundness strategies

Date: 2026-10-03
Scope: research only, no production implementation.

## Question

The 40-segment baked prototype is acceptable but still reads slightly polygonal in macro. What can make the camera/housing look rounder without returning to a massively dense runtime mesh?

## Primary-source findings

### 1. Normal maps and smooth shading cannot fix silhouette

Blender explicitly notes that Shade Smooth changes shading only; the object outline remains faceted.
Source: Blender 5.2 Manual, Shade Smooth:
https://docs.blender.org/manual/ru/5.2/scene_layout/object/editing/shading.html

Three.js likewise states that normal maps change lighting, not actual shape.
Source: MeshStandardMaterial.normalMap:
https://threejs.org/docs/pages/MeshStandardMaterial.html

Therefore the visible outer contour must still have enough geometric samples.

### 2. Curves are useful for authoring, not as a glTF runtime shortcut

Blender curves have their own resolution controls and can generate smooth geometry from a compact Bézier/NURBS control structure.
Source: Blender 5.2 Manual, Curve Geometry:
https://docs.blender.org/manual/ru/5.2/modeling/curves/properties/geometry.html

But Blender's glTF exporter does not preserve curves; curves and other non-mesh data must be converted to meshes before export.
Source: Blender 5.2 glTF exporter:
https://docs.blender.org/manual/ru/latest/addons/scene_gltf2.html

So curves can improve authoring and make topology generation deterministic, but runtime cost is still determined by the tessellated mesh resolution chosen at conversion/export.

### 3. Subdivision can generate smooth delivery geometry from a small control cage

Blender Subdivision Surface can create smooth surfaces from a simple control mesh, with the modifier remaining non-destructive until export/apply.
Source: Blender 5.2 Manual, Subdivision Surface:
https://docs.blender.org/manual/ru/latest/modeling/modifiers/generate/subdivision_surface.html

This can be useful for the camera housing if the control cage is designed around the Apple silhouette and major depth breaks.

However, if modifiers are applied for glTF export, those generated polygons still exist in the delivery mesh. Subdivision improves authoring and surface quality, not runtime geometry cost by magic.

### 4. Displacement is not a replacement for silhouette geometry

Three.js displacementMap moves existing vertices. It cannot create new vertices, so a coarse 16/24-sided outline remains coarse.
Source:
https://threejs.org/docs/pages/MeshStandardMaterial.html

For this asset, displacement is appropriate only for local relief on an already sufficiently tessellated surface, not for making a camera circle round.

### 5. Adaptive density is the strongest production strategy

For a circular/capsule contour, silhouette error is radius-dependent:
error = radius * (1 - cos(pi / n)).

A fixed segment count wastes polygons on small radii and undersamples large ones.

For a target geometric silhouette error near 0.04 mm:
- housing outer radius 12.44 mm -> about 40 segments
- inner housing radius ~9.83 mm -> about 35
- camera ring radius 8.00 mm -> about 32
- ring bevel radius 7.44 mm -> about 31
- camera glass radius 6.81 mm -> about 29

This aligns with the visual prototype result: 40 is useful for the large housing outline while 32 is sufficient for the smaller camera rings.

A hybrid camera assembly using housing/seat at 40 and ring/bevel/glass at 32 is about 1088 triangles in the current prototype construction, versus 1280 triangles for uniform 40 and 1024 for uniform 32.

## Recommended production direction

### Authoring representation

Use Bézier/curve or a small parametric control representation for circular/capsule silhouettes where that improves editability.

Convert/evaluate to mesh for export with an explicit screen-space or geometric silhouette tolerance.

### Runtime mesh

Use adaptive radial density:
- camera housing outer silhouette: 40 baseline
- inner housing: 36 or shared 40 only if topology alignment is useful
- camera outer rings: 32
- bevel/glass circles: 28-32 depending on macro review
- interior optical details that never define silhouette: 16-24 where normal maps can carry the appearance

### Maps

Keep high-poly -> low-poly tangent-space normal baking for:
- bevel roll-off
- small chamfers
- pentalobe and machining detail
- micro curvature

Keep roughness/metallic/AO for optical response.

Do not use displacement as the main roundness mechanism.

## Alternative strategies

1. Uniform 48/64 geometry:
   - simplest
   - still cheap in absolute terms
   - wastes geometry on smaller radii

2. Curve authoring -> adaptive mesh conversion:
   - best editability
   - deterministic smooth source
   - still produces triangles for GLB
   - recommended for production generator if implementation stays simple

3. Subdivision-surface control cage:
   - good for housing surfaces
   - can preserve a very simple editable source
   - exported result still contains generated polygons
   - harder to maintain exact industrial dimensions unless cage/creases are carefully designed

4. Shader/SDF impostor:
   - can render mathematically perfect circles on planar regions
   - poor fit for arbitrary 3D viewing angles, real silhouettes, depth, shadows, and glTF portability
   - not recommended for this iPhone asset

## Conclusion

The best next prototype is not "more polygons everywhere".

Use:
- 40 segments only where the large housing silhouette needs them;
- ~32 on camera rings;
- fewer segments on smaller/internal circles;
- high-poly normal bake for bevel/detail;
- optionally curves as the authoring source, converted to the adaptive mesh at build/export time.

This gives a rounder macro silhouette with roughly the same ~1k-triangle camera budget instead of returning to tens of thousands of triangles.

## Game Development Studio note

The requested Game Development Studio asset-production workflow was consulted. Its local `game-dev` CLI is not currently installed/available on Titan, so capability/doctor checks could not run. No provider generation or paid operation was needed for this research.
