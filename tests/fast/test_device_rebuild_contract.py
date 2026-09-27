import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / 'tools' / 'build_device_deliveries.py'


class DeviceRebuildContractTests(unittest.TestCase):
    def test_plan_covers_all_canonical_device_deliveries(self):
        result = subprocess.run(
            [sys.executable, str(TOOL), '--plan'],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        plan = json.loads(result.stdout)
        self.assertEqual(
            [item['asset_id'] for item in plan],
            [
                'iphone_17',
                'ipad_pro_11_m5',
                'ipad_pro_13_m5',
                'macbook_pro_14_m5',
            ],
        )
        self.assertTrue(all(item['generator_version'] for item in plan))
        self.assertTrue(all(item['manifest'].endswith('.asset.json') for item in plan))


if __name__ == '__main__':
    unittest.main()
