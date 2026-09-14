# SPDX-License-Identifier: GPL-3.0-or-later
"""Bundled device-asset catalog and Blender append adapter."""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path


DEVICE_ASSET_SPECS = {
    'DEVICE_IPHONE_17': {
        'label': 'iPhone 17 (LOW draft)',
        'asset_id': 'iphone_17',
        'stage': 'LOW_DRAFT',
        'variant': 'low_v10',
        'dimensions_m': (0.0715, 0.00795, 0.1496),
        'blend_path': 'assets/devices/iphone_17_low_v10.blend',
        'entry_collection': 'AWFUL_DEVICE_IPHONE_17',
        'root_name': 'CTRL_IPHONE_17',
        'source_revision': 'a1003c674ed83182cee6bf70816168f2c6533947594553d9cba6d2a6bc75d586',
    },
    'DEVICE_IPAD_PRO_11': {
        'label': 'iPad Pro 11 M5',
        'asset_id': 'ipad_pro_11_m5',
        'stage': 'RELEASE_CANDIDATE',
        'variant': 'low_v1_release',
        'dimensions_m': (0.1775, 0.0053, 0.2497),
        'blend_path': 'assets/devices/ipad_pro_11_m5_low_v1_release.blend',
        'entry_collection': 'AWFUL_DEVICE_IPAD_PRO_11',
        'root_name': 'CTRL_IPAD_PRO_11',
        'source_revision': '379f203ee49f97f11ecb13b7a1d4b31141330c18fff509b769543d4dd1b21900',
    },
    'DEVICE_IPAD_PRO_13': {
        'label': 'iPad Pro 13 M5',
        'asset_id': 'ipad_pro_13_m5',
        'stage': 'RELEASE_CANDIDATE',
        'variant': 'low_v1_release',
        'dimensions_m': (0.2155, 0.0051, 0.2816),
        'blend_path': 'assets/devices/ipad_pro_13_m5_low_v1_release.blend',
        'entry_collection': 'AWFUL_DEVICE_IPAD_PRO_13',
        'root_name': 'CTRL_IPAD_PRO_13',
        'source_revision': '3eca4df4deaf161ee2bedc8a4a5b9d0d43e2a5342dbd5deff994e385f07c7a74',
    },
    'DEVICE_MACBOOK_PRO_14': {
        'label': 'MacBook Pro 14 M5',
        'asset_id': 'macbook_pro_14_m5',
        'stage': 'RELEASE_CANDIDATE',
        'variant': 'low_v1_release',
        'dimensions_m': (0.3126, 0.2212, 0.0155),
        'blend_path': 'assets/devices/macbook_pro_14_m5_low_v1_release.blend',
        'entry_collection': 'AWFUL_DEVICE_MACBOOK_PRO_14',
        'root_name': 'CTRL_MACBOOK_PRO_14',
        'source_revision': '6c5c67ae9aac7b0888ee226ffce3071052eb32b42d86ddff14c0c89e755c0530',
        'controls': ('CTRL_HINGE',),
    },
}


def device_asset_keys() -> tuple[str, ...]:
    return tuple(DEVICE_ASSET_SPECS)


def device_asset_spec(key: str) -> dict:
    try:
        return deepcopy(DEVICE_ASSET_SPECS[key])
    except KeyError as exc:
        raise ValueError(f'Unknown AWFUL device asset: {key}') from exc


def device_asset_path(key: str) -> Path:
    spec = device_asset_spec(key)
    return Path(__file__).resolve().parent / spec['blend_path']


def is_device_asset_key(key: str) -> bool:
    return key in DEVICE_ASSET_SPECS


def _managed_role(prefix: str, key: str, name: str = '') -> str:
    suffix = name.replace(' ', '_').upper() if name else key
    return f'{prefix}_{key}_{suffix}'

def create_device_asset(legacy, scene, key):
    spec = device_asset_spec(key)
    path = device_asset_path(key)
    if not path.is_file():
        raise RuntimeError(f'Bundled AWFUL device asset is missing: {path.name}')
    product_collection = legacy.REG.collection('COL_PRODUCT')
    if product_collection is None:
        raise RuntimeError('AWFUL product collection is missing; Build Studio first')

    bpy = legacy.bpy
    with bpy.data.libraries.load(str(path), link=False) as (data_from, data_to):
        entry = spec['entry_collection']
        if entry not in data_from.collections:
            raise RuntimeError(f'{path.name} is missing collection {entry}')
        data_to.collections = [entry]
    collection = data_to.collections[0]
    if collection is None:
        raise RuntimeError(f'Unable to append bundled device asset: {key}')
    product_collection.children.link(collection)
    legacy.mark_managed(collection, _managed_role('MOCKUP_DEVICE_COLLECTION', key))

    root = collection.objects.get(spec['root_name'])
    if root is None:
        raise RuntimeError(f'{path.name} is missing root {spec["root_name"]}')
    legacy.mark_managed(root, 'MOCKUP_ROOT')
    root['awful_mockup_key'] = key
    root['awful_mockup_source_dimensions_m'] = tuple(float(v) for v in spec['dimensions_m'])
    root['awful_asset_id'] = spec['asset_id']
    root['awful_asset_stage'] = spec['stage']
    root['awful_asset_variant'] = spec['variant']
    root['awful_asset_source_revision'] = spec['source_revision']

    for obj in [root] + legacy.descendants(root):
        if obj != root:
            legacy.mark_managed(obj, _managed_role('MOCKUP_DEVICE_OBJECT', key, obj.name))
        data = getattr(obj, 'data', None)
        if data is not None:
            legacy.mark_managed(data, _managed_role('MOCKUP_DEVICE_DATA', key, obj.name))
        if getattr(data, 'materials', None) is not None:
            for material in data.materials:
                if material is not None:
                    legacy.mark_managed(
                        material,
                        _managed_role('MOCKUP_MAT_DEVICE', key, material.name),
                    )
    return root


def purge_orphan_device_collections(legacy, scene):
    bpy = legacy.bpy
    for collection in list(bpy.data.collections):
        role = str(collection.get(legacy.ROLE_KEY, ''))
        if (legacy.ownership.owned(collection, scene)
                and role.startswith('MOCKUP_DEVICE_COLLECTION_')
                and len(collection.objects) == 0):
            bpy.data.collections.remove(collection)
