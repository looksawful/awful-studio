# AWFUL STUDIO

AWFUL STUDIO is a Blender-native virtual product and advertising studio for building editable product-shooting scenes, lighting rigs, camera setups, environments, procedural product mockups and motion presets without replacing Blender's native controls.

## Status

- Current release: **1.0.0**.
- Historical baseline: **Alpha 0.0.15** (`historical/0.0.15/awful_studio_v4_2_gpu_perf.py`).
- Blender target: **5.2 LTS**; exact qualification runtime: **Blender 5.2.1**, build `9e2066aef7ef`.
- Manifest compatibility: Blender `>= 5.2.0` and `< 5.3.0`.
- Exact official Windows/Linux distribution pins: `runtime/blender.lock`.
- Structural/runtime qualification uses one exact built Extension ZIP on Ubuntu and Windows.

Historical source SHA-256:

```text
5d14513b699a0c0a0e693bba7c31111f264ac5988cf1abb85c7153f6a2e7e56b
```

## What ships in 1.0.0

- ownership-safe Build / Rebuild / Remove and explicit historical migration;
- metric cyclorama and independent studio architecture visibility;
- commercial/product lighting, photographic Flash, Natural Light, Physical Sky and Hybrid Studio + World modes;
- independent environment illumination and camera-visible background brightness;
- product-bounds camera framing and Auto Fit;
- Product / Camera Once, Loop and Ping-Pong with synchronized Preview Range;
- procedural Bottle / Jar / Box / Can / Phone / Tablet starter mockups;
- deterministic offline starter materials;
- explicit optional HDRI download workflow with provenance-safe cache behavior;
- optional professional Post Pipeline with Light Groups, passes and managed compositor;
- Fast Preview / Quality Preview viewport profiles without silently changing Blender's Cycles device;
- native Blender Extension package/repository validation and cross-platform packaged-runtime QA.

The invalid PaintedPlaster PNGs found in the pre-release candidate are deliberately **not** bundled in 1.0.0. The affected surfaces use the existing procedural/offline fallback instead. A verified texture bundle can return in a patch release after binary integrity validation.

## Repository map

```text
extension/awful_studio/   Blender Extension package source
historical/0.0.15/        immutable historical baseline
runtime/blender.lock      exact verified Blender runtime pins
tests/fast/               pure/static policy and tooling tests
tests/runtime/            real Blender packaged-runtime contracts
tools/awful.py            status, doctor, fast, bootstrap, runtime entrypoint
tools/setup_blender.py    official Blender download/checksum bootstrap
tools/verify_extension.py official build + exact-ZIP runtime verifier
docs/                     install, releases, engineering plans and references
AGENTS.md                  default contributor/agent instructions
STATE.md                   current engineering handoff
```

## Development invariants

- Blender behavior requires real Blender 5.2 runtime evidence; static tests are not proof of `bpy` behavior.
- Import/register/enable/restart must not build or mutate a scene.
- Build/Rebuild are explicit user actions and preserve Blender's native device selection.
- Base studio operation is offline; optional asset downloads require explicit opt-in.
- Rebuild/Remove/migration preserve unmanaged and shared user data.
- Heavy post/compositor paths remain opt-in.
- Ordinary structural QA contains no render invocation and does not probe local GPU hardware automatically.
- Binary media under the Extension asset tree must never be Git text-normalized.

## Tests and runtime

Fast checks, no Blender:

```sh
python -m unittest discover -s tests/fast -v
```

Agent/human health checks:

```sh
python tools/awful.py status
python tools/awful.py doctor
python tools/awful.py fast
```

Explicit runtime bootstrap:

```sh
python tools/awful.py bootstrap --destination .blender
```

Explicit full runtime verification:

```sh
python tools/awful.py test-runtime --blender <path-to-blender>
```

The canonical CI path downloads the exact official Blender 5.2.1 distribution, verifies Blender's published SHA-256, validates/builds the Extension with Blender's CLI, then tests the same generated ZIP in isolated profiles on Ubuntu and Windows.

## Installation

Use the release artifact `awful_studio-1.0.0.zip` with Blender **Edit → Preferences → Extensions → Install from Disk**. Installation and enabling are scene-clean; run **Build Studio** explicitly from `N → AWFUL STUDIO`.

See `docs/INSTALL_UPDATE.md` for installation, GPU/Rendered Viewport notes, optional HDRIs, Post Pipeline and troubleshooting.

## Post-1.0 work

Unfinished Scene Lab visuals, production device mockups, physical studio-equipment assets, visual-regression automation and optional external bridges remain in GitHub Issues. They are deliberately not treated as blockers for the stable core release and will be delivered through patch/minor versions when qualified.

## Release references

- Current state: `STATE.md`
- Install/update: `docs/INSTALL_UPDATE.md`
- 1.0.0 release notes: `docs/releases/1.0.0.md`
- Third-party assets: `docs/THIRD_PARTY_ASSETS.md`
- Official Blender Extension references: `docs/references/blender-extension-development.md`

Implementation truth is the released source plus current GitHub issue/PR/CI evidence, not stale planning prose.
