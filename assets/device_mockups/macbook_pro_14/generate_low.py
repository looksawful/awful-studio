import json, math, os, sys, bmesh, bpy
HERE=os.path.dirname(os.path.abspath(__file__))
COMMON=os.path.normpath(os.path.join(HERE,'..','common'))
if COMMON not in sys.path: sys.path.insert(0,COMMON)
import foundation_common as fc
MM=fc.MM
W,D,CLOSED_H=312.6*MM,221.2*MM,15.5*MM
LID_T=4.7*MM; BASE_H=8.3*MM; GAP=CLOSED_H-LID_T-BASE_H
LID_W,LID_H=312.0*MM,212.0*MM
SCREEN_W,SCREEN_H=301.66*MM,195.92*MM
OPEN_ANGLE=102.0

def arg(flag,default):
 argv=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
 return argv[argv.index(flag)+1] if flag in argv else default
OUT=os.path.abspath(arg('--out',os.path.join(HERE,'generated','macbook_pro_14_m5_low_v1_release.blend')))
EVIDENCE=os.path.abspath(arg('--evidence',os.path.join(HERE,'evidence','low_v1_release_validation.json')))
PREVIEWS=os.path.abspath(arg('--previews',os.path.join(HERE,'previews','current')))

def cyl_x(name,radius,depth,material,collection,location):
 bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=radius,depth=depth,location=location,rotation=(0,math.radians(90),0))
 o=bpy.context.object; o.name=name; o.data.materials.append(material); fc.move_to(o,collection)
 b=o.modifiers.new('EDGE_BEVEL','BEVEL'); b.width=.00018; b.segments=3
 return o
fc.clear_scene(); fc.setup_scene()
base_c=fc.make_collection('MACBOOK_PRO_14_LOW_BASE')
lid_c=fc.make_collection('MACBOOK_PRO_14_LOW_LID')
detail_c=fc.make_collection('MACBOOK_PRO_14_LOW_DETAILS')
screen_c=fc.make_collection('MACBOOK_PRO_14_LOW_SCREEN')
ctrl_c=fc.make_collection('MACBOOK_PRO_14_CONTROLS')
metal=fc.make_material('MAT_SPACE_BLACK_ALUMINUM',(0.12,0.13,0.15),0.86,0.22)
metal2=fc.make_material('MAT_EDGE_ALUMINUM',(0.18,0.19,0.21),0.88,0.20)
keymat=fc.make_material('MAT_KEYCAP',(0.012,0.014,0.018),0.0,0.28)
dark=fc.make_material('MAT_PORT_DARK',(0.004,0.005,0.007),0.02,0.16)
trackmat=fc.make_material('MAT_TRACKPAD',(0.11,0.12,0.14),0.68,0.26)
bezelmat=fc.make_material('MAT_DISPLAY_BEZEL',(0.002,0.003,0.005),0.0,0.12)
glass=fc.make_material('MAT_DISPLAY_GLASS',(0.012,0.015,0.020),0.0,0.14)
glass.diffuse_color=(0.012,0.015,0.020,0.16)
gbsdf=glass.node_tree.nodes.get('Principled BSDF'); gbsdf.inputs['Base Color'].default_value=(0.012,0.015,0.020,0.16); gbsdf.inputs['Alpha'].default_value=0.16; gbsdf.inputs['Coat Weight'].default_value=0.10; gbsdf.inputs['Coat Roughness'].default_value=0.12
try: glass.surface_render_method='DITHERED'
except Exception: pass
screenmat=fc.make_screen_material('MAT_SCREEN_CONTENT',(0.002,0.003,0.006),0.65)
root=fc.empty('CTRL_MACBOOK_PRO_14',ctrl_c)
root['asset_id']='macbook_pro_14_m5'; root['stage']='LOW_DRAFT'; root['asset_version']='low_draft_0.2'
root['closed_dimensions_mm']='312.6 x 221.2 x 15.5'
base=fc.rounded_prism('BASE_UNIBODY',W,D,BASE_H,8.4*MM,metal,base_c,axis='Z',location=(0,0,BASE_H*.5),edge_bevel=.00055)
base.parent=root
for poly in base.data.polygons: poly.use_smooth = poly.index >= 2
bottom=fc.rounded_prism('BOTTOM_PANEL',W-3.0*MM,D-3.0*MM,.55*MM,7.4*MM,metal2,detail_c,axis='Z',location=(0,0,.30*MM),edge_bevel=.00018); bottom.parent=root
keywell=fc.rounded_prism('KEYBOARD_WELL',275*MM,96*MM,.32*MM,4.5*MM,dark,detail_c,axis='Z',location=(0,31*MM,BASE_H+.08*MM),edge_bevel=.00012); keywell.parent=root
track_gap=fc.rounded_prism('TRACKPAD_GAP',134*MM,88*MM,.22*MM,4.7*MM,dark,detail_c,axis='Z',location=(0,-50*MM,BASE_H+.10*MM)); track_gap.parent=root
track=fc.rounded_prism('TRACKPAD',132*MM,86*MM,.24*MM,4.2*MM,trackmat,detail_c,axis='Z',location=(0,-50*MM,BASE_H+.23*MM),edge_bevel=.00012); track.parent=root

hinge_y=D*.5-8.5*MM
hinge=fc.empty('CTRL_HINGE',ctrl_c,location=(0,hinge_y,BASE_H+GAP)); hinge.parent=root
hinge.rotation_euler.x=math.radians(90.0-OPEN_ANGLE)
hinge['open_angle_deg']=OPEN_ANGLE; hinge['preset']='OPEN_102'
hinge['preset_closed_deg']=0.0; hinge['preset_30_deg']=30.0; hinge['preset_60_deg']=60.0; hinge['preset_90_deg']=90.0; hinge['preset_102_deg']=102.0
limit=hinge.constraints.new('LIMIT_ROTATION'); limit.use_limit_x=True; limit.min_x=math.radians(-12.0); limit.max_x=math.radians(90.0); limit.owner_space='LOCAL'

def hinge_action(name,start_deg,end_deg,end_frame):
 action=bpy.data.actions.new(name=name); hinge.animation_data_create(); hinge.animation_data.action=action
 hinge.rotation_euler.x=math.radians(90.0-start_deg); hinge.keyframe_insert(data_path='rotation_euler',index=0,frame=1)
 hinge.rotation_euler.x=math.radians(90.0-end_deg); hinge.keyframe_insert(data_path='rotation_euler',index=0,frame=end_frame)
 hinge.animation_data.action=None
 return action
lid_open=hinge_action('lid_open',0.0,OPEN_ANGLE,36)
lid_close=hinge_action('lid_close',OPEN_ANGLE,0.0,32)
for action in (lid_open,lid_close):
 track=hinge.animation_data.nla_tracks.new(); track.name=action.name
 track.strips.new(action.name,int(action.frame_range[0]),action); track.mute=True
hinge.rotation_euler.x=math.radians(90.0-OPEN_ANGLE)
root['animation_clips']='lid_open,lid_close'
for side in (-1,1):
    x=side*(W*.5-48*MM)
    barrel=cyl_x(f'HINGE_BARREL_{"L" if side<0 else "R"}',3.3*MM,58*MM,metal2,detail_c,(x,hinge_y,BASE_H+GAP)); barrel.parent=root
    cover=cyl_x(f'HINGE_COVER_{"L" if side<0 else "R"}',3.65*MM,51*MM,metal,detail_c,(x,0,0)); cover.parent=hinge

lid=fc.rounded_prism('LID_UNIBODY',LID_W,LID_H,LID_T,8.0*MM,metal,lid_c,axis='Y',edge_bevel=.00035); lid.parent=hinge; lid.location=(0,LID_T*.5,LID_H*.5)
for poly in lid.data.polygons: poly.use_smooth = poly.index >= 2
bezel=fc.rounded_prism('DISPLAY_BEZEL',307.2*MM,204.2*MM,.28*MM,6.6*MM,bezelmat,screen_c,axis='Y',edge_bevel=.00010); bezel.parent=hinge; bezel.location=(0,-.12*MM,LID_H*.5+2.6*MM)
screen=fc.rounded_prism('SCREEN_CONTENT',SCREEN_W,SCREEN_H,.12*MM,5.8*MM,screenmat,screen_c,axis='Y'); screen.parent=hinge; screen.location=(0,-.28*MM,LID_H*.5+2.0*MM)
screen_path=os.path.join(HERE,'reference','macos26_official_screen.png')
img=bpy.data.images.load(screen_path,check_existing=True); img.pack()
nodes=screenmat.node_tree.nodes; links=screenmat.node_tree.links; sbsdf=nodes.get('Principled BSDF')
tex=nodes.get('AWFUL_SCREEN_IMAGE') or nodes.new('ShaderNodeTexImage'); tex.name='AWFUL_SCREEN_IMAGE'; tex.image=img
for socket_name in ('Base Color','Emission Color'):
 socket=sbsdf.inputs.get(socket_name)
 if socket:
  for old in list(socket.links): links.remove(old)
  links.new(tex.outputs['Color'],socket)
if sbsdf.inputs.get('Emission Strength'): sbsdf.inputs['Emission Strength'].default_value=0.65
uv=screen.data.uv_layers.new(name='UVMap')
for loop in screen.data.loops:
 v=screen.data.vertices[loop.vertex_index].co; uv.data[loop.index].uv=((v.x/SCREEN_W)+.5,(v.z/SCREEN_H)+.5)
screen['screen_state']='screen_on'; screen['screen_on_emission']=0.65; screen['screen_off_emission']=0.0
screen_glass=fc.rounded_prism('SCREEN_GLASS',307.6*MM,204.6*MM,.36*MM,6.8*MM,glass,screen_c,axis='Y',edge_bevel=.00008); screen_glass.parent=hinge; screen_glass.location=(0,-.34*MM,LID_H*.5+2.6*MM)
glow_data=bpy.data.lights.new('SCREEN_GLOW_LIGHT','AREA'); glow_data.shape='RECTANGLE'; glow_data.energy=8.0; glow_data.color=(0.82,0.90,1.0); glow_data.size=SCREEN_W; glow_data.size_y=SCREEN_H
glow=bpy.data.objects.new('SCREEN_GLOW_LIGHT',glow_data); screen_c.objects.link(glow); glow.parent=hinge; glow.location=(0,-1.2*MM,LID_H*.5+2.0*MM); glow.rotation_euler.x=math.radians(-90)
glow['screen_state']='screen_on'; glow['screen_on_energy']=8.0; glow['screen_off_energy']=0.0
root['screen_states']='screen_off,screen_on'; root['screen_glow_light']='SCREEN_GLOW_LIGHT'
notch=fc.rounded_prism('CAMERA_NOTCH',36*MM,10.5*MM,.20*MM,4.3*MM,bezelmat,detail_c,axis='Y'); notch.parent=hinge; notch.location=(0,-.55*MM,LID_H-5.8*MM)
cam=fc.cylinder('FACETIME_CAMERA',1.35*MM,.20*MM,dark,detail_c,axis='Y',vertices=48); cam.parent=hinge; cam.location=(0,-.72*MM,LID_H-5.8*MM)

key_z=.82*MM; key_h=13.2*MM; gap_x=2.0*MM; gap_y=2.25*MM
row_specs=[
 ([14.0]*14,0.0),
 ([18.0]+[14.0]*12+[18.0],0.0),
 ([21.0]+[14.0]*11+[27.0],0.0),
 ([25.0]+[14.0]*10+[37.0],0.0),
 ([31.0]+[14.0]*9+[45.0],0.0),
 ([18.0,18.0,18.0,82.0,18.0,18.0,18.0,18.0],0.0),
]
row_y0=-2*MM
for r,(widths,_) in enumerate(row_specs):
    y=row_y0+r*(key_h+gap_y)
    total=sum(widths)*MM+(len(widths)-1)*gap_x
    x=-total*.5
    for c,wmm in enumerate(widths):
        w=wmm*MM
        key=fc.rounded_cube(f'KEY_{r:02d}_{c:02d}',(w,key_h,key_z),1.65*MM,keymat,detail_c,(x+w*.5,y,BASE_H+key_z*.5+.34*MM)); key.parent=root
        x+=w+gap_x
# Touch ID replaces the far-right function-row key visually
fc.rounded_cube('TOUCH_ID',(15.8*MM,13.2*MM,.92*MM),2.4*MM,keymat,detail_c,(127*MM,row_y0+5*(key_h+gap_y),BASE_H+.80*MM)).parent=root
for side in (-1,1):
    sx=side*(W*.5-20.0*MM)
    for row in range(15):
        sy=2.0*MM+row*5.2*MM
        for col in range(5):
            ox=(col-2)*2.35*MM
            hole=fc.cylinder(f'SPEAKER_{"L" if side<0 else "R"}_{row:02d}_{col:02d}',.48*MM,.24*MM,dark,detail_c,(sx+ox,sy,BASE_H+.21*MM),axis='Z',vertices=20); hole.parent=root

port_specs=[
 ('MAGSAFE','L',62,14.0,3.4),('TB_LEFT_1','L',27,12.5,2.6),('TB_LEFT_2','L',-1,12.5,2.6),('HEADPHONE','L',-54,7.2,3.7),
 ('HDMI','R',53,17.0,4.4),('SDXC','R',18,19.5,2.4),('TB_RIGHT','R',-22,12.5,2.6),
]
for name,side,y_mm,length_mm,height_mm in port_specs:
    sgn=-1 if side=='L' else 1
    x=sgn*(W*.5+.10*MM)
    rim=fc.rounded_cube(f'{name}_RIM',(.38*MM,(length_mm+1.6)*MM,(height_mm+1.0)*MM),min(.8*MM,height_mm*.30*MM),metal2,detail_c,(x,y_mm*MM,BASE_H*.50)); rim.parent=root
    cav=fc.rounded_cube(name,(.48*MM,length_mm*MM,height_mm*MM),min(.7*MM,height_mm*.26*MM),dark,detail_c,(sgn*(W*.5+.22*MM),y_mm*MM,BASE_H*.50)); cav.parent=root

for i,(x,y) in enumerate(((-W*.5+18*MM,-D*.5+17*MM),(W*.5-18*MM,-D*.5+17*MM),(-W*.5+18*MM,D*.5-20*MM),(W*.5-18*MM,D*.5-20*MM)),1):
    foot=fc.cylinder(f'FOOT_{i:02d}',5.2*MM,.75*MM,keymat,detail_c,(x,y,-.28*MM),axis='Z',vertices=48); foot.parent=root
for side in (-1,1):
    for idx in range(12):
        y=(D*.5-34*MM)-idx*3.2*MM
        vent=fc.rounded_cube(f'VENT_{"L" if side<0 else "R"}_{idx:02d}',(.35*MM,2.0*MM,1.0*MM),.15*MM,dark,detail_c,(side*(W*.5+.06*MM),y,2.2*MM)); vent.parent=root


# Release polish recovered from the verified low_v1 release file.
logo_path=os.path.join(HERE,'reference','apple_logo_alpha.png')
logo_mat=bpy.data.materials.new('MAT_APPLE_LOGO_RELEASE'); logo_mat.use_nodes=True
nodes=logo_mat.node_tree.nodes; links=logo_mat.node_tree.links
for node in list(nodes): nodes.remove(node)
outn=nodes.new('ShaderNodeOutputMaterial'); lbsdf=nodes.new('ShaderNodeBsdfPrincipled'); tex=nodes.new('ShaderNodeTexImage')
tex.image=bpy.data.images.load(logo_path,check_existing=True); tex.image.pack()
lbsdf.inputs['Base Color'].default_value=(.018,.020,.024,1)
lbsdf.inputs['Metallic'].default_value=.82; lbsdf.inputs['Roughness'].default_value=.16
links.new(tex.outputs['Alpha'],lbsdf.inputs['Alpha']); links.new(lbsdf.outputs['BSDF'],outn.inputs['Surface'])
try: logo_mat.surface_render_method='DITHERED'
except Exception: pass
verts=[(-13.838*MM,4.75*MM,89*MM),(13.838*MM,4.75*MM,89*MM),(13.838*MM,4.75*MM,0.12299999594688416),(-13.838*MM,4.75*MM,0.12299999594688416)]
mesh=bpy.data.meshes.new('APPLE_LOGO_RELEASE_MESH'); mesh.from_pydata(verts,[],[(0,1,2,3)]); mesh.update()
logo=bpy.data.objects.new('APPLE_LOGO_RELEASE',mesh); bpy.context.scene.collection.objects.link(logo); logo.parent=hinge; logo.data.materials.append(logo_mat)
uv=mesh.uv_layers.new(name='UVMap')
for loop,coord in zip(mesh.loops,((0,0),(1,0),(1,1),(0,1))): uv.data[loop.index].uv=coord
root['stage']='RELEASE_CANDIDATE'; root['release_export_target']='GLB uncompressed'; root['release_polish']='apple_logo + embedded source image'

def local_dims_mm(obj):
 xs=[v.co.x for v in obj.data.vertices]; ys=[v.co.y for v in obj.data.vertices]; zs=[v.co.z for v in obj.data.vertices]
 return {'x':(max(xs)-min(xs))/MM,'y':(max(ys)-min(ys))/MM,'z':(max(zs)-min(zs))/MM}
def non_manifold_edges(obj):
 bm=bmesh.new(); bm.from_mesh(obj.data); count=sum(1 for edge in bm.edges if not edge.is_manifold); bm.free(); return count
base_dims=local_dims_mm(base); lid_dims=local_dims_mm(lid)
base_expected={'x':312.6,'y':221.2,'z':8.3}; lid_expected={'x':312.0,'y':4.7,'z':212.0}
base_delta={k:base_dims[k]-base_expected[k] for k in base_expected}; lid_delta={k:lid_dims[k]-lid_expected[k] for k in lid_expected}
mandatory=['SCREEN_GLOW_LIGHT','BASE_UNIBODY','LID_UNIBODY','SCREEN_CONTENT','SCREEN_GLASS','CAMERA_NOTCH','FACETIME_CAMERA','TRACKPAD','TOUCH_ID','MAGSAFE','TB_LEFT_1','TB_LEFT_2','HEADPHONE','HDMI','SDXC','TB_RIGHT','APPLE_LOGO_RELEASE','FOOT_01','SPEAKER_L_00_00','SPEAKER_R_14_04']
missing=[name for name in mandatory if bpy.data.objects.get(name) is None]
base_nm=non_manifold_edges(base); lid_nm=non_manifold_edges(lid)
passed=(not missing and base_nm==0 and lid_nm==0 and all(abs(v)<=.01 for v in base_delta.values()) and all(abs(v)<=.01 for v in lid_delta.values()) and abs(hinge['open_angle_deg']-OPEN_ANGLE)<1e-6)
evidence={'asset_id':'macbook_pro_14_m5','stage':'RELEASE_CANDIDATE','blender_version':bpy.app.version_string,'base_expected_mm':base_expected,'base_actual_mm':{k:round(v,6) for k,v in base_dims.items()},'base_delta_mm':{k:round(v,6) for k,v in base_delta.items()},'lid_expected_mm':lid_expected,'lid_actual_mm':{k:round(v,6) for k,v in lid_dims.items()},'lid_delta_mm':{k:round(v,6) for k,v in lid_delta.items()},'base_non_manifold_edges':base_nm,'lid_non_manifold_edges':lid_nm,'mandatory_missing':missing,'object_count':len(bpy.data.objects),'material_count':len(bpy.data.materials),'hinge_open_angle_deg':hinge['open_angle_deg'],'animation_clips':['lid_open','lid_close'],'screen_states':['screen_off','screen_on'],'passed':passed}
os.makedirs(os.path.dirname(EVIDENCE),exist_ok=True)
with open(EVIDENCE,'w',encoding='utf-8') as f: json.dump(evidence,f,indent=2)

for material in list(bpy.data.materials):
 if material.users==0: bpy.data.materials.remove(material)
evidence['material_count']=len(bpy.data.materials)
with open(EVIDENCE,'w',encoding='utf-8') as f: json.dump(evidence,f,indent=2)
fc.save_blend(OUT)
print('MACBOOK_LOW_VALIDATION',json.dumps(evidence,sort_keys=True))
if not passed: raise RuntimeError('MacBook Pro 14 LOW v1 release validation failed')
