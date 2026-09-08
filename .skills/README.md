# AWFUL STUDIO project-local skills

This directory is reserved for thin project-specific workflow adapters.

The authoritative adoption decisions live in `.agents/skills-audit.md`.

## Rules

- A project-local skill describes a repeatable method, not project state.
- Do not duplicate Notion requirements or GitHub issue status inside a skill.
- Prefer small adapters over vendoring entire third-party skill ecosystems.
- External skills remain `candidate` or `pilot` until their exact version/commit is tested.
- Blender behavior requires Blender 5.2 runtime evidence where relevant.
- Static tests alone never prove scene/render correctness.
- Performance regressions are defects.
- Business requirements are not relaxed to satisfy tooling.

## Proposed adapters

- `awful-tdd`
- `awful-systematic-debugging`
- `awful-verification`
- `blender-runtime-qa`
- `blender-performance-profiling`
- `blender-visual-regression`
- `research-doc-sync`
- `git-change-review`

These names are recommendations only. Their presence in this README does not mean the skill directories are installed or active.
