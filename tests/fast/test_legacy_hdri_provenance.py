import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
LEGACY = ROOT / 'extension' / 'awful_studio' / 'core' / 'legacy.py'


class LegacyHdriProvenanceContract(unittest.TestCase):
    def test_environment_decode_requires_validated_curated_cache_entry(self):
        source = LEGACY.read_text(encoding='utf-8')
        self.assertIn('def load_hdri_asset(', source)
        self.assertIn('asset_cache.read_valid(path, expected_url=url)', source)
        self.assertNotIn('load_image(hdri_asset_path(HDRI_PRESETS[preset_id]["asset"]), False)', source)
        self.assertNotIn('load_image(hdri_asset_path(HDRI_PRESETS[preset]["asset"]), False)', source)


if __name__ == '__main__':
    unittest.main()
