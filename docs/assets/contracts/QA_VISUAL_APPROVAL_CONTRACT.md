# QA and Visual Approval Contract

Release requires four independent gates: geometry, materials, runtime and visual approval.

Geometry: dimensions, origins, mounts, normals, manifold status, duplicate/z-fighting checks and articulation ranges.
Materials: missing files = 0, absolute paths = 0, correct color spaces, physically distinct surface roles and bounded runtime shaders.
Runtime: spawn/delete/respawn, save/reopen, LOD export, collision export, GLB validation and Blender 5.2.1 packaged runtime checks.
Visual: deterministic front/rear/side/three-quarter views plus top/bottom and macro views when useful. Review silhouette, proportion, labels, surface response and mechanical plausibility against cited references.

A green unit test is not visual approval. An attractive render is not dimensional approval. `FINAL` requires both.
