# AWFUL STUDIO project-local skills

This directory contains thin, project-specific workflow adapters. Skills define repeatable working methods only. They do not duplicate Notion requirements, GitHub issue state, or external skill ecosystems.

## Installed adapters

- `awful-tdd` — RED/GREEN/REFACTOR with Blender-runtime rules.
- `awful-systematic-debugging` — root-cause-first Blender/Python/CI debugging.
- `awful-verification` — evidence gate before completion claims.
- `git-change-isolation` — branch/worktree ownership and concurrent-agent rules.
- `git-change-review` — issue-linked code review and destructive-safety priorities.
- `blender-runtime-qa` — two-tier static + Blender 5.2 final-ZIP runtime testing.
- `blender-extension-lifecycle` — register/enable/disable/restart/package lifecycle discipline.
- `blender-managed-data-safety` — scene-scoped ownership, migration and cleanup safety.
- `asset-network-safety` — offline-first network/cache/provenance discipline.
- `blender-performance-profiling` — measure-first build/rebuild performance evidence.
- `release-readiness` — final ZIP, native repository/update and publication gates.
- `agent-handoff` — precise issue/evidence/branch handoff and recursive review.
- `blender-evidence-loop` — existing selected Blender Agent Studio evidence/refinement pilot.

## Rules

- A local skill adds AWFUL-specific constraints to a general method; it is not a vendored copy of an upstream skill.
- Business/product/architecture requirements remain authoritative in Notion.
- GitHub Issues own implementation tasks and status.
- Blender-dependent claims require Blender 5.2 runtime evidence.
- Static tests alone never prove `bpy` scene behavior.
- Performance regressions are defects.
- No skill may weaken requirements or destructive-data safeguards to make a test pass.
- External integrations remain `candidate`, `pilot`, `reference`, or `rejected` until exact-version runtime evidence justifies `supported`.

Read `AGENTS.md` first, then only the skills relevant to the task.