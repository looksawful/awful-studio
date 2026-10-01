"""Runtime construction gate: physical profiles, camera layers and own-site display."""
import bpy
import bmesh
from mathutils import Vector

screen = bpy.data.materials['MAT_SCREEN_CONTENT'].node_tree.nodes['AWFUL_SCREEN_IMAGE'].image
assert screen.name.startswith('looksawful_home_3024x1964'), 'Display still uses the macOS demo instead of our site'
assert tuple(screen.size) == (3024, 1964) and screen.packed_file, 'Native offline screen capture missing'
for name in ('BASE_UNIBODY', 'LID_UNIBODY'):
    obj = bpy.data.objects[name]
    assert obj.get('profile_rings', 0) >= 8, f'{name} is still a flat extruded slab'
    bm = bmesh.new(); bm.from_mesh(obj.data)
    assert all(edge.is_manifold for edge in bm.edges), f'{name}: open shell'
    assert bm.calc_volume(signed=True) > 0, f'{name}: inward shell'
    bm.free()
assert bpy.data.objects.get('DISPLAY_GASKET'), 'Missing display seating gasket'
hinge_frame=bpy.data.objects['CTRL_HINGE']
for side in ('L','R'):
    barrel=bpy.data.objects[f'HINGE_BARREL_{side}']
    cover=bpy.data.objects[f'HINGE_COVER_{side}'].evaluated_get(bpy.context.evaluated_depsgraph_get())
    # Probe near both barrel ends: the old short sleeve left seven millimeters
    # of reflective mechanism exposed, despite passing collision checks.
    x_center=barrel.location.x
    barrel_x=[(hinge_frame.matrix_world.inverted()@(barrel.matrix_world@Vector(p))).x for p in barrel.bound_box]
    half_length=(max(barrel_x)-min(barrel_x))/2
    for end in (-1,1):
        origin=hinge_frame.matrix_world@Vector((x_center+end*(half_length-.00025),-.006,0))
        direction=hinge_frame.matrix_world.to_3x3()@Vector((0,1,0))
        hit,point,_,_=cover.ray_cast(cover.matrix_world.inverted()@origin,cover.matrix_world.inverted().to_3x3()@direction)
        assert hit, f'Exposed hinge barrel at {side} end {end}'
        local=hinge_frame.matrix_world.inverted()@(cover.matrix_world@point)
        assert -.0038<local.y<-.0033, 'Hinge shroud lost radial clearance or exceeds chassis cut'
    surface=cover.data.materials[0].node_tree.nodes.get('Principled BSDF')
    assert surface.inputs['Metallic'].default_value<=.15 and surface.inputs['Roughness'].default_value>=.4, 'External hinge still reads as a reflective metal rod'
assert len([o for o in bpy.data.objects if o.get('function_icon')]) == 12, 'Mac function row still uses F-number proxy labels'
well=bpy.data.objects['KEYBOARD_WELL']; track=bpy.data.objects['TRACKPAD']
assert min((well.matrix_world@Vector(v)).y for v in well.bound_box)-max((track.matrix_world@Vector(v)).y for v in track.bound_box) >= .004, 'Trackpad collides visually with keyboard well'
assert bpy.data.objects['KEY_03_01'].get('profile_rings', 0) >= 6, 'Keycaps still have flat block profiles'
assert bpy.data.objects['BASE_UNIBODY'].get('speaker_apertures', 0) >= 1000, 'Speaker grilles still have sparse proxy dots'
key=bpy.data.objects['KEY_03_01']
assert max(v.co.z for v in key.data.vertices)-key.data.vertices[-1].co.z >= .00005, 'Key top has no shallow dish'
base=bpy.data.objects['BASE_UNIBODY'].evaluated_get(bpy.context.evaluated_depsgraph_get())
hit,point,_,_=base.ray_cast(base.matrix_world.inverted()@Vector((0,0,-.01)),Vector((0,0,1)))
assert hit and (base.matrix_world@point).z >= .0003, 'Bottom panel is hidden behind a solid chassis cap'
for side in (-1,1):
    for index in range(12):
        hit,point,_,_=base.ray_cast(base.matrix_world.inverted()@Vector((side*.160,.0766-index*.0032,.00105)),Vector((-side,0,0)))
        assert hit and .1563-abs((base.matrix_world@point).x) >= .0015, f'Vent is an exterior plate instead of a chassis opening: {side,index}'
hit,point,_,_=base.ray_cast(base.matrix_world.inverted()@Vector((0,-.057,.02)),Vector((0,0,-1)))
assert hit and .0083-(base.matrix_world@point).z >= .0002, 'Trackpad is still placed on top of an uncut deck'
holes=0
for side in (-1,1):
    for row in range(88):
        for column in range(9):
            origin=Vector((side*.1463+(column-4)*.00068,(2+row*.82)/1000,.02))
            hit,point,_,_=base.ray_cast(base.matrix_world.inverted()@origin,Vector((0,0,-1)))
            assert hit and .0083-(base.matrix_world@point).z >= .0005, f'Speaker aperture missing at {side,row,column}'
            holes+=1
for name in ('FACETIME_LENS', 'FACETIME_SENSOR', 'CAMERA_STATUS_LED', 'AMBIENT_LIGHT_SENSOR'):
    assert bpy.data.objects.get(name), f'Missing camera layer: {name}'
lens = bpy.data.objects['FACETIME_LENS']
sensor = bpy.data.objects['FACETIME_SENSOR']
assert sensor.location.y > lens.location.y, 'Camera pupil must sit behind its cover toward the lid'
assert len([o for o in bpy.data.objects if o.name.startswith('BOTTOM_SCREW_')]) == 8, 'Missing underside fasteners'
assert bpy.data.objects.get('FRONT_FINGER_RECESS'), 'Missing front opening recess'
logo = bpy.data.objects['APPLE_LOGO_RELEASE']
assert max(v.co.z for v in logo.data.vertices)-min(v.co.z for v in logo.data.vertices) < .040, 'Logo is stretched vertically'
hinge=bpy.data.objects['CTRL_HINGE']; original=hinge.rotation_euler.x
hinge.rotation_euler.x=__import__('math').pi/2; bpy.context.view_layer.update()
points=[]
depsgraph=bpy.context.evaluated_depsgraph_get()
for obj in bpy.data.objects:
    if obj.type=='MESH':
        evaluated=obj.evaluated_get(depsgraph)
        points.extend(evaluated.matrix_world@Vector(v) for v in evaluated.bound_box)
closed=[(max(p[i] for p in points)-min(p[i] for p in points))*1000 for i in range(3)]
hinge.rotation_euler.x=original; bpy.context.view_layer.update()
assert all(abs(a-b)<=.01 for a,b in zip(closed,(312.6,221.2,15.5))), f'Complete closed assembly including feet exceeds envelope: {closed}'
print('MACBOOK_CONSTRUCTION_PASS', bpy.app.version_string, 'verified_apertures', holes)
print('MACBOOK_CLOSED_ASSEMBLY_MM',closed)
