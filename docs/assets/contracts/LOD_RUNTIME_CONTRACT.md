# LOD and Runtime Contract

- Shipping format is GLB/glTF 2.0; source of truth remains Blender.
- Runtime hierarchy uses stable asset roots and semantic mounts. Preview cameras, lights, reference boxes and authoring-only helpers never ship.
- LOD0 preserves reviewed MID silhouette and product-defining details. LOD1 targets ≤75% of LOD0 triangles. LOD2 targets ≤35% while retaining silhouette, pivots and mounts.
- Collision is separate simplified geometry. Never use hero meshes as physics meshes by default.
- Meshopt is the preferred geometry-compression path after structural validation. KTX2 is the preferred runtime texture path when texture compression is required.
- Repeated props/supports should support instancing. Exported transforms are normalized and pivots remain meaningful for Three.js/game runtimes.
