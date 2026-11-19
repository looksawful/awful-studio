# Domain

Single product: Blender-native virtual shooting studio as a Blender 5.2 Extension. Preserve source-to-runtime and extension ZIP provenance, multi-scene/user-data ownership, offline default behavior and native Blender controls.

- Domain: `extension/awful_studio/`, presets and scenes; active architecture is governed by AGENTS.md and accepted specs.
- Verification: `python tools/awful.py fast`; Blender runtime gates only when explicitly invoked, using exact pinned target.
- Visual catalog: `preview/` already hosts the canonical 3D Storybook, not a second rendering engine.
- Historical alpha baseline is immutable. Avoid duplicate runtime/bootstrap/test paths.
