---
name: awful-systematic-debugging
description: Root-cause-first debugging for AWFUL STUDIO Python, Blender runtime, Extension packaging, CI, scene state, data safety and performance failures.
status: installed
---

# AWFUL Systematic Debugging

No fix before root cause evidence.

## 1. Reproduce

Record the exact commit/branch, Blender version/platform, command/operator, scene/fixture, and failure output. Prefer factory startup/isolated profiles for lifecycle defects. Preserve the first failing artifact/log.

Classify the failure before editing:

- pure Python/tooling;
- Blender API/runtime;
- Extension install/registration/lifecycle;
- scene ownership/data mutation;
- migration/schema;
- network/cache/filesystem;
- CI/environment/distribution;
- performance;
- visual/render quality.

## 2. Trace boundaries

For multi-stage paths such as CI → runtime bootstrap → Blender → build ZIP → install → runtime phase, record which stage received what and where the first failure occurs. Do not patch later stages when an earlier stage never completed.

For scene-state defects, snapshot the relevant user and managed data before the operation and identify the first function that mutates it incorrectly.

## 3. Compare working evidence

Find the closest verified working path in this repository or the immutable 0.0.15 baseline. List concrete differences before choosing a hypothesis.

## 4. Form one hypothesis

State one specific root-cause hypothesis and the evidence supporting it. Test the smallest variable possible. If wrong, return to evidence rather than stacking patches.

## 5. Fix via TDD

Use `.skills/awful-tdd/SKILL.md`: create the smallest failing reproduction, verify RED, implement the source-level cause, verify GREEN and run broader regression coverage.

After three failed fix hypotheses, stop patching and question the architecture. Record that in the owning issue.

## Blender-specific evidence

Capture when relevant:

- `bpy.app.version_string` and platform;
- active scene and owner/schema metadata;
- object/collection/material/world/camera relationships;
- managed/unmanaged tags;
- operator return value and traceback;
- network-attempt count/offline mode;
- package path/SHA for installed Extension;
- build/rebuild timings and datablock counts.

Never infer success from source structure alone.