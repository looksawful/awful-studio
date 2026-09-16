import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "docs" / "assets" / "registry.json"
REQUIRED_HEADINGS = (
    "## Identity and production role",
    "## Dimensional contract",
    "## Reference and provenance",
    "## Component decomposition",
    "## Geometry plan",
    "## Materials and surface response",
    "## UV and texture plan",
    "## Bake plan",
    "## LOD, collision and runtime",
    "## Rigging, variants and mounts",
    "## QA and acceptance gates",
    "## Production handoff",
)

class AssetDossierContractTests(unittest.TestCase):
    def test_registry_and_all_dossiers_are_complete(self):
        self.assertTrue(REGISTRY.exists(), "docs/assets/registry.json is required")
        data = json.loads(REGISTRY.read_text(encoding="utf-8"))
        self.assertEqual(data["schema_version"], 1)
        assets = data["assets"]
        self.assertGreaterEqual(len(assets), 55)
        ids = [asset["id"] for asset in assets]
        self.assertEqual(len(ids), len(set(ids)), "asset ids must be unique")
        for asset in assets:
            with self.subTest(asset=asset["id"]):
                for key in (
                    "category", "identity_class", "stage", "tier",
                    "dimensions", "source_refs", "dossier_path",
                    "production_ready", "runtime",
                ):
                    self.assertIn(key, asset)
                self.assertTrue(asset["dimensions"])
                self.assertTrue(asset["source_refs"])
                dossier = ROOT / asset["dossier_path"]
                self.assertTrue(dossier.exists(), str(dossier))
                text = dossier.read_text(encoding="utf-8")
                for heading in REQUIRED_HEADINGS:
                    self.assertIn(heading, text)
                upper = text.upper()
                self.assertNotIn("TODO", upper)
                self.assertNotIn("TBD", upper)
                self.assertNotIn("FILL IN", upper)

    def test_master_docs_exist(self):
        for rel in (
            "docs/assets/README.md",
            "docs/assets/sources.md",
            "docs/assets/PRODUCTION_ORDER.md",
            "docs/assets/contracts/GENERAL_ASSET_CONTRACT.md",
            "docs/assets/contracts/STUDIO_RIG_CONTRACT.md",
            "docs/assets/contracts/MATERIAL_TEXTURE_CONTRACT.md",
            "docs/assets/contracts/LOD_RUNTIME_CONTRACT.md",
            "docs/assets/contracts/QA_VISUAL_APPROVAL_CONTRACT.md",
        ):
            self.assertTrue((ROOT / rel).exists(), rel)

if __name__ == "__main__":
    unittest.main()
