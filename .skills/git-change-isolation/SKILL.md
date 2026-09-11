---
name: git-change-isolation
description: Git branch/worktree isolation and concurrent-agent ownership rules for AWFUL STUDIO.
status: installed
---

# Git Change Isolation

Use before substantial implementation or when multiple agents are active.

## Before editing

1. Inspect `main`, the intended base branch, active PRs and relevant issue.
2. Compare the candidate base with other active branches touching the same subsystem.
3. Create/use one short-lived branch: `agent/<issue>-<scope>`.
4. Declare the files/subsystem owned by this branch in the issue/handoff.

A GitHub branch is sufficient isolation for remote agents. Local agents may use a worktree when available; never create an unignored project-local worktree directory.

## Concurrency

Parallel work is allowed only for independent domains. Two agents must not both invent runtime bootstrap, ownership, migration or release mechanisms. If overlap is discovered, stop and reconcile rather than merge competing implementations.

When another branch owns a required file, either:

- depend on its public interface;
- add a new non-overlapping test/helper file;
- record the dependency/blocker in the issue.

Do not quietly edit the shared file and hope Git's conflict markers will perform architecture review.

## Commits

- one meaningful tested change per commit;
- no unrelated formatting/refactor churn;
- issue-linked message where useful;
- never commit generated runtime/cache/dist/private assets unless intentionally versioned;
- do not merge main or delete another branch without explicit authorization.

## Before handoff

Compare branch to base, inspect changed filenames, run relevant tests plus `git diff --check`, push, and record commit SHA/evidence in the issue.