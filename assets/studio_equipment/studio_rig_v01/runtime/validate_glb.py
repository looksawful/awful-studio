import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MANIFEST = json.loads((ROOT / "asset_manifest.json").read_text(encoding="utf-8"))
EVIDENCE = ROOT / "glb_validation.json"


def read_glb(path):
    data = path.read_bytes()
    magic, version, total = struct.unpack_from("<4sII", data, 0)
    if magic != b"glTF" or version != 2 or total != len(data):
        raise ValueError(f"Invalid GLB header: {path}")
    json_len, json_type = struct.unpack_from("<II", data, 12)
    if json_type != 0x4E4F534A:
        raise ValueError(f"Missing GLB JSON chunk: {path}")
    raw = data[20:20 + json_len].decode("utf-8").rstrip("\x00 ")
    return json.loads(raw)


def geometry_stats(doc):
    accessors = doc.get("accessors", [])
    primitives = vertices = triangles = 0
    for mesh in doc.get("meshes", []):
        for primitive in mesh.get("primitives", []):
            primitives += 1
            position = primitive.get("attributes", {}).get("POSITION")
            if position is not None:
                vertices += accessors[position]["count"]
            indices = primitive.get("indices")
            if indices is not None:
                triangles += accessors[indices]["count"] // 3
            elif position is not None:
                triangles += accessors[position]["count"] // 3
    return primitives, vertices, triangles


def inspect_asset(asset_key, entry):
    path = ROOT / entry["glb"]
    if not path.is_file() or path.stat().st_size == 0:
        raise FileNotFoundError(path)
    doc = read_glb(path)
    names = [node.get("name", "") for node in doc.get("nodes", [])]
    primitives, vertices, triangles = geometry_stats(doc)
    extensions = set(doc.get("extensionsUsed", []))
    item = {
        "file": entry["glb"],
        "bytes": path.stat().st_size,
        "nodes": len(names),
        "meshes": len(doc.get("meshes", [])),
        "primitives": primitives,
        "vertices": vertices,
        "triangles": triangles,
        "materials": len(doc.get("materials", [])),
        "meshopt": "EXT_meshopt_compression" in extensions,
        "cameras": len(doc.get("cameras", [])),
        "lights": "KHR_lights_punctual" in extensions,
        "reference_nodes": [n for n in names if "REFERENCE_ENVELOPE" in n],
        "stable_root": entry["root"] in names,
    }
    item["pass"] = all((
        item["meshopt"],
        item["cameras"] == 0,
        not item["lights"],
        item["reference_nodes"] == [],
        item["stable_root"],
        item["triangles"] > 0,
    ))
    return item


def main():
    assets = {
        key: inspect_asset(key, entry)
        for key, entry in MANIFEST["assets"].items()
    }
    result = {
        "schema_version": 1,
        "assets": assets,
        "pass": all(item["pass"] for item in assets.values()),
    }
    EVIDENCE.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    for key, item in assets.items():
        print(
            "AWFUL_GLTF_VALIDATE",
            key,
            f"{item['bytes']}B",
            f"{item['triangles']}tris",
            f"{item['materials']}mats",
            "PASS" if item["pass"] else "FAIL",
        )
    if not result["pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
