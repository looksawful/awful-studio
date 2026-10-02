"""Estimated ANSI layout and physical port interiors, in the metric chassis."""
import math
import bpy
import bmesh
from mathutils import Matrix
from construction_details import profiled_shell
import function_legends
from port_layout import PORTS


SPEAKER_ROWS = 88
SPEAKER_COLS = 9
SPEAKER_ROW_PITCH_MM = .82
SPEAKER_COL_PITCH_MM = .68
SPEAKER_HOLE_RADIUS_MM = .20
SPEAKER_FIELD_WIDTH_MM = 6.2
SPEAKER_FIELD_HEIGHT_MM = 73.0
SPEAKER_CENTER_Y_MM = 37.67


def _weighted_normals(obj, weight=50):
    modifier = obj.modifiers.new('WEIGHTED_NORMAL', 'WEIGHTED_NORMAL')
    modifier.keep_sharp = True
    modifier.weight = weight
    return modifier


def trackpad(fc, collection, root, material, base_height):
    mm = fc.MM
    obj = profiled_shell(
        fc, 'TRACKPAD', 132*mm, 80*mm, .20*mm, 4.6*mm,
        [(z*mm, inset*mm) for z, inset in (
            (-.10, .42), (-.075, .16), (-.035, .03),
            (.045, 0), (.085, .12), (.10, .38),
        )],
        material, collection, axis='Z',
        location=(0, -57*mm, base_height-.10*mm),
    )
    obj.parent = root
    obj['surface_family'] = 'glass_trackpad'
    obj['master_runtime_shared'] = True
    _weighted_normals(obj, 55)
    return obj


def _key_family(label, width, height):
    if label == 'space':
        return 'space'
    if label in {'←', '↓', '→', '↑'} or height < 10:
        return 'arrow'
    if label == 'Touch ID':
        return 'touch_id'
    if label.startswith('F') and label[1:].isdigit():
        return 'function'
    if width > 20 or label in {'fn', 'control', 'option', 'command', 'shift', 'caps', 'return', 'tab', 'delete'}:
        return 'modifier'
    return 'regular'


def _key_profile(family):
    profiles = {
        'regular': ((-.41,.36),(-.28,.05),(.16,0),(.34,.10),(.41,.30),(.37,.70),(.30,1.05)),
        'modifier': ((-.41,.34),(-.28,.04),(.17,0),(.34,.09),(.41,.28),(.37,.62),(.31,.90)),
        'space': ((-.41,.30),(-.28,.03),(.18,0),(.34,.07),(.40,.24),(.37,.50),(.33,.72)),
        'arrow': ((-.41,.28),(-.28,.03),(.17,0),(.33,.08),(.40,.24),(.37,.48),(.33,.68)),
        'function': ((-.41,.34),(-.28,.04),(.17,0),(.34,.09),(.41,.28),(.37,.60),(.31,.88)),
        'touch_id': ((-.41,.30),(-.28,.03),(.18,0),(.34,.07),(.40,.22),(.37,.48),(.33,.70)),
    }
    return profiles[family]


def _speaker_proxy_images():
    rgba = bpy.data.images.get('MACBOOK_SPEAKER_PROXY_RGBA')
    normal = bpy.data.images.get('MACBOOK_SPEAKER_PROXY_NORMAL')
    if rgba and normal:
        return rgba, normal

    width_px, height_px = 128, 1024
    rgba = bpy.data.images.new('MACBOOK_SPEAKER_PROXY_RGBA', width=width_px, height=height_px, alpha=True)
    normal = bpy.data.images.new('MACBOOK_SPEAKER_PROXY_NORMAL', width=width_px, height=height_px, alpha=False)
    normal.colorspace_settings.name = 'Non-Color'

    rgba_pixels = [0.0, 0.0, 0.0, 0.0] * (width_px * height_px)
    normal_pixels = [0.5, 0.5, 1.0, 1.0] * (width_px * height_px)
    sx = (width_px - 1) / SPEAKER_FIELD_WIDTH_MM
    sy = (height_px - 1) / SPEAKER_FIELD_HEIGHT_MM
    radius = SPEAKER_HOLE_RADIUS_MM

    for row in range(SPEAKER_ROWS):
        y_mm = 2 + row*SPEAKER_ROW_PITCH_MM - SPEAKER_CENTER_Y_MM
        cy = int(round((y_mm / SPEAKER_FIELD_HEIGHT_MM + .5) * (height_px - 1)))
        for col in range(SPEAKER_COLS):
            x_mm = (col - (SPEAKER_COLS-1)/2) * SPEAKER_COL_PITCH_MM
            cx = int(round((x_mm / SPEAKER_FIELD_WIDTH_MM + .5) * (width_px - 1)))
            rx = max(1, int(math.ceil(radius*sx)))
            ry = max(1, int(math.ceil(radius*sy)))
            for py in range(max(0, cy-ry), min(height_px, cy+ry+1)):
                dy = (py-cy) / sy
                for px in range(max(0, cx-rx), min(width_px, cx+rx+1)):
                    dx = (px-cx) / sx
                    rr = math.sqrt(dx*dx + dy*dy)
                    if rr > radius:
                        continue
                    index = (py*width_px + px)*4
                    edge = min(1.0, max(0.0, (radius-rr) / max(.025, radius*.16)))
                    rgba_pixels[index:index+4] = [.004, .005, .007, .92*edge]
                    nx = max(-.72, min(.72, dx/radius*.72))
                    ny = max(-.72, min(.72, dy/radius*.72))
                    nz = math.sqrt(max(0.0, 1.0-nx*nx-ny*ny))
                    normal_pixels[index:index+4] = [.5+nx*.5, .5+ny*.5, .5+nz*.5, 1.0]

    rgba.pixels.foreach_set(rgba_pixels)
    normal.pixels.foreach_set(normal_pixels)
    rgba.pack()
    normal.pack()
    return rgba, normal


def _speaker_proxy_material():
    material = bpy.data.materials.get('MAT_SPEAKER_PROXY')
    if material:
        return material
    rgba, normal = _speaker_proxy_images()
    material = bpy.data.materials.new('MAT_SPEAKER_PROXY')
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    bsdf = nodes.get('Principled BSDF')
    bsdf.inputs['Metallic'].default_value = 0.0
    bsdf.inputs['Roughness'].default_value = .76
    bsdf.inputs['Specular IOR Level'].default_value = .08

    color = nodes.new('ShaderNodeTexImage')
    color.name = 'SPEAKER_PROXY_RGBA'
    color.image = rgba
    normal_tex = nodes.new('ShaderNodeTexImage')
    normal_tex.name = 'SPEAKER_PROXY_NORMAL'
    normal_tex.image = normal
    normal_map = nodes.new('ShaderNodeNormalMap')
    normal_map.inputs['Strength'].default_value = .55
    links.new(color.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(color.outputs['Alpha'], bsdf.inputs['Alpha'])
    links.new(normal_tex.outputs['Color'], normal_map.inputs['Color'])
    links.new(normal_map.outputs['Normal'], bsdf.inputs['Normal'])
    try:
        material.surface_render_method = 'DITHERED'
    except Exception:
        pass
    return material


def speaker_runtime_proxies(fc, collection, root, width, base_height):
    mm = fc.MM
    material = _speaker_proxy_material()
    for side, suffix in ((-1, 'L'), (1, 'R')):
        center_x = side*(width/2-10*mm)
        mesh = bpy.data.meshes.new(f'SPEAKER_RUNTIME_PROXY_{suffix}_MESH')
        w = SPEAKER_FIELD_WIDTH_MM*mm*.5
        h = SPEAKER_FIELD_HEIGHT_MM*mm*.5
        mesh.from_pydata([(-w,-h,0),(w,-h,0),(w,h,0),(-w,h,0)], [], [(0,1,2,3)])
        mesh.update()
        uv = mesh.uv_layers.new(name='UVMap')
        for loop, coord in zip(mesh.loops, ((0,0),(1,0),(1,1),(0,1))):
            uv.data[loop.index].uv = coord
        obj = bpy.data.objects.new(f'SPEAKER_RUNTIME_PROXY_{suffix}', mesh)
        collection.objects.link(obj)
        obj.parent = root
        obj.location = (center_x, SPEAKER_CENTER_Y_MM*mm, base_height+.025*mm)
        obj.data.materials.append(material)
        obj['runtime_only'] = True
        obj['runtime_role'] = 'speaker_proxy'
        obj['speaker_rows'] = SPEAKER_ROWS
        obj['speaker_columns'] = SPEAKER_COLS
        obj.hide_render = True
    return material


def keyboard(fc, collection, root, material, base_height):
    mm = fc.MM
    legend_mat = fc.make_material('MAT_KEY_LEGENDS', (.60, .62, .65), 0, .65)
    rows = [
        (0, ['fn', 'control', 'option', 'command', 'space', 'command', 'option'], [1, 1, 1, 1.25, 5.25, 1.25, 1]),
        (1, ['shift'] + list('ZXCVBNM') + [',', '.', '/', 'shift'], [2.25] + [1] * 10 + [2.25]),
        (2, ['caps'] + list('ASDFGHJKL') + [';', "'", 'return'], [1.75] + [1] * 11 + [1.75]),
        (3, ['tab'] + list('QWERTYUIOP') + ['[', ']', '\\'], [1.5] + [1] * 13),
        (4, ['`'] + list('1234567890') + ['-', '=', 'delete'], [1] * 13 + [1.5]),
        (5, ['esc'] + [f'F{i}' for i in range(1, 13)] + ['Touch ID'], [1.1] + [1] * 13),
    ]

    def key(name, label, x, y, width, height=13.2):
        family = _key_family(label, width, height)
        radius_mm = {'space': 1.25, 'arrow': .82, 'modifier': 1.05, 'function': .95,
                     'touch_id': 1.05, 'regular': 1.0}[family]
        obj = profiled_shell(
            fc, name, width*mm, height*mm, .82*mm, radius_mm*mm,
            [(z*mm, inset*mm) for z, inset in _key_profile(family)],
            material, collection, location=(x*mm,y*mm,base_height+.75*mm),
        )
        obj.parent = root
        obj['key_label'] = label
        obj['key_family'] = family
        obj['surface_family'] = 'sculpted_keycap'
        _weighted_normals(obj, 48)
        stem = fc.rounded_cube('KEYSEAT_'+name, ((width-2)*mm,(height-1.2)*mm,.86*mm), .12*mm,
                               material,collection,(x*mm,y*mm,base_height-.05*mm)); stem.parent=root
        if label == 'Touch ID':
            sensor_mat = fc.make_material('MAT_TOUCH_ID_SENSOR', (.003, .004, .005), 0, .22)
            sensor = fc.cylinder('TOUCH_ID_SENSOR', 4.3 * mm, .06 * mm, sensor_mat, collection,
                                 (x * mm, y * mm, base_height + 1.18 * mm), axis='Z', vertices=48)
            sensor.parent = root
            return
        if label == 'space':
            return
        if label.startswith('F') and label[1:].isdigit():
            function_legends.icon('LEGEND_'+name,int(label[1:]),collection,root,legend_mat,
                                  (x*mm,y*mm,base_height+1.08*mm))
            return
        font = bpy.data.curves.new('LEGEND_' + name, 'FONT')
        font.body = label
        font.align_x = 'CENTER'
        font.align_y = 'CENTER'
        font.size = (1.8 if len(label) > 3 else 3.6) * mm
        legend = bpy.data.objects.new('LEGEND_' + name, font)
        collection.objects.link(legend)
        legend.parent = root
        legend.location = (x * mm, y * mm, base_height + 1.08 * mm)
        font.materials.append(legend_mat)
        bpy.ops.object.select_all(action='DESELECT')
        legend.select_set(True)
        bpy.context.view_layer.objects.active = legend
        bpy.ops.object.convert(target='MESH')

    for row, labels, units in rows:
        assert len(labels) == len(units)
        x = -130.5 if row == 0 else -sum(units) * 18 / 2
        for index, (label, span) in enumerate(zip(labels, units)):
            name = 'TOUCH_ID' if label == 'Touch ID' else f'KEY_{row:02d}_{index:02d}'
            key(name, label, x + span * 9, -2 + row * 15.25, span * 18 - 1.8)
            x += span * 18
    # Four half-height arrows occupy an inverted T in the remaining bottom row.
    for index, (label, x, y) in enumerate((('←', 88.2, -5.5), ('↓', 104.4, -5.5),
                                         ('→', 120.6, -5.5), ('↑', 104.4, 1.3))):
        key(f'KEY_ARROW_{index}', label, x, y, 14.4, 6.1)


def ports(fc, collection, root, base, width, base_height, dark):
    mm = fc.MM
    contacts = fc.make_material('MAT_PORT_CONTACTS', (.31, .25, .12), .8, .30)
    for spec in PORTS:
        name,side,y,length,height=spec.name,spec.side,spec.y_mm,spec.width_mm,spec.height_mm
        center = (side * (width / 2 - 1.1 * mm), y * mm, base_height / 2)
        if name == 'HEADPHONE':
            bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=1.8 * mm, depth=3 * mm,
                                                location=center, rotation=(0, math.pi / 2, 0))
            cutter = bpy.context.object
        elif name == 'HDMI':
            profile = [(-length / 2, height / 2), (length / 2, height / 2),
                       (length / 2, -height * .15), (length * .38, -height / 2),
                       (-length * .38, -height / 2), (-length / 2, -height * .15)]
            vertices = [(x * mm, y * mm, z * mm) for x in (-1.5, 1.5) for y, z in profile]
            count = len(profile)
            faces = [tuple(range(count - 1, -1, -1)), tuple(range(count, count * 2))]
            faces += [(i, (i + 1) % count, (i + 1) % count + count, i + count) for i in range(count)]
            mesh = bpy.data.meshes.new(name + '_CUTTER'); mesh.from_pydata(vertices, [], faces); mesh.update()
            cutter = bpy.data.objects.new(name + '_CUTTER', mesh); collection.objects.link(cutter)
            cutter.location = center
        else:
            radius = height / 2 if name.startswith('TB_') else min(height * .45, .9)
            cutter = fc.rounded_prism(name + '_CUTTER', length * mm, height * mm, 3 * mm,
                                      radius * mm, None, collection, axis='Y')
            cutter.rotation_euler.z = math.pi / 2
            cutter.location = center
        # X/Z outlines reverse handedness when extruded along Y.
        if name!='HDMI':
            for polygon in cutter.data.polygons:
                polygon.use_smooth=(abs(polygon.normal.z)<.5 if name=='HEADPHONE' else polygon.index>=2)
        bm = bmesh.new()
        bm.from_mesh(cutter.data)
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        bm.to_mesh(cutter.data)
        bm.free()
        bpy.context.view_layer.update()
        fc.boolean_difference(base, cutter, name='CUT_' + name)
        # Recessed dark floor, rather than a black plate outside the chassis.
        floor = fc.rounded_cube(name, (.16 * mm, length * .96 * mm, height * .90 * mm), .06 * mm,
                                dark, collection, (side * (width / 2 - 2.45 * mm), y * mm, base_height / 2))
        floor.parent = root
        if name.startswith('TB_') or name == 'HDMI':
            tongue = fc.rounded_cube(name + '_TONGUE', (1.4 * mm, length * .70 * mm, .55 * mm), .12 * mm,
                                     dark, collection, (side * (width / 2 - 1.6 * mm), y * mm, base_height / 2))
            tongue.parent = root
            if name.startswith('TB_'):
                for row,sign in (('A',1),('B',-1)):
                    for index in range(12):
                        contact=fc.rounded_cube(f'{name}_CONTACT_{row}{index+1:02d}',
                            (.70*mm,.22*mm,.04*mm),.008*mm,contacts,collection,
                            (side*(width/2-1.55*mm),(y+(index-5.5)*.5)*mm,base_height/2+sign*.30*mm))
                        contact.parent=root
        if name == 'MAGSAFE':
            for i in range(5):
                pin = fc.cylinder(f'{name}_CONTACT_{i}', .35 * mm, .10 * mm, contacts, collection,
                                  axis='Y', vertices=20)
                pin.rotation_euler = (0, math.pi / 2, 0)
                pin.location = (side * (width / 2 - 2.30 * mm), (y + (i - 2) * 2.1) * mm, base_height / 2)
                pin.parent = root


def speakers(fc, collection, root, base, width, base_height, dark):
    mm = fc.MM
    bm = bmesh.new()
    for side in (-1, 1):
        center_x = side*(width/2-10*mm)
        backing = fc.rounded_prism(
            f'SPEAKER_BACKING_{side}', SPEAKER_FIELD_WIDTH_MM*mm, SPEAKER_FIELD_HEIGHT_MM*mm,
            .10*mm, .3*mm, dark, collection, axis='Z',
            location=(center_x,SPEAKER_CENTER_Y_MM*mm,base_height-.68*mm),
        )
        backing.parent=root
        backing['master_only'] = True
        for row in range(SPEAKER_ROWS):
            for col in range(SPEAKER_COLS):
                x = center_x+(col-(SPEAKER_COLS-1)/2)*SPEAKER_COL_PITCH_MM*mm
                y = (2+row*SPEAKER_ROW_PITCH_MM)*mm
                bmesh.ops.create_cone(
                    bm, cap_ends=True, cap_tris=False, segments=12,
                    radius1=SPEAKER_HOLE_RADIUS_MM*mm, radius2=SPEAKER_HOLE_RADIUS_MM*mm,
                    depth=.75*mm, matrix=Matrix.Translation((x,y,base_height-.25*mm)),
                )
                # Preserve the two public legacy identifiers in the master without one object per hole.
                if (side,row,col) in ((-1,0,0),(1,14,4)):
                    floor=fc.cylinder(
                        f'SPEAKER_{"L" if side<0 else "R"}_{row:02d}_{col:02d}',
                        .18*mm,.04*mm,dark,collection,(x,y,base_height-.67*mm),axis='Z',vertices=12,
                    )
                    floor.parent=root
                    floor['master_only'] = True
    mesh = bpy.data.meshes.new('SPEAKER_CUTTERS'); bm.to_mesh(mesh); bm.free()
    cutter = bpy.data.objects.new('SPEAKER_CUTTERS', mesh); collection.objects.link(cutter)
    bpy.context.view_layer.update()
    bpy.ops.object.select_all(action='DESELECT'); base.select_set(True); bpy.context.view_layer.objects.active=base
    modifier=base.modifiers.new('CUT_SPEAKER_FIELDS','BOOLEAN')
    modifier.operation='DIFFERENCE'; modifier.solver='MANIFOLD'; modifier.object=cutter
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    bpy.data.objects.remove(cutter,do_unlink=True)
    base['speaker_apertures']=SPEAKER_ROWS*SPEAKER_COLS*2
    base['speaker_pattern']='88x9 per side; shared with runtime alpha+normal proxy'
