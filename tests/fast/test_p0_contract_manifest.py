import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
AUDIT = ROOT / 'docs' / 'reviews' / '2026-09-10-editorial-deep-audit.md'


class P0ContractInventoryTests(unittest.TestCase):
    def test_current_milestone_is_explicitly_audited(self):
        text = AUDIT.read_text(encoding='utf-8')
        for required in (
            'Flash regime',
            'Metric cyclorama distance',
            'Playback Once/Loop/Ping-Pong',
            'Natural light v2',
            'Visible floor/door/visibility',
            'Complete lighting preset reachability',
            'Base camera target/safe framing',
            'Performance evidence',
            'Release/native update',
        ):
            self.assertIn(required, text)

    def test_render_regression_is_not_a_current_release_gate(self):
        text = AUDIT.read_text(encoding='utf-8')
        self.assertIn('Visual regression | explicitly deferred', text)


if __name__ == '__main__':
    unittest.main()
