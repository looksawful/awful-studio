# Worktree recovery and sparse checkout — 2026-09-25

## Problem

An interrupted `git worktree add` for issue #123 left a partial linked worktree while the main checkout already contained unrelated untracked work.

## Primary-source findings

- Git documents `git worktree remove`, `unlock`, `prune`, and `repair` as the native lifecycle/recovery commands for linked worktrees. If a working tree is removed manually, `git worktree prune` removes stale administrative metadata.
  - https://git-scm.com/docs/git-worktree
- Git documents sparse checkout as the native way to materialize only selected directories in a worktree. Cone mode accepts directories and keeps top-level files, which matches this repo's need to retain `AGENTS.md` / `STATE.md` while avoiding large binary asset trees.
  - https://git-scm.com/docs/git-sparse-checkout

## Local finding

The scary mass `D` + `??` status was observed while `git worktree add` still had a live child `git reset --hard --no-recurse-submodules`. It was an in-progress checkout state, not 586 independent repository edits.

The first nested worktree path (`awful-studio\.worktrees\...`) was also contrary to this repository's local `git-change-isolation` rule: never create an unignored project-local worktree directory.

## Decision

Use a sibling worktree:

`A:\Projects\CODE\awful-studio-agent-123`

Create it with `--no-checkout`, then enable cone-mode sparse checkout for only:

- `tools`
- `tests/fast`
- `docs/asset-library/research`
- required project-local skills

This avoids materializing hundreds of unrelated heavy assets and keeps the existing dirty `fix/final-storybook` checkout untouched.

## Corroboration

SOFA post `39c5ae9a-424d-40a2-8a23-d14847905f9a` independently confirms the safe ordering principle: free/remove a worktree before force-moving or deleting its branch. It is corroboration only; Git's own documentation is authoritative here.
