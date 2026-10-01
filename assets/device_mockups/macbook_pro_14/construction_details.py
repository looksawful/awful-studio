"""Reference-led construction profiles. Local dimensions are LOW estimates in metres."""
import bpy
import bmesh
import math


def hinge_shroud(fc, name, material, collection, hinge, x):
    """Closed sleeve around the pivot, with a shallow flat on its visible face.

    Local radii/length are estimates. The complete cross section remains inside
    the existing 3.9 mm chassis relief and outside the 3.3 mm pivot.
    """
    mm=fc.MM; count=64; vertices=[]
    for end in (-30*mm,30*mm):
        for radius in (3.65*mm,3.42*mm):
            for index in range(count):
                angle=2*math.pi*index/count
                y=radius*math.cos(angle)
                if radius>3.5*mm: y=max(y,-3.46*mm)
                vertices.append((end,y,radius*math.sin(angle)))
    faces=[]
    for index in range(count):
        j=(index+1)%count
        faces.extend(((index,j,2*count+j,2*count+index),
                      (count+index,3*count+index,3*count+j,count+j),
                      (index,count+index,count+j,j),
                      (2*count+index,2*count+j,3*count+j,3*count+index)))
    mesh=bpy.data.meshes.new(name+'_SLEEVE'); mesh.from_pydata(vertices,[],faces); mesh.update()
    bm=bmesh.new(); bm.from_mesh(mesh); bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces)); bm.to_mesh(mesh); bm.free()
    mesh.materials.append(material)
    for polygon in mesh.polygons: polygon.use_smooth=polygon.index%4<2
    obj=bpy.data.objects.new(name,mesh); collection.objects.link(obj)
    obj.parent=hinge; obj.location=(x,0,0)
    bevel=obj.modifiers.new('SHROUD_EDGE','BEVEL'); bevel.width=.025*mm; bevel.segments=2
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


def camera_stack(fc, collection, hinge, lid_height, bezel, dark):
    mm = fc.MM
    # Black notch joins the top bezel; optics face the viewer on local -Y.
    notch = fc.rounded_prism('CAMERA_NOTCH', 32*mm, 8.2*mm, .15*mm, 2.8*mm, bezel, collection, axis='Y')
    notch.parent = hinge; notch.location = (0, -.57*mm, lid_height-4.7*mm)
    optical = fc.make_glass_material('MAT_FACETIME_OPTICAL', (.009, .022, .041), .06, .92, 1.52)
    coating = fc.make_material('MAT_FACETIME_COATING', (.018, .045, .095), .28, .10)
    for name, radius, depth, y, mat in (
        ('FACETIME_CAMERA', 1.18, .10, -.69, dark),
        ('FACETIME_SENSOR', .72, .04, -.755, dark),
        ('FACETIME_LENS', .98, .06, -.82, optical),
        ('FACETIME_INNER_LENS', .49, .015, -.788, coating),
    ):
        obj = fc.cylinder(name, radius*mm, depth*mm, mat, collection, axis='Y', vertices=64)
        obj.parent = hinge; obj.location = (0, y*mm, lid_height-4.7*mm)
    for name, x, radius in (('CAMERA_STATUS_LED', 3.4, .19), ('AMBIENT_LIGHT_SENSOR', -5.6, .40)):
        obj = fc.cylinder(name, radius*mm, .025*mm, dark, collection, axis='Y', vertices=32)
        obj.parent = hinge; obj.location = (x*mm, -.675*mm, lid_height-4.7*mm)


def underside(fc, collection, root, base, width, depth, base_height, metal, rubber):
    mm = fc.MM
    cutter = fc.rounded_cube('OPENING_CUT', (36*mm, 6*mm, 3.1*mm), 1.0*mm, None, collection,
                             (0, -depth/2+1.0*mm, base_height-.2*mm))
    bpy.context.view_layer.update(); fc.boolean_difference(base, cutter, name='CUT_FRONT_OPENING')
    recess = fc.empty('FRONT_FINGER_RECESS', collection, (0, -depth/2, base_height-1.4*mm)); recess.parent = root
    positions = [(-width/2+15*mm, -depth/2+11*mm), (width/2-15*mm, -depth/2+11*mm),
                 (-width/2+15*mm, depth/2-11*mm), (width/2-15*mm, depth/2-11*mm),
                 (-55*mm, -depth/2+11*mm), (55*mm, -depth/2+11*mm),
                 (-55*mm, depth/2-11*mm), (55*mm, depth/2-11*mm)]
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
