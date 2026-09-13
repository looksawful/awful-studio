# AWFUL STUDIO third-party asset attribution

## Painted Plaster 017

- Provider: ambientCG
- Asset: PaintedPlaster017
- Source page: https://ambientcg.com/view?id=PaintedPlaster017
- License: Creative Commons CC0 1.0 Universal
- License URL: https://docs.ambientcg.com/license/
- Distribution in AWFUL STUDIO 1.0.0: reference-only; no PaintedPlaster binary maps are bundled.

The pre-release copies were removed after byte-level inspection proved that Git text EOL normalization had corrupted their PNG signatures. AWFUL STUDIO 1.0.0 uses the existing procedural/offline material fallback instead of shipping invalid third-party media.

A future patch may reintroduce selected maps only after restoring them from the reviewed upstream archive and validating the exact packaged bytes with Blender.
