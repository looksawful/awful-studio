import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
EXT = ROOT / 'extension' / 'awful_studio'
INVENTORY = EXT / 'assets' / 'provenance.json'


class MaterialCatalogContractTests(unittest.TestCase):
    def load(self):
        return json.loads(INVENTORY.read_text(encoding='utf-8'))['assets']

    def test_curated_materials_are_cc0_poly_haven_api_records(self):
        materials = {k:v for k,v in self.load().items() if v.get('asset_kind') == 'pbr-material'}
        self.assertEqual(set(materials), {
            'material_blue_metal_plate', 'material_brushed_concrete', 'material_american_walnut'
        })
        for key, record in materials.items():
            self.assertEqual(record['provider'], 'Poly Haven', key)
            self.assertEqual(record['license'], 'CC0-1.0', key)
            self.assertEqual(record['distribution'], 'api-catalog', key)
            self.assertFalse(record['active'], key)
            self.assertTrue(record['api_attribution_required'], key)
            self.assertEqual(record['preferred_resolution'], '2k', key)
            self.assertTrue({'Diffuse','nor_gl','Rough'}.issubset(record['preferred_maps']), key)
            self.assertEqual(record['download_url'], f"https://api.polyhaven.com/files/{record['asset_id']}")

    def test_api_catalog_records_cannot_be_authorized_by_direct_cache(self):
        source = (EXT / 'asset_cache.py').read_text(encoding='utf-8')
        self.assertIn("record['distribution'] != 'remote-only'", source)

    def test_material_catalog_is_pure_and_has_no_network_client(self):
        source = (EXT / 'material_catalog.py').read_text(encoding='utf-8')
        self.assertNotIn('urllib', source)
        self.assertNotIn('requests', source)
        self.assertIn('preferred_maps', source)


if __name__ == '__main__':
    unittest.main()
