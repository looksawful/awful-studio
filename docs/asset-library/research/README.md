# AWFUL STUDIO Asset Research

This directory is the evidence layer for production-grade 3D asset work. It exists to prevent reference drift, guessed dimensions, accidental model conflation and texture decisions made from vibes.

## Rules

1. Presence in the historical Sensetique inventory is a separate fact from technical dimensions.
2. Manufacturer documentation is the primary source for geometry and mechanical interfaces.
3. Historical studio pages may confirm that an item was present, but copied CMS fields are not accepted as dimensional truth.
4. Every value is tagged conceptually as `VERIFIED`, `DERIVED`, `ESTIMATED` or `UNKNOWN`.
5. Conflicting values are preserved and resolved explicitly; they are never silently averaged.
6. Photos are reference evidence, not scale drawings unless a known dimension is visible in the same projection.
7. Logos, serial plates and control legends belong to decals/masks unless they materially change silhouette.
8. High-poly work is allowed only when it contributes to silhouette, bake, deformation or hero close-up quality.
9. `HISTORICAL_*` and `REPRESENTATIVE_*` identities must never be conflated. A technically excellent reference model is not historical evidence by osmosis.

## Wave 01 / 01B

Scope: Sensetique studio lighting inventory, support/grip research and the first AWFUL STUDIO configurable studio-rig family.

Files:

- `sensetique-studio-equipment-wave-01.md` — researched historical inventory, dimensions, modeling decomposition, conflicts and model priorities.
- `support-grip-wave-01b.md` — representative Avenger support/grip standard with explicit historical-identity disclaimer.
- `dimensional-diagrams-wave-01.md` — derived dimensional/interface diagrams, coordinate conventions and blockout formulas.
- `studio-equipment-specs.csv` — machine-readable dimensional/specification table.
- `modeling-material-brief-wave-01.md` — geometry, material, texture and bake guidance.
- `source-register-wave-01.md` — equipment source/provenance register and confidence notes.
- `source-register-wave-01b-support.md` — support/grip sources, Dedolight envelope corroboration and ARRI CAD route.

## Canonical first vertical slice

`A2025F_REP C-Stand + Profoto D1 500 Air + Profoto Magnum Reflector + G200-1_REP Sandbag`

The D1 and Magnum are historical/evidence-ready. The support and sandbag use explicitly representative Avenger identities until historical Sensetique SKUs are proven.

## Current research gates

### Ready for technical drawing / precision blockout preparation

- Profoto D1 500 Air.
- Profoto Magnum Reflector 100624.
- Profoto Zoom Reflector 100785.
- Profoto Softlight Reflector 100607 / 100608.
- Profoto RFi 2x3 / 3x4 / 5' Octa.
- ARRI 300 Plus, with manufacturer 2D CAD route identified.
- Avenger A2025F / D200 / D520 as representative support components.

### Research more before claiming precision/historical approval

- Dedolight DLHM4-300: secondary envelope `171 x 132 x 174 mm` found, but axis order and manufacturer drawing still need corroboration.
- Fotokvant Evenly 30 x 160: exact depth/internal construction.
- D600 boom: manufacturer page contains internally inconsistent structured min/max fields; inspect drawing.
- Exact historical C-stand / light-stand brands and models.
- Exact Canon body and lens SKU.
- Exact Sensetique furniture manufacturers/models.

## Known conflicts

- Historical Grifon octabox conflict: current portfolio says `SB-FW95 95 cm`; archived studio page labels an octa as `101 cm`. Treat `SB-FW95 / 95 cm` as the confirmed model and keep the archived 101 cm label as a CMS/history discrepancy until original purchase records are found.
- Acute/D4 cable length differs across Profoto revisions. Keep cable procedural and retain the conflict in metadata.
- Archived Sensetique pages contain clearly copied/invalid dimensional fields for some continuous fixtures. Those fields are never used as geometry evidence.
- Current Avenger D600 regional product metadata reverses/mangles boom min/max fields while manufacturer prose gives a sensible range. Do not encode the malformed structured values.
