"""Runtime smoke for core AWFUL STUDIO workstation import/export and booleans."""

import os
import tempfile

import bpy


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)


assert tuple(bpy.app.version[:3]) == (5, 2, 1), bpy.app.version_string
with tempfile.TemporaryDirectory(prefix="awful-blender-smoke-") as root:
    clear_scene()
    bpy.ops.mesh.primitive_cube_add(size=2)
    glb = os.path.join(root, "roundtrip.glb")
    bpy.ops.export_scene.gltf(filepath=glb, export_format="GLB", use_selection=False)
    assert os.path.getsize(glb) > 0
    clear_scene()
    bpy.ops.import_scene.gltf(filepath=glb)
    assert any(obj.type == "MESH" for obj in bpy.context.scene.objects)
    print("GLTF_ROUNDTRIP_PASS", os.path.getsize(glb))

    fbx = os.path.join(root, "roundtrip.fbx")
    bpy.ops.export_scene.fbx(filepath=fbx, use_selection=False)
    assert os.path.getsize(fbx) > 0
    clear_scene()
    bpy.ops.import_scene.fbx(filepath=fbx)
    assert any(obj.type == "MESH" for obj in bpy.context.scene.objects)
    print("FBX_ROUNDTRIP_PASS", os.path.getsize(fbx))

    svg = os.path.join(root, "shape.svg")
    with open(svg, "w", encoding="utf-8") as handle:
        handle.write('<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100"><rect x="10" y="10" width="80" height="80"/></svg>')
    clear_scene()
    bpy.ops.import_curve.svg(filepath=svg)
    assert any(obj.type == "CURVE" for obj in bpy.context.scene.objects)
    print("SVG_IMPORT_PASS")

    clear_scene()
    bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
    base = bpy.context.object
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0.75, 0, 0))
    cutter = bpy.context.object
    base.select_set(True)
    cutter.select_set(True)
    bpy.context.view_layer.objects.active = base
    result = bpy.ops.object.boolean_auto_difference()
    assert result == {"FINISHED"}, result
    assert len(bpy.context.scene.objects) == 1
    assert len(base.data.polygons) > 6
    print("BOOL_TOOL_PASS", len(base.data.polygons))

print("SMOKE_ROUNDTRIP_PASS")
