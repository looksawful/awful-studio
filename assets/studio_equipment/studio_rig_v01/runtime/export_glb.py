import json
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parent
MANIFEST = json.loads((ROOT / "asset_manifest.json").read_text(encoding="utf-8"))


def descendants(root):
    result = [root]
    stack = list(root.children)
    while stack:
        obj = stack.pop()
        result.append(obj)
        stack.extend(obj.children)
    return result


def visual_exportable(obj):
    if obj.type in {"CAMERA", "LIGHT"}:
        return False
    if obj.name.endswith("REFERENCE_ENVELOPE"):
        return False
    if obj.name.startswith("COL_"):
        return False
    return True


def select_tree(root_name, predicate=lambda _obj: True):
    bpy.ops.object.select_all(action="DESELECT")
    root = bpy.data.objects.get(root_name)
    if root is None:
        raise RuntimeError(f"Missing runtime root: {root_name}")
    selected = []
    for obj in descendants(root):
        if not predicate(obj):
            continue
        obj.hide_set(False)
        obj.select_set(True)
        selected.append(obj)
    bpy.context.view_layer.objects.active = root
    return selected


def export_selected(target, materials="EXPORT", meshopt=True):
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
        export_meshopt_compression_enable=meshopt,
        export_texcoords=(materials != "NONE"),
        export_normals=(materials != "NONE"),
        export_materials=materials,
    )
    if not target.is_file() or target.stat().st_size == 0:
        raise RuntimeError(f"GLB export failed: {target}")


def export_visual(asset_key, entry):
    selected = select_tree(entry["root"], visual_exportable)
    if not selected:
        raise RuntimeError(f"No visual objects for {asset_key}")
    target = ROOT / entry["glb"]
    export_selected(target, materials="EXPORT", meshopt=True)
    print("AWFUL_GLTF_EXPORT", asset_key, target.name, target.stat().st_size)


def export_collision(asset_key, entry):
    selected = select_tree(entry["collider"])
    if not selected:
        raise RuntimeError(f"No collision objects for {asset_key}")
    target = ROOT / entry["collision_glb"]
    export_selected(target, materials="NONE", meshopt=False)
    print("AWFUL_COLLISION_EXPORT", asset_key, target.name, target.stat().st_size)


def main():
    for asset_key, entry in MANIFEST["assets"].items():
        export_visual(asset_key, entry)
        export_collision(asset_key, entry)
    bpy.ops.object.select_all(action="DESELECT")


if __name__ == "__main__":
    main()
