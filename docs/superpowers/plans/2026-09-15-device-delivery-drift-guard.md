# Device Delivery Drift Guard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the iPhone 17 v20 Blender source, web GLB, manifest, validation evidence, browser QA and AWFUL STUDIO plugin bundle reproducible from one source revision and reject stale generated artifacts.

**Architecture:** Keep Blender generation authoritative. A delivery builder fingerprints generator inputs, runs Blender to produce the canonical `.blend`, exports GLB with metadata in `extras`, validates structure/triangles/nodes, runs Khronos validation and browser QA, then writes a manifest containing all source and artifact hashes. Fast tests verify committed artifacts match the manifest and plugin loader revision.

**Tech Stack:** Python 3.12, Blender 5.2.1 LTS, glTF 2.0/GLB, Khronos glTF Validator, Node/Three.js headless browser QA, GitHub Actions.

**Spec:** GitHub issue #70 and plugin integration issue #53.

## Global Constraints
- Blender target is exact official 5.2.1 LTS.
- No implicit decimation or simplification.
- `LOW_DRAFT` must remain distinct from approved LOW/DELIVERY.
- Khronos validation must report 0 errors / 0 warnings.
- Critical camera/logo/screen nodes and metric envelope must survive GLB export.
- Plugin bundle must reference the same source revision recorded by delivery manifest.

---

### Task 1: Source fingerprint and drift contract
**Files:** create `tests/fast/test_device_delivery_contract.py`; create `tools/device_delivery_contract.py`.
**Produces:** deterministic source fingerprint, manifest parser, stale/wrong-stage rejection helpers.
- [ ] Write failing tests for v20 revision, stage, generator fingerprint, artifact hashes and plugin revision agreement.
- [ ] Run focused test and confirm RED against current v15 delivery/plugin state.
- [ ] Implement minimal fingerprint/manifest helpers.
- [ ] Run focused test and keep failures only for missing v20 delivery artifacts.

### Task 2: Canonical v20 delivery builder
**Files:** create `assets/device_mockups/iphone_17/build_delivery_v20.py`; create `assets/device_mockups/iphone_17/export_runtime_v20.py`; modify `generate_low_v20.py` only if metadata required by the contract is missing.
**Produces:** `runtime/v20/iphone_17_v20_delivery.blend`, `iphone_17_v20_web.glb`, `iphone_17_v20.asset.json`, validation/evidence hashes.
- [ ] Write failing contract assertions for required manifest/extras fields.
- [ ] Generate v20 from source with Blender 5.2.1 into a temporary output tree.
- [ ] Export source-derived GLB without simplification and embed asset/source revision/stage in root extras.
- [ ] Write artifact SHA-256, generator/source fingerprint, object/material/triangle/node metrics to manifest.
- [ ] Re-run builder and prove deterministic structural manifest values.

### Task 3: GLB round-trip and browser QA
**Files:** create `tools/qa_device_glb.py`; create `tools/qa_device_threejs.mjs`; create browser QA evidence under `assets/device_mockups/iphone_17/runtime/v20/browser_qa/`.
**Produces:** machine-readable QA report plus front/back/three-quarter/camera/logo screenshots.
- [ ] Assert required semantic nodes, dimensions and triangle budget from GLB JSON/buffers.
- [ ] Run Khronos validator and require 0 errors / 0 warnings.
- [ ] Load GLB through Three.js `GLTFLoader` and assert expected nodes/bounds.
- [ ] Capture deterministic headless browser views for front/back/three-quarter/camera/logo evidence.
- [ ] Record browser/runtime versions and evidence file hashes in QA report.

### Task 4: Plugin bundle v20 and stale rejection
**Files:** modify `extension/awful_studio/device_asset_loader.py`; replace packaged iPhone v15 `.blend` with v20; update `extension/awful_studio/assets/devices/PREVIEWS.md`; extend runtime/fast tests.
**Produces:** plugin bundle points at v20 and validates revision/stage before loading.
- [ ] Write failing tests that reject mismatched source revision and wrong delivery stage.
- [ ] Package v20 device-only `.blend` with no diagnostic cameras/lights.
- [ ] Update loader manifest to v20 fingerprint and enforce metadata match.
- [ ] Run focused tests, then full fast suite and exact-package Blender runtime.

### Task 5: CI and integration
**Files:** modify `.github/workflows/extension-qa.yml` only if the new fast guard is not already exercised automatically; update #70/#53 after merge.
**Produces:** CI fails on stale generated artifacts and current main is independently verified after merge.
- [ ] Confirm fast CI executes the drift-guard test on pull requests.
- [ ] Run `python -m unittest discover -s tests/fast -v`, Python compile and `git diff --check`.
- [ ] Run intentional local exact-package and native repository verification with Blender 5.2.1.
- [ ] Open PR, wait for fast + Ubuntu candidate + Windows runtime success, squash merge.
- [ ] Reset isolated audit worktree to merged `origin/main` and re-run fast + exact-package verification.
- [ ] Update #70 and #53 with completed vs remaining contract items and close only requirements actually satisfied.

## Self-review
- Spec coverage: source fingerprint, provenance, GLB extras, drift CI, node/dimension/triangle QA, explicit no-simplification profile, Khronos validator, browser evidence and plugin stale-stage enforcement are each mapped above.
- No placeholders remain; each task has an executable verification gate.
- Interfaces use `asset_id`, `stage`, `variant`, `source_revision` and SHA-256 consistently across generator, manifest, GLB and plugin loader.
