import os, sys, bpy
from mathutils import Vector
HERE=os.path.dirname(os.path.abspath(__file__))
def arg(flag,default):
    argv=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
    return argv[argv.index(flag)+1] if flag in argv else default
OUT=os.path.abspath(arg('--out',os.path.join(HERE,'previews','current')))
os.makedirs(OUT,exist_ok=True)
scene=bpy.context.scene
scene.render.engine='BLENDER_EEVEE'
scene.render.resolution_x=1400; scene.render.resolution_y=1400; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.view_settings.exposure=-0.7
scene.world.use_nodes=True
bg=scene.world.node_tree.nodes.get('Background'); bg.inputs['Color'].default_value=(0.001,0.001,0.001,1); bg.inputs['Strength'].default_value=0.02
for o in list(bpy.data.objects):
    if o.type in {'LIGHT','CAMERA'}: bpy.data.objects.remove(o,do_unlink=True)

def target(obj,pt): obj.rotation_euler=(Vector(pt)-obj.location).to_track_quat('-Z','Y').to_euler()
def area(name,loc,energy,size,pt):
    d=bpy.data.lights.new(name,'AREA'); d.energy=energy; d.shape='RECTANGLE'; d.size=size; d.size_y=size*.35
    o=bpy.data.objects.new(name,d); scene.collection.objects.link(o); o.location=loc; target(o,pt); return o
area('KEY',(0.42,-0.38,0.42),720,0.34,(0,0.01,0.08))
area('FILL',(-0.36,-0.20,0.22),190,0.28,(0,0.02,0.07))
area('RIM',(0.30,0.32,0.34),680,0.22,(0,0.06,0.10))
area('TOP',(-0.08,0.02,0.55),260,0.30,(0,0.02,0.08))
def camera(name,loc,pt,lens=62):
    d=bpy.data.cameras.new(name); d.lens=lens; d.sensor_width=36; d.clip_start=0.01
    o=bpy.data.objects.new(name,d); scene.collection.objects.link(o); o.location=loc; target(o,pt); return o
cams=[
 ('hero',camera('CAM_HERO',(0.33,-0.43,0.25),(0,0.015,0.085),58)),
 ('front',camera('CAM_FRONT',(0,-0.58,0.145),(0,0.035,0.105),72)),
 ('side',camera('CAM_SIDE',(0.46,-0.02,0.14),(0,0.03,0.075),72)),
 ('keyboard',camera('CAM_KEYBOARD',(0,-0.27,0.17),(0,-0.015,0.025),78)),
 ('hinge',camera('CAM_HINGE',(0.22,0.22,0.13),(0,0.104,0.055),90)),
 ('ports',camera('CAM_PORTS',(-0.37,-0.01,0.075),(-0.155,0.01,0.04),88)),
]
for label,cam in cams:
    scene.camera=cam
    scene.render.filepath=os.path.join(OUT,f'macbook_pro_14_current_{label}.png')
    bpy.ops.render.render(write_still=True)
print('MACBOOK_PREVIEWS_OK',OUT)
