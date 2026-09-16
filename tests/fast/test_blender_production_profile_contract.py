import ast
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SETUP = ROOT / "tools" / "blender" / "configure_production_profile.py"
OVERRIDE = ROOT / "tools" / "blender" / "awful_studio_keymap_overrides.py"


def assigned_tuple_strings(source: str, name: str) -> set[str]:
    tree = ast.parse(source)
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
            return {elt.value for elt in node.value.elts if isinstance(elt, ast.Constant) and isinstance(elt.value, str)}
    raise AssertionError(f"missing assignment: {name}")


class BlenderProductionProfileContractTests(unittest.TestCase):
    def test_setup_declares_required_runtime_and_asset_contract(self):
        source = SETUP.read_text(encoding="utf-8-sig")
        required = assigned_tuple_strings(source, "REQUIRED_ADDONS")
        for module in (
            "cycles", "io_curve_svg", "io_scene_fbx", "io_scene_gltf2", "blender_mcp",
            "bl_ext.blender_org.CAD_Sketcher", "bl_ext.blender_org.measureit",
            "bl_ext.blender_org.nd", "bl_ext.blender_org.bool_tool",
            "bl_ext.blender_org.looptools", "bl_ext.blender_org.magic_uv",
        ):
            self.assertIn(module, required)
        for token in (r'A:\assets\3D ASSET', r'A:\Textures', r'A:\assets\SUBSTANCE'):
            self.assertIn(token, source)

    def test_setup_does_not_change_adobe_or_substance_addon_preferences(self):
        source = SETUP.read_text(encoding="utf-8-sig")
        self.assertNotIn("Substance3DInBlender", source)
        self.assertNotIn("sre_path", source)
        self.assertNotIn("path_library", source)

    def test_override_only_resolves_known_bool_tool_collisions(self):
        source = OVERRIDE.read_text(encoding="utf-8-sig")
        for operator in (
            "object.boolean_brush_difference",
            "object.boolean_brush_union",
            "object.boolean_brush_intersect",
            "object.boolean_brush_slice",
            "VIEW3D_MT_boolean_popup",
        ):
            self.assertIn(operator, source)
        self.assertNotIn("substance.", source.lower())


if __name__ == "__main__":
    unittest.main()
