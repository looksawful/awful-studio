# AWFUL STUDIO Production Readiness Design

Date: 2026-09-10
Status: accepted execution design based on the approved project roadmap and current review findings

## Goal

Deliver AWFUL STUDIO Alpha 0.0.16 as a reliable Blender 5.2 Extension that can be installed, enabled, used offline, rebuilt without damaging user data, saved/reopened, migrated from the historical 0.0.15 scene format, updated through Blender's native Extension repository flow, and verified reproducibly by agents and CI.

## Non-goals for 0.0.16

- large feature expansion;
- visual redesign of the studio presets;
- mandatory render/image regression suite;
- rewriting the 0.0.15 monolith into many modules;
- Docker/GHCR unless measured evidence later proves a need;
- arbitrary remote Blender control or unrestricted MCP execution.

## Architecture

### Historical baseline

`historical/0.0.15/awful_studio_v4_2_gpu_perf.py` remains byte-identical to SHA-256 `5d14513b699a0c0a0e693bba7c31111f264ac5988cf1abb85c7153f6a2e7e56b`. It is evidence and a migration fixture, not production code to edit.

### Extension package

`extension/awful_studio/` is the only release package source. For 0.0.16 it may retain the adapted monolithic implementation under `core/legacy.py`; lifecycle, ownership, migration, asset/network and release boundaries are separated around it. Modularization of feature internals follows after the foundation is proven.

### Lifecycle

Import/register/enable/disable/re-enable/restart must not create or rebuild a studio. `register()` owns class/property registration only. Build/Rebuild/Remove/Migrate are explicit operators. Failure to establish safe ownership or compatible schema cancels before destructive mutation.

### Ownership and data safety

Ownership is scene/studio scoped and explicitly tagged. Names and semantic roles are lookup aids, not authorization. Destructive operations may affect only data proven to belong to the active AWFUL owner. User objects, transforms, materials, collections, world/camera choices and linked/shared data survive all lifecycle paths. Global `bpy.data` scans may be used for evidence or lookup only when mutation is additionally constrained by proven owner and scene membership. Allocation pointers are not durable identity.

### Migration

Schema 0 represents historical AWFUL metadata. Migration to schema 1 is explicit, metadata-only, idempotent, and does not reconstruct geometry or reset artistic/user transforms. Shared/ambiguous historical data is rejected rather than guessed. Future schema versions are rejected before mutation.

### Offline and assets

Base studio creation has a procedural fallback and must make zero network attempts. Network downloads happen only after explicit user action, require Blender online access plus AWFUL opt-in, use curated URLs, bounded download sizes, cache confinement, provenance metadata and validation. Cache cleanup deletes only recognized AWFUL cache entries.

### Runtime and testing

One canonical runtime bootstrap supplies exact Blender 5.2.1 binaries/checksum metadata for local agents and CI. Fast tests cover pure policy/tooling. Blender runtime tests cover registration, packaging, scene mutation, ownership, migration, save/reopen, offline behavior and final-ZIP execution. The same runtime contract is used locally and in CI. A source-checkout import cannot substitute for testing the built package.

### Release/update

Blender's own CLI validates/builds the package and generates the static Extension repository. GitHub Actions produces evidence and candidate artifacts but cannot publish a release when required runtime gates fail. A static remote repository is hosted for Blender-native updates. Update verification installs a lower test version, discovers a higher version through the repository, performs native update, reopens the saved scene and reruns compatibility assertions.

### Agent execution model

GitHub Issues are implementation work items; Notion is business/product/architecture authority. Agents use short-lived isolated branches and domain ownership. Parallel agents must not edit the same subsystem. Every substantial agent leaves issue evidence and a fresh review gate. `AGENTS.md`, `STATE.md` and `.skills/` are onboarding/work-method files, not a second project-management system.

## Release gates

Alpha 0.0.16 is ready only when all are true:

1. Historical baseline hash passes.
2. Project license is explicitly approved and manifest/SPDX/LICENSE agree.
3. Extension source and final ZIP validate with Blender 5.2 tooling.
4. Exact final ZIP installs into an isolated profile.
5. Enable/disable/re-enable/restart does not mutate ordinary scene content or accumulate handlers/RNA.
6. Explicit offline Build succeeds with zero network attempts.
7. Rebuild is bounded and preserves unmanaged/shared/multi-scene data.
8. Remove deletes only proven AWFUL-owned scene data and restores previous world/camera where applicable.
9. Historical migration is metadata-only, idempotent and save/reopen safe.
10. Future schema is rejected before mutation.
11. Optional asset fetch is explicit, cache-confined, provenance-recorded and failure-safe.
12. Linux Blender 5.2.1 runtime suite passes on the built ZIP.
13. Windows Blender 5.2.1 runtime suite passes on the built ZIP.
14. Build/rebuild performance evidence shows no material unapproved regression from the foundation baseline.
15. Static Extension repository is generated by Blender tooling and native update is verified end-to-end.
16. Installation, update, uninstall/remove, troubleshooting and known limitations are documented from verified behavior.
17. PR review has no unresolved critical/major safety issue.
18. Release artifacts include package SHA-256 and runtime evidence.

## Integration order

Runtime canonicalization and ownership safety land before release work is considered authoritative. Migration and asset/network branches integrate after ownership APIs stabilize. Release/update tooling can develop independently but stays gated until the canonical runtime and package tests are green. Only then is the feature foundation PR consolidated and prepared for main.

## Decision boundaries

- No implementation may silently change business requirements to satisfy a test.
- No agent may decide the project license incidentally.
- No failing runtime job may be converted into a warning to permit publishing.
- No second runtime/bootstrap/package index is introduced when an existing canonical path can be extended.
- No release-ready claim without fresh evidence from the exact candidate commit/package.