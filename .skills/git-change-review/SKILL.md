---
name: git-change-review
description: Issue-linked code review workflow for AWFUL STUDIO branches and PRs, prioritizing destructive safety and runtime evidence.
status: installed
---

# Git Change Review

Review the diff, not the author's confidence.

## Inputs

- owning GitHub issue and acceptance criteria;
- base/head refs and changed filenames;
- code diff;
- current CI/runtime evidence;
- relevant `AGENTS.md` invariant and domain skill.

## Severity order

1. Critical: can delete/mutate unmanaged data, corrupt/update scenes, bypass security/checksum/network boundaries, or publish a bad release.
2. Major: lifecycle/runtime/migration/package behavior is wrong or unverified in a way that blocks acceptance.
3. Minor: maintainability, diagnostics, naming, docs or test clarity that does not invalidate behavior.

## Required review questions

- Does the change solve the issue without changing the requirement?
- Is destructive authority explicit and scene/owner scoped?
- Are multi-scene/shared data cases safe?
- Is import/register/startup side-effect free?
- Does offline behavior remain zero-network?
- Does the test prove the behavior and was RED observed for new regression coverage?
- For `bpy` changes, is there real Blender 5.2 evidence?
- For release changes, was the exact built ZIP tested?
- Did the branch duplicate another active implementation?
- Did it accidentally change user/product text or unrelated code?

## Review output

Put actionable findings in the PR/owning issue with file/function, impact, reproduction/evidence and expected fix. Do not approve a branch merely because fast/static tests pass when the acceptance behavior requires Blender runtime.

After fixes, review fresh diff and rerun the relevant test evidence before resolving the finding.