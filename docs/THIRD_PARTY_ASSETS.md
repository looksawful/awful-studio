# Third-party assets

AWFUL STUDIO code is licensed separately under GPL-3.0-or-later. Optional third-party media is not relicensed as AWFUL code.

The machine-readable source of truth is `extension/awful_studio/assets/provenance.json`. A remote asset must be present there before the Extension cache will authorize its download.

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

## Bundled floor/cyclorama PBR maps

The current Extension bundles four reviewed ambientCG `PaintedPlaster017` maps so the default visible floor and cyclorama material work offline and do not fall back to a missing-texture/magenta state.

| AWFUL key | Asset | Provider | Source | License | Packaged? |
| --- | --- | --- | --- | --- | --- |
| `painted_plaster017` | Painted Plaster 017 | ambientCG | `https://ambientcg.com/view?id=PaintedPlaster017` | CC0-1.0 | Yes, selected 2K PNG maps |

Bundled files are listed in `extension/awful_studio/assets/ATTRIBUTION.md` and in the `bundled_files` field of `extension/awful_studio/assets/provenance.json`. The historical 2K PNG ZIP URL remains recorded because the immutable 0.0.15 fixture still contains it, but the current Extension does not authorize that ZIP as an active network download.

ambientCG license source: `https://docs.ambientcg.com/license/` (CC0 1.0 Universal).

## Cache policy

- Network access requires both Blender online access and the AWFUL `Allow Network Assets` preference.
- Only `active: true`, `distribution: remote-only` provenance records are downloadable. Bundled records are local package assets and are never fetched over the network.
- The requested destination must exactly match the provenance-derived AWFUL cache path.
- HDR downloads are bounded by the configured maximum size and checked for a Radiance header before they replace the cache target.
- Sidecar metadata records provider, asset id, source page, direct source URL, license, hash and byte count.
- Cache cleanup iterates exact active provenance records only. It never recursively deletes a user-selected directory and never follows cache symlinks.
- A third-party binary asset must not be added to the Extension package without a separate explicit review, attribution file entry and corresponding provenance/distribution change.

## Adding an asset

1. Add a complete record to `assets/provenance.json`.
2. Mark it active only if the Extension is intended to fetch it.
3. Keep provider source and license URLs separate from the direct download URL.
4. Add the runtime/preset reference.
5. Run fast tests. `test_asset_provenance_contract.py` rejects unrecorded third-party `.hdr`/`.zip` URLs and any bundled third-party binary media except the reviewed floor maps listed in provenance.
6. Let packaged Blender 5.2.1 CI verify offline Build/preset behavior and the official Extension package.

Do not add a remote URL first and promise to document it later. That is how provenance turns into archaeology.
