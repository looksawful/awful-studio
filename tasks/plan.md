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
