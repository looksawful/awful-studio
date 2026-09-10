import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
LIFECYCLE = ROOT / 'extension' / 'awful_studio' / '__init__.py'


class LegacyHdriProvenanceContract(unittest.TestCase):
    def test_environment_decode_is_interposed_by_validated_curated_cache_gate(self):
        source = LIFECYCLE.read_text(encoding='utf-8')
        self.assertIn('def _load_image_with_hdri_provenance(', source)
        self.assertIn('for key, (_filename, url) in legacy.ASSET_URLS.items():', source)
        self.assertIn('asset_cache.read_valid(path, expected_url=url)', source)
        self.assertIn('legacy.load_image = _load_image_with_hdri_provenance', source)
        self.assertIn('return _legacy_load_image_raw(path, non_color)', source)


if __name__ == '__main__':
    unittest.main()
