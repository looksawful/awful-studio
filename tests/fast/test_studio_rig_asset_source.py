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

    def test_d1_manual_features_are_explicit(self):
        spec = json.loads((ASSET / "spec.json").read_text(encoding="utf-8"))
        features = set(spec["d1_500_air"]["verified_features"])
        required = {"frosted_glass_plate", "flash_tube", "modeling_lamp",
                    "sync_connector", "ac_connector", "fuse_holder",
                    "umbrella_tube", "zoom_scale", "stand_adapter",
                    "ergonomic_handle", "side_vent_slots", "rear_control_panel"}
        self.assertTrue(required <= features)

    def test_cstand_reference_geometry_is_explicit(self):
        spec = json.loads((ASSET / "spec.json").read_text(encoding="utf-8"))
        support = spec["support"]
        self.assertEqual(support["geometry_reference"], "Avenger A2025F")
        self.assertEqual(support["reference_tube_diameters_mm"], [35, 30, 25])
        self.assertEqual(support["reference_leg_diameter_mm"], 25)
        self.assertEqual(support["reference_max_footprint_mm"], 950)
        self.assertEqual(support["rig_mount_height_mm"], 1750)
