# SPDX-License-Identifier: GPL-3.0-or-later
"""Explicit local integration for user-acquired third-party asset libraries."""
from functools import lru_cache
import json
from pathlib import Path

_CATALOG = Path(__file__).with_name('assets') / 'external_libraries.json'
_IMPORTERS = {'.obj': 'obj', '.fbx': 'fbx', '.gltf': 'gltf', '.glb': 'gltf'}


@lru_cache(maxsize=1)
def catalog():
    data = json.loads(_CATALOG.read_text(encoding='utf-8-sig'))
    if data.get('schema_version') != 1 or not isinstance(data.get('libraries'), dict):
        raise RuntimeError('Invalid AWFUL external asset library catalog')
    return data


def discover(root):
    root = Path(root).expanduser()
    if not root.is_dir():
        return []
    return sorted(path for path in root.rglob('*') if path.is_file() and path.suffix.lower() in _IMPORTERS)


def register_asset_browser_root(bpy, root, name='AWFUL External Assets'):
    root = Path(root).expanduser().resolve()
    if not root.is_dir():
        raise ValueError('External asset library directory does not exist')
    libraries = bpy.context.preferences.filepaths.asset_libraries
    for library in libraries:
        if Path(library.path).resolve() == root:
            return library
    return libraries.new(name=name, directory=str(root))


def import_asset(bpy, filepath):
    path = Path(filepath).expanduser().resolve()
    if not path.is_file():
        raise ValueError('External asset file does not exist')
    kind = _IMPORTERS.get(path.suffix.lower())
    if kind == 'obj':
        return bpy.ops.wm.obj_import(filepath=str(path))
    if kind == 'fbx':
        return bpy.ops.wm.fbx_import(filepath=str(path))
    if kind == 'gltf':
        return bpy.ops.import_scene.gltf(filepath=str(path))
    raise ValueError(f'Unsupported external asset format: {path.suffix}')
