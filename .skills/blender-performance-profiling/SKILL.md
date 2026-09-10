---
name: blender-performance-profiling
description: Profile AWFUL STUDIO scene-build and render-sensitive work before optimizing and require repeatable before/after evidence.
---

# Blender performance profiling

Profile before optimizing. Record a comparable baseline and changed result under the same representative scene/configuration.

At minimum consider:

- clean base-studio build time;
- object and data-block counts;
- repeated timings, preferably a median/distribution rather than one lucky run;
- memory/VRAM-sensitive optional features where measurable;
- viewport/render setup changes relevant to the task;
- render time/device evidence when GPU/render behavior is affected.

Use Python `cProfile`/`pstats` for Python hotspots and Blender-side timing markers for scene construction. Python profiling alone is not GPU evidence.

Do not make heavy features implicit defaults to simplify a benchmark. Preserve opt-in boundaries and treat a meaningful unexplained regression as a defect.
