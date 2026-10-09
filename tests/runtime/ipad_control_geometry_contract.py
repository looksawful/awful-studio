"""Blender 5.2 contract for iPad Pro M5 physical controls."""
import argparse
import json
import sys

import bpy
from mathutils import Vector

MM = 1000.0
# Apple M5 Dimensional Drawings, 2025-12-08:
# developer.apple.com/download/files/accessories/dimensional-drawings/ipad-pro-11-inch-m5.pdf
# developer.apple.com/download/files/accessories/dimensional-drawings/ipad-pro-13-inch-m5.pdf
EXPECTED = {
    "11": {"profile": 2.26, "vol_len": 10.06, "vol_up_top": 19.33, "vol_down_top": 31.39},
    "13": {"profile": 2.26, "vol_len": 10.06, "vol_up_top": 19.33, "vol_down_top": 31.39},
}


def bounds_mm(obj):
    points = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    return {
        "xmin": min(p.x for p in points) * MM,
        "xmax": max(p.x for p in points) * MM,
        "ymin": min(p.y for p in points) * MM,
        "ymax": max(p.y for p in points) * MM,
        "zmin": min(p.z for p in points) * MM,
        "zmax": max(p.z for p in points) * MM,
    }


def close(actual, expected, tolerance=0.06):
    return abs(actual - expected) <= tolerance


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--size", choices=sorted(EXPECTED), required=True)
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
    spec = EXPECTED[args.size]
    body = bounds_mm(bpy.data.objects["BODY_ALUMINUM"])
    report = {"size": args.size, "blender": bpy.app.version_string, "checks": []}

    for name in ("TOP_BUTTON", "VOL_UP", "VOL_DOWN"):
        box = bounds_mm(bpy.data.objects[name])
        profile = box["ymax"] - box["ymin"]
        report["checks"].append(
            {"name": f"{name} profile", "actual": profile, "expected": spec["profile"],
             "passed": close(profile, spec["profile"])}
        )

    for name, key in (("VOL_UP", "vol_up_top"), ("VOL_DOWN", "vol_down_top")):
        box = bounds_mm(bpy.data.objects[name])
        center_z = (box["zmin"] + box["zmax"]) * 0.5
        from_top = body["zmax"] - center_z
        length = box["zmax"] - box["zmin"]
        report["checks"].append(
            {"name": f"{name} from top", "actual": from_top, "expected": spec[key],
             "passed": close(from_top, spec[key])}
        )
        report["checks"].append(
            {"name": f"{name} length", "actual": length, "expected": spec["vol_len"],
             "passed": close(length, spec["vol_len"], 0.08)}
        )

    print("IPAD_CONTROL_CONTRACT " + json.dumps(report, sort_keys=True))
    failures = [check for check in report["checks"] if not check["passed"]]
    if failures:
        print("IPAD_CONTROL_FAILURES " + json.dumps(failures, sort_keys=True))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
