import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COMMON = ROOT / "assets" / "device_mockups" / "common"
CONTRACT_PATH = COMMON / "material_contract.json"
PIPELINE_PATH = COMMON / "material_pipeline.py"


def load_pipeline():
    spec = importlib.util.spec_from_file_location("awful_device_material_pipeline", PIPELINE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class DeviceMaterialContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        cls.pipeline = load_pipeline()

    def test_contract_has_nine_canonical_material_classes(self):
        expected = {"ALUMINUM", "GLASS_DISPLAY", "GLASS_BACK", "OPTICAL_GLASS", "POLYMER_BLACK", "RUBBER", "SCREEN", "DECAL", "GAP"}
        self.assertEqual(set(self.contract["materials"]), expected)
        self.assertEqual({spec["canonical_name"] for spec in self.contract["materials"].values()}, {f"MAT_{name}" for name in expected})

    def test_delivery_policy_is_explicit_and_bounded(self):
        self.assertEqual(self.contract["delivery"]["quality_presets"], [1024, 2048, 4096])
        self.assertEqual(self.contract["delivery"]["packed_orm"], {"r": "ao", "g": "roughness", "b": "metallic"})
        self.assertIn("LOW", self.contract["delivery"]["uv_gate"])

    def test_current_device_material_names_map_to_canonical_ids(self):
        cases = {
            "MAT_ANODIZED_ALUMINUM": "ALUMINUM",
            "MAT_IPAD_ALUMINUM": "ALUMINUM",
            "MAT_SPACE_BLACK_ALUMINUM": "ALUMINUM",
            "MAT_DISPLAY_GLASS": "GLASS_DISPLAY",
            "MAT_BACK_GLASS": "GLASS_BACK",
            "MAT_LENS_GLASS": "OPTICAL_GLASS",
            "MAT_OPTICAL_GLASS": "OPTICAL_GLASS",
            "MAT_KEYCAP": "POLYMER_BLACK",
            "MAT_PORT_DARK": "POLYMER_BLACK",
            "MAT_SCREEN_CONTENT": "SCREEN",
            "MAT_APPLE_LOGO_DECAL": "DECAL",
            "MAT_ASSEMBLY_GAP": "GAP",
        }
        for name, expected in cases.items():
            with self.subTest(name=name):
                self.assertEqual(self.pipeline.classify_material_name(name), expected)

    def test_delivery_roles_are_separate_from_material_classification(self):
        self.assertEqual(self.pipeline.classify_object_role("SCREEN_CONTENT"), ("image_driven", "keep_geometry"))
        self.assertEqual(self.pipeline.classify_object_role("TOP_L_SPEAKER_01"), ("bake_candidate", "bake_if_subpixel"))
        self.assertEqual(self.pipeline.classify_object_role("CAM_PREVIEW"), ("development_helper", "exclude_delivery"))
        self.assertEqual(self.pipeline.classify_object_role("DEVICE_BODY"), ("geometry_keep", "keep_geometry"))


if __name__ == "__main__":
    unittest.main()
