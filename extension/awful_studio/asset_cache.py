"""Opt-in asset cache. No work is performed at import, enable or Blender startup."""
import hashlib
import json
import os
from pathlib import Path
import urllib.request

MAX_BYTES = 128 * 1024 * 1024
LICENSE_ID = 'CC0-1.0'
LICENSE_URL = 'https://polyhaven.com/license'
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


def _is_radiance_hdr(path):
    with Path(path).open('rb') as stream:
        return stream.read(16).startswith((b'#?RADIANCE', b'#?RGBE'))


def read_valid(path, expected_url=None):
    path = Path(path)
    try:
        meta = json.loads(path.with_suffix(path.suffix + '.json').read_text(encoding='utf-8'))
        size = path.stat().st_size
        return (
            meta['status'] == 'ready'
            and isinstance(meta['source_url'], str)
            and bool(meta['source_url'])
            and (expected_url is None or meta['source_url'] == expected_url)
            and meta['license'] == LICENSE_ID
            and meta['license_url'] == LICENSE_URL
            and 0 < size <= MAX_BYTES
            and meta['bytes'] == size
            and _is_radiance_hdr(path)
            and digest(path) == meta['sha256']
        )
    except (OSError, TypeError, ValueError, KeyError):
        return False


def last_error():
    return _LAST_ERROR or 'Asset unavailable; procedural fallback remains active'


def _write_metadata(path, metadata):
    try:
        path.write_text(json.dumps(metadata, indent=2), encoding='utf-8')
        return True
    except OSError:
        return False


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
    cache_root = root().resolve()
    path = Path(path)
    if path.is_symlink() or not path.resolve().is_relative_to(cache_root):
        raise ValueError('Asset destination must be inside the AWFUL cache')
    cached_before = read_valid(path, expected_url=url)
    if not force and cached_before:
        return True
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + '.part')
    sidecar = path.with_suffix(path.suffix + '.json')
    sidecar_temp = sidecar.with_suffix(sidecar.suffix + '.part')
    if temp.is_symlink() or sidecar.is_symlink() or sidecar_temp.is_symlink():
        raise ValueError('Symlink cache files are not writable')
    previous_sidecar = None
    if cached_before:
        try:
            previous_sidecar = sidecar.read_bytes()
        except OSError:
            cached_before = False
    metadata = {
        'source_url': url,
        'license': LICENSE_ID,
        'license_url': LICENSE_URL,
        'status': 'downloading',
    }
    sidecar_promoted = False
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
        if not _is_radiance_hdr(temp):
            raise ValueError('Downloaded asset is not a Radiance HDR image')
        metadata.update(status='ready', sha256=digest(temp), bytes=total)
        if not _write_metadata(sidecar_temp, metadata):
            raise OSError('Unable to write asset provenance metadata')
        os.replace(sidecar_temp, sidecar)
        sidecar_promoted = True
        os.replace(temp, path)
        _LAST_ERROR = ''
        return True
    except (OSError, ValueError) as exc:
        _LAST_ERROR = str(exc)
        temp.unlink(missing_ok=True)
        sidecar_temp.unlink(missing_ok=True)
        if sidecar_promoted:
            if previous_sidecar is not None:
                try:
                    sidecar.write_bytes(previous_sidecar)
                except OSError:
                    pass
            else:
                sidecar.unlink(missing_ok=True)
        if not cached_before:
            metadata.update(status='error', error=_LAST_ERROR)
            _write_metadata(sidecar, metadata)
        return False


def clear():
    # Only known, valid provenance-bearing cache files; never recursively delete a user directory.
    from .core.legacy import ASSET_URLS
    removed = 0
    for filename, url in ASSET_URLS.values():
        path = root() / 'hdri' / filename
        sidecar = path.with_suffix(path.suffix + '.json')
        if path.is_symlink() or sidecar.is_symlink() or not path.resolve().is_relative_to(root().resolve()):
            continue
        if not read_valid(path, expected_url=url):
            continue
        try:
            path.unlink()
            sidecar.unlink()
            removed += 1
        except OSError:
            continue
    return removed
