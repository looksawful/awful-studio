import json
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parent
SPEC = json.loads((ROOT / "spec.json").read_text(encoding="utf-8"))
OUT = ROOT / "generated" / "validation.json"


def dims_mm(name):
    obj = bpy.data.objects[name]
    return [round(value * 1000.0, 3) for value in obj.dimensions]


def collection_bounds_mm(name):
    col = bpy.data.collections[name]
    points = []
    for obj in col.all_objects:
        if obj.type != "MESH" or obj.name.endswith("REFERENCE_ENVELOPE"):
            continue
        for corner in obj.bound_box:
            points.append(obj.matrix_world @ Vector(corner))
    mins = [min(p[i] for p in points) for i in range(3)]
    maxs = [max(p[i] for p in points) for i in range(3)]
    return [round((maxs[i] - mins[i]) * 1000.0, 3) for i in range(3)]

def close(actual, expected, tol=1.0):
    return all(abs(a - e) <= tol for a, e in zip(actual, expected))


def check(condition, label, details, results):
    results.append({"check": label, "pass": bool(condition), "details": details})


def main():
    results = []
    required = {
        "ROOT_AWFUL_STUDIO_RIG",
        "ROOT_SUPPORT_CSTAND",
        "ROOT_FIX_PROFOTO_D1_500",
        "ROOT_MOD_PROFOTO_MAGNUM",
        "ROOT_ACC_SANDBAG",
        "MOUNT_SUPPORT",
        "MOUNT_FIXTURE",
        "MOUNT_MODIFIER",
        "EMITTER_ORIGIN",
        "LIGHT_TARGET",
        "LIGHT_D1_NATIVE",
        "D1_REFERENCE_ENVELOPE",
        "MAGNUM_REFERENCE_ENVELOPE",
        "D1_GLASS_PLATE",
        "D1_FLASHTUBE",
        "D1_MODELING_LAMP",
        "D1_SYNC_PORT",
        "D1_AC_CONNECTOR",
        "D1_FUSE_HOLDER",
        "D1_UMBRELLA_TUBE",
        "D1_ZOOM_TICK_01",
        "D1_YOKE_BAND",
        "D1_SIDE_VENT_L_01",
        "D1_SIDE_VENT_R_01",
        "D1_REAR_DISPLAY",
    }
    missing = sorted(required - set(bpy.data.objects.keys()))
    check(not missing, "required_objects", {"missing": missing}, results)

    d1 = dims_mm("D1_REFERENCE_ENVELOPE")
    check(close(d1, [130, 300, 170]), "d1_envelope_mm", {"actual": d1}, results)
    d1_visible = collection_bounds_mm("AS_FIX_PROFOTO_D1_500")
    check(d1_visible[1] <= 301.0, "d1_visible_depth_mm", {"actual": d1_visible[1]}, results)
    magnum = dims_mm("MAGNUM_REFERENCE_ENVELOPE")
    check(
        close(sorted(magnum), [265, 345, 345], tol=1.0),
        "magnum_envelope_mm",
        {"actual": magnum, "sorted": sorted(magnum)},
        results,
    )
    magnum_materials = {
        name: [slot.material.name for slot in bpy.data.objects[name].material_slots if slot.material]
        for name in ("MAGNUM_OUTER_SHELL", "MAGNUM_INNER_REFLECTOR",
                     "MAGNUM_COLLAR_REAR", "MAGNUM_COLLAR_FRONT", "MAGNUM_FRONT_RIM")
    }
    check("MAT_BLACK_POWDER" in magnum_materials["MAGNUM_OUTER_SHELL"],
          "magnum_outer_black", magnum_materials, results)
    check("MAT_REFLECTOR_SILVER" in magnum_materials["MAGNUM_INNER_REFLECTOR"],
          "magnum_inner_silver", magnum_materials, results)
    check("MAT_BLACK_POWDER" in magnum_materials["MAGNUM_COLLAR_FRONT"],
          "magnum_collar_black", magnum_materials, results)
    check("MAT_ALUMINUM" in magnum_materials["MAGNUM_FRONT_RIM"],
          "magnum_front_rim_silver", magnum_materials, results)
    magnum_visible = collection_bounds_mm("AS_MOD_PROFOTO_MAGNUM")
    check(
        close(sorted(magnum_visible), [265, 345, 345], tol=1.5),
        "magnum_visible_assembly_bounds_mm",
        {"actual": magnum_visible, "sorted": sorted(magnum_visible)},
        results,
    )
    mount_z = round(bpy.data.objects["MOUNT_SUPPORT"].matrix_world.translation.z * 1000, 3)
    check(abs(mount_z - 1750.0) <= 10.0, "support_mount_height_mm", {"actual": mount_z}, results)
    support_bounds = collection_bounds_mm("AS_SUPPORT_CSTAND_01")
    check(max(support_bounds[0], support_bounds[1]) <= 950.0,
          "support_footprint_mm", {"actual": support_bounds[:2]}, results)
    riser_diameters = [dims_mm(name)[0] for name in
                       ("CSTAND_RISER_01", "CSTAND_RISER_02", "CSTAND_RISER_03")]
    check(close(riser_diameters, [35.0, 30.0, 25.0], tol=0.2),
          "support_tube_diameters_mm", {"actual": riser_diameters}, results)
    leg_diameter = dims_mm("CSTAND_LEG_1")[0]
    check(abs(leg_diameter - 25.0) <= 0.2,
          "support_leg_diameter_mm", {"actual": leg_diameter}, results)
    pouch_mods = {name: {m.name for m in bpy.data.objects[name].modifiers}
                  for name in ("SANDBAG_POUCH_1", "SANDBAG_POUCH_2")}
    check(all({"SOFT_BEVEL", "SOFT_SUBDIV", "MICRO_SAG"} <= mods for mods in pouch_mods.values()),
          "sandbag_soft_surface_modifiers", {k: sorted(v) for k, v in pouch_mods.items()}, results)
    scene = bpy.context.scene
    check(scene.unit_settings.system == "METRIC", "metric_units", {"system": scene.unit_settings.system}, results)

    absolute_images = []
    for image in bpy.data.images:
        path = image.filepath or ""
        if path and Path(bpy.path.abspath(path)).is_absolute() and not path.startswith("//"):
            absolute_images.append({"name": image.name, "path": path})
    check(not absolute_images, "no_absolute_image_paths", absolute_images, results)

    root = bpy.data.objects.get("ROOT_AWFUL_STUDIO_RIG")
    check(root and root.get("awful_asset_id") == "AS_RIG_STUDIO_V01",
          "rig_metadata", {"asset_id": root.get("awful_asset_id") if root else None}, results)
    payload = {
        "asset_id": "AS_RIG_STUDIO_V01",
        "blender_version": bpy.app.version_string,
        "object_count": len(bpy.data.objects),
        "mesh_count": len(bpy.data.meshes),
        "material_count": len(bpy.data.materials),
        "visible_bounds_mm": {"d1": collection_bounds_mm("AS_FIX_PROFOTO_D1_500"), "magnum": collection_bounds_mm("AS_MOD_PROFOTO_MAGNUM")},
        "checks": results,
        "pass": all(item["pass"] for item in results),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    if not payload["pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
