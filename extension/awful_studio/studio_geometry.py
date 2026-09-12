# SPDX-License-Identifier: GPL-3.0-or-later
"""Pure studio-geometry policy plus Blender adapter hooks for AWFUL STUDIO.

The policy functions in this module intentionally avoid importing ``bpy`` so
metric placement/material/role rules can be proven by the fast test layer.
Blender-specific scene mutation is installed explicitly later by ``install``.
"""
from __future__ import annotations

import math
from typing import Mapping


CYC_LOOKS = {
    'WHITE': (0.78, 0.78, 0.78, 1.0),
    'BLACK': (0.015, 0.015, 0.015, 1.0),
    'CHROMA_GREEN': (0.02, 0.55, 0.04, 1.0),
}

CYC_FINISH = {
    'MATTE': 0.82,
    'MEDIUM': 0.48,
    'GLOSSY': 0.18,
}

ARCHITECTURE_ROLE_GROUPS = {
    'WALLS': (
        'ROOM_RIGHT_CAMERA',
        'ROOM_RIGHT_DOOR_FRONT',
        'ROOM_RIGHT_DOOR_TOP',
        'ROOM_CAMERA',
        'ROOM_BACKGROUND',
        'ROOM_LEFT_CAMERA',
        'ROOM_LEFT_BACKGROUND',
        'ROOM_LEFT_WINDOW_BOTTOM',
        'ROOM_LEFT_WINDOW_TOP',
    ),
    'FLOOR': ('ARCH_FLOOR_VISIBLE',),
    'CEILING': ('ROOM_CEILING',),
    'DOOR': ('DOOR_FRAME', 'DOOR_LEAF'),
    'WINDOW_FRAME': ('WINDOW_FRAME',),
    'WINDOW_GLASS': ('WINDOW_GLASS',),
    'CYC': ('CYC',),
}


def architecture_camera_physical(group: str, reflective_room: bool) -> bool:
    """Decouple camera-visible architecture from the hidden light-bounce room."""
    if group in {'FLOOR', 'DOOR', 'WINDOW_FRAME', 'CYC'}:
        return True
    return bool(reflective_room)


def window_frame_layout(window: Mapping) -> dict[str, object]:
    """Return a clean seven-bar studio-window layout in local Y/Z coordinates."""
    width = float(window['width'])
    bottom = float(window['bottom_z'])
    top = float(window['top_z'])
    frame_width = float(window['frame_width'])
    height = top - bottom
    if width <= frame_width * 3.0 or height <= frame_width * 3.0:
        raise ValueError('Window opening is too small for its frame width')

    ymin, ymax = -width * 0.5, width * 0.5
    inner_width = width - 2.0 * frame_width
    inner_height = height - 2.0 * frame_width
    mid_z = (bottom + top) * 0.5
    mullion = frame_width * 0.70
    interior_ymin = ymin + frame_width
    bars = [
        {'name': 'WINDOW_Frame_Rear', 'center_yz': (ymin + frame_width * 0.5, mid_z),
         'size_yz': (frame_width, inner_height)},
        {'name': 'WINDOW_Frame_Front', 'center_yz': (ymax - frame_width * 0.5, mid_z),
         'size_yz': (frame_width, inner_height)},
        {'name': 'WINDOW_Frame_Bottom', 'center_yz': (0.0, bottom + frame_width * 0.5),
         'size_yz': (width, frame_width)},
        {'name': 'WINDOW_Frame_Top', 'center_yz': (0.0, top - frame_width * 0.5),
         'size_yz': (width, frame_width)},
    ]
    for index, fraction in enumerate((1.0 / 3.0, 2.0 / 3.0), 1):
        y = interior_ymin + inner_width * fraction
        bars.append({
            'name': f'WINDOW_Mullion_V{index}', 'center_yz': (y, mid_z),
            'size_yz': (mullion, inner_height),
        })
    bars.append({
        'name': 'WINDOW_Mullion_H1', 'center_yz': (0.0, mid_z),
        'size_yz': (inner_width, mullion),
    })
    return {
        'bars': bars,
        'glass_center_yz': (0.0, mid_z),
        'glass_size_yz': (inner_width, inner_height),
    }


def cyclorama_distance_bounds(studio_spec: Mapping, clearance: float = 0.25) -> tuple[float, float]:
    """Return physically safe stage-origin -> cove-tangent distance bounds.

    Minimum clearance keeps the maximum supported product envelope away from
    the cove. Maximum clearance keeps the cove radius/vertical section inside
    the room background shell. The rule derives from dimensions instead of a
    magic UI range so future room sizes remain self-consistent.
    """
    clearance = float(clearance)
    if clearance < 0.0:
        raise ValueError('Cyclorama clearance must be non-negative')

    cyc = studio_spec['cyc']
    envelope = studio_spec['product_envelope']
    minimum = max(0.5, float(envelope['max_xy']) * 0.5 + clearance)
    maximum = float(studio_spec['background_y']) - float(cyc['radius']) - clearance
    if maximum <= minimum:
        raise ValueError('Studio dimensions leave no safe cyclorama placement range')
    return minimum, maximum


def clamp_cyclorama_distance(value: float, studio_spec: Mapping, clearance: float = 0.25) -> float:
    low, high = cyclorama_distance_bounds(studio_spec, clearance)
    return min(max(float(value), low), high)


def cyclorama_profile(
    studio_spec: Mapping,
    distance: float,
    segments: int = 64,
    clearance: float = 0.25,
) -> list[tuple[float, float]]:
    """Return the Y/Z profile for the floor run, quarter cove and back rise."""
    if int(segments) < 2:
        raise ValueError('Cyclorama curve needs at least two segments')

    cyc = studio_spec['cyc']
    radius = float(cyc['radius'])
    height = float(cyc['height'])
    if radius <= 0.0 or height < radius:
        raise ValueError('Cyclorama radius/height are physically invalid')

    tangent_y = clamp_cyclorama_distance(distance, studio_spec, clearance)
    front_y = float(cyc['front_y'])
    if front_y >= tangent_y:
        raise ValueError('Cyclorama front edge must stay camera-side of the cove tangent')

    profile: list[tuple[float, float]] = [(front_y, 0.0), (tangent_y, 0.0)]
    for index in range(1, int(segments) + 1):
        t = index / float(segments)
        angle = math.radians(-90.0 + 90.0 * t)
        y = tangent_y + radius * math.cos(angle)
        z = radius + radius * math.sin(angle)
        profile.append((y, z))
    profile.append((tangent_y + radius, height))
    return profile


def cyclorama_style(look: str, finish: str) -> dict[str, object]:
    """Resolve orthogonal cyclorama look and finish into bounded material intent."""
    try:
        base_color = CYC_LOOKS[look]
    except KeyError as exc:
        raise ValueError(f'Unknown cyclorama look: {look}') from exc
    try:
        roughness = CYC_FINISH[finish]
    except KeyError as exc:
        raise ValueError(f'Unknown cyclorama finish: {finish}') from exc
    return {
        'look': look,
        'finish': finish,
        'base_color': base_color,
        'roughness': float(roughness),
    }


DOOR_SPEC = {
    'center_y': -5.5,
    'width': 1.4,
    'height': 2.4,
    'frame_depth': 0.24,
    'frame_width': 0.10,
    'leaf_thickness': 0.05,
}


def _owned_role_objects(legacy, scene, roles):
    role_set = set(roles)
    return [obj for obj in scene.objects
            if legacy.ownership.owned(obj, scene)
            and obj.get(legacy.ROLE_KEY, '') in role_set]


def _set_camera_workflow_visibility(legacy, obj, shown, physical=True):
    obj.hide_viewport = not bool(shown)
    obj.hide_render = not bool(physical)
    legacy.safe_set(obj, 'visible_camera', bool(shown) and bool(physical))


def _principled(material):
    if not material or not material.use_nodes:
        return None
    return next((node for node in material.node_tree.nodes
                 if node.type == 'BSDF_PRINCIPLED'), None)


def _apply_cyclorama_material(legacy, material, look, finish):
    style = cyclorama_style(look, finish)
    shader = _principled(material)
    if shader:
        if 'Base Color' in shader.inputs:
            shader.inputs['Base Color'].default_value = style['base_color']
        if 'Roughness' in shader.inputs:
            shader.inputs['Roughness'].default_value = style['roughness']
    nodes = material.node_tree.nodes if material and material.use_nodes else None
    if nodes:
        mix = nodes.get('AWFUL_PAINT_COLOR_MIX')
        if mix is not None:
            mix.inputs[1].default_value = style['base_color']
        rough = nodes.get('AWFUL_PAINT_ROUGHNESS_RANGE')
        if rough is not None:
            value = float(style['roughness'])
            rough.inputs['To Min'].default_value = max(0.0, value - 0.06)
            rough.inputs['To Max'].default_value = min(1.0, value + 0.06)
    return style


def _write_cyclorama_mesh(obj, width, profile):
    half = float(width) * 0.5
    verts = [(x, y, z) for x in (-half, half) for y, z in profile]
    n = len(profile)
    faces = [(i, i + 1, n + i + 1, n + i) for i in range(n - 1)]
    mesh = obj.data
    mesh.clear_geometry()
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    for poly in mesh.polygons:
        poly.use_smooth = True


def apply_cyclorama_state(legacy, scene):
    cyc = legacy.REG.object('CYC')
    if cyc is None:
        return
    settings = scene.awful_studio
    distance = clamp_cyclorama_distance(
        float(settings.cyclorama_distance_m), legacy.STUDIO_SPEC)
    if abs(float(settings.cyclorama_distance_m) - distance) > 1e-7:
        settings.cyclorama_distance_m = distance
        return
    profile = cyclorama_profile(legacy.STUDIO_SPEC, distance)
    _write_cyclorama_mesh(cyc, legacy.STUDIO_SPEC['cyc']['width'], profile)
    material = legacy.REG.material('MAT_CYC')
    if material:
        _apply_cyclorama_material(
            legacy, material, settings.cyclorama_look, settings.cyclorama_finish)
    target = legacy.REG.object('TARGET_BACKGROUND')
    if target is not None:
        radius = float(legacy.STUDIO_SPEC['cyc']['radius'])
        target.location.y = distance + radius - 0.25
    scene['awful_cyclorama_distance_m'] = float(distance)
    apply_architecture_visibility(legacy, scene)


def _build_cyclorama(legacy, collection, material):
    scene = legacy.bpy.context.scene
    settings = scene.awful_studio
    distance = clamp_cyclorama_distance(
        float(settings.cyclorama_distance_m), legacy.STUDIO_SPEC)
    profile = cyclorama_profile(legacy.STUDIO_SPEC, distance)
    mesh = legacy.bpy.data.meshes.new('MESH_Cyclorama')
    legacy.mark_managed(mesh, 'CYC_MESH')
    obj = legacy.bpy.data.objects.new('CYC_Cyclorama', mesh)
    legacy.mark_managed(obj, 'CYC')
    collection.objects.link(obj)
    _write_cyclorama_mesh(obj, legacy.STUDIO_SPEC['cyc']['width'], profile)
    obj.data.materials.append(material)
    _apply_cyclorama_material(
        legacy, material, settings.cyclorama_look, settings.cyclorama_finish)
    scene['awful_cyclorama_distance_m'] = float(distance)
    return obj


def _floor_box(legacy, name, location, dimensions, collection, material):
    obj = legacy.add_box(
        name, 'ARCH_FLOOR_VISIBLE', location, dimensions,
        collection, material, camera_visible=True)
    obj.display_type = 'SOLID'
    return obj


def _build_visible_floor(legacy, room_col, material):
    spec = legacy.STUDIO_SPEC
    cyc = spec['cyc']
    thickness = 0.04
    z = -thickness * 0.5
    camera_y = float(spec['camera_y'])
    background_y = float(spec['background_y'])
    front_y = float(cyc['front_y'])
    room_width = float(spec['width'])
    cyc_width = float(cyc['width'])
    camera_depth = front_y - camera_y
    if camera_depth > 0:
        _floor_box(
            legacy, 'ARCH_Floor_Camera',
            (0.0, camera_y + camera_depth * 0.5, z),
            (room_width, camera_depth, thickness), room_col, material)
    side_width = max((room_width - cyc_width) * 0.5, 0.0)
    side_depth = background_y - front_y
    if side_width > 0 and side_depth > 0:
        x = cyc_width * 0.5 + side_width * 0.5
        y = front_y + side_depth * 0.5
        for label, xx in (('Left', -x), ('Right', x)):
            _floor_box(
                legacy, f'ARCH_Floor_{label}', (xx, y, z),
                (side_width, side_depth, thickness), room_col, material)


def _build_door_system(legacy, room_col, wall_material, frame_material):
    spec = legacy.STUDIO_SPEC
    half_w = float(spec['width']) * 0.5
    thick = float(spec['wall_thickness'])
    center_y = float(DOOR_SPEC['center_y'])
    width = float(DOOR_SPEC['width'])
    height = float(DOOR_SPEC['height'])
    frame_depth = float(DOOR_SPEC['frame_depth'])
    frame_width = float(DOOR_SPEC['frame_width'])
    ymin = center_y - width * 0.5
    ymax = center_y + width * 0.5
    camera_y = float(spec['camera_y'])
    background_y = float(spec['background_y'])
    room_height = float(spec['height'])

    camera_len = ymin - camera_y
    front_len = background_y - ymax
    if camera_len <= 0 or front_len <= 0 or height >= room_height:
        raise ValueError('Door opening does not fit inside studio wall')

    walls = (
        ('ROOM_Right_Camera', 'ROOM_RIGHT_CAMERA',
         (half_w, camera_y + camera_len * 0.5, room_height * 0.5),
         (thick, camera_len, room_height)),
        ('ROOM_Right_Front', 'ROOM_RIGHT_DOOR_FRONT',
         (half_w, ymax + front_len * 0.5, room_height * 0.5),
         (thick, front_len, room_height)),
        ('ROOM_Right_DoorTop', 'ROOM_RIGHT_DOOR_TOP',
         (half_w, center_y, height + (room_height - height) * 0.5),
         (thick, width, room_height - height)),
    )
    for name, role, location, dimensions in walls:
        obj = legacy.add_room_shell(name, role, location, dimensions, room_col, wall_material)
        obj.display_type = 'SOLID'
    x = half_w - thick * 0.55
    mid_z = height * 0.5
    for name, y, dims in (
        ('DOOR_Frame_Rear', ymin, (frame_depth, frame_width, height)),
        ('DOOR_Frame_Front', ymax, (frame_depth, frame_width, height)),
        ('DOOR_Frame_Top', center_y, (frame_depth, width + frame_width, frame_width)),
    ):
        z = mid_z if 'Top' not in name else height
        obj = legacy.add_box(
            name, 'DOOR_FRAME', (x, y, z), dims,
            room_col, frame_material, camera_visible=True)
        obj.display_type = 'SOLID'

    leaf = legacy.add_box(
        'DOOR_Leaf', 'DOOR_LEAF',
        (x - 0.04, center_y, height * 0.5),
        (float(DOOR_SPEC['leaf_thickness']), width - 0.08, height - 0.06),
        room_col, wall_material, camera_visible=True)
    leaf.display_type = 'SOLID'
    return leaf


def _build_room(legacy, room_col, window_col, wall_mat, floor_mat, frame_mat, glass_mat):
    spec = legacy.STUDIO_SPEC
    width, height = float(spec['width']), float(spec['height'])
    half_w = width * 0.5
    camera_y, bg_y = float(spec['camera_y']), float(spec['background_y'])
    center_y = (camera_y + bg_y) * 0.5
    thick = float(spec['wall_thickness'])
    floor_offset = float(spec['floor_offset'])
    depth = float(spec['depth'])

    _build_door_system(legacy, room_col, wall_mat, frame_mat)
    legacy.add_room_shell(
        'ROOM_CameraSide', 'ROOM_CAMERA',
        (0, camera_y, height * 0.5), (width, thick, height), room_col, wall_mat)
    legacy.add_room_shell(
        'ROOM_BackgroundWall', 'ROOM_BACKGROUND',
        (0, bg_y, height * 0.5), (width, thick, height), room_col, wall_mat)
    ceiling = legacy.add_room_shell(
        'ROOM_Ceiling', 'ROOM_CEILING',
        (0, center_y, height), (width, depth, thick), room_col, wall_mat)
    ceiling.display_type = 'SOLID'
    legacy.add_room_shell(
        'ROOM_Floor', 'ROOM_FLOOR',
        (0, center_y, -floor_offset - thick * 0.5),
        (width, depth, thick), room_col, wall_mat)
    _build_visible_floor(legacy, room_col, floor_mat)

    win = spec['window']
    ymin = float(win['center_y']) - float(win['width']) * 0.5
    ymax = float(win['center_y']) + float(win['width']) * 0.5
    rear_len = ymin - camera_y
    front_len = bg_y - ymax
    rear_center = (camera_y + ymin) * 0.5
    front_center = (ymax + bg_y) * 0.5
    mid_y = float(win['center_y'])
    bottom = float(win['bottom_z'])
    top = float(win['top_z'])
    mid_z = (bottom + top) * 0.5
    win_h = top - bottom

    wall_specs = (
        ('ROOM_Left_Camera', 'ROOM_LEFT_CAMERA',
         (-half_w, rear_center, height * 0.5), (thick, rear_len, height)),
        ('ROOM_Left_Background', 'ROOM_LEFT_BACKGROUND',
         (-half_w, front_center, height * 0.5), (thick, front_len, height)),
        ('ROOM_Left_WindowBottom', 'ROOM_LEFT_WINDOW_BOTTOM',
         (-half_w, mid_y, bottom * 0.5), (thick, float(win['width']), bottom)),
        ('ROOM_Left_WindowTop', 'ROOM_LEFT_WINDOW_TOP',
         (-half_w, mid_y, top + (height - top) * 0.5),
         (thick, float(win['width']), height - top)),
    )
    for name, role, location, dimensions in wall_specs:
        obj = legacy.add_room_shell(name, role, location, dimensions, room_col, wall_mat)
        obj.display_type = 'SOLID'

    frame_d = float(win['frame_depth'])
    frame_w = float(win['frame_width'])
    x = -half_w + 0.02
    frame_layout = window_frame_layout(win)
    for item in frame_layout['bars']:
        local_y, z = item['center_yz']
        size_y, size_z = item['size_yz']
        obj = legacy.add_box(
            item['name'], 'WINDOW_FRAME', (x, mid_y + local_y, z),
            (frame_d, size_y, size_z), window_col, frame_mat, camera_visible=True)
        bevel = obj.modifiers.new('AWFUL Window Edge', 'BEVEL')
        bevel.width = min(0.018, frame_w * 0.16)
        bevel.segments = 3
    glass_y, glass_z = frame_layout['glass_center_yz']
    glass_w, glass_h = frame_layout['glass_size_yz']
    glass = legacy.add_box(
        'WINDOW_Glass', 'WINDOW_GLASS',
        (-half_w + 0.045, mid_y + glass_y, glass_z),
        (float(win['glass_thickness']), glass_w, glass_h),
        window_col, glass_mat, camera_visible=True)
    glass.hide_render = True
    glass.hide_viewport = True
    return glass


def apply_architecture_visibility(legacy, scene):
    settings = scene.awful_studio
    physical = bool(settings.reflective_room_enabled)
    show_map = {
        'WALLS': bool(settings.show_walls),
        'FLOOR': bool(settings.show_floor),
        'CEILING': bool(settings.show_ceiling),
        'DOOR': bool(settings.show_door),
        'WINDOW_FRAME': bool(settings.show_window_frame),
        'WINDOW_GLASS': bool(settings.show_window_glass),
        'CYC': bool(settings.show_cyclorama),
    }
    for group, roles in ARCHITECTURE_ROLE_GROUPS.items():
        for obj in _owned_role_objects(legacy, scene, roles):
            object_physical = architecture_camera_physical(group, physical)
            if group == 'WINDOW_GLASS':
                object_physical = physical and bool(settings.window_glass_enabled)
            _set_camera_workflow_visibility(
                legacy, obj, show_map[group], object_physical)
    bounce_floor = legacy.REG.object('ROOM_FLOOR')
    if bounce_floor is not None:
        bounce_floor.hide_viewport = True
        bounce_floor.hide_render = not physical
        legacy.safe_set(bounce_floor, 'visible_camera', False)
    legacy.set_window_portal_enabled(
        scene, physical and bool(settings.natural_light_enabled))


def _on_cyclorama_update(legacy, _self, context):
    scene = getattr(context, 'scene', None)
    if scene is not None and legacy.REG.object('CYC') is not None:
        apply_cyclorama_state(legacy, scene)


def _on_architecture_visibility(legacy, _self, context):
    scene = getattr(context, 'scene', None)
    if scene is not None and legacy.REG.object('CYC') is not None:
        apply_architecture_visibility(legacy, scene)


def _install_properties(legacy):
    props = legacy.bpy.props
    annotations = legacy.AWFUL_StudioSettings.__annotations__
    cyc_update = lambda self, context: _on_cyclorama_update(legacy, self, context)
    vis_update = lambda self, context: _on_architecture_visibility(legacy, self, context)
    annotations['cyclorama_distance_m'] = props.FloatProperty(
        name='Distance', default=3.0, min=0.5, max=10.0,
        unit='LENGTH', update=cyc_update)
    annotations['cyclorama_look'] = props.EnumProperty(
        name='Look',
        items=(('WHITE', 'White', ''), ('BLACK', 'Black', ''),
               ('CHROMA_GREEN', 'Chroma Green', '')),
        default='WHITE', update=cyc_update)
    annotations['cyclorama_finish'] = props.EnumProperty(
        name='Finish',
        items=(('MATTE', 'Matte', ''), ('MEDIUM', 'Medium', ''),
               ('GLOSSY', 'Glossy', '')),
        default='MATTE', update=cyc_update)
    annotations['show_cyclorama'] = props.BoolProperty(
        name='Cyclorama', default=True, update=vis_update)
    annotations['show_walls'] = props.BoolProperty(
        name='Walls', default=False, update=vis_update)
    annotations['show_floor'] = props.BoolProperty(
        name='Floor', default=True, update=vis_update)
    annotations['show_ceiling'] = props.BoolProperty(
        name='Ceiling', default=False, update=vis_update)
    annotations['show_door'] = props.BoolProperty(
        name='Door', default=True, update=vis_update)
    annotations['show_window_frame'] = props.BoolProperty(
        name='Window Frame', default=True, update=vis_update)
    annotations['show_window_glass'] = props.BoolProperty(
        name='Window Glass', default=False, update=vis_update)


def _install_panel(legacy):
    class AWFUL_PT_StudioGeometry(legacy.bpy.types.Panel):
        bl_label = 'Studio'
        bl_idname = 'AWFUL_PT_STUDIO_GEOMETRY'
        bl_parent_id = 'AWFUL_PT_MAIN_V4'
        bl_space_type = 'VIEW_3D'
        bl_region_type = 'UI'
        bl_options = {'DEFAULT_CLOSED'}

        def draw(self, context):
            layout = self.layout
            settings = context.scene.awful_studio
            if legacy.REG.object('CYC') is None:
                layout.label(text='Build Studio first')
                return
            cyc = layout.box()
            cyc.label(text='Cyclorama')
            cyc.prop(settings, 'cyclorama_distance_m')
            cyc.prop(settings, 'cyclorama_look')
            cyc.prop(settings, 'cyclorama_finish')
            cyc.prop(settings, 'show_cyclorama', toggle=True)
            arch = layout.box()
            arch.label(text='Architecture')
            row = arch.row(align=True)
            row.prop(settings, 'show_walls', toggle=True)
            row.prop(settings, 'show_floor', toggle=True)
            row.prop(settings, 'show_ceiling', toggle=True)
            row = arch.row(align=True)
            row.prop(settings, 'show_door', toggle=True)
            row.prop(settings, 'show_window_frame', toggle=True)
            row.prop(settings, 'show_window_glass', toggle=True)

    legacy.AWFUL_PT_StudioGeometry = AWFUL_PT_StudioGeometry
    legacy.CLASSES = tuple(legacy.CLASSES) + (AWFUL_PT_StudioGeometry,)


def install(legacy):
    """Install scene-clean Blender adapters before class registration."""
    if getattr(legacy, '_awful_studio_geometry_policy_installed', False):
        return
    _install_properties(legacy)
    _install_panel(legacy)
    legacy.build_cyclorama = lambda collection, material: _build_cyclorama(
        legacy, collection, material)
    legacy.build_room = lambda room_col, window_col, wall_mat, floor_mat, frame_mat, glass_mat: _build_room(
        legacy, room_col, window_col, wall_mat, floor_mat, frame_mat, glass_mat)
    legacy.apply_cyclorama_state = lambda scene: apply_cyclorama_state(legacy, scene)
    legacy.apply_architecture_visibility = lambda scene: apply_architecture_visibility(legacy, scene)
    legacy.apply_room_visibility = lambda scene: apply_architecture_visibility(legacy, scene)
    legacy._awful_studio_geometry_policy_installed = True
