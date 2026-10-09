import ast
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
BUILD = ROOT / "tools" / "build_iphone17_v30.py"
PACKAGER = ROOT / "tools" / "package_device_asset.py"


def source_files():
    tree = ast.parse(BUILD.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "SOURCE_FILES"
            for target in node.targets
        ):
            return set(ast.literal_eval(node.value))
    raise AssertionError("SOURCE_FILES not found")


class IPhoneProductionBundleContractTests(unittest.TestCase):
    def test_consumed_texture_bake_and_build_inputs_are_fingerprinted(self):
        required = {
            "assets/device_mockups/iphone_17/reference/front_camera_detail_mask.png",
            "assets/device_mockups/iphone_17/reference/control_bake_v30/provenance.json",
            "assets/device_mockups/iphone_17/reference/control_bake_v30/action_button_normal.png",
            "assets/device_mockups/iphone_17/reference/control_bake_v30/camera_control_normal.png",
            "assets/device_mockups/iphone_17/reference/control_bake_v30/side_button_normal.png",
            "assets/device_mockups/iphone_17/reference/control_bake_v30/vol_down_normal.png",
            "assets/device_mockups/iphone_17/reference/control_bake_v30/vol_up_normal.png",
            "assets/device_mockups/iphone_17/optimize_runtime_v30.py",
            "tools/build_iphone17_v30.py",
            "tools/package_device_asset.py",
            "tools/device_delivery_contract.py",
        }
        self.assertEqual(required - source_files(), set())

    def test_iphone_build_requests_runtime_visible_plugin_packaging(self):
        text = BUILD.read_text(encoding="utf-8")
        self.assertIn("'--runtime-visible-only'", text)

    def test_packager_has_opt_in_hidden_mesh_exclusion(self):
        text = PACKAGER.read_text(encoding="utf-8")
        self.assertIn("runtime_visible_only", text)
        self.assertIn("obj.type == 'MESH' and obj.hide_render", text)


if __name__ == "__main__":
    unittest.main()
