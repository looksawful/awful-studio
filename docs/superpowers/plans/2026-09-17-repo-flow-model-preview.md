# Repo Flow + Model Preview Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Protect `main`, simplify release flow, and add a minimal Storybook-based internal 3D asset preview to AWFUL STUDIO.

**Architecture:** Keep `main` as the only permanent branch. Use one isolated `preview/` Node package that derives a canonical asset catalog from existing repository manifests and serves repository GLBs directly; only Scene Lab preview GLBs are generated. A single `merge-gate` check aggregates Extension QA and preview QA.

**Tech Stack:** Python unittest, GitHub Actions, GitHub branch protection, Node 24, Storybook 10.6, `@storybook/html-vite` 10.6, Three.js 0.185.x, Playwright 1.61.x, Blender 5.2.1.

**Specs:** `docs/superpowers/specs/2026-09-17-git-flow-protection-design.md`; `docs/superpowers/specs/2026-09-17-storybook-model-preview-design.md`

## Global Constraints
- `main` is the only long-lived branch.
- Keep this entire implementation on `chore/repo-flow-preview` until merge.
- No permanent preview/dev/release branch.
- Do not modify `looksawful.ru`; only reuse viewer behavior as reference.
- Preview must consume canonical device and Studio Rig GLBs in place without duplicating them.
- Scene preview exports are generated artifacts from canonical v2 `.blend` files.
- Required merge check is one stable `merge-gate` context.
- TDD for behavior changes; configuration changes are verified by contract tests.

---

### Task 1: Repository flow contracts

**Files:**
- Create: `tests/fast/test_repository_flow_contract.py`
- Modify: `.github/workflows/extension-ci.yml`
- Modify: `.github/workflows/release.yml`
- Modify: `tools/verify_extension.py`

**Interfaces:**
- Produces required `merge-gate` check.
- Produces tag-driven release workflow and manifest-derived package identity.

- [ ] Write failing fast tests asserting `merge-gate`, preview dependency, tag-only release trigger, and no hard-coded release title/tag.
- [ ] Run the focused test and confirm RED.
- [ ] Add `merge-gate` and normalize Extension QA branch triggers.
- [ ] Make release workflow use `v*` tags and derive version/package from `blender_manifest.toml`.
- [ ] Make `verify_extension.py` derive expected package name from the manifest.
- [ ] Run focused test, existing release tests, and full fast suite; confirm GREEN.
- [ ] Commit and push.

### Task 2: Canonical preview catalog

**Files:**
- Create: `preview/package.json`
- Create: `preview/tools/catalog-sources.mjs`
- Create: `preview/tools/generate-catalog.mjs`
- Create: `preview/tests/catalog.test.mjs`
- Generate: `preview/generated/asset-catalog.json`

**Interfaces:**
- Produces `asset-catalog.json` entries with `id`, `label`, `group`, `sourceBlend`, `previewGlb`, `version`, optional `lods`, `collision`, and metadata.
- Consumes only canonical device manifests, Studio Rig manifest, and known Scene Lab v2 sources.

- [ ] Write catalog tests first: canonical device versions only, four Studio Rig assets, three scene entries, unique ids, and all non-generated GLB paths exist.
- [ ] Run Node tests and confirm RED because generator/package do not exist.
- [ ] Add minimal package and generator.
- [ ] Generate catalog and run tests to GREEN.
- [ ] Add `--check` mode that rejects stale output.
- [ ] Commit and push.

### Task 3: Scene preview export

**Files:**
- Create: `preview/tools/export-scenes.py`
- Create: `tests/fast/test_scene_preview_export_contract.py`
- Generate: `preview/generated/scenes/white_studio_v2.glb`
- Generate: `preview/generated/scenes/dark_neon_v2.glb`
- Generate: `preview/generated/scenes/loft_daylight_v2.glb`

**Interfaces:**
- Consumes the three canonical `scene_lab/*/generated/*_v2.blend` files.
- Produces deterministic browser-only GLBs at paths referenced by the catalog.

- [ ] Write failing export contract test for Blender 5.2.1 source mapping and output names.
- [ ] Run focused test and confirm RED.
- [ ] Implement one small Blender export script with explicit source/output mapping.
- [ ] Run contract test to GREEN.
- [ ] Execute exports with Blender 5.2.1 and verify all GLBs reopen through Blender import or glTF validation.
- [ ] Regenerate catalog and verify `--check` passes.
- [ ] Commit and push.

### Task 4: Storybook viewer

**Files:**
- Create: `preview/.storybook/main.mjs`
- Create: `preview/.storybook/preview.mjs`
- Create: `preview/src/model-viewer.mjs`
- Create: `preview/src/asset-browser.mjs`
- Create: `preview/stories/catalog.stories.mjs`
- Create: `preview/stories/devices.stories.mjs`
- Create: `preview/stories/studio-equipment.stories.mjs`
- Create: `preview/stories/scenes.stories.mjs`
- Create: `preview/tests/viewer-contract.test.mjs`

**Interfaces:**
- `mountModelViewer(root, asset)` creates and returns `{ dispose(), fit(), reset() }`.
- `mountAssetBrowser(root, entries)` provides asset selection and delegates rendering to the viewer.

- [ ] Write viewer contract tests first for exported API, supported controls, LOD selection behavior, and cleanup contract.
- [ ] Run tests and confirm RED.
- [ ] Implement minimal Three.js viewer with orbit/zoom, fit/reset, camera presets, perspective/ortho, autorotate, fullscreen, background, studio lighting, render modes, animations when present, LOD switching, clipping, axes/bounds/stats.
- [ ] Implement shared asset browser and four thin Storybook stories.
- [ ] Install locked dependencies and run Node tests to GREEN.
- [ ] Build Storybook successfully.
- [ ] Commit and push.

### Task 5: Preview CI and browser smoke

**Files:**
- Create: `preview/tools/smoke.mjs`
- Modify: `preview/package.json`
- Modify: `.github/workflows/extension-ci.yml`

**Interfaces:**
- Preview job runs catalog check, Node tests, Storybook build, Chromium smoke.
- `merge-gate` depends on `fast`, `candidate`, `runtime-windows`, and `preview`.

- [ ] Write smoke script that opens built Storybook and verifies iPhone 17 v30 and a Studio Rig asset produce a canvas and loaded-model marker.
- [ ] Run against a local Storybook server and confirm failures are actionable.
- [ ] Add preview job to Extension QA and include it in `merge-gate` dependencies.
- [ ] Run local preview tests/build/smoke to GREEN.
- [ ] Run full Python fast suite and `git diff --check`.
- [ ] Commit and push.

### Task 6: GitHub settings, PR, merge, cleanup

**Files:**
- Modify repository settings through GitHub API/`gh` only after CI context exists.
- No new long-lived files beyond the documented specs/plan.

**Interfaces:**
- Repository settings: squash only, auto-merge, update-branch, delete head branch after merge.
- Branch protection: PR required, `merge-gate` required, conversations resolved, force-push/deletion disabled.

- [ ] Open one PR from `chore/repo-flow-preview` to `main`.
- [ ] Wait for/check all CI, fix only on the same branch.
- [ ] Apply repository merge settings.
- [ ] Apply `main` protection requiring `merge-gate` without human approval.
- [ ] Enable auto-merge or squash-merge the green PR.
- [ ] Confirm GitHub deletes the branch and `main` is the sole remote branch.
- [ ] Pull `main`, remove the local temporary branch if necessary, and run final fast tests/status checks.
- [ ] Verify branch protection and rules with API reads and report final state.
