"""Opt-in provenance-backed asset cache. No work occurs at import/enable/startup."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import urllib.request

from . import asset_provenance, asset_workflow

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


def legacy_root():
    import bpy
    try:
        return Path(bpy.utils.user_resource('DATAFILES')).expanduser() / 'awful_studio' / 'assets'
    except Exception:
        return root().parent / 'awful_studio' / 'assets'


def _ready_metadata(record, source_url, sha256, size):
    return {
        'provider': record['provider'],
        'asset_id': record['asset_id'],
        'title': record['title'],
        'source_page': record['source_page'],
        'source_url': source_url,
        'license': record['license'],
        'license_url': record['license_url'],
        'distribution': record['distribution'],
        'status': 'ready',
        'sha256': sha256,
        'bytes': int(size),
        'migrated_from': 'legacy-awful_studio/assets',
    }


def migrate_legacy_asset(record):
    """Import a same-provider file from the pre-0.0.17 cache, no network involved."""
    global _LAST_ERROR
    if record.get('distribution') != 'remote-only':
        return False
    destination = root() / record.get('cache_subdir', '') / record['filename']
    if read_valid(destination):
        return True
    source = legacy_root() / record.get('cache_subdir', '') / record['filename']
    try:
        if source.is_symlink() or not source.is_file():
            return False
        size = source.stat().st_size
        if not 0 < size <= MAX_BYTES:
            return False
        destination.parent.mkdir(parents=True, exist_ok=True)
        temp = destination.with_suffix(destination.suffix + '.part')
        if temp.is_symlink():
            raise ValueError('Symlink cache files are not writable')
        shutil.copy2(source, temp)
        if record.get('media_type') == 'image/vnd.radiance':
            with temp.open('rb') as stream:
                if not stream.read(16).startswith((b'#?RADIANCE', b'#?RGBE')):
                    raise ValueError('Legacy cache asset is not a Radiance HDR image')
        sha256 = digest(temp)
        os.replace(temp, destination)
        sidecar = destination.with_suffix(destination.suffix + '.json')
        sidecar.write_text(
            json.dumps(_ready_metadata(record, record['download_url'], sha256, size), indent=2),
            encoding='utf-8',
        )
        _LAST_ERROR = ''
        return True
    except (OSError, ValueError) as exc:
        _LAST_ERROR = str(exc)
        try:
            temp.unlink(missing_ok=True)
        except Exception:
            pass
        return False


def _active_record_for_url(url):
    record = asset_provenance.record_for_url(url)
    if not record or not record['active'] or record['distribution'] != 'remote-only':
        raise ValueError('Only provenance-reviewed active remote assets may be downloaded')
    return record


def fetch(url, path, force=False):
    import bpy
    global _LAST_ERROR
    prefs = preferences()
    permission = asset_workflow.permission_state(
        blender_online=bool(bpy.app.online_access),
        awful_consent=bool(prefs and prefs.allow_network_assets),
    )
    if not permission['ready']:
        raise RuntimeError(str(permission['message']))
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
    metadata = _ready_metadata(record, url, '', 0)
    metadata['status'] = 'downloading'
    metadata.pop('sha256', None)
    metadata.pop('bytes', None)
    metadata.pop('migrated_from', None)
    try:
        request = urllib.request.Request(url, headers={'User-Agent': 'AWFUL-Studio/0.0.17'})
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
