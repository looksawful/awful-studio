# SPDX-License-Identifier: GPL-3.0-or-later
"""Product Quality policy and Blender adapter hooks for AWFUL STUDIO.

The catalog and starter-material policy at the top of this module are pure
Python so ordinary tests can validate product intent without launching Blender.
Scene mutation is added through explicit adapter functions below that consume
the retained ``legacy`` module rather than importing Blender at module import.
"""
from __future__ import annotations

from copy import deepcopy


MOCKUP_SPECS = {
    'BOTTLE': {
        'label': 'Bottle',
        'dimensions_m': (0.075, 0.075, 0.220),
        'material_slots': ('BODY', 'CAP', 'LABEL'),
        'slot_materials': {
            'BODY': 'GLASS_CLEAR',
            'CAP': 'PLASTIC_GLOSSY',
            'LABEL': 'PAPER_LABEL',
        },
        'max_mesh_parts': 4,
        'bevel_segments': 4,
    },
    'JAR': {
        'label': 'Jar',
        'dimensions_m': (0.090, 0.090, 0.110),
        'material_slots': ('BODY', 'LID', 'LABEL'),
        'slot_materials': {
            'BODY': 'GLASS_CLEAR',
            'LID': 'METAL_ANODIZED',
            'LABEL': 'PAPER_LABEL',
        },
        'max_mesh_parts': 4,
        'bevel_segments': 4,
    },
    'BOX': {
        'label': 'Box',
        'dimensions_m': (0.120, 0.070, 0.180),
        'material_slots': ('BODY', 'LABEL'),
        'slot_materials': {
            'BODY': 'CARDBOARD',
            'LABEL': 'PAPER_LABEL',
        },
        'max_mesh_parts': 2,
        'bevel_segments': 4,
    },
    'CAN': {
        'label': 'Can',
        'dimensions_m': (0.066, 0.066, 0.122),
        'material_slots': ('BODY', 'TOP', 'LABEL'),
        'slot_materials': {
            'BODY': 'METAL_ANODIZED',
            'TOP': 'METAL_ANODIZED',
            'LABEL': 'PAPER_LABEL',
        },
        'max_mesh_parts': 4,
        'bevel_segments': 4,
    },
    'PHONE': {
        'label': 'Phone',
        'dimensions_m': (0.071, 0.008, 0.147),
        'material_slots': ('FRAME', 'BACK', 'SCREEN'),
        'slot_materials': {
            'FRAME': 'METAL_ANODIZED',
            'BACK': 'GLASS_DARK',
            'SCREEN': 'SCREEN',
        },
        'max_mesh_parts': 4,
        'bevel_segments': 5,
    },
    'TABLET': {
        'label': 'Tablet',
        'dimensions_m': (0.178, 0.0065, 0.248),
        'material_slots': ('FRAME', 'BACK', 'SCREEN'),
        'slot_materials': {
            'FRAME': 'METAL_ANODIZED',
            'BACK': 'GLASS_DARK',
            'SCREEN': 'SCREEN',
        },
        'max_mesh_parts': 4,
        'bevel_segments': 5,
    },
}


MATERIAL_STARTERS = {
    'PLASTIC_MATTE': {
        'label': 'Matte Plastic',
        'base_color': (0.12, 0.13, 0.15, 1.0),
        'roughness': 0.62,
        'metallic': 0.0,
        'transmission': 0.0,
        'ior': 1.46,
        'emission_strength': 0.0,
    },
    'PLASTIC_GLOSSY': {
        'label': 'Glossy Plastic',
        'base_color': (0.09, 0.10, 0.12, 1.0),
        'roughness': 0.22,
        'metallic': 0.0,
        'transmission': 0.0,
        'ior': 1.46,
        'emission_strength': 0.0,
    },
    'METAL_ANODIZED': {
        'label': 'Anodized Metal',
        'base_color': (0.18, 0.19, 0.21, 1.0),
        'roughness': 0.28,
        'metallic': 1.0,
        'transmission': 0.0,
        'ior': 1.50,
        'emission_strength': 0.0,
    },
    'GLASS_CLEAR': {
        'label': 'Clear Glass',
        'base_color': (0.94, 0.97, 1.0, 1.0),
        'roughness': 0.08,
        'metallic': 0.0,
        'transmission': 0.95,
        'ior': 1.45,
        'emission_strength': 0.0,
    },
    'GLASS_DARK': {
        'label': 'Dark Glass',
        'base_color': (0.025, 0.03, 0.04, 1.0),
        'roughness': 0.12,
        'metallic': 0.0,
        'transmission': 0.92,
        'ior': 1.50,
        'emission_strength': 0.0,
    },
    'CERAMIC': {
        'label': 'Ceramic',
        'base_color': (0.82, 0.80, 0.76, 1.0),
        'roughness': 0.34,
        'metallic': 0.0,
        'transmission': 0.0,
        'ior': 1.50,
        'emission_strength': 0.0,
    },
    'CARDBOARD': {
        'label': 'Cardboard',
        'base_color': (0.42, 0.27, 0.13, 1.0),
        'roughness': 0.78,
        'metallic': 0.0,
        'transmission': 0.0,
        'ior': 1.45,
        'emission_strength': 0.0,
    },
    'PAPER_LABEL': {
        'label': 'Paper Label',
        'base_color': (0.86, 0.84, 0.79, 1.0),
        'roughness': 0.56,
        'metallic': 0.0,
        'transmission': 0.0,
        'ior': 1.45,
        'emission_strength': 0.0,
    },
    'SCREEN': {
        'label': 'Screen',
        'base_color': (0.015, 0.020, 0.028, 1.0),
        'roughness': 0.16,
        'metallic': 0.0,
        'transmission': 0.0,
        'ior': 1.50,
        'emission_color': (0.035, 0.055, 0.085, 1.0),
        'emission_strength': 0.65,
    },
}


def mockup_keys() -> tuple[str, ...]:
    return tuple(MOCKUP_SPECS)


def mockup_spec(key: str) -> dict:
    try:
        return deepcopy(MOCKUP_SPECS[key])
    except KeyError as exc:
        raise ValueError(f'Unknown AWFUL mockup: {key}') from exc


def material_spec(key: str) -> dict:
    try:
        return deepcopy(MATERIAL_STARTERS[key])
    except KeyError as exc:
        raise ValueError(f'Unknown AWFUL starter material: {key}') from exc


def mockup_key(root) -> str:
    key = str(root.get('awful_mockup_key', ''))
    if key not in MOCKUP_SPECS:
        raise ValueError('Object is not an AWFUL procedural mockup root')
    return key


def mockup_roots(legacy, scene) -> list:
    return [
        obj for obj in scene.objects
        if legacy.ownership.owned(obj, scene)
        and obj.get(legacy.ROLE_KEY, '') == 'MOCKUP_ROOT'
    ]


def _set_socket(shader, names, value):
    for name in names:
        if name in shader.inputs:
            shader.inputs[name].default_value = value
            return True
    return False


def _starter_material(legacy, scene, key):
    spec = material_spec(key)
    role = f'MOCKUP_MAT_{key}'
    existing = legacy.REG.material(role)
    if existing is not None:
        return existing

    bpy = legacy.bpy
    material = bpy.data.materials.new(f'MAT_AWFUL_{spec["label"].replace(" ", "_")}')
    legacy.mark_managed(material, role)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()
    output = nodes.new('ShaderNodeOutputMaterial')
    shader = nodes.new('ShaderNodeBsdfPrincipled')
    shader.name = 'AWFUL_MOCKUP_SHADER'
    _set_socket(shader, ('Base Color',), spec['base_color'])
    _set_socket(shader, ('Roughness',), float(spec['roughness']))
    _set_socket(shader, ('Metallic',), float(spec['metallic']))
    _set_socket(shader, ('IOR',), float(spec['ior']))
    _set_socket(shader, ('Transmission Weight', 'Transmission'), float(spec['transmission']))
    if float(spec.get('emission_strength', 0.0)) > 0.0:
        _set_socket(shader, ('Emission Color', 'Emission'), spec.get('emission_color', spec['base_color']))
        _set_socket(shader, ('Emission Strength',), float(spec['emission_strength']))
    links.new(shader.outputs['BSDF'], output.inputs['Surface'])
    return material


def _slot_materials(legacy, scene, spec):
    return [
        _starter_material(legacy, scene, spec['slot_materials'][slot])
        for slot in spec['material_slots']
    ]


def _bevel(obj, dimensions, segments):
    modifier = obj.modifiers.new('AWFUL Bevel', 'BEVEL')
    modifier.width = min(float(value) for value in dimensions) * 0.10
    modifier.segments = int(segments)
    return modifier


def _mark_primary(obj, materials):
    obj['awful_mockup_primary'] = True
    obj.data.materials.clear()
    for material in materials:
        obj.data.materials.append(material)


def _add_cylinder(legacy, collection, root, name, role, radius, height, z, segments, material=None):
    bpy = legacy.bpy
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=64, radius=float(radius), depth=float(height), location=(0.0, 0.0, float(z)))
    obj = bpy.context.object
    obj.name = name
    legacy.mark_managed(obj, role)
    legacy.mark_managed(obj.data, role + '_MESH')
    legacy.link_object_to_collection(obj, collection)
    obj.parent = root
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    if material is not None:
        obj.data.materials.append(material)
    return obj


def _build_bottle(legacy, scene, collection, root, spec, materials):
    width, depth, height = map(float, spec['dimensions_m'])
    body_height = height * 0.82
    neck_height = height * 0.11
    cap_height = height - body_height - neck_height
    body = _add_cylinder(
        legacy, collection, root, 'MOCKUP_Bottle_Body', 'MOCKUP_BOTTLE_BODY',
        width * 0.5, body_height, body_height * 0.5,
        spec['bevel_segments'])
    _mark_primary(body, materials)
    _bevel(body, (width, depth, body_height), spec['bevel_segments'])
    neck = _add_cylinder(
        legacy, collection, root, 'MOCKUP_Bottle_Neck', 'MOCKUP_BOTTLE_NECK',
        width * 0.28, neck_height, body_height + neck_height * 0.5,
        spec['bevel_segments'], materials[0])
    cap = _add_cylinder(
        legacy, collection, root, 'MOCKUP_Bottle_Cap', 'MOCKUP_BOTTLE_CAP',
        width * 0.32, cap_height, body_height + neck_height + cap_height * 0.5,
        spec['bevel_segments'], materials[1])
    return body, neck, cap


def _build_jar(legacy, scene, collection, root, spec, materials):
    width, depth, height = map(float, spec['dimensions_m'])
    body_height = height * 0.82
    lid_height = height - body_height
    body = _add_cylinder(
        legacy, collection, root, 'MOCKUP_Jar_Body', 'MOCKUP_JAR_BODY',
        width * 0.5, body_height, body_height * 0.5,
        spec['bevel_segments'])
    _mark_primary(body, materials)
    _bevel(body, (width, depth, body_height), spec['bevel_segments'])
    lid = _add_cylinder(
        legacy, collection, root, 'MOCKUP_Jar_Lid', 'MOCKUP_JAR_LID',
        width * 0.5, lid_height, body_height + lid_height * 0.5,
        spec['bevel_segments'], materials[1])
    return body, lid


def _build_box(legacy, scene, collection, root, spec, materials):
    width, depth, height = map(float, spec['dimensions_m'])
    body = legacy.add_box(
        'MOCKUP_Box_Body', 'MOCKUP_BOX_BODY',
        (0.0, 0.0, height * 0.5), (width, depth, height), collection,
        camera_visible=True)
    body.parent = root
    _mark_primary(body, materials)
    _bevel(body, (width, depth, height), spec['bevel_segments'])
    return (body,)


def _build_can(legacy, scene, collection, root, spec, materials):
    width, depth, height = map(float, spec['dimensions_m'])
    body_height = height * 0.94
    top_height = height - body_height
    body = _add_cylinder(
        legacy, collection, root, 'MOCKUP_Can_Body', 'MOCKUP_CAN_BODY',
        width * 0.5, body_height, body_height * 0.5,
        spec['bevel_segments'])
    _mark_primary(body, materials)
    _bevel(body, (width, depth, body_height), spec['bevel_segments'])
    top = _add_cylinder(
        legacy, collection, root, 'MOCKUP_Can_Top', 'MOCKUP_CAN_TOP',
        width * 0.49, top_height, body_height + top_height * 0.5,
        spec['bevel_segments'], materials[1])
    return body, top


def _build_device(legacy, scene, collection, root, spec, materials, label):
    width, depth, height = map(float, spec['dimensions_m'])
    body = legacy.add_box(
        f'MOCKUP_{label}_Body', f'MOCKUP_{label.upper()}_BODY',
        (0.0, 0.0, height * 0.5), (width, depth, height), collection,
        camera_visible=True)
    body.parent = root
    _mark_primary(body, materials)
    _bevel(body, (width, depth, height), spec['bevel_segments'])

    screen_width = width * 0.90
    screen_height = height * 0.91
    screen_depth = min(depth * 0.10, 0.0007)
    screen = legacy.add_box(
        f'MOCKUP_{label}_Screen', f'MOCKUP_{label.upper()}_SCREEN',
        (0.0, -depth * 0.5 + screen_depth * 0.5, height * 0.5),
        (screen_width, screen_depth, screen_height), collection,
        materials[2], camera_visible=True)
    screen.parent = root
    return body, screen


def create_mockup(legacy, scene, key):
    spec = mockup_spec(key)
    collection = legacy.REG.collection('COL_PRODUCT')
    if collection is None:
        raise RuntimeError('AWFUL product collection is missing; Build Studio first')
    root = legacy.add_empty(
        f'MOCKUP_{key}_ROOT', 'MOCKUP_ROOT', (0.0, 0.0, 0.0),
        collection, 'PLAIN_AXES', 0.10)
    root['awful_mockup_key'] = key
    root['awful_mockup_source_dimensions_m'] = tuple(float(value) for value in spec['dimensions_m'])
    materials = _slot_materials(legacy, scene, spec)

    if key == 'BOTTLE':
        _build_bottle(legacy, scene, collection, root, spec, materials)
    elif key == 'JAR':
        _build_jar(legacy, scene, collection, root, spec, materials)
    elif key == 'BOX':
        _build_box(legacy, scene, collection, root, spec, materials)
    elif key == 'CAN':
        _build_can(legacy, scene, collection, root, spec, materials)
    elif key == 'PHONE':
        _build_device(legacy, scene, collection, root, spec, materials, 'Phone')
    elif key == 'TABLET':
        _build_device(legacy, scene, collection, root, spec, materials, 'Tablet')
    else:
        raise ValueError(f'Unknown AWFUL mockup: {key}')
    return root


def _mounted_unmanaged_products(legacy, scene):
    content = legacy.REG.object('PRODUCT_CONTENT')
    if content is None:
        return []
    result = []
    for child in content.children:
        if legacy.ownership.owned(child, scene):
            continue
        hierarchy = [child] + legacy.descendants(child)
        if legacy.world_bbox(hierarchy) is not None:
            result.append(child)
    return result


def _guard_mockup_hierarchies(legacy, scene):
    for root in mockup_roots(legacy, scene):
        foreign = [
            child for child in legacy.descendants(root)
            if not legacy.ownership.owned(child, scene)
        ]
        if foreign:
            raise RuntimeError(
                'User data is parented under the AWFUL mockup; detach it before replacing the mockup')


def _purge_orphan_mockup_data(legacy, scene):
    bpy = legacy.bpy
    for mesh in list(bpy.data.meshes):
        if (legacy.ownership.owned(mesh, scene)
                and str(mesh.get(legacy.ROLE_KEY, '')).startswith('MOCKUP_')
                and mesh.users == 0):
            bpy.data.meshes.remove(mesh)
    for material in list(bpy.data.materials):
        if (legacy.ownership.owned(material, scene)
                and str(material.get(legacy.ROLE_KEY, '')).startswith('MOCKUP_MAT_')
                and material.users == 0):
            bpy.data.materials.remove(material)


def _remove_owned_mockups(legacy, scene):
    _guard_mockup_hierarchies(legacy, scene)
    for root in list(mockup_roots(legacy, scene)):
        legacy.delete_object_hierarchy(root)
    _purge_orphan_mockup_data(legacy, scene)


def replace_mockup(legacy, scene, key):
    mockup_spec(key)
    legacy.ownership.preflight(scene)
    unmanaged = _mounted_unmanaged_products(legacy, scene)
    if unmanaged:
        raise RuntimeError(
            'A user product is mounted; unmount it before generating an AWFUL mockup')
    _guard_mockup_hierarchies(legacy, scene)
    with legacy.ownership.for_scene(scene):
        _remove_owned_mockups(legacy, scene)
        root = create_mockup(legacy, scene, key)
        legacy.mount_product([root], bool(scene.awful_studio.auto_fit))
        _purge_orphan_mockup_data(legacy, scene)
    return root


def install(legacy):
    if getattr(legacy, '_awful_product_quality_installed', False):
        return

    items = [('NONE', 'None', 'Keep the diagnostic fixture or mounted user product')]
    items.extend((key, MOCKUP_SPECS[key]['label'], f'Generate AWFUL {MOCKUP_SPECS[key]["label"]} mockup')
                 for key in mockup_keys())
    annotations = legacy.AWFUL_StudioSettings.__annotations__
    annotations['product_mockup'] = legacy.EnumProperty(
        name='Mockup', items=items, default='NONE')

    original_draw = legacy.AWFUL_PT_Product.draw

    def draw_product(self, context):
        original_draw(self, context)
        layout = self.layout
        settings = context.scene.awful_studio
        box = layout.box()
        box.label(text='Procedural Mockup')
        box.prop(settings, 'product_mockup', text='Mockup')
        row = box.row()
        row.enabled = settings.product_mockup != 'NONE'
        row.operator('awful.generate_mockup', text='Generate / Replace AWFUL Mockup')

    legacy.AWFUL_PT_Product.draw = draw_product

    original_diagnostic = legacy.create_diagnostic_product

    def create_diagnostic_or_selected_mockup(diag_col, material):
        scene = legacy.bpy.context.scene
        key = getattr(scene.awful_studio, 'product_mockup', 'NONE')
        if key != 'NONE':
            return create_mockup(legacy, scene, key)
        return original_diagnostic(diag_col, material)

    legacy.create_diagnostic_product = create_diagnostic_or_selected_mockup
    legacy._awful_product_quality_installed = True
