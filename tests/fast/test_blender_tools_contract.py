import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "extension" / "awful_studio" / "integrations" / "blender_tools.json"

class BlenderToolsContract(unittest.TestCase):
    def test_manifest_is_safe_and_declarative(self):
        data = json.loads(MANIFEST.read_text(encoding="utf-8-sig"))
        self.assertEqual(data["policy"], "declarative-only-no-implicit-install-or-enable")
        ids = [tool["id"] for tool in data["tools"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue({"node_wrangler", "looptools", "bool_tool", "measureit", "blenderkit", "makehuman"}.issubset(ids))
        for tool in data["tools"]:
            self.assertIn(tool["automation"], {"builtin", "extension-repository", "manual"})
            self.assertNotIn("token", tool)
            self.assertNotIn("password", tool)

    def test_runtime_module_has_no_bpy_or_network_side_effects(self):
        source = (ROOT / "extension" / "awful_studio" / "blender_tools.py").read_text(encoding="utf-8-sig")
        self.assertNotIn("import bpy", source)
        self.assertNotIn("urllib", source)
        self.assertNotIn("requests", source)
        self.assertNotIn("subprocess", source)

if __name__ == "__main__": unittest.main()
