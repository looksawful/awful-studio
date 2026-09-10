---
name: blender-runtime-qa
description: Verify AWFUL STUDIO Blender-dependent behavior inside Blender 5.2 instead of treating static Python checks as runtime proof.
---

# Blender runtime QA

Use a two-tier model.

## Tier 1: pure/static

Keep fast tests for data transforms, math, registries, policy/configuration, serialization and other logic that does not require `bpy` state.

## Tier 2: Blender 5.2 runtime

Use Blender runtime evidence for:

- object/data-block creation and deletion;
- addon/register/unregister behavior;
- scene mutation and managed-data cleanup;
- materials, collections, cameras and lights;
- render-engine/device setup;
- rendering and file output;
- repeated-run/idempotency behavior.

Prefer factory startup and deterministic fixtures when practical. Verify both the intended result and cleanup/lifecycle behavior so a passing render does not hide leaked objects or stale scene state.

A live-session bridge may help inspect a failure but is not the canonical test harness. Record the exact Blender version and relevant runtime configuration with evidence.
