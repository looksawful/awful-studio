import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
EXT = ROOT / 'extension' / 'awful_studio'
INVENTORY = EXT / 'assets' / 'provenance.json'
HISTORICAL = ROOT / 'historical' / '0.0.15' / 'awful_studio_v4_2_gpu_perf.py'
ASSET_URL_RE = re.compile(r'https://[^\"\s]+(?:\.hdr|\.zip)')


class AssetProvenanceContractTests(unittest.TestCase):
    def load_inventory(self):
        return json.loads(INVENTORY.read_text(encoding='utf-8'))

    def test_inventory_exists_and_has_required_fields(self):
        data = self.load_inventory()
        self.assertEqual(data['schema_version'], 1)
        self.assertTrue(data['assets'])
        required = {
            'provider', 'asset_id', 'title', 'source_page', 'download_url',
            'filename', 'license', 'license_url', 'distribution', 'active',
        }
        for key, record in data['assets'].items():
            self.assertTrue(required.issubset(record), (key, required - set(record)))
            self.assertEqual(record['license'], 'CC0-1.0')
            self.assertTrue(record['source_page'].startswith('https://'))
            self.assertTrue(record['license_url'].startswith('https://'))

    def test_active_downloads_are_exactly_the_five_reviewed_hdris(self):
        data = self.load_inventory()
        active = {record['download_url'] for record in data['assets'].values() if record['active']}
        self.assertEqual(len(active), 5)
        self.assertTrue(all(url.endswith('.hdr') for url in active))
        source = (EXT / 'core' / 'legacy.py').read_text(encoding='utf-8')
        for url in active:
            self.assertIn(url, source)

    def test_all_extension_third_party_asset_urls_are_recorded(self):
        data = self.load_inventory()
        recorded = {record['download_url'] for record in data['assets'].values()}
        urls = set()
        for path in EXT.rglob('*.py'):
            urls.update(ASSET_URL_RE.findall(path.read_text(encoding='utf-8')))
        self.assertTrue(urls)
        self.assertTrue(urls.issubset(recorded), urls - recorded)

    def test_historical_third_party_asset_urls_are_in_inventory(self):
        data = self.load_inventory()
        recorded = {record['download_url'] for record in data['assets'].values()}
        source = HISTORICAL.read_text(encoding='utf-8')
        historical_urls = set(ASSET_URL_RE.findall(source))
        self.assertTrue(historical_urls)
        self.assertTrue(historical_urls.issubset(recorded), historical_urls - recorded)

    def test_only_reviewed_floor_maps_are_bundled_with_attribution(self):
        binary_suffixes = {'.hdr', '.exr', '.png', '.jpg', '.jpeg', '.zip', '.tif', '.tiff'}
        bundled = {
            str(path.relative_to(EXT)).replace('\\', '/') for path in EXT.rglob('*')
            if path.is_file() and path.suffix.lower() in binary_suffixes
        }
        expected = {
            'assets/painted_plaster017/painted_plaster017_color.png',
            'assets/painted_plaster017/painted_plaster017_roughness.png',
            'assets/painted_plaster017/painted_plaster017_normalgl.png',
            'assets/painted_plaster017/painted_plaster017_displacement.png',
        }
        self.assertEqual(bundled, expected)
        record = self.load_inventory()['assets']['painted_plaster017']
        self.assertEqual(record['provider'], 'ambientCG')
        self.assertEqual(record['distribution'], 'bundled')
        self.assertEqual(set(record['bundled_files']), expected)
        self.assertTrue((EXT / 'assets' / 'ATTRIBUTION.md').is_file())

    def test_cache_uses_provenance_for_authorization_and_metadata(self):
        source = (EXT / 'asset_cache.py').read_text(encoding='utf-8')
        self.assertIn('asset_provenance', source)
        self.assertIn("record['license']", source)
        self.assertIn("record['asset_id']", source)
        self.assertIn("record['source_page']", source)
        self.assertNotIn("metadata = {'source_url': url, 'license': 'CC0-1.0'", source)
        self.assertNotIn('shutil.rmtree', source)


if __name__ == '__main__':
    unittest.main()
