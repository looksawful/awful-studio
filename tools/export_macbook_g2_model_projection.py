"""Export actual Blender geometry projections for MacBook G2 Apple-reference overlays."""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector


MM_TO_MODEL = 0.001
MODEL_TO_MM = 1000.0


def argv_after_double_dash() -> list[str]:
    return sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []


def convex_hull(points: list[tuple[float, float]]) -> list[list[float]]:
    pts = sorted(set((round(x, 6), round(y, 6)) for x, y in points))
    if len(pts) <= 1:
        return [[x, y] for x, y in pts]

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower = []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    upper = []
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return [[x, y] for x, y in lower[:-1] + upper[:-1]]


def object_points_2d(obj, axes: tuple[int, int], frame=None) -> list[tuple[float, float]]:
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    try:
        transform = evaluated.matrix_world
        if frame is not None:
            transform = frame.matrix_world.inverted() @ transform
        return [
            (
                (transform @ vertex.co)[axes[0]] * MODEL_TO_MM,
                (transform @ vertex.co)[axes[1]] * MODEL_TO_MM,
            )
            for vertex in mesh.vertices
        ]
    finally:
        evaluated.to_mesh_clear()


def object_hull(obj, axes: tuple[int, int], frame=None) -> list[list[float]]:
    return convex_hull(object_points_2d(obj, axes, frame))


def object_center_mm(obj, frame=None) -> list[float]:
    point = obj.matrix_world.translation
    if frame is not None:
        point = frame.matrix_world.inverted() @ point
    return [point.x * MODEL_TO_MM, point.y * MODEL_TO_MM, point.z * MODEL_TO_MM]


def is_descendant_of(obj, ancestor) -> bool:
    parent = obj.parent
    while parent is not None:
        if parent == ancestor:
            return True
        parent = parent.parent
    return False


def visible_meshes():
    return [
        obj
        for obj in bpy.data.objects
        if obj.type == "MESH"
        and not obj.hide_render
        and not obj.get("runtime_only_source")
        and not obj.get("runtime_only")
    ]


def assembly_hull(objects, axes):
    points = []
    for obj in objects:
        points.extend(object_points_2d(obj, axes))
    return convex_hull(points)


def named_hulls(names, axes, frame=None):
    out = {}
    for name in names:
        obj = bpy.data.objects.get(name)
        if obj is not None and obj.type == "MESH":
            out[name] = object_hull(obj, axes, frame)
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv_after_double_dash())

    hinge = bpy.data.objects["CTRL_HINGE"]
    original_rotation = hinge.rotation_euler.copy()

    # Closed-state projections use the actual evaluated assembly.
    hinge.rotation_euler.x = math.pi / 2
    bpy.context.view_layer.update()
    closed_objects = visible_meshes()
    closed = {
        "top_xy": assembly_hull(closed_objects, (0, 1)),
        "front_xz": assembly_hull(closed_objects, (0, 2)),
        "left_yz": assembly_hull(closed_objects, (1, 2)),
        "right_yz": assembly_hull(closed_objects, (1, 2)),
        "bottom_xy": assembly_hull(closed_objects, (0, 1)),
        "logo_xy": named_hulls(["APPLE_LOGO_RELEASE"], (0, 1)),
    }

    # Restore authored G2 open state for deck/display evidence.
    hinge.rotation_euler = original_rotation
    bpy.context.view_layer.update()

    deck_names = [
        obj.name for obj in bpy.data.objects
        if obj.type == "MESH" and (
            obj.get("key_label") is not None
            or obj.name in {
                "KEYBOARD_WELL",
                "TRACKPAD",
                "TOUCH_ID",
                "SPEAKER_MASTER_PROXY_L",
                "SPEAKER_MASTER_PROXY_R",
            }
        )
    ]
    deck = named_hulls(deck_names, (0, 1))

    bottom_feature_names = [
        *(f"FOOT_{i:02d}" for i in range(1, 5)),
        *(f"BOTTOM_SCREW_{i:02d}" for i in range(8)),
    ]
    bottom_features = {
        name: {
            "center_xyz_mm": object_center_mm(bpy.data.objects[name]),
            "hull_xy": object_hull(bpy.data.objects[name], (0, 1)),
        }
        for name in bottom_feature_names
        if bpy.data.objects.get(name) is not None
    }

    port_names = ["MAGSAFE", "TB_LEFT_1", "TB_LEFT_2", "HEADPHONE", "HDMI", "SDXC", "TB_RIGHT"]
    ports = {
        name: {
            "center_xyz_mm": object_center_mm(bpy.data.objects[name]),
            "left_yz": object_hull(bpy.data.objects[name], (1, 2)),
            "right_yz": object_hull(bpy.data.objects[name], (1, 2)),
        }
        for name in port_names
        if bpy.data.objects.get(name) is not None
    }

    display_names = ["DISPLAY_SURROUND_VISUAL", "SCREEN_CONTENT", "CAMERA_NOTCH", "FACETIME_CAMERA"]
    display = {
        name: {
            "center_xyz_mm": object_center_mm(bpy.data.objects[name], hinge),
            "hull_xz": object_hull(bpy.data.objects[name], (0, 2), hinge),
        }
        for name in display_names
        if bpy.data.objects.get(name) is not None
    }

    hinge_names = ["HINGE_COVER_L", "HINGE_COVER_R", "HINGE_BARREL_L", "HINGE_BARREL_R"]
    hinge_parts = {
        name: {
            "center_xyz_mm": object_center_mm(bpy.data.objects[name]),
            "top_xy": object_hull(bpy.data.objects[name], (0, 1)),
            "front_xz": object_hull(bpy.data.objects[name], (0, 2)),
            "geometry_authority": bpy.data.objects[name].get("geometry_authority", ""),
        }
        for name in hinge_names
        if bpy.data.objects.get(name) is not None
    }

    payload = {
        "schema_version": 1,
        "source": "actual evaluated Blender geometry",
        "blender_version": bpy.app.version_string,
        "blend_file": bpy.data.filepath,
        "open_angle_deg": bpy.data.objects["CTRL_HINGE"].get("open_angle_deg"),
        "closed": closed,
        "deck": deck,
        "bottom_features": bottom_features,
        "ports": ports,
        "display": display,
        "hinge": hinge_parts,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print("MACBOOK_G2_MODEL_PROJECTION", json.dumps({
        "out": str(args.out),
        "blender_version": bpy.app.version_string,
        "deck_objects": len(deck),
        "ports": len(ports),
        "display_objects": len(display),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
