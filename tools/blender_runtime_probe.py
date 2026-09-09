"""AWFUL STUDIO Blender runtime probe.

Run through Blender, not normal Python:

    blender --background --factory-startup --python tools/blender_runtime_probe.py -- \
        --source C:/path/to/awful_studio_v4_2_gpu_perf.py \
        --output C:/path/to/evidence/runtime-probe.json

This probe deliberately does not modify AWFUL business behavior. It executes the
selected historical source as __main__, records runtime state, performs one
rebuild, and proves that an unrelated unmanaged sentinel survives.
"""

from __future__ import annotations

import argparse
import json
import math
import pathlib
import sys
import time
import traceback
from typing import Any

import bpy


MANAGED_KEY = "awful_managed"
ROLE_KEY = "awful_role"
POST_PIPELINE_KEY = "awful_post_pipeline_enabled"
SENTINEL_NAME = "AWFUL_PROBE_UNMANAGED_SENTINEL"


def parse_args() -> argparse.Namespace:
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1 :]
    else:
        argv = []
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args(argv)


def safe_json(value: Any) -> Any:
    if value is None or isinstance(value, (bool, int, float, str)):
        if isinstance(value, float) and not math.isfinite(value):
            return str(value)
        return value
    if isinstance(value, (list, tuple)):
        return [safe_json(v) for v in value]
    if isinstance(value, dict):
        return {str(k): safe_json(v) for k, v in value.items()}
    return str(value)


def object_record(obj: bpy.types.Object) -> dict[str, Any]:
    return {
        "name": obj.name,
        "type": obj.type,
        "managed": bool(obj.get(MANAGED_KEY, False)),
        "role": obj.get(ROLE_KEY),
        "hide_render": bool(obj.hide_render),
        "hide_viewport": bool(obj.hide_viewport),
        "location": [float(v) for v in obj.location],
        "dimensions": [float(v) for v in obj.dimensions],
        "parent": obj.parent.name if obj.parent else None,
    }


def scene_snapshot() -> dict[str, Any]:
    scene = bpy.context.scene
    objects = list(bpy.data.objects)
    managed = [obj for obj in objects if bool(obj.get(MANAGED_KEY, False))]
    roles: dict[str, list[str]] = {}
    for obj in managed:
        role = obj.get(ROLE_KEY)
        if role:
            roles.setdefault(str(role), []).append(obj.name)

    lights = []
    for obj in objects:
        if obj.type != "LIGHT":
            continue
        data = obj.data
        lights.append(
            {
                "name": obj.name,
                "role": obj.get(ROLE_KEY),
                "light_type": getattr(data, "type", None),
                "energy": float(getattr(data, "energy", 0.0)),
                "color": [float(v) for v in getattr(data, "color", (0, 0, 0))],
                "hide_render": bool(obj.hide_render),
            }
        )

    cameras = [object_record(obj) for obj in objects if obj.type == "CAMERA"]

    cycles = getattr(scene, "cycles", None)
    return {
        "blender_version": bpy.app.version_string,
        "engine": scene.render.engine,
        "cycles_device": getattr(cycles, "device", None) if cycles else None,
        "resolution": [scene.render.resolution_x, scene.render.resolution_y],
        "resolution_percentage": scene.render.resolution_percentage,
        "preview_pixel_size": getattr(scene.render, "preview_pixel_size", None),
        "frame_range": [scene.frame_start, scene.frame_end],
        "object_count": len(objects),
        "managed_object_count": len(managed),
        "roles": {key: sorted(value) for key, value in sorted(roles.items())},
        "lights": sorted(lights, key=lambda item: item["name"]),
        "cameras": sorted(cameras, key=lambda item: item["name"]),
        "active_camera": scene.camera.name if scene.camera else None,
        "world": scene.world.name if scene.world else None,
        "post_pipeline_enabled": bool(scene.get(POST_PIPELINE_KEY, False)),
        "sentinel_present": SENTINEL_NAME in bpy.data.objects,
    }


def make_unmanaged_sentinel() -> None:
    mesh = bpy.data.meshes.new(f"{SENTINEL_NAME}_MESH")
    obj = bpy.data.objects.new(SENTINEL_NAME, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.location = (5.123, -4.321, 2.222)
    obj["probe_unmanaged"] = True


def execute_source(source_path: pathlib.Path) -> dict[str, Any]:
    namespace: dict[str, Any] = {"__name__": "__main__", "__file__": str(source_path)}
    code = compile(source_path.read_text(encoding="utf-8"), str(source_path), "exec")
    exec(code, namespace, namespace)
    return namespace


def main() -> int:
    args = parse_args()
    source = pathlib.Path(args.source).expanduser().resolve()
    output = pathlib.Path(args.output).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    report: dict[str, Any] = {
        "probe_version": 1,
        "source": str(source),
        "source_exists": source.exists(),
        "status": "failed",
    }

    started = time.perf_counter()
    try:
        if not source.is_file():
            raise FileNotFoundError(source)

        make_unmanaged_sentinel()
        report["sentinel_before_build"] = SENTINEL_NAME in bpy.data.objects

        namespace = execute_source(source)
        report["initial_build_seconds"] = time.perf_counter() - started
        report["initial"] = scene_snapshot()

        build_studio = namespace.get("build_studio")
        if not callable(build_studio):
            raise RuntimeError("Source did not expose callable build_studio().")

        rebuild_started = time.perf_counter()
        build_studio(True)
        report["rebuild_seconds"] = time.perf_counter() - rebuild_started
        report["after_rebuild"] = scene_snapshot()

        report["checks"] = {
            "blender_5_2": tuple(bpy.app.version[:2]) == (5, 2),
            "sentinel_survived_initial_build": bool(report["initial"]["sentinel_present"]),
            "sentinel_survived_rebuild": bool(report["after_rebuild"]["sentinel_present"]),
            "managed_objects_exist": report["after_rebuild"]["managed_object_count"] > 0,
            "camera_exists": bool(report["after_rebuild"]["cameras"]),
            "lights_exist": bool(report["after_rebuild"]["lights"]),
            "post_pipeline_default_off": not bool(report["after_rebuild"]["post_pipeline_enabled"]),
        }
        report["status"] = "passed" if all(report["checks"].values()) else "failed"
    except Exception as exc:  # Blender probe should always leave diagnostics.
        report["error"] = f"{type(exc).__name__}: {exc}"
        report["traceback"] = traceback.format_exc()
    finally:
        report["total_seconds"] = time.perf_counter() - started
        output.write_text(json.dumps(safe_json(report), indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"AWFUL runtime probe: {report['status']} -> {output}")

    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
