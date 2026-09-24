"""Keep generated device documentation stages aligned with committed validation evidence."""

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "docs" / "assets" / "registry.json"

DEVICE_EVIDENCE = {
    "iphone_17": ROOT / "assets" / "device_mockups" / "iphone_17" / "evidence" / "low_v30_validation.json",
    "ipad_pro_11_m5": ROOT / "assets" / "device_mockups" / "ipad_pro" / "evidence" / "ipad_pro_11_m5_low_v6_validation.json",
    "ipad_pro_13_m5": ROOT / "assets" / "device_mockups" / "ipad_pro" / "evidence" / "ipad_pro_13_m5_low_v6_validation.json",
    "macbook_pro_14_m5": ROOT / "assets" / "device_mockups" / "macbook_pro_14" / "evidence" / "low_v1_release_validation.json",
}


class AssetDocumentationStageContractTests(unittest.TestCase):
    def test_device_registry_stage_matches_canonical_validation_evidence(self):
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        assets = {asset["id"]: asset for asset in registry["assets"]}

        for asset_id, evidence_path in DEVICE_EVIDENCE.items():
            with self.subTest(asset=asset_id):
                evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
                self.assertEqual(
                    assets[asset_id]["stage"],
                    evidence["stage"],
                    f"{asset_id} documentation stage must match canonical validation evidence",
                )

    def test_device_dossier_stage_matches_registry(self):
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        assets = {asset["id"]: asset for asset in registry["assets"]}

        for asset_id in DEVICE_EVIDENCE:
            with self.subTest(asset=asset_id):
                dossier = ROOT / assets[asset_id]["dossier_path"]
                text = dossier.read_text(encoding="utf-8")
                self.assertIn(
                    f"- Current stage: `{assets[asset_id]['stage']}`",
                    text,
                )


if __name__ == "__main__":
    unittest.main()
