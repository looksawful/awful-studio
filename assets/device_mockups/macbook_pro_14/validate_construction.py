"""Runtime construction gate: physical profiles, camera layers and own-site display."""
import bpy
import bmesh
import os, sys
from mathutils import Vector
sys.path.insert(0, os.path.dirname(__file__))
from geometry_contract import CHASSIS_FACTS, G2_EXTERNAL_FACTS, G2_DISPLAY_FACTS, derive_metric_measurements, release_display_measurements, require_frozen_fact

G1 = derive_metric_measurements()

def world_bounds_mm(objects):
    points = [
        obj.matrix_world @ Vector(corner)
        for obj in objects
        for corner in obj.bound_box
    ]
    mins = [min(point[axis] for point in points) * 1000 for axis in range(3)]
    maxs = [max(point[axis] for point in points) * 1000 for axis in range(3)]
    return {
        "min": mins,
        "max": maxs,
        "dims": [maxs[axis] - mins[axis] for axis in range(3)],
        "center": [(mins[axis] + maxs[axis]) / 2 for axis in range(3)],
    }


def bounds_in_frame_mm(objects, frame):
    inv = frame.matrix_world.inverted()
    points = [
        inv @ (obj.matrix_world @ Vector(corner))
        for obj in objects
        for corner in obj.bound_box
    ]
    mins = [min(point[axis] for point in points) * 1000 for axis in range(3)]
    maxs = [max(point[axis] for point in points) * 1000 for axis in range(3)]
    return {
        "min": mins,
        "max": maxs,
        "dims": [maxs[axis] - mins[axis] for axis in range(3)],
        "center": [(mins[axis] + maxs[axis]) / 2 for axis in range(3)],
    }

def assert_close(actual, expected, tolerance, label):
    assert abs(actual - expected) <= tolerance, (
        f"{label}: actual {actual:.4f} mm, expected {expected:.4f} +/- {tolerance:.4f} mm"
    )

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
surround=bpy.data.objects.get('DISPLAY_SURROUND_VISUAL')
assert surround, 'Missing explicit non-authoritative display surround'
assert surround.get('geometry_authority') == 'RELATIONAL_VISUAL'
assert surround.get('unverified_dimensions') == 'outer_corner_radius,visual_plane_thickness'
display_target=release_display_measurements()
display_frame=bpy.data.objects['CTRL_HINGE']
screen_obj=bpy.data.objects['SCREEN_CONTENT']
screen_bounds=bounds_in_frame_mm([screen_obj], display_frame)
assert_close(screen_bounds['dims'][0], display_target['active_width_mm'], .10, 'active display width')
assert_close(screen_bounds['dims'][2], display_target['active_height_mm'], .10, 'active display height')
notch=bpy.data.objects['CAMERA_NOTCH']
notch_bounds=bounds_in_frame_mm([notch], display_frame)
assert_close(notch_bounds['dims'][0], display_target['notch_top_width_mm'], .20, 'display notch width')
assert_close(notch_bounds['dims'][2], display_target['notch_height_mm'], .20, 'display notch height')
camera=bpy.data.objects['FACETIME_CAMERA']
camera_in_frame=display_frame.matrix_world.inverted() @ camera.matrix_world.translation
assert_close(camera_in_frame.x*1000, display_target['camera_center_x_mm'], .20, 'camera center X')
hinge_frame=bpy.data.objects['CTRL_HINGE']
chassis_rear_mm = CHASSIS_FACTS['depth'].value_mm / 2
for side in ('L','R'):
    barrel=bpy.data.objects[f'HINGE_BARREL_{side}']
    cover=bpy.data.objects[f'HINGE_COVER_{side}']
    assert cover.get('g2_role') == 'display_hinge_cover'
    dims=[d*1000 for d in cover.dimensions]
    assert abs(dims[0]-require_frozen_fact(G2_EXTERNAL_FACTS,'hinge_cover_width_mm')) <= 2.0
    assert cover.get('geometry_authority') == 'UNVERIFIED_VISUAL'
    assert cover.get('unverified_dimensions') == 'depth,thickness'
    assert abs(abs(cover.location.x*1000)-require_frozen_fact(G2_EXTERNAL_FACTS,'hinge_cover_center_abs_x_mm')) <= 2.0
    cover_world=[cover.matrix_world@Vector(p) for p in cover.bound_box]
    barrel_world=[barrel.matrix_world@Vector(p) for p in barrel.bound_box]
    assert max(p.y for p in cover_world)*1000 <= chassis_rear_mm + .05
    assert max(p.y for p in barrel_world)*1000 <= chassis_rear_mm + .05
    surface=cover.data.materials[0].node_tree.nodes.get('Principled BSDF')
    assert surface.inputs['Metallic'].default_value<=.15 and surface.inputs['Roughness'].default_value>=.4
assert len([o for o in bpy.data.objects if o.get('function_icon')]) == 12, 'Mac function row still uses F-number proxy labels'

# G2 geometry acceptance must inspect generated world-space meshes, not just contract constants.
keys = [obj for obj in bpy.data.objects if obj.get('key_label') is not None]
assert len(keys) == 78, f'Expected 78 generated key meshes, got {len(keys)}'
keyboard_bounds = world_bounds_mm(keys)
keyboard_target = G1['keyboard']
assert_close(keyboard_bounds['dims'][0], keyboard_target['bounds_width_mm'], .80, 'keyboard aggregate width')
assert_close(keyboard_bounds['dims'][1], keyboard_target['bounds_height_mm'], .80, 'keyboard aggregate depth')
assert_close(keyboard_bounds['center'][0], keyboard_target['bounds_center_x_mm'], .45, 'keyboard aggregate center X')
assert_close(keyboard_bounds['center'][1], keyboard_target['bounds_center_y_mm'], .45, 'keyboard aggregate center Y')

well=bpy.data.objects['KEYBOARD_WELL']; track=bpy.data.objects['TRACKPAD']
well_bounds = world_bounds_mm([well])
assert_close(well_bounds['dims'][0], keyboard_target['well_width_mm']-.2, .40, 'keyboard well width')
assert_close(well_bounds['dims'][1], keyboard_target['well_height_mm']-.2, .40, 'keyboard well depth')
assert_close(well_bounds['center'][0], keyboard_target['well_center_x_mm'], .35, 'keyboard well center X')
assert_close(well_bounds['center'][1], keyboard_target['well_center_y_mm'], .35, 'keyboard well center Y')

track_bounds = world_bounds_mm([track])
track_target = G1['trackpad']
assert_close(track_bounds['dims'][0], track_target['width_mm'], .45, 'trackpad width')
assert_close(track_bounds['dims'][1], track_target['height_mm'], .45, 'trackpad depth')
assert_close(track_bounds['center'][0], track_target['target_center_x_mm'], .30, 'trackpad center X')
assert_close(track_bounds['center'][1], track_target['center_y_mm'], .35, 'trackpad center Y')
chassis_front_y = -CHASSIS_FACTS['depth'].value_mm / 2
assert_close(track_bounds['min'][1]-chassis_front_y, track_target['front_gap_mm'], .45, 'trackpad front gap')

touch = bpy.data.objects['TOUCH_ID']
touch_bounds = world_bounds_mm([touch])
touch_target = G1['touch_id']
assert_close(touch_bounds['dims'][0], touch_target['outer_width_mm'], .45, 'Touch ID width')
assert_close(touch_bounds['dims'][1], touch_target['outer_height_mm'], .45, 'Touch ID depth')
assert_close(touch_bounds['center'][0], touch_target['center_x_mm'], .40, 'Touch ID center X')
assert_close(touch_bounds['center'][1], touch_target['center_y_mm'], .40, 'Touch ID center Y')
actual_gap_mm = (
    min((well.matrix_world@Vector(v)).y for v in well.bound_box)
    - max((track.matrix_world@Vector(v)).y for v in track.bound_box)
) * 1000
expected_gap_mm = G1['keyboard']['trackpad_gap_mm']
assert abs(actual_gap_mm-expected_gap_mm) <= .75, (
    f'Trackpad/keyboard gap drift: actual {actual_gap_mm:.3f} mm, '
    f'calibrated {expected_gap_mm:.3f} mm'
)
assert bpy.data.objects['KEY_03_01'].get('profile_rings', 0) >= 6, 'Keycaps still have flat block profiles'
base_source = bpy.data.objects['BASE_UNIBODY']
expected_speaker_points = G1['speaker']['grid_rows'] * G1['speaker']['grid_columns'] * 2
assert base_source.get('speaker_pattern_count') == expected_speaker_points
assert base_source.get('speaker_visual') == 'derived_alpha_normal_proxy'
for suffix in ('L', 'R'):
    proxy = bpy.data.objects[f'SPEAKER_MASTER_PROXY_{suffix}']
    assert not proxy.hide_render
    assert proxy.get('surface_family') == 'speaker_alpha_normal'
    proxy_bounds = world_bounds_mm([proxy])
    speaker_target = G1['speaker']
    assert_close(proxy_bounds['dims'][0], speaker_target['observed_width_mm'], .40, f'speaker {suffix} width')
    assert_close(proxy_bounds['dims'][1], speaker_target['observed_height_mm'], .40, f'speaker {suffix} depth')
    assert_close(abs(proxy_bounds['center'][0]), speaker_target['field_center_abs_x_mm'], .35, f'speaker {suffix} center X')
    assert_close(proxy_bounds['center'][1], speaker_target['field_center_y_mm'], .35, f'speaker {suffix} center Y')
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
speaker = G1['speaker']
speaker_points = speaker['grid_rows'] * speaker['grid_columns'] * 2
for name in ('FACETIME_LENS', 'FACETIME_SENSOR', 'CAMERA_STATUS_LED', 'AMBIENT_LIGHT_SENSOR'):
    assert bpy.data.objects.get(name), f'Missing camera layer: {name}'
lens = bpy.data.objects['FACETIME_LENS']
sensor = bpy.data.objects['FACETIME_SENSOR']
assert sensor.location.y > lens.location.y, 'Camera pupil must sit behind its cover toward the lid'
screws=[o for o in bpy.data.objects if o.name.startswith('BOTTOM_SCREW_')]
assert len(screws) == 8, 'Missing underside fasteners'
front_y = -CHASSIS_FACTS['depth'].value_mm/2 + require_frozen_fact(G2_EXTERNAL_FACTS,'front_screw_edge_inset_mm')
rear_y = CHASSIS_FACTS['depth'].value_mm/2 - require_frozen_fact(G2_EXTERNAL_FACTS,'rear_screw_edge_inset_mm')
front_outer_x = CHASSIS_FACTS['width'].value_mm/2 - require_frozen_fact(G2_EXTERNAL_FACTS,'front_outer_screw_side_inset_mm')
rear_outer_x = CHASSIS_FACTS['width'].value_mm/2 - require_frozen_fact(G2_EXTERNAL_FACTS,'rear_outer_screw_side_inset_mm')
inner_x = require_frozen_fact(G2_EXTERNAL_FACTS,'inner_screw_center_abs_x_mm')
expected_screws = [
    (-front_outer_x, front_y), (front_outer_x, front_y),
    (-rear_outer_x, rear_y), (rear_outer_x, rear_y),
    (-inner_x, front_y), (inner_x, front_y),
    (-inner_x, rear_y), (inner_x, rear_y),
]
actual_screws = [(obj.matrix_world.translation.x*1000, obj.matrix_world.translation.y*1000) for obj in screws]
for ex, ey in expected_screws:
    nearest = min(((ax-ex)**2 + (ay-ey)**2)**.5 for ax, ay in actual_screws)
    assert nearest <= .30, f'bottom screw missing near ({ex:.2f},{ey:.2f}); nearest {nearest:.3f} mm'

recess=bpy.data.objects.get('FRONT_FINGER_RECESS')
assert recess, 'Missing front opening recess'
assert abs(recess.get('width_mm',0)-require_frozen_fact(G2_EXTERNAL_FACTS,'front_finger_recess_width_mm')) <= .1

feet=[bpy.data.objects[f'FOOT_{i:02d}'] for i in range(1,5)]
foot_diameter=require_frozen_fact(G2_EXTERNAL_FACTS,'foot_diameter_mm')
foot_x = CHASSIS_FACTS['width'].value_mm/2 - require_frozen_fact(G2_EXTERNAL_FACTS,'foot_side_inset_mm')
foot_y = CHASSIS_FACTS['depth'].value_mm/2 - require_frozen_fact(G2_EXTERNAL_FACTS,'foot_edge_inset_mm')
expected_feet={(-foot_x,-foot_y),(foot_x,-foot_y),(-foot_x,foot_y),(foot_x,foot_y)}
actual_feet=set()
for foot in feet:
    assert abs(foot.dimensions.x*1000-foot_diameter) <= .15
    assert abs(foot.dimensions.y*1000-foot_diameter) <= .15
    actual_feet.add((round(foot.matrix_world.translation.x*1000,3),round(foot.matrix_world.translation.y*1000,3)))
for ex,ey in expected_feet:
    nearest=min(((ax-ex)**2+(ay-ey)**2)**.5 for ax,ay in actual_feet)
    assert nearest <= .30, f'foot missing near ({ex:.2f},{ey:.2f}); nearest {nearest:.3f} mm'

logo = bpy.data.objects['APPLE_LOGO_RELEASE']
logo_width_mm=(max(v.co.x for v in logo.data.vertices)-min(v.co.x for v in logo.data.vertices))*1000
logo_height_mm=(max(v.co.z for v in logo.data.vertices)-min(v.co.z for v in logo.data.vertices))*1000
assert abs(logo_width_mm-require_frozen_fact(G2_EXTERNAL_FACTS,'logo_width_mm')) <= .25
assert 40.0 <= logo_height_mm <= 48.0
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
print('MACBOOK_CONSTRUCTION_PASS', bpy.app.version_string, 'verified_speaker_points', speaker_points)
print('MACBOOK_CLOSED_ASSEMBLY_MM',closed)
