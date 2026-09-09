"""Explicit, metadata-only migrations for historical AWFUL scenes."""
import uuid
import bpy
from . import ownership

CURRENT_SCHEMA = 1
_VERSION = '0.0.16'
_MISSING = object()


def migration_path(version, target=CURRENT_SCHEMA):
    if type(version) is not int or type(target) is not int or version < 0 or target < 0 or version > target:
        raise ValueError(f'Unsupported AWFUL scene schema: {version}')
    return list(range(version, target))


def _append_identity_unique(items, block):
    if block is not None and not any(existing is block for existing in items):
        items.append(block)


def _scene_surface(scene, *, managed_only=False):
    """Return datablocks physically referenced by a scene on the 0.0.15 migration surface."""
    blocks = []

    def add(block):
        if block is None:
            return
        if managed_only and not block.get(ownership.MANAGED):
            return
        _append_identity_unique(blocks, block)

    for obj in scene.objects:
        add(obj)
        data = getattr(obj, 'data', None)
        add(data)
        for material in getattr(data, 'materials', ()) if data is not None else ():
            add(material)
    for collection in scene.collection.children_recursive:
        add(collection)
    add(scene.world)
    add(getattr(scene, 'compositing_node_group', None))
    return blocks


def _historical_surface(scene):
    return _scene_surface(scene, managed_only=True)


def _validate_historical(scene, blocks):
    if not blocks or not any(any(block is obj for obj in scene.objects) for block in blocks):
        raise ValueError('This file has no historical AWFUL studio to migrate')
    if scene.awful_state.owner_id:
        raise ValueError('Historical AWFUL schema already contains scene ownership metadata')
    tagged = [block for block in blocks if block.get(ownership.KEY)]
    if tagged:
        raise ValueError('Historical AWFUL schema contains partial ownership metadata')

    for other in bpy.data.scenes:
        if other is scene:
            continue
        foreign = _scene_surface(other)
        if any(any(block is candidate for candidate in foreign) for block in blocks):
            raise ValueError('Historical AWFUL data is shared across scenes')


def _mark_for_owner(block, owner_id):
    block[ownership.MANAGED] = True
    block[ownership.KEY] = owner_id
    block[ownership.ROLE] = block.get(ownership.ROLE, 'DATA')
    block['awful_version'] = _VERSION


def _restore_metadata(block, previous):
    for key, value in previous.items():
        if value is _MISSING:
            if key in block:
                del block[key]
        else:
            block[key] = value


def migrate(scene):
    state = scene.awful_state
    path = migration_path(state.schema_version)
    if not path:
        return False
    if path != [0]:
        raise ValueError(f'No migration implementation for AWFUL schema path: {path}')

    blocks = _historical_surface(scene)
    _validate_historical(scene, blocks)

    owner_id = uuid.uuid4().hex
    keys = (ownership.MANAGED, ownership.KEY, ownership.ROLE, 'awful_version')
    previous = [(block, {key: block[key] if key in block else _MISSING for key in keys}) for block in blocks]
    try:
        for block in blocks:
            _mark_for_owner(block, owner_id)
    except Exception:
        for block, metadata in previous:
            _restore_metadata(block, metadata)
        raise

    state.owner_id = owner_id
    state.schema_version = CURRENT_SCHEMA
    state.built = True
    return True
