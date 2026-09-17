# AWFUL STUDIO Consolidation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Consolidate all current AWFUL STUDIO in-flight work into `main`, preserve unique work, and reduce active branches/worktrees to `main` plus at most one genuinely unfinished branch.

**Architecture:** `main` is the only canonical product line. Existing branches are audited for patch-equivalent, merged, unique, or unfinished work; only unique accepted deltas may enter `main`. Historical checkpoints are preserved by reachable commits/tags before their branches are removed.

**Tech Stack:** Git, Python unittest, Blender 5.2.1, GitHub Actions, Blender Extension tooling.

**Spec:** User-approved consolidation direction in chat plus `AGENTS.md` and `STATE.md`.

## Global Constraints

- Work only in `looksawful/awful-studio`; do not modify `looksawful.ru`.
- Never delete a branch/worktree until unique commits and dirty files are proven preserved.
- Do not weaken provenance, checksum, ownership, offline, or lifecycle gates.
- Production behavior changes require RED → GREEN TDD.
- Blender-dependent claims require Blender 5.2.1 evidence.
- Every merged result must pass fresh fast tests and `git diff --check`.
- `main` remains canonical; temporary consolidation branches are deleted after integration.

### Task 1: Inventory and preserve
- [ ] Fetch/prune and record current `main`, PRs, branches and worktrees.
- [ ] Inspect every dirty worktree before removal.
- [ ] Compare each branch with `main` using `rev-list`, `cherry`, and tree diff.
- [ ] Preserve unique dirty/committed work in GitHub before cleanup.

### Task 2: Integrate current deliverables
- [ ] Confirm iPhone v30 and Wave 01 research are canonical on `main`.
- [ ] Reconcile legacy release/smoke PRs against current 1.0.0/main and keep only unique useful tooling.
- [ ] Reconcile the studio-rig draft without promoting unfinished geometry to APPROVED.
- [ ] Reconcile device foundation/material handoff data still living outside `main`.

### Task 3: Collapse branch topology
- [ ] Remove worktrees whose changes are merged or preserved.
- [ ] Delete local and remote branches proven merged/superseded.
- [ ] Close superseded PRs with an evidence-based handoff comment.
- [ ] Keep no more than one unfinished feature branch besides `main`.

### Task 4: Verify canonical state
- [ ] Run `python -m unittest discover -s tests/fast -v`.
- [ ] Run `git diff --check` and relevant Blender/package checks for integrated changes.
- [ ] Verify branch/worktree counts and remote reachability.
- [ ] Update `STATE.md` and owning issues only where project-level state actually changed.
