# AWFUL STUDIO Storybook Model Preview Design

## Goal
Give `awful-studio` its own lightweight internal Storybook for inspecting canonical 3D assets without depending on `looksawful.ru` for day-to-day model review.

## Scope
- Add one isolated preview package inside `awful-studio`.
- Reuse only the model-viewer behavior already proven in `looksawful.ru`.
- Do not copy the site design system, public preview pages, lab shell, CMS, or unrelated Storybook infrastructure.
- Keep `main` as the only long-lived branch; this work ships through the same short-lived infrastructure branch as Git-flow protection.

## Preview stack
- Storybook `10.6.x` with `@storybook/html-vite`.
- Three.js with `GLTFLoader`, `OrbitControls`, and `RoomEnvironment`.
- No framework layer is introduced unless Storybook itself requires it.
- Preview code lives under `preview/` and remains independent from Blender Extension runtime code.

## Catalog model
A generator creates `preview/generated/asset-catalog.json` from canonical repository manifests and known scene definitions.
The catalog includes only current canonical assets by default, not superseded device revisions.
Each entry exposes stable metadata: id, label, group, source blend path, preview GLB path, canonical version, LOD paths, collision path when present, and manifest/source revision data when available.

## Initial groups
- Devices: iPhone 17 v30, iPad Pro 11 v6, iPad Pro 13 v6, MacBook Pro 14 v1.
- Studio Equipment: current Studio Rig v01 runtime objects.
- Scenes: White Studio v2, Dark Neon v2, Loft Daylight v2 after preview GLB export.

## Viewer behavior
The viewer supports orbit/zoom, fit and reset, front/side/top camera presets, perspective/orthographic projection, autorotation, fullscreen, background controls, basic studio lighting, render modes, animation playback when clips exist, LOD switching, clipping, and useful debug overlays/statistics.
Advanced controls are hidden when the selected asset does not support them.

## Asset delivery
Existing canonical device and Studio Rig GLBs are consumed directly from their repository runtime paths.
The preview must not duplicate those binaries.

Scene Lab candidates currently exist as `.blend` only. A Blender preview-export tool produces deterministic preview GLBs for Storybook without changing the production `.blend` sources or declaring the scenes Extension runtime assets.
Preview-exported scene GLBs live in an explicitly generated preview location and can be regenerated from source.

## Story structure
Storybook contains one catalog landing story and one reusable model story template driven by catalog entries.
Stories are grouped as `Models/Devices`, `Models/Studio Equipment`, and `Models/Scenes`.
Asset metadata is displayed next to the viewer so review does not require opening manifests by hand.

## Validation
A lightweight preview CI job must:
- regenerate or validate the catalog;
- reject missing catalog paths and duplicate asset ids;
- build Storybook successfully;
- run a browser smoke test that loads at least iPhone 17 v30 and one Studio Rig asset and confirms a rendered canvas/model;
- keep Blender-heavy Extension QA separate from Storybook build verification.

Scene preview export is validated with Blender 5.2.1 and should only run when scene source/export tooling changes or when explicitly requested.

## Non-goals
- No public deployment contract for `looksawful.ru`.
- No synchronization of UI styles with `looksawful.ru`.
- No permanent preview branch.
- No database, CMS, or external asset service.
- No requirement to expose historical device revisions in the default catalog.
- No attempt to load `.blend` directly in the browser.

## Success criteria
Running one preview command from `awful-studio` opens Storybook with every current browser-previewable canonical model discoverable from the generated catalog. A reviewer can rotate, zoom, fit, change useful visualization controls, inspect metadata, and switch models without opening Blender or `looksawful.ru`.
