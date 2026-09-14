import json
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parent
MANIFEST = json.loads((ROOT / "asset_manifest.json").read_text(encoding="utf-8"))
OUTPUT = ROOT / "glb"


def descendants(root):
    result = [root]
    stack = list(root.children)
    while stack:
        obj = stack.pop()
        result.append(obj)
        stack.extend(obj.children)
    return result


def exportable(obj):
    if obj.type in {"CAMERA", "LIGHT"}:
        return False
    if obj.name.endswith("REFERENCE_ENVELOPE"):
        return False
    return True


def select_asset(root_name):
    bpy.ops.object.select_all(action="DESELECT")
    root = bpy.data.objects.get(root_name)
    if root is None:
        raise RuntimeError(f"Missing runtime root: {root_name}")
    selected = []
    for obj in descendants(root):
        if not exportable(obj):
            continue
        obj.hide_set(False)
        obj.select_set(True)
        selected.append(obj)
    bpy.context.view_layer.objects.active = root
    return selected


def export_one(asset_key, entry):
    selected = select_asset(entry["root"])
    if not selected:
        raise RuntimeError(f"No exportable objects for {asset_key}")
    target = ROOT / entry["glb"]
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        target.unlink()
    bpy.ops.export_scene.gltf(
        filepath=str(target),
        check_existing=False,
        export_format="GLB",
        use_selection=True,
        export_yup=True,
        export_apply=True,
        export_extras=True,
        export_cameras=False,
        export_lights=False,
        export_animations=False,
        export_meshopt_compression_enable=True,
        export_texcoords=True,
        export_normals=True,
        export_materials="EXPORT",
    )
    if not target.is_file() or target.stat().st_size == 0:
        raise RuntimeError(f"GLB export failed: {target}")
    print("AWFUL_GLTF_EXPORT", asset_key, target.name, target.stat().st_size)


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for asset_key, entry in MANIFEST["assets"].items():
        export_one(asset_key, entry)
    bpy.ops.object.select_all(action="DESELECT")


if __name__ == "__main__":
    main()
