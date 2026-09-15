# AWFUL STUDIO device mockup foundation - Blender 5.2+
import bpy, math, os, sys
from mathutils import Vector

MM = 0.001

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for c in list(bpy.data.collections):
        if c.name != 'Collection': bpy.data.collections.remove(c)

def setup_scene():
    s=bpy.context.scene
    s.unit_settings.system='METRIC'; s.unit_settings.scale_length=1.0; s.unit_settings.length_unit='METERS'
    s.render.engine='BLENDER_EEVEE_NEXT'

def mat(name, base, metallic=0.0, rough=.35):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color=(*base,1)
    m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=(*base,1); bs.inputs['Metallic'].default_value=metallic; bs.inputs['Roughness'].default_value=rough
    return m

def coll(name):
    c=bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if c.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(c)
    return c

def move_to_collection(obj, collection):
    for old in list(obj.users_collection): old.objects.unlink(obj)
    collection.objects.link(obj)

def rounded_box(name, dims, radius, material, collection, location=(0,0,0), segments=6):
    bpy.ops.mesh.primitive_cube_add(location=location)
    o=bpy.context.object; o.name=name; o.dimensions=dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    b=o.modifiers.new('BEVEL','BEVEL'); b.width=radius; b.segments=segments; b.limit_method='ANGLE'
    o.data.materials.append(material); move_to_collection(o,collection)
    return o

def cyl_y(name, radius, depth, material, collection, location=(0,0,0), vertices=64):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=location, rotation=(math.radians(90),0,0))
    o=bpy.context.object; o.name=name; o.data.materials.append(material); move_to_collection(o,collection); return o

def save_output(default_name):
    argv=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
    out=None
    for i,a in enumerate(argv):
        if a=='--out' and i+1<len(argv): out=argv[i+1]
    if not out: out=os.path.abspath(default_name)
    bpy.ops.wm.save_as_mainfile(filepath=out)
    print('AWFUL_STUDIO_SAVED',out)

clear_scene(); setup_scene()
body_c=coll('IPHONE_17_BODY'); detail_c=coll('IPHONE_17_DETAILS'); screen_c=coll('IPHONE_17_SCREEN')
metal=mat('MAT_ANODIZED_ALUMINUM',(0.55,0.56,0.58),.75,.28); glass=mat('MAT_DISPLAY_GLASS',(0.015,0.018,0.022),0,.12); back=mat('MAT_BACK_GLASS',(0.60,0.58,0.64),0,.30); black=mat('MAT_CAMERA_BLACK',(0.01,0.012,0.016),.1,.08)
W,H,D=71.5*MM,149.6*MM,7.95*MM
rounded_box('BODY_ALUMINUM',(W,D,H),13.6*MM,metal,body_c)
rounded_box('SCREEN_CONTENT',(66.55*MM,.00035,144.69*MM),10.8*MM,glass,screen_c,(0,-D/2-.00022,0))
rounded_box('BACK_GLASS',(W-.0016,.00045,H-.0016),12.6*MM,back,body_c,(0,D/2+.0002,0))
for i,(x,z) in enumerate([(-22.1,60.9),(-22.1,43.2)],1):
    cyl_y(f'CAMERA_{i}_RING',8*MM,.0022,black,detail_c,(x*MM,D/2+.0011,z*MM))
    cyl_y(f'CAMERA_{i}_GLASS',5.76*MM,.0005,glass,detail_c,(x*MM,D/2+.00245,z*MM))
cyl_y('FLASH',3.14*MM,.0007,mat('MAT_FLASH',(0.9,.87,.76),0,.22),detail_c,(-13*MM,D/2+.0010,52*MM))
rounded_box('DYNAMIC_ISLAND',(21*MM,.00045,6.3*MM),3.15*MM,black,detail_c,(0,-D/2-.0005,H/2-14*MM))
for name,z,l in [('ACTION_BUTTON',H/2-34.08*MM,12*MM),('VOL_UP',H/2-48.23*MM,9*MM),('VOL_DOWN',H/2-62.43*MM,9*MM)]: rounded_box(name,(0.0010,0.00055,l),0.00045,metal,detail_c,(-W/2-.0002,0,z))
rounded_box('SIDE_BUTTON',(0.0010,0.00055,18*MM),.00045,metal,detail_c,(W/2+.0002,0,H/2-44*MM))
rounded_box('CAMERA_CONTROL',(0.0010,0.00045,20*MM),.00045,black,detail_c,(W/2+.00025,0,-31*MM))
root=bpy.data.objects.new('CTRL_IPHONE_17',None); bpy.context.scene.collection.objects.link(root)
for c in (body_c,detail_c,screen_c):
    for o in c.objects: o.parent=root
root['asset_id']='iphone_17'; root['stage']='BLOCKOUT'; root['dimensions_mm']='71.5 x 149.6 x 7.95'
save_output('iphone_17_foundation.blend')
