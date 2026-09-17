import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

class AssetDocumentationCompletenessTests(unittest.TestCase):
    def test_required_system_docs_exist(self):
        required = [
            "docs/assets/COMPATIBILITY_MATRIX.md",
            "docs/assets/diagrams/studio_rig.md",
            "docs/assets/diagrams/asset_pipeline.md",
            "docs/assets/diagrams/soft_modifier_system.md",
            "docs/assets/diagrams/camera_lens_system.md",
            "docs/assets/diagrams/furniture_layers.md",
            "docs/assets/diagrams/device_material_stack.md",
            "docs/superpowers/plans/2026-09-16-asset-library-production.md",
        ]
        for rel in required:
            self.assertTrue((ROOT / rel).is_file(), rel)

    def test_asset_docs_have_no_placeholders(self):
        for path in (ROOT / "docs" / "assets").rglob("*.md"):
            upper = path.read_text(encoding="utf-8").upper()
            for forbidden in ("TODO", "TBD", "FILL IN", "PLACEHOLDER"):
                self.assertNotIn(forbidden, upper, f"{forbidden} in {path}")

if __name__ == "__main__":
    unittest.main()
