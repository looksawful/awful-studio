# SPDX-License-Identifier: GPL-3.0-or-later
"""Pure helpers for packaged third-party asset provenance.

The inventory is local package metadata. Importing this module never performs
network access or touches Blender state.
"""
from functools import lru_cache
import json
from pathlib import Path

_INVENTORY = Path(__file__).with_name('assets') / 'provenance.json'
_REQUIRED = {
    'provider', 'asset_id', 'title', 'source_page', 'download_url',
    'filename', 'license', 'license_url', 'distribution', 'active',
}


@lru_cache(maxsize=1)
def inventory():
    data = json.loads(_INVENTORY.read_text(encoding='utf-8'))
    if data.get('schema_version') != 1 or not isinstance(data.get('assets'), dict):
        raise RuntimeError('Invalid AWFUL asset provenance inventory')
    for key, record in data['assets'].items():
        missing = _REQUIRED.difference(record)
        if missing:
            raise RuntimeError(f'Asset provenance {key} missing: {sorted(missing)}')
    return data


def assets():
    return inventory()['assets']


def active_assets():
    return {key: record for key, record in assets().items() if record['active']}


def record_for_key(key):
    try:
        return assets()[key]
    except KeyError as exc:
        raise KeyError(f'Unknown AWFUL asset provenance key: {key}') from exc


def record_for_url(url):
    for record in assets().values():
        if record['download_url'] == url:
            return record
    return None


def active_download_map():
    return {
        key: (record['filename'], record['download_url'])
        for key, record in active_assets().items()
    }
