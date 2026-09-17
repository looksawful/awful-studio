"""Probe MAT_DIAGNOSTIC lifecycle across procedural mockup replacement.

This is diagnostic-only tooling for the workstation-smoke blocker discovered on
run-323. It does not render or mutate release source code.
"""
from __future__ import annotations

import addon_utils
import bpy
import importlib
import json
from pathlib import Path
import traceback

MODULE = "bl_ext.user_default.awful_studio"
OUT = Path(r"A:\assets\AWFUL_STUDIO\smoke-profiles\run-323\workstation\material_lifecycle_probe.json")
REPORT = {"status": "failed", "states": [], "blender": bpy.app.version_string}


def state(label, legacy):
    material = legacy.REG.material("MAT_DIAGNOSTIC")
    named = bpy.data.materials.get("MAT_AWFUL_Diagnostic")
    users = []
    target = material or named
    if target is not None:
        for obj in bpy.data.objects:
            data = getattr(obj, "data", None)
            for slot in getattr(data, "materials", ()) if data is not None else ():
                if slot == target:
                    users.append(obj.name)
    REPORT["states"].append({
        "label": label,
        "registry_found": material is not None,
        "named_found": named is not None,
        "material_name": target.name if target else None,
        "material_users": int(target.users) if target else None,
        "object_users": users,
        "all_role_matches": [
            {"name": mat.name, "users": int(mat.users)}
            for mat in bpy.data.materials
            if str(mat.get(legacy.ROLE_KEY, "")) == "MAT_DIAGNOSTIC"
        ],
    })


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    try:
        if not addon_utils.check(MODULE)[1]:
            addon_utils.enable(MODULE, default_set=False)
        ext = importlib.import_module(MODULE)
        product_quality = importlib.import_module(MODULE + ".product_quality")
        legacy = ext.legacy
        scene = bpy.context.scene
        scene.render.engine = "CYCLES"
        bpy.ops.awful.build_studio()
        state("after_build", legacy)
        for key in product_quality.mockup_keys():
            scene.awful_studio.product_mockup = key
            result = bpy.ops.awful.generate_mockup()
            REPORT.setdefault("operators", []).append({"key": key, "result": sorted(result)})
            state(f"after_{key}", legacy)
        REPORT["status"] = "passed"
    except Exception:
        REPORT["traceback"] = traceback.format_exc()
        traceback.print_exc()
    finally:
        OUT.write_text(json.dumps(REPORT, indent=2, ensure_ascii=False), encoding="utf-8")
        print(json.dumps(REPORT, ensure_ascii=False))
    if REPORT["status"] != "passed":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
