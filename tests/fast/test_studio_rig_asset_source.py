import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
ASSET = ROOT / "assets" / "studio_equipment" / "studio_rig_v01"

class StudioRigAssetSourceTests(unittest.TestCase):
    def test_asset_package_has_required_source_contract(self):
        self.assertTrue((ASSET / "generate.py").is_file())
        self.assertTrue((ASSET / "validate.py").is_file())
        spec = json.loads((ASSET / "spec.json").read_text(encoding="utf-8"))
        self.assertEqual(spec["blender_target"], "5.2.1")
        self.assertEqual(spec["d1_500_air"]["envelope_mm"], [300, 130, 170])
        self.assertEqual(spec["magnum_100624"]["diameter_mm"], 345)
        self.assertEqual(spec["magnum_100624"]["depth_mm"], 265)
        self.assertEqual(spec["support"]["identity_class"], "REPRESENTATIVE_STANDARD")
        self.assertIn("MOUNT_FIXTURE", spec["semantic_mounts"])
        self.assertIn("MOUNT_MODIFIER", spec["semantic_mounts"])

if __name__ == "__main__":
    unittest.main()
