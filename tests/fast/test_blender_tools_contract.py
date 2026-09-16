import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
INTEGRATIONS = ROOT / "extension" / "awful_studio" / "integrations"
MANIFEST = INTEGRATIONS / "blender_tools.json"
CONTENT_POLICY = INTEGRATIONS / "blender_content_policy.json"


class BlenderToolsContract(unittest.TestCase):
    def test_manifest_is_safe_and_declarative(self):
        data = json.loads(MANIFEST.read_text(encoding="utf-8-sig"))
        self.assertEqual(data["policy"], "declarative-only-no-implicit-install-or-enable")
        ids = [tool["id"] for tool in data["tools"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(
            {
                "node_wrangler",
                "looptools",
                "bool_tool",
                "measureit",
                "images_as_planes",
                "material_utils",
                "collection_manager",
                "camera_rigs",
                "tri_lighting",
                "blenderkit",
                "makehuman",
            }.issubset(ids)
        )
        tools = {tool["id"]: tool for tool in data["tools"]}
        self.assertEqual(tools["node_wrangler"]["automation"], "extension-repository")
        self.assertEqual(tools["blenderkit"]["automation"], "manual")
        self.assertEqual(tools["makehuman"]["automation"], "manual")
        for tool in data["tools"]:
            self.assertIn(tool["automation"], {"builtin", "extension-repository", "manual"})
            self.assertIn(tool["tier"], {"core", "useful", "optional"})
            self.assertTrue(tool["purpose"])
        serialized = json.dumps(data).lower()
        for forbidden in ("password", "api_key", "apikey", "access_token", "secret_key"):
            self.assertNotIn(forbidden, serialized)

    def test_preset_and_template_policy_cannot_overwrite_user_profile(self):
        data = json.loads(CONTENT_POLICY.read_text(encoding="utf-8-sig"))
        self.assertEqual(data["schema"], 1)
        self.assertEqual(data["policy"], "awful-owned-declarative-content-no-user-profile-overwrite")
        self.assertEqual(data["presets"]["storage"], "extension-owned")
        self.assertEqual(data["presets"]["user_space_export"], "explicit-only")
        self.assertFalse(data["presets"]["overwrite_existing"])
        self.assertFalse(data["presets"]["binary_payloads"])
        self.assertEqual(data["templates"]["storage"], "declarative-spec")
        self.assertFalse(data["templates"]["startup_blend_mutation"])
        self.assertFalse(data["templates"]["user_template_mutation"])
        self.assertFalse(data["templates"]["binary_blend_in_repo"])

    def test_runtime_module_has_no_bpy_or_network_side_effects(self):
        source = (ROOT / "extension" / "awful_studio" / "blender_tools.py").read_text(encoding="utf-8-sig")
        self.assertNotIn("import bpy", source)
        self.assertNotIn("urllib", source)
        self.assertNotIn("requests", source)
        self.assertNotIn("subprocess", source)


if __name__ == "__main__":
    unittest.main()
