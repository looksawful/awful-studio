#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError as exc:  # pragma: no cover - Python < 3.11
    raise SystemExit("AWFUL tooling requires Python 3.11+ (tomllib).") from exc


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class DoctorResult:
    level: str
    name: str
    detail: str


def load_toml(path: Path) -> dict:
    with path.open("rb") as fh:
        return tomllib.load(fh)


def load_runtime_lock(root: Path = ROOT) -> dict:
    return load_toml(root / "runtime" / "blender.lock")


def load_integrations(root: Path = ROOT) -> dict[str, str]:
    path = root / "integrations" / "manifest.toml"
    if not path.exists():
        return {}
    data = load_toml(path)
    return {
        item["id"]: item.get("status", "unknown")
        for item in data.get("integration", [])
        if item.get("id")
    }


def build_status_snapshot(root: Path = ROOT) -> dict:
    runtime = load_runtime_lock(root)
    return {
        "project": "AWFUL STUDIO",
        "current_release": "0.0.15",
        "target_release": "0.0.16",
        "blender_version": runtime["version"],
        "blender_platform": runtime["platform"],
        "integrations": load_integrations(root),
    }


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def expected_blender_path(root: Path = ROOT) -> Path:
    runtime = load_runtime_lock(root)
    executable = runtime.get("executable", "blender")
    if os.name == "nt" and not executable.lower().endswith(".exe"):
        executable += ".exe"
    return root / ".runtime" / runtime["extracted_dir"] / executable


def find_blender(root: Path = ROOT, blender_override: str | None = None) -> Path | None:
    override = blender_override or os.environ.get("AWFUL_BLENDER")
    if override:
        candidate = Path(override).expanduser()
        if candidate.exists():
            return candidate

    candidate = expected_blender_path(root)
    if candidate.exists():
        return candidate

    system = shutil.which("blender")
    return Path(system) if system else None


def doctor_checks(root: Path = ROOT, blender_override: str | None = None) -> list[DoctorResult]:
    results: list[DoctorResult] = []
    for name in ("AGENTS.md", "STATE.md"):
        path = root / name
        results.append(DoctorResult("PASS" if path.exists() else "FAIL", name, str(path)))

    lock = root / "runtime" / "blender.lock"
    results.append(DoctorResult("PASS" if lock.exists() else "FAIL", "Blender lock", str(lock)))

    integrations = root / "integrations" / "manifest.toml"
    results.append(
        DoctorResult(
            "PASS" if integrations.exists() else "WARN",
            "Integration manifest",
            str(integrations),
        )
    )

    blender = find_blender(root, blender_override)
    if blender:
        results.append(DoctorResult("PASS", "Blender runtime", str(blender)))
    else:
        results.append(
            DoctorResult(
                "WARN",
                "Blender runtime",
                "not present locally; run `python tools/awful.py bootstrap` or use CI",
            )
        )
    return results


def print_status(root: Path = ROOT) -> int:
    snapshot = build_status_snapshot(root)
    print(snapshot["project"])
    print(f"Current release: {snapshot['current_release']}")
    print(f"Target release: {snapshot['target_release']}")
    print(f"Blender runtime: {snapshot['blender_version']} ({snapshot['blender_platform']})")
    if snapshot["integrations"]:
        print("Integrations:")
        for name, status in sorted(snapshot["integrations"].items()):
            print(f"  {name}: {status}")
    return 0


def print_doctor(root: Path = ROOT, blender_override: str | None = None) -> int:
    results = doctor_checks(root, blender_override)
    for item in results:
        print(f"{item.level:4} {item.name}: {item.detail}")
    return 1 if any(item.level == "FAIL" for item in results) else 0


def _download(url: str, destination: Path) -> None:
    request = urllib.request.Request(url, headers={"User-Agent": "AWFUL-STUDIO-bootstrap"})
    with urllib.request.urlopen(request, timeout=60) as response, destination.open("wb") as out:
        shutil.copyfileobj(response, out)


def bootstrap_blender(root: Path = ROOT, force: bool = False) -> Path:
    runtime = load_runtime_lock(root)
    installed = expected_blender_path(root)
    if installed.exists() and not force:
        return installed

    cache = root / ".cache" / "blender"
    cache.mkdir(parents=True, exist_ok=True)
    archive = cache / runtime["archive"]

    if force and archive.exists():
        archive.unlink()

    if not archive.exists():
        errors: list[str] = []
        for url_key in ("release_asset_url", "official_url"):
            url = runtime.get(url_key, "").strip()
            if not url:
                continue
            try:
                print(f"Downloading Blender from {url}")
                with tempfile.NamedTemporaryFile(dir=cache, delete=False) as tmp:
                    tmp_path = Path(tmp.name)
                try:
                    _download(url, tmp_path)
                    tmp_path.replace(archive)
                finally:
                    tmp_path.unlink(missing_ok=True)
                break
            except (OSError, urllib.error.URLError) as exc:
                errors.append(f"{url}: {exc}")
        else:
            raise RuntimeError("Unable to download pinned Blender runtime:\n" + "\n".join(errors))

    actual_sha = sha256_file(archive)
    if actual_sha != runtime["sha256"]:
        raise RuntimeError(
            f"Blender archive checksum mismatch: expected {runtime['sha256']}, got {actual_sha}"
        )

    runtime_root = root / ".runtime"
    runtime_root.mkdir(parents=True, exist_ok=True)
    target_dir = runtime_root / runtime["extracted_dir"]
    if target_dir.exists() and force:
        shutil.rmtree(target_dir)

    if not target_dir.exists():
        with tarfile.open(archive, mode="r:xz") as tf:
            tf.extractall(runtime_root, filter="data")

    if not installed.exists():
        raise RuntimeError(f"Blender executable missing after extraction: {installed}")
    return installed


def run_runtime_smoke(root: Path = ROOT, blender_override: str | None = None) -> int:
    blender = find_blender(root, blender_override)
    if blender is None:
        print("Blender runtime not found. Run `python tools/awful.py bootstrap` first.")
        return 2
    test_script = root / "tests" / "blender" / "runtime_smoke.py"
    if not test_script.exists():
        print(f"Runtime smoke script missing: {test_script}")
        return 2
    command = [
        str(blender),
        "--background",
        "--factory-startup",
        "--disable-autoexec",
        "--python-exit-code",
        "1",
        "--python",
        str(test_script),
    ]
    print("Running:", " ".join(command), flush=True)
    return subprocess.run(command, cwd=root, check=False).returncode


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AWFUL STUDIO development entrypoint")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("status", help="print concise project/runtime state")
    doctor = sub.add_parser("doctor", help="check agent development prerequisites")
    doctor.add_argument("--blender", help="explicit Blender executable")
    bootstrap = sub.add_parser("bootstrap", help="download and extract pinned Blender runtime")
    bootstrap.add_argument("--force", action="store_true")
    runtime = sub.add_parser("test-runtime", help="run the real Blender headless smoke test")
    runtime.add_argument("--blender", help="explicit Blender executable")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "status":
        return print_status(ROOT)
    if args.command == "doctor":
        return print_doctor(ROOT, args.blender)
    if args.command == "bootstrap":
        try:
            blender = bootstrap_blender(ROOT, force=args.force)
        except Exception as exc:  # CLI boundary
            print(f"FAIL bootstrap: {exc}", file=sys.stderr)
            return 1
        print(f"PASS Blender runtime: {blender}")
        return 0
    if args.command == "test-runtime":
        return run_runtime_smoke(ROOT, args.blender)
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
