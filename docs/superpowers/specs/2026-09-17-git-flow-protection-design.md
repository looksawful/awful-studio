# AWFUL STUDIO Git Flow and Branch Protection Design

## Goal
Keep `main` as the only long-lived branch while making accidental direct changes, stale branches, and unverified merges difficult.

## Branch model
- `main` is the only permanent branch.
- Work happens in short-lived branches only.
- Allowed working prefixes: `feat/`, `fix/`, `chore/`, `docs/`, `asset/`, `scene/`.
- No permanent `dev`, `develop`, or `release/*` branch.
- Branches are deleted automatically after merge.

## Merge policy
- All changes enter `main` through pull requests.
- Direct pushes to `main` are blocked.
- Force-push and deletion of `main` are blocked.
- Merge method: squash only.
- Merge commits and rebase merges are disabled.
- Pull request conversations must be resolved before merge.
- Human approval is not required for this single-owner/agent workflow.

## Required verification
The existing `Extension QA` workflow remains the source of truth for build validation.
A stable `merge-gate` job will depend on:
- `fast`
- `candidate`
- `runtime-windows`

`merge-gate` becomes the single required status check for `main`, insulating branch protection from future internal job restructuring.
## Repository settings
Enable:
- auto-merge
- automatic deletion of head branches after merge
- branch update button for pull requests
- squash merge

Disable:
- merge commits
- rebase merge

## Release flow
Stable releases are tag-driven rather than branch-driven:

`short-lived branch -> PR -> merge-gate -> squash into main -> version tag -> release workflow -> GitHub Release`

`release.yml` must stop publishing on every push to `main`. It should publish only from a version tag matching `v*` (and retain manual dispatch for recovery).
The release version and artifact names must be derived from the tag/project metadata instead of hard-coding `1.0.0`.

## Automation behavior
Agents may create short-lived branches and PRs. Once `merge-gate` succeeds and all conversations are resolved, auto-merge may complete the squash merge. GitHub then deletes the branch automatically.

Agents must not create a new branch merely to preserve history. Historical checkpoints belong in tags when preservation is actually needed.

## Failure behavior
- Failed CI blocks merge.
- A stale/outdated branch is updated from `main` and rerun before merge.
- If protection configuration breaks normal development, repository administrators may adjust the ruleset, but ordinary pushes still use the PR path.
- Stable release tags are treated as immutable; an existing release tag is never silently replaced.