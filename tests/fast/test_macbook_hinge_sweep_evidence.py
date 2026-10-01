import json
from pathlib import Path
from unittest import TestCase


class MacBookHingeSweepEvidenceTests(TestCase):
    def test_clearance_evidence_covers_every_integer_degree_and_lid(self):
        root = Path(__file__).resolve().parents[2]
        report = json.loads((root / 'assets/device_mockups/macbook_pro_14/evidence/hinge_clearance_delivery.json').read_text())
        self.assertTrue(report['passed'])
        self.assertEqual([state['angle_deg'] for state in report['states']], list(range(103)))
        for state in report['states']:
            self.assertTrue(state['pass'])
            self.assertIn('lid_base', state['intersection_mm3'])
