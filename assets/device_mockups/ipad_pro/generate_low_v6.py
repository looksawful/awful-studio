import json, math, os, sys, bmesh, bpy
HERE=os.path.dirname(os.path.abspath(__file__))
COMMON=os.path.normpath(os.path.join(HERE,'..','common'))
if COMMON not in sys.path: sys.path.insert(0,COMMON)
import foundation_common as fc
MM=fc.MM
SPECS={
 '11':dict(w=177.5,h=249.7,d=5.3,sw=160.13,sh=232.32,br=9.0,sr=6.8),
 '13':dict(w=215.5,h=281.6,d=5.1,sw=199.14,sh=265.19,br=9.5,sr=7.3),
}
def arg(flag,default):
 argv=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
 return argv[argv.index(flag)+1] if flag in argv else default
SIZE=arg('--size','13')
if SIZE not in SPECS: raise ValueError(SIZE)
s=SPECS[SIZE]; W,H,D=s['w']*MM,s['h']*MM,s['d']*MM; SW,SH=s['sw']*MM,s['sh']*MM
GLASS_T=.35*MM; CORE_D=D-GLASS_T; CORE_Y=GLASS_T*.5; FRONT_Y=-D*.5+GLASS_T*.5; FRONT_SURFACE=-D*.5
OUT=os.path.abspath(arg('--out',os.path.join(HERE,'generated',f'ipad_pro_{SIZE}_m5_low_v6.blend')))
EVIDENCE=os.path.abspath(arg('--evidence',os.path.join(HERE,'evidence',f'ipad_pro_{SIZE}_m5_low_v6_validation.json')))
PREVIEWS=os.path.abspath(arg('--previews',os.path.join(HERE,'previews',SIZE,'low_v6')))
fc.clear_scene(); fc.setup_scene()
body_c=fc.make_collection(f'IPAD_PRO_{SIZE}_LOW_BODY')
detail_c=fc.make_collection(f'IPAD_PRO_{SIZE}_LOW_DETAILS')
screen_c=fc.make_collection(f'IPAD_PRO_{SIZE}_LOW_SCREEN')
ctrl_c=fc.make_collection(f'IPAD_PRO_{SIZE}_CONTROLLERS')
metal=fc.make_material('MAT_IPAD_ALUMINUM',(0.0045,0.0055,0.0080),1.0,0.30)
metal_dark=fc.make_material('MAT_IPAD_EDGE',(0.010,0.012,0.017),1.0,0.22)
black=fc.make_material('MAT_OPTICS_BLACK',(0.0005,0.0007,0.0010),0.0,0.08)
gap=fc.make_material('MAT_ASSEMBLY_GAP',(0.0003,0.0004,0.0006),0.0,0.34)
bezel=fc.make_material('MAT_DISPLAY_BEZEL',(0.0005,0.0007,0.0010),0.0,0.12)
glass=fc.make_material('MAT_DISPLAY_GLASS',(0.008,0.010,0.014),0.0,0.12)
gbsdf=glass.node_tree.nodes.get('Principled BSDF'); gbsdf.inputs['Coat Weight'].default_value=.14; gbsdf.inputs['Coat Roughness'].default_value=.10; gbsdf.inputs['Alpha'].default_value=.10
try: glass.surface_render_method='DITHERED'
except Exception: pass
optic=fc.make_material('MAT_OPTICAL_GLASS',(0.0008,0.0012,0.0020),0.0,0.025)
obsdf=optic.node_tree.nodes.get('Principled BSDF'); obsdf.inputs['Coat Weight'].default_value=.55; obsdf.inputs['Coat Roughness'].default_value=.010
front_optic=fc.make_material('MAT_FRONT_OPTIC',(0.0040,0.0060,0.0100),0.0,0.028)
fobsdf=front_optic.node_tree.nodes.get('Principled BSDF'); fobsdf.inputs['Coat Weight'].default_value=.62; fobsdf.inputs['Coat Roughness'].default_value=.012
screen_mat=fc.make_material('MAT_SCREEN_CONTENT',(0.0018,0.0026,0.0040),0.0,0.18)
screen_path=os.path.join(HERE,'reference',f'ipados26_official_screen_{SIZE}.png')
screen_tex=screen_mat.node_tree.nodes.new('ShaderNodeTexImage'); screen_tex.image=bpy.data.images.load(screen_path,check_existing=True); screen_tex.image.colorspace_settings.name='sRGB'; screen_tex.image.pack()
screen_bsdf=screen_mat.node_tree.nodes.get('Principled BSDF'); screen_mat.node_tree.links.new(screen_tex.outputs['Color'],screen_bsdf.inputs['Base Color']); screen_mat.node_tree.links.new(screen_tex.outputs['Color'],screen_bsdf.inputs['Emission Color']); screen_bsdf.inputs['Emission Strength'].default_value=.85
flash=fc.make_material('MAT_FLASH',(0.90,0.84,0.68),0.0,0.16)
body=fc.rounded_prism('BODY_ALUMINUM',W,H,CORE_D,s['br']*MM,metal,body_c,axis='Y',location=(0,CORE_Y,0),outline_segments=48)
fc.rounded_prism('DISPLAY_GLASS_SEAT',W-.30*MM,H-.30*MM,.05*MM,(s['br']-.15)*MM,gap,screen_c,axis='Y',location=(0,FRONT_Y+.025*MM,0),outline_segments=48)
fc.rounded_prism('DISPLAY_BEZEL',SW+1.3*MM,SH+1.3*MM,.08*MM,(s['sr']+.50)*MM,bezel,screen_c,axis='Y',location=(0,FRONT_Y-.04*MM,0),outline_segments=48)
screen_content=fc.rounded_prism('SCREEN_CONTENT',SW,SH,.06*MM,s['sr']*MM,screen_mat,screen_c,axis='Y',location=(0,FRONT_Y-.09*MM,0),outline_segments=48)
uv=screen_content.data.uv_layers.new(name='UVMap')
for loop in screen_content.data.loops:
    co=screen_content.data.vertices[loop.vertex_index].co
    uv.data[loop.index].uv=((co.x/SW)+0.5,(co.z/SH)+0.5)
screen_glass=fc.rounded_prism('SCREEN_GLASS',W-.45*MM,H-.45*MM,GLASS_T,(s['br']-.2)*MM,glass,screen_c,axis='Y',location=(0,FRONT_Y,0),edge_bevel=.00007,outline_segments=48)
glow_anchor=fc.empty('SCREEN_GLOW_ANCHOR',ctrl_c,location=(0,FRONT_SURFACE-1.0*MM,0))
glow_anchor['screen_on_energy']=8.0; glow_anchor['glow_type']='rect_area'; glow_anchor['glow_width_m']=SW; glow_anchor['glow_height_m']=SH
screen_content['screen_state']='screen_on'
# Landscape-edge front camera: right long edge in portrait coordinates.
fc.cylinder('FRONT_CAMERA_GLASS',1.05*MM,.022*MM,front_optic,detail_c,(W*.5-4.5*MM,FRONT_SURFACE+.012*MM,0),axis='Y',vertices=96)
fc.cylinder('FRONT_CAMERA_INNER',.55*MM,.016*MM,black,detail_c,(W*.5-4.5*MM,FRONT_SURFACE+.006*MM,0),axis='Y',vertices=64)
fc.cylinder('FRONT_CAMERA_PUPIL',.24*MM,.012*MM,front_optic,detail_c,(W*.5-4.5*MM,FRONT_SURFACE+.002*MM,0),axis='Y',vertices=48)
hs=29.0*MM; hx=-W*.5+hs*.5+5.5*MM; hz=H*.5-hs*.5-6.5*MM
housing=fc.rounded_prism('CAMERA_HOUSING',hs,hs,.82*MM,6.4*MM,metal,detail_c,axis='Y',location=(hx,D*.5+.39*MM,hz),edge_bevel=.00018,outline_segments=48)
fc.cylinder('REAR_CAMERA_RING',6.35*MM,.46*MM,metal_dark,detail_c,(hx-5.8*MM,D*.5+.86*MM,hz+5.5*MM),axis='Y',vertices=128)
fc.cylinder('REAR_CAMERA_GLASS',5.20*MM,.22*MM,optic,detail_c,(hx-5.8*MM,D*.5+1.18*MM,hz+5.5*MM),axis='Y',vertices=128)
fc.cylinder('REAR_CAMERA_INNER',3.75*MM,.12*MM,black,detail_c,(hx-5.8*MM,D*.5+1.34*MM,hz+5.5*MM),axis='Y',vertices=96)
fc.cylinder('REAR_CAMERA_PUPIL',1.55*MM,.06*MM,optic,detail_c,(hx-5.8*MM,D*.5+1.43*MM,hz+5.5*MM),axis='Y',vertices=80)
fc.cylinder('FLASH',2.75*MM,.16*MM,flash,detail_c,(hx+5.8*MM,D*.5+.92*MM,hz+5.5*MM),axis='Y',vertices=80)
fc.cylinder('LIDAR_RING',4.15*MM,.18*MM,metal_dark,detail_c,(hx-5.8*MM,D*.5+.88*MM,hz-5.5*MM),axis='Y',vertices=96)
fc.cylinder('LIDAR',3.35*MM,.14*MM,optic,detail_c,(hx-5.8*MM,D*.5+1.02*MM,hz-5.5*MM),axis='Y',vertices=96)
fc.cylinder('REAR_MIC',.55*MM,.14*MM,black,detail_c,(hx+5.8*MM,D*.5+.94*MM,hz-5.5*MM),axis='Y',vertices=48)
# Apple logo decal for product/presentation fidelity.
logo_path=os.path.join(HERE,'reference','apple_logo_alpha.png')
logo_mat=bpy.data.materials.new('MAT_APPLE_LOGO_DECAL'); logo_mat.use_nodes=True
nodes=logo_mat.node_tree.nodes; links=logo_mat.node_tree.links
for node in list(nodes): nodes.remove(node)
outn=nodes.new('ShaderNodeOutputMaterial'); lbsdf=nodes.new('ShaderNodeBsdfPrincipled'); tex=nodes.new('ShaderNodeTexImage'); tex.image=bpy.data.images.load(logo_path,check_existing=True); tex.image.pack()
lbsdf.inputs['Base Color'].default_value=(.006,.007,.009,1); lbsdf.inputs['Metallic'].default_value=.58; lbsdf.inputs['Roughness'].default_value=.20
links.new(tex.outputs['Alpha'],lbsdf.inputs['Alpha']); links.new(lbsdf.outputs['BSDF'],outn.inputs['Surface'])
try: logo_mat.surface_render_method='DITHERED'
except Exception: pass
lw,lh=18*MM,22.1*MM; verts=[(-lw/2,0,-lh/2),(lw/2,0,-lh/2),(lw/2,0,lh/2),(-lw/2,0,lh/2)]
mesh=bpy.data.meshes.new('APPLE_LOGO_MESH'); mesh.from_pydata(verts,[],[(0,1,2,3)]); mesh.update(); logo=bpy.data.objects.new('APPLE_LOGO_DECAL',mesh); detail_c.objects.link(logo); logo.location=(0,D*.5+.006*MM,0); logo.data.materials.append(logo_mat)
uv=mesh.uv_layers.new(name='UVMap')
for loop,coord in zip(mesh.loops,((0,0),(1,0),(1,1),(0,1))): uv.data[loop.index].uv=coord
boolean_cuts=[]
usb_cut=fc.rounded_cube('USB_C_CUTTER',(12.8*MM,3.2*MM,1.8*MM),.55*MM,None,detail_c)
fc.place_on_rounded_edge(usb_cut,W,H,s['br']*MM,'BOTTOM',0,outward=-.55*MM,local_normal=(0,0,1)); fc.boolean_difference(body,usb_cut,name='CUT_USB_C'); boolean_cuts.append('USB_C')
usb=fc.rounded_cube('USB_C_CAVITY',(11.3*MM,1.65*MM,.46*MM),.40*MM,black,detail_c)
fc.place_on_rounded_edge(usb,W,H,s['br']*MM,'BOTTOM',0,outward=-.24*MM,local_normal=(0,0,1))
for edge_name in ('BOTTOM','TOP'):
    for side in (-1,1):
        base_x=side*(W*.5-20*MM)
        for idx,off in enumerate((-6.0,-3.6,-1.2,1.2,3.6,6.0),1):
            x=base_x+off*MM
            cut=fc.cylinder(f'{edge_name}_{side}_{idx}_CUTTER',.58*MM,1.4*MM,None,detail_c,axis='Z',vertices=32)
            fc.place_on_rounded_edge(cut,W,H,s['br']*MM,edge_name,x,outward=-.38*MM,local_normal=(0,0,1)); fc.boolean_difference(body,cut,name=f'CUT_SPK_{edge_name}_{side}_{idx}')
            cavity=fc.cylinder(f'{edge_name}_{"L" if side<0 else "R"}_SPEAKER_{idx:02d}',.46*MM,.34*MM,black,detail_c,axis='Z',vertices=32)
            fc.place_on_rounded_edge(cavity,W,H,s['br']*MM,edge_name,x,outward=-.16*MM,local_normal=(0,0,1)); boolean_cuts.append(f'SPK_{edge_name}_{side}_{idx}')
# Physical button recesses and shallow controls.
CONTROL_PROFILE=2.26*MM
CONTROL_RECESS_CLEARANCE=.20*MM
VOLUME_LENGTH=10.06*MM
VOLUME_UP_FROM_TOP=19.33*MM
VOLUME_DOWN_FROM_TOP=31.39*MM
def edge_button(name,edge_name,coord,dims,cut_dims,normal):
    cut=fc.rounded_cube(name+'_CUTTER',cut_dims,.25*MM,None,detail_c); fc.place_on_rounded_edge(cut,W,H,s['br']*MM,edge_name,coord,outward=-.28*MM,local_normal=normal); fc.boolean_difference(body,cut,name='CUT_'+name); boolean_cuts.append(name)
    btn=fc.rounded_cube(name,dims,.12*MM,metal_dark,detail_c); fc.place_on_rounded_edge(btn,W,H,s['br']*MM,edge_name,coord,outward=.018*MM,local_normal=normal); return btn
edge_button('TOP_BUTTON','TOP',-W*.5+24*MM,(14*MM,CONTROL_PROFILE,.12*MM),(14.8*MM,CONTROL_PROFILE+CONTROL_RECESS_CLEARANCE,1.0*MM),(0,0,1))
edge_button('VOL_UP','RIGHT',H*.5-VOLUME_UP_FROM_TOP,(.12*MM,CONTROL_PROFILE,VOLUME_LENGTH),(1.0*MM,CONTROL_PROFILE+CONTROL_RECESS_CLEARANCE,10.8*MM),(1,0,0))
edge_button('VOL_DOWN','RIGHT',H*.5-VOLUME_DOWN_FROM_TOP,(.12*MM,CONTROL_PROFILE,VOLUME_LENGTH),(1.0*MM,CONTROL_PROFILE+CONTROL_RECESS_CLEARANCE,10.8*MM),(1,0,0))
bev=fc.add_bevel(body,.00018,segments=4)
for edge in body.data.edges: edge.use_edge_sharp=True
bev.harden_normals=True
for poly in body.data.polygons: poly.use_smooth=True
body_wn=body.modifiers.new('WEIGHTED_NORMAL','WEIGHTED_NORMAL'); body_wn.keep_sharp=True; body_wn.weight=50
for idx,x_mm in enumerate((-5.27,0,5.27),1):
    fc.cylinder(f'SMART_CONNECTOR_{idx}',1.35*MM,.22*MM,metal_dark,detail_c,(x_mm*MM,D*.5+.08*MM,-H*.5+12*MM),axis='Y',vertices=32)
rail=fc.rounded_cube('PENCIL_MAGNETIC_RAIL',(.04*MM,.72*MM,82*MM),.04*MM,metal_dark,detail_c)
fc.place_on_rounded_edge(rail,W,H,s['br']*MM,'RIGHT',6*MM,outward=-.012*MM,local_normal=(1,0,0))
root=fc.empty(f'CTRL_IPAD_PRO_{SIZE}',ctrl_c)
glow_anchor.parent=root
for c in (body_c,detail_c,screen_c):
    for o in c.objects: o.parent=root
root['asset_id']=f'ipad_pro_{SIZE}_m5'; root['asset_version']='low_v6_0.3'; root['stage']='LOW_DRAFT'; root['size_variant']=SIZE
root['dimensions_mm']=f"{s['w']} x {s['h']} x {s['d']}"; root['screen_object']='SCREEN_CONTENT'; root['runtime_contract']='awful-device-v1'
root['screen_texture']=f'reference/ipados26_official_screen_{SIZE}.png'; root['screen_texture_source']='Apple Support iPad User Guide, iPadOS 26 official lock screen artwork'; root['screen_texture_source_url']='https://help.apple.com/assets/698A8EFC4AF0A5C4CF042598/698A8F004AF0A5C4CF04259E/en_US/3fc0f24ff5065da6a985df207b96d8f2.png'
root['screen_state_default']='screen_on'; root['screen_on_emission_strength']=.85; root['screen_off_emission_strength']=0.0; root['screen_glow_energy']=8.0; root['screen_glow_type']='rect_area'
root['dimensional_drawing_url']=f'https://developer.apple.com/download/files/accessories/dimensional-drawings/ipad-pro-{SIZE}-inch-m5.pdf'
scene=bpy.context.scene; scene.render.resolution_x=1600; scene.render.resolution_y=1600; scene.render.resolution_percentage=100; scene.view_settings.exposure=-1.05
scene.world.use_nodes=True; bg=scene.world.node_tree.nodes.get('Background'); bg.inputs['Color'].default_value=(.001,.001,.001,1); bg.inputs['Strength'].default_value=.025
studio=fc.make_collection('_STUDIO_RIG')
fc.add_area_light('KEY_SOFTBOX',(.42,-.30,.46),115,.24,studio,target=(0,0,.02)); fc.add_area_light('FILL_SOFTBOX',(-.38,-.18,.04),24,.30,studio,target=(0,0,0)); fc.add_area_light('RIM_STRIP',(.38,.42,.24),120,.12,studio,target=(0,0,.02)); fc.add_area_light('TOP_STRIP',(-.18,.06,.58),52,.18,studio,target=(0,0,.04))
cams=fc.make_collection('_DIAGNOSTIC_CAMERAS')
def persp(name,location,target,lens=82):
    d=bpy.data.cameras.new(name); d.type='PERSP'; d.lens=lens; d.sensor_width=36; d.clip_start=.0005; d.clip_end=10.0; c=bpy.data.objects.new(name,d); c.location=location; c.rotation_euler=(fc.Vector(target)-fc.Vector(location)).to_track_quat('-Z','Y').to_euler(); cams.objects.link(c); return c
cam_front=persp('CAM_FRONT',(0,-.72,0),(0,0,0),88); cam_back=persp('CAM_BACK',(0,.72,0),(0,0,0),88)
cam_three=persp('CAM_THREE_QUARTER',(W*.72,-H*.62,H*.30),(0,0,.01),82); cam_camera=persp('CAM_CAMERA_MACRO',(hx-.055,.18,hz+.055),(hx,D*.006,hz),110)
cam_port=persp('CAM_PORT_MACRO',(0,-.020,-H*.5-.050),(0,0,-H*.5),115); cam_side=persp('CAM_SIDE_CONTROLS',(W*.72,-.16,H*.24),(W*.49,0,H*.24),105)
cam_front_camera=persp('CAM_FRONT_CAMERA',(W*.5-4.5*MM,-.022,0),(W*.5-4.5*MM,FRONT_SURFACE,0),165)
bpy.context.view_layer.update()
assembly=(body,screen_glass); mins=[1e9]*3; maxs=[-1e9]*3
for obj in assembly:
    for corner in obj.bound_box:
        p=obj.matrix_world@fc.Vector(corner)
        for a in range(3): mins[a]=min(mins[a],p[a]); maxs[a]=max(maxs[a],p[a])
actual={'width':(maxs[0]-mins[0])/MM,'depth':(maxs[1]-mins[1])/MM,'height':(maxs[2]-mins[2])/MM}
expected={'width':s['w'],'depth':s['d'],'height':s['h']}; delta={k:actual[k]-expected[k] for k in expected}
bm=bmesh.new(); bm.from_mesh(body.data); non_manifold=sum(1 for e in bm.edges if not e.is_manifold); bm.free()
mandatory=['CAMERA_HOUSING','REAR_CAMERA_GLASS','LIDAR','REAR_MIC','USB_C_CAVITY','DISPLAY_BEZEL','SCREEN_GLASS','PENCIL_MAGNETIC_RAIL','APPLE_LOGO_DECAL','FRONT_CAMERA_GLASS','FRONT_CAMERA_PUPIL','TOP_BUTTON','VOL_UP','VOL_DOWN']
missing=[n for n in mandatory if bpy.data.objects.get(n) is None]
passed=non_manifold==0 and not missing and len(boolean_cuts)==28 and all(abs(v)<=.01 for v in delta.values())
evidence={'asset_id':f'ipad_pro_{SIZE}_m5','stage':'LOW_DRAFT','blender_version':bpy.app.version_string,
          'expected_mm':expected,'actual_mm':{k:round(v,6) for k,v in actual.items()},
          'delta_mm':{k:round(v,6) for k,v in delta.items()},'body_non_manifold_edges':non_manifold,
          'mandatory_missing':missing,'object_count':len(bpy.data.objects),'material_count':len(bpy.data.materials),'passed':passed}
evidence['boolean_cut_count']=len(boolean_cuts); evidence['boolean_cuts']=boolean_cuts
os.makedirs(os.path.dirname(EVIDENCE),exist_ok=True)
with open(EVIDENCE,'w',encoding='utf-8') as f: json.dump(evidence,f,indent=2)
fc.save_blend(OUT)
renders=(
 (cam_front,f'ipad_pro_{SIZE}_low_v6_front.png'),
 (cam_back,f'ipad_pro_{SIZE}_low_v6_back.png'),
 (cam_three,f'ipad_pro_{SIZE}_low_v6_three_quarter.png'),
 (cam_camera,f'ipad_pro_{SIZE}_low_v6_camera_macro.png'),
 (cam_port,f'ipad_pro_{SIZE}_low_v6_port_macro.png'),
 (cam_side,f'ipad_pro_{SIZE}_low_v6_side_controls.png'),
 (cam_front_camera,f'ipad_pro_{SIZE}_low_v6_front_camera_macro.png'),
)
def set_light(name, energy):
    obj=bpy.data.objects.get(name)
    if obj and getattr(obj,"data",None): obj.data.energy=energy

def render_profile(cam, filename):
    if "front_camera_macro" in filename:
        profile=(-0.18,{"KEY_SOFTBOX":95,"FILL_SOFTBOX":68,"RIM_STRIP":28,"TOP_STRIP":24})
    elif "port_macro" in filename:
        profile=(-0.20,{"KEY_SOFTBOX":112,"FILL_SOFTBOX":62,"RIM_STRIP":35,"TOP_STRIP":42})
    elif "side_controls" in filename:
        profile=(-0.42,{"KEY_SOFTBOX":72,"FILL_SOFTBOX":34,"RIM_STRIP":54,"TOP_STRIP":32})
    elif "camera_macro" in filename or "back" in filename:
        profile=(-0.54,{"KEY_SOFTBOX":42,"FILL_SOFTBOX":20,"RIM_STRIP":46,"TOP_STRIP":26})
    elif "three_quarter" in filename:
        profile=(-0.18,{"KEY_SOFTBOX":0,"FILL_SOFTBOX":42,"RIM_STRIP":86,"TOP_STRIP":58})
    else:
        profile=(-0.26,{"KEY_SOFTBOX":18,"FILL_SOFTBOX":28,"RIM_STRIP":70,"TOP_STRIP":34})
    scene.view_settings.exposure=profile[0]
    for n,e in profile[1].items(): set_light(n,e)
    fc.render_camera(cam,os.path.join(PREVIEWS,filename))
for cam,filename in renders: render_profile(cam,filename)
print('AWFUL_LOW_VALIDATION',json.dumps(evidence,sort_keys=True))
if not passed: raise RuntimeError(f'iPad Pro {SIZE} LOW v6 validation failed')
