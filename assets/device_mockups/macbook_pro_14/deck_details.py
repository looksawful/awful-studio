"""Estimated ANSI layout and physical port interiors, in the metric chassis."""
import math
import bpy
import bmesh
from mathutils import Matrix


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
        obj = fc.rounded_cube(name, (width * mm, height * mm, .82 * mm), .26 * mm,
                              material, collection, (x * mm, y * mm, base_height + .75 * mm))
        obj.parent = root
        obj['key_label'] = label
        if label == 'Touch ID':
            sensor_mat = fc.make_material('MAT_TOUCH_ID_SENSOR', (.003, .004, .005), 0, .22)
            sensor = fc.cylinder('TOUCH_ID_SENSOR', 4.3 * mm, .06 * mm, sensor_mat, collection,
                                 (x * mm, y * mm, base_height + 1.18 * mm), axis='Z', vertices=48)
            sensor.parent = root
            return
        if label == 'space':
            return
        font = bpy.data.curves.new('LEGEND_' + name, 'FONT')
        font.body = label
        font.align_x = 'CENTER'
        font.align_y = 'CENTER'
        font.size = (1.6 if len(label) > 3 else 2.5) * mm
        legend = bpy.data.objects.new('LEGEND_' + name, font)
        collection.objects.link(legend)
        legend.parent = root
        legend.location = (x * mm, y * mm, base_height + 1.18 * mm)
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
    specs = [('MAGSAFE', -1, 62, 14, 3.4), ('TB_LEFT_1', -1, 27, 10, 2.8),
             ('TB_LEFT_2', -1, -1, 10, 2.8), ('HEADPHONE', -1, -54, 3.6, 3.6),
             ('HDMI', 1, 53, 15, 4.4), ('SDXC', 1, 18, 25, 2.1), ('TB_RIGHT', 1, -22, 10, 2.8)]
    for name, side, y, length, height in specs:
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
        for row in range(15):
            for col in range(5):
                x = side * (width / 2 - 10 * mm) + (col - 2) * 2.35 * mm
                y = (2 + row * 5.2) * mm
                bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=24,
                                      radius1=.48 * mm, radius2=.48 * mm, depth=.8 * mm,
                                      matrix=Matrix.Translation((x, y, base_height - .22 * mm)))
                floor = fc.cylinder(f'SPEAKER_{"L" if side < 0 else "R"}_{row:02d}_{col:02d}',
                                    .40 * mm, .10 * mm, dark, collection,
                                    (x, y, base_height - .55 * mm), axis='Z', vertices=20)
                floor.parent = root
    mesh = bpy.data.meshes.new('SPEAKER_CUTTERS'); bm.to_mesh(mesh); bm.free()
    cutter = bpy.data.objects.new('SPEAKER_CUTTERS', mesh); collection.objects.link(cutter)
    bpy.context.view_layer.update()
    fc.boolean_difference(base, cutter, name='CUT_SPEAKER_FIELDS')
