# Third-party assets

AWFUL STUDIO code is licensed under GPL-3.0-or-later. Third-party media keeps its own source/license provenance and is not relicensed as AWFUL code.

The machine-readable source of truth is `extension/awful_studio/assets/provenance.json`. A remote asset must be present there and explicitly active before the Extension cache can authorize its download.

## Active optional HDRIs

All active HDRIs are remote-only, lazy, explicit opt-in cache assets. They are not bundled in the Extension ZIP and are not downloaded during import, enable, Build, Rebuild, restart, migration or ordinary preset switching.

| AWFUL key | Asset | Provider | Source | License | Packaged? |
| --- | --- | --- | --- | --- | --- |
| `hdri_fish_hoek` | Fish Hoek Beach | Poly Haven | `https://polyhaven.com/a/fish_hoek_beach` | CC0-1.0 | No |
| `hdri_blouberg` | Blouberg Sunrise 2 | Poly Haven | `https://polyhaven.com/a/blouberg_sunrise_2` | CC0-1.0 | No |
| `hdri_kloppenheim` | Kloppenheim 01 (Pure Sky) | Poly Haven | `https://polyhaven.com/a/kloppenheim_01_puresky` | CC0-1.0 | No |
| `hdri_belfast` | Belfast Sunset (Pure Sky) | Poly Haven | `https://polyhaven.com/a/belfast_sunset_puresky` | CC0-1.0 | No |
| `hdri_rogland` | Rogland Overcast | Poly Haven | `https://polyhaven.com/a/rogland_overcast` | CC0-1.0 | No |

Poly Haven license source: `https://polyhaven.com/license`.

## PaintedPlaster017 reference

ambientCG `PaintedPlaster017` remains recorded because the immutable historical implementation references its 2K PNG archive and it may be reintroduced after a verified binary restoration.

It is **not bundled in AWFUL STUDIO 1.0.0**. The pre-release copies were proven corrupt after Git text EOL normalization changed the PNG signature. Shipping knowingly invalid media would be worse than using the existing procedural fallback, so 1.0.0 contains no third-party binary texture maps for this surface.

| AWFUL key | Asset | Provider | Source | License | Packaged? |
| --- | --- | --- | --- | --- | --- |
| `painted_plaster017` | Painted Plaster 017 | ambientCG | `https://ambientcg.com/view?id=PaintedPlaster017` | CC0-1.0 | No, reference-only in 1.0.0 |

ambientCG license source: `https://docs.ambientcg.com/license/` (CC0 1.0 Universal).

## Cache policy

- Network access requires both Blender online access and the AWFUL `Allow Network Assets` preference.
- Only `active: true`, `distribution: remote-only` provenance records are downloadable.
- Reference-only records are documentation/provenance entries and are not authorized for runtime download.
- The requested destination must exactly match the provenance-derived AWFUL cache path.
- HDR downloads are bounded by the configured maximum size and checked for a Radiance header before they replace the cache target.
- Sidecar metadata records provider, asset id, source page, direct source URL, license, hash and byte count.
- Cache cleanup iterates exact active provenance records only. It never recursively deletes a user-selected directory and never follows cache symlinks.
- A third-party binary asset must not be added to the Extension package without explicit source/license review and byte-level/package-runtime validation.
- `.gitattributes` marks common media formats as `-text` so Git cannot newline-normalize them.

## Adding or reintroducing an asset

1. Verify the upstream source and license.
2. Record or update the complete provenance record.
3. If the asset is bundled, verify its binary signature/hash before commit and again from the built ZIP.
4. If the asset is remote, mark it active only when runtime download is intended and reviewed.
5. Add runtime/preset integration without creating implicit network access.
6. Run fast tests and packaged Blender runtime checks.
7. For image media, prove Blender can actually decode the package bytes before release.

Do not add a URL or binary first and promise to document/validate it later. That is how asset provenance becomes archaeology with extra magenta pixels.
