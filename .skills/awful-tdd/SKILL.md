---
name: awful-tdd
description: Apply TDD to AWFUL STUDIO without mistaking static Python tests for Blender 5.2 runtime evidence.
---

# AWFUL STUDIO TDD

Use generic RED/GREEN/REFACTOR methodology from Superpowers, then add the project-specific rules below.

- Pure logic gets a failing unit/characterization test before implementation when practical.
- Blender-dependent behavior gets a runtime contract before implementation; static tests alone are insufficient.
- Scene creation, registration, managed-data cleanup, render configuration and `bpy` behavior require Blender 5.2 evidence.
- Visual requirements need deterministic evidence scenes/renders in addition to semantic assertions.
- Performance-sensitive changes need before/after evidence; never make a slower path green by weakening the requirement.
- Existing strict-xfail tests may document not-yet-implemented requirements only when the xfail is explicit, scoped and still represents the real requirement.
- Do not change business/product requirements to make a test pass.

Prefer the smallest test that proves the requirement. Keep pure tests fast and use Blender runtime tests only where Blender state actually matters.
