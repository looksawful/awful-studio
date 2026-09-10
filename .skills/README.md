# AWFUL STUDIO project-local skills

This directory contains thin project-specific workflow adapters. The authoritative adoption decisions live in `.agents/skills-audit.md`.

## Rules

- A project-local skill describes a repeatable method, not project state.
- Do not duplicate Notion requirements or GitHub issue status inside a skill.
- Prefer small adapters over vendoring entire third-party skill ecosystems.
- External skills remain `candidate` or `pilot` until their exact version/commit is tested.
- Blender behavior requires Blender 5.2 runtime evidence where relevant.
- Static tests alone never prove scene/render correctness.
- Performance regressions are defects.
- Business requirements are not relaxed to satisfy tooling.

## Active adapters

- `blender-evidence-loop` — existing evidence-oriented Blender workflow.
- `awful-tdd` — Superpowers TDD adapted to Blender runtime and product constraints.
- `awful-systematic-debugging` — root-cause debugging with Blender/scene/GPU classification.
- `awful-verification` — completion gate requiring the right runtime, visual and performance evidence.
- `blender-runtime-qa` — two-tier pure/static plus Blender 5.2 runtime verification.
- `blender-performance-profiling` — repeatable before/after scene-build and render-sensitive profiling.
- `blender-visual-regression` — deterministic fixed-view visual evidence plus semantic assertions.
- `research-doc-sync` — separates verified project state, external reference, recommendation and installed/tested integration status.
- `git-change-review` — change review for scope, evidence, business-text safety and generated/private asset leakage.

## External upstream status

Superpowers remains upstream methodology and is not copied wholesale into this repository. `ifBars/blender-agent-studio` remains selective/pilot only until its exact revision is exercised against the target Blender 5.2 environment. Flue and `pytest-blender` remain evaluation candidates as described in `.agents/skills-audit.md`.

Do not describe an external integration as installed or supported merely because one of these local adapters references its methods.
