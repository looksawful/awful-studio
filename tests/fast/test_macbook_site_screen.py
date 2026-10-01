import hashlib
import json
import struct
import sys
from pathlib import Path
from unittest import TestCase

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))


class MacBookSiteScreenTests(TestCase):
    def test_offline_screen_is_native_resolution_own_site_capture(self):
        import build_macbook_v1_web as build
        path = 'assets/device_mockups/macbook_pro_14/reference/looksawful_home_3024x1964.png'
        self.assertIn(path, build.SOURCE_FILES)
        raw = (ROOT / path).read_bytes()
        self.assertEqual(struct.unpack('>II', raw[16:24]), (3024, 1964))
        meta = json.loads((ROOT / path).with_suffix('.json').read_text())
        self.assertEqual(meta['url'], 'https://www.looksawful.ru/')
        self.assertEqual(meta['viewport_css'], [1512, 982])
        self.assertEqual(meta['sha256'], hashlib.sha256(raw).hexdigest())
