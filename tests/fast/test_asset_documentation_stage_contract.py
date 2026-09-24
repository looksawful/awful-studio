"""Keep generated device documentation stages aligned with committed validation evidence."""

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "docs" / "assets" / "registry.json"

DEVICE_EVIDENCE = {
    "iphone_17": (ROOT / "assets" / "device_mockups" / "iphone_17" / "evidence", "low_v*_validation.json"),
    "ipad_pro_11_m5": (ROOT / "assets" / "device_mockups" / "ipad_pro" / "evidence", "ipad_pro_11_m5_low_v*_validation.json"),
    "ipad_pro_13_m5": (ROOT / "assets" / "device_mockups" / "ipad_pro" / "evidence", "ipad_pro_13_m5_low_v*_validation.json"),
    "macbook_pro_14_m5": (ROOT / "assets" / "device_mockups" / "macbook_pro_14" / "evidence", "low_v*_release_validation.json"),
}


def latest_validation(directory: Path, pattern: str) -> Path:
    candidates = list(directory.glob(pattern))
    if not candidates:
        raise AssertionError(f"no validation evidence matching {directory / pattern}")

    def version(path: Path) -> int:
        match = re.search(r"low_v(\d+)", path.name)
        if not match:
            raise AssertionError(f"validation filename has no low_vN version: {path}")
        return int(match.group(1))

    return max(candidates, key=version)


class AssetDocumentationStageContractTests(unittest.TestCase):
    def test_device_registry_stage_matches_latest_committed_validation_evidence(self):
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        assets = {asset["id"]: asset for asset in registry["assets"]}

        for asset_id, (directory, pattern) in DEVICE_EVIDENCE.items():
            with self.subTest(asset=asset_id):
                evidence_path = latest_validation(directory, pattern)
                evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
                self.assertEqual(
                    assets[asset_id]["stage"],
                    evidence["stage"],
                    f"{asset_id} documentation stage must match {evidence_path.name}",
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
