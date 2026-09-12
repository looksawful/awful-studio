# AWFUL STUDIO Scene Lab

This directory is intentionally independent from `extension/awful_studio`.

Goal: author portfolio-grade Blender 5.2 scenes first, then integrate only approved scene ideas into the Extension later.

## Branch policy

- `scene/hero-scenes-foundation` — shared production contract and helpers only.
- `scene/white-studio-v1` — bright commercial studio.
- `scene/loft-daylight-v1` — daylight loft / lifestyle studio.
- `scene/dark-neon-v1` — dark cyan-magenta tech studio.

No scene branch may modify `extension/awful_studio/**` during this phase.

## Deliverables per scene

- `scene.json` — dimensions, camera, hero reserve, materials, lights, prop strategy.
- `build_scene.py` — deterministic Blender 5.2 builder.
- `README.md` — art direction and acceptance criteria.
- generated `.blend` and review renders are produced locally and are not source-of-truth until visually approved.

## Production rules

1. Real metre scale.
2. One explicit hero reserve around `PRODUCT_ANCHOR`.
3. Architecture is procedural and editable; generated assets are decorative only.
4. Materials must separate base color, roughness, normal/bump intent and displacement where useful.
5. Lighting must create readable form, controlled reflections and deliberate negative fill.
6. Camera composition is part of the scene contract, not an afterthought.
7. No dependency on the AWFUL STUDIO add-on while authoring these scenes.
8. Tripo/to3D/Meshy-style generation is reserved for approved decorative props, never structural walls/floors/ceilings.

## Local build command

```powershell
blender.exe --background --factory-startup --python scene_lab/<scene>/build_scene.py -- --output A:/.../<scene>.blend
```

Review renders may be generated after the `.blend` is structurally built, but render approval remains separate from structural success.
