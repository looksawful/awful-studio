"""Scene-scoped ownership. Names and semantic roles alone never grant ownership."""
import uuid
import bpy

KEY = 'awful_owner'
MANAGED = 'awful_managed'
ROLE = 'awful_role'
GROUPS = ('objects', 'collections', 'meshes', 'curves', 'cameras', 'lights',
          'materials', 'worlds', 'node_groups', 'actions', 'images')


def owner(scene):
    return scene.awful_state.owner_id


def owned(block, scene):
    return bool(block and owner(scene) and block.get(MANAGED) and block.get(KEY) == owner(scene))


def mark(block, role=''):
    scene = bpy.context.scene
    if not owner(scene):
        raise RuntimeError('Build or migrate a studio before creating AWFUL data')
    block[MANAGED] = True
    block[KEY] = owner(scene)
    block[ROLE] = role
    block['awful_version'] = '0.0.16'
    return block


def snapshot():
    return {name: {b.as_pointer() for b in getattr(bpy.data, name)} for name in GROUPS}


def mark_generated(before):
    for name in GROUPS:
        for block in getattr(bpy.data, name):
            if block.as_pointer() not in before[name]:
                mark(block, block.get(ROLE, name.upper()))
                tree = getattr(block, 'node_tree', None)
                if tree:
                    mark(tree, 'NODE_TREE')
                    for node in tree.nodes:
                        mark(node, node.name)


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
    for obj in list(bpy.data.objects):
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
    scene['awful_post_pipeline_enabled'] = False
    scene.awful_state.built = False
