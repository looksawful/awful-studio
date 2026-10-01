"""Camera pupil sits under the cover; USB-C has an interior tongue."""
import bpy
import bmesh
from mathutils import Vector

glass = bpy.data.objects['REAR_CAMERA_GLASS']
pupil = bpy.data.objects['REAR_CAMERA_PUPIL']
glass_front = max((glass.matrix_world @ Vector(p)).y for p in glass.bound_box)
pupil_front = max((pupil.matrix_world @ Vector(p)).y for p in pupil.bound_box)
assert pupil_front < glass_front, 'Camera pupil protrudes in front of its cover glass'
bsdf = glass.active_material.node_tree.nodes.get('Principled BSDF')
assert bsdf.inputs['Transmission Weight'].default_value >= 0.8, 'Camera cover must transmit to recessed optics'
assert bpy.data.objects.get('USB_C_TONGUE') is not None, 'USB-C requires a physical recessed tongue'
screen = bpy.data.objects['SCREEN_CONTENT'].active_material.node_tree.nodes.get('Principled BSDF')
assert not screen.inputs['Base Color'].is_linked, 'OLED image must emit rather than reflect as printed paper'
assert screen.inputs['Specular IOR Level'].default_value == 0.0
for name in ('MAT_ASSEMBLY_GAP', 'MAT_DISPLAY_BEZEL'):
    material = bpy.data.materials[name].node_tree.nodes.get('Principled BSDF')
    assert material.inputs['Specular IOR Level'].default_value <= .15, 'Display borders must retain the dark finish under studio lights'
for name in ('BODY_ALUMINUM', 'CAMERA_HOUSING', 'SCREEN_GLASS'):
    bm = bmesh.new(); bm.from_mesh(bpy.data.objects[name].data)
    assert bm.calc_volume(signed=True) > 0, f'{name}: inward shell normals'
    bm.free()
print('IPAD_OPTICS_PORTS_PASS', bpy.app.version_string)
