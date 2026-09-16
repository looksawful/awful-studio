import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
CONTRACT_PATH = os.path.join(HERE, "material_contract.json")
with open(CONTRACT_PATH, "r", encoding="utf-8") as handle:
    CONTRACT = json.load(handle)
MATERIALS = CONTRACT["materials"]


def material_spec(material_id):
    if material_id not in MATERIALS:
        raise KeyError(f"Unknown material id: {material_id}")
    return MATERIALS[material_id]


def tag_material(material, material_id):
    spec = material_spec(material_id)
    material["awful_material_id"] = material_id
    material["awful_source_mode"] = spec["source_mode"]
    material["awful_geometry_policy"] = spec["geometry_policy"]
    material["awful_delivery_maps"] = ",".join(spec["delivery_maps"])
    material["awful_contract_version"] = CONTRACT["version"]
    return material


def classify_material_name(name):
    n = name.upper()
    if "SCREEN_CONTENT" in n or n == "MAT_SCREEN": return "SCREEN"
    if "DISPLAY_GLASS" in n or "SCREEN_GLASS" in n: return "GLASS_DISPLAY"
    if "BACK_GLASS" in n: return "GLASS_BACK"
    if "OPTICAL" in n or "LENS_GLASS" in n or "FLASH" in n: return "OPTICAL_GLASS"
    if "RUBBER" in n: return "RUBBER"
    if "GAP" in n or "ASSEMBLY" in n: return "GAP"
    if "DECAL" in n or "LOGO" in n or "LEGEND" in n: return "DECAL"
    if "POLYMER" in n or "KEYCAP" in n or "PORT_DARK" in n or "OPTICS_BLACK" in n or "BEZEL" in n: return "POLYMER_BLACK"
    if "ALUMINUM" in n or "METAL" in n or "TRACKPAD" in n or "EDGE" in n: return "ALUMINUM"
    return None


def classify_object_role(name):
    n = name.upper()
    if "CUTTER" in n or n.startswith("CAM_") or n.startswith("LIGHT_"):
        return "development_helper", "exclude_delivery"
    if "SCREEN_CONTENT" in n or "LOGO" in n or "LEGEND" in n or "LABEL" in n:
        return "image_driven", "keep_geometry"
    if "APERTURE" in n or "SPEAKER" in n or "ANTENNA" in n or "MIC" in n or "SCREW" in n or "VENT" in n:
        return "bake_candidate", "bake_if_subpixel"
    if "GAP" in n or "SEAT" in n:
        return "bake_candidate", "bake_when_subpixel"
    return "geometry_keep", "keep_geometry"


def tag_object(obj, material_id=None):
    delivery_role, bake_policy = classify_object_role(obj.name)
    obj["awful_delivery_role"] = delivery_role
    obj["awful_bake_policy"] = bake_policy
    obj["awful_contract_version"] = CONTRACT["version"]
    if material_id:
        obj["awful_material_id"] = material_id
    return obj


def auto_tag_scene(bpy_module):
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
        material_ids = []
        for slot in obj.material_slots:
            if slot.material and "awful_material_id" in slot.material:
                material_ids.append(slot.material["awful_material_id"])
        material_id = material_ids[0] if material_ids else None
        tag_object(obj, material_id)
        report["objects"][obj.name] = {
            "material_id": material_id,
            "delivery_role": obj["awful_delivery_role"],
            "bake_policy": obj["awful_bake_policy"],
        }
        if not material_id and obj["awful_delivery_role"] != "development_helper":
            report["unclassified_objects"].append(obj.name)
    return report

