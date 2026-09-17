"""Non-render workstation smoke for an installed AWFUL STUDIO 0.0.17 candidate.

Run with Blender 5.2.1 from the user's normal profile after installing the exact
candidate ZIP. The script intentionally does not render. It checks GPU/backend
visibility, Build, all six procedural mockups, Fast/Quality preview policies,
Post Pipeline, save/reopen, Rebuild, Remove, and survival of unmanaged user data.
"""
from __future__ import annotations

import addon_utils
import bpy
import importlib
import json
from pathlib import Path
import traceback

MODULE = "bl_ext.user_default.awful_studio"
WORK = Path(r"A:\assets\AWFUL_STUDIO\smoke-profiles\run-323\workstation")
REPORT = {
    "status": "failed",
    "module": MODULE,
    "blender": bpy.app.version_string,
    "checks": [],
    "render_invoked": False,
}


def check(name, condition, value=None):
    REPORT["checks"].append({"name": name, "passed": bool(condition), "value": value})
    if not condition:
        raise AssertionError(name)


def run_operator(idname):
    namespace, name = idname.split(".", 1)
    return getattr(getattr(bpy.ops, namespace), name)()


def main():
    WORK.mkdir(parents=True, exist_ok=True)
    try:
        if not addon_utils.check(MODULE)[1]:
            addon_utils.enable(MODULE, default_set=False)
        check("exact extension enabled", addon_utils.check(MODULE)[1])

        ext = importlib.import_module(MODULE)
        product_quality = importlib.import_module(MODULE + ".product_quality")
        performance = importlib.import_module(MODULE + ".runtime_performance")
        legacy = ext.legacy
        check("candidate version 0.0.17", tuple(ext.VERSION) == (0, 0, 17), tuple(ext.VERSION))

        scene = bpy.context.scene
        scene.render.engine = "CYCLES"
        cycles_addon = bpy.context.preferences.addons.get("cycles")
        prefs = cycles_addon.preferences if cycles_addon else None
        if prefs:
            try:
                prefs.get_devices()
            except Exception:
                pass
        compute_type = str(getattr(prefs, "compute_device_type", "NONE") or "NONE") if prefs else "NONE"
        devices = [
            {"name": str(d.name), "type": str(d.type), "use": bool(d.use)}
            for d in (getattr(prefs, "devices", []) if prefs else [])
        ]
        REPORT["cycles_before"] = {
            "compute_device_type": compute_type,
            "devices": devices,
            "scene_device": str(scene.cycles.device),
        }
        check("GPU backend configured", compute_type not in {"NONE", ""}, REPORT["cycles_before"])
        check(
            "usable GPU device configured",
            any(d["use"] and d["type"] in {"OPTIX", "CUDA", "HIP", "ONEAPI", "METAL"} for d in devices),
            devices,
        )

        scene.cycles.device = "GPU"
        final_before = {
            "device": str(scene.cycles.device),
            "samples": int(scene.cycles.samples),
            "resolution_x": scene.render.resolution_x,
            "resolution_y": scene.render.resolution_y,
            "resolution_percentage": scene.render.resolution_percentage,
        }

        result = bpy.ops.awful.build_studio()
        check("Build Studio finished", result == {"FINISHED"}, sorted(result))
        check("managed studio built", bool(scene.awful_state.built), scene.awful_state.last_operation)
        diagnostics = performance.collect_diagnostics(legacy, scene)
        REPORT["diagnostics_after_build"] = diagnostics
        check("Build preserves GPU scene device", diagnostics["scene_device"] == "GPU", diagnostics)
        check("Build sees configured backend", diagnostics["compute_device_type"] == compute_type, diagnostics)
        check("managed lights present", diagnostics["light_count"] > 0, diagnostics["light_count"])

        mockups = []
        for key in product_quality.mockup_keys():
            scene.awful_studio.product_mockup = key
            result = bpy.ops.awful.generate_mockup()
            mockups.append({"key": key, "result": sorted(result)})
            check(f"mockup {key}", result == {"FINISHED"}, sorted(result))
        REPORT["mockups"] = mockups
        check("six mockups exercised", len(mockups) == 6, [item["key"] for item in mockups])

        fast = performance.apply_preview_profile(scene, "FAST")
        check("Fast Preview applied", int(scene.cycles.preview_samples) == int(fast["samples"]), fast)
        quality = performance.apply_preview_profile(scene, "QUALITY")
        check("Quality Preview applied", int(scene.cycles.preview_samples) == int(quality["samples"]), quality)
        final_after = {
            "device": str(scene.cycles.device),
            "samples": int(scene.cycles.samples),
            "resolution_x": scene.render.resolution_x,
            "resolution_y": scene.render.resolution_y,
            "resolution_percentage": scene.render.resolution_percentage,
        }
        check("preview modes preserve final render/device", final_after == final_before, {"before": final_before, "after": final_after})

        post_id = legacy.AWFUL_OT_BuildPostPipeline.bl_idname
        result = run_operator(post_id)
        check("Setup Post Pipeline finished", result == {"FINISHED"}, {"id": post_id, "result": sorted(result)})
        check("Post Pipeline ready flag set", bool(scene.get(legacy.POST_PIPELINE_KEY, False)))
        result = run_operator(post_id)
        check("Post Pipeline rebuild finished", result == {"FINISHED"}, sorted(result))

        user_mesh = bpy.data.meshes.new("AWFUL_SMOKE_USER_MESH")
        user_object = bpy.data.objects.new("AWFUL_SMOKE_USER_OBJECT", user_mesh)
        scene.collection.objects.link(user_object)
        user_object.location = (1.234, 2.345, 3.456)

        blend = WORK / "awful_0017_workstation_smoke.blend"
        bpy.ops.wm.save_as_mainfile(filepath=str(blend))
        check("smoke blend saved", blend.exists(), str(blend))
        bpy.ops.wm.open_mainfile(filepath=str(blend), use_scripts=False)
        scene = bpy.context.scene
        check("save/reopen retains built studio", bool(scene.awful_state.built))
        check("save/reopen retains Post Pipeline", bool(scene.get(legacy.POST_PIPELINE_KEY, False)))
        check("unmanaged marker survives reopen", bpy.data.objects.get("AWFUL_SMOKE_USER_OBJECT") is not None)
        check("save/reopen keeps GPU scene device", str(scene.cycles.device) == "GPU", str(scene.cycles.device))

        result = bpy.ops.awful.rebuild_studio()
        check("Rebuild Studio finished", result == {"FINISHED"}, sorted(result))
        check("unmanaged marker survives Rebuild", bpy.data.objects.get("AWFUL_SMOKE_USER_OBJECT") is not None)
        result = bpy.ops.awful.remove_studio()
        check("Remove Studio finished", result == {"FINISHED"}, sorted(result))
        check("unmanaged marker survives Remove", bpy.data.objects.get("AWFUL_SMOKE_USER_OBJECT") is not None)
        check("managed CYC removed", legacy.REG.object("CYC") is None)
        REPORT["status"] = "passed"
    except Exception:
        REPORT["traceback"] = traceback.format_exc()
        traceback.print_exc()
    finally:
        WORK.mkdir(parents=True, exist_ok=True)
        output = WORK / "normal_profile_smoke.json"
        output.write_text(json.dumps(REPORT, indent=2, ensure_ascii=False), encoding="utf-8")
        print("AWFUL_SMOKE_REPORT", output)
        print(json.dumps(REPORT, ensure_ascii=False))

    if REPORT["status"] != "passed":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
