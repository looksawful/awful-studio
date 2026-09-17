from __future__ import annotations

import argparse
import sys
from pathlib import Path

import bpy


def parse_args():
    tail = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--studio", required=True)
    parser.add_argument("--site", required=True)
    parser.add_argument("--out", required=True)
    return parser.parse_args(tail)


def descendants(root):
    result = []
    stack = list(root.children)
    while stack:
        obj = stack.pop()
        result.append(obj)
        stack.extend(obj.children)
    return result


def select_hierarchy(root):
    bpy.ops.object.select_all(action="DESELECT")
    for obj in [root, *descendants(root)]:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = root


def export_fbx(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.export_scene.fbx(
        filepath=str(path),
        use_selection=True,
        apply_unit_scale=True,
        add_leaf_bones=False,
        path_mode="COPY",
        embed_textures=True,
    )
    print(f"AWFUL_EXPORT:{path}")


def export_studio(studio: Path, out_dir: Path):
    sys.path.insert(0, str(studio / "extension"))
    import awful_studio

    awful_studio.register()
    scene = bpy.context.scene
    keys = ("BOTTLE", "JAR", "BOX", "CAN", "PHONE", "TABLET")
    scene.awful_studio.product_mockup = keys[0]
    if not bpy.ops.awful.build_studio.poll():
        raise RuntimeError("AWFUL Build Studio is unavailable in clean scene")
    if bpy.ops.awful.build_studio() != {"FINISHED"}:
        raise RuntimeError("AWFUL Build Studio failed")

    for index, key in enumerate(keys):
        if index:
            scene.awful_studio.product_mockup = key
            if bpy.ops.awful.generate_mockup() != {"FINISHED"}:
                raise RuntimeError(f"AWFUL mockup generation failed: {key}")
        root = next(
            (obj for obj in scene.objects if obj.get("awful_mockup_key") == key),
            None,
        )
        if root is None:
            raise RuntimeError(f"AWFUL mockup root missing: {key}")
        select_hierarchy(root)
        export_fbx(out_dir / f"{key.lower()}.fbx")


def clear_scene_objects():
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)


def export_site_models(site: Path, out_dir: Path):
    public_root = site / "public"
    models = sorted(public_root.rglob("*.glb"))
    for source in models:
        clear_scene_objects()
        bpy.ops.import_scene.gltf(filepath=str(source))
        bpy.ops.object.select_all(action="SELECT")
        relative = source.relative_to(public_root).with_suffix("")
        slug = "__".join(relative.parts)
        export_fbx(out_dir / f"{slug}.fbx")
    return len(models)


def main():
    args = parse_args()
    studio = Path(args.studio).resolve()
    site = Path(args.site).resolve()
    out = Path(args.out).resolve()
    studio_out = out / "Models" / "Studio"
    site_out = out / "Models" / "Site"
    studio_out.mkdir(parents=True, exist_ok=True)
    site_out.mkdir(parents=True, exist_ok=True)
    export_studio(studio, studio_out)
    site_count = export_site_models(site, site_out)
    print(f"AWFUL_DONE:studio=6;site={site_count}")


if __name__ == "__main__":
    main()
