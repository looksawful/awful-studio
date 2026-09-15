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


def inspect_visual(entry, relative_path):
    path = ROOT / relative_path
    doc = read_glb(path)
    names = [node.get("name", "") for node in doc.get("nodes", [])]
    primitives, vertices, triangles = geometry_stats(doc)
    extensions = set(doc.get("extensionsUsed", []))
    item = {
        "file": relative_path,
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
        "collision_nodes": [n for n in names if n.startswith("COL_")],
        "stable_root": entry["root"] in names,
    }
    item["pass"] = all((
        item["meshopt"],
        item["cameras"] == 0,
        not item["lights"],
        item["reference_nodes"] == [],
        item["collision_nodes"] == [],
        item["stable_root"],
        item["triangles"] > 0,
    ))
    return item


def inspect_collision(entry):
    path = ROOT / entry["collision_glb"]
    doc = read_glb(path)
    names = [node.get("name", "") for node in doc.get("nodes", [])]
    primitives, vertices, triangles = geometry_stats(doc)
    item = {
        "file": entry["collision_glb"],
        "bytes": path.stat().st_size,
        "nodes": len(names),
        "meshes": len(doc.get("meshes", [])),
        "primitives": primitives,
        "vertices": vertices,
        "triangles": triangles,
        "materials": len(doc.get("materials", [])),
        "stable_root": entry["collider"] in names,
    }
    item["pass"] = all((
        item["triangles"] > 0,
        item["triangles"] <= 256,
        item["materials"] == 0,
        item["stable_root"],
    ))
    return item


def lod_budget_pass(lods):
    l0 = lods["LOD0"]["triangles"]
    l1 = lods["LOD1"]["triangles"]
    l2 = lods["LOD2"]["triangles"]
    return (
        l1 < l0
        and l2 < l1
        and l1 <= int(l0 * 0.75)
        and l2 <= int(l0 * 0.35)
    )


def main():
    assets = {}
    lod_assets = {}
    collision_assets = {}
    for key, entry in MANIFEST["assets"].items():
        lods = {
            level: inspect_visual(entry, path)
            for level, path in entry["lod_glb"].items()
        }
        lods["budget_pass"] = lod_budget_pass(lods)
        assets[key] = lods["LOD0"]
        lod_assets[key] = lods
        collision_assets[key] = inspect_collision(entry)

    result = {
        "schema_version": 3,
        "assets": assets,
        "lod_assets": lod_assets,
        "collision_assets": collision_assets,
        "pass": (
            all(item["pass"] for item in assets.values())
            and all(item["budget_pass"] for item in lod_assets.values())
            and all(item["pass"] for item in collision_assets.values())
        ),
    }
    EVIDENCE.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    for key, lods in lod_assets.items():
        print(
            "AWFUL_LOD_VALIDATE", key,
            f"LOD0={lods['LOD0']['triangles']}",
            f"LOD1={lods['LOD1']['triangles']}",
            f"LOD2={lods['LOD2']['triangles']}",
            "PASS" if lods["budget_pass"] else "FAIL",
        )
    for key, item in collision_assets.items():
        print("AWFUL_COLLISION_VALIDATE", key, f"{item['triangles']}tris", "PASS" if item["pass"] else "FAIL")
    if not result["pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
