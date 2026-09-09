"""Opt-in asset cache. No work is performed at import, enable or Blender startup."""
import hashlib
import json
import os
from pathlib import Path
import urllib.request

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


def fetch(url, path, force=False):
    import bpy
    from .core.legacy import ASSET_URLS
    global _LAST_ERROR
    prefs = preferences()
    if not prefs or not prefs.allow_network_assets or not bpy.app.online_access:
        raise RuntimeError('Enable Blender online access and AWFUL Allow Network Assets first')
    allowed = {u for _, u in ASSET_URLS.values()}
    if url not in allowed:
        raise ValueError('Only curated official asset URLs may be downloaded')
    path = Path(path)
    if path.is_symlink() or not path.resolve().is_relative_to(root().resolve()):
        raise ValueError('Asset destination must be inside the AWFUL cache')
    if not force and read_valid(path):
        return True
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + '.part')
    sidecar = path.with_suffix(path.suffix + '.json')
    if temp.is_symlink() or sidecar.is_symlink():
        raise ValueError('Symlink cache files are not writable')
    metadata = {'source_url': url, 'license': 'CC0-1.0',
                'license_url': 'https://polyhaven.com/license', 'status': 'downloading'}
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
    # Only known, provenance-bearing cache files; never recursively delete a user directory.
    from .core.legacy import ASSET_URLS
    removed = 0
    for filename, url in ASSET_URLS.values():
        path = root() / 'hdri' / filename
        sidecar = path.with_suffix(path.suffix + '.json')
        if path.is_symlink() or sidecar.is_symlink() or not path.resolve().is_relative_to(root().resolve()):
            continue
        try:
            if json.loads(sidecar.read_text()).get('source_url') != url:
                continue
            path.unlink(missing_ok=True)
            sidecar.unlink()
            removed += 1
        except (OSError, ValueError):
            continue
    return removed
