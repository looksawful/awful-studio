# Cyclorama + Studio Architecture Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete GitHub #7 and #21 by giving AWFUL STUDIO a metric, styleable cyclorama and independently controllable visible studio architecture without weakening the existing ownership/lifecycle/runtime foundation.

**Architecture:** Keep retained v4 scene construction callable but move the new geometry/policy logic into a focused `studio_geometry.py` adapter, following the existing `photography.py` / `camera_policy.py` install pattern. `legacy.py` keeps only the Blender RNA properties, callbacks and minimal N-panel wiring needed before class registration. Pure policy is testable without Blender; `bpy` behavior is verified against the exact built Extension ZIP on Blender 5.2.1.

**Tech Stack:** Python 3.11+/3.12 tooling, Blender Python API (`bpy`) 5.2.1, Blender Extensions CLI, `unittest`, GitHub Actions Windows/Linux runtime matrix.

**Spec:** `docs/superpowers/specs/2026-09-11-studio-visual-product-completion-design.md`

## Global Constraints

- Blender target: 5.2 LTS; verification runtime: exact Blender 5.2.1.
- Historical Alpha 0.0.15 source remains byte-identical and untouched.
- Import/register/enable/update/restart must not build or mutate a scene.
- Base Build remains offline and performs zero network requests.
- All destructive mutation remains owner- and scene-scoped; semantic roles alone never grant ownership.
- Unmanaged/foreign/shared user data survives Build, Rebuild, Remove and save/reopen.
- Blender-native transforms/material settings remain authoritative outside explicit AWFUL workflow operations.
- No mandatory render gate blocks structural GREEN, but visual-changing behavior must later produce #4 reference evidence.
- No second runtime/bootstrap system is introduced; extend `tools/verify_extension.py`.

---

## File Map

### Create

- `extension/awful_studio/studio_geometry.py` — pure cyclorama policy plus Blender adapter installed into retained legacy scene construction.
- `tests/fast/test_studio_geometry_contract.py` — pure RED/GREEN policy contract.
- `tests/runtime/p0_studio_geometry_contract.py` — exact-ZIP Blender 5.2.1 structural/runtime evidence for #7/#21.

### Modify

- `extension/awful_studio/__init__.py` — import/install studio geometry policy before class registration.
- `extension/awful_studio/core/legacy.py` — RNA properties, callbacks, N-panel controls, and calls into installed geometry policy.
- `tools/verify_extension.py` — add `studio_geometry` packaged runtime phase.
- `docs/superpowers/plans/2026-09-11-alpha-0.0.16-p0-completion.md` — point to this executable slice and record current sequence.

### Do not modify

- `historical/0.0.15/awful_studio_v4_2_gpu_perf.py`.
- License/SPDX state as part of this feature.
- unrelated lighting/camera motion implementation.

---

### Task 1: RED pure cyclorama policy contract

**Files:**
- Create: `tests/fast/test_studio_geometry_contract.py`
- Future implementation: `extension/awful_studio/studio_geometry.py`

**Interfaces:**
- Consumes: current `STUDIO_SPEC` dimensions conceptually, but the pure tests use plain dictionaries so they do not import `bpy`.
- Produces expected interfaces:
  - `cyclorama_distance_bounds(studio_spec: dict, clearance: float = 0.25) -> tuple[float, float]`
  - `clamp_cyclorama_distance(value: float, studio_spec: dict) -> float`
  - `cyclorama_profile(studio_spec: dict, distance: float, segments: int = 64) -> list[tuple[float, float]]`
  - `cyclorama_style(look: str, finish: str) -> dict`
  - `ARCHITECTURE_ROLE_GROUPS: dict[str, tuple[str, ...]]`

- [ ] **Step 1: Write failing distance/profile tests**

```python
class StudioGeometryContractTests(unittest.TestCase):
    def test_default_distance_is_inside_derived_room_bounds(self):
        lo, hi = studio_geometry.cyclorama_distance_bounds(SPEC)
        self.assertLessEqual(lo, 3.0)
        self.assertGreaterEqual(hi, 3.0)

    def test_profile_tangent_matches_requested_metric_distance(self):
        profile = studio_geometry.cyclorama_profile(SPEC, 3.25)
        self.assertIn((3.25, 0.0), profile)

    def test_large_distance_is_clamped_before_background_shell(self):
        _, hi = studio_geometry.cyclorama_distance_bounds(SPEC)
        self.assertEqual(studio_geometry.clamp_cyclorama_distance(100.0, SPEC), hi)
```

- [ ] **Step 2: Write failing look/finish tests**

```python
def test_look_and_finish_are_orthogonal(self):
    white_matte = studio_geometry.cyclorama_style('WHITE', 'MATTE')
    white_glossy = studio_geometry.cyclorama_style('WHITE', 'GLOSSY')
    black_matte = studio_geometry.cyclorama_style('BLACK', 'MATTE')
    self.assertEqual(white_matte['base_color'], white_glossy['base_color'])
    self.assertNotEqual(white_matte['roughness'], white_glossy['roughness'])
    self.assertNotEqual(white_matte['base_color'], black_matte['base_color'])
```

- [ ] **Step 3: Write failing architecture-role tests**

```python
def test_architecture_groups_are_independent(self):
    groups = studio_geometry.ARCHITECTURE_ROLE_GROUPS
    self.assertIn('ROOM_CEILING', groups['CEILING'])
    self.assertIn('ARCH_FLOOR_VISIBLE', groups['FLOOR'])
    self.assertIn('DOOR_LEAF', groups['DOOR'])
    self.assertNotIn('ROOM_FLOOR', groups['FLOOR'])
```

- [ ] **Step 4: Run RED test only**

Run:

```powershell
python -m unittest tests.fast.test_studio_geometry_contract -v
```

Expected: FAIL because `studio_geometry` or the required interfaces do not yet exist. Record the exact failure in #7 and #21.

- [ ] **Step 5: Commit RED only**

```powershell
git add tests/fast/test_studio_geometry_contract.py
git commit -m "test(#7 #21): add RED studio geometry contract"
git push
```

---

### Task 2: GREEN pure cyclorama policy

**Files:**
- Create: `extension/awful_studio/studio_geometry.py`
- Test: `tests/fast/test_studio_geometry_contract.py`

**Interfaces:**
- Produces the pure interfaces declared by Task 1.
- `cyclorama_distance_bounds()` derives the maximum from `background_y - radius - clearance` and derives the minimum from the product safe envelope plus clearance.
- `cyclorama_profile()` preserves the long camera-side floor run and uses the requested metric tangent distance instead of mutating global `STUDIO_SPEC`.

- [ ] **Step 1: Implement pure distance policy**

```python
def cyclorama_distance_bounds(spec, clearance=0.25):
    cyc = spec['cyc']
    envelope = spec['product_envelope']
    minimum = max(0.5, envelope['max_xy'] * 0.5 + clearance)
    maximum = spec['background_y'] - cyc['radius'] - clearance
    if maximum <= minimum:
        raise ValueError('Studio dimensions leave no safe cyclorama placement range')
    return minimum, maximum


def clamp_cyclorama_distance(value, spec):
    lo, hi = cyclorama_distance_bounds(spec)
    return min(max(float(value), lo), hi)
```

- [ ] **Step 2: Implement deterministic profile generation**

The first profile point remains the camera-side `front_y`; the second is `(distance, 0.0)`; the quarter-circle starts there and rises to the existing cyclorama height.

- [ ] **Step 3: Implement style policy**

Use bounded starter values:

```python
CYC_LOOKS = {
    'WHITE': (0.78, 0.78, 0.78, 1.0),
    'BLACK': (0.015, 0.015, 0.015, 1.0),
    'CHROMA_GREEN': (0.02, 0.55, 0.04, 1.0),
}
CYC_FINISH = {'MATTE': 0.82, 'MEDIUM': 0.48, 'GLOSSY': 0.18}
```

- [ ] **Step 4: Implement role groups**

```python
ARCHITECTURE_ROLE_GROUPS = {
    'WALLS': (...room wall roles excluding floor/ceiling...),
    'FLOOR': ('ARCH_FLOOR_VISIBLE',),
    'CEILING': ('ROOM_CEILING',),
    'DOOR': ('DOOR_FRAME', 'DOOR_LEAF'),
    'WINDOW_FRAME': ('WINDOW_FRAME',),
    'WINDOW_GLASS': ('WINDOW_GLASS',),
    'CYC': ('CYC',),
}
```

- [ ] **Step 5: Run targeted fast test**

```powershell
python -m unittest tests.fast.test_studio_geometry_contract -v
```

Expected: PASS.

- [ ] **Step 6: Run broader fast suite**

```powershell
python -m unittest discover -s tests/fast -v
```

Expected: all tests PASS.

- [ ] **Step 7: Commit GREEN policy**

```powershell
git add extension/awful_studio/studio_geometry.py tests/fast/test_studio_geometry_contract.py
git commit -m "feat(#7 #21): add studio geometry policy"
git push
```

---

### Task 3: RED Blender runtime contract for cyclorama and architecture

**Files:**
- Create: `tests/runtime/p0_studio_geometry_contract.py`
- Modify: `tools/verify_extension.py`

**Interfaces:**
- Consumes installed Extension module `bl_ext.awful_test.awful_studio` and the studio built by the existing install phase.
- Produces `studio_geometry.json` evidence and `studio_geometry.log` in verifier output.

- [ ] **Step 1: Add runtime assertions for registered workflow properties**

The installed scene must expose:

```text
cyclorama_distance_m
cyclorama_look
cyclorama_finish
show_cyclorama
show_walls
show_floor
show_ceiling
show_door
show_window_frame
show_window_glass
```

- [ ] **Step 2: Add runtime assertions for required managed roles**

Check `CYC`, `ARCH_FLOOR_VISIBLE`, at least one `DOOR_FRAME`, `DOOR_LEAF`, `ROOM_CEILING`, `WINDOW_FRAME` and `WINDOW_GLASS` under the active owner.

- [ ] **Step 3: Add metric-distance mutation assertion**

```python
before = cyc.matrix_world.copy()
settings.cyclorama_distance_m = target
bpy.context.view_layer.update()
check('cyc tangent moved to metric target', ...)
check('metric update did not rebuild unrelated datablocks', counts_before == counts_after)
```

Also assert camera framing remains valid by reusing `camera_policy.bounds_fit()` with current product metrics and actual `camera.data.view_frame(scene=scene)`.

- [ ] **Step 4: Add look/finish idempotence assertion**

Cycle all nine look/finish combinations and assert the same `MAT_CYC` datablock is reused and node/material counts remain bounded.

- [ ] **Step 5: Add independent visibility assertion**

Toggle each architecture property individually. Assert only the intended owned role group changes viewport/camera visibility. Create an unmanaged object with a colliding `awful_role` and assert it remains unchanged.

- [ ] **Step 6: Add no-coplanar-floor structural assertion**

Compare the visible floor mesh regions/bounds against the cyclorama floor region and reject overlapping coplanar surfaces.

- [ ] **Step 7: Wire verifier phase**

Extend `tools/verify_extension.py`:

```python
('studio_geometry', ROOT/'tests/runtime/p0_studio_geometry_contract.py'),
```

- [ ] **Step 8: Run packaged runtime and observe RED**

```powershell
python .\tools\verify_extension.py --blender "D:\Blender Foundation\Blender 5.2\blender.exe" --output .\dist
```

Expected: existing phases pass until `studio_geometry`, which fails on the first missing #7/#21 requirement. Preserve `dist/studio_geometry.log` and JSON evidence.

- [ ] **Step 9: Commit RED runtime contract**

```powershell
git add tests/runtime/p0_studio_geometry_contract.py tools/verify_extension.py
git commit -m "test(#7 #21): add RED packaged studio runtime contract"
git push
```

---

### Task 4: GREEN metric cyclorama build and state application

**Files:**
- Modify: `extension/awful_studio/studio_geometry.py`
- Modify: `extension/awful_studio/__init__.py`
- Modify: `extension/awful_studio/core/legacy.py`

**Interfaces:**
- `studio_geometry.install(legacy)` replaces `legacy.build_cyclorama` with a closure that uses the current scene settings and pure profile policy.
- `legacy.apply_cyclorama_state(scene)` is installed as the explicit runtime state application function.

- [ ] **Step 1: Install policy before class registration**

In `__init__.py`:

```python
from . import ..., studio_geometry
...
studio_geometry.install(legacy)
```

No scene access occurs during `install()`.

- [ ] **Step 2: Add Blender RNA properties**

Import `FloatProperty` in `legacy.py`, then add:

```python
cyclorama_distance_m: FloatProperty(name='Distance', default=3.0, min=0.5, max=10.0, unit='LENGTH', update=on_cyclorama_update)
cyclorama_look: EnumProperty(name='Look', items=[...], default='WHITE', update=on_cyclorama_update)
cyclorama_finish: EnumProperty(name='Finish', items=[...], default='MATTE', update=on_cyclorama_update)
show_cyclorama: BoolProperty(name='Cyclorama', default=True, update=on_architecture_visibility)
```

The broad RNA numeric range is not the physical authority; the callback clamps against `cyclorama_distance_bounds()` and writes the clamped value back without recursive drift.

- [ ] **Step 3: Build profile from current settings**

The replacement `build_cyclorama()` consumes `scene.awful_studio.cyclorama_distance_m` after clamping and builds the same managed `CYC`/`CYC_MESH` roles using the pure profile.

- [ ] **Step 4: Apply distance without full studio rebuild**

`apply_cyclorama_state(scene)` updates/rebuilds only owned cyclorama mesh geometry/material state and dependent target location. It must not remove/recreate unrelated room, camera, light or user datablocks.

- [ ] **Step 5: Apply look/finish to existing `MAT_CYC`**

Update Principled/fallback material inputs in place. Reuse the material and texture stack if optional maps are present.

- [ ] **Step 6: Rerun targeted fast + packaged runtime**

```powershell
python -m unittest tests.fast.test_studio_geometry_contract -v
python .\tools\verify_extension.py --blender "D:\Blender Foundation\Blender 5.2\blender.exe" --output .\dist
```

Expected: cyclorama-specific checks progress; architecture checks may still fail until Task 5.

- [ ] **Step 7: Commit cyclorama GREEN slice**

```powershell
git add extension/awful_studio/studio_geometry.py extension/awful_studio/__init__.py extension/awful_studio/core/legacy.py
git commit -m "feat(#7): add metric cyclorama controls and finishes"
git push
```

---

### Task 5: GREEN visible floor and real door architecture

**Files:**
- Modify: `extension/awful_studio/studio_geometry.py`
- Modify: `extension/awful_studio/core/legacy.py`

**Interfaces:**
- Replacement `legacy.build_room` builds the existing bounce shell plus managed visible architecture.
- `build_visible_floor(...) -> bpy.types.Object`
- `build_door_system(...) -> tuple[list[bpy.types.Object], bpy.types.Object]`

- [ ] **Step 1: Split the right wall around a real door opening**

Use a documented opening near the camera side, bounded entirely inside the room. Construct wall boxes around the void; do not place a door plane on top of an intact full wall.

- [ ] **Step 2: Create managed frame and leaf**

Use `DOOR_FRAME` for frame members and `DOOR_LEAF` for the leaf. Default leaf may be slightly open for legible studio architecture, but it must have deterministic transform and remain user-editable through native Blender transforms after Build.

- [ ] **Step 3: Create non-overlapping visible floor**

Build `ARCH_FLOOR_VISIBLE` from regions outside the cyclorama floor footprint:

- camera-side strip between room camera wall and cyclorama `front_y`;
- left/right side strips outside cyclorama width;
- no coplanar surface under the cyclorama floor run.

- [ ] **Step 4: Preserve hidden bounce floor**

`ROOM_FLOOR` remains the hidden physical shell below the visible floor/cyclorama and must not be reused as the camera-visible floor.

- [ ] **Step 5: Run runtime contract**

Expected: required floor/door role and structural tests become GREEN; independent visibility checks still wait for Task 6 if not already implemented.

- [ ] **Step 6: Commit architecture geometry**

```powershell
git add extension/awful_studio/studio_geometry.py extension/awful_studio/core/legacy.py
git commit -m "feat(#21): add visible floor and real studio door"
git push
```

---

### Task 6: GREEN independent architecture visibility and N-panel UX

**Files:**
- Modify: `extension/awful_studio/core/legacy.py`
- Modify: `extension/awful_studio/studio_geometry.py`

**Interfaces:**
- `studio_geometry.apply_architecture_visibility(legacy, scene)` applies owner-scoped state.
- Existing `reflective_room_enabled` remains the physical bounce-shell master.

- [ ] **Step 1: Add RNA visibility properties**

```python
show_walls: BoolProperty(name='Walls', default=False, update=on_architecture_visibility)
show_floor: BoolProperty(name='Floor', default=True, update=on_architecture_visibility)
show_ceiling: BoolProperty(name='Ceiling', default=False, update=on_architecture_visibility)
show_door: BoolProperty(name='Door', default=True, update=on_architecture_visibility)
show_window_frame: BoolProperty(name='Window Frame', default=True, update=on_architecture_visibility)
show_window_glass: BoolProperty(name='Window Glass', default=False, update=on_architecture_visibility)
```

Defaults prioritize a clean product-stage view while retaining physically useful hidden room participation.

- [ ] **Step 2: Apply owner-scoped role groups**

Never iterate global role collisions as authorization. Resolve active-owner managed objects/collections, then apply only those roles.

- [ ] **Step 3: Separate camera/viewport visibility from physical ray participation**

For ordinary architecture hide/show:

- change `hide_viewport` for viewport workflow;
- change `visible_camera` for final camera visibility;
- do not set `hide_render=True` merely because camera visibility is off when the surface should continue contributing to diffuse/glossy/shadow rays.

Keep the existing reflective-room master as the separate physical/bounce switch.

- [ ] **Step 4: Add focused `Studio` panel**

Under AWFUL STUDIO N-panel:

```text
Studio
  Cyclorama
    Distance
    Look
    Finish
    Visible
  Architecture
    Walls | Floor | Ceiling
    Door | Window Frame | Window Glass
```

Do not duplicate native transforms or material-node parameters.

- [ ] **Step 5: Run full packaged runtime**

```powershell
python .\tools\verify_extension.py --blender "D:\Blender Foundation\Blender 5.2\blender.exe" --output .\dist
```

Expected: `historical`, `install`, `reopen`, `migrate`, `lighting`, `camera`, and `studio_geometry` all PASS locally.

- [ ] **Step 6: Run all fast tests and diff checks**

```powershell
python -m unittest discover -s tests/fast -v
git diff --check feature/extension-foundation...HEAD
```

- [ ] **Step 7: Commit visibility/UI GREEN**

```powershell
git add extension/awful_studio/core/legacy.py extension/awful_studio/studio_geometry.py
git commit -m "feat(#7 #21): add studio architecture visibility controls"
git push
```

---

### Task 7: Regression, ownership and performance evidence

**Files:**
- Modify if needed: `tests/runtime/p0_studio_geometry_contract.py`
- Evidence only: `dist/*.json`, `dist/*.log` remain build artifacts and are not committed unless existing project policy explicitly requires it.

**Interfaces:**
- Consumes exact candidate ZIP created by `tools/verify_extension.py`.
- Produces issue evidence for #7/#21.

- [ ] **Step 1: Verify unmanaged role collision survives**

Create unmanaged object/material with `awful_role` matching an architecture role and prove toggles/rebuild do not mutate it.

- [ ] **Step 2: Verify multi-scene safety**

Use or extend the existing multi-scene fixture so foreign-scene architecture-like objects remain untouched.

- [ ] **Step 3: Verify repeated state is bounded**

Repeated distance, look, finish and visibility applications must not grow object/material/mesh/node/action counts.

- [ ] **Step 4: Record build/rebuild timings**

Compare with the current 0.0.16 foundation runtime evidence. Any material unapproved regression is a defect before merge.

- [ ] **Step 5: Run fresh complete local verifier**

```powershell
Remove-Item .\dist -Recurse -Force -ErrorAction SilentlyContinue
python .\tools\verify_extension.py --blender "D:\Blender Foundation\Blender 5.2\blender.exe" --output .\dist
Get-Content .\dist\verification.json
```

Expected: `status` = `passed` and `phases` includes `studio_geometry`.

---

### Task 8: GitHub CI, documentation and merge gate

**Files:**
- Modify: `docs/superpowers/plans/2026-09-11-alpha-0.0.16-p0-completion.md`
- Update GitHub #7 and #21 evidence comments.
- Update corresponding Notion backlog rows after verification.

**Interfaces:**
- Consumes local verified commit SHA.
- Produces reviewable PR into `feature/extension-foundation`.

- [ ] **Step 1: Push final candidate and open PR**

PR title:

```text
0.0.16 P0: metric cyclorama and visible studio architecture (#7 #21)
```

- [ ] **Step 2: Require CI fast + Windows runtime + Ubuntu runtime**

All jobs must test the same PR head and exact built ZIP. Do not accept source-only evidence.

- [ ] **Step 3: Inspect failed job logs directly if any job is red**

Do not weaken assertions or turn runtime failure into a warning.

- [ ] **Step 4: Update issue evidence**

Record:

- RED commit/run;
- root cause/current gap;
- production commits;
- local Blender 5.2.1 verifier result;
- Windows/Ubuntu CI run IDs;
- exact candidate SHA;
- known visual limitations deferred to #4.

- [ ] **Step 5: Update Notion statuses**

Only after packaged Windows/Linux runtime is green:

- Metric cyclorama distance controls → Done / Done;
- Cyclorama appearance and visibility presets → Done / Done structurally, with #4 visual evidence referenced separately;
- Visible studio floor, door and architecture visibility controls → Done / Done.

- [ ] **Step 6: Merge only after fresh verification evidence**

Squash into `feature/extension-foundation`. Close #7/#21 as completed. Update `STATE.md` only if this changes project-level immediate state, not merely because a feature landed.

---

## Next plans after #7/#21

Do not implement these in the same branch. Create fresh isolated branches and dedicated executable plans from the accepted design spec:

1. `#9` Natural Light v2: Pure HDRI / Physical Sky / managed Sun / zero-energy portal / network-clean switching.
2. `#8` Playback: Once / Loop / Ping-Pong independently for Product and Camera.
3. `#23` Asset provenance / Extensions compatibility.
4. `#3/#5/#10/#12` runtime/performance/release reconciliation and native Extension update path.
5. `#4` deterministic visual evidence for completed visual slices.
6. 0.0.17 Product Quality: Bottle / Jar / Box / Can / Phone / Tablet plus starter materials.

Each later plan must preserve the same RED → GREEN → packaged Blender 5.2.1 → Windows/Linux CI → evidence → merge sequence.
