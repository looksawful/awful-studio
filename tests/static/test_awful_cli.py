import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[2] / "tools" / "awful.py"
spec = importlib.util.spec_from_file_location("awful_cli", MODULE_PATH)
awful = importlib.util.module_from_spec(spec)
sys.modules["awful_cli"] = awful
spec.loader.exec_module(awful)


class AwfulCliTests(unittest.TestCase):
    def make_repo(self):
        td = tempfile.TemporaryDirectory()
        root = Path(td.name)
        (root / "runtime").mkdir()
        (root / "integrations").mkdir()
        (root / "runtime" / "blender.lock").write_text(
            'schema_version = "1.0"\nversion = "5.2.1"\nseries = "5.2"\nplatform = "linux-x64"\narchive = "blender-5.2.1-linux-x64.tar.xz"\nsha256 = "abc"\nrelease_asset_url = "https://example.invalid/blender.tar.xz"\nofficial_url = "https://example.invalid/fallback.tar.xz"\nextracted_dir = "blender-5.2.1-linux-x64"\nexecutable = "blender"\n',
            encoding="utf-8",
        )
        (root / "integrations" / "manifest.toml").write_text(
            'schema_version = "1.0"\n[[integration]]\nid = "blender-agent-studio"\nname = "Blender Agent Studio"\nstatus = "pilot"\n[[integration]]\nid = "flue"\nname = "Flue"\nstatus = "candidate"\n',
            encoding="utf-8",
        )
        (root / "AGENTS.md").write_text("rules", encoding="utf-8")
        (root / "STATE.md").write_text("state", encoding="utf-8")
        return td, root

    def test_load_runtime_lock_reads_pinned_blender_version(self):
        td, root = self.make_repo()
        self.addCleanup(td.cleanup)
        data = awful.load_runtime_lock(root)
        self.assertEqual(data["version"], "5.2.1")
        self.assertEqual(data["platform"], "linux-x64")

    def test_status_snapshot_reads_integration_statuses(self):
        td, root = self.make_repo()
        self.addCleanup(td.cleanup)
        snapshot = awful.build_status_snapshot(root)
        self.assertEqual(snapshot["blender_version"], "5.2.1")
        self.assertEqual(snapshot["integrations"]["blender-agent-studio"], "pilot")
        self.assertEqual(snapshot["integrations"]["flue"], "candidate")

    def test_sha256_file_returns_digest(self):
        td, root = self.make_repo()
        self.addCleanup(td.cleanup)
        payload = root / "payload.bin"
        payload.write_bytes(b"awful")
        self.assertEqual(
            awful.sha256_file(payload),
            "87e1315329cf22c9ce1432d1626cbbb1f8e2798faf0494040d7c4616ba9ea854",
        )

    def test_doctor_warns_when_blender_is_not_bootstrapped_but_repo_is_valid(self):
        td, root = self.make_repo()
        self.addCleanup(td.cleanup)
        results = awful.doctor_checks(root, blender_override=None)
        by_name = {item.name: item for item in results}
        self.assertEqual(by_name["AGENTS.md"].level, "PASS")
        self.assertEqual(by_name["STATE.md"].level, "PASS")
        self.assertEqual(by_name["Blender runtime"].level, "WARN")

    def test_find_blender_prefers_explicit_override(self):
        td, root = self.make_repo()
        self.addCleanup(td.cleanup)
        fake = root / "fake-blender"
        fake.write_text("", encoding="utf-8")
        found = awful.find_blender(root, blender_override=str(fake))
        self.assertEqual(found, fake)


if __name__ == "__main__":
    unittest.main()
