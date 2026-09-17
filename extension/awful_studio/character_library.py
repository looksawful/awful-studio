# SPDX-License-Identifier: GPL-3.0-or-later
"""Pure discovery helpers for user-managed character, rig and mocap libraries."""
from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path

_CATALOG = Path(__file__).with_name('character_assets') / 'catalog.json'
_REQUIRED = {
    'provider', 'title', 'kind', 'source_page', 'license', 'license_url',
    'commercial_use', 'redistribution', 'formats', 'import_formats',
    'recommended_subdir', 'install_mode', 'requires_account', 'active',
}
_IMPORT_PLANS = {
    '.fbx': {'strategy': 'operator', 'operator': 'wm.fbx_import'},
    '.obj': {'strategy': 'operator', 'operator': 'wm.obj_import'},
    '.gltf': {'strategy': 'operator', 'operator': 'import_scene.gltf'},
    '.glb': {'strategy': 'operator', 'operator': 'import_scene.gltf'},
    '.bvh': {'strategy': 'operator', 'operator': 'import_anim.bvh'},
    '.blend': {'strategy': 'blend-library'},
    '.mhx2': {'strategy': 'external-addon'},
}


@lru_cache(maxsize=1)
def catalog() -> dict:
    data = json.loads(_CATALOG.read_text(encoding='utf-8-sig'))
    if data.get('schema_version') != 1 or data.get('library_kind') != 'character-rig-mocap':
        raise RuntimeError('Invalid AWFUL character asset catalog')
    for key, record in data.get('libraries', {}).items():
        missing = _REQUIRED.difference(record)
        if missing:
            raise RuntimeError(f'Character asset catalog {key} missing: {sorted(missing)}')
        if not str(record['source_page']).startswith('https://'):
            raise RuntimeError(f'Character asset catalog {key} has invalid source page')
        formats = {str(fmt).lower().lstrip('.') for fmt in record['formats']}
        import_formats = {str(fmt).lower().lstrip('.') for fmt in record['import_formats']}
        if not import_formats.issubset(formats):
            raise RuntimeError(f'Character asset catalog {key} imports undeclared formats')
        subdir = Path(record['recommended_subdir'])
        if subdir.is_absolute() or '..' in subdir.parts:
            raise RuntimeError(f'Character asset catalog {key} has unsafe subdir')
    return data


def libraries() -> dict[str, dict]:
    return catalog()['libraries']


def library_root(cache_root: Path | str, key: str) -> Path:
    record = libraries().get(key)
    if record is None:
        raise KeyError(f'Unknown character asset library: {key}')
    return Path(cache_root).expanduser() / 'characters' / Path(record['recommended_subdir'])


def discover(cache_root: Path | str) -> dict[str, dict]:
    """Describe local availability without downloading or importing anything."""
    result = {}
    for key, record in libraries().items():
        root = library_root(cache_root, key)
        present = root.is_dir() and any(root.iterdir())
        result[key] = {
            'path': str(root),
            'present': present,
            'provider': record['provider'],
            'kind': record['kind'],
            'license': record['license'],
            'install_mode': record['install_mode'],
        }
    return result


def import_plan(path: Path | str) -> dict[str, str]:
    """Describe the Blender 5.2 handoff for a supported interchange file."""
    suffix = Path(path).suffix.lower()
    plan = _IMPORT_PLANS.get(suffix)
    if plan is None:
        raise ValueError(f'Unsupported direct Blender character import format: {suffix or "<none>"}')
    return dict(plan)


def import_candidates(cache_root: Path | str, key: str) -> list[Path]:
    """Return safe files AWFUL can hand to Blender; no Blender dependency here."""
    record = libraries().get(key)
    if record is None:
        raise KeyError(f'Unknown character asset library: {key}')
    root = library_root(cache_root, key)
    if not root.is_dir():
        return []
    suffixes = {'.' + str(fmt).lower().lstrip('.') for fmt in record['import_formats']}
    resolved_root = root.resolve()
    candidates = []
    for path in root.rglob('*'):
        if path.is_symlink() or not path.is_file() or path.suffix.lower() not in suffixes:
            continue
        try:
            if not path.resolve().is_relative_to(resolved_root):
                continue
        except OSError:
            continue
        candidates.append(path)
    return sorted(candidates)
