import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest import mock


REPO = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO / 'extension' / 'awful_studio' / 'asset_cache.py'
ASSET_URL = 'https://example.invalid/curated.hdr'
FILENAME = 'curated.hdr'


class _Prefs:
    allow_network_assets = True
    asset_cache_path = ''


class _InterruptedResponse:
    url = ASSET_URL

    def __init__(self):
        self.calls = 0

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self, size):
        self.calls += 1
        if self.calls == 1:
            return b'#?RADIANCE\npartial'
        raise OSError('connection interrupted')


class AssetCacheTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cache_base = Path(self.tmp.name)
        _Prefs.asset_cache_path = str(self.cache_base)

        bpy = types.ModuleType('bpy')
        bpy.context = types.SimpleNamespace(
            preferences=types.SimpleNamespace(
                addons={'awful_studio': types.SimpleNamespace(preferences=_Prefs())}
            )
        )
        bpy.app = types.SimpleNamespace(online_access=True)
        bpy.path = types.SimpleNamespace(abspath=lambda value: value)
        bpy.utils = types.SimpleNamespace(user_resource=lambda kind: str(self.cache_base))
        sys.modules['bpy'] = bpy

        package = types.ModuleType('awful_studio')
        package.__path__ = []
        core = types.ModuleType('awful_studio.core')
        core.__path__ = []
        legacy = types.ModuleType('awful_studio.core.legacy')
        legacy.ASSET_URLS = {'test': (FILENAME, ASSET_URL)}
        sys.modules['awful_studio'] = package
        sys.modules['awful_studio.core'] = core
        sys.modules['awful_studio.core.legacy'] = legacy

        spec = importlib.util.spec_from_file_location('awful_studio.asset_cache', MODULE_PATH)
        self.asset_cache = importlib.util.module_from_spec(spec)
        sys.modules['awful_studio.asset_cache'] = self.asset_cache
        spec.loader.exec_module(self.asset_cache)
        self.path = self.asset_cache.root() / 'hdri' / FILENAME
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        for name in ('awful_studio.asset_cache', 'awful_studio.core.legacy', 'awful_studio.core', 'awful_studio', 'bpy'):
            sys.modules.pop(name, None)
        self.tmp.cleanup()

    def _write_entry(self, payload, *, source_url=ASSET_URL, status='ready', sha256=None, byte_count=None):
        self.path.write_bytes(payload)
        meta = {
            'source_url': source_url,
            'license': 'CC0-1.0',
            'license_url': 'https://polyhaven.com/license',
            'status': status,
            'sha256': sha256 or hashlib.sha256(payload).hexdigest(),
            'bytes': len(payload) if byte_count is None else byte_count,
        }
        self.path.with_suffix(self.path.suffix + '.json').write_text(json.dumps(meta), encoding='utf-8')

    def test_valid_cached_hdr_requires_expected_source(self):
        self._write_entry(b'#?RADIANCE\nvalid hdr payload', source_url='https://example.invalid/wrong.hdr')
        self.assertFalse(self.asset_cache.read_valid(self.path, expected_url=ASSET_URL))

    def test_valid_cached_hdr_rejects_non_hdr_even_with_matching_digest(self):
        self._write_entry(b'not an hdr file but digest matches')
        self.assertFalse(self.asset_cache.read_valid(self.path, expected_url=ASSET_URL))

    def test_valid_cached_hdr_checks_recorded_byte_count(self):
        payload = b'#?RADIANCE\nvalid hdr payload'
        self._write_entry(payload, byte_count=len(payload) + 1)
        self.assertFalse(self.asset_cache.read_valid(self.path, expected_url=ASSET_URL))

    def test_fetch_does_not_reuse_forged_cached_payload(self):
        self._write_entry(b'not hdr', source_url=ASSET_URL)
        with mock.patch.object(self.asset_cache.urllib.request, 'urlopen', side_effect=OSError('offline')) as urlopen:
            self.assertFalse(self.asset_cache.fetch(ASSET_URL, self.path))
        urlopen.assert_called_once()

    def test_valid_cache_reuse_makes_zero_network_attempts(self):
        self._write_entry(b'#?RADIANCE\nvalid hdr payload')
        with mock.patch.object(self.asset_cache.urllib.request, 'urlopen', side_effect=AssertionError('network attempted')) as urlopen:
            self.assertTrue(self.asset_cache.fetch(ASSET_URL, self.path))
        urlopen.assert_not_called()

    def test_failed_forced_refresh_preserves_previous_valid_cache(self):
        payload = b'#?RADIANCE\nvalid hdr payload'
        self._write_entry(payload)
        with mock.patch.object(self.asset_cache.urllib.request, 'urlopen', side_effect=OSError('offline')):
            self.assertFalse(self.asset_cache.fetch(ASSET_URL, self.path, force=True))
        self.assertEqual(self.path.read_bytes(), payload)
        self.assertTrue(self.asset_cache.read_valid(self.path, expected_url=ASSET_URL))

    def test_clear_preserves_payload_when_sidecar_is_not_valid_provenance(self):
        payload = b'#?RADIANCE\nuser payload'
        self._write_entry(payload, sha256='0' * 64)
        self.assertEqual(self.asset_cache.clear(), 0)
        self.assertTrue(self.path.exists())

    def test_interrupted_download_cleans_partial_if_error_sidecar_write_fails(self):
        temp = self.path.with_suffix(self.path.suffix + '.part')
        with mock.patch.object(self.asset_cache.urllib.request, 'urlopen', return_value=_InterruptedResponse()), \
             mock.patch.object(Path, 'write_text', side_effect=OSError('sidecar unwritable')):
            self.assertFalse(self.asset_cache.fetch(ASSET_URL, self.path))
        self.assertFalse(temp.exists())
        self.assertFalse(self.path.exists())

    def test_network_gate_blocks_before_urlopen(self):
        sys.modules['bpy'].app.online_access = False
        with mock.patch.object(self.asset_cache.urllib.request, 'urlopen', side_effect=AssertionError('network attempted')) as urlopen:
            with self.assertRaises(RuntimeError):
                self.asset_cache.fetch(ASSET_URL, self.path)
        urlopen.assert_not_called()

    def test_destination_escape_is_rejected_before_network(self):
        escaped = self.cache_base.parent / 'escape.hdr'
        with mock.patch.object(self.asset_cache.urllib.request, 'urlopen', side_effect=AssertionError('network attempted')) as urlopen:
            with self.assertRaises(ValueError):
                self.asset_cache.fetch(ASSET_URL, escaped)
        urlopen.assert_not_called()


if __name__ == '__main__':
    unittest.main()
