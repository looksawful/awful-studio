---
name: blender-performance-profiling
description: Measure-first performance evidence for AWFUL STUDIO build, rebuild, optional heavy features and asset loading.
status: installed
---

# Blender Performance Profiling

Performance regressions are defects, but optimize only after measuring a reproducible regression.

## Baseline

For the same commit/environment record:

- Blender version/platform/device;
- clean Build wall time;
- Rebuild wall time;
- at least five repetitions where practical and median value;
- object/collection/material/mesh/camera/light/world/action/node-group/image counts;
- optional feature activation time/counts when that feature changed.

Do not compare a warm cached run with a cold baseline without labeling it.

## Diagnosis

Use Python timing/cProfile for Python construction hotspots. Use Blender runtime counts and operation markers for `bpy` behavior. Render/GPU performance needs separate evidence only when render behavior actually changed; Python profiling cannot prove GPU/render speed.

## Gate

A change touching base scene construction, asset decoding, compositor/post setup or volumetric/heavy systems should include before/after evidence. If a material slowdown is found, record it in issue #5 before speculative optimization.

Do not increase default memory/VRAM cost or enable persistent/heavy pipelines globally merely to improve a narrow benchmark.