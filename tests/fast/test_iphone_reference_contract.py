import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / 'assets/device_mockups/iphone_17/reference/iphone_17_dimensional_ledger.json'
LOADER = ROOT / 'extension/awful_studio/device_asset_loader.py'

class IPhoneReferenceContractTests(unittest.TestCase):
    def test_official_body_dimensions_match_current_loader(self):
        ledger = json.loads(LEDGER.read_text(encoding='utf-8'))
        refs = {item['element']: item['reference'] for item in ledger['dimensions']}
        spec = importlib.util.spec_from_file_location('device_asset_loader', LOADER)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        dims = module.DEVICE_ASSET_SPECS['DEVICE_IPHONE_17']['dimensions_m']
        actual = [round(dims[0] * 1000, 2), round(dims[2] * 1000, 2), round(dims[1] * 1000, 2)]
        expected = [refs['body.width'], refs['body.height'], refs['body.depth']]
        self.assertEqual(actual, expected)

if __name__ == '__main__':
    unittest.main()
