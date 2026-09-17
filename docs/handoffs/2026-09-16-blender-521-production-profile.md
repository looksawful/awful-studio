# Blender 5.2.1 production workstation profile

Issue: #86
Date: 2026-09-16
Machine: Titan
Runtime: Blender 5.2.1 LTS, build `9e2066aef7ef`

## Scope

This change makes the Titan workstation profile reproducible for AWFUL STUDIO device and hard-surface work. It does not change AWFUL scene-building behavior, Adobe/Substance add-on preferences, or device source assets.

## Applied profile

- Asset libraries preserved: `A:\assets\3D ASSET`, `A:\Textures`, `A:\assets\SUBSTANCE`.
- Autosave enabled at 2 minutes; 2 backup versions; 64 undo steps; unlimited undo memory cap.
- Cycles compute backend: `OPTIX`; RTX 4070 Ti OptiX enabled; CPU compute disabled.
- Bool Tool: `EXACT` solver; destructive apply order limited to Boolean modifiers.
- ND: fast booleans disabled so hard-surface boolean behavior stays exact.
- K-Tools Texture Map Loader: sanitized/folder-based names, bump-only displacement default, no automatic packing into `.blend`.
- AmbientCG importer cache: `A:\Textures\ambientCG`.
- CAD Sketcher: decimal precision 4, angle precision 1, What's New disabled.
- Blender MCP remains enabled; live GUI listener verified on `127.0.0.1:9876`.

## Keymap policy

ND remains the primary Ctrl+NumPad hard-surface boolean layer. `awful_studio_keymap_overrides.py` persistently disables only the four overlapping Bool Tool Ctrl+NumPad brush bindings and the overlapping Bool Tool `Ctrl+Shift+B` popup. Bool Tool itself remains enabled and available through its UI/operators. Substance shortcut conflicts were intentionally left unchanged because Adobe/Substance settings were out of scope.

## Runtime evidence

- Live GUI MCP: `LIVE_MCP_VERIFY_PASS` / `LIVE_PROFILE_ASSERT_PASS`.
- Headless setup from repository: `AWFUL_BLENDER_SETUP`, exit code 0.
- Fresh persisted-profile process: `VERIFY_PROFILE_PASS 5.2.1 LTS OPTIX`.
- Fresh keymap/operator process: `VERIFY_KEYMAPS_PASS`, four duplicate Bool Tool bindings inactive, 9 target operators registered.
- Runtime smoke: `GLTF_ROUNDTRIP_PASS 1732`, `FBX_ROUNDTRIP_PASS 11836`, `SVG_IMPORT_PASS`, `BOOL_TOOL_PASS 12`, `SMOKE_ROUNDTRIP_PASS`, exit code 0.

Observed startup noise outside this task includes the Substance add-on's process-lifecycle messages and Blender probing the unavailable AMD HIP runtime on an NVIDIA-only workstation. Neither affected the verified target operations; this change does not modify those integrations.

## Preferences backup

- Before-production backup: `A:\assets\3D ASSET\Blender\config-backups\userpref-5.2.1-production-20260916-175208.blend`
- Backup SHA-256: `483D3692AB3811887F45A1D7437C83D7F99F15C286C2326535645370756D883E`
- Current `userpref.blend` SHA-256 after live/headless synchronization: `858ABF1209EF6801D98A66F2802F690AF6F6CCF90D126A2A14E2E1515F1E22C0`

## Repository files

- `tools/blender/configure_production_profile.py`
- `tools/blender/awful_studio_keymap_overrides.py`
- `tools/blender/verify_profile.py`
- `tools/blender/verify_keymaps.py`
- `tools/blender/smoke_roundtrip.py`
- `tests/fast/test_blender_production_profile_contract.py`
