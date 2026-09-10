---
name: blender-visual-regression
description: Validate AWFUL STUDIO visual changes with deterministic scenes, fixed views and semantic assertions instead of relying on a single subjective render.
---

# Blender visual regression

Use deterministic evidence scenes and fixed cameras. Visual acceptance should combine image evidence with semantic/runtime assertions.

Recommended evidence views when relevant:

- hero camera render;
- side or three-quarter render;
- daylight acceptance scene with managed studio lights disabled;
- direct-flash scene showing the intended hard-shadow regime and off-axis flash position;
- framing/orbit safety view around representative product bounds.

Keep render settings, camera transforms and representative assets stable when comparing before/after results. Record intentional acceptance changes rather than silently refreshing baselines.

Pixel diff alone is too brittle for renderer noise, color-management and GPU differences. Pair image comparison with assertions about camera, lights, object bounds, managed data and render configuration.
