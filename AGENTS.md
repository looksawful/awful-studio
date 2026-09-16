# AWFUL STUDIO Agent Guide

This file is the default entry point for GPT Chat, GPT Work, Codex-like agents, and human contributors.

## Start here

1. Read `STATE.md`.
2. Read the relevant GitHub issue and active PR/branch before editing.
3. Read only the project-local skill(s) relevant to the task under `.skills/`.
4. Read Notion only when product/business/architecture requirements are missing or disputed. Notion is authoritative for those requirements; GitHub Issues own implementation work and status.
5. Never infer Blender behavior from static source alone. Runtime-dependent claims require Blender 5.2 evidence.

## Product invariants

- Product: AWFUL STUDIO, a Blender-native virtual product/advertising studio.
- Target: Blender 5.2 LTS; verified working runtime target is Blender 5.2.1.
- Alpha 0.0.15 is the immutable historical monolithic baseline.
- Alpha 0.0.16 is the Extension Foundation target.
- Blender-native controls stay authoritative. Do not duplicate standard Blender transforms/settings merely to create a custom control layer.
- Extension import/register/enable/update/restart must not build or mutate a scene.
- Studio creation is explicit through Build/Rebuild operators.
- Base Build must work offline and make zero network attempts.
- Optional assets, heavy compositor stages, volumes, and similarly expensive systems remain opt-in.
- Unmanaged user data must survive Build, Rebuild, Remove, disable/re-enable, save/reopen, migration, and update.
- Performance regressions in normal studio construction are defects.
- Render/image regression testing is not mandatory for the current 0.0.16 foundation unless a task explicitly changes visual output.

## Ownership safety

Names and `awful_role` do not grant ownership. Destructive operations require explicit owner metadata belonging to the active scene/studio. Never iterate global `bpy.data` and mutate/remove items merely because they look like AWFUL data. Shared objects/materials/images/collections and multi-scene files are first-class safety cases.

Do not use allocation addresses/pointers as durable identity. If a migration or rebuild cannot prove ownership safely, refuse mutation and surface a clear error instead of guessing.

## Network and filesystem safety

- No network access on import, register, enable, startup, update, Build, or ordinary preset switching.
- Network operations require explicit user intent plus Blender online access.
- Downloads must be allowlisted, bounded in size, provenance-recorded, validated, and written only inside the configured AWFUL cache.
- Cache deletion must never recursively delete arbitrary user directories.
- Never silently weaken checksum or provenance verification to make CI green.

## Development method

For a bug or unexpected behavior: use `.skills/awful-systematic-debugging/SKILL.md` before editing.

For production code changes: use `.skills/awful-tdd/SKILL.md`. Write the failing test first, run it and verify the intended failure, implement the minimum fix, then rerun targeted and broader tests.

Before claiming completion: use `.skills/awful-verification/SKILL.md`.

For Blender behavior: use `.skills/blender-runtime-qa/SKILL.md` and the existing `.skills/blender-evidence-loop/SKILL.md` when relevant.

## Git and concurrent agents

- Work on an isolated short-lived branch. Prefer `agent/<issue>-<scope>`.
- One agent owns one problem domain. Avoid editing files assigned to another active agent.
- Before starting, compare the intended branch with its base and inspect active branches/PRs.
- Do not create a second implementation of an existing bootstrap/test/release path. Consolidate or reuse.
- Small, reviewable commits are preferred. Do not mix unrelated refactors or formatting.
- Do not merge to `main`, publish a release, or delete another agent branch unless explicitly authorized.
- GitHub issue comments and engineering handoff notes are written in English.
- When two branches solve the same subsystem differently, stop feature work and reconcile architecture before merging either.

## Review expectations

Every substantial change must be reviewable against an issue and acceptance evidence. Reviewers prioritize:

1. user-data/destructive safety;
2. lifecycle correctness;
3. runtime correctness under Blender 5.2;
4. offline/network boundaries;
5. migration/update compatibility;
6. performance regression;
7. maintainability and polish.

Do not approve because source looks plausible. Inspect test evidence and, for `bpy` behavior, real Blender execution.

## Release rules

A release candidate is not ready until the exact built ZIP has been validated, installed into an isolated Blender profile, enabled, disabled, re-enabled, restarted/reopened, and exercised by the required runtime contract. Native repository/update behavior must be tested using the package that will actually be published.

Project licensing is currently an explicit decision gate. Do not change `LICENSE`, SPDX headers, or manifest license fields as an incidental engineering fix. Record licensing inconsistencies as blockers until the owner approves the license.

## External integrations

`candidate`, `pilot`, `reference`, `supported`, and `rejected` are meaningful statuses. An integration is not `supported` until its exact version/commit has target-runtime evidence and documented setup/failure/rollback behavior. Blender Agent Studio remains selective/pilot; Flue remains optional candidate; pytest-blender is optional pending evidence; unrestricted Blender MCP servers are not default dependencies.

## Handoff

Before stopping a substantial task:

- run fresh relevant verification;
- commit/push the branch;
- comment the owning issue with root cause/changes/tests/commit SHA/blockers;
- update `STATE.md` only if project-level current state changed;
- leave exact next steps, not vague prose.

Evidence before claims. If the relevant test was not run in the current work session, do not state that it passes.