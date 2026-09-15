from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONTRACT = json.loads((HERE / "material_contract.json").read_text(encoding="utf-8"))
MATERIALS = CONTRACT["materials"]


def material_spec(material_id: str) -> dict:
    if material_id not in MATERIALS:
        raise KeyError(f"Unknown material id: {material_id}")
    return MATERIALS[material_id]


def classify_material_name(name: str) -> str | None:
    value = name.upper()
    if "SCREEN_CONTENT" in value or value == "MAT_SCREEN":
        return "SCREEN"
    if "DISPLAY_GLASS" in value or "SCREEN_GLASS" in value:
        return "GLASS_DISPLAY"
    if "BACK_GLASS" in value:
        return "GLASS_BACK"
    if "OPTICAL" in value or "LENS_GLASS" in value or "FLASH" in value:
        return "OPTICAL_GLASS"
    if "RUBBER" in value:
        return "RUBBER"
    if "GAP" in value or "ASSEMBLY" in value:
        return "GAP"
    if "DECAL" in value or "LOGO" in value or "LEGEND" in value:
        return "DECAL"
    if any(token in value for token in ("POLYMER", "KEYCAP", "PORT_DARK", "OPTICS_BLACK", "BEZEL")):
        return "POLYMER_BLACK"
    if any(token in value for token in ("ALUMINUM", "METAL", "TRACKPAD", "EDGE")):
        return "ALUMINUM"
    return None


def classify_object_role(name: str) -> tuple[str, str]:
    value = name.upper()
    if "CUTTER" in value or value.startswith(("CAM_", "LIGHT_")):
        return "development_helper", "exclude_delivery"
    if any(token in value for token in ("SCREEN_CONTENT", "LOGO", "LEGEND", "LABEL")):
        return "image_driven", "keep_geometry"
    if any(token in value for token in ("APERTURE", "SPEAKER", "ANTENNA", "MIC", "SCREW", "VENT")):
        return "bake_candidate", "bake_if_subpixel"
    if "GAP" in value or "SEAT" in value:
        return "bake_candidate", "bake_when_subpixel"
    return "geometry_keep", "keep_geometry"


def tag_material(material, material_id: str):
    spec = material_spec(material_id)
    material["awful_material_id"] = material_id
    material["awful_source_mode"] = spec["source_mode"]
    material["awful_geometry_policy"] = spec["geometry_policy"]
    material["awful_delivery_maps"] = ",".join(spec["delivery_maps"])
    material["awful_contract_version"] = CONTRACT["version"]
    return material


def tag_object(obj, material_id: str | None = None):
    delivery_role, bake_policy = classify_object_role(obj.name)
    obj["awful_delivery_role"] = delivery_role
    obj["awful_bake_policy"] = bake_policy
    obj["awful_contract_version"] = CONTRACT["version"]
    if material_id:
        obj["awful_material_id"] = material_id
    return obj


def auto_tag_scene(bpy_module) -> dict:
    report = {"materials": {}, "objects": {}, "unclassified_materials": [], "unclassified_objects": []}
    for material in bpy_module.data.materials:
        material_id = classify_material_name(material.name)
        if material_id:
            tag_material(material, material_id)
            report["materials"][material.name] = material_id
        else:
            report["unclassified_materials"].append(material.name)
    for obj in bpy_module.data.objects:
        if obj.type != "MESH":
            continue
        material_ids = [slot.material.get("awful_material_id") for slot in obj.material_slots if slot.material and slot.material.get("awful_material_id")]
        material_id = material_ids[0] if material_ids else None
        tag_object(obj, material_id)
        report["objects"][obj.name] = {"material_id": material_id, "delivery_role": obj["awful_delivery_role"], "bake_policy": obj["awful_bake_policy"]}
        if not material_id and obj["awful_delivery_role"] != "development_helper":
            report["unclassified_objects"].append(obj.name)
    return report
