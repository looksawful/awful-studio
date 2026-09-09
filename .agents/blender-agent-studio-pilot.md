# Blender Agent Studio pilot protocol

Status: pilot, not installed, not supported
GitHub issue: #2
Pinned upstream: `ifBars/blender-agent-studio@1f9e050b17ecbb9174c93a001bece7fdbe73f436`
Observed plugin version at that commit: `0.6.2`
Target runtime: Blender 5.2 on Windows

## Purpose

Evaluate Blender Agent Studio (BAS) as a source of useful Blender workflows for AWFUL STUDIO without allowing it to replace AWFUL orchestration, business rules, project state, or product-specific acceptance criteria.

The comparison must separate three conditions:

1. **vanilla AWFUL** — existing AWFUL workflow only;
2. **selected BAS skills** — only the explicitly selected BAS methods listed below;
3. **full BAS plugin** — full upstream plugin including its own routing/MCP layer.

A condition may only be called tested after it has been run against the same representative AWFUL task, Blender version, source input, cameras, render settings, acceptance criteria, and evidence protocol as the other conditions.

## Selected BAS methods for the first pilot

### Adopt for evaluation

- `blender-asset-validation`
  - deterministic authored-scene inspection;
  - fixed multiview evidence;
  - semantic/technical checks in addition to images;
  - explicit distinction between authored scene and exported artifact.

- `blender-iterative-refinement`
  - freeze candidate before repair;
  - write a pass/fail/unclear requirement ledger;
  - make the smallest source-level repair;
  - rerun the exact same evidence protocol;
  - retain repair only if the target improves without regressions.

- `blender-rendering-workflow`
  - explicit render contract;
  - reproducible engine/device/color-management/output settings;
  - low-cost diagnostic render before final render;
  - visually open final evidence instead of trusting file existence.

- `blender-procedural-workflow`
  - explicit generator contract;
  - semantic node/socket naming;
  - deterministic seeds;
  - test default/min/max plus a seeded variation where applicable;
  - keep generated output distinct from source inputs.

### Conditional

- `blender-animation-workflow` only for camera/product-motion tasks.
- bounded BAS MCP only as a separate experimental variable.

### Excluded from AWFUL core pilot

- character workflow;
- simulation workflow;
- game-ready/GLB delivery ceremony when the task does not require export;
- generic asset-production stages that do not map to an AWFUL business requirement;
- BAS umbrella routing as project authority;
- benchmark gauntlet process for routine studio work.

## First representative tasks

### Task A — studio geometry / procedural

Build or regenerate a minimal AWFUL studio fixture with:

- metric room/stage geometry;
- cyclorama role;
- visible floor separate from hidden bounce floor;
- named managed objects;
- no destructive deletion of unrelated scene content.

Evidence:

- object/collection role manifest;
- dimensions/world bounds;
- front/side/three-quarter diagnostic renders;
- rebuild result proving unmanaged content survives.

### Task B — lighting / render evidence

Use a neutral product fixture and compare:

- continuous studio-light regime;
- daylight regime with artificial studio lights disabled;
- direct-flash regime with cool/neutral flash intent and off-axis placement.

Evidence:

- fixed hero camera;
- fixed three-quarter evidence camera;
- light-role manifest;
- render metadata;
- visual proof that daylight reaches product/cyclorama;
- visual proof that flash produces the intended hard-shadow regime.

### Task C — camera / product motion

Validate one camera orbit and one product motion preset against representative product bounds.

Evidence:

- fixed frame samples;
- no floor/pedestal intersection;
- framing safety margin remains valid;
- playback policy recorded separately from artistic motion preset.

## Metrics

For every condition record:

- Blender version;
- upstream BAS commit/version when used;
- runtime and render engine/device;
- task completion status;
- number of critical defects after first complete candidate;
- number of repair iterations;
- regressions introduced during repair;
- total wall-clock task time when measurable;
- generated evidence count;
- whether instructions conflicted with AWFUL requirements;
- whether a second project-state/routing source appeared;
- final qualitative result: better / equivalent / worse, with evidence.

Do not invent a single combined score before baseline variance and task relevance are understood.

## Stop conditions

Stop the full-plugin condition if it:

- attempts to rewrite AWFUL business requirements;
- makes BAS project state authoritative;
- requires destructive scene operations outside the task;
- requires unnecessary external asset acquisition;
- cannot preserve identical comparison conditions;
- materially increases ceremony without an observable QA or output benefit.

## Adoption rule

An individual BAS skill may graduate from `pilot` to `supported` only if:

- it improves at least one representative AWFUL task;
- it does not weaken AWFUL runtime/TDD/business-rule gates;
- overlap with existing AWFUL skills is reduced to one clear authority;
- setup/removal instructions are documented;
- exact upstream commit/version is recorded;
- Blender 5.2 runtime evidence exists.

Until then BAS remains an external pilot/reference, not an installed dependency.
