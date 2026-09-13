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

SIZE='13'
argv=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
for i,a in enumerate(argv):
    if a=='--size' and i+1<len(argv): SIZE=argv[i+1]
if SIZE=='11': W,H,D,SW,SH=177.5,249.7,5.3,160.13,232.32
else: W,H,D,SW,SH=215.5,281.6,5.1,199.14,265.19
W*=MM;H*=MM;D*=MM;SW*=MM;SH*=MM
clear_scene(); setup_scene()
body_c=coll(f'IPAD_PRO_{SIZE}_BODY'); detail_c=coll(f'IPAD_PRO_{SIZE}_DETAILS'); screen_c=coll(f'IPAD_PRO_{SIZE}_SCREEN')
metal=mat('MAT_SPACE_BLACK_ALUMINUM',(.18,.18,.20),.78,.26); glass=mat('MAT_DISPLAY_GLASS',(.012,.014,.018),0,.10); dark=mat('MAT_CAMERA_BLACK',(.01,.012,.016),.1,.08)
rounded_box('BODY_ALUMINUM',(W,D,H),9*MM,metal,body_c)
rounded_box('SCREEN_CONTENT',(SW,.00032,SH),7*MM,glass,screen_c,(0,-D/2-.0002,0))
hs=36*MM; hx=-W/2+hs/2+6*MM; hz=H/2-hs/2-10*MM
rounded_box('CAMERA_HOUSING',(hs,.0020,hs),7*MM,metal,detail_c,(hx,D/2+.001,hz))
for name,dx,dz,r,m in [('REAR_CAMERA',-7,7,5.415,dark),('FLASH',7,7,3.35,mat('MAT_FLASH',(.9,.86,.75),0,.22)),('LIDAR',-7,-7,4.2,dark),('REAR_MIC',7,-7,1.8,dark)]: cyl_y(name,r*MM,.0012,m,detail_c,(hx+dx*MM,D/2+.0022,hz+dz*MM),48)
for x in (-5.27,0,5.27): cyl_y('SMART_CONNECTOR',1.7*MM,.0004,metal,detail_c,(x*MM,D/2+.0003,-H/2+12*MM),32)
root=bpy.data.objects.new(f'CTRL_IPAD_PRO_{SIZE}',None); bpy.context.scene.collection.objects.link(root)
for c in (body_c,detail_c,screen_c):
    for o in c.objects:o.parent=root
root['asset_id']=f'ipad_pro_{SIZE}_m5'; root['stage']='BLOCKOUT'; root['size_variant']=SIZE
save_output(f'ipad_pro_{SIZE}_m5_foundation.blend')
