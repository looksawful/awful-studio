# iPhone 17 v30 topology rebuild — implementation handoff

Latest owner decision: 2026-10-05. Earlier dated sections are historical evidence.
Repository: looksawful/awful-studio
Branch: `agent/118-topology-rebuild-v2`
Shared ledger: GitHub issue #118
PR #119 remains DRAFT/HOLD. Do not merge it.

Preview consolidation checkpoint — 2026-10-05: all four selected devices now
use the same Storybook catalog and viewer. See `preview/README.md` for exact
hashes, writer branches, archive policy and publication contract. The common
local Titan landing is http://127.0.0.1:6006/?path=/story/models-catalog--catalog.
GitHub Pages is still the older Sep28 build; its four device GLB hashes were
fetched and differ from these review snapshots. Independent iPad/MacBook
writer checkouts retain production ownership; their current coherent GLBs
are copied as immutable WIP review evidence, not rebuilt or promoted here.
Catalog and primary stories now select the same pinned files. Older checkout
device runtimes are retained for consumers and excluded from review serving.
Preview25/25, fast209/209 (this checkout), static build and all11 browser
stories PASS. Existing native/human gates and the display-frame RED remain.
No commit/push/merge/deploy. This updates viewing context, not the model backlog.

## Goal

### Owner decision and closeout plan — 2026-10-05

Execution remains in issue #118 and Asana task 1219036864546294. This section
records requirements and order, not a second backlog. Continue the existing
`agent/118-topology-rebuild-v2` writer; starting HEAD is `fcc2c47`.

The owner requires an interactive **existing Storybook / Three.js viewer at
every meaningful stage**, with orbit/zoom, full materials and the actual GLB
triangle wireframe. Static Blender sheets do not replace this review surface.
Reuse the viewer, stories, catalog generator, exporter, Meshopt and runtime
contracts. No new viewer, generic topology framework, model-version fork or
parallel production pipeline.

Active appearance reference: exact current GLB SHA-256 `68bcd22831e427a077ddfd48662e41bbe8ef46ebda0359c7153b9e3579afeae0`,
frozen on Oct05 with saved Blender/native/export files, source/viewer inputs,
render profile and control captures. The single primary Storybook entry loads
`preview/generated/iphone-review/frozen-current-2026-10-05/model.glb`, verifies
its checksum before parsing, and pins its material policy, finish palette,
screen images, exposure, environment/light intensity and FOV. Freeze means
appearance evidence, not accepted topology or whole-device HUMAN PASS.

Historical `117546a` (64,554 triangles) is archived under
`preview/generated/iphone-review/archive/117546a-before-topology`, excluded from
active stories/static publication. It may inform a diagnosed regression; it is
not the current review target. Camera accepted appearance remains frozen; use
`48b271a` only when isolating a demonstrated camera regression. Compare each
new working candidate against the frozen current look with matched settings.

#### Requirements and Definition of Done

Owner clarification after inspecting two wireframes (Oct05): current whole-device
topology is **NOT ACCEPTED**. The primary task is an intentional, optimized mesh
with segments chosen for each feature, inspectable in both Blender and actual
exported GLB, while preserving high-quality render. Low triangle count, manifold
status and a good shaded image alone do not meet this requirement. This decision
supersedes older claims that implementation is finished and only approval remains.

Inspect each component separately as well as the full assembly: the existing
wireframe draws all mesh triangles, so front/rear/glass/seat layers overlap.
Keep the full exported triangle view honest; do not hide triangulation or replace
it with an aesthetically simplified line proxy to claim a topology fix. Sparse
triangles on a truly planar panel are valid; uniform dense quads are not a goal.
Choose curved-edge/bevel/lens/aperture segmentation from silhouette error and
highlight continuity at the agreed closest review zoom, then document the local
choice. Require deliberate edge flow, controlled triangulation and no unnecessary
layers/segments, slivers or fans in changed feature regions. Recheck UV/tangents,
normal/roughness compatibility, dimensions and exports after each actual repair.

Next Stage 3 slice: attribute the supplied wireframe observations to individual
actual GLB meshes, compare their authored Blender faces and exported triangles,
and select the first failing panel/edge region. Source and exported mesh quality
are separate gates; all existing functional contracts remain required. Preserve
the accepted camera appearance; topology acceptance for the whole assembly is
still open. USB-C shading observation remains a separate diagnostic question.

- Silhouette, glass/metal highlights, contact edges, openings, buttons and rear
  optics must have no owner-visible quality loss against the reference under
  matched views. Triangle count is secondary; increase only a failing local
  region when evidence demonstrates the need. RMS is diagnostic, not approval.
- Production-visible geometry is materialized: no runtime BOOLEAN/BEVEL/
  WEIGHTED_NORMAL dependency, no dense HIGH reference in native delivery.
  Author intentional triangles/quads; zero source n-gons, non-manifold edges,
  zero-length edges or degenerate faces on changed hard-surface meshes.
- Preserve SCREEN_CONTENT and on/off/lock/website/resume states; software
  Dynamic Island artwork; FRONT_SENSOR_MASK / FRONT_CAMERA_MASK under glass;
  official 7.79 mm front-hardware datum; privacy indicator as screen state.
  No coplanar island mesh, depth hack or runtime geometry offset.
- All five finishes tint the body and intended aluminum controls in both web
  and native consumers while retaining individual normal/roughness maps.
- Control UV closing walls must not span/overlap the full unwrap strip. Bake
  compatibility must be demonstrated after any UV change; rejected body macro
  maps stay excluded. Geometry owns silhouette; maps carry shallow detail.
- Catalog, manifest, all consumed bake inputs, saved blend, compat GLB,
  Meshopt GLB and native bundle must refer to one reproducible candidate.
- Exact Blender 5.2.1, focused contracts, full fast suite, exported world-space
  geometry, Khronos compat+Meshopt, provenance, Storybook build/browser smoke,
  canonical Media Catalog resolution and diff check must pass freshly.
- Standards + Spec review must have no unresolved blocker. Final whole-device
  HUMAN PASS must name the inspected candidate; then commit/push and the
  authorized delivery/PR action. #119 remains DRAFT/HOLD until reconciliation
  with the actual implementation branch; no automatic merge or release.

#### Ordered stages and interactive checkpoints

1. **[100%] Reconstruct current state.** Git, current issue/Asana, handoff and
   relevant chats checked. Candidate `fcc2c47`; old named checkout is stale.
2. **[100%] Restore trustworthy Storybook review.** Reproduce catalog drift and
   copied-control finish failure; fix minimally. Load current + historical
   reference through the existing viewer. Verify orbit, zoom, render/wireframe
   switching and exact GLB identity in a real browser. Show this checkpoint.
3. **[45%] Decide local quality corrections.** Exact appearance frozen, review
   alternatives archived, 51 exported nodes and native-only parts inventoried;
   existing viewer can isolate all leaves and nine groups. Recursive design is
   recorded below. Next: first display-frame saved/exported RED/GREEN pilot.
   Inspect front/rear, both rails,
   bottom, camera and screen edges in render/clay/wire, all finishes. Record
   each actual defect against this candidate. Keep accepted regions intact.
4. **[0%] Repair production geometry and bakes.** One demonstrated defect per
   RED/GREEN slice; repair UV seam / bake compatibility, HIGH exclusion,
   provenance input coverage and modifier guard. Fix any owner-visible shape
   or shading defect locally. Rebuild via existing pipeline, show each slice
   in the same Storybook and repeat matched reference views.
5. **[0%] Verify exported delivery and consumers.** Actual exported contour/
   dimensions/material coverage, Meshopt, native bundle, fingerprints; focused
   tests then full fast once; exact-candidate browser + Media Catalog checks.
   Render/wire checkpoint remains inspectable.
6. **[0%] Review and human decision.** Separate Standards/Spec review, then
   owner whole-device render/wire PASS or explicit corrections. Loop only the
   affected slice. No approval from counts, screenshots alone or old gates.
7. **[0%] Close authorized delivery.** After PASS, commit/push, reconcile the
   existing draft/branch, perform only authorized integration, verify the
   delivered hashes/consumer, update #118/Asana/handoff and archive experiments
   only with appropriate ownership. The project stays WIP until these gates.

#### TDD seams already requested by the owner

Use observable exported GLB/world-space/native/browser behavior, not private
helper AST or constant-vs-constant checks. Each slice: observed RED on the
exact candidate -> smallest source fix -> same GREEN -> matched interactive
checkpoint. Test catalog drift without regenerating the committed file first;
load actual GLB materials for all-finish map-preservation tests; inspect saved
control UVs and packaged visible objects in Blender; mutate a bake in an
isolated fixture to prove stale delivery rejection; prove exported contour
coverage against deliberate diamond-like contour loss. Keep first RED logs.

Needed text is limited to stage/reference labels, model identity, concise
inspection instructions, defect/verdict records and this existing handoff.
No marketing copy, new master specification or copied execution queue.

#### Stage 2 result — 2026-10-05

The earlier two-version checkpoint is superseded by the frozen-look checkpoint.
Storybook is served on Titan at `http://127.0.0.1:6006/` from the existing
static build. Single iPhone story: `models-devices--i-phone-17`, labelled
FROZEN LOOK 05.10.2026 (68bcd228). Select mode `render` (internal
value `texture`), `wireframe`, `clay`, or `normals`; drag to orbit, wheel to
zoom, switch finish/screen state. Wireframe uses actual loaded GLB geometry,
not an edge proxy. `part` selects whole assembly, one of nine groups or any of
51 existing GLB mesh nodes. Selecting SCREEN_CONTENT preserves its multi-material
group. Selection changes visibility only; transforms/parents/geometry stay intact.
`fit` frames the selected part. Five finishes and screen states remain controls,
not competing iPhone stories. No historical version is in the active story list.
Wireframe uses a disposable light-colored diagnostic material on the same loaded
triangle buffers so dark frame/optic leaves remain readable. Render restores the
original materials and PBR maps. No depth/order/geometry workaround; this changes
inspection line color, not the frozen rendered appearance.
Finish and screen controls update saved original PBR materials even while a
diagnostic material is visible. Browser regressions cover both Black/Off and
White/Home selected in wireframe, then restored render; line color stays neutral.

Observed RED: stale catalog (tests previously regenerated it before checking),
four exported aluminum control names skipped by finish mapping, and the same
names missing calibrated metal reflection policy. Minimal repairs retain all
individual bake maps and leave production geometry/binary delivery unchanged.
Current compat SHA-256 remains `68bcd22831e427a077ddfd48662e41bbe8ef46ebda0359c7153b9e3579afeae0`;
reference SHA-256 is `da2a08021a5e02f2af8d9131ed8617cb03d0979346e12893008011a875fa703f`.

Fresh evidence: preview 23/23; Python fast 209/209; exact Blender 5.2.1
ten saved-candidate contracts PASS; Khronos compat and Meshopt 0 errors /
0 warnings; manifest checks PASS for declared inputs only; Storybook build
PASS; extended real-browser smoke PASS for 11 canonical assets + reference,
all five finishes/map identity, triangle wireframe/render, orbit and zoom;
diff check PASS. Declared-input verification does not close omitted bake input
coverage. Full build still reports its large-chunk warning; runtime captures
record existing THREE.Clock deprecation and a current GLB driver shader
precision warning. Do not claim warning-free final runtime acceptance.

Matched front / three-quarter / rear / bottom render, wire and clay captures
were inspected. Initial quality observation: the USB-C inner edge/insertion
reads brighter in the pre-optimization reference while the current cavity is
darker/flatter. This is an open macro-review question, not an established
geometry root cause. Inspect identical close-up views before choosing a fix.
No whole-device visual PASS has been inferred from these images. Native finish,
UV/bake seam, HIGH exclusion, provenance coverage, exported-contour regression
and final consumer gates remain stages 3-7. No commit/push/merge this session.

Oct05 actual-buffer wireframe audit: current 11,538 vs historical 64,554 tris.
BACK_GLASS is 268 vs 780; SCREEN_CONTENT 268 vs 2,332; CAMERA_HOUSING 164 vs
10,540. DISPLAY_GLASS_SEAT and DISPLAY_BEZEL are unchanged at 780 each; their
maximum local indexed edge lengths are 150.412 and 148.6835 mm. These measurements
identify review regions, not automatic defect thresholds. Both assets contain
long planar edges. The two supplied cropped screenshots lack story/hash metadata;
do not assign either image to a specific version based on appearance alone.

#### Recursive work design after freeze

Complete leaf/group inventory and source correspondence are research, not another
execution queue: `docs/handoffs/iphone17-topology-component-research.md`. Issue
#118 and Asana task 1219036864546294 continue to own work/status.

Order: (1) display bezel and display seat pilot; (2) back/screen panels, logo and
native-only SCREEN_GLASS; (3) body corners/rails/side and bottom cells; (4) each
control and antenna with its corresponding body boundary; (5) USB cavity/tongue,
each acoustic port and screw; (6) front masks/optic layers/receiver and screen
states; (7) rear housing/seat, each camera's six leaves, flash/ring/mic; (8) whole
device, native bundle, export/consumer/provenance gates and final owner decision.

Each focused slice has at most one existing leaf or shared construction family.
If a shared helper changes, verify every existing caller. For each slice:
record its source object/region and actual GLB node, functional purpose, exact
defect, mating neighbors and UV/bake constraints; reproduce RED on saved Blender
or exported buffers; change only needed geometry/segments; materialize relevant
production modifiers; update affected UV/bakes and fingerprint inputs; export
through the existing pipeline; focused GREEN; inspect isolated leaf -> mating
neighbors -> group -> full assembly in the same Storybook render/wireframe.
An approved leaf is retained; it is not rebuilt simply because another fails.

Use the frozen baseline and exactly matched macro viewpoints at an agreed close
review zoom to choose segmentation. Diagnose silhouette deviation/highlight
continuity before assigning numerical tolerances. Keep flat interiors sparse;
do not impose universal quads, density, aspect ratio or triangle cap. A frame cap
must have deliberate authored triangles/quads and controlled export triangulation,
not an incidental n-gon triangulation. Acceptance is per region and assembly.

"Assembly" is not joining all objects into one mesh. Existing root/anchors/names,
material and screen-state boundaries remain. Weld only a continuous physical skin
whose mating boundary is proven compatible; preserve distinct glass, controls,
optics, decal and screen surfaces. No bulk object joins or hierarchy changes to
save draw calls. Body's disconnected source cells need their own boundary audit.

Pinned Blender 5.2.1 saved-file audit on Oct05: source and plugin bundle each have
56 mesh objects (52 hide_render=False); delivery.blend has 52 meshes and no HIGH.
Web exports 51 meshes: SCREEN_GLASS is native-only. Source/plugin keep four hidden
references: BACK_GLASS_SEAT, BODY_ALUMINUM_HIGH and CAMERA_1_SEAT/CAMERA_2_SEAT.
Plugin-bundle HIGH exclusion is therefore still unmet even though delivery.blend
is clean. Visible native modifiers remain on antennas, FRONT_RECEIVER_MIC, USB
cavity/tongue and SCREEN_GLASS. DISPLAY_BEZEL and DISPLAY_GLASS_SEAT each have
two authored n-gons; SCREEN_GLASS has three. These are concrete pilot/native
work items; the existing ten passing contracts do not cover all these requirements.

Freeze/isolation milestone verification: mutation RED -> SHA guard GREEN;
unfrozen primary story RED -> pinned story GREEN; absent part isolation RED ->
all 51 leaves/nine groups GREEN in a real browser with unchanged parents/world
transforms and assembly restoration. Preview24/24, fast209/209, exact Blender
ten contracts, declared-input checks, Khronos compat/Meshopt 0 errors/0 warnings,
Storybook build and extended browser smoke PASS. Driver/Clock/large-chunk warnings
remain recorded. Standards/Spec milestone reviews: 0 findings each, worst none.
No geometry repair, commit/push/merge or whole-device HUMAN PASS in this milestone.

#### Historical implementation records below

The following Oct03/Oct04 records are provenance, not current completion claims.
Any older "release-candidate quality" / "only Human Gate remains" statement is
superseded by the Oct05 owner topology rejection, frozen reference and recursive
work design above. Old camera approval describes accepted appearance only.

Finish production topology for the entire canonical iPhone 17 v30, not only the camera. Preserve Apple datums, materials, finishes, names, roles, anchors and v30 identity while replacing dense, n-gon-heavy or brittle source/runtime meshes with intentional low-poly hard-surface topology.

## Frozen principles

- Geometry owns silhouette, openings/cavities, physical depth transitions, contact edges and profile-visible forms.
- Tangent normal / roughness owns shallow microdetail only.
- No global remesh and no generic topology framework.
- Exported GLB is the shipping seam.
- Changed runtime-visible hard-surface meshes must have intentional triangles/quads, zero n-gons and zero non-manifold edges.
- Triangle reduction is secondary to shape/shading correctness.
- Camera Human Gate is already PASS and remains frozen.

## Camera — frozen PASS

- 8 visible camera meshes: 1,288 tris total.
- 40-class visible silhouette.
- Housing/seat horizontal quad-strip caps.
- 0 n-gons / 0 non-manifold.
- Frozen silhouette error: 0.038348 mm.
- Deterministic 512 bake maps, 24 px margin.
- Housing/ring/bevel normals retained; glass normal omitted.
- Camera Human Gate remains PASS and is not reopened by later body work.

## Completed whole-model topology slices

Relevant commits on the rebuild line:

- `337e79e` — clean low-poly side-control bake.
- `532d393` — bottom hardware topology.
- `346f127` — back glass and front hardware topology.
- `4bb11b8` — rear optics topology.
- `2dd3903` — side-control bake/topology contract.
- `48fa798` — authored v30 body topology.
- `a88b70d` — body-cell angle normalization / contour preservation.
- `a474117` — rebuilt canonical v30 delivery artifacts.

### BODY_ALUMINUM

Current runtime body on the verified generated blend:

- 2,832 vertices.
- 2,822 faces.
- 5,644 triangles.
- 0 n-gons.
- 0 non-manifold edges.
- 0 zero-length edges.
- 0 tiny/degenerate faces.
- 1 UV layer.
- no runtime bevel or weighted-normal modifier.

The old authored body baseline was 7,308 source triangles; current body is ~22.77% lower. The old evaluated body was ~20,620 triangles; current authored runtime body is ~72.63% lower.

Apple Detail A uses 28 samples per quarter in the current builder. A Wolfram numerical check of the canonical quintic corner Bezier gives a maximum polyline deviation of about 0.01060 mm at 28 segments/quarter. For comparison, 24 segments/quarter is ~0.01436 mm and 16 segments/quarter is ~0.03225 mm.

The body cutout architecture is local manifold cells:
- side controls use capsule cells;
- bottom USB/mic/speaker/screw openings use local cells;
- corner acoustic cells follow the actual Apple bottom curve;
- no global boolean-derived runtime rail topology.

A regression contract now preserves every authored capsule contour direction. This fixed the pointed/diamond-like control recess regression while keeping the mesh manifold.

### Body shading / bake decision

The clean low body retains the existing anodized-aluminum normal and roughness maps on the metal material.

A dedicated high→low macro-normal experiment tested metal-only bake targets at 0.15 / 0.25 / 0.35 mm ray distance. Those maps were effectively flat and produced no meaningful visual improvement. This is expected because the remaining high/low differences are primarily silhouette/contact-edge geometry, which a normal map must not be asked to repair.

Therefore:
- do not commit the rejected experimental body macro-normal maps;
- keep silhouette/contact edge improvements geometric;
- keep the existing subtle anodized micro-normal + roughness material detail;
- camera and side controls remain the places where committed tangent-normal bakes materially carry accepted high→low detail.

Primary-source bake notes are in:
`docs/research/iphone17-body-bake-primary-sources-2026-10-04.md`.

## Current runtime totals

From `assets/device_mockups/iphone_17/runtime/v30/iphone_17_v30.asset.json`:

- runtime triangle count: 11,538.
- old pre-rebuild runtime baseline: 64,554 triangles.
- reduction: ~82.13%.
- compat GLB: 4,748,960 bytes.
- meshopt GLB: 4,224,172 bytes, ~11.05% smaller than compat.
- old compat baseline: 6,192,648 bytes, so current compat is ~23.31% smaller.

## Fresh verification on 2026-10-04

Blender 5.2.1 runtime contracts on the same generated candidate:

- `iphone_v30_body_topology_contract.py` — GREEN.
- `iphone_v30_body_visible_material_contract.py` — GREEN.
- `iphone_v30_body_cell_shape_contract.py` — GREEN.
- `iphone_v30_topology_contract.py` — GREEN.
- `iphone_v30_screen_topology_contract.py` — GREEN.
- `iphone_v30_controls_topology_contract.py` — GREEN.
- `iphone_v30_bottom_topology_contract.py` — GREEN.
- `iphone_v30_surface_topology_contract.py` — GREEN.
- `iphone_v30_rear_optics_topology_contract.py` — GREEN.

Fast suite:
- 208 / 208 PASS.

Khronos glTF Validator `2.0.0-dev.3.10`:
- compat: 0 errors / 0 warnings / 49 infos / 0 hints.
- meshopt: 0 errors / 0 warnings / 50 infos / 0 hints.
- retained evidence hashes were refreshed to the current GLBs.

## Review evidence

Current generated previews are the canonical review surfaces:
`assets/device_mockups/iphone_17/previews/low_v30/`

The side-control recess regression that appeared as pointed/diamond-like openings is fixed in the latest generated source and guarded by `tests/runtime/iphone_v30_body_cell_shape_contract.py`.

Do not use the untracked `assets/device_mockups/iphone_17/prototypes/` directory as source of truth. It contains iterative diagnostics, including rejected body-bake experiments. Source modules, runtime contracts, generated delivery artifacts and issue #118 are authoritative.

## Next work

### Resume verification on 2026-10-04

The requested rebuild had already reached `ad0d8b2` before this continuation.
This session retained the exact delivery rather than regenerating unchanged binaries.
Fresh checks: Blender 5.2.1 (9e2066aef7ef), nine topology/material contracts
plus `iphone_v30_geometry_contract.py` PASS; full fast suite 209/209 PASS;
compat and meshopt Khronos 2.0.0-dev.3.10 both 0 errors/0 warnings;
manifest hashes, GLB provenance and structural round-trip checks PASS.
These round-trip checks are structural; they are not a browser visual test.

Added pure fast regression `test_iphone_body_cell_contour.py`, exercising
8/12/16 capsule arc samples. Removing authored hole angle insertion in an
isolated function copy reproduces RED (2.1496046 mm contour loss); current
function is GREEN (about 1.65e-14 m loss). Production geometry is unchanged.

Durable evidence in `assets/device_mockups/iphone_17/evidence/`:
- `topology_resume_verification_2026_10_04.json` (nine contracts).
- `topology_resume_delivery_2026_10_04.json` (exact GLB hashes and Khronos).
- `body_bake_ab_2026_10_04/` (prototype A/B images, rejected map, measured deltas).
- `topology_resume_clay_wire/` (fresh left/right/bottom diagnostic renders).

Bake qualification: existing metal-only prototype renders were remeasured,
not rebaked on the final candidate. Side RMS on 0-255 RGB is 0.1166 left /
0.1848 right; bottom 8.5084 and three-quarter 3.2807. Thus the earlier
"no material visual gain" statement must not be read as zero delta everywhere.
The retained map is mostly flat but has a conspicuous magenta artifact.
No evidence justifies promoting that macro-normal to production. Keep the
accepted micro-normal/roughness and clean geometry. Experimental target
nonmanifold counts do not describe the production body.

Review: focused contour test/evidence diff has no blocking Standards finding;
it tests observable vertex preservation and changes no runtime behavior.
Spec/#118: body remains 2,832 verts / 2,822 faces / 5,644 tris, clean topology,
no runtime modifiers. Latest material side previews show rounded recesses.
The dark bottom material preview and orthographic diagnostic sheets are
insufficient to approve whole-device appearance. Human Gate remains pending.
No fresh browser interaction or five-finish visual gate was executed in this
continuation. Do not claim release/ship approval. PR #119 remains draft/HOLD.

Resume from this Git branch and issue #118. Inspect the whole-device candidate
in material/clay/wire and record the owner's decision; fix any exact reported
defect before final acceptance. ArtifactBridge room instrumentation was
unavailable (`agent_connector_required`); Git/issue remain the handoff source.

Technical implementation is at release-candidate quality. The remaining owner-facing gate is a whole-device Human Gate using render / clay / wire views from the latest generated model.

If that Human Gate passes:
1. record PASS in issue #118 and the owning project/task system;
2. run final review against the rebuild baseline;
3. keep PR #119 on HOLD unless the owner separately authorizes its landing;
4. do not reopen the frozen camera aesthetics unless a real production-equivalence deviation is found.

If the Human Gate finds a defect, fix only the exact affected topology slice and rerun its focused contract plus the full runtime/fast gates.


## 2026-10-05 late — Ticket #138 display-frame topology repair

This checkpoint supersedes the older "technical release-candidate quality" wording
above. The owner's Oct05 whole-device topology rejection still stands. Only the
display-frame slice is accepted by engineering evidence here; whole-device Human
Gate remains pending.

Baseline before this slice: commit `134f03f3a231a77fd62f7139f90815af63f0913a`.
The frozen appearance reference remains immutable at
`68bcd22831e427a077ddfd48662e41bbe8ef46ebda0359c7153b9e3579afeae0`.

Ticket #138 root cause: `DISPLAY_BEZEL` and `DISPLAY_GLASS_SEAT` were authored
with two n-gon caps each. Deterministic cap triangulation of the rejected baseline
also exposed minimum triangle angle about 0.937 degrees and max aspect about
43.22:1. A first attempted repair was rejected because it inflated each mesh to
618 verts / 1024 faces and produced extreme slivers; its patch is retained outside
the repo at `F:\Temp\iphone17-ticket138-v2-rejected.patch`.

Retained repair:
- dedicated `display_topology_v30.py`, following existing body/camera topology
  module boundaries; no shared `foundation_common.rounded_prism` change;
- each display-frame source mesh: 318 verts / 460 faces, 0 n-gons,
  0 non-manifold edges, 108 outline points;
- contour error: about 0.00582 mm bezel / 0.00645 mm glass seat;
- deterministic cap triangulation: min angle about 7.39 degrees,
  max aspect about 7.77:1;
- dimensions, locations and material identities remain locked by the runtime
  contract;
- exact web delivery is 11,242 triangles, down from the frozen 11,538.

Exact current identity:
- source revision:
  `c6a54220cb8b1bcfd8ef1b67a6f4c7c2d046d0396754bdd35272659ec19e23cd`;
- compat GLB:
  `56ff5dec5b31a96a8cc656b9f5872313bb94695427e8e73e3b6e0181c7e1d3d3`;
- Meshopt GLB:
  `82cf2c72f281d0560af95f087eb12efa1b66bee1e8ce493dea8af6a493a2656c`.

Fresh verification on the retained repair:
- Blender 5.2.1: baseline RED and current GREEN for
  `iphone_v30_display_frame_topology_contract.py`;
- all 11 iPhone v30 runtime contracts PASS;
- Python fast suite 209/209 PASS;
- preview tests 25/25 PASS;
- Khronos glTF Validator 2.0.0-dev.3.10: compat and Meshopt both
  0 errors / 0 warnings;
- temporary exact-candidate Storybook build PASS;
- browser evidence verified frozen SHA and current SHA independently and kept
  geometry identity stable across texture / clay / actual triangle wire modes;
- matched whole-device texture comparison changed about 0.0138% of pixels
  (RMSE about 0.127/255); clay changed about 0.0008% (RMSE about 0.0016/255).

Browser evidence is retained outside the repo at
`F:\Temp\iphone17-ticket138-final-browser-evidence`. Temporary Storybook
working-candidate files were removed/restored before staging.

Decision: retain repair for Ticket #138. This does not approve screen/panel,
body, controls, bottom, front hardware, rear system, production provenance or
the whole device. Next frontier is Ticket #139. PR #119 remains DRAFT/HOLD.

## 2026-10-05 late - Ticket #139 screen/panel topology closure

Fixed point for this slice: commit `b522ece91bf85828357c44b5c7fb96bfba816667`.
The immutable appearance reference remains
`68bcd22831e427a077ddfd48662e41bbe8ef46ebda0359c7153b9e3579afeae0`.

Requirement ledger:
- native `SCREEN_GLASS` is explicit saved production geometry: PASS;
- authored n-gons and saved runtime modifier debt are removed: PASS;
- `BACK_GLASS`, `SCREEN_CONTENT` and `APPLE_LOGO_DECAL` topology/material/UV contracts remain unchanged: PASS;
- screen state and physical glass/content/bezel depth ordering remain explicit: PASS;
- web-visible panel payload remains unchanged relative to accepted Ticket #138 web candidate: PASS;
- whole-device topology remains owner-rejected and is outside this ticket.

Root cause: native `SCREEN_GLASS` was produced as a solid rounded prism, then boolean-cut
for the active area. The saved source retained three n-gons, an empty material slot,
`EDGE_BEVEL`, and `WEIGHTED_NORMAL` modifier debt.

RED evidence on exact `b522ece`: 784 saved verts / 396 faces / 3 n-gons,
0 non-manifold edges, `EDGE_BEVEL + WEIGHTED_NORMAL`. Evaluated baseline geometry
was 3,920 verts / 3,532 faces and still retained the three n-gons.

Retained repair:
- `display_topology_v30.py` now authors the native cover-glass ring directly from
  matched outer/inner rounded outlines;
- bevel is materialized through the existing runtime-bevel path;
- the weighted-normal and boolean active-area path is removed for `SCREEN_GLASS`;
- current saved `SCREEN_GLASS`: 1,920 verts / 1,920 faces, 0 n-gons,
  0 non-manifold edges, no runtime modifiers, one `MAT_DISPLAY_GLASS` slot;
- native glass dimensions/location and intentional no-UV contract are preserved.

Exact current build identity before the Ticket #139 commit:
- source revision:
  `12ca0a810dcdc15ef404fd25c259d093333c1b43b902a9abedda4288940df24c`;
- compat GLB:
  `da0c8aa4b88e596e6ea7071c147cd75af721b947f1388f9d1f470de8fe13cd6e`;
- Meshopt GLB:
  `ba9bdf9f36a2397a136cd34d77fff54b2f01fbf16c428e1d020252f69e1049c1`;
- web delivery remains 11,242 triangles because native-only `SCREEN_GLASS`
  is intentionally excluded from web delivery.

Fresh verification:
- Blender 5.2.1 baseline RED and repaired GREEN for
  `iphone_v30_panel_stack_topology_contract.py`;
- all 12 iPhone v30 runtime contracts PASS;
- Python fast suite 209/209 PASS after refreshing retained Khronos evidence;
- Khronos glTF Validator 2.0.0-dev.3.10: compat and Meshopt both
  0 errors / 0 warnings;
- temporary exact-candidate preview suite 25/25 PASS and Storybook build PASS;
- browser evidence pinned exact SHA/revision, verified required web panel nodes,
  verified native-only `SCREEN_GLASS` does not leak into GLB, and kept geometry
  buffers invariant across texture / clay / actual triangle-wire modes;
- matched Blender 5.2.1 native renders using the existing `CAM_FRONT` and
  `CAM_SCREEN_EDGE_MACRO` cameras show no visible silhouette/screen-stack
  regression or z-fighting. Baseline/current RMSE is about 0.132/255 front and
  0.474/255 edge macro; evidence is retained outside the repo at
  `F:\\Temp\\iphone17-ticket139-native-evidence`.

The Ticket #138 and Ticket #139 compat GLBs have byte-identical BIN chunks:
`3150815ef0b71a975d44507599cdfa8a3285fe19acedd90cf7af5d55bb920bb6`
(4,660,308 bytes). Their only node JSON change is the root provenance extras
(`delivery_source_revision` / `delivery_source_commit`). Thus this native
glass repair does not alter web geometry, indices, embedded binary payload, or
web-visible panel appearance.

Browser evidence is retained outside the repo at
`F:\Temp\iphone17-ticket139-browser-evidence`. Temporary Storybook candidate
files were removed/restored before staging.

The generated manifest still records `source_commit=b522ece...` because the exact
artifacts were built before this slice's commit. Final consumed-input/source-commit
provenance reconciliation remains explicitly assigned to Tickets #145/#146; do
not treat this checkpoint as final provenance closure.

Decision: retain repair for Ticket #139. This does not approve body, controls,
bottom, front hardware, rear system, production provenance, or the whole device.
Next frontier is Ticket #140. PR #119 remains DRAFT/HOLD.
## 2026-10-06 - Ticket #140 body corners and rails

Fixed point: `a8ad3a202d4c187ca28556fab9037d98b6457ea7`; branch
`agent/118-topology-rebuild-v2`. Owner transferred active worktree execution to
this continuation after residual writer activity completed. Incoming dirty files
were backed up in `F:\Temp\iphone17-ticket140-continuation\incoming`.
The prototypes directory and previous diagnostic captures were preserved.

Actual defect: `_rounded_outline` traversed the inner body contour in the opposite
order to the Apple outer outline. Connecting equally indexed points crossed the
annulus and produced overlapping cap strips. Manifold/triangle-count checks had
not detected this. An independent physical annulus coverage invariant reproduces
RED on exact baseline: projected cap triangle area 0.005391497 m² versus physical
outer-minus-inner area 0.000388314 m² on the front plane. Current passes both planes.

Retained minimum repair:
- correct only body inner-ring correspondence;
- subdivide only long edges in the main shell (14 mm target), preserving disconnected
  aperture/control cells, contour positions and material boundaries;
- persist intentional main-cap diagonals in saved Blender geometry, rather than
  measuring a prettier diagnostic triangulation;
- assign existing materials before the local BMesh mutation;
- stop the existing build on Blender Python exceptions (`--python-exit-code 7`).
  A real failing Blender generator reproduced baseline reaching export after failure;
  current stops before export/package in a temporary fixture without production writes.

Current BODY_ALUMINUM: 2,944 verts / 3,250 faces / 5,868 triangles; zero n-gons,
non-manifold, degenerate or zero-length defects; no runtime modifiers. The 632 main
cap triangles have min angle 1.97924°, max aspect 23.1779:1, max edge 13.9067 mm.
These diagnostics are local regression guards, not whole-device quality approval.
All 632 cap triangles are present in the actual compat GLB buffers.

Exact retained identity:
- source revision `2c4cd1d64c35fee34dd4f015c42b480f033a0bf030d9168dbf52bb08cb580591`;
- compat `61fa9616c5b26b7c9c43bf8b10db307ab132ac5dc311197f83992d9d2725def1`;
- Meshopt `74b1714b4e7d45a70de239d0c5f24a0d1d681e68276474b86ad9fe561f9a0ff5`;
- web delivery 11,466 triangles (diagnostic, not optimization goal).
The appearance reference remains `68bcd228...feae0`, unchanged.
Manifest/root source_commit remains the precommit fixed point; final consumed-input
provenance closure is explicitly deferred to #145/#146.

Fresh verification: Blender 5.2.1 all 13 iPhone runtime contracts PASS; fast209/209,
preview25/25 and Storybook build PASS; Khronos compat/Meshopt both 0 errors/0 warnings.
Matched exact baseline/current/frozen browser audits cover 15 views × render/clay/
actual triangle wire each, with SHA/revision verification, identical geometry buffers
across modes and zero browser errors. Four isolated corners and all four rails were
checked; four assembled corner macros show no visible contact-edge notch or highlight
break. Isolated bottom notches are covered by the existing panel stack; no aperture
or tray redesign was justified. Whole-device matched texture deltas are small
(front RMSE1.181/255, front3/4 0.642/255, rear3/4 0.862/255).
All 50 other GLB mesh payloads, materials and embedded images are byte unchanged;
body bounds are exact unchanged.

Independent /code-review against a8ad3a2: Standards PASS and Spec PASS, limited to
#140. Previous evidence gaps were resolved before acceptance. Durable evidence:
`assets/device_mockups/iphone_17/evidence/ticket140_body_rails/`; full captures/logs:
`F:\Temp\iphone17-ticket140-continuation`.
Existing Storybook remains the review surface; additional Tailscale HTTPS8443 proxies
its existing6006 server, preserving the separate443 route. Mobile landing:
`https://titan.tail85619a.ts.net:8443/?path=/story/models-catalog--catalog`.
The ordinary iPhone story still shows the frozen appearance snapshot; diagnostic
candidate captures use the same viewer with exact bytes, not a second viewer.

Decision: retain #140 repair after both review axes PASS. Next frontier #141:
controls / antennas / recesses. No whole-device Human PASS, production provenance
closure, merge, deploy or release is implied. #119 remains OPEN/DRAFT/HOLD.

### Ticket140 evidence portability follow-up

Fresh fast verification after evidence retention exposed a hardcoded Blender path
in the diagnostic proof harness. It now requires CLI --blender, derives its repo
and uses system temp fixtures. Actual RED/GREEN proof rerun PASS; fast209/209 PASS;
independent Standards and Spec PASS. Geometry and candidate bytes are unchanged.

## 2026-10-06 - Ticket #141 controls / antennas / recesses

Geometry fixed point `f38343912861546bef5ea371604dad612b7e562a`; precommit
HEAD `eb7021427a84805cbcd9d26ca94c6bdcd34c2027` adds only the independently
reviewed portable #140 evidence harness. Source ownership/preflight confirmed;
prototypes remain preserved/untracked. Baseline copies and raw diagnostics:
`F:\Temp\iphone17-ticket141`.

Fresh Blender audit: all five controls already have intentional saved capsule
geometry,44 verts/44 faces, no runtime modifiers. No concrete control/recess defect
was reproduced. Four antennas were saved8-vertex/6-face boxes with runtime BEVEL;
GLB exported only12 triangles each. Focused contract observed RED before source edit.

Retained local repair: materialize only the four antenna bevels in the existing
source generator, before placement, with three controlled arc spans. Shared helpers,
controls, mating body cells and all unrelated geometry are untouched. Two spans
were rejected: sampled native surface error5.186um exceeded the selected5um bound.
Three spans retain evaluated native surface within sampled2.194um. This is a
bidirectional vertex-to-triangle sample, not a certified continuous Hausdorff bound.
Native evaluated baseline was300 triangles per antenna; current saved geometry is
96verts/98faces/188triangles, zero n-gons/non-manifold/degenerate/zero-length defects,
no modifiers, preserved material/UV layer/datum/root. Complete saved triangle counters
match all four compat GLB meshes.

Exact retained candidate:
- compat `17d542c9a8317401a182f453930fa9967fd8cddf10aa0278e49d2d34720fb40a`;
- Meshopt `3e8250c6e5b01ab51778a5e7f6f5336db9fd6b36db568544974535ce01ab0b78`;
- source revision `5202ef46c41e321c72a92992990c69ac792838fad8e9707bd188c72a04f83679`;
- web12170 triangles, diagnostic only. Source_commit still a8ad3a2 precommit;
  final provenance remains #145/#146. Frozen68bcd228...feae0 is unchanged.

Fresh verification: existing build exit0; Blender5.2.1 all14 iPhone runtime contracts
PASS; fast209/209, preview25/25 and Storybook build PASS; Khronos compat/Meshopt both
0errors/0warnings. Exact baseline/current/frozen Storybook audits:9 assembled
control/recess/antenna/body views, five finishes, clay and actual triangle-wire,
63frames each, SHA/revision verified, geometry buffers invariant across modes,
no browser errors. Matched sheets inspected by independent Spec reviewer: no
pointed/diamond capsule boundary regression, spacing change, gap or shading break.
Volume/Side/Camera control texture/clay views are pixel-identical to baseline;
small Action-frame changes include the nearby repaired antenna. Body, all controls
and other47 GLB meshes, materials and embedded images are byte unchanged.

Independent Standards PASS + Spec PASS against the geometry fixed point.
Durable evidence: `assets/device_mockups/iphone_17/evidence/ticket141_controls_antennas/`.
Decision: retain #141 repair. Next frontier #142 bottom assembly / USB-C diagnosis;
do not change USB color before isolating geometry/normals/material cause. Whole-device
Human Gate remains pending after #146. Mobile access uses existing Storybook on
`https://titan.tail85619a.ts.net:8443`; primary iPhone story is still the frozen look,
not a working-candidate approval link. PR119 remains OPEN/DRAFT/HOLD; no push/merge/deploy.


## #142 bottom assembly checkpoint — 2026-10-06 (review pending)

Fixed point `ff22bb2a0ed7ea0aee87f04d6e3f70b3a4aae7f1`, same branch/worktree.
Read-only preflight preserved prototypes and exact frozen appearance bytes;
existing Storybook6006 remained available. No new viewer/exporter/pipeline.

Root cause reproduced before repair: antiparallel +Z/-Z quaternion placement gives
rectangular USB parts a90degree roll. Native/GLB cavity width was2.38mm instead
of8.45mm and device-depth span8.45mm exceeded body7.25mm. Tongue width was0.48mm
instead of5.25mm. Frozen appearance contains the same protrusion/vertical tongue.
Matched texture and clay show geometry cause; no material or color change.
Independent physical frame contract observed RED; explicit USB-only frame passed
native/exported dimensions and retained insets1.40/0.80mm. Ten radial callers keep
their previous frames. Separate RED proved saved BEVEL debt on both USB meshes.

Minimum topology repair materializes existing40um cavity bevel with2spans and80um
tongue bevel with3spans; persists BEAUTY triangles in authored geometry. Cavity
56verts/108triangles, tongue96verts/188triangles; both zero n-gons, non-manifold,
degenerate/zero-length defects and runtime modifiers. Complete source/GLB triangle
counters match. Native bidirectional vertex-to-triangle sampled errors4.23354um
and3.54817um are below5um diagnostic limit; not continuous Hausdorff certification.
Planar fronts need two triangles, arc spans own bevel curvature; no dense remesh.

Current exact working candidate:
- compat `679f6798e0b88e128cb991a22689b2d891a6f3d55544f1c65160fa50d020bb8c`;
- Meshopt `36c2d54b84d82cb6aa3803c4a6842eeb6f0215a68e0e40fe08d0da741b87acd1`;
- source revision `e0429e3d3ea23a808841e4cbcc4516774fb24eb68366cbb34de43a3f94f8783d`;
- web12442triangles, diagnostic only; manifest source_commit remains ff22bb2
  precommit, final provenance deferred#145/#146. FrozenSHA unchanged.

Fresh16/16Blender5.2.1 runtime contracts, fast209/209, preview25/25, Storybookbuild,
Khronos compat/Meshopt0errors0warnings.49othermeshes preserve positions/normals/
tangents/indices/worldframes;45fullpayloads byte-identical. Four antennaUV payloads
have maximum floating delta5.960464477539063e-8. Materials/images and bodybounds
identical, apertures/screw geometry and spacing unchanged. Do not claim all49
payloads byte-identical. Shared helper's default radial branch remains unchanged.

Matched existingviewer baseline/current/frozen:7assembled+2isolatedUSBviews,
fivefinish texture/clay/actualtrianglewire,63frames each; SHA/revision checks,
complete geometry-buffer invariants and browser-error checks PASS. Root inspected
all seven assembled sheets and isolated USB wire. Native build bottom render also
checked. Retained evidence: `assets/device_mockups/iphone_17/evidence/ticket142_bottom_assembly/`;
raw189PNGs and diagnostic/review inputs `F:\Temp\iphone17-ticket142`.

Standards/Spec review PASS after primary evidence adjudication. External reviewer hit usage quota; separate local
reviewer processes are used as fallback without Codex CLI dependency. Early local
advisory reports confused historicalRED with current GREEN and misclassified
ordinary Blender math/pipeline usage as hard smells; rawreports retained, verdicts
rejected. Final separate qwen3-coder:30b reports and primary adjudication are retained
in evidence/review-adjudication.md. Hosted parallel-agent review was unavailable;
local independent model review is explicitly identified. Implementation committed
as2ea91ae2ee2c04c9839e01d985fc5b30583659d2; #142closed with all acceptance
criteria verified. Closure comments #1426008952003 and #1186008952569. Next#143. No#143 work before#142review+commit. No push/merge/deploy;
PR119OPEN/DRAFT/HOLD. Whole-device Human Gate remains pending after#146 and will
use exact candidate bytes via existing TailscaleStorybook8443. Primary story still
shows frozenappearance, not this working candidate.


## #143 front hardware checkpoint — 2026-10-06 (WIP, no PASS/commit)

Read-only preflight fixed `6b294e0067741f9e6f6a8ba8fb857b11e65b9600`; branch unchanged,
prototypes preserved, frozenSHA verified, existing Storybook6006HTTP200.
Exact baseline blend/GLB and raw diagnostics in `F:\Temp\iphone17-ticket143`.

Two independently reproduced defects: sensor mask had4zeroedges/4degeneratefaces
from a duplicated equator row where its rounded-strip radius equals halfheight;
receiver retained a BEVEL modifier (saved8v/6f, evaluated300triangles).
`front-topology-red.log` failed sensor before source edit. Minimum existing-helper
fix omits only mirrored coincident equator row; BACK_GLASS/SCREEN_CONTENT callers
retain their original rows. Sensor now52v/50f/100triangles; all50previous nondegenerate
sourcefaces match exactly. Subsequent `receiver-topology-red.log` passed all sensor
checks and failed receiver modifier debt. Materialized only existing clamped9.8um
receiver rim with2spans; receiver56v/54f/108triangles, sampled native surfaceerror
1.03765um (<5um diagnosticlimit, not certified Hausdorff). No UV/material/artwork/
softwarestate/hardwaredatum redesign. No globalremesh/newpipeline.

Focused front contract now passes all7front meshes, zero n-gons/non-manifold/
degenerate/zero-length defects/modifiers, independent7.79mm hardware datum, finite
strict depth gaps across mask/glass/inner/iris/pupil, complete source/GLB triangle
correspondence and exported nondegenerate triangles. Existing full17runtime contracts
PASS; expanded front contract separately rerun GREEN. Fast209/209, preview25/25,
Khronos compat/Meshopt0errors0warnings current. Shared helper's other callers are
covered by current native contracts and exact exported physical-buffer comparison.
Other49geometry/frames/materials/images unchanged; antennaUV floating deltas recorded
separately in preservation-comparison.json, no allpayload byteidentity claim.

Current working compatSHA `354e53759fabaac61a39ff4df7fd69ae410da2ff8c52353184bb769b813570b0`;
source revision `92f2b5fe5c4eb902f3253ff15a282ab51c1878db2f1eb306613f61872667a11e`;
manifest source_commit2ea91ae precommit, final provenance#145/#146. Frozen unchanged.

Existingviewer8views(front/angled, island/angled, receiver/angled, twoisolated),
fivefinishes, fiveexisting screenstates, clay and actualwire:88frames/candidate.
Verified baseline/current/frozen audits are still running with exactSHA/revision,
awaited screen-state and geometry-buffer invariants. First partial captures without
awaited-state assertion were stopped and retained as rejected diagnostics; only
*-verified-browser results may support acceptance. Local independent Standards/Spec
review processes run without CodexCLI dependency; final visual inspection, fresh
Storybookbuild, review adjudication and staged checks must precede commit/closure.
No#144 work until#143commit. Whole-device/HumanGate remains unaccepted; PR119HOLD.

### Ticket143 final engineering review

Standards PASS and Spec PASS after primary inspection of all11 exact-byte matched
comparison sheets, 88frames per baseline/current/frozen (264total). Five finishes,
five screen states, clay and actual GLB wire; eight front/macro/isolated views.
No observed new front-stack visual regression or duplicate visible island.
Direct resume macro crops the island; angled/full views supply visibility evidence.
Local qwen3-coder30b reports lacked images; unsupported prose corrected explicitly
in retained primary adjudication. Runtime17, expanded front source/delivery/bundle
contracts, fast209, preview25, Storybook build, Khronos0errors/0warnings each PASS.
Evidence: assets/device_mockups/iphone_17/evidence/ticket143_front_stack.
Compat354e53759fabaac61a39ff4df7fd69ae410da2ff8c52353184bb769b813570b0;
Meshopt061c4df9e50fd31b6fe486f5431340d1d4cc051e3ffc7a842abc26de91677c1c;
revision92f2b5fe5c4eb902f3253ff15a282ab51c1878db2f1eb306613f61872667a11e.
12530webtris. Frozenreference unchanged. Commit pending staged verification;
next144 only after143commit. Wholedevice and HumanGate remain unaccepted.

### Ticket143 committed closure — supersedes WIP above

Implementation/evidence commit d3037f8b6f6b0de4f1afd8a2680be2d3da1503f9.
Staged fast209/209 and diffcheck PASS; only preserved prototypes remain untracked.
Issue143 CLOSED, closurecomment6009258155; ledger118comment6009258478;
Asana current notes updated without marking the whole task complete.
Next ticket144 rear-camera preservation audit. No push/merge/deploy.
Manifest precommit identity intentionally awaits145146. Whole-device topology and
HumanGate UNACCEPTED; final exact-candidate mobile links use existing Tailscale
Storybook after146, not the current primary frozen-reference story.

### Ticket144 WIP — rear preservation audit

Fixed point e5827f735eacd0dc97ee027da5d04059f84620c0; branch/preflight/frozen SHA
and existing Storybook HTTP200 verified. No camera geometry repair: all17 visible
rear meshes clean (ngons/nonmanifold/zeroedges/degfaces/modifiers zero, positive
signedvolume), and full exported geometry/normal/tangent/UV/index/node payloads
match frozen68bcd228...feae0 exactly. All materials/textures/samplers/embedded
images match frozen; source/delivery/bundle/manifest/bake files unchanged fromHEAD.

Initial diagnostic wrongly demanded Blender loop-triangle vsGLB triangle identity:
seven quadded leaves have alternative valid diagonals. This is not a geometryRED;
all actualtriangles match uniquely to authoredfaces, with winding/boundary/area
coverage independently checked. Existing rear runtimecontract expanded9→17leaves,
plus actualGLB coverage. No weakened existingtest or modifiedproductioninputs.
Capsule40-class/10cornersteps and circular40 radial samples preserve accepted
UV/silhouette. Circularcap9degree fans are regular, not thin curved slivers. Seat
min0.987degree/max58aspect concerns its straight planar0.30mm wall, not curved
surface; speculative longitudinaldensity is unwarranted. Regionmetrics retained.
Matingaudit: housing1.78mm and glass3.45mm above backglass, concentricstacks,
ordered optical visible surfaces, descendingdiameters and flash/ringcontact PASS.
Nativevolume nesting is intentional; no claim of pairwise disjoint optical solids.

Fresh runtime17/17, fast209/209, preview25/25; Khronosboth0errors0warnings.
Matched existingviewer9views×fivefinish/clay/actualwire current/frozen63frames each
running. Initial fullback crop corrected symmetrically; partial folders retained as
rejecteddiagnostics. SHA/revision/loadedstate/geometry invariants apply. Raw
F:\Temp\iphone17-ticket144. Separate local30b Standards/Spec reviews running;
primaryvisual adjudication and commit pending. No144PASS, no145work yet.
Wholedevice/HumanGate remain UNACCEPTED, PR119DRAFT/HOLD, no push/merge/deploy.

### Ticket144 concrete RED — supersedes no-defect/provisional reviews above

Matched REAR_MIC macro missing physical aperture. Existing official drawing
pure_ref/drawing_page_2.png Detail D shows Ø1mm rear microphone at currentdatum.
Independent BVH9rays(center+8within0.35mm) fail new visibilityassertion: opaque
CAMERA_HOUSING surfaceY5.755mm occludes REAR_MIC frontY5.065mm by0.69mm.
Frozen appearance shares the defect. Geometry/UV/payload cleanliness and exact
frozenidentity did not prove valid mating exposure. No source/model repair yet.
Existing rear runtimecontract now intentionally RED; baseline17runtime PASS was
before this additional independently observed assertion. Local30b reviewreports
cover earlier audit-only state and are superseded; no final144PASS or commit.
Next minimum physicalmic aperture repair restricted to housing/mic mating slice,
preserving camera-stack/seat/flash/silhouette and accepted bake inputs. Then existing
pipeline rebuild, focused/export/matched views, broader gates, new Standards+Spec
review, commit/closure. No145work, wholedevice/HumanGatepending; PR119HOLD.

## Ticket #144 repair closure checkpoint — 2026-10-06

Fixed point remains `e5827f735eacd0dc97ee027da5d04059f84620c0`; this section supersedes the earlier "no repair yet" note.

- Reproduced RED: official Detail D requires an exposed rear microphone Ø1 mm; nine native BVH rays were intercepted by `CAMERA_HOUSING` 0.69 mm before `REAR_MIC`.
- Minimal source repair: author a local Ø1 mm housing aperture at the existing rear-mic datum. Camera stacks, seat, flash, body silhouette, transforms, accepted materials/images/bakes and screen states are not redesigned.
- Fresh rear contract GREEN: all 17 rear leaves clean; authored/export face coverage passes; all nine mic visibility rays first hit `REAR_MIC`.
- Fresh whole-device runtime contracts: 17/17 GREEN in Blender 5.2.1.
- Broad regression: fast 209/209 GREEN; preview 25/25 GREEN; Storybook static build GREEN.
- Khronos: compat and Meshopt 0 errors / 0 warnings.
- Exact repaired browser audit: 9 views × 7 cases = 126 frames, zero capture errors; repaired compat GLB SHA-256 `7f91e3ca97ec4273862919f952c3ac8b367278207dab8a1e592f1b839cd3ae1f`, source revision `b5438febcbe35574c29f352d1e5daf356c0b6c81c604a96b42af72b2843e6cd6`.
- Primary visual comparison of matched frozen vs repaired camera-system view confirms the intended delta: the physical rear-mic port becomes visible while camera/flash/housing silhouette remains unchanged. Wire review localizes new topology to the flat housing cap around the port.
- Preservation note: a broad byte comparator observed regenerated `USB_C_CAVITY` UV drift max 5.96e-8 and derived tangent drift max 1.00e-4 (minimum tangent xyz dot 0.999922, handedness unchanged); POSITION/NORMAL/indices are byte-identical and USB runtime contracts remain GREEN. This is exporter floating-point/derived-field drift outside #144, not a geometry regression.
- Independent local Standards + Spec reviews return PASS for #144 scope. They do not grant whole-device/Human acceptance.
- `PR #119` remains HOLD; no push/merge/deploy. Whole-device Human Gate remains after #146.
- Next after an explicit #144 commit/issue close: #145 production bundle/provenance gaps, then #146 exact whole-device integration.

## Ticket #145 production bundle/provenance closure — 2026-10-06

- Reproduced plugin-bundle leak before the fix: source/plugin each carried 56 meshes, including hidden `BODY_ALUMINUM_HIGH`, `BACK_GLASS_SEAT`, `CAMERA_1_SEAT`, `CAMERA_2_SEAT`; three hidden meshes still had unapplied modifiers. Runtime delivery was already clean at 52 visible meshes.
- Reproduced provenance gap: the canonical source fingerprint omitted the consumed front-camera detail mask, five immutable control normal maps plus their provenance record, and build/packaging inputs that change delivery identity.
- Fix: `package_device_asset.py` now has an opt-in `--runtime-visible-only` mode; the iPhone v30 build opts in without changing iPad/MacBook packaging behavior.
- Rebuilt plugin bundle is 52 visible meshes, 0 hidden meshes, 0 modifiers, 0 HIGH/reference flags. Generated authoring source intentionally retains the four hidden helper/HIGH meshes; delivery and plugin do not.
- Source fingerprint now covers 27 inputs, including the consumed texture/bake files and `optimize_runtime_v30.py`, `build_iphone17_v30.py`, `package_device_asset.py`, `device_delivery_contract.py`. Control-bake provenance pins SHA-256 for all five maps.
- New source revision: `9b1913cbd9fa9188dd61c119c7731e4d6ea9aa6ab520e0ca39ee347da65de1f5`.
- Fresh verification: fast 212/212 GREEN; Blender runtime 17/17 GREEN; Khronos compat and Meshopt 0 errors / 0 warnings.
- Exact GLB SHA-256: compat `ba4ef30c68ef93470eff6d8d472d78454ad51f99a727469a8f6d12fa58eda05c`; Meshopt `57f25b2a72741e7ea630fa5580e112e6f4a40c4a2830813bb901e8690edf7b07`.
- Plugin bundle SHA-256: `82173e9bdfb0c22d521ea939ed4dd7343600bcfdd87e8d3b516ac6414f4b40a3`.
- #145 is ready for a local commit/issue close. PR #119 remains HOLD; no merge/deploy or whole-device Human PASS. Next slice: #146 exact whole-device integration.
