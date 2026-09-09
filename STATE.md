# AWFUL STUDIO Current State

Last reviewed: 2026-09-10

This is a short handoff, not the project-management source of truth. Requirements live in Notion; implementation work/status lives in GitHub Issues and PRs.

## Release state

- Historical release: Alpha 0.0.15.
- Target: Alpha 0.0.16 Extension Foundation.
- Blender target: 5.2 LTS; verified local/cloud target runtime: 5.2.1.
- Historical source SHA-256: `5d14513b699a0c0a0e693bba7c31111f264ac5988cf1abb85c7153f6a2e7e56b`.
- Draft Extension work: PR #11 on `feature/extension-foundation`.
- PR #11 is not release-ready. Fast tests pass, but current runtime CI is blocked before Blender execution by an HTTP 403 while fetching the official checksum file.

## Active architectural issue

Two independent runtime foundations currently diverge from the same `main`:

- `feature/extension-foundation`: Extension packaging/runtime harness plus Alpha 0.0.16 source foundation.
- `agent/6-agent-runtime-foundation`: `AGENTS.md`/`STATE.md` proposal, pinned `runtime/blender.lock`, unified `tools/awful.py`, runtime bootstrap/cache/CI experiments.

They must be reconciled into one canonical runtime/bootstrap/CI path before either runtime implementation is merged. Issue #12 owns that reconciliation; issue #3 owns runtime harness acceptance.

## Known merge blockers / review risks

Issue #10 contains the detailed review ledger. Current high-priority items include:

- ownership code relies on global `bpy.data` snapshots and `as_pointer()` identity, which is not a safe durable owner-discovery mechanism across deletion/recreation;
- destructive cleanup must be proven scene-scoped in multi-scene files;
- historical migration coverage must be metadata-only, idempotent, and must not guess ownership;
- base Build/preset behavior must make zero network attempts offline;
- the final built ZIP has not yet passed the complete install/disable/re-enable/restart/save/reopen/migrate contract in CI;
- project license/SPDX state was introduced as GPL-3.0-or-later without a recorded owner approval and remains an explicit decision gate.

## Current test policy

- Pure/static tests for policy, parsing, math, metadata, tooling.
- Real Blender 5.2 runtime tests for registration, lifecycle, `bpy` data creation/mutation/removal, migration, packaging, save/reopen and update behavior.
- No mandatory render tests for the current foundation.
- Performance measurements are required when scene-build or expensive optional paths change.

## Immediate sequence

1. Reconcile canonical runtime/bootstrap/CI (#12 + #3).
2. Fix and independently review ownership/multi-scene safety (#10).
3. Complete migration and offline asset/network contracts (#10).
4. Run final-ZIP runtime verification on Blender 5.2.1 Linux and Windows.
5. Build and verify the native static Extension repository/update path.
6. Resolve licensing explicitly before public release.
7. Reconcile README/install/update/troubleshooting docs with verified behavior.
8. Publish Alpha 0.0.16 only after all release gates are green.

Use `AGENTS.md` and the relevant `.skills/*/SKILL.md` before editing.