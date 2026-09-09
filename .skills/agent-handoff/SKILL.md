---
name: agent-handoff
description: Handoff, recursive review and issue-evidence protocol for autonomous AWFUL STUDIO agents.
status: installed
---

# AWFUL Agent Handoff

Use before delegating work, before stopping a substantial task, and when reviewing another agent's branch.

## Delegation

Give each agent exactly one independent problem domain with:

- repository and base branch;
- isolated branch name;
- owning issue/PR;
- allowed files/subsystem;
- explicitly forbidden overlapping files;
- acceptance behavior;
- required TDD/runtime evidence;
- expected issue comment and commit output.

Do not dispatch parallel agents to the same mutable subsystem.

## Completion handoff

Before stopping:

1. compare branch against base and inspect changed files;
2. run fresh targeted and broader verification;
3. commit/push;
4. comment the owning issue in English with root cause, changes, commands/results, Blender version where applicable, commit SHA and remaining blockers;
5. update `STATE.md` only for project-level state changes.

## Independent recursive review

A substantial autonomous implementation gets a fresh review pass after the implementation pass. The reviewer must not trust the implementation summary: inspect diff, run tests, verify evidence and look for destructive/compatibility regressions.

If confirmed problems exist, record them in the issue, fix them on the same domain branch with TDD, and run another verification pass. A further delayed review is created only while actionable blockers remain. Stop recursion when an independent review finds no actionable blocker and the required evidence is current.

Do not generate endless review tasks merely to satisfy ceremony.

## Conflict rule

If another branch has changed the same subsystem or introduced a competing architecture, stop integration and reconcile first. Never use automatic merge conflict resolution as a substitute for engineering review.