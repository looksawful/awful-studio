# iPhone 17 camera low-poly + bake prototype

Question: what is the lowest camera geometry density that preserves the approved v30 appearance when shallow bevel/detail is baked from one high-poly source into tangent-space normal maps?

High-poly source: 192 radial segments, physical bevels.
Low-poly candidates: 16 / 24 / 32 / 40.
Bake: Blender Cycles Selected-to-Active, tangent-space normal, 512x512 PNG per unique part, cage extrusion 0.35 mm, max ray distance 0.55 mm.
Delivery test: GLB with explicit tangents.

Results:
- 16: 272 verts, 512 tris, 0.2390 mm max analytic silhouette error, ~5.16 px macro estimate, 222.2 KiB GLB.
- 24: 400 verts, 768 tris, 0.1064 mm, ~2.30 px, 287.6 KiB GLB.
- 32: 528 verts, 1024 tris, 0.0599 mm, ~1.29 px, 325.1 KiB GLB.
- 40: 656 verts, 1280 tris, 0.0383 mm, ~0.83 px, 334.5 KiB GLB.

All four GLBs: Khronos validator 0 errors / 0 warnings after explicit tangent export.
Baked normal maps are non-flat and preserve high-poly bevel response.

Visual findings from the fixed macro camera:
- 16: clearly faceted; reject.
- 24: faceting still visible; reject for macro use.
- 32: close, but housing silhouette remains slightly readable as polygonal.
- 40: current review candidate; silhouette is substantially calmer while geometry remains tiny.

No displacement is used in the baseline. Normal maps handle shading detail; geometry remains responsible for silhouette and real depth.

This prototype is throwaway. Do not import its code into production. Carry only the validated policy into the specification.
