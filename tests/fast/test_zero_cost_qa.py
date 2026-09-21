import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
AWFUL = ROOT / "tools" / "awful.py"


class AssetMetricsCliTests(unittest.TestCase):
    def run_awful(self, *args):
        return subprocess.run(
            [sys.executable, str(AWFUL), *map(str, args)],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )

    def test_asset_metrics_writes_deterministic_machine_readable_receipt(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            asset = root / "model.glb"
            asset.write_bytes(b"glTF-test-payload")
            output = root / "receipt.json"

            result = self.run_awful("asset-metrics", asset, "--output", output)

            self.assertEqual(result.returncode, 0, result.stderr)
            receipt = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(receipt["schema_version"], 1)
            self.assertEqual(receipt["asset"]["name"], "model.glb")
            self.assertEqual(receipt["asset"]["extension"], ".glb")
            self.assertEqual(receipt["asset"]["bytes"], len(b"glTF-test-payload"))
            self.assertEqual(len(receipt["asset"]["sha256"]), 64)
            self.assertNotIn("absolute_path", json.dumps(receipt))
            self.assertEqual(json.loads(result.stdout), receipt)

    def test_asset_metrics_rejects_missing_asset_without_creating_receipt(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            output = root / "receipt.json"

            result = self.run_awful("asset-metrics", root / "missing.glb", "--output", output)

            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(output.exists())

    def test_tooling_doctor_is_offline_and_reports_optional_zero_cost_tools(self):
        result = self.run_awful("tooling-doctor")

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "PASS")
        tools = {item["name"]: item for item in payload["tools"]}
        self.assertEqual(tools["SonarQube Community"]["required"], False)
        self.assertEqual(tools["Docker"]["required"], False)
        self.assertEqual(tools["CircleCI CLI"]["required"], False)


if __name__ == "__main__":
    unittest.main()
