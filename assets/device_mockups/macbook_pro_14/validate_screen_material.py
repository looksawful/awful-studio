"""The image emits light; the separate cover owns screen reflections."""
import bpy

material = bpy.data.objects['SCREEN_CONTENT'].active_material
bsdf = material.node_tree.nodes.get('Principled BSDF')
assert not bsdf.inputs['Base Color'].is_linked, 'Display image must not reflect studio lights as printed paper'
assert max(bsdf.inputs['Base Color'].default_value[:3]) <= 0.01
assert bsdf.inputs['Specular IOR Level'].default_value == 0.0, 'Cover glass owns specular reflections'
assert bsdf.inputs['Emission Color'].is_linked, 'Screen image must remain emissive'
assert bsdf.inputs['Emission Strength'].default_value > 0.0
print('MACBOOK_SCREEN_MATERIAL_PASS', bpy.app.version_string)
