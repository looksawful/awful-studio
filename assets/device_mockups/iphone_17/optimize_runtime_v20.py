import json
import os
import struct
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNTIME = HERE / "runtime" / "v20"
COMPAT = RUNTIME / "iphone_17_v20_web.glb"
MESHOPT = RUNTIME / "iphone_17_v20_web_meshopt.glb"
MANIFEST = RUNTIME / "iphone_17_v20.asset.json"
GLTF_TRANSFORM_VERSION = "4.5.0"
CRITICAL_NODES = {
    "CTRL_IPHONE_17",
    "DYNAMIC_ISLAND",
    "FRONT_SENSOR_PILL",
    "FRONT_CAMERA_GLASS",
    "SCREEN_CONTENT",
    "ANCHOR_CENTER",
    "ANCHOR_BOTTOM_CENTER",
    "ANCHOR_SCREEN_CENTER",
    "ANCHOR_REAR_CAMERA",
}


def read_glb_json(path: Path):
    data = path.read_bytes()
    if data[:4] != b"glTF":
        raise RuntimeError(f"Not a GLB: {path}")
    json_len, json_type = struct.unpack_from("<II", data, 12)
    if json_type != 0x4E4F534A:
        raise RuntimeError(f"First GLB chunk is not JSON: {path}")
    return json.loads(data[20:20 + json_len].decode("utf-8").rstrip(" \t\r\n\x00"))


def node_names(doc):
    return {node.get("name") for node in doc.get("nodes", []) if node.get("name")}


def main():
    for path in (COMPAT, MANIFEST):
        if not path.is_file():
            raise FileNotFoundError(path)

    npx = "npx.cmd" if os.name == "nt" else "npx"
    cmd = [
        npx,
        "--yes",
        f"@gltf-transform/cli@{GLTF_TRANSFORM_VERSION}",
        "meshopt",
        str(COMPAT),
        str(MESHOPT),
        "--level",
        "high",
    ]
    subprocess.run(cmd, check=True, cwd=HERE)

    compat_doc = read_glb_json(COMPAT)
    meshopt_doc = read_glb_json(MESHOPT)
    missing = CRITICAL_NODES - node_names(meshopt_doc)
    if missing:
        raise RuntimeError(f"Meshopt output lost critical nodes: {sorted(missing)}")
    required = set(meshopt_doc.get("extensionsRequired", []))
    if "EXT_meshopt_compression" not in required:
        raise RuntimeError(f"Meshopt extension is not required: {sorted(required)}")
    if COMPAT.stat().st_size <= MESHOPT.stat().st_size:
        raise RuntimeError("Meshopt output is not smaller than compatibility GLB")

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    manifest["web_variants"] = {
        "compat": {
            "file": COMPAT.name,
            "requires": [],
        },
        "meshopt": {
            "file": MESHOPT.name,
            "requires": ["MeshoptDecoder"],
            "extensions_required": sorted(required),
        },
    }
    manifest["default_web_variant"] = "compat"
    manifest["preferred_web_variant"] = "meshopt"
    manifest["web_optimizer"] = {
        "tool": "@gltf-transform/cli",
        "version": GLTF_TRANSFORM_VERSION,
        "command": "meshopt --level high",
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({
        "compat_bytes": COMPAT.stat().st_size,
        "meshopt_bytes": MESHOPT.stat().st_size,
        "ratio": round(MESHOPT.stat().st_size / COMPAT.stat().st_size, 4),
        "critical_nodes": sorted(CRITICAL_NODES),
        "extensions_required": sorted(required),
        "manifest": str(MANIFEST),
    }, indent=2))


if __name__ == "__main__":
    main()
