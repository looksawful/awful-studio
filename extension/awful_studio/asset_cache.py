"""Opt-in provenance-backed asset cache. No work occurs at import/enable/startup."""
import hashlib
import json
import os
from pathlib import Path
import urllib.request

from . import asset_provenance

MAX_BYTES = 128 * 1024 * 1024
_LAST_ERROR = ''


def preferences():
    import bpy
    entry = bpy.context.preferences.addons.get(__package__)
    return entry.preferences if entry else None


def root():
    import bpy
    prefs = preferences()
    base = prefs.asset_cache_path if prefs and prefs.asset_cache_path else bpy.utils.user_resource('DATAFILES')
    return Path(bpy.path.abspath(base)).expanduser() / 'awful-studio-cache-v1'


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def read_valid(path):
    path = Path(path)
    try:
        meta = json.loads(path.with_suffix(path.suffix + '.json').read_text())
        return (meta['status'] == 'ready' and 0 < path.stat().st_size <= MAX_BYTES
                and digest(path) == meta['sha256'])
    except (OSError, ValueError, KeyError):
        return False


def last_error():
    return _LAST_ERROR or 'Asset unavailable; procedural fallback remains active'


def _active_record_for_url(url):
    record = asset_provenance.record_for_url(url)
    if not record or not record['active'] or record['distribution'] != 'remote-only':
        raise ValueError('Only provenance-reviewed active remote assets may be downloaded')
    return record


def fetch(url, path, force=False):
    import bpy
    global _LAST_ERROR
    prefs = preferences()
    if not prefs or not prefs.allow_network_assets or not bpy.app.online_access:
        raise RuntimeError('Enable Blender online access and AWFUL Allow Network Assets first')
    record = _active_record_for_url(url)
    path = Path(path)
    expected = root() / record.get('cache_subdir', '') / record['filename']
    if path.is_symlink() or path.resolve() != expected.resolve():
        raise ValueError('Asset destination must match its provenance cache path')
    if not force and read_valid(path):
        return True
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + '.part')
    sidecar = path.with_suffix(path.suffix + '.json')
    if temp.is_symlink() or sidecar.is_symlink():
        raise ValueError('Symlink cache files are not writable')
    metadata = {
        'provider': record['provider'],
        'asset_id': record['asset_id'],
        'title': record['title'],
        'source_page': record['source_page'],
        'source_url': url,
        'license': record['license'],
        'license_url': record['license_url'],
        'distribution': record['distribution'],
        'status': 'downloading',
    }
    try:
        request = urllib.request.Request(url, headers={'User-Agent': 'AWFUL-Studio/0.0.16'})
        with urllib.request.urlopen(request, timeout=30) as response, temp.open('wb') as output:
            if response.url != url:
                raise ValueError('Unexpected asset redirect; review the curated source')
            total = 0
            for chunk in iter(lambda: response.read(1024 * 1024), b''):
                total += len(chunk)
                if total > MAX_BYTES:
                    raise ValueError('Asset exceeds the cache download limit')
                output.write(chunk)
        with temp.open('rb') as stream:
            if record.get('media_type') == 'image/vnd.radiance':
                if not stream.read(16).startswith((b'#?RADIANCE', b'#?RGBE')):
                    raise ValueError('Downloaded asset is not a Radiance HDR image')
        metadata.update(status='ready', sha256=digest(temp), bytes=total)
        os.replace(temp, path)
        sidecar.write_text(json.dumps(metadata, indent=2), encoding='utf-8')
        _LAST_ERROR = ''
        return True
    except (OSError, ValueError) as exc:
        _LAST_ERROR = str(exc)
        metadata.update(status='error', error=_LAST_ERROR)
        sidecar.write_text(json.dumps(metadata, indent=2), encoding='utf-8')
        temp.unlink(missing_ok=True)
        return False


def clear():
    # Delete only exact active provenance-bearing files. Never recurse into a
    # user-selected cache parent and never follow symlinks.
    removed = 0
    cache_root = root().resolve()
    for record in asset_provenance.active_assets().values():
        path = root() / record.get('cache_subdir', '') / record['filename']
        sidecar = path.with_suffix(path.suffix + '.json')
        if path.is_symlink() or sidecar.is_symlink() or not path.resolve().is_relative_to(cache_root):
            continue
        try:
            meta = json.loads(sidecar.read_text(encoding='utf-8'))
            if (meta.get('source_url') != record['download_url'] or
                    meta.get('asset_id') != record['asset_id']):
                continue
            path.unlink(missing_ok=True)
            sidecar.unlink()
            removed += 1
        except (OSError, ValueError):
            continue
    return removed
