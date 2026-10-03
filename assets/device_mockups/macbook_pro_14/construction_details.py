"""Reference-led construction profiles. Local dimensions are LOW estimates in metres."""
import bpy
import bmesh
import math
from geometry_contract import G2_EXTERNAL_FACTS, G2_PROVISIONAL_FACTS, require_frozen_fact


def hinge_shroud(fc, name, material, collection, hinge, x):
    """Fixed top-case display-hinge cover from the Apple repair-view relation."""
    mm = fc.MM
    width = require_frozen_fact(G2_EXTERNAL_FACTS, "hinge_cover_width_mm") * mm
    depth = G2_PROVISIONAL_FACTS["hinge_cover_depth_mm"].value_mm * mm
    thickness = G2_PROVISIONAL_FACTS["hinge_cover_thickness_mm"].value_mm * mm
    root = hinge.parent
    obj = fc.rounded_prism(
        name,
        width,
        depth,
        thickness,
        2.2 * mm,
        material,
        collection,
        axis='Z',
        location=(x, hinge.location.y - depth * .5, hinge.location.z - thickness * .55),
        edge_bevel=.00008,
    )
    obj.parent = root
    obj['g2_role'] = 'display_hinge_cover'
    obj['source_relation'] = 'apple_repair_display_hinge_cover'
    obj['geometry_authority'] = 'UNVERIFIED_VISUAL'
    obj['unverified_dimensions'] = 'depth,thickness'
    return obj


def profiled_shell(fc, name, width, height, depth, radius, rings, material, collection, axis='Z', location=(0, 0, 0)):
    vertices = []
    for position, inset in rings:
        outline = fc.rounded_outline(width-2*inset, height-2*inset, max(radius-inset, .0001), segments=24)
        vertices.extend((x, position, y) if axis == 'Y' else (x, y, position) for x, y in outline)
    count = len(outline)
    faces = [tuple(reversed(range(count))), tuple(range((len(rings)-1)*count, len(rings)*count))]
    for layer in range(len(rings)-1):
        for index in range(count):
            a = layer*count+index; b = layer*count+(index+1) % count
            faces.append((a, b, b+count, a+count))
    mesh = bpy.data.meshes.new(name+'_PROFILE'); mesh.from_pydata(vertices, [], faces); mesh.update()
    bm = bmesh.new(); bm.from_mesh(mesh); bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces)); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh); collection.objects.link(obj); obj.location = location
    mesh.materials.append(material)
    for polygon in mesh.polygons: polygon.use_smooth = polygon.index >= 2
    obj['profile_rings'] = len(rings)
    obj['profile_units'] = 'metres; estimated radii, verified outer envelope'
    return obj


def camera_stack(fc, collection, hinge, screen_center_z, screen_height, display, bezel, dark):
    mm = fc.MM
    notch_w = display['notch_top_width_mm']
    notch_h = display['notch_height_mm']
    notch_radius = min(display['notch_lower_radius_mm'], notch_h/2)
    screen_top_z = screen_center_z + screen_height/2
    notch_center_z = screen_top_z - notch_h*mm/2
    camera_x = display['camera_center_x_mm']*mm
    camera_z = screen_top_z - display['camera_from_top_mm']*mm
    # Black notch intrudes from the calibrated active-display top edge.
    notch = fc.rounded_prism(
        'CAMERA_NOTCH', notch_w*mm, notch_h*mm, .15*mm, notch_radius*mm,
        bezel, collection, axis='Y')
    notch.parent = hinge; notch.location = (0, -.57*mm, notch_center_z)
    optical = fc.make_glass_material('MAT_FACETIME_OPTICAL', (.009, .022, .041), .06, .92, 1.52)
    coating = fc.make_material('MAT_FACETIME_COATING', (.018, .045, .095), .28, .10)
    for name, radius, depth, y, mat in (
        ('FACETIME_CAMERA', 1.18, .10, -.69, dark),
        ('FACETIME_SENSOR', .72, .04, -.755, dark),
        ('FACETIME_LENS', .98, .06, -.82, optical),
        ('FACETIME_INNER_LENS', .49, .015, -.788, coating),
    ):
        obj = fc.cylinder(name, radius*mm, depth*mm, mat, collection, axis='Y', vertices=64)
        obj.parent = hinge; obj.location = (camera_x, y*mm, camera_z)
    for name, x_offset, radius in (
        ('CAMERA_STATUS_LED', 3.4, .19),
        ('AMBIENT_LIGHT_SENSOR', -5.6, .40),
    ):
        obj = fc.cylinder(name, radius*mm, .025*mm, dark, collection, axis='Y', vertices=32)
        obj.parent = hinge; obj.location = (camera_x+x_offset*mm, -.675*mm, camera_z)


def underside(fc, collection, root, base, width, depth, base_height, metal, rubber):
    mm = fc.MM
    recess_width_mm = require_frozen_fact(G2_EXTERNAL_FACTS, "front_finger_recess_width_mm")
    recess_w = recess_width_mm * mm
    cutter = fc.rounded_cube(
        'OPENING_CUT',
        (recess_w, 6*mm, 3.1*mm),
        1.0*mm,
        None,
        collection,
        (0, -depth/2+1.0*mm, base_height-.2*mm),
    )
    bpy.context.view_layer.update(); fc.boolean_difference(base, cutter, name='CUT_FRONT_OPENING')
    recess = fc.empty('FRONT_FINGER_RECESS', collection, (0, -depth/2, base_height-1.4*mm))
    recess.parent = root
    recess['width_mm'] = recess_width_mm

    front_y = -depth/2 + require_frozen_fact(G2_EXTERNAL_FACTS, "front_screw_edge_inset_mm")*mm
    rear_y = depth/2 - require_frozen_fact(G2_EXTERNAL_FACTS, "rear_screw_edge_inset_mm")*mm
    front_outer_x = width/2 - require_frozen_fact(G2_EXTERNAL_FACTS, "front_outer_screw_side_inset_mm")*mm
    rear_outer_x = width/2 - require_frozen_fact(G2_EXTERNAL_FACTS, "rear_outer_screw_side_inset_mm")*mm
    inner_x = require_frozen_fact(G2_EXTERNAL_FACTS, "inner_screw_center_abs_x_mm")*mm
    positions = [
        (-front_outer_x, front_y), (front_outer_x, front_y),
        (-rear_outer_x, rear_y), (rear_outer_x, rear_y),
        (-inner_x, front_y), (inner_x, front_y),
        (-inner_x, rear_y), (inner_x, rear_y),
    ]
    for index, (x, y) in enumerate(positions):
        obj = fc.cylinder(f'BOTTOM_SCREW_{index:02d}', 1.1*mm, .12*mm, metal, collection,
                          (x, y, .035*mm), axis='Z', vertices=40); obj.parent = root
        slot = fc.cylinder(f'SCREW_SOCKET_{index:02d}', .40*mm, .012*mm, rubber, collection,
                           (x, y, -.032*mm), axis='Z', vertices=6); slot.parent = root


def vents(fc, collection, root, base, width, depth, dark):
    mm=fc.MM
    for side in (-1,1):
        for index in range(12):
            y=depth/2-34*mm-index*3.2*mm
            cutter=fc.rounded_cube('VENT_CUT', (3*mm,2*mm,.55*mm),.13*mm,None,collection,
                                   (side*(width/2-1.1*mm),y,1.05*mm))
            bpy.context.view_layer.update(); fc.boolean_difference(base,cutter,name='CUT_VENT')
            backing=fc.rounded_cube(f'VENT_{"L" if side<0 else "R"}_{index:02d}',(.16*mm,1.8*mm,.40*mm),.04*mm,dark,collection,
                                    (side*(width/2-2.45*mm),y,1.05*mm)); backing.parent=root
