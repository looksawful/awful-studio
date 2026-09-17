import tempfile
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

try:
    import device_review
except ImportError:
    device_review = None


class DeviceReviewTests(unittest.TestCase):
    def test_classifies_supported_candidates_and_ignores_blend_backups(self):
        self.assertIsNotNone(device_review)
        self.assertEqual(device_review.candidate_format(Path("iphone_v20.blend")), "BLEND")
        self.assertEqual(device_review.candidate_format(Path("iphone_v20.glb")), "GLB")
        self.assertIsNone(device_review.candidate_format(Path("iphone_v20.blend1")))
        self.assertIsNone(device_review.candidate_format(Path("logo.png")))

    def test_infers_device_and_version_from_filename(self):
        self.assertIsNotNone(device_review)
        meta = device_review.infer_identity(Path("ipad_pro_11_m5_low_v6.blend"))
        self.assertEqual(meta["device"], "ipad_pro_11")
        self.assertEqual(meta["version"], "v6")
        meta = device_review.infer_identity(Path("iphone_17_v20_web_meshopt.glb"))
        self.assertEqual(meta["device"], "iphone_17")
        self.assertEqual(meta["version"], "v20")
    def test_inventory_deduplicates_bytes_but_keeps_all_provenance(self):
        self.assertIsNotNone(device_review)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            a = root / "one" / "iphone_17_low_v20.blend"
            b = root / "two" / "iphone_17_low_v20.blend"
            c = root / "two" / "iphone_17_low_v21.blend"
            for path in (a, b, c):
                path.parent.mkdir(parents=True, exist_ok=True)
            a.write_bytes(b"same")
            b.write_bytes(b"same")
            c.write_bytes(b"different")

            items = device_review.inventory([root])
            self.assertEqual(len(items), 2)
            v20 = next(item for item in items if item["version"] == "v20")
            self.assertEqual(len(v20["provenance"]), 2)
            self.assertEqual(v20["format"], "BLEND")

    def test_review_contract_has_required_views_and_modes(self):
        self.assertIsNotNone(device_review)
        self.assertEqual(
            device_review.VIEWS,
            ("front", "back", "left", "right", "top", "bottom", "front_3q", "back_3q"),
        )
        for mode in ("material", "clay", "wire", "normals", "silhouette"):
            self.assertIn(mode, device_review.MODES)


if __name__ == "__main__":
    unittest.main()