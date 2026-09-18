# AWFUL STUDIO Production Pass Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Turn the existing AWFUL STUDIO 1.x Blender Extension into a polished task-oriented product workflow while preserving the stable ownership/lifecycle architecture.

**Architecture:** Add thin workflow/status/diagnostic adapters around existing Blender-native systems instead of rewriting `core/legacy.py`. Product, lighting, camera, environment and output continue to use existing authoritative scene state; new UI code only orchestrates those systems and exposes clearer status/actions.

**Tech Stack:** Blender 5.2.1 Python API, Python 3.11/3.12 policy tests, Blender Extension packaging, unittest, existing AWFUL runtime verifier.

**Spec:** `docs/superpowers/specs/2026-09-18-awful-studio-production-pass-design.md`

## Global Constraints

- Work only in `agent/production-pass`; do not create additional feature branches.
- Do not merge to dev/main or publish a release without explicit owner approval.
- Blender + AWFUL STUDIO is the only source of truth; Unreal is viewer/QA only.
- Target Blender 5.2 LTS; qualification runtime is Blender 5.2.1.
- Import/register/enable/restart must not mutate a scene.
- Base Build and ordinary preset switching remain offline.
- Unmanaged user data must survive Build/Rebuild/Remove/save/reopen.
- Do not silently change the user's Cycles device/backend.
- TDD is mandatory for production-code changes.
- Keep new workflow code out of the 125k legacy module unless correctness requires a surgical fix.

---

### Task 1: Task-oriented workflow status and panel shell

**Files:**
- Create: `extension/awful_studio/workflow_ui.py`
- Modify: `extension/awful_studio/__init__.py`
- Test: `tests/fast/test_workflow_ui_contract.py`

**Interfaces:**
- Produces: `workflow_snapshot(legacy, scene) -> dict[str, object]`
- Produces: `status_lines(snapshot: Mapping[str, object]) -> tuple[str, ...]`
- Produces: `install(legacy) -> None`
- Later tasks reuse the same snapshot keys; no second persistent scene-state model is introduced.

- [x] **Step 1: Write the failing fast contract**

```python
def test_workflow_module_is_scene_clean_and_declares_order():
    module = load_policy()
    assert module.PANEL_ORDER == (
        'STUDIO', 'PRODUCT', 'LIGHTING', 'CAMERA',
        'ENVIRONMENT', 'OUTPUT', 'DIAGNOSTICS',
    )
    source = MODULE_PATH.read_text(encoding='utf-8')
    assert 'import bpy' not in source
```

- [x] **Step 2: Run the targeted test and observe RED**

Run: `python -m unittest tests.fast.test_workflow_ui_contract -v`

Expected: FAIL because `workflow_ui.py` does not exist.

- [x] **Step 3: Implement the minimal workflow adapter**

```python
PANEL_ORDER = (
    'STUDIO', 'PRODUCT', 'LIGHTING', 'CAMERA',
    'ENVIRONMENT', 'OUTPUT', 'DIAGNOSTICS',
)

def workflow_snapshot(legacy, scene):
    settings = scene.awful_studio
    return {
        'built': legacy.REG.object('CYC') is not None,
        'product': getattr(settings, 'product_mockup', 'NONE'),
        'lighting': settings.studio_light_preset,
        'camera': settings.camera_motion,
        'environment': settings.world_preset,
        'preview': getattr(settings, 'preview_mode', 'FAST'),
        'last_error': getattr(scene.awful_state, 'last_error', ''),
    }

def status_lines(snapshot):
    state = 'Ready' if snapshot['built'] and not snapshot['last_error'] else (
        'Needs attention' if snapshot['last_error'] else 'Not built')
    return (
        f"Studio: {state}",
        f"Product: {snapshot['product']}",
        f"Lighting: {snapshot['lighting']}",
    )
```

`install(legacy)` patches the existing main panel draw function, adds Output and Diagnostics child panels through the established `legacy.CLASSES += (...,)` pattern, and never touches a scene during import/register.

- [x] **Step 4: Wire install before class registration**

Add `workflow_ui` to the Extension imports and call `workflow_ui.install(legacy)` after the existing policy installers and before `CLASSES = ...`.

- [x] **Step 5: Run targeted + fast tests**

Run:
```powershell
python -m unittest tests.fast.test_workflow_ui_contract -v
python -m unittest discover -s tests/fast -q
```

Expected: targeted PASS; full fast suite PASS.

- [x] **Step 6: Commit**

```bash
git add extension/awful_studio/workflow_ui.py extension/awful_studio/__init__.py tests/fast/test_workflow_ui_contract.py
git commit -m "feat(ui): add production workflow shell"
```

### Task 2: Actionable diagnostics and validation result

**Files:**
- Create: `extension/awful_studio/studio_diagnostics.py`
- Modify: `extension/awful_studio/workflow_ui.py`
- Test: `tests/fast/test_studio_diagnostics_contract.py`
- Modify runtime test: `tests/runtime/p0_suite.py`

**Interfaces:**
- Produces: `Diagnostic(code: str, section: str, level: str, message: str)`
- Produces: `summarize(diagnostics) -> dict[str, int]`
- Produces: `collect(legacy, scene, runtime_performance) -> tuple[Diagnostic, ...]`
- `workflow_ui` renders these results and exposes an explicit Validate/Doctor operator.

- [x] **Step 1: Write RED tests for severity and grouping**

```python
def test_summary_counts_levels():
    items = (
        Diagnostic('studio.ready', 'Studio', 'OK', 'Ready'),
        Diagnostic('asset.optional', 'Assets', 'WARNING', 'Optional HDRI missing'),
        Diagnostic('camera.missing', 'Camera', 'ERROR', 'Camera missing'),
    )
    assert summarize(items) == {'OK': 1, 'WARNING': 1, 'ERROR': 1}
```

Also require source to remain importable without Blender by avoiding module-level `import bpy`.

- [x] **Step 2: Run targeted RED**

Run: `python -m unittest tests.fast.test_studio_diagnostics_contract -v`

Expected: FAIL because the module is missing.

- [x] **Step 3: Implement diagnostics**

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Diagnostic:
    code: str
    section: str
    level: str
    message: str

def summarize(items):
    counts = {'OK': 0, 'WARNING': 0, 'ERROR': 0}
    for item in items:
        counts[item.level] += 1
    return counts
```

`collect()` checks existing owned studio objects, current product source/stage/LOD, active light preset, camera availability/framing metadata, environment/HDRI availability, preview mode, post-pipeline marker and lightweight runtime-performance diagnostics. Optional remote HDRIs yield WARNING, not ERROR.

- [x] **Step 4: Add explicit diagnostics operator/UI**

The operator runs `legacy.validate_static_configuration(scene)` and `legacy.validate_built_scene(scene)`, stores a concise success/failure in `scene.awful_state.last_operation/last_error`, and never performs repair automatically.

- [x] **Step 5: Extend packaged runtime contract**

Add runtime checks that diagnostics returns no ERROR for a freshly built default studio and that calling diagnostics does not change datablock counts or trigger network attempts.

- [x] **Step 6: Run tests**

Run:
```powershell
python -m unittest tests.fast.test_studio_diagnostics_contract -v
python -m unittest discover -s tests/fast -q
```

Later packaged runtime uses the existing `p0_suite.py` entrypoint.

- [x] **Step 7: Commit**

```bash
git add extension/awful_studio/studio_diagnostics.py extension/awful_studio/workflow_ui.py tests/fast/test_studio_diagnostics_contract.py tests/runtime/p0_suite.py
git commit -m "feat(diagnostics): add actionable studio health report"
```

### Task 3: Product/device capability-driven workflow

**Files:**
- Modify: `extension/awful_studio/device_asset_loader.py`
- Modify: `extension/awful_studio/product_quality.py`
- Modify: `extension/awful_studio/workflow_ui.py`
- Test: `tests/fast/test_device_asset_loader_contract.py`
- Test: `tests/fast/test_product_quality_contract.py`
- Runtime: `tests/runtime/product_quality_contract.py`

**Interfaces:**
- Produces: `device_capabilities(key: str) -> frozenset[str]`
- Uses existing `device_asset_spec`, `lod_keys`, `orientation_preset_keys`, `hinge_preset_keys`.
- UI never infers capability from display labels or object names.

- [x] **Step 1: Write failing capability tests**

```python
def test_device_capabilities_are_explicit():
    loader = load_loader()
    assert {'screen', 'orientation', 'lod'} <= loader.device_capabilities('DEVICE_IPHONE_17')
    assert {'screen', 'orientation', 'lod'} <= loader.device_capabilities('DEVICE_IPAD_PRO_11')
    assert {'screen', 'hinge', 'lod'} <= loader.device_capabilities('DEVICE_MACBOOK_PRO_14')
    assert 'orientation' not in loader.device_capabilities('DEVICE_MACBOOK_PRO_14')
```

- [x] **Step 2: Observe RED**

Run: `python -m unittest tests.fast.test_device_asset_loader_contract tests.fast.test_product_quality_contract -v`

Expected: FAIL because `device_capabilities` is undefined.

- [x] **Step 3: Add the explicit capability helper**

```python
def device_capabilities(key):
    spec = device_asset_spec(key)
    caps = {'lod', 'screen'}
    if spec.get('orientation_axis'):
        caps.add('orientation')
    if 'CTRL_HINGE' in spec.get('controls', ()):
        caps.add('hinge')
    return frozenset(caps)
```

Use the catalog's existing `orientation_axis`, `controls`, `screen_object` and `lods` fields; do not add redundant booleans to every asset.

- [x] **Step 4: Make Product UI capability-driven**

Replace key-specific UI checks with `device_capabilities(selected)`. Show Stage and LOD as distinct labels/controls. Unsupported controls are not drawn.

- [x] **Step 5: Extend real Blender product runtime**

For each bundled device, assert the UI-facing capability set agrees with actual runtime behavior, then re-run existing screen/orientation/hinge/save-reopen checks.

- [x] **Step 6: Run targeted + fast tests**

Run:
```powershell
python -m unittest tests.fast.test_device_asset_loader_contract tests.fast.test_product_quality_contract -v
python -m unittest discover -s tests/fast -q
```

- [x] **Step 7: Commit**

```bash
git add extension/awful_studio/device_asset_loader.py extension/awful_studio/product_quality.py extension/awful_studio/workflow_ui.py tests/fast/test_device_asset_loader_contract.py tests/fast/test_product_quality_contract.py tests/runtime/product_quality_contract.py
git commit -m "feat(product): polish capability-driven device workflow"
```

### Task 4: Deterministic still-camera views

**Files:**
- Modify: `extension/awful_studio/camera_policy.py`
- Modify: `extension/awful_studio/workflow_ui.py`
- Test: `tests/fast/test_camera_framing_contract.py`
- Runtime: `tests/runtime/p0_camera_contract.py`

**Interfaces:**
- Produces: `CAMERA_VIEW_PRESETS: Mapping[str, dict]`
- Produces: `camera_view_spec(key: str) -> dict`
- Produces runtime adapter: `legacy.apply_camera_view(scene, key) -> None`
- Still view state remains separate from existing `camera_motion`.

- [x] **Step 1: Write RED tests for still views**

```python
def test_still_view_inventory_is_photographic():
    policy = load_policy()
    assert set(policy.CAMERA_VIEW_PRESETS) == {
        'HERO_85', 'THREE_QUARTER_LEFT_85', 'THREE_QUARTER_RIGHT_85',
        'SIDE_85', 'WIDE_50', 'DETAIL_120', 'TOP_THREE_QUARTER_85',
    }
    assert policy.camera_view_spec('WIDE_50')['lens'] == 50.0
    assert policy.camera_view_spec('HERO_85')['lens'] == 85.0
    assert policy.camera_view_spec('DETAIL_120')['lens'] == 120.0
```

- [x] **Step 2: Observe RED**

Run: `python -m unittest tests.fast.test_camera_framing_contract -v`

- [x] **Step 3: Implement pure view specs + runtime adapter**

```python
CAMERA_VIEW_PRESETS = {
    'HERO_85': {'lens': 85.0, 'margin': 1.24, 'yaw_deg': 0.0, 'pitch_deg': 4.0},
    'THREE_QUARTER_LEFT_85': {'lens': 85.0, 'margin': 1.28, 'yaw_deg': -28.0, 'pitch_deg': 5.0},
    'THREE_QUARTER_RIGHT_85': {'lens': 85.0, 'margin': 1.28, 'yaw_deg': 28.0, 'pitch_deg': 5.0},
    'SIDE_85': {'lens': 85.0, 'margin': 1.30, 'yaw_deg': 90.0, 'pitch_deg': 2.0},
    'WIDE_50': {'lens': 50.0, 'margin': 1.38, 'yaw_deg': 0.0, 'pitch_deg': 3.0},
    'DETAIL_120': {'lens': 120.0, 'margin': 1.10, 'yaw_deg': -18.0, 'pitch_deg': 4.0},
    'TOP_THREE_QUARTER_85': {'lens': 85.0, 'margin': 1.32, 'yaw_deg': -28.0, 'pitch_deg': 24.0},
}
```

The runtime adapter clears camera-rig animation, sets motion to `STATIC`, calls existing `apply_camera_base_pose` with lens/margin, then sets owned yaw/pitch controls from the view spec. Reapplying the same view produces identical transforms.

- [x] **Step 4: Add `camera_view` EnumProperty and UI**

Add it through `camera_policy.install(legacy)`; the Camera panel shows Still View first, Motion second. No duplicate lens slider is added.

- [x] **Step 5: Extend Blender runtime**

Apply HERO в†’ WIDE в†’ HERO and assert HERO transform/lens are identical before/after; verify product bounds still fit and unmanaged objects are untouched.

- [x] **Step 6: Run tests and commit**

Run fast camera + full suite, then:
```bash
git add extension/awful_studio/camera_policy.py extension/awful_studio/workflow_ui.py tests/fast/test_camera_framing_contract.py tests/runtime/p0_camera_contract.py
git commit -m "feat(camera): add deterministic product still views"
```

### Task 5: Production lighting shortcuts without duplicate state

**Files:**
- Create: `extension/awful_studio/lighting_workflow.py`
- Modify: `extension/awful_studio/__init__.py`
- Modify: `extension/awful_studio/workflow_ui.py`
- Test: `tests/fast/test_lighting_workflow_contract.py`
- Runtime: `tests/runtime/p0_lighting_contract.py`

**Interfaces:**
- Produces: `PRODUCTION_LOOKS: Mapping[str, str]` mapping workflow names to existing canonical preset IDs.
- Produces: `apply_look(legacy, scene, look: str) -> str`.
- Does not add a second persistent lighting preset property.

- [x] **Step 1: Write RED mapping tests**

```python
def test_production_looks_route_to_existing_presets():
    policy = load_policy()
    assert policy.PRODUCTION_LOOKS == {
        'PRODUCT': 'COMMERCIAL_3LIGHT',
        'SOFT_BEAUTY': 'TOP_SOFT_PACKSHOT',
        'HARD_FLASH': 'DIRECT_FLASH',
        'EDGE': 'DUAL_STRIP_HERO',
        'ACCENT': 'DUAL_COLOR_STRIP',
        'GOBO': 'HARD_GOBO',
        'WINDOW': 'WINDOW_BALANCED',
        'GLASS': 'BACKLIT_GLASS',
    }
```

- [x] **Step 2: Observe RED**

Run: `python -m unittest tests.fast.test_lighting_workflow_contract -v`

- [x] **Step 3: Implement thin routing**

```python
def apply_look(legacy, scene, look):
    try:
        preset_id = PRODUCTION_LOOKS[look]
    except KeyError as exc:
        raise ValueError(f'Unknown production lighting look: {look}') from exc
    legacy.apply_lighting_preset(scene, preset_id, False, True)
    return preset_id
```

- [x] **Step 4: Add quick-look buttons above advanced family/preset controls**

The existing `studio_light_family` and `studio_light_preset` remain authoritative and continue to show the exact selected preset.

- [x] **Step 5: Extend runtime idempotence test**

Apply ACCENT в†’ PRODUCT в†’ ACCENT and compare active light roles, energy/color/temperature and shaper state for the two ACCENT applications. Apply PRODUCT afterward and assert colored FX lights are inactive rather than leaking from the previous look.

- [x] **Step 6: Run fast tests and commit**

```bash
git add extension/awful_studio/lighting_workflow.py extension/awful_studio/__init__.py extension/awful_studio/workflow_ui.py tests/fast/test_lighting_workflow_contract.py tests/runtime/p0_lighting_contract.py
git commit -m "feat(lighting): add production look shortcuts"
```

### Task 6: Clear environment workflow and offline state

**Files:**
- Modify: `extension/awful_studio/workflow_ui.py`
- Modify: `extension/awful_studio/natural_light.py` only if a pure status helper is missing.
- Test: `tests/fast/test_natural_light_contract.py`
- Runtime: `tests/runtime/p0_natural_light_contract.py`

**Interfaces:**
- Produces/uses an environment status snapshot containing mode, selected world preset, background visibility, glass visibility and optional-asset availability.
- Existing `world_preset`, `natural_light_enabled`, `show_environment_background` and window-glass state remain authoritative.

- [x] **Step 1: Add RED tests for explicit environment status**

Require Physical Sky to report no remote-asset requirement, HDRI modes to distinguish cached/available/missing optional assets, and ordinary status collection to make zero network attempts.

- [x] **Step 2: Observe RED**

Run: `python -m unittest tests.fast.test_natural_light_contract -v`

- [x] **Step 3: Implement status helper/UI only where needed**

The Environment panel shows the existing mode/preset selector, Studio/World relationship, BG and Glass toggles, plus a concise `Ready / Optional asset missing` line and explicit Download/Retry button. Merely opening/drawing the panel never downloads anything.

- [x] **Step 4: Extend real Blender runtime**

Exercise Physical Sky, cached HDRI and missing-HDRI states; assert Build/preset switching/status inspection stay network-clean and that artificial lights remain independently controllable.

- [x] **Step 5: Run tests and commit**

```bash
git add extension/awful_studio/workflow_ui.py extension/awful_studio/natural_light.py tests/fast/test_natural_light_contract.py tests/runtime/p0_natural_light_contract.py
git commit -m "feat(environment): clarify offline studio world workflow"
```
### Task 7: Output panel and safe preview/final preparation

**Files:**
- Modify: `extension/awful_studio/workflow_ui.py`
- Modify: `extension/awful_studio/runtime_performance.py`
- Test: `tests/fast/test_runtime_performance_contract.py`
- Runtime: `tests/runtime/p0_performance_contract.py`
- Runtime: `tests/runtime/p0_post_pipeline_contract.py`

**Interfaces:**
- Existing `preview_mode` remains authoritative for FAST/QUALITY viewport state.
- Produces: `output_snapshot(scene) -> dict[str, object]` for UI/diagnostics only.
- Uses native `scene.render.film_transparent` rather than duplicating transparency state.

- [x] **Step 1: Write RED output contract**

Require `output_snapshot` to report render engine, preview mode, transparent-background state and whether the managed post pipeline exists, while source contains no assignment to Cycles compute backend/device.

- [x] **Step 2: Observe RED**

Run: `python -m unittest tests.fast.test_runtime_performance_contract -v`

- [x] **Step 3: Implement output snapshot and panel**

Output panel contains:
- Fast Preview / Quality Preview via existing `preview_mode`;
- native Film Transparent toggle;
- current render engine/device diagnostic text;
- explicit Build Post Pipeline action;
- no fake Final preset that overwrites unrelated render settings.

- [x] **Step 4: Runtime safety assertions**

Switch FAST в†” QUALITY and assert:
- `scene.cycles.device` is unchanged;
- compute backend preference is unchanged;
- final render samples/settings outside the documented preview fields are unchanged;
- transparent toggle changes only `scene.render.film_transparent`;
- post pipeline remains opt-in and idempotent.

- [x] **Step 5: Run tests and commit**

```bash
git add extension/awful_studio/workflow_ui.py extension/awful_studio/runtime_performance.py tests/fast/test_runtime_performance_contract.py tests/runtime/p0_performance_contract.py tests/runtime/p0_post_pipeline_contract.py
git commit -m "feat(output): add safe production output workflow"
```

### Task 8: Canonical Full Studio review artifact and final gates

**Files:**
- Create: `tools/production_pass_review.py`
- Create: `docs/PRODUCTION_PASS_REVIEW.md`
- Modify: `tests/fast/test_preview_delivery_contract.py` only if a deterministic artifact contract is required.
- Use existing verifier; do not create a second packaging/runtime harness.

**Interfaces:**
- Explicit command builds a review scene from the Extension source, never during import/register.
- Outputs stay under a local/generated review directory and are not treated as runtime dependencies.

- [x] **Step 1: Write a contract for the review tool**

Require source to call explicit Build, select representative product/device, apply named lighting/camera states, save a `.blend` review scene and optionally render bounded-size previews only when explicitly invoked.

- [x] **Step 2: Implement the explicit review script**

The script accepts output directory and preset/product arguments, uses existing AWFUL operators/policies, and records a JSON manifest with Blender version, Extension version, chosen product, lighting, camera, environment and output files.

- [x] **Step 3: Run fast suite and explicit Blender review generation**

Run the review script with installed Blender 5.2.1 and inspect the generated Full Studio scene plus representative Product/Accent/Gobo/Window previews.

- [x] **Step 4: Run canonical health gates**

```powershell
python tools/awful.py status
python tools/awful.py doctor
python tools/awful.py fast
python -m unittest discover -s tests/fast -q
```

Then build/validate the Extension and run the existing exact-ZIP Blender 5.2.1 runtime verification path with local Blender explicitly allowed.

- [x] **Step 5: Lifecycle verification**

Using the exact candidate ZIP in an isolated profile: install в†’ enable в†’ Build в†’ save/reopen в†’ Rebuild в†’ Remove в†’ disable в†’ re-enable в†’ restart/reopen. Confirm no unmanaged-data, network, ownership or device-selection regression.

- [x] **Step 6: Review branch without merging**

Run `git diff --check`, inspect all commits/diffs, leave `agent/production-pass` unmerged and report exact test/runtime evidence to the owner for approval.

- [x] **Step 7: Commit final review tooling/docs**

```bash
git add tools/production_pass_review.py docs/PRODUCTION_PASS_REVIEW.md tests/fast/test_preview_delivery_contract.py
git commit -m "test(review): add production pass visual evidence workflow"
```


