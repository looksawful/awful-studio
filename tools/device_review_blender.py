import argparse
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector

VIEWS = {
    "front": (0, -1, 0), "back": (0, 1, 0),
    "left": (-1, 0, 0), "right": (1, 0, 0),
    "top": (0, 0, 1), "bottom": (0, 0, -1),
    "front_3q": (1, -1, 0.7), "back_3q": (-1, 1, 0.7),
}
MODES = ("material", "clay", "wire", "normals", "silhouette")


def parse_args():
    args = sys.argv[sys.argv.index("--") + 1:]
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--size", type=int, default=640)
    parser.add_argument("--modes", default=",".join(MODES))
    parser.add_argument("--views", default=",".join(VIEWS))
    return parser.parse_args(args)


def load_glb(path: Path):
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.gltf(filepath=str(path))


def meshes():
    return [obj for obj in bpy.context.scene.objects if obj.type == "MESH" and not obj.hide_render]


def bounds(objects):
    points = [obj.matrix_world @ Vector(corner) for obj in objects for corner in obj.bound_box]
    lo = Vector((min(p.x for p in points), min(p.y for p in points), min(p.z for p in points)))
    hi = Vector((max(p.x for p in points), max(p.y for p in points), max(p.z for p in points)))
    return lo, hi, (lo + hi) * 0.5, (hi - lo)

def ensure_camera(center, extent):
    data = bpy.data.cameras.new("AWFUL_REVIEW_CAMERA")
    camera = bpy.data.objects.new("AWFUL_REVIEW_CAMERA", data)
    bpy.context.scene.collection.objects.link(camera)
    data.type = "ORTHO"
    data.lens = 70
    bpy.context.scene.camera = camera
    return camera


def aim(camera, center, direction, extent, perspective=False):
    direction = Vector(direction).normalized()
    radius = max(extent.length * 0.5, 0.001)
    camera.location = center + direction * radius * 3.2
    camera.rotation_euler = (-direction).to_track_quat("-Z", "Y").to_euler()
    camera.data.type = "PERSP" if perspective else "ORTHO"
    if perspective:
        camera.data.lens = 70
    else:
        if abs(direction.z) > 0.9:
            visible = max(extent.x, extent.y)
        elif abs(direction.x) > 0.9:
            visible = max(extent.y, extent.z)
        else:
            visible = max(extent.x, extent.z)
        camera.data.ortho_scale = max(visible * 1.2, 0.001)


def setup_render(size):
    scene = bpy.context.scene
    scene.render.resolution_x = size
    scene.render.resolution_y = size
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.render.use_file_extension = True
    scene.world.color = (0.8, 0.8, 0.8)
    return scene


def add_area(name, location, energy, size):
    data = bpy.data.lights.new(name, "AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    obj = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = (Vector((0, 0, 0)) - obj.location).to_track_quat("-Z", "Y").to_euler()
    return obj

def normal_material():
    mat = bpy.data.materials.new("AWFUL_REVIEW_NORMALS")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    geo = nodes.new("ShaderNodeNewGeometry")
    scale = nodes.new("ShaderNodeVectorMath")
    scale.operation = "SCALE"
    scale.inputs[3].default_value = 0.5
    add = nodes.new("ShaderNodeVectorMath")
    add.operation = "ADD"
    add.inputs[1].default_value = (0.5, 0.5, 0.5)
    emission = nodes.new("ShaderNodeEmission")
    output = nodes.new("ShaderNodeOutputMaterial")
    links = mat.node_tree.links
    links.new(geo.outputs["Normal"], scale.inputs[0])
    links.new(scale.outputs[0], add.inputs[0])
    links.new(add.outputs[0], emission.inputs["Color"])
    links.new(emission.outputs[0], output.inputs["Surface"])
    return mat


def wire_material():
    mat = bpy.data.materials.new("AWFUL_REVIEW_WIRE")
    mat.diffuse_color = (0.05, 0.05, 0.05, 1.0)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    wire = nodes.new("ShaderNodeWireframe")
    wire.inputs["Size"].default_value = 0.7
    mix = nodes.new("ShaderNodeMixRGB")
    mix.blend_type = "MIX"
    mix.inputs[1].default_value = (0.55, 0.55, 0.55, 1.0)
    mix.inputs[2].default_value = (0.01, 0.01, 0.01, 1.0)
    emission = nodes.new("ShaderNodeEmission")
    output = nodes.new("ShaderNodeOutputMaterial")
    links = mat.node_tree.links
    links.new(wire.outputs["Fac"], mix.inputs[0])
    links.new(mix.outputs[0], emission.inputs["Color"])
    links.new(emission.outputs[0], output.inputs["Surface"])
    return mat


def configure_mode(scene, mode, objects, normals, wire):
    scene.view_layers[0].material_override = None
    for obj in objects:
        obj.show_wire = False
        obj.show_all_edges = False
    if mode in {"material", "normals", "wire"}:
        scene.render.engine = "BLENDER_EEVEE"
        scene.render.image_settings.color_mode = "RGBA"
        scene.view_layers[0].material_override = normals if mode == "normals" else wire if mode == "wire" else None
        return
    scene.render.engine = "BLENDER_WORKBENCH"
    shading = scene.display.shading
    shading.light = "STUDIO"
    shading.show_shadows = True
    shading.show_cavity = True
    shading.cavity_type = "BOTH"
    shading.color_type = "SINGLE"
    shading.single_color = (0.55, 0.55, 0.55) if mode != "silhouette" else (0.02, 0.02, 0.02)
    if mode == "wire":
        for obj in objects:
            obj.show_wire = True
            obj.show_all_edges = True
        shading.show_shadows = False
        shading.show_cavity = True

def main():
    args = parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    if args.input.suffix.lower() == ".glb":
        load_glb(args.input)
    objects = meshes()
    if not objects:
        raise RuntimeError(f"No renderable meshes in {args.input}")
    lo, hi, center, extent = bounds(objects)
    scene = setup_render(args.size)
    camera = ensure_camera(center, extent)
    radius = max(extent.length, 0.1)
    add_area("AWFUL_REVIEW_KEY", center + Vector((radius, -radius, radius)), 700, radius)
    add_area("AWFUL_REVIEW_FILL", center + Vector((-radius, -radius * 0.5, radius * 0.5)), 350, radius)
    add_area("AWFUL_REVIEW_RIM", center + Vector((0, radius, radius)), 500, radius)
    normals = normal_material()
    wire = wire_material()
    requested_modes = [mode for mode in args.modes.split(",") if mode in MODES]
    requested_views = [view for view in args.views.split(",") if view in VIEWS]
    for mode in requested_modes:
        configure_mode(scene, mode, objects, normals, wire)
        for view in requested_views:
            direction = VIEWS[view]
            aim(camera, center, direction, extent, perspective=view.endswith("3q"))
            scene.render.filepath = str(args.output / f"{mode}__{view}.png")
            bpy.ops.render.render(write_still=True)
    print(f"AWFUL_REVIEW_OK meshes={len(objects)} bounds={tuple(round(v, 6) for v in extent)}")


if __name__ == "__main__":
    main()