# iPhone 17 Storybook owner-review repair plan

Status: proposed ticket breakdown; awaiting owner approval of granularity and blocking edges.
Tracker: existing GitHub Issues, with awful-studio #118 as the current production gate and #50 as asset owner. Related delivery contract: #70. Consumer preview: looksawful.ru #976. No duplicate project or parallel backlog.
Date: 2026-09-30.

## Goal and scope
The owner must see the exact repaired iPhone candidate in private Storybook, in desktop Opera, before deciding Human Gate. Address the reported low/duplicated Dynamic Island, bad rail/edge shading and untextured rear flash. Preserve canonical v30 identity and LOW_DRAFT; source fixes regenerate delivery through the existing build contract. Do not promote public production or merge the asset approval gate automatically.

## Fresh facts and limits
- Source candidate: PR #119 at 2bebd2cc2a64f08230ca243f3437db270ac15152. This differs from the old catalog baseline the owner first saw.
- Blender 5.2.1 LTS is available and was invoked successfully.
- A Blender probe shows every face of the common Y-axis prism directed inward (54/54), whereas the Z-axis prism is outward (0/54 inward). Several existing iPhone shells have negative signed volume. Earlier cap-only reversal does not repair a complete shell.
- A new regression against the committed compatibility GLB fails: BACK_GLASS has 784 inward vertex normals; MAT_FLASH has no baseColorTexture. Five focused tests ran: three PASS, two FAIL. This is baseline RED evidence, not a completed fix.
- Source repair of complete prism winding and body sharp-edge policy has begun in an isolated working copy, but has not been regenerated, exported, visually verified or published.
- The screen source contains a baked black island. PR #119 separates the visible silhouette datum (~6.14 mm from body top) from the engineering hardware keepout (7.79 mm). Preserve that distinction; do not blindly move both.
- A local Storybook loaded the optimized baseline in actual Opera. The private remote route still showed blank content during investigation. A reachable route, downloaded GLB, green build, or local render does not prove the authenticated deployed story.
- Right-monitor placement is not yet verified by an available desktop UI control.
- Existing acceptance for bottom USB-C, 3 mic / 6 speaker apertures and screws remains part of final regression review.

## Decisions
1. Repair generator/DCC geometry before modifiers and export. No Three.js vertex-normal, offset, double-sided or material workaround to conceal source defects.
2. Keep the official screen raster intact as reference; deliver a separate cleaned screen plate and record derivation. Geometry owns the island; the screen plate contains no duplicated black pill.
3. Use an image-driven flash diffuser with embedded texture and correct UVs, grounded in a recorded reference. A solid white disk is insufficient.
4. Reuse the canonical Blender -> compatibility GLB -> Meshopt -> manifest pipeline and existing browser viewer.
5. Each slice exports a verifiable candidate to the same private review path. Final assembled candidate must have one consistent source fingerprint and artifact hash.
6. Keep implementation sequential where it shares generator/runtime files. Dependencies below express actual deliverable blockers, not arbitrary execution order.

## Proposed ticket index

### 1. A reviewer can reliably open the exact iPhone candidate in Storybook
Repository: looksawful.ru. Parent: #976; cross-reference awful-studio #118.
Blocked by: none.
Deliverable: authenticated private story loads the identified candidate in actual desktop Opera; refresh and direct story navigation work.
Acceptance:
- Exact candidate revision/hash is identifiable; the baseline and current candidate cannot be confused.
- Repeated cold and warm loads on desktop reach a visible model with working controls; retain measured load times and actual browser evidence.
- A failed asset/runtime load produces an actionable error/retry state rather than an endless blank spinner.
Verification: existing focused viewer/story tests, private Storybook build, actual authenticated browser cold-load and refresh. Preserve failure logs and distinguish network/runtime/bootstrap defects.
Likely scope: candidate story adapter, asset delivery mapping and viewer lifecycle/error seam; Medium.
Do not rebuild authentication or hosting without a proven route-specific failure.

### 2. The iPhone front shows one correctly placed geometric Dynamic Island
Repository: awful-studio. Parent: #118.
Blocked by: ticket 1, for end-to-end preview verification.
Deliverable: the model retains its physical island at the reference-correct front position when screen artwork changes; default artwork has no baked duplicate.
Acceptance:
- Visible geometry is verified against the independent official raster/reference, while front hardware retains its independent engineering datum.
- Only the selected island/background repair region changes in the cleaned screen derivative; artwork, dimensions and active-area UV remain correct.
- Fresh front and sensor macros in Blender and actual Three.js show one island, readable optics, no ghost/double screen or clipping.
Verification: independent raster/cleaned-image assertions, regenerated asset geometry/material checks, same-camera before/after screenshots.
Likely scope: generator, derived texture/provenance, existing front contract and regenerated artifacts; Medium.

### 3. The iPhone rails and rounded edges shade correctly through a complete orbit
Repository: awful-studio. Parent: #118.
Blocked by: ticket 1, for end-to-end preview verification.
Deliverable: left/right/top/bottom rails, rounded corners, bevels and camera edges retain coherent reflections in the exported candidate.
Acceptance:
- Reproduce the exact defect and verify consistent winding, outward normals, non-degenerate triangles and manifold chassis after evaluation/export; preserve envelope tolerance.
- The original exported-GLB regression is GREEN after source rebuild; test planar rails and rounded transitions, not just the Apple decal or source literals.
- Same-camera material/clay/normal views under fixed diagnostic lighting show no inverted/faceted reflection artifacts through browser orbit.
Verification: Blender 5.2 runtime geometry probe, GLB accessor/winding regression, structural QA and actual Three.js before/after visual evidence.
Likely scope: iPhone generator/normal evaluation, exporter only if proven necessary, existing shading contract and regenerated artifacts; Medium.
Check the actual bad-angle visual seam before accepting the new normal policy; do not blindly restore old Weighted Normal recipes.

### 4. The rear flash has a readable diffuser image texture
Repository: awful-studio. Parent: #118; reference shared materials #54 without opening unrelated HIGH/bake work.
Blocked by: ticket 1, for end-to-end preview verification.
Deliverable: rear macro visibly reads a textured physical flash lens/diffuser rather than a featureless white patch.
Acceptance:
- Texture reference/derivation is recorded; correct UVs, color space and embedded image survive compatibility and Meshopt export.
- Fresnel/diffuser detail remains readable under neutral and review lighting; no baked exterior rim/background or excessive emissive white patch.
- Fresh rear/flash macro works in Blender and actual Storybook without additional material/texture fetch errors.
Verification: MAT_FLASH image/UV/export assertions, Khronos validation and paired rear macro review.
Likely scope: generator flash material/UV, reference texture/provenance and existing material contract; Medium.

### 5. The owner can accept or reject one assembled iPhone candidate
Repository: awful-studio. Parent: #118. Link consumer preview slice.
Blocked by: tickets 2, 3 and 4 (which transitively depend on ticket 1).
Deliverable: a private review link and visible desktop Opera model correspond to the exact assembled, tested candidate.
Acceptance:
- Canonical rebuild/source fingerprint, compatibility/Meshopt GLBs and manifest agree; focused/full required checks pass, Khronos reports 0 errors/0 warnings.
- Real browser front/back/sides/top/bottom/three-quarter plus front sensor, flash and bottom macros cover every reported defect and existing bottom/screen contract; right-monitor placement is visibly confirmed.
- Owner approval/rejection is recorded against that exact candidate. LOW_DRAFT/HOLD persists until explicit approval; rejection reopens affected technical checks.
Verification: existing build/validation and preview scripts, artifact hash comparison, authenticated actual Opera evidence, owner visual decision.
Likely scope: integrated delivery metadata/evidence and private review handoff; Small source change, broader verification.

## Verification commands / contracts
- Focused regression: python -m unittest discover -s tests/fast -p test_iphone_web_shading_contract.py -v
- Front contract: python -m unittest discover -s tests/fast -p test_iphone_front_evidence_contract.py -v
- Canonical rebuild: python tools/build_iphone17_v30.py --blender <existing Blender 5.2.1 executable>
- Required before handoff: python -m unittest discover -s tests/fast -v; git diff --check
- Use existing Khronos and preview test/build scripts; inspect exit codes and full failure counts.
- Capture Blender version, camera/light/render settings, source fingerprint and exact GLB hash with visual evidence. Never substitute green static checks for a human visual pass.

## Checkpoints
- After ticket 1: private authenticated preview actually renders. Local-only success cannot close it.
- After tickets 2 and 3: front and rail evidence is independently reviewable; retain RED/GREEN proof.
- Before ticket 5: texture and geometry are integrated through a fresh canonical build.
- Final: owner Human Gate only after technical gates and visible exact candidate.

## Risks / unresolved questions
- Fixing inward shells before booleans can change chassis evaluation: recheck all 19 cuts, dimensions, bevels and required objects.
- Explicit triangulation/custom normals may change glTF split vertices; validate surface behavior rather than forcing an old triangle count.
- Source PR candidate and consumer baseline differ: identify candidate in the story before claiming a fix was shown.
- Actual remote blank-screen cause remains unresolved; do not attribute it to extensionless iframe redirects (local redirect experiment rendered successfully).
- Available browser tools do not currently prove physical monitor placement; retain as an explicit final delivery requirement.
- New issue creation awaits owner approval of this five-slice breakdown. Existing parent issues stay open and unmodified.

## Implementation handoff
Continue the existing isolated owner-review work; preserve other dirty worktrees and pending changes. No new asset version/framework or second canonical writer. Proposed execution order: preview reliability -> edge repair -> front repair -> flash -> integrated review. Source tasks 2/3/4 have no artificial dependency on one another and can be selected once the preview foundation is verified.


---

## 2026-10-02 plan revision — post-publish rail/normals slice

Status: active planning revision. Supersedes the five-slice execution order above for the current session; historical sections remain as provenance.
Tracker target: existing GitHub issue #118 only. Do not create a parallel ticket/backlog.
Implementation fixed point: PR #126 head `6098ffa6128fbac6c1cbdb90d53e6fc927a35ea5`.
Current production delivery: `iphone-17-v30.web.meshopt.glb` matches PR #126 by SHA-256.

### Scope
Fix only the remaining user-visible rounded rail / edge shading defect on the published iPhone 17. Preserve the PR #126 Dynamic Island, clean screen texture, flash, bottom hardware, current v30 identity, and existing delivery pipeline.

### Dependency graph

```
Exact PR #126 baseline
        ↓
RED regression at BODY_ALUMINUM exported-GLB seam
        ↓
minimal source normal-policy change
        ↓
canonical v30 rebuild
        ↓
focused regression + same-camera macro
        ↓
full delivery/runtime verification
        ↓
human visual gate
        ↓
Standards + Spec review
```

### Task 1 — Lock the rail/corner regression seam
Description: extend the existing iPhone shading contract so it fails on the current PR #126 BODY_ALUMINUM rail/corner normal defect and is derived from exported GLB behavior rather than generator literals.

Acceptance:
- Current PR #126 GLB produces RED on the exact rail/corner normal symptom.
- Test reads exported BODY_ALUMINUM geometry/normals at planar-to-rounded transitions.
- Existing Dynamic Island/screen/flash/bottom tests remain untouched.

Verification:
- `python -m unittest discover -s tests/fast -p test_iphone_web_shading_contract.py -v`
- Record the failing assertion/count against exact SHA 6098ffa.

Dependencies: none.
Likely files: `tests/fast/test_iphone_web_shading_contract.py`.
Scope: S.

### Task 2 — Minimal BODY_ALUMINUM normal-policy repair
Description: change only the chassis normal-generation path needed to turn Task 1 GREEN. Reuse the historically successful policy as a hypothesis, not as a blind copy: triangulation + Blender native `shade_smooth_by_angle(30°)` + `bevel.harden_normals = False`, removing body Weighted Normal only if required by the RED/GREEN loop.

Acceptance:
- Task 1 becomes GREEN.
- Same-camera `screen_edge_macro` visibly removes the stepped/faceted rail highlight.
- Envelope, manifoldness, required cuts and current screen/front behavior remain unchanged.

Verification:
- Targeted shading test GREEN.
- Fresh Blender 5.2.1 `screen_edge_macro` before/after comparison using the same camera/light.
- Structural validation remains GREEN.

Dependencies: Task 1.
Likely files: iPhone generator + existing shading test only.
Scope: S.

### Checkpoint — source fix
- RED captured before source edit.
- GREEN captured after minimal source edit.
- No changes to Three.js compensation, materials, lighting, Dynamic Island, asset version, or delivery architecture.
- If the proposed normal-policy does not clear the exact macro defect, stop and return to diagnosis rather than stacking more fixes.

### Task 3 — Canonical v30 rebuild and delivery verification
Description: regenerate the existing v30 identity through the existing Blender → compatibility GLB → Meshopt → manifest flow.

Acceptance:
- Canonical source fingerprint and regenerated delivery artifacts agree.
- Khronos compatibility and Meshopt validation: 0 errors / 0 warnings.
- Production-facing asset identity remains v30; no v31/v32 fork.

Verification:
- `python tools/build_iphone17_v30.py --blender <existing Blender 5.2.1 executable>`
- Focused iPhone tests.
- Full fast suite.
- Existing Khronos/Meshopt checks.
- `git diff --check`.

Dependencies: Task 2.
Likely files: generated/runtime artifacts and manifest produced by the existing builder.
Scope: M only because generated artifacts span files; no new source architecture.

### Task 4 — Browser and human visual gate
Description: verify the rebuilt exact candidate in the existing Storybook/Three.js path and obtain the owner's final visual decision.

Acceptance:
- Side rails + rounded corners read smoothly at the original bad review angles.
- Front/screen, bottom hardware, rear camera/flash and three-quarter views show no regression.
- Exact GLB hash shown in review matches the rebuilt candidate.

Verification:
- Existing Storybook build and canonical Three.js smoke.
- Browser check at the original bad side/three-quarter angles.
- Human accept/reject against exact candidate.

Dependencies: Task 3.
Scope: S.

### Task 5 — Final code review
Description: review only the diff from fixed point `6098ffa`.

Acceptance:
- Standards axis: repo rules/TDD/runtime evidence satisfied; no unrelated refactor or duplicate pipeline.
- Spec axis: rail/edge shading defect fixed without regressing PR #126 screen/island/flash/bottom work.
- Issue #118 receives root cause, tests, exact commit SHA, and remaining blocker if human gate rejects.

Verification:
- `git diff 6098ffa...HEAD`
- `git log 6098ffa..HEAD --oneline`
- final Standards + Spec review.

Dependencies: Task 4.
Scope: S.

### Explicit non-goals
- No new model version.
- No new renderer or visual-regression framework.
- No Three.js/CSS normal/shading workaround.
- No Dynamic Island rewrite.
- No material/light tuning unless a new independent defect is proven.
- No new GitHub issue unless #118 is formally split by the owner.

### Current progress
- [100%] Exact production/source baseline pinned to PR #126.
- [100%] Current visual rail/edge defect reproduced in Blender macro.
- [100%] Simple bevel-segment and Weighted-Normal-only probes rejected.
- [75%] Regression seam design / historical normal-policy differential understood.
- [0%] Permanent RED test committed.
- [0%] Source normal-policy fix.
- [0%] Canonical rebuild and delivery verification.
- [0%] Browser + human visual gate.
- [0%] Final Standards + Spec review.

## 2026-10-02 execution correction — authoritative for current closeout

This section supersedes the earlier normal-policy wording in Tasks 1–2.

- Root cause candidate: BODY_ALUMINUM used a generic constant-radius rounded rectangle that did not match Apple's explicit Corner Profile Detail A.
- Rejected as standalone causes: bevel 4→12, disabling Weighted Normal, triangulation-only, and outline-density-only changes.
- Regression seam: exported GLB BODY_ALUMINUM corner coordinates against independent Apple Detail A points.
- Baseline PR #126 `6098ffa`: max miss 5.63 mm → RED.
- Current candidate: max miss 0.377 mm → GREEN.
- Fix remains iPhone-local; no shared foundation rewrite, no v31/v32, no Three.js shading workaround.

Current closeout:
- [100%] source/production baseline pinned
- [100%] geometry RED→GREEN regression
- [100%] canonical v30 rebuild
- [100%] focused iPhone tests 14/14
- [100%] full fast tests 190/190
- [100%] Khronos compat + Meshopt 0 errors / 0 warnings
- [100%] preview tests 17/17 + Storybook build
- [100%] browser smoke across 11 canonical assets
- [90%] close browser visual evidence captured with no console/HTTP errors
- [0%] owner Human Gate
- [0%] final Standards + Spec review / commit

## 2026-10-02 front sensor + Camera Control correction

Authoritative for the current Human Gate; supersedes the earlier shared glossy-black material attempt.

- [100%] Orange privacy dot is screen-state raster artwork, not hardware geometry.
- [100%] Removed the single glossy DYNAMIC_ISLAND hardware capsule from v30 delivery.
- [100%] Added two independent physical under-glass masks: FRONT_SENSOR_MASK and FRONT_CAMERA_MASK.
- [100%] Under-glass masks use MAT_UNDER_GLASS_BLACK: near-black dielectric, high roughness, no clearcoat.
- [100%] FRONT_CAMERA_GLASS remains an independent optic inside the right camera mask.
- [100%] Camera Control uses its own MAT_CAMERA_CONTROL_GLASS contract.
- [100%] Camera Control is seated 0.10 mm into the existing side pocket; no new recess subsystem.
- [100%] Front evidence tests GREEN: 5/5.
- [100%] Focused front/shading tests GREEN: 16/16.
- [100%] Full fast suite GREEN: 192/192.
- [100%] Blender runtime geometry contract GREEN.
- [100%] Khronos compat + Meshopt: 0 errors / 0 warnings.
- [100%] Preview tests: 17/17; Storybook build GREEN; smoke GREEN across all 11 canonical assets.
- [100%] git diff --check clean.
- [0%] Owner visual Human Gate on exact refreshed candidate.
- [0%] Final Standards + Spec review, commit and push.

Human Gate checks:
1. Front: left black sensor mask + orange screen-state dot + right black camera mask/optic read as separate elements under the display surface.
2. Camera Control: very dark insert reads subtly recessed (~0.10 mm) rather than proud of the rail.

## 2026-10-02 plan revision — front sensor depth/shading conflict

Research source: `docs/research/iphone-17-front-layer-depth-conflict-2026-10-02.md`.
Execution owner remains GitHub #118. This revision supersedes the earlier assumption that material tuning alone closes the front-sensor Human Gate.

### [0%] Task A — GLB overlap regression (S)

**Description:** Add one exported-GLB regression that proves `SCREEN_CONTENT` has no front-face triangles underneath the two physical front hardware footprints.

**Acceptance criteria:**
- [ ] Current candidate is RED because screen triangles still occupy the sensor/camera footprints.
- [ ] Test is based on exported GLB geometry, not source-string matching.
- [ ] Existing orange-dot screen-state test stays GREEN.

**Verification:** focused front/shading unittest file.

**Dependencies:** none.

### [0%] Task B — cut two openings in SCREEN_CONTENT (S)

**Description:** Reuse the existing boolean-difference path to cut a pill opening for `FRONT_SENSOR_MASK` and a circular opening for `FRONT_CAMERA_MASK` out of the emissive screen prism. Move the masks/camera optic behind the screen front datum so they are visible through the openings rather than layered over screen polygons.

**Acceptance criteria:**
- [ ] Task A turns GREEN.
- [ ] No new renderer override, dependency, abstraction, or delivery version.
- [ ] Screen planar UVs and front/edge material ownership remain correct after the booleans.

**Verification:** focused tests + Blender front-sensor macro.

**Dependencies:** Task A.

### [0%] Checkpoint — deterministic front evidence

- [ ] `front_sensor_macro` has no stitching/halo at the previous bad light angle.
- [ ] New grazing-angle evidence shows stable black masks and camera optic.
- [ ] Orange privacy dot remains screen-state artwork.
- [ ] Camera Control is unchanged.

### [0%] Task C — web/runtime gate (S)

**Description:** Rebuild canonical v30 and run the existing delivery/runtime gates. Do not touch viewer clip planes unless the source-level fix still reproduces a depth artifact.

**Acceptance criteria:**
- [ ] Blender runtime geometry GREEN.
- [ ] full fast suite GREEN.
- [ ] Khronos compat + Meshopt: 0 errors / 0 warnings.
- [ ] Storybook build + all-asset smoke GREEN.

**Dependencies:** Task B.

### [0%] Human Gate

Check only the reported regression:
1. no front sensor/camera overlap or light-dependent stitching;
2. black masks remain visually darker than the display;
3. camera optic remains readable inside the right cutout.

If FAIL: return to diagnosis. If PASS: final Standards + Spec review, then commit/push.

### Ponytail scope guard

Skip on first pass:
- `polygonOffset` / `renderOrder` / `depthWrite=false`;
- transparent full cover-glass web mesh;
- global camera near/far changes;
- material retuning;
- Camera Control changes;
- new version or abstraction.

One regression → two screen cutouts → one rebuild → same Human Gate.

## 2026-10-02 execution result — front depth conflict

- [100%] Exported-GLB overlap regression added. Previous candidate RED: `FRONT_SENSOR_MASK=1`, `FRONT_CAMERA_MASK=1` screen-front triangle coverage.
- [100%] Added two physical cutouts to `SCREEN_CONTENT`: capsule sensor opening + circular camera opening.
- [100%] Moved physical masks/camera stack behind the display front plane.
- [100%] Normalized boolean-created material slots to exactly `MAT_SCREEN_CONTENT` + `MAT_SCREEN_EDGE`.
- [100%] Removed stale/duplicate UV layers after boolean and rebuilt one canonical planar `UVMap`.
- [100%] Overlap regression GREEN: both hardware footprints have zero screen-front coverage.
- [100%] Blender source evidence restored: wallpaper + orange screen-state dot + separate black masks/camera.
- [100%] Blender runtime geometry contract GREEN.
- [100%] Focused front/shading tests GREEN: 17/17.
- [100%] Full fast suite GREEN: 193/193.
- [100%] Khronos compat + Meshopt: 0 errors / 0 warnings.
- [100%] Preview tests GREEN: 17/17.
- [100%] Storybook build GREEN.
- [100%] Storybook smoke GREEN across all 11 canonical assets.
- [100%] `git diff --check` clean.
- [0%] Human visual gate at the original light/grazing-angle repro.
- [0%] Final Standards + Spec review, commit and push.

Current source revision: `8061472a09e835e5eca7f261ef47c8b29e02ce38f1bc0d75c3e71812a938825b`.
Current compat GLB SHA-256: `9b318cff287136a5a523fdf2406f31ad1b6729a6d1d4a92b2cd458119db78502`.
Current Meshopt GLB SHA-256: `606bd505c4e1e68f6294dde4982e91bfe7d676ee0f7636da58d5656a2effbd53`.

## 2026-10-02 authoritative correction — Dynamic Island layered contract

Supersedes the earlier "two independent masks only" front contract.

- Outer Dynamic Island = screen-state artwork on the OLED raster. It remains visibly black.
- Orange privacy indicator = screen-state artwork.
- Physical hardware inside the outer island = FRONT_SENSOR_MASK (left pill) + FRONT_CAMERA_MASK (right circular aperture).
- Camera optic stack must sit deeper than the right physical aperture, never proud of it.
- SCREEN_CONTENT must not overlap the two physical apertures.
- No new renderer depth hacks, no v31/v32 fork, no Camera Control changes.

Execution:
1. RED raster regression: current dynamic state lacks the visible outer black island.
2. GREEN raster: restore the official black outer island and keep orange indicator as artwork.
3. RED depth regression: camera optic must be deeper than camera aperture.
4. GREEN depth stack: move optic inward; preserve physical cutouts and non-overlap.
5. Rebuild canonical v30 and rerun Blender/runtime/Khronos/Storybook gates.
6. Human Gate: outer island visible; inner pill/camera read deeper; camera optic recessed; no light/view overlap artifacts.

## 2026-10-02 execution result — layered Dynamic Island correction

- [100%] #118 + plan synchronized to latest Human Gate contract.
- [100%] Raster RED observed: dynamic screen state had no black outer island.
- [100%] Raster GREEN: restored official outer Dynamic Island artwork; orange privacy dot remains screen-state artwork.
- [100%] Exported-GLB depth RED observed: FRONT_CAMERA_GLASS sat proud of FRONT_CAMERA_MASK.
- [100%] Depth GREEN: camera stack now recedes monotonically behind the right aperture; optic recess >= 0.03 mm.
- [100%] Existing two physical SCREEN_CONTENT cutouts preserved; no screen/hardware overlap regression.
- [100%] Focused front/shading tests GREEN: 17/17.
- [100%] Full fast suite GREEN: 193/193.
- [100%] Blender 5.2.1 runtime geometry contract GREEN.
- [100%] Khronos compat + Meshopt: 0 errors / 0 warnings.
- [100%] Preview tests GREEN: 17/17.
- [100%] Storybook build GREEN.
- [100%] Storybook smoke GREEN across all 11 canonical assets.
- [100%] git diff --check clean.
- [0%] Owner visual Human Gate on exact refreshed candidate.
- [0%] Final Standards + Spec review, commit and push.

Current source revision: `aaec31f14df6396b3f4c41b351f46730d858e489b72234326c413cea42c33b1b`.
Compat GLB SHA-256: `03ec4aeff2c307af1a8aa4d7819964fa0c79c6a7318f3f1909f9b9a7bd93d2c3`.
Meshopt GLB SHA-256: `f72fbeb715b8dcb1bdb9ee23e6001d1ab9680a65af78b9907b628084fa1b3162`.

## 2026-10-02 visual correction — vertical alignment

- [100%] User screenshot identified the real defect as vertical misalignment, not aperture gap.
- [100%] Wrong aperture-gap RED removed; cutter dimensions restored.
- [100%] Measured raster Dynamic Island center: 6.137 mm from body top.
- [100%] Previous physical hardware datum: 7.79 mm → 1.653 mm too low.
- [100%] FRONT_SENSOR_MASK + FRONT_CAMERA_MASK + camera stack moved to 6.14 mm visual center.
- [100%] Overlap regression now samples actual physical-mask node centers instead of stale 7.79 mm literal.
- [100%] Focused front/shading suite GREEN: 17/17.
- [100%] Storybook rebuilt with refreshed v30 runtime.
- [0%] Owner visual PASS on refreshed web candidate.

## 2026-10-02 execution result — vertical Dynamic Island alignment correction

- [100%] Restored official physical front-hardware datum: 7.79 mm from body top.
- [100%] Restored generator metadata/validation to the same 7.79 mm engineering source of truth.
- [100%] Tight RED reproduced on the actual defect: dynamic-state raster center 6.137 mm vs official hardware datum 7.790 mm (delta 1.653 mm).
- [100%] Rebuilt the dynamic screen-state raster by shifting only the software Dynamic Island artwork 28 px downward; orange privacy indicator remains screen-state artwork.
- [100%] Alignment regression GREEN against the official dimensional ledger.
- [100%] Physical sensor/camera cutouts, recessed camera stack, Camera Control and Three.js material/runtime policy unchanged.
- [100%] Focused front/shading tests GREEN: 18/18.
- [100%] Full fast suite GREEN: 194/194.
- [100%] Blender 5.2.1 runtime geometry contract GREEN.
- [100%] Khronos compat + Meshopt: 0 errors / 0 warnings.
- [100%] Preview tests GREEN: 17/17.
- [100%] Storybook build GREEN.
- [100%] Storybook smoke final run GREEN across all 11 canonical assets.
- [100%] git diff --check clean.
- [0%] Owner visual Human Gate on exact refreshed candidate.
- [0%] Commit/push remain blocked until Human PASS.

Current source revision: `20b5ed1bb3cdb0a765414dcf301bd8c071fe5285767df3d5bedb92a2696693ef`.
Compat GLB SHA-256: `2b24dadca5332555e3f4585215f2d8ec339be7d478e47b81597d63054e4ef564`.
Meshopt GLB SHA-256: `4d42c7a1bc5f59cc2123c98d254594ca936e2dcaac8d40e2d8fbfb655f8d0fa5`.

## 2026-10-02 final microfix — island spacing + camera detail mask

- [100%] Kept the outer Dynamic Island raster silhouette unchanged.
- [100%] Moved the physical right camera cluster from x=5.05 mm to x=6.72 mm so outer edge padding matches the left pill.
- [100%] Edge padding is now ~2.95 mm on both sides; regression enforces <=0.15 mm imbalance.
- [100%] Moved the orange privacy indicator to the midpoint between pill and camera (x=648 px).
- [100%] Added embedded `front_camera_detail_mask.png` to `MAT_FRONT_OPTIC`.
- [100%] Detail image uses glTF-portable MULTIPLY: dark baseColorFactor remains intact; mask only modulates it subtly.
- [100%] No extra overlay geometry; camera depth/recess stack unchanged.
- [100%] Focused front/shading GREEN: 21/21.
- [100%] Full fast suite GREEN: 197/197.
- [100%] Blender 5.2.1 runtime geometry GREEN.
- [100%] Khronos compat + Meshopt: 0 errors / 0 warnings.
- [100%] Preview tests GREEN: 17/17.
- [100%] Storybook build GREEN; smoke GREEN across all 11 assets.
- [100%] git diff --check clean.
- [0%] Final owner visual PASS; commit/push remain HOLD until PASS.

Source revision: `1005f6a4807438ac1bef3afbb5a0a3f6a58b483d42ca8e6a3a8c98d77aa72236`.
Compat SHA-256: `98d00b06db6ae13d57279867545011807784e0ec26c65f411681f8f22e5b34e6`.
Meshopt SHA-256: `75c0b5d95d597cb0444b53a3d2592b00de5e0fdd00e87235fc6e125ed1d03124`.

## 2026-10-02 rear-camera hard-edge fix — debug/tdd/implement/review

Root cause:
- Rear circular camera parts already used 192 radial segments.
- The visible runtime defect was not circumference density.
- `CAMERA_HOUSING`, `CAMERA_HOUSING_SEAT`, and `CAMERA_1/2_RING` exported with only two levels across their thickness: Blender bevel modifiers were not materialized into the GLB, leaving square cross-sections.

Execution:
- [100%] Reverted unrelated BODY_ALUMINUM normal experiment; original body bevel + Weighted Normal policy restored.
- [100%] Added exported-GLB regression `test_rear_camera_protrusions_export_rounded_depth_profiles`.
- [100%] Observed RED: `CAMERA_HOUSING` exported depth levels = 2.
- [100%] Added iPhone-local `apply_runtime_bevel()`; applies existing bevel geometry before save/export.
- [100%] CAMERA_HOUSING: 0.24 mm, 4 segments.
- [100%] CAMERA_HOUSING_SEAT: 0.11 mm, 4 segments.
- [100%] CAMERA_1/2_RING: 0.13 mm, 4 segments.
- [100%] CAMERA_1/2_BEVEL: 0.07 mm, 3 segments.
- [100%] CAMERA_1/2_GLASS: 0.06 mm, 3 segments.
- [100%] No radial-segment increase and no global remesh.
- [100%] Regression GREEN on exported GLB.
- [100%] Full fast suite GREEN: 198/198.
- [100%] Blender 5.2.1 runtime geometry GREEN.
- [100%] Khronos compat + Meshopt: 0 errors / 0 warnings.
- [100%] Preview tests GREEN: 17/17.
- [100%] Storybook build GREEN; smoke GREEN across all 11 assets.
- [100%] git diff --check clean.
- [100%] Code review: no new blocking Standards or Spec findings for this camera fix. Existing process debt: docs/agents/issue-tracker.md missing.
- [0%] Owner visual Human Gate on exact refreshed side/rear candidate.
- [0%] Commit/push remain HOLD until Human PASS.

Source revision: `f51b1ecea9e0815a5c5b004355fa85960bd94d3feaced089352243ad56c34720`.
Compat GLB SHA-256: `24bd4bad1de5df8e1b3824b0cdc85cd6796fd78c7c8966cd848b054fe3f32bf1`.
Meshopt GLB SHA-256: `b9957e6cc4146fd25db8cdb32c782a1fb88ebb19f7aa271556f4aae2a470cdd4`.

## 2026-10-02 authoritative correction — Dynamic Island system-owned overlay

Supersedes the earlier rule that the baseline outer Dynamic Island belongs to individual screen-state raster artwork.

- Apple research: `docs/research/iphone-17-dynamic-island-system-state-2026-10-02.md`.
- `SCREEN_CONTENT` is arbitrary clean Home/app/site artwork and does not own the baseline island.
- Active ordinary screen states use `dynamic_island_state = idle`.
- The baseline black island is composited as a system-owned screen layer above `SCREEN_CONTENT`.
- Physical `FRONT_SENSOR_MASK` / `FRONT_CAMERA_MASK` and optic depth remain independent under-glass hardware at the official 7.79 mm datum.
- Privacy indicators are conditional system state, not baked into ordinary Home/site rasters.
- No coplanar island mesh, no Three.js depth hack, no v31/v32 fork.

Execution evidence:
- [100%] RED state-contract test: active screen state had no independent Dynamic Island state.
- [100%] RED compositor test: website raster had no system-owned idle mask.
- [100%] RED generator/runtime contracts: canonical source still embedded the old dynamic-state raster.
- [100%] GREEN: clean `SCREEN_CONTENT` + independent idle CanvasTexture compositor.
- [100%] White-site browser repro: `screen_website`, no screen/console/network errors, baseline island visible.
- [100%] Focused front/shading: 9/9 + 15/15.
- [100%] Full fast: 200/200.
- [100%] Blender 5.2.1 runtime geometry: GREEN.
- [100%] Khronos compat + Meshopt: 0 errors / 0 warnings.
- [100%] Preview tests: 19/19; Storybook build GREEN; smoke 11/11.
- [100%] `git diff --check` clean; CRLF conversion warnings remain informational.
- [100%] Standards review complete: premature evidence/status claim corrected; remaining minor test-seam note is non-blocking; no runtime correctness blocker found.
- [100%] Spec review complete: 1 minor finding (idle silhouette is a reference-derived approximation, not published Apple geometry); current white-site baseline-island behavior matches the scoped contract.
- [100%] Owner Human Gate PASS on the exact refreshed candidate via Tailscale Storybook; commit/push unblocked.

Source revision: `07a2a0befde9e6f7c3a209db1635a5dda1d375ea92342c4d81a38a1f8ed2368f`.
Compat SHA-256: `2db54b01ca3ac2b043d1600963f6f49cb9647f76fe99194d0532e3565e1cf544`.
Meshopt SHA-256: `a30f455fcd515ed5a7029e32bfe04316ae949d53889c007329ddf1412aa5a65f`.

## 2026-10-02 post-ship Apple dimensional audit correction

Authority: `docs/research/iphone-17-post-ship-dimensional-audit-2026-10-02.md` and Apple iPhone 17 Dimensional Drawings dated 2025-09-09.

Scope remains the existing v30 line. No v31/v32 fork.

TDD / implementation:
- [100%] Rear camera depth RED: exported plateau 0.72 mm vs Apple 1.78 mm.
- [100%] Rear camera depth GREEN: plateau 1.78 mm, camera glass 3.45 mm from back glass.
- [100%] Bottom RED: exported sixth speaker port present.
- [100%] Bottom GREEN: 3 mic + 5 speaker, Ø1.35, Apple spacing; screws Ø1.50 at Apple datums.
- [100%] Side-control RED: Action 11.60 mm vs Apple 6.90 mm.
- [100%] Side-control GREEN: Action 6.90, Volume ± 11.20, Side 17.70, Camera Control 17.10 mm; center datums preserved.
- [100%] Rear-mic RED: X datum 22.675 mm from left vs Apple 20.54 mm.
- [100%] Rear-mic GREEN: 20.54 × 22.48 mm center, Ø1.00.
- [100%] Focused iPhone regression: 28/28.
- [100%] Code review: no Spec blocker; two minor maintainability findings fixed (unused import; stale Camera Control helper defaults).

Full verification:
- [100%] Full fast: 204/204.
- [100%] Blender 5.2.1 `--factory-startup` geometry: GREEN.
- [100%] Khronos compat: 0 errors / 0 warnings.
- [100%] Khronos Meshopt: 0 errors / 0 warnings.
- [100%] Preview tests: 19/19.
- [100%] Storybook production build: GREEN.
- [100%] Browser smoke: 11/11 canonical assets.
- [100%] Targeted `screen_website`: correct state, console errors [], failed responses [].
- [100%] `git diff --check`: clean.
- [0%] Owner Human Gate on corrected rear / bottom / left side / right side / front.
- [0%] PR #119 update / commit / push / main landing remain HOLD until Human PASS.

Manifest source revision: `6357d9fdeac268e8506b6e999a69eed1e957a476de8144b82d6e47d959a82347`.
Compat SHA-256: `7a10c91495d016899bb84837a08d31a89baa8c3b2e071cc4831ec7462f702893`.
Meshopt SHA-256: `664ac9f08a29be042575dcac6639d63502b5b6f9f2738a58981547b371cceff3`.


## 2026-10-03 PBR realism and official finish variants

Authority:
- `docs/research/iphone-17-finish-pbr-reference-2026-10-03.md`
- Apple iPhone 17 Technical Specifications / official product viewer.

Scope remains the same canonical v30 geometry. Finish variants do not duplicate GLB assets.

PBR / fasteners:
- [100%] RED exported-GLB contract: `MAT_FASTENER` had no normal texture.
- [100%] GREEN exported-GLB contract: fastener, anodized aluminum, edge/camera housing and back glass carry embedded normal + roughness maps.
- [100%] Bottom screw heads remain Apple Ø1.50 geometry; pentalobe socket is tangent-space normal + roughness detail.
- [100%] Acoustic opening silhouette remains geometry; grille weave remains normal-map microdetail.
- [100%] Required visible PBR meshes export `TEXCOORD_0`; runtime exporter triangulates normal-mapped runtime copies for stable tangent generation without changing authored source geometry.

Finish variants:
- [100%] Official Apple finish names: Black, White, Mist Blue, Sage, Lavender.
- [100%] Display tints calibrated from official Apple product-viewer renders; Apple does not publish canonical material RGB values.
- [100%] One GLB, one geometry, shared PBR maps; finish changes base material colors only.
- [100%] Storybook viewer exposes a finish selector.
- [100%] Storybook exposes generic + five first-class iPhone 17 finish stories.
- [100%] Blender extension exposes Finish + Set Finish and preserves the same five variants.
- [100%] Preview unit/contracts after variant UI: 21/21.

Final gate:
- [100%] Final canonical rebuild after PBR/provenance metadata. Source revision: `9ce24d6e6e292cd734d9e8be2993a2a37c1e9e24848e32ec27fe0f39752c5a65`.
- [100%] Full fast exact current WIP: 207/207.
- [100%] Blender 5.2.1 `--factory-startup` geometry: GREEN.
- [100%] Khronos compat: 0 errors / 0 warnings; SHA-256 `da2a08021a5e02f2af8d9131ed8617cb03d0979346e12893008011a875fa703f`.
- [100%] Khronos Meshopt: 0 errors / 0 warnings; SHA-256 `02f55142da9a718cc69814c9f2343277d2d9847e9d453f4fad665add768c0a6c`.
- [100%] Preview unit/contracts: 21/21; Storybook production build GREEN.
- [100%] Canonical Storybook smoke: all 11 canonical assets passed.
- [100%] Browser finish sweep: Black / White / Mist Blue / Sage / Lavender all load from the same GLB, preserve required PBR maps, correct runtime colorway state, console errors [], failed responses [].
- [100%] Combined Mist Blue + `screen_website` + Dynamic Island compositor gate: GREEN, console errors [], failed responses [].
- [100%] `git diff --check 394951d`: clean; CRLF notices informational only.
- [0%] Owner Human Gate: bottom pentalobe fasteners, back/camera materials, all five finishes.
- [0%] PR #119 remains HOLD/draft until Human PASS.
