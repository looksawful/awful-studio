# SPDX-License-Identifier: GPL-3.0-or-later
"""Bundled device-asset catalog and Blender append adapter."""
from __future__ import annotations

from copy import deepcopy
import math
from pathlib import Path


DEVICE_ASSET_SPECS = {
    'DEVICE_IPHONE_17': {
        'label': 'iPhone 17 v30 (LOW draft)',
        'asset_id': 'iphone_17',
        'stage': 'LOW_DRAFT',
        'dimensions_m': (0.07145, 0.00795, 0.14961),
        'default_lod': 'LOW',
        'lods': {'LOW': {'variant': 'low_v30', 'blend_path': 'assets/devices/iphone_17_low_v30.blend', 'entry_collection': 'AWFUL_DEVICE_IPHONE_17', 'source_revision': '4779cf8a01a0bb9623656fa580d9979b6876d515410c30922644434477b5ea13'}},
        'root_name': 'CTRL_IPHONE_17',
        'orientation_axis': 'Y',
        'screen_object': 'SCREEN_CONTENT',
        'screen_material': 'MAT_SCREEN_CONTENT',
    },
    'DEVICE_IPAD_PRO_11': {
        'label': 'iPad Pro 11 M5',
        'asset_id': 'ipad_pro_11_m5',
        'stage': 'LOW_DRAFT',
        'dimensions_m': (0.1775, 0.0053, 0.2497),
        'default_lod': 'LOW',
        'lods': {'LOW': {'variant': 'low_v6', 'blend_path': 'assets/devices/ipad_pro_11_m5_low_v6.blend', 'entry_collection': 'AWFUL_DEVICE_IPAD_PRO_11', 'source_revision': 'a719672382a63a1d753f11c5d3cdc179d9007442bfeb30de2841e3d4e5099d1d'}},
        'root_name': 'CTRL_IPAD_PRO_11',
        'orientation_axis': 'Y',
        'screen_object': 'SCREEN_CONTENT',
        'screen_material': 'MAT_SCREEN_CONTENT',
    },
    'DEVICE_IPAD_PRO_13': {
        'label': 'iPad Pro 13 M5',
        'asset_id': 'ipad_pro_13_m5',
        'stage': 'LOW_DRAFT',
        'dimensions_m': (0.2155, 0.0051, 0.2816),
        'default_lod': 'LOW',
        'lods': {'LOW': {'variant': 'low_v6', 'blend_path': 'assets/devices/ipad_pro_13_m5_low_v6.blend', 'entry_collection': 'AWFUL_DEVICE_IPAD_PRO_13', 'source_revision': '443e7ff80fea1c3ed07756b739e77215683f54038b26abe45b88f88d041e8924'}},
        'root_name': 'CTRL_IPAD_PRO_13',
        'orientation_axis': 'Y',
        'screen_object': 'SCREEN_CONTENT',
        'screen_material': 'MAT_SCREEN_CONTENT',
    },
    'DEVICE_MACBOOK_PRO_14': {
        'label': 'MacBook Pro 14 M5',
        'asset_id': 'macbook_pro_14_m5',
        'stage': 'RELEASE_CANDIDATE',
        'dimensions_m': (0.3126, 0.2212, 0.0155),
        'default_lod': 'LOW',
        'lods': {'LOW': {'variant': 'low_v1_release', 'blend_path': 'assets/devices/macbook_pro_14_m5_low_v1_release.blend', 'entry_collection': 'AWFUL_DEVICE_MACBOOK_PRO_14', 'source_revision': '733c4c0d6d1e789b22f58d07380bbd88c5541e87266b124c46a68883c92e13f1'}},
        'root_name': 'CTRL_MACBOOK_PRO_14',
        'screen_object': 'SCREEN_CONTENT',
        'screen_material': 'MAT_SCREEN_CONTENT',
        'controls': ('CTRL_HINGE',),
    },
}

HINGE_PRESETS_DEGREES = {
    'CLOSED': 0.0,
    '30': 30.0,
    '60': 60.0,
    '90': 90.0,
    '102': 102.0,
}

ORIENTATION_PRESETS_DEGREES = {
    'PORTRAIT': 0.0,
    'LANDSCAPE_LEFT': 90.0,
    'LANDSCAPE_RIGHT': -90.0,
    'PORTRAIT_INVERTED': 180.0,
}


def device_asset_keys() -> tuple[str, ...]:
    return tuple(DEVICE_ASSET_SPECS)


def device_asset_spec(key: str) -> dict:
    try:
        return deepcopy(DEVICE_ASSET_SPECS[key])
    except KeyError as exc:
        raise ValueError(f'Unknown AWFUL device asset: {key}') from exc



def hinge_preset_keys(key: str) -> tuple[str, ...]:
    spec = device_asset_spec(key)
    if 'CTRL_HINGE' not in spec.get('controls', ()):
        raise ValueError(f'AWFUL device asset has no hinge presets: {key}')
    return tuple(HINGE_PRESETS_DEGREES)


def hinge_angle_degrees(key: str, preset: str) -> float:
    hinge_preset_keys(key)
    try:
        return float(HINGE_PRESETS_DEGREES[preset])
    except KeyError as exc:
        raise ValueError(f'Unknown AWFUL hinge preset: {preset}') from exc


def orientation_preset_keys(key: str) -> tuple[str, ...]:
    spec = device_asset_spec(key)
    if spec.get('orientation_axis') != 'Y':
        raise ValueError(f'AWFUL device asset has no orientation presets: {key}')
    return tuple(ORIENTATION_PRESETS_DEGREES)


def orientation_angle_degrees(key: str, preset: str) -> float:
    orientation_preset_keys(key)
    try:
        return float(ORIENTATION_PRESETS_DEGREES[preset])
    except KeyError as exc:
        raise ValueError(f'Unknown AWFUL orientation preset: {preset}') from exc


def lod_keys(key: str) -> tuple[str, ...]:
    return tuple(device_asset_spec(key)['lods'])


def lod_spec(key: str, lod: str | None = None) -> dict:
    spec = device_asset_spec(key)
    selected = lod or spec['default_lod']
    try:
        return deepcopy(spec['lods'][selected])
    except KeyError as exc:
        raise ValueError(f'Unknown AWFUL device LOD {selected}: {key}') from exc


def device_asset_path(key: str, lod: str | None = None) -> Path:
    item = lod_spec(key, lod)
    return Path(__file__).resolve().parent / item['blend_path']


def is_device_asset_key(key: str) -> bool:
    return key in DEVICE_ASSET_SPECS



def _active_device_root(legacy, scene):
    roots = [obj for obj in scene.objects
             if legacy.ownership.owned(obj, scene)
             and obj.get(legacy.ROLE_KEY, '') == 'MOCKUP_ROOT'
             and is_device_asset_key(str(obj.get('awful_mockup_key', '')))]
    if len(roots) != 1:
        raise RuntimeError('Exactly one AWFUL device asset must be active')
    return roots[0]


def _screen_object(legacy, root, spec):
    expected = spec['screen_object']
    for obj in [root] + legacy.descendants(root):
        if obj.name == expected or obj.name.startswith(expected + '.'):
            return obj
    raise RuntimeError(f'AWFUL device asset is missing {expected}')


def _principled(material):
    for node in material.node_tree.nodes:
        if node.bl_idname == 'ShaderNodeBsdfPrincipled':
            return node
    raise RuntimeError(f'{material.name} is missing Principled BSDF')


def apply_screen_image(legacy, scene, filepath):
    root = _active_device_root(legacy, scene)
    spec = device_asset_spec(str(root['awful_mockup_key']))
    path = Path(filepath).expanduser().resolve()
    if not path.is_file():
        raise ValueError(f'Screen artwork file does not exist: {path}')
    screen = _screen_object(legacy, root, spec)
    material = next((m for m in screen.data.materials if m is not None), None)
    if material is None:
        raise RuntimeError(f'{screen.name} has no screen material')
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    shader = _principled(material)
    image_node = nodes.get('AWFUL_SCREEN_IMAGE')
    if image_node is None:
        image_node = nodes.new('ShaderNodeTexImage')
        image_node.name = 'AWFUL_SCREEN_IMAGE'
        image_node.label = 'AWFUL Screen Artwork'
    previous_image = image_node.image
    with legacy.ownership.for_scene(scene):
        image = legacy.bpy.data.images.load(str(path), check_existing=False)
        image.pack()
        legacy.mark_managed(image, _managed_role('MOCKUP_DEVICE_SCREEN_IMAGE', str(root['awful_mockup_key']), path.stem))
    image_node.image = image
    if (previous_image is not None and previous_image != image
            and legacy.ownership.owned(previous_image, scene)
            and previous_image.users == 0):
        legacy.bpy.data.images.remove(previous_image)
    for socket_name in ('Base Color', 'Emission Color', 'Emission'):
        socket = shader.inputs.get(socket_name)
        if socket is not None:
            for old in list(socket.links):
                links.remove(old)
            links.new(image_node.outputs['Color'], socket)
    strength = shader.inputs.get('Emission Strength')
    if strength is not None:
        strength.default_value = 1.0
    root['awful_screen_artwork_name'] = path.name
    screen['awful_screen_artwork_name'] = path.name
    return screen


def apply_hinge_preset(legacy, scene, preset: str):
    root = _active_device_root(legacy, scene)
    key = str(root['awful_mockup_key'])
    angle = hinge_angle_degrees(key, preset)
    controls = device_asset_spec(key).get('controls', ())
    hinge_name = 'CTRL_HINGE'
    if hinge_name not in controls:
        raise ValueError(f'AWFUL device asset has no hinge control: {key}')
    hinge = next((obj for obj in [root] + legacy.descendants(root)
                  if obj.name == hinge_name or obj.name.startswith(hinge_name + '.')), None)
    if hinge is None:
        raise RuntimeError(f'AWFUL device asset is missing {hinge_name}')
    hinge.rotation_mode = 'XYZ'
    hinge.rotation_euler.x = math.radians(90.0 - angle)
    hinge['open_angle_deg'] = angle
    hinge['preset'] = preset
    root['awful_hinge_preset'] = preset
    return hinge


def _managed_role(prefix: str, key: str, name: str = '') -> str:
    suffix = name.replace(' ', '_').upper() if name else key
    return f'{prefix}_{key}_{suffix}'

def apply_orientation_preset_to_root(root, key: str, preset: str):
    spec = device_asset_spec(key)
    axis = spec.get('orientation_axis')
    if axis != 'Y':
        raise ValueError(f'AWFUL device asset has no orientation presets: {key}')
    angle = orientation_angle_degrees(key, preset)
    root.rotation_mode = 'XYZ'
    base = float(root.get('awful_orientation_base_y', root.rotation_euler.y))
    if 'awful_orientation_base_y' not in root:
        root['awful_orientation_base_y'] = base
    root.rotation_euler.y = base + math.radians(angle)
    root['awful_orientation_preset'] = preset
    root['awful_orientation_angle_deg'] = angle
    return root


def apply_orientation_preset(legacy, scene, preset: str):
    root = _active_device_root(legacy, scene)
    key = str(root['awful_mockup_key'])
    selected = str(getattr(scene.awful_studio, 'product_mockup', ''))
    if selected != key:
        raise RuntimeError('Generate the selected AWFUL device before changing orientation')
    orientation_preset_keys(key)
    foreign = [obj for obj in legacy.descendants(root)
               if not legacy.ownership.owned(obj, scene)]
    if foreign:
        raise RuntimeError('User data is parented under the AWFUL device; detach it before changing orientation')
    content = root.parent
    if content is None or content.get(legacy.ROLE_KEY, '') != 'PRODUCT_CONTENT':
        raise RuntimeError('AWFUL device is not mounted in PRODUCT_CONTENT')
    legacy.parent_keep_world(root, None)
    apply_orientation_preset_to_root(root, key, preset)
    legacy.bpy.context.view_layer.update()
    legacy.mount_product([root], bool(scene.awful_studio.auto_fit))
    return root


def create_device_asset(legacy, scene, key, lod=None):
    spec = device_asset_spec(key)
    selected_lod = lod or getattr(scene.awful_studio, 'device_lod', '') or spec['default_lod']
    lod_item = lod_spec(key, selected_lod)
    path = device_asset_path(key, selected_lod)
    if not path.is_file():
        raise RuntimeError(f'Bundled AWFUL device asset is missing: {path.name}')
    product_collection = legacy.REG.collection('COL_PRODUCT')
    if product_collection is None:
        raise RuntimeError('AWFUL product collection is missing; Build Studio first')

    bpy = legacy.bpy
    with bpy.data.libraries.load(str(path), link=False) as (data_from, data_to):
        entry = lod_item['entry_collection']
        if entry not in data_from.collections:
            raise RuntimeError(f'{path.name} is missing collection {entry}')
        data_to.collections = [entry]
    collection = data_to.collections[0]
    if collection is None:
        raise RuntimeError(f'Unable to append bundled device asset: {key}')
    product_collection.children.link(collection)
    legacy.mark_managed(collection, _managed_role('MOCKUP_DEVICE_COLLECTION', key))

    root = collection.objects.get(spec['root_name'])
    if root is None:
        raise RuntimeError(f'{path.name} is missing root {spec["root_name"]}')
    legacy.mark_managed(root, 'MOCKUP_ROOT')
    root['awful_mockup_key'] = key
    root['awful_mockup_source_dimensions_m'] = tuple(float(v) for v in spec['dimensions_m'])
    root['awful_asset_id'] = spec['asset_id']
    root['awful_asset_stage'] = spec['stage']
    root['awful_asset_lod'] = selected_lod
    root['awful_asset_variant'] = lod_item['variant']
    root['awful_asset_source_revision'] = lod_item['source_revision']
    if spec.get('orientation_axis') == 'Y':
        preset = getattr(scene.awful_studio, 'device_orientation_preset', 'PORTRAIT') or 'PORTRAIT'
        apply_orientation_preset_to_root(root, key, preset)

    for obj in [root] + legacy.descendants(root):
        if obj != root:
            legacy.mark_managed(obj, _managed_role('MOCKUP_DEVICE_OBJECT', key, obj.name))
        data = getattr(obj, 'data', None)
        if data is not None:
            legacy.mark_managed(data, _managed_role('MOCKUP_DEVICE_DATA', key, obj.name))
        if getattr(data, 'materials', None) is not None:
            for material in data.materials:
                if material is not None:
                    legacy.mark_managed(
                        material,
                        _managed_role('MOCKUP_MAT_DEVICE', key, material.name),
                    )
    return root


def purge_orphan_device_collections(legacy, scene):
    bpy = legacy.bpy
    for collection in list(bpy.data.collections):
        role = str(collection.get(legacy.ROLE_KEY, ''))
        if (legacy.ownership.owned(collection, scene)
                and role.startswith('MOCKUP_DEVICE_COLLECTION_')
                and len(collection.objects) == 0):
            bpy.data.collections.remove(collection)
    for image in list(bpy.data.images):
        role = str(image.get(legacy.ROLE_KEY, ''))
        if (legacy.ownership.owned(image, scene)
                and role.startswith('MOCKUP_DEVICE_SCREEN_IMAGE_')
                and image.users == 0):
            bpy.data.images.remove(image)
