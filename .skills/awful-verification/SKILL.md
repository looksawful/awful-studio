---
name: awful-verification
description: Require the right evidence before claiming an AWFUL STUDIO change complete, including Blender 5.2 runtime, visual and performance evidence when relevant.
---

# AWFUL STUDIO verification

Use Superpowers verification-before-completion as the generic rule. For this repository, completion claims require task-relevant fresh evidence.

## Required evidence by change type

- Pure data/math/registry/config logic: relevant fast test suite.
- `bpy`, registration, scene mutation, managed object/data cleanup or render setup: Blender 5.2 runtime verification.
- Appearance, framing, camera, lighting, materials or compositor changes: deterministic visual evidence from fixed acceptance views.
- Scene-build, asset-loading, render setup, volumetrics or other performance-sensitive work: before/after performance evidence.
- Repository/tooling changes: relevant lint/type/static checks plus diff review.

Do not use a broad green test as a substitute for the specific missing evidence. Static Python success does not prove Blender runtime behavior; one render does not prove lifecycle cleanup; Python profiling does not prove GPU/render performance.

If a required environment is unavailable, state exactly which check remains unverified and do not upgrade the result to "supported", "fixed" or release-ready.
