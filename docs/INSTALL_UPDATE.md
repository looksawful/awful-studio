# AWFUL STUDIO 1.0.0 — Install, Update and Troubleshooting

AWFUL STUDIO 1.0.0 targets Blender 5.2 LTS. The exact qualification runtime is Blender 5.2.1 build `9e2066aef7ef` on Windows and Ubuntu.

The Extension manifest supports Blender `>= 5.2.0` and `< 5.3.0`.

## Install from Disk

1. Download the exact release artifact `awful_studio-1.0.0.zip` from the AWFUL STUDIO GitHub release.
2. Do not unpack or rename the ZIP.
3. Open Blender 5.2.
4. Open **Edit → Preferences → Extensions**.
5. Open the Extensions menu and choose **Install from Disk**.
6. Select `awful_studio-1.0.0.zip`.
7. Enable **AWFUL STUDIO** if Blender does not enable it automatically.
8. Return to the 3D Viewport, press `N` and open the **AWFUL STUDIO** tab.

Installation/enabling is intentionally scene-clean. It does not build or mutate the current scene. **Build Studio** remains an explicit user action.

## Updating 1.0.x

For a direct ZIP update:

1. Save important `.blend` files normally.
2. Open Blender Preferences → Extensions.
3. Disable/remove the installed AWFUL STUDIO Extension if Blender requires replacement rather than in-place install.
4. Install the new official `awful_studio-1.0.x.zip` artifact.
5. Reopen the scene and use explicit migration only when the release notes require it.

Do not treat an Extension package as a project backup.

## First use

1. Open `N → AWFUL STUDIO`.
2. Choose **Build Studio**.
3. Use Product / Camera / Lighting / Environment presets as starting points.
4. Use **Fast Preview** for responsive look development and **Quality Preview** for a cleaner Rendered Viewport.
5. Use **Setup Post Pipeline** only when Light Groups, passes and the managed compositor are wanted.
6. Continue to use Blender's native controls for materials, lights, cameras, render settings and Cycles device/backend selection.

1.0.0 includes Bottle, Jar, Box, Can, Phone and Tablet procedural starter mockups. These are workflow starters, not the separate precision device assets currently being developed in the post-1.0 asset program.

## Rendered Viewport and GPU device

AWFUL intentionally does not rewrite Blender's CUDA/OPTIX/HIP/ONEAPI/METAL preferences or silently switch the Cycles scene Device.

A Blender profile may have a GPU backend configured globally while a new scene still uses **Render Properties → Cycles → Device = CPU**. In that state Rendered Viewport can be dramatically slower even on powerful hardware.

For workstation performance checks:

1. use the normal Blender profile rather than a factory-clean correctness profile;
2. confirm Cycles is the render engine;
3. set **Render Properties → Device → GPU Compute** when GPU rendering is intended;
4. use AWFUL diagnostics to confirm the scene is not accidentally CPU-backed;
5. compare **Fast Preview** and **Quality Preview** while navigating the Rendered Viewport.

Fast/Quality Preview changes viewport-oriented settings only. It does not silently change final output resolution, the selected device/backend or the user's broader Blender preferences.

## Network and optional HDRIs

- Base Build, Rebuild, preset switching and procedural mockup generation require no network access.
- **Download All HDRIs** is an explicit network action for the reviewed HDRI set.
- Blender Online Access remains authoritative; AWFUL also requires its explicit network consent.
- Successful downloads are provenance-bound and cached only in the configured AWFUL cache path.
- If a selected HDRI is unavailable, AWFUL keeps the user's intent while exposing a usable fallback rather than presenting a broken environment as successful.
- Cache cleanup is limited to AWFUL-owned provenance records.

Third-party asset provenance and licenses are documented in `docs/THIRD_PARTY_ASSETS.md`.

## PaintedPlaster material in 1.0.0

The invalid ambientCG PaintedPlaster PNG copies discovered in the pre-release candidate are deliberately excluded from the stable ZIP. The affected studio surfaces use AWFUL's procedural/offline fallback in 1.0.0.

This is intentional release behavior, not a missing-file installation error. A verified binary texture bundle may return in a patch after source restoration and Blender decode validation.

## Post Pipeline

**Setup Post Pipeline** prepares the optional professional post workflow:

- Cycles Light Groups;
- render passes;
- managed compositor stack.

It is intentionally not created during normal Build/Rebuild. Repeated setup is bounded/idempotent and the pipeline is qualified to remain usable after save/reopen.

## Troubleshooting

### AWFUL STUDIO is installed but no studio appears

Expected. Registration is scene-clean. Open `N → AWFUL STUDIO` and run **Build Studio** explicitly.

### Rendered Viewport is unexpectedly slow

Check AWFUL diagnostics and Blender **Render Properties → Device** first. If the scene says CPU while GPU Compute is intended, switch the scene through Blender's native control. AWFUL does not silently make that hardware decision.

### Repository sync or HDRI download is blocked

Blender must allow online access for explicit network operations. AWFUL's core studio remains usable offline. The UI should expose blocked/error state rather than silently failing.

### Optional HDRI shows Blender magenta

Confirm the download/status state and cache file. A successful AWFUL HDRI path is expected to load valid image data; magenta on a supposedly successful path is a defect worth recording.

### Floor/cyclorama does not show a detailed PaintedPlaster image texture

Expected in 1.0.0. The corrupt pre-release binary maps were removed and the procedural fallback is the supported stable behavior.

### Setup Post Pipeline reports unavailable capability

Use Blender 5.2 LTS, preferably the exact qualified Blender 5.2.1 build. The action probes live Blender capability at invocation time so save/reopen does not rely on stale process state.

### Historical 0.0.15 scene is detected

Use **Upgrade Historical AWFUL Scene**. Migration is explicit; the historical source remains immutable compatibility evidence.

### Build/Rebuild appears to change GPU settings

That is not expected. Build/Rebuild preserves Blender's native Cycles device/backend selection. Record the exact Blender version and reproduction steps.

## Release evidence

The stable release pipeline requires:

- fast/static tests green;
- official Blender Extension source/package validation;
- exact built ZIP packaged runtime green on Blender 5.2.1 Ubuntu;
- the same exact ZIP packaged runtime green on Windows;
- native Extension Repository generation/sync/install green on both platforms;
- release-hygiene and binary-asset policy checks green.

Rendered visual-regression automation remains a post-1.0 work item and is not claimed as part of 1.0.0 evidence.
