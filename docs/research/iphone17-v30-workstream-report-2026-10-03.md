# iPhone 17 v30 workstream report

Date: 2026-10-03
Scope: engineering reconstruction of the current iPhone 17 v30 closeout, including successful decisions, failed paths, prototype results, tools, and remaining work.

## Current state

- Repo: `looksawful/awful-studio`
- Final production PR: #119
- PR #119 state: OPEN / DRAFT / HOLD
- PR head: `394951d61e21868cafe448d1543b82c10db14e39`
- Production correction worktree: `F:\Temp\iphone17-v30-dimfix`
- Production branch: `agent/119-iphone17-dimensional-fix`
- Low-poly bake prototype branch: `prototype/iphone17-camera-lowpoly-bake`
- Prototype commit: `b355e24495e6a7c9d4fcbf2ff927842ff75c5680`

Do not merge #119 until the current topology / UV / bake work returns through full verification and Human Gate.

## Route

`visual closeout -> Dynamic Island architecture -> #126 merge -> Apple dimensional audit -> HOLD #119 -> drawing-derived TDD fixes -> PBR + official finishes -> Human topology rejection -> topology audit -> rejected dense prototype -> low-poly+bake research -> 16/24/32/40 prototype -> 40 candidate -> adaptive 40+32 experiment -> macro rejection -> UV/bake cleanup -> remaining model parts -> spec -> tickets -> TDD implementation -> review -> final Human Gate -> exact-SHA ship`

## Accepted decisions

1. Dynamic Island is a system-owned compositor layer above clean `SCREEN_CONTENT`.
2. Physical front sensor/camera hardware remains independent at the Apple 7.79 mm datum.
3. Stay on canonical v30; do not fork v31/v32 for these repairs.
4. Apple dimensional drawings are the authority for physical geometry.
5. Product-visible tests target exported GLB/runtime behavior, not only generator formulas.
6. Geometry owns silhouette and real depth.
7. Tangent-space normal maps own shallow bevels, pentalobe, machining and microdetail.
8. Roughness/metallic/AO own surface response.
9. High-poly is a bake source; it is not the web delivery mesh.
10. Runtime glTF is allowed to triangulate; authoring topology should remain understandable and sparse.
11. One GLB carries five official finishes: Black, White, Mist Blue, Sage, Lavender.
12. Human macro review can reject a mathematically plausible segment count.

## Apple dimensional correction

The shipped tree `394951d` was strong on envelope, display, camera XY, camera diameters, flash, front datum, logo and corner profile, but official drawings exposed four material defects:

- rear camera plateau/glass depth;
- bottom acoustic count/spacing;
- side-control visible sizes;
- rear microphone X datum.

All four were implemented through RED -> GREEN contracts. The corrected local candidate passed:
- focused iPhone: 28/28;
- full fast: 204/204;
- Blender 5.2.1 geometry: GREEN;
- Khronos compat/Meshopt: 0 errors / 0 warnings;
- preview: 19/19;
- Storybook build: GREEN;
- browser smoke: 11/11;
- targeted website state: clean.

See `docs/research/iphone-17-post-ship-dimensional-audit-2026-10-02.md`.

## PBR / finishes

The local v30 WIP subsequently added:
- anodized aluminum normal + roughness;
- back-glass normal + roughness;
- Camera Control finish maps;
- pentalobe screw normal + roughness;
- shared PBR UV/tangent path;
- official five finish variants in Blender/Storybook/runtime.

Technical WIP gate reached:
- fast 207/207;
- Blender GREEN;
- Khronos compat/Meshopt 0/0;
- preview 21/21;
- Storybook build GREEN;
- five-finish browser sweep PASS.

Human Gate then exposed topology quality problems, so this state is not final acceptance.

See `docs/research/iphone-17-finish-pbr-reference-2026-10-03.md`.

## Topology error route

Current production geometry is visually acceptable shaded but structurally poor:
- body has large Boolean-derived n-gons;
- camera housing uses huge planar caps;
- camera cylinders were over-segmented;
- glTF triangulation exposes ugly wireframe.

Representative runtime counts:
- BODY_ALUMINUM ~8108 tris;
- CAMERA_HOUSING ~10540 tris;
- CAMERA_HOUSING_SEAT ~10540 tris;
- CAMERA_1_RING ~3836 tris.

The first cleanup prototype used structured 64/72/96 topology. It removed n-gons but remained far too dense. This prototype is retained only as negative evidence.

Branch: `prototype/iphone17-camera-topology`
Commit: `4605ed4013b4ece6f1ee40826888f78a7e24c48f`

## Low-poly + bake pivot

Research established:

`high-poly dimensional source -> bake -> sparse low-poly silhouette mesh -> tangent normal + ORM -> glTF/Three.js`

Normal/displacement cannot repair an under-sampled outer silhouette. The delivery mesh therefore keeps enough vertices only where outline/depth needs them.

Low-poly bake prototype results:
- 16: 272 verts / 512 tris / ~5.16 px macro error -> reject;
- 24: 400 verts / 768 tris / ~2.30 px -> reject;
- 32: 528 verts / 1024 tris / ~1.29 px -> close, still visible;
- 40: 656 verts / 1280 tris / ~0.83 px -> viable candidate.

After explicit tangent export, all prototype GLBs validate at Khronos 0 errors / 0 warnings.

Branch: `prototype/iphone17-camera-lowpoly-bake`
Commit: `b355e24495e6a7c9d4fcbf2ff927842ff75c5680`

See `docs/research/iphone17-lowpoly-bake-pipeline-research-2026-10-03.md`.

## Adaptive density experiment

Wolfram chord-sagitta calculations support radius-dependent density. At roughly 0.04 mm geometric error:
- outer housing ~40;
- inner housing ~35/36;
- camera ring ~32;
- bevel ~31/32;
- glass ~29/32.

An adaptive 40 housing + 32 ring/bevel/glass prototype produced 1088 tris vs 1280 for uniform 40 and validated Khronos 0/0.

However the owner macro review still saw the 32-segment visible rings as crooked. Therefore adaptive 40+32 is not approved as the final visible camera policy.

Current provisional visual policy: use 40 on silhouette-critical housing/rings/glass; reduce only internal non-silhouette optics until a new macro check proves otherwise.

## Current blocker: dirty camera halo

The current baked camera has dark dirty halos around rings.

Likely stacked causes:
- projection rays/cage too wide;
- current cage extrusion 0.35 mm;
- max ray distance 0.55 mm;
- closely stacked surfaces;
- Smart UV islands packed too tightly;
- only 8 px bake margin;
- actual contact shadows combining with normal-map artifacts.

The next prototype should not research further. It should isolate:
1. geometry only;
2. geometry + normal with shadows disabled;
3. geometry + normal + shadows;
4. deterministic UV islands;
5. 16-24 px gutter/dilation at 512;
6. tighter cage/ray settings;
7. visible rings at 40.

If the halo disappears without the normal map, fix bake. If it appears only with shadows, fix lighting/contact shadow. If it appears on mip/downscale, fix UV padding.

## Remaining order

After camera Human PASS:
1. body/rail;
2. side controls;
3. bottom I/O;
4. screws;
5. back glass/display;
6. UV/PBR consolidation;
7. finish variants full-device check.

Only after visual convergence:
`/to-spec -> /to-tickets -> /implement (TDD) -> /code-review -> full verification -> Human Gate -> exact-SHA approval -> #119 merge`

## Tool / skill boundaries

- Research: primary sources only when a factual unknown matters.
- Prototype: short throwaway experiment for one visual/technical question.
- CodebaseDesign: device-level topology seam; avoid generic DSL until a second device proves it.
- Codex Engineering Guardrails: verification remains separate from implementation.
- Wolfram: independent geometry math, never a substitute for visual acceptance.
- Game Development Studio: asset-production skill consulted; local `game-dev` CLI is not available on Titan, so no provider/CLI workflow was used.
- AgentMarkup: not applicable to this 3D asset task; no AgentMarkup changes were made.
- Remote Desktop Commander: primary Titan transport in this session.
- GitHub connector: PR/issue/shipping evidence.
- Khronos validator: required GLB delivery gate.
- Storybook/Three.js/Tailscale: runtime and Human Gate boundary.

## Authoritative references

- Apple iPhone 17 Dimensional Drawings:
  https://developer.apple.com/download/files/accessories/dimensional-drawings/iphone-17.pdf
- Apple iPhone 17 specifications:
  https://www.apple.com/iphone-17/specs/
- Apple Repair Manual:
  https://support.apple.com/en-us/123029
- Khronos glTF 2.0:
  https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html
- Blender glTF exporter:
  https://docs.blender.org/manual/en/4.5/addons/import_export/scene_gltf2.html
- Blender Cycles baking:
  https://docs.blender.org/manual/en/latest/render/cycles/baking.html
- Three.js MeshStandardMaterial:
  https://threejs.org/docs/pages/MeshStandardMaterial.html

## Progress snapshot

- [100%] Dynamic Island architecture
- [100%] Apple dimensional audit
- [100%] Four dimensional fixes technically verified
- [90%] PBR + official finish variants
- [85%] Camera low-poly topology hypothesis
- [55%] Camera UV / normal-bake quality
- [20%] Production topology architecture migration
- [5%] Body/rail cleanup
- [5%] Side-control topology cleanup
- [5%] Bottom topology cleanup
- [10%] Fastener visual realism
- [5%] Back glass/display cleanup
- [0%] Final spec after prototype convergence
- [0%] Tickets
- [0%] Production topology implementation
- [0%] Final code review
- [0%] Final full-device Human Gate
- [0%] New exact-SHA approval / merge #119
