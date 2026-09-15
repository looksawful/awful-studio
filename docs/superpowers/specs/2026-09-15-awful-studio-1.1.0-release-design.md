# AWFUL STUDIO 1.1.0 Release Design

## Goal

Ship AWFUL STUDIO 1.1.0 as a polished, user-ready Blender Extension with current device assets, reproducible delivery artifacts, clear documentation, verified installers/archives, real product visuals, and a complete GitHub release.

## Release rationale

1.1.0 is a minor release because it adds qualified workflows and assets beyond the stable 1.0.0 core: bundled precision devices, screen replacement, MacBook hinge controls, and manifest-driven LOD. This follows the repository's own versioning policy in `STATE.md`.

## Supported runtime

- Blender target: 5.2 LTS.
- Qualification runtime: Blender 5.2.1 build `9e2066aef7ef`.
- Manifest range: `>= 5.2.0` and `< 5.3.0`.
- Windows and Ubuntu must pass the same exact built Extension ZIP.
- Installation/enabling remains scene-clean; Build Studio is always explicit.

## Product scope

The release keeps the 1.0.0 stable studio core and adds the current device integration already developed in the repository. No unrelated new subsystem is introduced during release polish.## Device delivery contract

The plugin ships exactly these current device assets:

- iPhone 17 v20, stage `LOW_DRAFT`, source-derived and fingerprint-guarded.
- iPad Pro 11 M5 v6, stage `LOW_DRAFT`.
- iPad Pro 13 M5 v6, stage `LOW_DRAFT`.
- MacBook Pro 14 M5 release candidate with `CTRL_HINGE` and named hinge presets.

The plugin must expose explicit asset stage and LOD separately. A LOW_DRAFT or RELEASE_CANDIDATE asset must never be silently promoted to DELIVERY.

Screen replacement remains independent from cover-glass material. MacBook hinge presets remain CLOSED / 30 / 60 / 90 / 102. Runtime bundles contain no preview cameras or lights.

For iPhone v20, one reproducible command must generate the canonical `.blend`, web GLB, Meshopt GLB, manifest, validation evidence, and plugin bundle from the same source fingerprint. The plugin loader must match that fingerprint and reject stale revision/stage assumptions in tests.

## Distribution artifacts

The 1.1.0 release publishes:

- `awful_studio-1.1.0.zip`: official Blender Extension package.
- `awful_studio-1.1.0.zip.sha256`: checksum file.
- `awful-studio-1.1.0-source.zip`: source archive.
- `awful-studio-1.1.0-extension-repository.zip`: static Blender Extension Repository bundle.
- `install-awful-studio.ps1`: Windows helper using supported Blender CLI behavior rather than manual AppData mutation.
- `VERIFY.txt`: versions, artifact sizes, SHA-256 values, qualification runtime and verification commands.## Documentation and onboarding

The root README becomes user-first. The first screen explains what AWFUL STUDIO is, supported Blender version, the primary release artifact, installation, first-use flow and key capabilities before engineering details.

Required docs:

- Quick Start: install, enable, Build Studio, choose product/device, lighting, camera and render preview.
- Install / Update / Uninstall, including update from 1.0.0.
- Device Mockups: current stages, screen replacement, hinge presets and LOD semantics.
- Lighting / Environment / HDRI and network permissions.
- Motion and Preview Range behavior.
- Troubleshooting and FAQ.
- 1.1.0 release notes and migration notes.
- Developer section preserving qualification/runtime/contributor information without making it the user's entry point.

Documentation must not claim unfinished HIGH geometry, material/bake workflows or deterministic rendered regression as complete.

## Visual system

Release visuals use only real Blender renders/screenshots from current repository/device scenes. No generated Blender UI and no synthetic mock screenshots.

The visual direction is restrained editorial product photography: black or near-black studio foundation, one dominant product/device, controlled soft key and rim, large negative space, minimal typography. The cover must not become a feature collage.

Deliverables:

- 16:9 release/README hero.
- 1200×630 social/GitHub cover.
- compact feature strips using real interface/render evidence.
- source layout/script so covers can be regenerated from repository images.

Typography is added in post/composition, not baked by an image generator.## Release gates

Before tagging 1.1.0, all of the following must pass on the final release commit:

- full fast/static suite;
- Python compile and `git diff --check`;
- official Blender Extension validate/build;
- exact built ZIP runtime verification in Blender 5.2.1;
- native static Extension Repository generation/sync/install;
- GitHub Actions Ubuntu and Windows qualification using the same candidate ZIP;
- clean install into an isolated Blender profile;
- update path from 1.0.0 without scene mutation on enable;
- save/reopen with bundled device state;
- device add, screen replacement and MacBook hinge preset runtime checks;
- final ZIP contents audit and release-hygiene checks;
- iPhone v20 compat and Meshopt GLBs at 0 Khronos validator errors and warnings.

## Release workflow

1. Finish and merge the iPhone v20 delivery/fingerprint work.
2. Create a clean `release/1.1.0` branch from updated `main`.
3. Update version metadata and release-facing docs.
4. Create real-image release visuals and README integration.
5. Add reproducible packaging and Windows install helper.
6. Build and verify all release artifacts.
7. Open one release PR, run CI, review final diff and merge.
8. Tag `v1.1.0` and publish the GitHub Release with verified artifacts and release notes.
9. Re-fetch release metadata/artifacts from GitHub and verify hashes after publication.

## Non-goals

- No HIGH device geometry is invented for 1.1.0.
- No unverified texture/bake pipeline is represented as shipped.
- No automatic modification of Blender GPU preferences.
- No background network downloads.
- No replacement of native Blender controls with a closed custom renderer.
- No generated/fake Blender screenshots.

## Success criteria

A Blender 5.2 user can understand the project from the README, install one official ZIP, open `N → AWFUL STUDIO`, build a studio, add the bundled current devices, replace screen artwork, use the MacBook hinge presets, save/reopen, and reproduce the documented behavior without developer tooling. The GitHub Release contains all promised artifacts with matching checksums and qualification evidence.