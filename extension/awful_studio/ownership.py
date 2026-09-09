"""Scene-scoped ownership. Names and semantic roles alone never grant ownership."""
from contextlib import contextmanager
import uuid
import bpy

KEY = 'awful_owner'
MANAGED = 'awful_managed'
ROLE = 'awful_role'
VERSION_KEY = 'awful_version'
GROUPS = ('objects', 'collections', 'meshes', 'curves', 'cameras', 'lights',
          'materials', 'worlds', 'node_groups', 'actions', 'images')
_MARK_SCENE = None


def owner(scene):
    return scene.awful_state.owner_id


def owned(block, scene):
    return bool(block and owner(scene) and block.get(MANAGED) and block.get(KEY) == owner(scene))


@contextmanager
def for_scene(scene):
    """Bind legacy factory calls to one explicit scene for the duration of an operation."""
    global _MARK_SCENE
    previous = _MARK_SCENE
    _MARK_SCENE = scene
    try:
        yield
    finally:
        _MARK_SCENE = previous


def mark(block, role='', scene=None):
    scene = scene or _MARK_SCENE or getattr(bpy.context, 'scene', None)
    if scene is None or not owner(scene):
        raise RuntimeError('Build or migrate a studio before creating AWFUL data')
    block[MANAGED] = True
    block[KEY] = owner(scene)
    block[ROLE] = role
    block[VERSION_KEY] = '0.0.16'
    return block


def detach(block):
    """Transfer a retained managed datablock back to user ownership."""
    for key in (MANAGED, KEY, ROLE, VERSION_KEY):
        try:
            if key in block:
                del block[key]
        except (TypeError, ReferenceError):
            pass
    return block


def mark_generated_actions(scene):
    """Adopt only animation actions reachable from objects already owned by this scene."""
    for obj in scene.objects:
        if not owned(obj, scene):
            continue
        for source in (obj, getattr(obj, 'data', None)):
            animation = getattr(source, 'animation_data', None)
            action = getattr(animation, 'action', None) if animation else None
            if action and not owned(action, scene):
                mark(action, 'ACTION', scene)


def preflight(scene):
    """Refuse ambiguous cross-scene ownership before any destructive mutation."""
    oid = owner(scene)
    if oid and any(s != scene and hasattr(s, 'awful_state') and owner(s) == oid for s in bpy.data.scenes):
        raise RuntimeError('AWFUL scene ownership is shared; make an independent studio before rebuilding')
    objects = {o for o in scene.objects if owned(o, scene)}
    collections = {c for c in scene.collection.children_recursive if owned(c, scene)}
    for other in bpy.data.scenes:
        if other != scene and (objects.intersection(other.objects[:]) or
                              collections.intersection(other.collection.children_recursive)):
            raise RuntimeError('AWFUL data is linked to another scene; unlink it before rebuilding')
    # Parenting is global object state. Removing a parent owned by this scene would
    # mutate a child that lives only in another scene, even when the parent itself
    # is not linked there. Refuse rather than silently altering foreign scene data.
    scene_objects = set(scene.objects)
    if any(obj not in scene_objects and obj.parent in objects for obj in bpy.data.objects):
        raise RuntimeError('External scene object is parented to AWFUL data; detach it before rebuilding')


def initialize(scene):
    if not owner(scene):
        if any(o.get(MANAGED) and not o.get(KEY) for o in scene.objects):
            raise RuntimeError('Historical AWFUL scene: use Upgrade Historical AWFUL Scene first')
        scene.awful_state.owner_id = uuid.uuid4().hex
    preflight(scene)
    state = scene.awful_state
    if scene.world and not owned(scene.world, scene):
        state.previous_world = scene.world
    if scene.camera and not owned(scene.camera, scene):
        state.previous_camera = scene.camera


def detach_retained(scene):
    """User-referenced generated data survives cleanup without stale AWFUL ownership."""
    for name in GROUPS[2:]:
        for block in list(getattr(bpy.data, name)):
            if owned(block, scene) and block.users > 0:
                detach(block)


def remove(scene):
    preflight(scene)
    # External objects nested inside managed collections must stay linked and visible.
    managed_cols = [c for c in scene.collection.children_recursive if owned(c, scene)]
    for col in managed_cols:
        for obj in list(col.objects):
            if not owned(obj, scene) and obj.name not in scene.collection.objects:
                scene.collection.objects.link(obj)
        for child in list(col.children):
            if not owned(child, scene) and child.name not in scene.collection.children:
                scene.collection.children.link(child)
    for obj in list(scene.objects):
        if not owned(obj, scene) and obj.parent and owned(obj.parent, scene):
            world_matrix = obj.matrix_world.copy()
            obj.parent = None
            obj.matrix_world = world_matrix
    if owned(scene.world, scene):
        scene.world = scene.awful_state.previous_world
    if owned(scene.camera, scene):
        scene.camera = scene.awful_state.previous_camera
    comp = getattr(scene, 'compositing_node_group', None)
    if owned(comp, scene):
        scene.compositing_node_group = None
    for obj in list(scene.objects):
        if owned(obj, scene):
            bpy.data.objects.remove(obj, do_unlink=True)
    for col in managed_cols:
        bpy.data.collections.remove(col)
    # Multiple passes resolve dependency order (mesh -> material -> image, action).
    for _ in range(len(GROUPS)):
        count = 0
        for name in GROUPS[2:]:
            group = getattr(bpy.data, name)
            for block in list(group):
                if owned(block, scene) and block.users == 0:
                    group.remove(block)
                    count += 1
        if not count:
            break
    # Any generated datablock deliberately retained because a user datablock still
    # references it is no longer safe to treat as destructively managed by AWFUL.
    detach_retained(scene)
    scene['awful_post_pipeline_enabled'] = False
    scene.awful_state.built = False
