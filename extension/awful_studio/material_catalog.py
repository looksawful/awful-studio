# SPDX-License-Identifier: GPL-3.0-or-later
"""Pure catalog helpers for curated HDRI/PBR assets.

No network access is performed here. Poly Haven API records are deliberately
separate from active direct-download records so browsing can never silently
turn into downloading.
"""
from . import asset_provenance


def hdri_assets():
    return {k: v for k, v in asset_provenance.assets().items()
            if v.get('media_type') == 'image/vnd.radiance' and v.get('active')}


def pbr_materials():
    return {k: v for k, v in asset_provenance.assets().items()
            if v.get('asset_kind') == 'pbr-material'}


def polyhaven_api_endpoint(record):
    if record.get('provider') != 'Poly Haven' or record.get('distribution') != 'api-catalog':
        raise ValueError('Record is not a curated Poly Haven API catalog material')
    return record['download_url']


def preferred_maps(record):
    maps = tuple(record.get('preferred_maps', ()))
    if not maps or 'Diffuse' not in maps or 'nor_gl' not in maps or 'Rough' not in maps:
        raise ValueError('PBR material is missing the required Blender map contract')
    return maps
