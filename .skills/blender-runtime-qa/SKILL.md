---
name: blender-runtime-qa
description: Canonical Blender 5.2 runtime testing method for AWFUL STUDIO. Use whenever correctness depends on bpy, Extension installation, scene state or Blender process lifecycle.
status: installed
---

# Blender Runtime QA

AWFUL uses two test layers.

## Layer A: fast/static

Use for pure Python rules, manifests, path/checksum/release policy, parsing and source invariants. Fast tests are necessary but never sufficient proof of `bpy` behavior.

## Layer B: real Blender 5.2

Use headless Blender 5.2.1 with isolated user config/scripts/data/extensions where lifecycle matters. Prefer factory startup for initial install/build phases and reopen in a new process for restart evidence.

Runtime contracts should assert observable behavior rather than internal implementation names.

Core fixtures:

- ordinary factory scene;
- built AWFUL scene;
- unmanaged user object/material/collection/world/camera;
- multi-scene/shared data fixture;
- historical 0.0.15 scene;
- final built Extension ZIP.

Core phases:

1. validate/build ZIP;
2. install exact ZIP;
3. enable/disable/re-enable;
4. explicit offline Build/Rebuild/Remove;
5. ownership/multi-scene preservation;
6. save/reopen in another Blender process;
7. historical migration/save/reopen;
8. future-schema refusal;
9. optional asset/network contract as applicable.

Use `--offline-mode` for ordinary foundation runtime tests. Network-specific tests explicitly opt in and remain separate.

## Evidence

Each run records Blender version/platform, phase, checks, timings/counts where relevant, traceback on failure and package SHA when installed from ZIP. Preserve the first failed phase log rather than masking it with a later artifact error.

A live Blender bridge is a debugging aid, not a substitute for this reproducible harness.