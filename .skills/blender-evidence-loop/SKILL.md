---
name: blender-evidence-loop
description: AWFUL STUDIO pilot workflow for evidence-backed Blender 5.2 validation and bounded refinement. Use after a complete Blender candidate exists, or when a visual/runtime Blender change must be verified without changing project requirements.
status: pilot
upstream_reference: ifBars/blender-agent-studio@1f9e050b17ecbb9174c93a001bece7fdbe73f436
---

# AWFUL Blender Evidence Loop

This is a project-local adapter, not a vendored installation of Blender Agent Studio.

AWFUL business requirements, architecture decisions, GitHub issues, and Notion project state remain authoritative. External workflow advice may improve the method but may not redefine the requested result.

## 1. Freeze the candidate

Before editing a complete candidate, preserve enough evidence to compare the repair fairly:

- source script / editable `.blend`;
- Blender version;
- render engine and device;
- relevant preset and product fixture;
- fixed hero and diagnostic cameras;
- fixed frame samples for motion;
- runtime/semantic assertions;
- current rendered evidence.

Never overwrite the only reproducible candidate.

## 2. Build the requirement ledger

For each task-critical requirement write one of:

- `pass` — directly supported by runtime or visible evidence;
- `fail` — evidence proves the requirement is not met;
- `unclear` — available evidence cannot prove it either way.

Do not infer a visual pass from object names, source code, or file existence.

AWFUL-specific examples:

- daylight visibly reaches product and cyclorama with artificial studio lights disabled;
- direct flash is off-axis and produces the intended hard-shadow regime;
- unmanaged scene content survives rebuild;
- camera framing respects product bounds;
- product motion does not intersect floor or pedestal;
- heavy optional features remain opt-in.

## 3. Identify one proven cause

Prioritize:

1. violated business/runtime requirement;
2. destructive scene-state behavior;
3. incorrect geometry, framing, lighting, material, or motion result;
4. performance regression;
5. secondary polish.

Separate Python logic defects from Blender scene-state, render/GPU, and visual-quality defects.

## 4. Repair durable source

Change the smallest durable source-level cause that can fix the highest-priority failure.

Do not hand-patch only a derived render or generated artifact when the source can reproduce the defect.

Do not weaken a test or business rule to make the repair pass.

## 5. Repeat identical evidence

Re-run with the same:

- Blender executable/version;
- factory/startup policy where applicable;
- input fixture;
- camera names and transforms;
- sampled frames;
- render engine/device;
- render resolution/samples/color management;
- semantic assertions;
- performance measurement method.

A comparison is invalid when the repair is judged under easier conditions than the candidate.

## 6. Retain or rollback

Retain a repair only when:

- the targeted failure improves or passes;
- no critical requirement regresses;
- runtime assertions still pass;
- visual evidence remains acceptable;
- relevant performance does not materially regress without an accepted reason.

Otherwise retain the original candidate and record why the repair was rejected.

## 7. Evidence report

Record at minimum:

- issue/task reference;
- Blender version;
- candidate evidence paths;
- requirement ledger;
- selected defect and diagnosed cause;
- source-level repair;
- final evidence paths;
- runtime test result;
- visual comparison result;
- performance comparison when relevant;
- decision: `retain_repair`, `retain_candidate`, or `blocked`.

## Relationship to Blender Agent Studio

This pilot adapter intentionally borrows only the useful evidence/refinement principles from Blender Agent Studio 0.6.2 at the pinned commit above: freeze-before-repair, explicit requirement ledger, fixed multiview/render evidence, source-level repair, and identical recheck.

It does not import BAS umbrella routing, game-ready delivery assumptions, character/simulation workflows, full benchmark ceremony, or MCP as project authority.

See `.agents/blender-agent-studio-pilot.md` and GitHub issue #2 for the controlled comparison protocol.
