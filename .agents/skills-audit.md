# AWFUL STUDIO — Skills & Agent Infrastructure Audit

Status: verified recommendations, 2026-09-09

## Scope

This audit covers agent skills and workflows useful for AWFUL STUDIO: Blender 5.2 LTS, Python, 3D scene work, testing, systematic debugging, TDD, performance profiling, Git, documentation, visual regression, and research.

The goal is not to create a second project-management system. Notion remains the business/product documentation source of truth; GitHub issues remain implementation work items; skills describe repeatable working methods only.

## Project constraints that govern adoption

- Blender-native workflow. Do not replace ordinary Blender controls with agent abstractions.
- Runtime evidence is required for Blender behavior. Static Python tests are not proof of scene correctness.
- Performance regressions are bugs.
- Heavy pipelines, assets, compositor stages, volumetrics, and similar systems stay opt-in.
- No skill may silently alter business requirements.
- No integration is called installed, supported, or compatible until its exact version/commit has been exercised against the target environment.

## Verified installed methodology

The current host environment exposes the following Superpowers skills and they are suitable as upstream methodology:

1. `test-driven-development` — adopt as the generic RED/GREEN/REFACTOR discipline.
2. `systematic-debugging` — adopt for bug investigation before patching.
3. `verification-before-completion` — mandatory before claiming a task fixed or complete.
4. `requesting-code-review` / `receiving-code-review` — useful for substantial changes and review cycles.
5. `writing-plans` — useful for multi-step changes, but should not become mandatory ceremony for trivial Blender edits.

These skills should not be copied verbatim into the repository. Project-local adapters should reference their principles and add AWFUL-specific Blender requirements.

## Public candidates reviewed

### Blender Agent Studio

Repository: `ifBars/blender-agent-studio`

Observed strengths:

- explicitly validates Blender 5.2 LTS;
- deterministic asset inspection and evidence rendering;
- asset validation, iterative refinement, rendering, procedural, animation, character, simulation and MCP workflows;
- reproducible Python-first generation;
- multiview evidence and hard gates;
- bounded MCP that deliberately avoids arbitrary Python execution;
- benchmark modes for baseline / skills / skills+MCP.

Decision: **ADOPT SELECTIVELY / PILOT FULL PLUGIN**.

Recommended pieces for AWFUL STUDIO:

- `blender-asset-validation` — high value;
- `blender-iterative-refinement` — high value;
- `blender-rendering-workflow` — high value for evidence renders;
- `blender-procedural-workflow` — high value for generated studio geometry and helpers;
- `blender-animation-workflow` — conditional, when camera/product motion is under test;
- `blender-character-workflow` and simulation workflow — normally out of scope for core AWFUL STUDIO, but may be useful for adjacent experiments;
- benchmark/evidence harness ideas — useful as reference, but should be reduced to AWFUL-specific acceptance conditions;
- bounded MCP design — preferred security model over unrestricted `execute_blender_code` interfaces.

Conflicts / duplication:

- umbrella routing duplicates AWFUL orchestration;
- generic modeling/game-ready/GLB delivery assumptions are not core product requirements;
- benchmark gauntlets and immutable evaluation suites are excessive for routine studio-preset work;
- full plugin introduces another routing layer and more ceremony than the base project needs.

Do not globally install the full suite as an unquestioned dependency. Run a controlled comparison first.

### Flue

Repository: `SFKislev/Flue`

Observed strengths:

- thin shell-to-application bridge rather than a large MCP schema;
- direct access to Blender `bpy` runtime;
- structured JSON result channel;
- supports small inspectable operations against an open Blender session;
- useful for live debugging and inspection when headless reproduction is insufficient.

Risk:

- it intentionally exposes direct scripting power, so the effective safety boundary is the script the agent writes;
- live-session convenience must not replace reproducible headless tests.

Decision: **EVALUATE AS OPTIONAL DEVELOPER BRIDGE**. Not installed or supported yet.

### pytest-blender

Repository: `mondeja/pytest-blender`

Observed strengths:

- runs pytest inside Blender's own Python interpreter;
- can point at a specific Blender executable;
- supports addon installation/cleanup and CI use;
- fits the requirement that Blender runtime behavior be tested inside Blender.

Decision: **EVALUATE / LIKELY ADOPT** for runtime tests after confirming Blender 5.2 behavior on the target Windows workstation. Do not replace lightweight pure-Python tests with it; use two layers.

### blender-addon-tester

Repository: `nangtani/blender-addon-tester`

Useful historically for cross-version testing, but overlaps strongly with pytest-blender and carries more machinery than AWFUL currently needs.

Decision: **REFERENCE ONLY** unless multi-version Blender compatibility becomes an explicit release requirement.

### Large unrestricted Blender MCP servers

Several public Blender MCP projects expose dozens or hundreds of Blender tools plus arbitrary Python execution.

Decision: **DO NOT ADOPT BY DEFAULT**. They offer breadth, but duplicate Blender's own API, enlarge the attack/destructive surface, and create another maintenance layer. Prefer a small bounded interface or Flue for deliberate live scripting.

## Recommended `.skills/` layout

The repository should contain only thin AWFUL adapters, not copies of whole external ecosystems.

Proposed structure:

```text
.skills/
  README.md
  awful-tdd/
    SKILL.md
  awful-systematic-debugging/
    SKILL.md
  awful-verification/
    SKILL.md
  blender-runtime-qa/
    SKILL.md
  blender-performance-profiling/
    SKILL.md
  blender-visual-regression/
    SKILL.md
  research-doc-sync/
    SKILL.md
  git-change-review/
    SKILL.md
```

### `awful-tdd`

Adds AWFUL rules to generic TDD:

- pure logic gets normal unit tests first;
- Blender-dependent behavior gets a runtime contract before implementation;
- existing strict-xfail tests may document not-yet-implemented requirements, but xfail must be explicit and scoped;
- no business requirement is weakened to make a test green.

### `awful-systematic-debugging`

Adds Blender-specific evidence collection:

- reproduce under factory startup when possible;
- capture Blender version, render engine/device, active scene, selected preset and relevant managed-object metadata;
- separate pure-Python defect, Blender API defect, scene-state defect, GPU/render defect and visual-quality defect;
- fix the smallest proven cause, then rerun the reproduction.

### `awful-verification`

A completion claim requires the relevant evidence:

- pure test suite;
- Blender 5.2 runtime test when `bpy` behavior changed;
- visual evidence when appearance/framing/light behavior changed;
- performance comparison when code touches scene-build, render setup, asset loading or volumetrics;
- `git diff --check` and relevant lint/type checks.

### `blender-runtime-qa`

Two-tier test model:

1. pure/static tests for data, math, registry policy and configuration;
2. Blender 5.2 headless/runtime tests for object creation, addon registration, scene mutation, rendering and managed-data cleanup.

Live-session bridges are debugging aids, not the canonical test harness.

### `blender-performance-profiling`

Profile before optimizing. Record at minimum:

- clean base-studio build time;
- object/data-block counts;
- memory/VRAM-sensitive optional feature activation where measurable;
- viewport/render setup changes relevant to the task;
- repeated median or distribution rather than a single lucky timing.

Use Python `cProfile`/`pstats` for Python hotspots and Blender-side timing markers for scene construction. GPU/render performance requires separate render evidence; Python profiling alone is insufficient.

### `blender-visual-regression`

Use deterministic evidence scenes and fixed cameras.

Recommended first checks:

- hero camera render;
- side/three-quarter evidence render;
- daylight acceptance scene with studio lights disabled;
- direct-flash scene showing required hard-shadow regime and off-axis flash position;
- framing/orbit safety scene around representative product bounds.

Visual regression should combine image comparison with semantic assertions. Pixel diff alone is too brittle for Blender rendering changes.

### `research-doc-sync`

Research may propose changes, but must distinguish:

- verified current project state;
- external reference;
- recommendation;
- installed/tested integration.

Update Notion business/architecture pages only when the change is actually a business or engineering decision. Keep implementation state in GitHub issues.

### `git-change-review`

For implementation PRs:

- issue reference required;
- acceptance test/evidence described;
- no unrelated formatting/refactor churn;
- verify no user/business text was changed accidentally;
- generated renders, large benchmark traces and private assets stay out of Git unless intentionally versioned.

## Conflict and duplication matrix

| Candidate | Overlap | Decision |
|---|---|---|
| Superpowers TDD | generic process | keep upstream methodology, add thin AWFUL adapter |
| Superpowers systematic debugging | generic process | keep upstream methodology, add Blender evidence rules |
| Superpowers verification | generic completion gate | mandatory upstream principle |
| Blender Agent Studio umbrella routing | AWFUL orchestration | do not make authoritative |
| Blender Agent Studio asset validation | runtime/visual QA | adopt concepts; pilot skill |
| Blender Agent Studio iterative refinement | visual regression/debug loop | adopt concepts; pilot skill |
| Blender Agent Studio benchmark gauntlets | project QA | reduce heavily; use only for selected comparisons |
| Blender Agent Studio bounded MCP | live Blender interface | strong pilot candidate |
| Flue | live Blender interface | optional developer bridge candidate |
| pytest-blender | runtime tests | likely adopt after Blender 5.2 verification |
| blender-addon-tester | runtime/version tests | redundant for current scope |
| unrestricted Blender MCPs | live control | reject by default due breadth/destructive surface |

## Approved integration work

Create GitHub issues for:

1. evaluate Flue against Blender 5.2 on Windows;
2. pilot selected Blender Agent Studio skills and compare with full-plugin mode;
3. establish Blender 5.2 runtime pytest harness;
4. establish deterministic visual-regression evidence scenes;
5. establish a performance evidence gate for base build and opt-in heavy features.

## Definition of "installed" / "supported"

An external integration may be called **installed** only after the actual repository/environment contains it and the version/commit is recorded.

It may be called **supported** only after:

- target Blender 5.2 runtime verification;
- documented setup and rollback/removal steps;
- at least one representative AWFUL STUDIO task succeeds;
- failure mode is understood;
- the GitHub issue records evidence.

Until then the correct labels are `candidate`, `pilot`, `reference`, or `rejected`.
