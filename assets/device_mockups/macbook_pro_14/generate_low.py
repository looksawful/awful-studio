import json, math, os, sys, bmesh, bpy
HERE=os.path.dirname(os.path.abspath(__file__))
COMMON=os.path.normpath(os.path.join(HERE,'..','common'))
if COMMON not in sys.path: sys.path.insert(0,COMMON)
if HERE not in sys.path: sys.path.insert(0,HERE)
import foundation_common as fc
import deck_details
import construction_details as cd
from geometry_contract import CHASSIS_FACTS, derive_metric_measurements
MM=fc.MM
G1=derive_metric_measurements()
W=CHASSIS_FACTS['width'].value_mm*MM
D=CHASSIS_FACTS['depth'].value_mm*MM
CLOSED_H=CHASSIS_FACTS['closed_height'].value_mm*MM
LID_T=4.7*MM; BASE_H=8.3*MM; FOOT_BOTTOM=-.655*MM
GAP=CLOSED_H+FOOT_BOTTOM-LID_T-BASE_H
LID_W,LID_H=312.0*MM,212.0*MM
SCREEN_W=G1['display']['active_width_mm']*MM
SCREEN_H=G1['display']['active_height_mm']*MM
SCREEN_RADIUS=G1['display']['opening_corner_radius_mm']*MM
KEYBOARD=G1['keyboard']
TRACKPAD=G1['trackpad']
TRACKPAD_W=TRACKPAD['right_x_mm']-TRACKPAD['left_x_mm']
OPEN_ANGLE=102.0

def arg(flag,default):
 argv=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
 return argv[argv.index(flag)+1] if flag in argv else default
OUT=os.path.abspath(arg('--out',os.path.join(HERE,'generated','macbook_pro_14_m5_low_v1_release.blend')))
EVIDENCE=os.path.abspath(arg('--evidence',os.path.join(HERE,'evidence','low_v1_release_validation.json')))
PREVIEWS=os.path.abspath(arg('--previews',os.path.join(HERE,'previews','current')))

def subtract_cylinder_x(target,radius,depth,location):
 bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=radius,depth=depth,location=location,rotation=(0,math.radians(90),0))
 cutter=bpy.context.object
 bpy.ops.object.select_all(action='DESELECT'); target.select_set(True); bpy.context.view_layer.objects.active=target
 mod=target.modifiers.new('HINGE_CLEARANCE','BOOLEAN'); mod.operation='DIFFERENCE'; mod.solver='EXACT'; mod.object=cutter
 bpy.ops.object.modifier_apply(modifier=mod.name)
 bpy.data.objects.remove(cutter,do_unlink=True)

def cyl_x(name,radius,depth,material,collection,location,inner_radius=0.0):
 bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=radius,depth=depth,location=location,rotation=(0,math.radians(90),0))
 o=bpy.context.object; o.name=name; o.data.materials.append(material); fc.move_to(o,collection)
 if inner_radius:
  subtract_cylinder_x(o,inner_radius,depth+.001,location)
 b=o.modifiers.new('EDGE_BEVEL','BEVEL'); b.width=.00018; b.segments=3
 return o
fc.clear_scene(); fc.setup_scene()
base_c=fc.make_collection('MACBOOK_PRO_14_LOW_BASE')
lid_c=fc.make_collection('MACBOOK_PRO_14_LOW_LID')
detail_c=fc.make_collection('MACBOOK_PRO_14_LOW_DETAILS')
screen_c=fc.make_collection('MACBOOK_PRO_14_LOW_SCREEN')
ctrl_c=fc.make_collection('MACBOOK_PRO_14_CONTROLS')
metal=fc.make_material('MAT_SPACE_BLACK_ALUMINUM',(0.018,0.020,0.024),0.86,0.30)
metal2=fc.make_material('MAT_EDGE_ALUMINUM',(0.040,0.043,0.048),0.88,0.26)
keymat=fc.make_material('MAT_KEYCAP',(0.0020,0.0024,0.0030),0.0,0.78)
keymat.node_tree.nodes.get('Principled BSDF').inputs['Specular IOR Level'].default_value=.12
dark=fc.make_material('MAT_PORT_DARK',(0.004,0.005,0.007),0.02,0.62)
wellmat=fc.make_material('MAT_KEYBOARD_WELL',(0.001,0.0015,0.002),0.0,0.70)
wellmat.node_tree.nodes.get('Principled BSDF').inputs['Specular IOR Level'].default_value=.06
trackmat=fc.make_material('MAT_TRACKPAD',(0.014,0.016,0.020),0.0,0.22)
track_bsdf=trackmat.node_tree.nodes.get('Principled BSDF')
track_bsdf.inputs['Specular IOR Level'].default_value=.28
track_bsdf.inputs['Coat Weight'].default_value=.18
track_bsdf.inputs['Coat Roughness'].default_value=.16
bezelmat=fc.make_material('MAT_DISPLAY_BEZEL',(0.002,0.003,0.005),0.0,0.28)
bezelmat.node_tree.nodes.get('Principled BSDF').inputs['Specular IOR Level'].default_value=.025
hingemat=fc.make_material('MAT_HINGE_SHROUD',(0.003,0.0035,0.004),0.0,0.48)
hingemat.node_tree.nodes.get('Principled BSDF').inputs['Specular IOR Level'].default_value=.08
glass=fc.make_material('MAT_DISPLAY_GLASS',(0.012,0.015,0.020),0.0,0.14)
glass.diffuse_color=(0.012,0.015,0.020,0.04)
gbsdf=glass.node_tree.nodes.get('Principled BSDF'); gbsdf.inputs['Base Color'].default_value=(0.012,0.015,0.020,0.04); gbsdf.inputs['Alpha'].default_value=0.04; gbsdf.inputs['Coat Weight'].default_value=0.025; gbsdf.inputs['Coat Roughness'].default_value=0.12; gbsdf.inputs['Specular IOR Level'].default_value=.12
try: glass.surface_render_method='DITHERED'
except Exception: pass
screenmat=fc.make_screen_material('MAT_SCREEN_CONTENT',(0.002,0.003,0.006),0.65)
root=fc.empty('CTRL_MACBOOK_PRO_14',ctrl_c)
root['asset_id']='macbook_pro_14_m5'; root['stage']='LOW_DRAFT'; root['asset_version']='low_draft_0.2'
root['closed_dimensions_mm']='312.6 x 221.2 x 15.5'
base=cd.profiled_shell(fc,'BASE_UNIBODY',W,D,BASE_H,8.4*MM,
 [(z*MM,i*MM) for z,i in ((-4.15,1.8),(-3.95,1.0),(-3.55,.42),(-3.05,.08),(-2.6,0),(3.50,0),(3.85,.08),(4.08,.26),(4.15,.46))],
 metal,base_c,location=(0,0,BASE_H*.5))
base.parent=root
for poly in base.data.polygons: poly.use_smooth = poly.index >= 2
bottomcut=fc.rounded_prism('BOTTOM_PANEL_CUT',W-4.2*MM,D-4.2*MM,.75*MM,6.3*MM,None,detail_c,axis='Z',location=(0,0,.03*MM))
bpy.context.view_layer.update(); fc.boolean_difference(base,bottomcut,name='CUT_BOTTOM_PANEL_SEAT')
bottom=fc.rounded_prism('BOTTOM_PANEL',W-4.6*MM,D-4.6*MM,.30*MM,6.1*MM,metal2,detail_c,axis='Z',location=(0,0,.17*MM),edge_bevel=.00006); bottom.parent=root
keycut=fc.rounded_prism(
 'KEYBOARD_CUT',KEYBOARD['well_width_mm']*MM,KEYBOARD['well_height_mm']*MM,.85*MM,4.5*MM,None,detail_c,axis='Z',
 location=(KEYBOARD['well_center_x_mm']*MM,KEYBOARD['well_center_y_mm']*MM,BASE_H-.20*MM))
bpy.context.view_layer.update(); fc.boolean_difference(base,keycut,name='CUT_KEYBOARD_DECK')
keywell=fc.rounded_prism(
 'KEYBOARD_WELL',(KEYBOARD['well_width_mm']-.2)*MM,(KEYBOARD['well_height_mm']-.2)*MM,.12*MM,4.4*MM,wellmat,detail_c,axis='Z',
 location=(KEYBOARD['well_center_x_mm']*MM,KEYBOARD['well_center_y_mm']*MM,BASE_H-.52*MM),edge_bevel=.00004); keywell.parent=root
trackcut=fc.rounded_prism(
 'TRACKPAD_CUT',(TRACKPAD_W+1.0)*MM,(TRACKPAD['height_mm']+1.0)*MM,.42*MM,4.7*MM,None,detail_c,axis='Z',
 location=(TRACKPAD['measured_center_x_mm']*MM,TRACKPAD['center_y_mm']*MM,BASE_H-.08*MM))
bpy.context.view_layer.update(); fc.boolean_difference(base,trackcut,name='CUT_TRACKPAD_SEAT')
track_gap=fc.rounded_prism(
 'TRACKPAD_GAP',(TRACKPAD_W+.9)*MM,(TRACKPAD['height_mm']+.9)*MM,.06*MM,4.65*MM,dark,detail_c,axis='Z',
 location=(TRACKPAD['measured_center_x_mm']*MM,TRACKPAD['center_y_mm']*MM,BASE_H-.25*MM)); track_gap.parent=root
track=deck_details.trackpad(fc,detail_c,root,trackmat,BASE_H)

hinge_y=D*.5-8.5*MM
for side in (-1,1):
    x=side*(W*.5-48*MM)
    subtract_cylinder_x(base,3.90*MM,60*MM,(x,hinge_y,BASE_H+GAP))
base_bevel=base.modifiers.new('EDGE_BEVEL','BEVEL'); base_bevel.width=.00008; base_bevel.segments=3; base_bevel.limit_method='ANGLE'
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
    cover=cd.hinge_shroud(fc,f'HINGE_COVER_{"L" if side<0 else "R"}',hingemat,detail_c,hinge,x)

lid=cd.profiled_shell(fc,'LID_UNIBODY',LID_W,LID_H,LID_T,8.0*MM,
 [(y*MM,i*MM) for y,i in ((-2.35,.35),(-2.25,.14),(-2.05,.03),(-1.80,0),(1.45,0),(1.80,.08),(2.10,.28),(2.29,.55),(2.35,.82))],
 metal,lid_c,axis='Y'); lid.parent=hinge; lid.location=(0,LID_T*.5,LID_H*.5)
for poly in lid.data.polygons: poly.use_smooth = poly.index >= 2
bezel=fc.rounded_prism('DISPLAY_BEZEL',307.2*MM,204.2*MM,.28*MM,6.6*MM,bezelmat,screen_c,axis='Y',edge_bevel=.00010); bezel.parent=hinge; bezel.location=(0,-.12*MM,LID_H*.5+2.6*MM)
gasket=fc.rounded_prism('DISPLAY_GASKET',309.3*MM,207*MM,.20*MM,7.1*MM,keymat,screen_c,axis='Y',edge_bevel=.00003); gasket.parent=hinge; gasket.location=(0,-.05*MM,LID_H*.5+2.3*MM)
lower_rail=fc.rounded_prism('DISPLAY_LOWER_RAIL',307.2*MM,3.4*MM,.20*MM,.7*MM,bezelmat,screen_c,axis='Y',edge_bevel=.00003); lower_rail.parent=hinge; lower_rail.location=(0,-.12*MM,1.7*MM)
SCREEN_CENTER_Z=LID_H*.5+2.0*MM
screen=fc.rounded_prism('SCREEN_CONTENT',SCREEN_W,SCREEN_H,.12*MM,SCREEN_RADIUS,screenmat,screen_c,axis='Y'); screen.parent=hinge; screen.location=(0,-.28*MM,SCREEN_CENTER_Z)
screen_path=os.path.join(HERE,'reference','looksawful_home_3024x1964.png')
img=bpy.data.images.load(screen_path,check_existing=True); img.pack()
nodes=screenmat.node_tree.nodes; links=screenmat.node_tree.links; sbsdf=nodes.get('Principled BSDF')
tex=nodes.get('AWFUL_SCREEN_IMAGE') or nodes.new('ShaderNodeTexImage'); tex.name='AWFUL_SCREEN_IMAGE'; tex.image=img
for socket_name in ('Emission Color',):
 socket=sbsdf.inputs.get(socket_name)
 if socket:
  for old in list(socket.links): links.remove(old)
  links.new(tex.outputs['Color'],socket)
# OLED content emits the image; the separate cover glass owns reflections.
for old in list(sbsdf.inputs['Base Color'].links): links.remove(old)
sbsdf.inputs['Base Color'].default_value=(0.002,0.003,0.006,1.0)
sbsdf.inputs['Specular IOR Level'].default_value=0.0
if sbsdf.inputs.get('Emission Strength'): sbsdf.inputs['Emission Strength'].default_value=0.65
uv=screen.data.uv_layers.new(name='UVMap')
for loop in screen.data.loops:
 v=screen.data.vertices[loop.vertex_index].co; uv.data[loop.index].uv=((v.x/SCREEN_W)+.5,(v.z/SCREEN_H)+.5)
screen['screen_state']='screen_on'; screen['screen_on_emission']=0.65; screen['screen_off_emission']=0.0
screen_glass=fc.rounded_prism('SCREEN_GLASS',307.6*MM,204.6*MM,.36*MM,6.8*MM,glass,screen_c,axis='Y',edge_bevel=.00008); screen_glass.parent=hinge; screen_glass.location=(0,-.34*MM,LID_H*.5+2.6*MM)
glow_anchor=fc.empty('SCREEN_GLOW_ANCHOR',ctrl_c,location=(0,-1.2*MM,LID_H*.5+2.0*MM)); glow_anchor.parent=hinge
glow_anchor['screen_on_energy']=8.0; glow_anchor['glow_type']='rect_area'; glow_anchor['glow_width_m']=SCREEN_W; glow_anchor['glow_height_m']=SCREEN_H
root['screen_states']='screen_off,screen_on'; root['screen_glow_anchor']='SCREEN_GLOW_ANCHOR'; root['screen_glow_energy']=8.0
cd.camera_stack(fc,detail_c,hinge,SCREEN_CENTER_Z,SCREEN_H,G1['display'],bezelmat,dark)
cd.underside(fc,detail_c,root,base,W,D,BASE_H,metal2,keymat)

deck_details.keyboard(fc,detail_c,root,keymat,BASE_H)
print('MACBOOK_CONSTRUCTION_PORTS_BEGIN',flush=True)
cd.vents(fc,detail_c,root,base,W,D,dark)
deck_details.ports(fc,detail_c,root,base,W,BASE_H,dark)

# Freeze the post-mechanical, pre-speaker body for the derived runtime asset.
# The authoritative master keeps physical apertures for close evidence renders.
runtime_base=base.copy(); runtime_base.data=base.data.copy(); runtime_base.name='BASE_UNIBODY_RUNTIME_SOURCE'
detail_c.objects.link(runtime_base); runtime_base.parent=root; runtime_base.hide_render=True
runtime_base['runtime_only_source']=True
runtime_base['runtime_variant']='clean_body_plus_speaker_proxy'
deck_details.speaker_runtime_proxies(fc,detail_c,root,W,BASE_H)

print('MACBOOK_CONSTRUCTION_SPEAKERS_BEGIN',flush=True)
deck_details.speakers(fc,detail_c,root,base,W,BASE_H,dark)
print('MACBOOK_CONSTRUCTION_CUTS_END',flush=True)

for i,(x,y) in enumerate(((-W*.5+18*MM,-D*.5+17*MM),(W*.5-18*MM,-D*.5+17*MM),(-W*.5+18*MM,D*.5-20*MM),(W*.5-18*MM,D*.5-20*MM)),1):
    foot=fc.cylinder(f'FOOT_{i:02d}',5.2*MM,.75*MM,keymat,detail_c,(x,y,FOOT_BOTTOM+.375*MM),axis='Z',vertices=48); foot.parent=root


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
logo_image=tex.image
logo_w=27.676*MM; logo_h=logo_w*logo_image.size[1]/logo_image.size[0]; logo_z=LID_H*.52
verts=[(-logo_w/2,LID_T+.004*MM,logo_z-logo_h/2),(logo_w/2,LID_T+.004*MM,logo_z-logo_h/2),(logo_w/2,LID_T+.004*MM,logo_z+logo_h/2),(-logo_w/2,LID_T+.004*MM,logo_z+logo_h/2)]
mesh=bpy.data.meshes.new('APPLE_LOGO_RELEASE_MESH'); mesh.from_pydata(verts,[],[(0,1,2,3)]); mesh.update()
logo=bpy.data.objects.new('APPLE_LOGO_RELEASE',mesh); bpy.context.scene.collection.objects.link(logo); logo.parent=hinge; logo.data.materials.append(logo_mat)
uv=mesh.uv_layers.new(name='UVMap')
for loop,coord in zip(mesh.loops,((0,0),(1,0),(1,1),(0,1))): uv.data[loop.index].uv=coord
root['stage']='RELEASE_CANDIDATE'; root['release_export_target']='GLB uncompressed'; root['release_polish']='apple_logo + embedded source image'

# X/Z prisms extruded on Y reverse handedness; closed shells face outward.
for obj in list(bpy.data.objects):
    if obj.type != 'MESH': continue
    bm=bmesh.new(); bm.from_mesh(obj.data)
    if bm.faces and all(edge.is_manifold for edge in bm.edges) and bm.calc_volume(signed=True)<0:
        bmesh.ops.reverse_faces(bm,faces=list(bm.faces)); bm.to_mesh(obj.data); obj.data.update()
    bm.free()

def local_dims_mm(obj):
 xs=[v.co.x for v in obj.data.vertices]; ys=[v.co.y for v in obj.data.vertices]; zs=[v.co.z for v in obj.data.vertices]
 return {'x':(max(xs)-min(xs))/MM,'y':(max(ys)-min(ys))/MM,'z':(max(zs)-min(zs))/MM}
def non_manifold_edges(obj):
 bm=bmesh.new(); bm.from_mesh(obj.data); count=sum(1 for edge in bm.edges if not edge.is_manifold); bm.free(); return count
base_dims=local_dims_mm(base); lid_dims=local_dims_mm(lid)
base_expected={'x':312.6,'y':221.2,'z':8.3}; lid_expected={'x':312.0,'y':4.7,'z':212.0}
base_delta={k:base_dims[k]-base_expected[k] for k in base_expected}; lid_delta={k:lid_dims[k]-lid_expected[k] for k in lid_expected}
mandatory=['SCREEN_GLOW_ANCHOR','BASE_UNIBODY','LID_UNIBODY','SCREEN_CONTENT','SCREEN_GLASS','CAMERA_NOTCH','FACETIME_CAMERA','TRACKPAD','TOUCH_ID','MAGSAFE','TB_LEFT_1','TB_LEFT_2','HEADPHONE','HDMI','SDXC','TB_RIGHT','APPLE_LOGO_RELEASE','FOOT_01','SPEAKER_L_00_00','SPEAKER_R_14_04']
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
