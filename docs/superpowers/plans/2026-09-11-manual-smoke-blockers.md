# Manual Smoke Blockers Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Resolve the six Blender 5.2.1 manual-smoke blockers for AWFUL STUDIO 0.0.17 and produce a new exact candidate that is safe to re-smoke.

**Architecture:** Keep the accepted Extension architecture intact. Add pure policy helpers where behavior can be defined without Blender, then prove the Blender adapter/runtime behavior with the existing packaged-runtime harness. Do not mix speculative performance changes with functional fixes; profiling precedes optimization. Each blocker gets its own RED → GREEN → REFACTOR cycle and reviewable commit.

**Tech Stack:** Python 3 / Blender 5.2.1 `bpy`, `unittest`, existing `tests/runtime` packaged Extension harness, Blender native Extension ZIP/repository CI.

**Spec:** GitHub issue #39.

## Global Constraints

- Target Blender 5.2 LTS; exact qualification runtime Blender 5.2.1.
- Import/register/enable/restart remain scene-clean.
- Build/Rebuild/Remove remain explicit and ownership-scoped.
- Base studio operation remains offline; remote assets require explicit user + Blender online permission.
- No hidden GPU backend selection or probing during Build/Rebuild.
- No render/GPU CI test is added without explicit opt-in.
- Historical `historical/0.0.15/awful_studio_v4_2_gpu_perf.py` remains byte-identical.
- Product/Camera animation data stays independent and user-authored unmanaged data is never rewritten.
- Do not tag/publish 0.0.17 until a new exact candidate passes the manual smoke.

---

### Task 1: Reproduce and fix product/support-surface placement

**Files:**
- Modify: `extension/awful_studio/product_quality.py`
- Modify only if the root cause proves shared mounting policy is wrong: `extension/awful_studio/core/legacy.py`
- Modify: `tests/fast/test_product_quality_contract.py`
- Modify: `tests/runtime/product_quality_contract.py`

**Interfaces:**
- Consumes: existing `MOCKUP_SPECS`, `legacy.world_bbox()`, `legacy.mount_product()`, `STUDIO_SPEC['pedestal']['height']`.
- Produces: pure `support_surface_offset(bottom_z: float, support_z: float) -> float` or equivalent small policy helper; runtime guarantee that a non-floating mockup bottom equals the pedestal top within tolerance.

- [ ] **Step 1: Add a RED pure support-surface test**

```python
def test_support_surface_offset_places_bottom_on_support():
    import product_quality

    self.assertAlmostEqual(product_quality.support_surface_offset(0.125, 0.500), 0.375)
    self.assertAlmostEqual(product_quality.support_surface_offset(0.500, 0.500), 0.0)
```

- [ ] **Step 2: Run the fast test and verify RED**

Run:

```sh
python -m unittest tests.fast.test_product_quality_contract.ProductQualityContractTests.test_support_surface_offset_places_bottom_on_support -v
```

Expected: FAIL because the support-surface policy does not exist yet.

- [ ] **Step 3: Add a RED Blender runtime assertion for every built-in mockup**

In `tests/runtime/product_quality_contract.py`, after each mockup is generated and mounted, derive the evaluated world bounding box and assert:

```python
pedestal_top = float(ext.legacy.STUDIO_SPEC['pedestal']['height'])
mn, mx = ext.legacy.world_bbox([root] + ext.legacy.descendants(root))
check(
    f'{key} bottom contacts pedestal',
    abs(float(mn.z) - pedestal_top) <= 1e-4,
)
```

Also repeat after Auto Fit and after Rebuild.

- [ ] **Step 4: Run packaged Blender runtime and verify RED**

Use the existing exact-ZIP runtime path. Expected: at least the observed diagnostic/mockup placement path fails the support-contact assertion. If it does not fail, record the exact observed object/preset/frame from the manual screenshot before changing production code; do not guess.

- [ ] **Step 5: Implement the smallest root-cause fix**

Pure helper:

```python
def support_surface_offset(bottom_z: float, support_z: float) -> float:
    return float(support_z) - float(bottom_z)
```

Apply the offset at the single coordinate-space boundary that owns product grounding. Do not patch camera framing and do not introduce a second product rig. Preserve special clearance only for motions that actually rotate through the support plane (`SPIN_X`, `SPIN_Y`, `TUMBLE`); `STATIC`, `SPIN_Z` and ordinary generated mockups must begin grounded.

- [ ] **Step 6: GREEN fast + packaged runtime**

Run fast suite and exact packaged Blender runtime. Verify all six built-in mockups, Auto Fit and Rebuild remain bounded and grounded.

- [ ] **Step 7: Commit**

```sh
git add extension/awful_studio/product_quality.py extension/awful_studio/core/legacy.py tests/fast/test_product_quality_contract.py tests/runtime/product_quality_contract.py
git commit -m "fix(product): ground mockups on support surface"
```

---

### Task 2: Synchronize Timeline preview range with Product/Camera playback

**Files:**
- Modify: `extension/awful_studio/playback_policy.py`
- Modify: `tests/fast/test_playback_policy_contract.py`
- Modify: `tests/runtime/p0_playback_contract.py`

**Interfaces:**
- Produces: `preview_span(mode: str, keyed_start: int, keyed_end: int) -> tuple[int, int]` and `combined_preview_span(spans: list[tuple[int, int]]) -> tuple[int, int] | None`.
- Blender adapter writes only `scene.use_preview_range`, `scene.frame_preview_start`, `scene.frame_preview_end`; it does not rewrite keyframes or the user's global render frame range.

- [ ] **Step 1: RED pure tests for playback preview span**

```python
def test_preview_span_matches_playback_semantics(self):
    import playback_policy

    self.assertEqual(playback_policy.preview_span('ONCE', 1, 241), (1, 241))
    self.assertEqual(playback_policy.preview_span('LOOP', 1, 241), (1, 481))
    self.assertEqual(playback_policy.preview_span('PING_PONG', 1, 241), (1, 481))
```

The repeat modes show two keyed spans so the user can see the repeat/return boundary instead of hunting for it manually.

- [ ] **Step 2: RED pure test for independent Product + Camera union**

```python
def test_combined_preview_span_uses_union(self):
    import playback_policy

    self.assertEqual(
        playback_policy.combined_preview_span([(1, 481), (20, 260)]),
        (1, 481),
    )
```

- [ ] **Step 3: Verify RED**

Run the two focused fast tests. They must fail because the helpers do not exist.

- [ ] **Step 4: RED Blender runtime**

After Product and Camera actions are applied, assert the preview range is enabled and covers the derived union. Reapply playback modes and assert the range does not drift or grow repeatedly.

- [ ] **Step 5: Minimal implementation**

```python
def preview_span(mode, keyed_start, keyed_end):
    mode_policy(mode)
    start = int(keyed_start)
    end = int(keyed_end)
    if end < start:
        start, end = end, start
    if mode in {'LOOP', 'PING_PONG'}:
        end = start + (end - start) * 2
    return start, end


def combined_preview_span(spans):
    spans = [span for span in spans if span is not None]
    if not spans:
        return None
    return min(s[0] for s in spans), max(s[1] for s in spans)
```

Add one adapter function that derives actual F-Curve keyframe bounds from `_actions()` and updates only Blender's preview range after Product/Camera motion or playback changes.

- [ ] **Step 6: GREEN and idempotency verification**

Fast suite + `tests/runtime/p0_playback_contract.py` must pass. Confirm Cycles modifiers remain at most one per F-Curve.

- [ ] **Step 7: Commit**

```sh
git add extension/awful_studio/playback_policy.py tests/fast/test_playback_policy_contract.py tests/runtime/p0_playback_contract.py
git commit -m "fix(playback): sync timeline preview with motion span"
```

---

### Task 3: Decouple camera-visible environment brightness from lighting energy

**Files:**
- Modify: `extension/awful_studio/natural_light.py`
- Modify as required for world-node construction: `extension/awful_studio/core/legacy.py`
- Modify: `tests/fast/test_natural_light_contract.py`
- Modify: `tests/runtime/p0_natural_light_contract.py`

**Interfaces:**
- Produces: pure environment strength policy returning separate `lighting_strength` and `camera_strength`.
- Blender graph must use distinct Background shaders for non-camera illumination and camera rays.

- [ ] **Step 1: RED pure policy test**

```python
def test_camera_background_strength_is_independent_from_lighting_strength(self):
    import natural_light

    policy = natural_light.strength_policy('FISH_HOEK')
    self.assertIn('lighting_strength', policy)
    self.assertIn('camera_strength', policy)
    self.assertNotEqual(id(policy['lighting_strength']), id(policy['camera_strength']))
```

Also assert sane positive bounded defaults, e.g. `0.0 <= lighting_strength <= 1.0` and `0.0 <= camera_strength <= 2.0`. The exact calibration values are selected only after reproducing the overexposure in Blender; do not hide calibration inside the test.

- [ ] **Step 2: RED Blender node-graph contract**

Assert two different managed `ShaderNodeBackground` nodes feed camera vs non-camera branches when natural lighting is active. Toggle `show_environment_background` and assert the non-camera lighting Background strength is unchanged.

- [ ] **Step 3: Verify RED**

Current graph routes the same active Background to both paths, so the graph-identity assertion must fail.

- [ ] **Step 4: Implement separate managed camera Background nodes**

Use a shared Environment/Sky texture, but distinct Background shaders:

```text
Environment/Sky Color -> AWFUL_LIGHTING_BG_<preset> -> non-camera branch
Environment/Sky Color -> AWFUL_CAMERA_BG_<preset>   -> camera-ray branch
```

`show_environment_background=False` routes camera rays to black only; it must not modify non-camera illumination.

- [ ] **Step 5: Calibrate hybrid World + Studio only after reproduction**

Capture before/after numeric node strengths and keep the change preset-specific. Do not lower studio lights globally and do not add exposure compensation that changes final render color management.

- [ ] **Step 6: GREEN fast + runtime**

Verify Pure HDRI, Physical Sky, managed Sun, portal policy and offline semantics remain intact.

- [ ] **Step 7: Commit**

```sh
git add extension/awful_studio/natural_light.py extension/awful_studio/core/legacy.py tests/fast/test_natural_light_contract.py tests/runtime/p0_natural_light_contract.py
git commit -m "fix(environment): decouple camera background from world lighting"
```

---

### Task 4: Make HDRI download reliable and actionable

**Files:**
- Modify: `extension/awful_studio/asset_cache.py`
- Modify: `extension/awful_studio/core/legacy.py`
- Modify: `extension/awful_studio/__init__.py` only if a small status property/operator is needed
- Modify: `tests/fast/test_asset_provenance_contract.py`
- Create: `tests/fast/test_asset_cache_policy.py`
- Modify: `tests/runtime/p0_natural_light_contract.py`

**Interfaces:**
- Preserve provenance allowlist and explicit network permission.
- Produce actionable status: selected asset, cache path, result, exact error.

- [ ] **Step 1: Reproduce the actual manual failure before changing redirect policy**

Record `asset_cache.last_error()`, selected preset, `bpy.app.online_access`, AWFUL network preference, requested URL and final HTTP URL. If the failure is permission-only, fix UX rather than weakening provenance checks.

- [ ] **Step 2: RED pure tests for allowed download result policy**

Extract URL acceptance into a pure helper:

```python
def test_reviewed_download_url_accepts_exact_url(self):
    import asset_cache
    expected = 'https://dl.polyhaven.org/file/a.hdr'
    self.assertTrue(asset_cache.download_url_allowed(expected, expected, 'dl.polyhaven.org'))
```

If evidence shows Poly Haven performs a legitimate redirect, add the exact reviewed host/path rule as a second RED test. Do not accept arbitrary redirects.

- [ ] **Step 3: RED failure-state test**

Test that a failed fetch leaves an error sidecar/status and never marks the asset `ready`.

- [ ] **Step 4: RED Blender runtime for missing HDRI**

With network denied and cache empty, selecting an HDRI must keep the world source safe (black/procedural unavailable state) and must not assign a missing image that renders magenta.

- [ ] **Step 5: Minimal implementation**

Keep download atomic `.part -> os.replace`, SHA validation and provenance destination checks. Surface exact failure text through the existing operator and AWFUL panel; change redirect handling only if the captured request proves it is the root cause.

Also update the stale user-agent version from `AWFUL-Studio/0.0.16` to `AWFUL-Studio/0.0.17` as part of this focused asset path once the tests cover it.

- [ ] **Step 6: GREEN tests**

Fast cache/provenance tests + packaged natural-light runtime. No ordinary Build/Rebuild network attempt is allowed.

- [ ] **Step 7: Commit**

```sh
git add extension/awful_studio/asset_cache.py extension/awful_studio/core/legacy.py extension/awful_studio/__init__.py tests/fast/test_asset_cache_policy.py tests/fast/test_asset_provenance_contract.py tests/runtime/p0_natural_light_contract.py
git commit -m "fix(assets): make HDRI fetch state reliable and visible"
```

---

### Task 5: Make Build Post Pipeline verifiable, idempotent and understandable

**Files:**
- Modify: `extension/awful_studio/core/legacy.py`
- Modify: `extension/awful_studio/__init__.py` only if operator/status responsibility is moved out of legacy
- Create: `tests/runtime/post_pipeline_contract.py`
- Modify: `tests/runtime/p0_suite.py`
- Create: `tests/fast/test_post_pipeline_source_contract.py` if a pure capability/result policy is extracted

**Interfaces:**
- Existing operator: `awful.build_post_pipeline_v4`.
- Existing scene state: `awful_post_pipeline_enabled`.
- Required result: managed Light Groups + passes + compositor state, or explicit capability/error report.

- [ ] **Step 1: RED runtime test for actual operator output**

```python
result = bpy.ops.awful.build_post_pipeline_v4()
check('post pipeline operator finished', result == {'FINISHED'})
check('post pipeline state enabled', bool(scene.get(ext.legacy.POST_PIPELINE_KEY)))
```

Then assert the concrete nodes/passes/groups expected for Blender 5.2.

- [ ] **Step 2: RED idempotency test**

Capture relevant datablock/node/group counts, invoke the operator a second time, and assert no accumulation.

- [ ] **Step 3: RED capability/no-op test**

If a required Blender API capability is absent, the operator must return `CANCELLED` with an actionable message rather than silently returning success after helper no-ops.

- [ ] **Step 4: Implement result verification at the operator boundary**

After `setup_light_groups`, `setup_passes`, `build_compositor`, verify the created state before setting `POST_PIPELINE_KEY=True`. Keep the pipeline optional and keep normal Build/Rebuild resetting it to false.

Change UI label/description to make intent explicit, e.g. `Build Optional Post / Compositor Pipeline`; do not overload `Build Studio` semantics.

- [ ] **Step 5: GREEN runtime and repeated-build checks**

Add the focused contract to `p0_suite.py`. No renders are required.

- [ ] **Step 6: Commit**

```sh
git add extension/awful_studio/core/legacy.py extension/awful_studio/__init__.py tests/runtime/post_pipeline_contract.py tests/runtime/p0_suite.py tests/fast/test_post_pipeline_source_contract.py
git commit -m "fix(post): verify optional pipeline build and status"
```

---

### Task 6: Profile rendered viewport before changing performance policy

**Files:**
- Create: `tests/runtime/viewport_diagnostics.py`
- Modify: `tests/runtime/p0_suite.py` only for non-render diagnostic collection if appropriate
- Modify after root cause is proven: `extension/awful_studio/runtime_performance.py` and/or `extension/awful_studio/core/legacy.py`
- Add a focused fast test only for the proven policy change.

**Interfaces:**
- Diagnostics must not render and must not enumerate/change GPU backends.
- Report JSON fields: engine, `scene.cycles.device`, preview samples, adaptive threshold, denoise, Light Tree, preview pixel size, object/mesh/light/image counts, loaded HDRI dimensions/estimated bytes, depsgraph update timings.

- [ ] **Step 1: Add non-render diagnostic fixture**

Example report fragment:

```python
report['viewport_policy'] = {
    'engine': scene.render.engine,
    'cycles_device': scene.cycles.device,
    'preview_samples': scene.cycles.preview_samples,
    'preview_adaptive_threshold': scene.cycles.preview_adaptive_threshold,
    'use_denoising': scene.cycles.use_denoising,
    'use_light_tree': scene.cycles.use_light_tree,
    'preview_pixel_size': scene.render.preview_pixel_size,
    'lights': len(bpy.data.lights),
    'images': len(bpy.data.images),
}
```

- [ ] **Step 2: Gather baseline from exact packaged runtime**

This does not prove interactive FPS, but it proves what AWFUL configures and catches accidental scene complexity/resource growth.

- [ ] **Step 3: Manual profile the same smoke scene in rendered viewport**

Record Blender status-bar device, viewport sample convergence time, VRAM use and behavior with one variable changed at a time: denoise, Light Tree, World, studio lights, loaded HDRI. No production code change yet.

- [ ] **Step 4: State one root-cause hypothesis**

Example form only: `Rendered viewport stalls because X; disabling X changes convergence from A to B while other variables remain fixed.` Do not implement until this evidence exists.

- [ ] **Step 5: Add RED test for the proven policy change**

If the culprit is an AWFUL-owned configuration value, encode only that budget. If Blender is simply using CPU because of the user's native device setting, do not make AWFUL override it; document the device state instead.

- [ ] **Step 6: Minimal performance fix, GREEN, no final-render regression**

Final render samples/settings remain untouched unless the observed root cause explicitly concerns them.

- [ ] **Step 7: Commit**

```sh
git add tests/runtime/viewport_diagnostics.py tests/runtime/p0_suite.py extension/awful_studio/runtime_performance.py extension/awful_studio/core/legacy.py tests/fast
git commit -m "perf(viewport): fix measured interactive bottleneck"
```

---

### Task 7: Full candidate verification and repeat smoke handoff

**Files:**
- Modify only evidence/docs if needed: `STATE.md`, `docs/releases/0.0.17.md`
- No version bump unless release policy explicitly decides the fixes require one before publication.

- [ ] **Step 1: Run full fast suite**

```sh
python -m unittest discover -s tests/fast -v
git diff --check
```

Expected: GREEN.

- [ ] **Step 2: Build one canonical exact ZIP in cloud CI**

Expected package: `awful_studio-0.0.17.zip`.

- [ ] **Step 3: Verify that exact same ZIP on Ubuntu and Windows Blender 5.2.1**

Required: packaged runtime + native static Extension repository install GREEN on both platforms.

- [ ] **Step 4: Record exact commit, workflow, artifact ID and contained ZIP SHA-256 in issue #39**

- [ ] **Step 5: Repeat the manual UI smoke against that exact package**

Required manual checks include all six issue findings. Do not use the previous candidate.

- [ ] **Step 6: Only after manual smoke passes, close #39 and resume tag/release/publication**
