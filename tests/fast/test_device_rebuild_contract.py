import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / 'tools' / 'build_device_deliveries.py'
KHRONOS_EVIDENCE = ROOT / 'assets/device_mockups/device_delivery_khronos_validation.json'


def load_tool():
    spec = importlib.util.spec_from_file_location('awful_device_rebuild', TOOL)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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

    def test_retained_khronos_evidence_matches_current_glbs(self):
        self.assertTrue(KHRONOS_EVIDENCE.is_file(), 'missing retained Khronos evidence')
        evidence = json.loads(KHRONOS_EVIDENCE.read_text(encoding='utf-8'))
        self.assertTrue(evidence['pass'])
        self.assertEqual(len(evidence['assets']), 4)
        for variants in evidence['assets'].values():
            self.assertEqual(set(variants), {'compat', 'meshopt'})
            for summary in variants.values():
                self.assertTrue(summary['pass'])
                self.assertEqual(summary['errors'], 0)
                self.assertEqual(summary['warnings'], 0)
                path = ROOT / summary['file']
                digest = hashlib.sha256(path.read_bytes()).hexdigest()
                self.assertEqual(summary['sha256'], digest)

    def test_khronos_gate_rejects_errors_or_warnings(self):
        tool = load_tool()
        clean = {
            'validatorVersion': '2.0.0-dev.3.10',
            'issues': {'numErrors': 0, 'numWarnings': 0, 'numInfos': 3, 'numHints': 0},
        }
        self.assertEqual(tool.summarize_khronos_report(clean)['pass'], True)

        with self.assertRaisesRegex(RuntimeError, 'Khronos validation failed'):
            tool.summarize_khronos_report({
                'validatorVersion': '2.0.0-dev.3.10',
                'issues': {'numErrors': 0, 'numWarnings': 1, 'numInfos': 0, 'numHints': 0},
            })


if __name__ == '__main__':
    unittest.main()
