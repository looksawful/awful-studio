# Product Quality Mockups Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add production-usable procedural Bottle, Jar, Box, Can, Phone and Tablet mockups plus deterministic starter materials without weakening AWFUL ownership, offline behavior, camera framing or bounded runtime behavior.

**Architecture:** Add one focused `extension/awful_studio/product_quality.py` policy/adapter module, following the existing `studio_geometry.py`, `natural_light.py` and `playback_policy.py` pattern. Pure catalog/material policy remains importable without Blender; `install(legacy)` adds scene settings/UI hooks before registration, while scene mutation happens only after an explicit user action or explicit Build/Rebuild restoration. AWFUL mockups are scene-owned and replaceable; unmanaged mounted products are never replaced, deleted or reparented by mockup selection.

**Tech Stack:** Python 3, Blender 5.2.1 `bpy`, Blender Extension packaging, `unittest`, existing AWFUL ownership/runtime harness.

**Spec:** `docs/superpowers/specs/2026-09-11-studio-visual-product-completion-design.md`

## Global Constraints

- Blender target is 5.2 LTS; runtime evidence uses Blender 5.2.1.
- `historical/0.0.15/awful_studio_v4_2_gpu_perf.py` remains byte-identical and is never edited.
- Import/register/enable/update/restart never creates or mutates a studio scene.
- Build/Rebuild/Remove remain explicit operations.
- Base Build and mockup generation are offline and make zero network requests.
- Destructive mutation is explicit-owner and scene scoped; names/roles alone never authorize deletion.
- Unmanaged mounted products survive Build/Rebuild/Remove and all mockup operations.
- Generated geometry/material cost is bounded and deterministic.
- No render/GPU tests are part of structural GREEN. Visual approval remains a separate opt-in #4 gate.
- This is the first 0.0.17 Product Quality slice, developed on an isolated branch from the verified 0.0.16 P0 base. Do not merge it into a public 0.0.16 release candidate merely to close the issue.

---

### Task 1: Pure mockup and starter-material policy

**Files:**
- Create: `extension/awful_studio/product_quality.py`
- Create: `tests/fast/test_product_quality_contract.py`

**Interfaces:**
- Produces: `MOCKUP_SPECS: dict[str, dict]`, `MATERIAL_STARTERS: dict[str, dict]`, `mockup_spec(key: str) -> dict`, `material_spec(key: str) -> dict`, `mockup_keys() -> tuple[str, ...]`.
- Mockup keys: `BOTTLE`, `JAR`, `BOX`, `CAN`, `PHONE`, `TABLET`.
- Material keys: `COATED`, `GLASS`, `METAL`, `PAPER`, `SCREEN`.

- [ ] **Step 1: Write the failing pure contract**

```python
EXPECTED = {'BOTTLE', 'JAR', 'BOX', 'CAN', 'PHONE', 'TABLET'}


def test_catalog_has_six_real_world_mockups():
    import product_quality
    assert set(product_quality.mockup_keys()) == EXPECTED
    for key in EXPECTED:
        spec = product_quality.mockup_spec(key)
        x, y, z = spec['dimensions_m']
        assert 0.004 <= min(x, y, z)
        assert max(x, y, z) <= 0.40
        assert 1 <= spec['max_mesh_parts'] <= 8
        assert 3 <= spec['bevel_segments'] <= 6
        assert spec['material_slots']


def test_material_starters_are_bounded_and_offline():
    for key in ('COATED', 'GLASS', 'METAL', 'PAPER', 'SCREEN'):
        spec = product_quality.material_spec(key)
        assert 0.0 <= spec['roughness'] <= 1.0
        assert 0.0 <= spec['metallic'] <= 1.0
        assert 'url' not in repr(spec).lower()
```

- [ ] **Step 2: Run the focused test and verify RED**

Run: `python -m unittest tests.fast.test_product_quality_contract -v`

Expected: FAIL because `product_quality.py` / catalog interfaces do not exist.

- [ ] **Step 3: Add the minimum pure policy**

Use plausible starter dimensions in meters, stored as immutable intent rather than Blender geometry:

```python
MOCKUP_SPECS = {
    'BOTTLE': {'dimensions_m': (0.075, 0.075, 0.220), 'material_slots': ('BODY', 'CAP', 'LABEL'), 'max_mesh_parts': 4, 'bevel_segments': 4},
    'JAR': {'dimensions_m': (0.090, 0.090, 0.110), 'material_slots': ('BODY', 'LID', 'LABEL'), 'max_mesh_parts': 4, 'bevel_segments': 4},
    'BOX': {'dimensions_m': (0.120, 0.070, 0.180), 'material_slots': ('BODY', 'LABEL'), 'max_mesh_parts': 2, 'bevel_segments': 4},
    'CAN': {'dimensions_m': (0.066, 0.066, 0.122), 'material_slots': ('BODY', 'TOP', 'LABEL'), 'max_mesh_parts': 4, 'bevel_segments': 4},
    'PHONE': {'dimensions_m': (0.071, 0.008, 0.147), 'material_slots': ('FRAME', 'BACK', 'SCREEN'), 'max_mesh_parts': 4, 'bevel_segments': 5},
    'TABLET': {'dimensions_m': (0.178, 0.0065, 0.248), 'material_slots': ('FRAME', 'BACK', 'SCREEN'), 'max_mesh_parts': 4, 'bevel_segments': 5},
}
```

Starter materials contain only numeric/shader intent. `SCREEN` may have bounded emission strength; `GLASS` may have bounded transmission/IOR. No texture/HDRI/network references are allowed.

- [ ] **Step 4: Run focused + full fast suite**

Run: `python -m unittest tests.fast.test_product_quality_contract -v && python -m unittest discover -s tests/fast -v`

Expected: PASS.

- [ ] **Step 5: Commit**

Commit only the pure policy and its test.

---

### Task 2: Blender mockup builders and deterministic material slots

**Files:**
- Modify: `extension/awful_studio/product_quality.py`
- Modify: `extension/awful_studio/__init__.py`
- Create: `tests/runtime/product_quality_contract.py`

**Interfaces:**
- Consumes: `MOCKUP_SPECS`, `MATERIAL_STARTERS`, existing `legacy.mark_managed`, `legacy.mount_product`, `ownership.owned`, `ownership.for_scene`.
- Produces: `create_mockup(legacy, scene, key) -> bpy.types.Object`, `mockup_roots(legacy, scene) -> list[bpy.types.Object]`, `replace_mockup(legacy, scene, key) -> bpy.types.Object`.
- Owned root role: `MOCKUP_ROOT`; owned mesh roles use `MOCKUP_<KEY>_*`; starter material roles use `MOCKUP_MAT_<STARTER>`.

- [ ] **Step 1: Extend runtime contract before implementation**

For every mockup key, open the packaged studio fixture and assert:

```python
root = product_quality.replace_mockup(legacy, scene, key)
assert ownership.owned(root, scene)
assert root['awful_role'] == 'MOCKUP_ROOT'
assert product_quality.mockup_key(root) == key
meshes = [o for o in [root, *legacy.descendants(root)] if o.type == 'MESH']
assert 1 <= len(meshes) <= product_quality.mockup_spec(key)['max_mesh_parts']
assert legacy.world_bbox(meshes) is not None
```

Also record source dimensions as custom properties on the root and assert bottom alignment before Auto Fit is approximately zero within `1e-4 m`.

- [ ] **Step 2: Run packaged cloud runtime and verify RED**

Commit the runtime contract and add it to `tests/runtime/p0_suite.py` under name `product_quality`, then let GitHub Actions run the exact built ZIP on Windows/Ubuntu.

Expected: product-quality contract fails because Blender builders do not exist.

- [ ] **Step 3: Implement bounded primitive builders**

Use deterministic Blender primitives and bounded modifiers only:

- Bottle: cylindrical body + shoulder/neck + cap; smooth shading; body/cap/label slot order.
- Jar: cylindrical body + lid; smooth shading; body/lid/label order.
- Box: beveled rectangular body; body/label order.
- Can: cylindrical body + top detail; body/top/label order.
- Phone: rounded body + inset screen; frame/back/screen order.
- Tablet: same policy at tablet dimensions; frame/back/screen order.

Each builder must:

```python
legacy.mark_managed(obj, role)
legacy.mark_managed(obj.data, f'{role}_MESH')
obj.parent = root
```

Bevel/subdivision segment counts come from `MOCKUP_SPECS`; no adaptive unbounded tessellation and no network calls.

- [ ] **Step 4: Implement starter materials once per scene owner**

Create/reuse owned materials by stable roles. Configure Principled BSDF with Blender 5.2 socket-name checks rather than assuming one historical socket layout. Material slot order on generated meshes must match `material_slots` metadata deterministically.

- [ ] **Step 5: Run cloud runtime GREEN**

Expected: six mockups generate with measurable bounds, expected owned roles, deterministic slots and bounded part counts on Windows/Ubuntu Blender 5.2.1.

- [ ] **Step 6: Commit**

Commit builder/material implementation separately from the RED contract commit.

---

### Task 3: Safe replacement, explicit UI action and rebuild restoration

**Files:**
- Modify: `extension/awful_studio/product_quality.py`
- Modify: `extension/awful_studio/__init__.py`
- Modify: `tests/fast/test_product_quality_contract.py`
- Modify: `tests/runtime/product_quality_contract.py`

**Interfaces:**
- Adds scene setting annotation `product_mockup` with `NONE/BOTTLE/JAR/BOX/CAN/PHONE/TABLET`.
- Adds registered operator `awful.generate_mockup` via `product_quality.CLASSES` or an install-time class list consumed by root `CLASSES`.
- Product panel shows `Mockup` selector + `Generate / Replace AWFUL Mockup` action.

- [ ] **Step 1: Add RED safety cases**

Runtime cases:

```python
# user-mounted hierarchy must survive an attempted mockup replacement
user_root = make_unmanaged_product_fixture()
legacy.mount_product([user_root], False)
result = bpy.ops.awful.generate_mockup()
assert result == {'CANCELLED'}
assert user_root.name in bpy.data.objects
assert not ownership.owned(user_root, scene)

# repeated owned replacement is bounded
baseline = managed_mockup_counts(scene)
for key in ('BOTTLE', 'JAR', 'PHONE', 'BOTTLE'):
    product_quality.replace_mockup(legacy, scene, key)
assert managed_mockup_counts(scene) <= bounded_expected
```

- [ ] **Step 2: Verify RED in cloud runtime**

Expected: operator/safety behavior missing.

- [ ] **Step 3: Implement scene-scoped replacement**

Before deleting anything:

1. call `ownership.preflight(scene)`;
2. identify current mounted unmanaged roots under `PRODUCT_CONTENT`;
3. if any measurable unmanaged product exists, refuse mockup generation with a clear error;
4. identify replaceable objects only when `ownership.owned(obj, scene)` and role is `MOCKUP_ROOT` or a descendant of such a root;
5. if an unmanaged child is parented under a mockup root, refuse instead of mutating it;
6. remove only owned mockup objects and zero-user owned mockup meshes/materials;
7. create the new mockup and mount it through existing product metrics/framing logic.

Do not call broad `ownership.remove(scene)` for a mockup swap.

- [ ] **Step 4: Preserve mockup choice across explicit Rebuild**

Wrap the retained diagnostic fallback path during `install(legacy)`: if there is no preserved unmanaged product and `scene.awful_studio.product_mockup != 'NONE'`, create the selected AWFUL mockup instead of the diagnostic fixture. The default remains `NONE`, so ordinary Build behavior does not change until the user explicitly chooses a mockup.

- [ ] **Step 5: Add UI without duplicating Blender controls**

Patch only `AWFUL_PT_Product.draw`: keep existing Product Motion/Playback UI and append the mockup selector/action. Do not expose native transforms/bevel/material node controls through duplicate custom properties.

- [ ] **Step 6: Verify fast + packaged runtime**

Expected: user data survives, mockup replacement is bounded, rebuild restores selected AWFUL mockup, import/register remain scene-clean, no network attempts occur.

- [ ] **Step 7: Commit**

Commit the safety/UI/rebuild slice separately.

---

### Task 4: Auto Fit / camera framing and lifecycle regression evidence

**Files:**
- Modify: `tests/runtime/product_quality_contract.py`
- Modify: `tests/runtime/p0_suite.py`
- Modify only if a proven defect exists: `extension/awful_studio/product_quality.py`, `camera_policy.py` or retained mounting code.

**Interfaces:**
- Consumes existing `legacy.mount_product`, `camera_policy.required_camera_distance`, scene ownership and exact-ZIP verifier.
- Produces no new product API unless runtime evidence proves a gap.

- [ ] **Step 1: Add failing-or-passing acceptance assertions before changing production code**

For all six generated mockups:

- mount with Auto Fit enabled;
- assert final measured width/depth/height are positive and within `STUDIO_SPEC['product_envelope']` maxima;
- apply representative static camera framing and assert the camera distance is finite/positive;
- rebuild three times and assert object/mesh/material/action counts remain bounded;
- save/reopen and assert selected mockup metadata and measurable geometry survive;
- assert network-attempt counter remains zero.

- [ ] **Step 2: Run exact ZIP runtime on Windows/Ubuntu**

If all assertions already pass, make no production change. If one fails, use systematic debugging and add the smallest focused fix after the failing evidence exists.

- [ ] **Step 3: Run full regression gate**

Required GREEN:

- `python -m unittest discover -s tests/fast -v`;
- official Blender Extension validate/build;
- exact ZIP install/lifecycle/migration suite;
- product-quality contract;
- native static Extension repository generation/sync/install;
- Windows and Ubuntu Blender 5.2.1;
- `render_tests: false`.

- [ ] **Step 4: Commit any necessary runtime-only test/fix changes**

No speculative refactor if existing framing/mounting already passes.

---

### Task 5: Evidence, issue/Notion handoff and milestone boundary

**Files:**
- Modify: `STATE.md` only if the project-level current state materially changes.
- Do not modify `LICENSE` or unrelated release policy.

**Interfaces:**
- Produces review evidence in PR #28 branch/PR, GitHub issue #28 and the corresponding Notion backlog row.

- [ ] **Step 1: Record exact CI evidence**

Include final head SHA, CI run ID, Windows/Ubuntu results, exact package SHA-256, product-quality contract status, native repository status, and explicit `render_tests: false`.

- [ ] **Step 2: Update issue #28 and Notion**

Set implementation status to complete only after fresh exact-ZIP runtime evidence exists. State explicitly that structural/product-quality acceptance is GREEN while visual approval remains pending #4 because render/GPU evidence was not authorized.

- [ ] **Step 3: Keep milestone boundary clean**

Do not merge this 0.0.17 slice into a public 0.0.16 release candidate. The branch may be fully implemented and cloud-verified while the 0.0.16 public release/license decision remains separate.

- [ ] **Step 4: Final verification before completion claim**

Use `superpowers:verification-before-completion`; inspect fresh CI, PR changed files, and unresolved review threads before marking the slice complete.
