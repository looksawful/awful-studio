import json
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parent
MANIFEST = json.loads((ROOT / "asset_manifest.json").read_text(encoding="utf-8"))
LOD_RATIOS = {"LOD1": 0.50, "LOD2": 0.18}

LOD1_DROP = (
    "D1_DISPLAY_SEG_", "D1_REAR_BUTTON_", "D1_READY_INDICATOR",
    "D1_ZOOM_TICK_", "D1_UMBRELLA_TUBE_RIM",
    "SANDBAG_SEAM_", "SANDBAG_LABEL_PATCH",
    "CSTAND_TBAR_", "CSTAND_TOP_TBAR",
)
LOD2_DROP = LOD1_DROP + (
    "D1_SIDE_VENT_", "D1_FLASHTUBE", "D1_MODELING_LAMP",
    "D1_SYNC_PORT", "D1_AC_CONNECTOR", "D1_FUSE_HOLDER",
    "D1_UMBRELLA_TUBE", "D1_LOCK_RING", "D1_REAR_DISPLAY",
    "D1_SETTING_KNOB", "CSTAND_KNOB_STEM_", "CSTAND_KNOB_",
    "CSTAND_TOP_HANDLE_STEM", "CSTAND_TOP_HANDLE",
    "CSTAND_TOP_GRIP_FACE_", "SANDBAG_HANDLE_",
    "MAGNUM_COLLAR_GROOVE", "MAGNUM_INNER_RIM",
)


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


def lod_exportable(obj, level):
    if not visual_exportable(obj):
        return False
    drop = LOD1_DROP if level == "LOD1" else LOD2_DROP
    return not any(obj.name.startswith(prefix) for prefix in drop)


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


def add_lod_modifiers(selected, level):
    ratio = LOD_RATIOS[level]
    added = []
    for obj in selected:
        if obj.type != "MESH":
            continue
        has_subsurf = any(mod.type == "SUBSURF" for mod in obj.modifiers)
        if len(obj.data.polygons) < 20 and not has_subsurf:
            continue
        mod = obj.modifiers.new(f"_AWFUL_{level}_DECIMATE", "DECIMATE")
        mod.decimate_type = "COLLAPSE"
        mod.ratio = ratio
        mod.use_collapse_triangulate = True
        added.append((obj, mod))
    return added


def remove_lod_modifiers(added):
    for obj, mod in reversed(added):
        if obj and mod and mod.name in obj.modifiers:
            obj.modifiers.remove(mod)


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
    target = ROOT / entry["lod_glb"]["LOD0"]
    export_selected(target, materials="EXPORT", meshopt=True)
    print("AWFUL_GLTF_EXPORT", asset_key, "LOD0", target.name, target.stat().st_size)


def export_lod(asset_key, entry, level):
    selected = select_tree(entry["root"], lambda obj: lod_exportable(obj, level))
    if not selected:
        raise RuntimeError(f"No {level} visual objects for {asset_key}")
    added = add_lod_modifiers(selected, level)
    target = ROOT / entry["lod_glb"][level]
    try:
        export_selected(target, materials="EXPORT", meshopt=True)
    finally:
        remove_lod_modifiers(added)
    print("AWFUL_LOD_EXPORT", asset_key, level, target.name, target.stat().st_size)


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
        export_lod(asset_key, entry, "LOD1")
        export_lod(asset_key, entry, "LOD2")
        export_collision(asset_key, entry)
    bpy.ops.object.select_all(action="DESELECT")


if __name__ == "__main__":
    main()
