import json
import os
import sys
import bpy
from mathutils import Vector

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
COMMON = os.path.join(ROOT, "assets", "device_mockups", "common")
if COMMON not in sys.path:
    sys.path.insert(0, COMMON)
import material_pipeline as mp

OUT_DIR = os.path.join(ROOT, "assets", "device_mockups", "shared", "materials")
OUT_BLEND = os.path.join(OUT_DIR, "device_material_masters.blend")
OUT_PREVIEW = os.path.join(OUT_DIR, "device_material_masters_preview.png")
OUT_REPORT = os.path.join(OUT_DIR, "device_material_masters_validation.json")
os.makedirs(OUT_DIR, exist_ok=True)


def clean():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for m in list(bpy.data.materials):
        bpy.data.materials.remove(m)


def new_mat(material_id):
    name = mp.material_spec(material_id)["canonical_name"]
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.use_fake_user = True
    mp.tag_material(mat, material_id)
    mat["awful_procedural_master"] = True
    return mat


def bsdf(mat):
    return mat.node_tree.nodes.get("Principled BSDF")


def set_input(shader, name, value):
    socket = shader.inputs.get(name)
    if socket is not None:
        socket.default_value = value


def add_micro_surface(mat, scale=650.0, rough_min=0.20, rough_max=0.28, bump_strength=0.04, bump_distance=0.000025):
    nt = mat.node_tree
    shader = bsdf(mat)
    tex = nt.nodes.new("ShaderNodeTexNoise")
    tex.name = "MICRO_SURFACE_NOISE"
    tex.inputs["Scale"].default_value = scale
    tex.inputs["Detail"].default_value = 2.0
    tex.inputs["Roughness"].default_value = 0.55
    mapper = nt.nodes.new("ShaderNodeMapRange")
    mapper.name = "ROUGHNESS_RANGE"
    mapper.inputs["From Min"].default_value = 0.0
    mapper.inputs["From Max"].default_value = 1.0
    mapper.inputs["To Min"].default_value = rough_min
    mapper.inputs["To Max"].default_value = rough_max
    nt.links.new(tex.outputs["Fac"], mapper.inputs["Value"])
    nt.links.new(mapper.outputs["Result"], shader.inputs["Roughness"])
    bump = nt.nodes.new("ShaderNodeBump")
    bump.name = "MICRO_NORMAL"
    bump.inputs["Strength"].default_value = bump_strength
    bump.inputs["Distance"].default_value = bump_distance
    nt.links.new(tex.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], shader.inputs["Normal"])


def make_aluminum():
    mat = new_mat("ALUMINUM")
    sh = bsdf(mat)
    set_input(sh, "Base Color", (0.34, 0.35, 0.37, 1.0))
    set_input(sh, "Metallic", 1.0)
    add_micro_surface(mat, scale=900.0, rough_min=0.18, rough_max=0.26, bump_strength=0.035, bump_distance=0.000018)
    mat["awful_mid_detail"] = "procedural_micrograin"
    return mat


def make_glass(material_id, color, roughness, ior=1.46, transmission=1.0):
    mat = new_mat(material_id)
    sh = bsdf(mat)
    set_input(sh, "Base Color", (*color, 1.0))
    set_input(sh, "Roughness", roughness)
    set_input(sh, "IOR", ior)
    set_input(sh, "Transmission Weight", transmission)
    return mat


def make_back_glass():
    mat = new_mat("GLASS_BACK")
    sh = bsdf(mat)
    set_input(sh, "Base Color", (0.20, 0.21, 0.23, 1.0))
    set_input(sh, "Roughness", 0.28)
    set_input(sh, "IOR", 1.46)
    add_micro_surface(mat, scale=520.0, rough_min=0.24, rough_max=0.34, bump_strength=0.025, bump_distance=0.000012)
    return mat


def make_polymer(material_id, color, roughness, scale, bump_strength):
    mat = new_mat(material_id)
    sh = bsdf(mat)
    set_input(sh, "Base Color", (*color, 1.0))
    set_input(sh, "Metallic", 0.0)
    add_micro_surface(mat, scale=scale, rough_min=max(0.0, roughness-0.05), rough_max=min(1.0, roughness+0.05), bump_strength=bump_strength, bump_distance=0.000020)
    return mat


def make_screen():
    mat = new_mat("SCREEN")
    nt = mat.node_tree
    sh = bsdf(mat)
    image = bpy.data.images.new("SCREEN_PLACEHOLDER", width=4, height=4)
    image.generated_color = (0.004, 0.006, 0.010, 1.0)
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.name = "SCREEN_IMAGE"
    tex.label = "Replace this image"
    tex.image = image
    nt.links.new(tex.outputs["Color"], sh.inputs["Base Color"])
    if sh.inputs.get("Emission Color"):
        nt.links.new(tex.outputs["Color"], sh.inputs["Emission Color"])
        sh.inputs["Emission Strength"].default_value = 0.65
    sh.inputs["Roughness"].default_value = 0.18
    mat["awful_image_node"] = "SCREEN_IMAGE"
    mat["awful_replaceable_image"] = True
    return mat


def make_decal():
    mat = new_mat("DECAL")
    nt = mat.node_tree
    sh = bsdf(mat)
    image = bpy.data.images.new("DECAL_PLACEHOLDER", width=4, height=4, alpha=True)
    image.generated_color = (1.0, 1.0, 1.0, 0.0)
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.name = "DECAL_IMAGE"
    tex.label = "Replace decal image"
    tex.image = image
    nt.links.new(tex.outputs["Color"], sh.inputs["Base Color"])
    nt.links.new(tex.outputs["Alpha"], sh.inputs["Alpha"])
    sh.inputs["Roughness"].default_value = 0.35
    mat["awful_image_node"] = "DECAL_IMAGE"
    mat["awful_replaceable_image"] = True
    return mat


def make_gap():
    mat = new_mat("GAP")
    sh = bsdf(mat)
    set_input(sh, "Base Color", (0.006, 0.007, 0.009, 1.0))
    set_input(sh, "Roughness", 0.42)
    return mat


def add_preview_swatch(name, mat, x, z):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=32, radius=0.045, location=(x, 0, z))
    obj = bpy.context.object
    obj.name = f"SWATCH_{name}"
    obj.data.materials.append(mat)
    return obj


def setup_preview(materials):
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1200
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = False
    scene.world.color = (0.015, 0.015, 0.018)
    ids = list(materials.keys())
    coords = [(-0.12,0.10),(0,0.10),(0.12,0.10),(-0.12,0),(0,0),(0.12,0),(-0.12,-0.10),(0,-0.10),(0.12,-0.10)]
    for material_id, (x,z) in zip(ids, coords):
        add_preview_swatch(material_id, materials[material_id], x, z)
    bpy.ops.object.light_add(type="AREA", location=(0.18,-0.22,0.22))
    key = bpy.context.object
    key.data.energy = 850
    key.data.shape = "DISK"
    key.data.size = 0.22
    key.rotation_euler = (Vector((0,0,0))-key.location).to_track_quat("-Z","Y").to_euler()
    bpy.ops.object.light_add(type="AREA", location=(-0.20,-0.08,0.08))
    fill = bpy.context.object
    fill.data.energy = 380
    fill.data.size = 0.18
    fill.rotation_euler = (Vector((0,0,0))-fill.location).to_track_quat("-Z","Y").to_euler()
    bpy.ops.object.camera_add(location=(0,-0.62,0.015))
    cam = bpy.context.object
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = 0.42
    cam.rotation_euler = (Vector((0,0,0))-cam.location).to_track_quat("-Z","Y").to_euler()
    scene.camera = cam
    scene.render.filepath = OUT_PREVIEW
    bpy.ops.render.render(write_still=True)


def main():
    clean()
    materials = {
        "ALUMINUM": make_aluminum(),
        "GLASS_DISPLAY": make_glass("GLASS_DISPLAY", (0.012,0.016,0.022), 0.035, 1.46, 1.0),
        "GLASS_BACK": make_back_glass(),
        "OPTICAL_GLASS": make_glass("OPTICAL_GLASS", (0.006,0.010,0.018), 0.015, 1.50, 1.0),
        "POLYMER_BLACK": make_polymer("POLYMER_BLACK", (0.008,0.009,0.012), 0.32, 780.0, 0.025),
        "RUBBER": make_polymer("RUBBER", (0.012,0.013,0.014), 0.68, 420.0, 0.05),
        "SCREEN": make_screen(),
        "DECAL": make_decal(),
        "GAP": make_gap(),
    }
    setup_preview(materials)
    report = {
        "contract_version": mp.CONTRACT["version"],
        "blender_version": bpy.app.version_string,
        "canonical_materials": sorted(materials.keys()),
        "material_count": len(materials),
        "passed": set(materials.keys()) == set(mp.MATERIALS.keys()),
    }
    with open(OUT_REPORT, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, sort_keys=True)
    bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)
    print("AWFUL_MATERIAL_LIBRARY", json.dumps(report, sort_keys=True))
    if not report["passed"]:
        raise RuntimeError("Material library does not match contract")


if __name__ == "__main__":
    main()
