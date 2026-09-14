import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
RUNTIME = ROOT / "assets" / "studio_equipment" / "studio_rig_v01" / "runtime"


class StudioRigWebRuntimeContractTests(unittest.TestCase):
    def test_runtime_contract_is_explicit_and_web_ready(self):
        contract_path = RUNTIME / "runtime_contract.json"
        self.assertTrue(contract_path.is_file())
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
        self.assertEqual(contract["shipping_format"], "GLB")
        self.assertEqual(contract["mesh_compression"], "meshopt")
        self.assertEqual(contract["texture_container"], "KTX2")
        self.assertEqual(contract["source_units"], "meters")
        self.assertEqual(contract["source_up_axis"], "Z")
        self.assertEqual(contract["runtime_up_axis"], "Y")
        self.assertEqual(contract["lod_levels"], ["LOD0", "LOD1", "LOD2"])
        self.assertEqual(set(contract["collision_proxies"]), {
            "COL_SUPPORT", "COL_FIXTURE", "COL_MODIFIER", "COL_SANDBAG"
        })
        self.assertEqual(set(contract["stable_roots"]), {
            "ROOT_SUPPORT_CSTAND", "ROOT_FIX_PROFOTO_D1_500",
            "ROOT_MOD_PROFOTO_MAGNUM", "ROOT_ACC_SANDBAG"
        })

    def test_runtime_manifest_uses_stable_keys_not_filenames_as_api(self):
        manifest_path = RUNTIME / "asset_manifest.json"
        self.assertTrue(manifest_path.is_file())
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(set(manifest["assets"]), {
            "studio_support_cstand_01", "profoto_d1_500_air",
            "profoto_magnum_100624", "studio_sandbag_01"
        })
        for entry in manifest["assets"].values():
            self.assertIn("root", entry)
            self.assertIn("glb", entry)
            self.assertIn("interaction", entry)

    def test_blender_exporter_emits_clean_meshopt_glb_candidates(self):
        exporter = RUNTIME / "export_glb.py"
        self.assertTrue(exporter.is_file())
        source = exporter.read_text(encoding="utf-8")
        for token in (
            "export_format=\"GLB\"",
            "export_meshopt_compression_enable=meshopt",
            "meshopt=True",
            "meshopt=False",
            "export_yup=True",
            "export_apply=True",
            "export_extras=True",
            "export_cameras=False",
            "export_lights=False",
        ):
            self.assertIn(token, source)
        manifest = json.loads((RUNTIME / "asset_manifest.json").read_text(encoding="utf-8"))
        for entry in manifest["assets"].values():
            self.assertTrue((RUNTIME / entry["glb"]).is_file(), entry["glb"])

    def test_headless_exporter_never_waits_for_overwrite_confirmation(self):
        exporter = (RUNTIME / "export_glb.py").read_text(encoding="utf-8")
        self.assertIn("check_existing=False", exporter)

    def test_glb_runtime_validation_evidence_exists(self):
        validator = RUNTIME / "validate_glb.py"
        evidence = RUNTIME / "glb_validation.json"
        self.assertTrue(validator.is_file())
        self.assertTrue(evidence.is_file())
        data = json.loads(evidence.read_text(encoding="utf-8"))
        self.assertTrue(data["pass"])
        self.assertEqual(set(data["assets"]), {
            "studio_support_cstand_01", "profoto_d1_500_air",
            "profoto_magnum_100624", "studio_sandbag_01"
        })
        for item in data["assets"].values():
            self.assertTrue(item["meshopt"])
            self.assertEqual(item["cameras"], 0)
            self.assertFalse(item["lights"])
            self.assertEqual(item["reference_nodes"], [])

    def test_collision_assets_ship_separately_from_visual_glb(self):
        manifest = json.loads((RUNTIME / "asset_manifest.json").read_text(encoding="utf-8"))
        evidence = json.loads((RUNTIME / "glb_validation.json").read_text(encoding="utf-8"))
        self.assertIn("collision_assets", evidence)
        for key, entry in manifest["assets"].items():
            self.assertIn("collision_glb", entry)
            self.assertTrue((RUNTIME / entry["collision_glb"]).is_file())
            visual = evidence["assets"][key]
            collision = evidence["collision_assets"][key]
            self.assertEqual(visual.get("collision_nodes", []), [])
            self.assertLessEqual(collision["triangles"], 256)
            self.assertEqual(collision["materials"], 0)
            self.assertTrue(collision["stable_root"])
