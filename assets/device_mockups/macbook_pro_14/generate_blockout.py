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
base_c=coll('MACBOOK_PRO_14_BASE'); lid_c=coll('MACBOOK_PRO_14_LID'); detail_c=coll('MACBOOK_PRO_14_DETAILS'); screen_c=coll('MACBOOK_PRO_14_SCREEN')
metal=mat('MAT_SPACE_BLACK_ALUMINUM',(.16,.16,.18),.82,.27); keymat=mat('MAT_KEYCAP',(.025,.025,.028),0,.32); glass=mat('MAT_DISPLAY_GLASS',(.008,.010,.014),0,.09)
W,D,BH=312.6*MM,221.2*MM,8.3*MM
rounded_box('BASE_UNIBODY',(W,D,BH),8*MM,metal,base_c,(0,0,BH/2))
rounded_box('TRACKPAD',(132*MM,86*MM,.0007),4*MM,metal,detail_c,(0,-50*MM,BH+.00035))
kw,kh,gap=16.2*MM,16.2*MM,2.2*MM; cols,rows=14,6; total=cols*kw+(cols-1)*gap; x0=-total/2+kw/2; y0=18*MM
for r in range(rows):
    for c in range(cols):
        if r==5 and 3<=c<=10: continue
        rounded_box(f'KEY_{r:02}_{c:02}',(kw,kh,1.2*MM),2*MM,keymat,detail_c,(x0+c*(kw+gap),y0+r*(kh+gap),BH+.0006),3)
rounded_box('KEY_SPACE',(85*MM,kh,1.2*MM),2*MM,keymat,detail_c,(0,y0+5*(kh+gap),BH+.0006),3)
for x in (-W/2+27*MM,W/2-27*MM): rounded_box('SPEAKER_GRILLE_PROXY',(20*MM,118*MM,.0005),3*MM,keymat,detail_c,(x,30*MM,BH+.00025))
bpy.ops.object.empty_add(type='PLAIN_AXES',location=(0,D/2-7*MM,BH)); hinge=bpy.context.object; hinge.name='CTRL_HINGE'; move_to_collection(hinge,lid_c)
LH,LW,LT=212*MM,312*MM,4.7*MM
lid=rounded_box('LID_UNIBODY',(LW,LT,LH),7.5*MM,metal,lid_c,(0,0,LH/2)); lid.parent=hinge
screen=rounded_box('SCREEN_CONTENT',(301.66*MM,.0005,195.92*MM),6*MM,glass,screen_c,(0,-LT/2-.0003,LH/2+3*MM)); screen.parent=hinge
notch=rounded_box('CAMERA_NOTCH',(36*MM,.0007,10*MM),4*MM,keymat,detail_c,(0,-LT/2-.0007,LH-5*MM)); notch.parent=hinge
hinge.rotation_euler.x=math.radians(12.0); hinge['open_angle_deg']=102.0
root=bpy.data.objects.new('CTRL_MACBOOK_PRO_14',None); bpy.context.scene.collection.objects.link(root)
for c in (base_c,detail_c):
    for o in c.objects:o.parent=root
hinge.parent=root
root['asset_id']='macbook_pro_14_m5'; root['stage']='BLOCKOUT'; root['dimensions_mm']='312.6 x 221.2 x 15.5 closed envelope'
save_output('macbook_pro_14_m5_foundation.blend')
