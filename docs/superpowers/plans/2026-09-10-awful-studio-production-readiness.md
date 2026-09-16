# AWFUL STUDIO Alpha 0.0.16 Production Readiness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: use the project-local `.skills/agent-handoff`, `.skills/awful-tdd`, `.skills/awful-systematic-debugging`, and the domain-specific skill for your task. Execute task-by-task on isolated branches and review before integration.

**Goal:** ship Alpha 0.0.16 as a safe, installable, updateable Blender 5.2 Extension with reproducible final-ZIP runtime evidence.

**Architecture:** preserve the verified 0.0.15 implementation as the behavioral baseline, wrap it with explicit Extension lifecycle/ownership/migration/network boundaries, and drive correctness from one canonical Blender 5.2.1 runtime harness. Release and native update are gated by exact-package evidence rather than source plausibility.

**Tech Stack:** Python 3.11+, Blender Python API (`bpy`), Blender 5.2.1 LTS, Blender Extension CLI, `unittest`/runtime scripts, GitHub Actions, static GitHub Pages-compatible Extension repository.

**Spec:** `docs/superpowers/specs/2026-09-10-awful-studio-production-readiness-design.md`

## Global constraints

- Historical 0.0.15 SHA-256 remains `5d14513b699a0c0a0e693bba7c31111f264ac5988cf1abb85c7153f6a2e7e56b`.
- Target Blender is 5.2.1 for 0.0.16 release evidence.
- No mandatory render tests for this foundation.
- No automatic network access during import/register/startup/build/preset switching.
- No unmanaged data deletion or mutation authorized by names/roles alone.
- No release publishing while required runtime evidence is red/missing.
- Licensing is an owner decision gate; engineering does not silently choose/change it.
- GitHub Issues own implementation status; Notion owns product/business/architecture requirements.

---

## Task 1: Reconcile the runtime foundation

**Files:** `runtime/blender.lock`, `tools/awful.py` or the selected canonical runtime tool, `tools/setup_blender.py` only if retained, `.github/workflows/extension-ci.yml`, runtime tests, docs.

**Produces:** one canonical API for locating/bootstraping Blender and invoking runtime QA; no competing bootstrap implementations.

- [ ] Compare `feature/extension-foundation` with `agent/6-agent-runtime-foundation` and document which runtime concepts survive.
- [ ] Write failing tests for the chosen bootstrap contract: exact version, exact pinned SHA-256, local-cache reuse, release-asset/official fallback, and setup-failure evidence.
- [ ] Run the targeted test and confirm the intended RED failure.
- [ ] Implement the minimum canonical bootstrap; delete/retire the duplicate path in the integration branch rather than retaining both.
- [ ] Run fast tests and verify GREEN.
- [ ] Run a real Blender smoke invocation:

```sh
python tools/awful.py doctor
python tools/awful.py bootstrap
python tools/awful.py test-runtime
```

- [ ] Update CI to call the same runtime entrypoint.
- [ ] Ensure setup failure still uploads a diagnostic text/JSON artifact instead of producing a second artifact-upload failure.
- [ ] Record exact Blender path/version/checksum in evidence.
- [ ] Commit and comment #12/#3 with the decision and evidence.

## Task 2: Make ownership scene-safe and deterministic

**Files:** `extension/awful_studio/ownership.py`, lifecycle call sites only as needed, dedicated runtime ownership tests.

**Produces:** explicit owner-scoped mutation/removal contract that is safe across multiple scenes and shared data.

- [ ] Add a runtime regression fixture with two scenes, unmanaged cross-scene objects, shared materials, nested unmanaged collections, and owned parents.
- [ ] Add a test proving role/name alone never grants destructive authority.
- [ ] Add a test that recreates/removes datablocks across rebuild and does not rely on pointer reuse for ownership discovery.
- [ ] Run tests and confirm RED against current implementation.
- [ ] Replace post-hoc global pointer-diff ownership as the authority with explicit owner tagging at creation boundaries; if temporary discovery remains, scope it so pointer reuse cannot skip tags.
- [ ] Constrain cleanup mutation to proven active-owner data and active-scene relationships.
- [ ] Preserve unmanaged child world transforms when detaching from managed parents.
- [ ] Preserve shared generated materials/images when external users remain.
- [ ] Run targeted Blender runtime tests until GREEN.
- [ ] Run the full current runtime contract before commit.
- [ ] Comment #10 with the destructive-safety cases now covered.

## Task 3: Make Build/Rebuild failure-safe

**Files:** `extension/awful_studio/__init__.py`, ownership/lifecycle helpers, runtime lifecycle tests.

**Produces:** no partially authorized destructive rebuild when preflight/schema checks fail.

- [ ] Add a test where an invalid/future schema causes Rebuild to cancel before any scene/data mutation.
- [ ] Add a test where ownership preflight fails and Build/Rebuild leaves the original scene unchanged.
- [ ] Confirm RED.
- [ ] Move every compatibility/ownership preflight before destructive legacy removal.
- [ ] Ensure `last_error`/`last_operation` reporting does not itself imply a successful build.
- [ ] Ensure `mark_generated` or its replacement is not run after a failed operation in a way that adopts unrelated data.
- [ ] Verify GREEN and run lifecycle runtime suite.

## Task 4: Complete historical migration

**Files:** `extension/awful_studio/migrations.py`, migration runtime tests, historical fixture only as immutable input.

**Produces:** explicit metadata-only schema 0 → 1 migration with safe refusal for ambiguity.

- [ ] Enumerate historical managed datablock classes actually created by 0.0.15: objects, object data, collections, materials, world, node groups/images/actions where relevant.
- [ ] Add tests for migration physical-state equality before/after, idempotence, save/reopen, shared-scene rejection, and unknown future schema rejection.
- [ ] Confirm RED for missing coverage.
- [ ] Implement only metadata tagging necessary to establish safe owner/schema state; do not rebuild geometry/lights/material appearance.
- [ ] Reject ambiguous shared data with a clear error before mutation.
- [ ] Verify GREEN and run `historical` + `migrate` phases from the final runtime harness.

## Task 5: Finish offline and optional asset behavior

**Files:** `extension/awful_studio/asset_cache.py`, narrowly scoped asset helpers, dedicated asset tests.

**Produces:** explicit opt-in network fetch with safe cache/provenance and zero-network ordinary operation.

- [ ] Add tests that monkey/block socket/urllib entry points and assert Build, Rebuild and preset cycling make zero network attempts.
- [ ] Add tests for disabled AWFUL network preference, Blender offline mode, disallowed URL, cache traversal/symlink, oversized download, invalid HDR payload, partial-file cleanup and provenance mismatch.
- [ ] Confirm RED where current behavior is incomplete.
- [ ] Implement minimum fixes only in asset/network boundary code.
- [ ] Ensure cache clear only deletes recognized provenance-bearing files inside the AWFUL cache.
- [ ] Verify procedural fallback continues when external assets are unavailable.
- [ ] Verify GREEN and run the offline runtime contract.

## Task 6: Lock Extension lifecycle behavior

**Files:** `extension/awful_studio/__init__.py`, manifest only for verified metadata, lifecycle runtime tests.

**Produces:** install/enable/disable/re-enable/restart-safe Extension registration with no scene build side effects.

- [ ] Test import/register under restricted/factory context.
- [ ] Test install of the final ZIP with `enable_on_install=False`.
- [ ] Test enable does not change ordinary scene snapshot.
- [ ] Test two disable/re-enable cycles remove/restore RNA cleanly and do not accumulate handlers.
- [ ] Test built scene survives disable/re-enable unchanged.
- [ ] Test saved user preferences and new Blender process load the Extension without auto-building.
- [ ] Confirm any missing behavior RED, implement minimum fix, then GREEN.

## Task 7: Verify user-facing core operators

**Files:** operator tests and only operator/lifecycle code required for correctness.

**Produces:** reliable Build, Rebuild, Remove, Migrate, Use Selected Product, Fetch Assets, Validate, optional Post Pipeline.

- [ ] Build from factory scene and validate generated core roles.
- [ ] Rebuild three times and assert bounded managed datablock counts.
- [ ] Mount unmanaged user product, rebuild, and verify transform/content preservation.
- [ ] Remove studio and verify original user world/camera plus nested unmanaged content are restored/preserved.
- [ ] Validate post pipeline remains opt-in and base Build creates no eager volume/heavy stage.
- [ ] Verify optional Fetch Assets cannot run without both online gates.
- [ ] Fix only proven operator defects with RED/GREEN tests.

## Task 8: Establish performance evidence

**Files:** runtime evidence/report code and issue #5 documentation; production changes only if a regression is proven.

**Produces:** repeatable build/rebuild timing and datablock-count baseline.

- [ ] Run at least five clean Build measurements and five Rebuild measurements in the same environment.
- [ ] Record Blender version/platform/device and median wall time.
- [ ] Record managed/object/material/light/image/node-group counts.
- [ ] Compare against the verified 0.0.15/initial 0.0.16 evidence where available.
- [ ] If a material regression exists, open/comment issue #5 before optimizing.
- [ ] Do not add GPU/render benchmarks to the required gate unless the changed path actually depends on them.

## Task 9: Make final-ZIP verification canonical

**Files:** `tools/verify_extension.py`, runtime harness/evidence output.

**Produces:** one command that validates, builds and tests the exact release package in isolated Blender profiles/processes.

- [ ] Add unit tests around deterministic package path/version/evidence handling where code is pure Python.
- [ ] Validate Extension source with Blender CLI.
- [ ] Build via Blender CLI.
- [ ] Validate the generated ZIP itself.
- [ ] Install that ZIP into an isolated user extension repository/profile.
- [ ] Run historical/install/reopen/migrate/lifecycle/offline/ownership phases in isolated processes as appropriate.
- [ ] Persist JSON and log evidence even on the first failed phase.
- [ ] Write `verification.json` only as passed when every required phase passes.
- [ ] Include package SHA-256, Blender version and platform.

Canonical command:

```sh
python tools/verify_extension.py --blender /absolute/path/to/blender
```

## Task 10: Resolve licensing before candidate publication

**Files:** `LICENSE`, `extension/awful_studio/LICENSE`, SPDX headers, `blender_manifest.toml`.

**Produces:** one explicitly owner-approved license state.

- [ ] Stop treating current GPL metadata as automatically approved.
- [ ] Present the owner with the actual licensing choices/constraints separately from engineering fixes.
- [ ] After explicit approval, update root/package LICENSE, manifest and SPDX headers consistently in one dedicated commit.
- [ ] Add a fast test asserting consistency, not a hard-coded license chosen by an agent.

## Task 11: Build the native Extension repository/update path

**Files:** release-specific tool/workflow, `docs/release.md`, generated `dist/repository/` only as CI artifact/deploy output.

**Produces:** Blender-compatible static remote repository and verified native update workflow.

- [ ] Add a test for release tooling inputs/gating where pure Python logic exists.
- [ ] Copy only verified package artifacts into a temporary repository directory.
- [ ] Generate repository metadata with Blender:

```sh
blender --command extension server-generate --repo-dir dist/repository
```

- [ ] Ensure deployment workflow depends on verified candidate evidence and cannot publish from arbitrary failing PR jobs.
- [ ] Publish a non-production test repository/version pair.
- [ ] Add repository in Blender, install lower test version, sync, discover higher version and update natively.
- [ ] Restart/reopen saved AWFUL scene and rerun schema/lifecycle assertions.
- [ ] Record update evidence before enabling production publishing.

## Task 12: Documentation and recovery paths

**Files:** `README.md`, `docs/testing.md`, `docs/release.md`, troubleshooting/install/update docs, `STATE.md`.

**Produces:** docs matching verified behavior, not aspirations.

- [ ] Document install via remote repository and local ZIP testing separately.
- [ ] Document enable/disable, Build/Rebuild/Remove, optional asset download, cache location/clear, update, uninstall and troubleshooting.
- [ ] Document offline behavior and known limitations.
- [ ] Document local/CI test commands and where evidence artifacts live.
- [ ] Remove stale statements that contradict verified runtime state.
- [ ] Update `STATE.md` to the final candidate commit and remaining blockers.

## Task 13: Independent review and integration

**Produces:** a single integration branch/PR with no unresolved critical or major defect.

- [ ] Independently review each domain branch against its base before integration.
- [ ] Reject or rework overlapping/duplicate implementations instead of blindly merging both.
- [ ] Integrate in dependency order: runtime → ownership/lifecycle → migration → assets → release/update → docs.
- [ ] Run full fast suite.
- [ ] Run full Linux Blender 5.2.1 final-ZIP suite.
- [ ] Run full Windows Blender 5.2.1 final-ZIP suite.
- [ ] Run `git diff --check`.
- [ ] Inspect package contents for accidental test/history/private files.
- [ ] Review unresolved GitHub issue comments and PR review threads.
- [ ] Keep PR draft until every required release gate has current evidence.

## Task 14: Alpha 0.0.16 release gate

- [ ] Verify all 18 release gates in the design spec against fresh evidence.
- [ ] Create release candidate package from the exact reviewed commit.
- [ ] Record commit SHA, package SHA-256, Blender version/platform and test artifacts.
- [ ] Publish the production static Extension repository only after required gates pass.
- [ ] Tag/publish Alpha 0.0.16 only after the owner-approved license is present.
- [ ] Reinstall/update from the public repository one final time and run the smoke/lifecycle check.
- [ ] Close #10/#12/#3 only according to their actual acceptance criteria; move deferred feature work to its existing later issues rather than burying it in the release notes.

## Plan self-review

Coverage: runtime, lifecycle, ownership, migration, network/cache, performance, packaging, licensing, update, docs, integration and release are represented. No render gate was accidentally introduced. The plan deliberately avoids a monolith rewrite and avoids adopting Docker/pytest-blender/Flue as release dependencies. Every production code task requires a RED/GREEN cycle; every readiness claim requires exact-package runtime evidence.