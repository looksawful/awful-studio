# AWFUL STUDIO 0.0.16 — editorial deep audit

Date: 2026-09-10
Branch: `integration/0.0.16-rc1`
Method: AWFUL Editorial source hierarchy + fact extraction + critic pass + Blender/3D QA loop.

## Audit rule

This review separates four things that must not be collapsed:

1. **Canonical requirement** — current explicit user instruction and current AWFUL STUDIO Notion pages.
2. **Observed implementation** — code and packaged Blender runtime behavior on this branch.
3. **Evidence** — fast tests, Blender 5.2.1 runtime reports and GitHub Actions.
4. **Claim** — what README/issues/release metadata are allowed to say.

A green CI job is evidence for the behavior that job actually exercises. It is not evidence that the whole product backlog is complete.

Current user instruction overrides older backlog items that require render/visual regression. Alpha 0.0.16 is therefore qualified without render tests; render/visual evidence remains deferred work rather than a release claim.

## Confirmed current evidence

`integration/0.0.16-rc1` currently passes the canonical Linux x64 packaged runtime path with Blender 5.2.1 LTS.

Verified by the runtime suite:

- exact Extension manifest validation;
- official Extension ZIP build;
- install of that exact ZIP;
- enable / disable / re-enable without scene mutation or handler accumulation;
- explicit Build;
- repeated Rebuild with bounded datablock counts;
- scene ownership tagging;
- preservation of unmanaged objects, collections and shared materials;
- cross-scene destructive-operation refusal;
- offline Extension operation without implicit network access;
- Remove and restoration of previous world/camera;
- save/reopen ordinary and AWFUL `.blend` files;
- future-schema refusal without mutation;
- explicit metadata-only migration from the exact historical 0.0.15 source;
- migrated scene reopen and rebuild.

This evidence is strong enough to call the Extension lifecycle **Linux runtime GREEN**. It is not yet enough to call Alpha 0.0.16 product-complete.

## Source reconciliation

### Licensing

**Canonical:** Notion `Legal & Attribution — GPL Review` records the reviewed decision that the Blender-facing `bpy` add-on uses GPL-3.0-or-later. The corresponding P0 backlog item is Done.

**Conflict:** PR #18 still says it does not include a public license/release decision; earlier release-pipeline work treated licensing as unresolved.

**Decision:** GPL-3.0-or-later is no longer an unresolved engineering question. Public publication remains an explicit release action, but release tooling/docs must not represent the license decision itself as unknown.

### Runtime harness

**Canonical:** P0 backlog still says `Headless Blender runtime test harness` is Not started.

**Observed:** packaged Blender 5.2.1 runtime QA is implemented and green on the integration RC.

**Decision:** backlog state is stale and must be synchronized after the integration evidence is recorded.

### Repository publication

**Canonical backlog text:** `Publish public GitHub repository looksawful/awfulstudio` is In progress.

**Observed:** the active public canonical repository is `looksawful/awful-studio`.

**Decision:** old repository-name requirement is stale. Do not create a duplicate repository merely to satisfy old text.

### Flash milestone

**Canonical newer Notion records:** Alpha 0.0.16 includes the flash photographic-policy slice with established defaults:

- scene exposure: `-3 EV` in flash mode;
- aperture intent: `f/11`;
- camera flash CCT: `6500 K`;
- continuous default CCT: `4300 K`;
- portrait camera flash: camera-left and off the optical axis.

**Conflict:** issue #6 still calls this an Alpha 0.0.18 contract and current legacy implementation does not implement the full regime.

**Decision:** reconcile issue #6 to the current 0.0.16 target and implement through runtime TDD.

### Motion milestone

**Canonical:** independent Once / Loop / Ping-Pong policy is P0 for 0.0.16. Broader expanded motion/orbit work is assigned to later versions by the newer project overview.

**Conflict:** issue #8 bundles playback policy with expanded 360/multi-axis motion.

**Decision:** split release scope. Playback policy is 0.0.16; expanded motion remains later work unless a newer explicit requirement promotes it.

### Natural light / volumetrics

**Canonical:** natural-light daylight/Physical Sky/Sun work is P0 in the 0.0.16 backlog. Volumetrics are explicitly deferred to 0.0.17+ by the newer project overview.

**Conflict:** issue #9 bundles pure-HDRI/environment work with bounded volumetrics.

**Decision:** separate the work. Do not add a volume to 0.0.16 merely because old issue text couples the two.

## Material code findings

### BLOCKER — room visibility is not owner-scoped

**Expected:** Rebuild/controls affect only the current scene's AWFUL-owned data.

**Observed:** `legacy.apply_room_visibility(scene)` scans all `bpy.data.objects` and changes objects whose semantic role starts with `ROOM_` or equals `WINDOW_FRAME`, without checking AWFUL ownership or scene membership.

**Impact:** toggling room visibility in one studio can mutate a foreign scene or an unmanaged user object that happens to carry a colliding role property.

**Required fix:** Blender runtime RED fixture with a foreign/unmanaged role-collision object, then restrict mutations to objects explicitly owned by the supplied scene.

### MAJOR — registry still depends on active Blender context

The hidden collection lookup was repaired, but registry object/material resolution still reads `bpy.context.scene`. This is safer than the old global-name registry but remains context-coupled. For 0.0.16 this is acceptable only if all user-facing operators operate on `context.scene` and multi-scene runtime fixtures prove no cross-scene mutation. A scene-explicit registry refactor belongs in 0.0.17 unless a failing runtime contract forces it earlier.

### MAJOR — Build/Rebuild is not transactionally reversible

`run_build()` records an error if `legacy.build_studio()` fails, but the legacy rebuild removes existing managed data before recreating it. Blender's UNDO operator boundary may protect interactive execution, but direct/runtime calls and partial failures are not a documented transactional guarantee.

For 0.0.16: add a deliberate injected-failure runtime contract and prove whether Blender operator undo/state behavior is sufficient. If the previous studio is destroyed after `CANCELLED`, treat as blocker and implement rollback/temporary-build strategy. Do not assume `bl_options={'UNDO'}` is equivalent to an application transaction.

### MAJOR — historical migration surface may omit generated Actions

Migration enumerates scene objects, object data, materials, child collections, world and compositor group. Object/data animation Actions are not explicitly included. Historical 0.0.15 generated animations can therefore remain `awful_managed` without scene owner metadata after metadata-only migration, then escape later owner-scoped cleanup.

Required: inspect the exact historical fixture, add an animated historical migration test, and either migrate reachable Actions or prove the baseline never creates managed Actions that survive.

### MAJOR — flash photographic regime is incomplete

Current Flash presets are lighting presets, but selecting them does not yet establish the canonical `-3 EV / f11 / 6500 K / camera-left` scene-level regime and exact restoration behavior. This is a P0 product gap, not a documentation problem.

### MAJOR — P0 cyclorama metric control still lacks verified current implementation

Current studio geometry uses fixed world coordinates. The P0 requirement is a physically understandable metric product/stage-to-cyclorama control with valid framing and bounded placement. Issue #7 and Notion claim prior RED/GREEN work existed, but no such feature branch is present in the current repository branch list. Treat it as unimplemented until runtime evidence says otherwise.

### MAJOR — playback policy is absent

Product/camera motion presets generate keyframes, but independent Once / Loop / Ping-Pong policy is not represented in the current settings or runtime contract. This remains P0 for 0.0.16.

### MAJOR — natural-light v2 acceptance is not represented by structural runtime tests

Current implementation has HDRI/Physical Sky and a window portal, but the newer requirement also calls for a separate Sun role and explicit helper-free environment behavior. With render tests prohibited for this milestone, structural runtime acceptance should at least verify mode semantics, object roles, enabled/disabled artificial sources, and no hidden energy source masquerading as a portal.

### MAJOR — visible architecture controls are incomplete

Current room shell contains walls/floor/ceiling/window, but P0 asks for visible studio floor, door + real opening, and independent visibility controls for architectural parts and cyclorama. Current panel exposes a coarse Room toggle and Glass/BG, not the full requested switchboard.

### MAJOR — complete lighting library requirement conflicts with current three-flash baseline

Historical 0.0.15 exposes 16 presets and only three Flash presets. The P0 requirement says Flash should include Direct, Wide, Neutral Ambient and Color Ambient, so a neutral-ambient flash preset is missing. All baseline Commercial/Cinema/Natural schemes must remain reachable.

### MAJOR — release pipeline branch is stale relative to canonical runtime

`agent/10-release-update` contains useful deterministic candidate/repository tooling, but its workflow references the removed `tools/setup_blender.py` path. It must be ported onto `tools/awful.py`, not merged wholesale.

### MINOR — Blender 6.0 deprecation warnings

`Material.use_nodes` / `World.use_nodes` produce deprecation warnings in Blender 5.2. They do not block 0.0.16 but should be tracked for the 5.3/6.0 compatibility horizon.

## P0 release matrix after audit

| Area | Current state | 0.0.16 action |
| --- | --- | --- |
| Extension lifecycle | GREEN on Linux Blender 5.2.1 | preserve, add Windows qualification |
| Ownership/rebuild/remove | GREEN for existing runtime cases | add room-toggle role-collision and failure-safety tests |
| Offline asset cache | GREEN for current HDRI path | audit provenance docs / third-party list |
| Historical migration | GREEN for current fixture | add generated-action coverage |
| GPL licensing | decision resolved | synchronize README/release tooling |
| Flash regime | incomplete | implement P0 via runtime TDD |
| Metric cyclorama distance | incomplete/unverified | implement via TDD |
| Playback Once/Loop/Ping-Pong | incomplete | implement policy via TDD |
| Natural light v2 | incomplete structurally | split from volumetrics, implement non-render acceptance |
| Visible floor/door/visibility | incomplete | create/track P0 slice and implement |
| Complete lighting preset reachability | partial | add missing neutral flash + reachability checks |
| Base camera target/safe framing | unverified P0 | create runtime acceptance and fix if RED |
| Performance evidence | partial timings exist | record repeatable non-render measurements |
| Visual regression | explicitly deferred by current user instruction | do not block 0.0.16 |
| Public repo | already public as `looksawful/awful-studio` | sync stale Notion text, do not duplicate repo |
| Release/native update | infrastructure partial | port release pipeline to canonical runtime and verify native repository update |

## Change order

1. Safety regressions first: cross-scene room visibility, migration action ownership, failed rebuild safety.
2. Reconcile stale issues/backlog states so tests target current requirements.
3. Flash P0 slice.
4. Metric cyclorama control + safe framing.
5. Playback policy.
6. Natural-light structural contract and lighting-library reachability.
7. Visible architecture controls.
8. Performance evidence.
9. Windows packaged runtime qualification.
10. Canonical deterministic release/static-repository/native-update path.
11. Final critic pass: compare every release claim against fresh evidence, update README/STATE/Notion/issues, and only then remove draft status / publish.

No item is considered complete because its code exists. Completion requires a fresh test/evidence path appropriate to that behavior.