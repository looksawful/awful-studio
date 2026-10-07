# AWFUL STUDIO model preview

One Storybook package (`preview/`), one Three.js viewer (`src/model-viewer.mjs`), one generated catalog. Browser wireframe shows the actual exported GLB triangles, including front/back surfaces; it does not show Blender's authored quad topology.

## Where to review

The permanent published address is https://looksawful.github.io/awful-studio/. On 2026-10-05, the latest successful Pages workflow was [36424975204](https://github.com/looksawful/awful-studio/actions/runs/36424975204), built on 2026-09-28 from `c3162abcc781e9ee917b3ba271d416fa3c5f65e4`. Its device stories exist, but this is an older published build. It does not contain the pinned review snapshots below.

The current local review build on Titan is http://127.0.0.1:6006/?path=/story/models-catalog--catalog. The iPhone primary story is the exact #146 Human Gate candidate; the frozen 2026-10-05 look remains preserved separately as appearance reference. Rotate, zoom, and switch between render, clay, and hidden-line GLB triangle wireframe. Every primary device story reads the same catalog entry shown on the landing page.

| Primary story ID | Review selection | GLB SHA-256 prefix | Triangles |
| --- | --- | --- | --- |
| `models-devices--i-phone-17` | #146 exact Human Gate candidate; owner verdict required | from canonical v30 manifest | from canonical v30 manifest |
| `models-devices--i-pad-pro-11` | iPad writer WIP snapshot; human review needed | `3640fec046ab` | 20,674 |
| `models-devices--i-pad-pro-13` | iPad writer WIP snapshot; human review needed | `7003ee11422a` | 20,682 |
| `models-devices--mac-book-pro-14` | MacBook G2 writer WIP snapshot; human review needed | `bc4a4c03f511` | 74,023 |

The iPhone entry is derived from its canonical runtime manifest; the other three devices are selected snapshots. `v30`, `v6` and `v1` alone do not identify the latest geometry everywhere. Freshness requires GLB checksum and source revision/commit; copied snapshots additionally retain their branch/HEAD. The exporter source commit can predate writer HEAD or omit uncommitted changes; the full snapshot identity and copied source manifest preserve that distinction. A manifest's `RELEASE_CANDIDATE` stage does not confer visual acceptance.

## Sources and archive policy

The iPad writer is `agent/51-ipad-control-geometry`, HEAD `c6c9457e238c65f32e521d8b7234c82d788fc175`, including rebuilt uncommitted source/runtime. MacBook is `fix/macbook-g2-overlay-calibration`, HEAD `e39d8d10` at audit, with uncommitted geometry-contract changes included in the source revision. These writers are separate checkouts and are not represented by the iPhone checkout's worktree list. Their source-file hashes, artifact hashes and GLB-root provenance were checked before copying the browser candidates.

The iPhone freeze stays in `generated/iphone-review/frozen-current-2026-10-05/` as immutable appearance evidence. The active #146 Human Gate candidate is derived directly from `assets/device_mockups/iphone_17/runtime/v30/iphone_17_v30.asset.json` and serves that canonical compat GLB without copying it. The three other byte-exact review copies and original manifests are in `generated/device-review/current-2026-10-05/`. They are review evidence, never replacement production sources. No native Blender source, generator or delivery file in another writer was edited. Embedded textures, current screen-state/glow metadata and MacBook animation clips are retained. All four browser loads verify the pinned checksum before parsing, then verify manifest provenance on the loaded root.

Older device runtime files in this checkout remain at their production paths for existing consumers, but are not served by this review build or selectable as primary device stories. Historical iPhone reference evidence remains under `generated/iphone-review/archive/`, excluded from static serving. Do not delete old source evidence or duplicate binaries merely to hide them from the catalog. Replace a review snapshot only by an explicit new selection with new evidence; never silently overwrite the frozen iPhone.

## Local use and verification

```powershell
cd preview
npm ci
npm run storybook
```

```powershell
npm test
npm run storybook:build
npm run smoke
```

`npm run catalog` assembles selected device snapshot metadata and existing Studio Rig/scene manifests. `catalog:check` rejects stale metadata without rewriting it. The same static build can be served locally or through the existing GitHub Pages workflow; a second preview application or hosting service is unnecessary.

Studio Rig v01 and White Studio/Dark Neon/Loft Daylight v2 remain in the catalog. Studio Rig uses repository runtime files; scene GLBs remain preview exports from canonical Blender candidates.

## iPhone presentation contract

The frozen snapshot pins display artwork, finish palette, material policies and lighting values. It preserves `SCREEN_CONTENT` states, software Dynamic Island artwork, privacy indicator as screen state, under-glass front masks, and the authored 7.79 mm hardware datum. The viewer does not move front optics to follow screen artwork. Wireframe uses exported triangle geometry; render restores its PBR materials and selected screen/finish state.

## Publishing and responsibility

The existing `.github/workflows/preview-pages.yml` builds/deploys this Storybook on `main`, with manual dispatch also available. Working files and local evidence do not reach Pages automatically. Dispatching an old remote branch cannot publish uncommitted snapshots.

Current review preparation does not authorize committing, pushing, merging or deploying held model work. Keep each model's existing human visual gate and PR holds. Once the selected deliverable is approved and authorized for delivery, publish through this same workflow and verify deployed story IDs and exact GLB hashes before calling the published URL current.

GitHub owns implementation/evidence, Asana owns execution, and Notion owns durable context. Dated handoffs and published builds are provenance until current owner evidence verifies them; this README is a preview entry point, not another backlog.
