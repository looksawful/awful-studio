# MacBook Pro 14 M5 device asset

Current reproducible state: `RELEASE_CANDIDATE`.
This preserves the current reviewed low-v1 scene without claiming the separate production-LOW review gate in issue #52 has passed.

## Build

Use Blender 5.2.1 LTS:

```powershell
blender --background --factory-startup --python generate_low.py
```

The generator writes:
- `generated/macbook_pro_14_m5_low_v1_release.blend`
- `evidence/low_v1_release_validation.json`

The release source contains the hinge-driven lid assembly, keyboard deck, trackpad, speaker fields, ports, feet, display stack, FaceTime camera and packed Apple-logo source image.

## Preview evidence
Render the six current diagnostic views from the generated release file:

```powershell
blender generated/macbook_pro_14_m5_low_v1_release.blend --background --python render_current_previews.py
```

The renderer produces hero, front, side, keyboard, hinge and ports views in `previews/current/`.

## Validation contract

The generator verifies base and lid dimensions, zero non-manifold edges on both chassis meshes, required functional objects, the 102-degree hinge preset and the release metadata before saving.

Run the full mechanical hinge gate against the generated candidate:

```powershell
blender generated/macbook_pro_14_m5_low_v1_release.blend --background --python validate_hinge_clearance.py -- --out evidence/hinge_clearance_validation.json
```

The hinge validator checks solid intersections at CLOSED / 30 / 60 / 90 / 102 for both hinge barrels and covers against the base and against each other. The committed acceptance evidence must report zero intersection volume at all five presets.

Render the deterministic human-review pack with:

```powershell
blender generated/macbook_pro_14_m5_low_v1_release.blend --background --python render_hinge_acceptance.py -- --out previews/acceptance_v1
```

The current release candidate intentionally differs from the earlier pre-clearance candidate: local base hinge recesses and hollow hinge covers remove the solid collisions while preserving the verified chassis envelope.
