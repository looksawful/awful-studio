"""Explicit, non-rebuilding data migrations. Version 0 is the historical script schema."""
import uuid
import bpy
from . import ownership

CURRENT_SCHEMA = 1


def migration_path(version, target=CURRENT_SCHEMA):
    if not isinstance(version, int) or version < 0 or version > target:
        raise ValueError(f'Unsupported AWFUL scene schema: {version}')
    return list(range(version, target))


def migrate(scene):
    state = scene.awful_state
    path = migration_path(state.schema_version)
    if not path:
        return False
    historical = [o for o in scene.objects if o.get('awful_managed') and not o.get('awful_owner')]
    if not historical:
        raise ValueError('This file has no historical AWFUL studio to migrate')
    for other in bpy.data.scenes:
        if other != scene and any(o.name in other.objects for o in historical):
            raise ValueError('Historical AWFUL objects are shared across scenes')
    state.owner_id = state.owner_id or uuid.uuid4().hex
    # Metadata only. Never reconstruct geometry, lights, world or user transforms.
    for obj in historical:
        ownership.mark(obj, obj.get('awful_role', 'OBJECT'))
        if obj.data and obj.data.get('awful_managed'):
            ownership.mark(obj.data, obj.data.get('awful_role', 'DATA'))
    for col in scene.collection.children_recursive:
        if col.get('awful_managed') and not col.get('awful_owner'):
            ownership.mark(col, col.get('awful_role', 'COLLECTION'))
    materials = {m for o in historical for m in getattr(o.data, 'materials', ()) if m}
    for block in materials | ({scene.world} if scene.world else set()):
        if block.get('awful_managed') and not block.get('awful_owner'):
            ownership.mark(block, block.get('awful_role', 'DATA'))
    state.schema_version = CURRENT_SCHEMA
    state.built = True
    return True
