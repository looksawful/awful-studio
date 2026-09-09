import importlib.util
import pathlib
import sys
import types
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
MIGRATIONS = ROOT / 'extension' / 'awful_studio' / 'migrations.py'


class Block(dict):
    __hash__ = object.__hash__

    def __init__(self, name, *, data=None, materials=()):
        super().__init__()
        self.name = name
        self.data = data
        self.materials = list(materials)


class Object(Block):
    pass


class Collection(Block):
    def __init__(self, name, children=()):
        super().__init__(name)
        self.children_recursive = list(children)


class State:
    def __init__(self, schema_version=0, owner_id=''):
        self.schema_version = schema_version
        self.owner_id = owner_id
        self.built = False


class Scene:
    def __init__(self, name, objects=(), collections=(), world=None):
        self.name = name
        self.objects = list(objects)
        self.collection = Collection(name + '_ROOT', collections)
        self.world = world
        self.awful_state = State()


def managed(block, role):
    block['awful_managed'] = True
    block['awful_role'] = role
    return block


def load_migrations(scenes, context_scene):
    bpy = types.ModuleType('bpy')
    bpy.data = types.SimpleNamespace(scenes=scenes)
    bpy.context = types.SimpleNamespace(scene=context_scene)
    sys.modules['bpy'] = bpy

    package = types.ModuleType('awful_studio')
    package.__path__ = []
    sys.modules['awful_studio'] = package

    ownership = types.ModuleType('awful_studio.ownership')
    ownership.KEY = 'awful_owner'
    ownership.MANAGED = 'awful_managed'
    ownership.ROLE = 'awful_role'

    def owner(scene):
        return scene.awful_state.owner_id

    def mark(block, role=''):
        oid = owner(bpy.context.scene)
        if not oid:
            raise RuntimeError('Build or migrate a studio before creating AWFUL data')
        block['awful_managed'] = True
        block['awful_owner'] = oid
        block['awful_role'] = role
        block['awful_version'] = '0.0.16'
        return block

    ownership.owner = owner
    ownership.mark = mark
    sys.modules['awful_studio.ownership'] = ownership

    spec = importlib.util.spec_from_file_location('awful_studio.migrations', MIGRATIONS)
    module = importlib.util.module_from_spec(spec)
    sys.modules['awful_studio.migrations'] = module
    spec.loader.exec_module(module)
    return module


class MigrationTests(unittest.TestCase):
    def test_schema_bool_is_rejected(self):
        scene = Scene('Target')
        migrations = load_migrations([scene], scene)
        with self.assertRaises(ValueError):
            migrations.migration_path(True)

    def test_target_scene_does_not_depend_on_active_context(self):
        mesh = managed(Block('Mesh'), 'CYC_MESH')
        obj = managed(Object('CYC', data=mesh), 'CYC')
        target = Scene('Target', [obj])
        active = Scene('Active')
        migrations = load_migrations([target, active], active)

        self.assertTrue(migrations.migrate(target))
        self.assertEqual(obj.get('awful_owner'), target.awful_state.owner_id)
        self.assertEqual(mesh.get('awful_owner'), target.awful_state.owner_id)
        self.assertFalse(active.awful_state.owner_id)

    def test_shared_historical_data_is_rejected_before_mutation(self):
        mesh = managed(Block('SharedMesh'), 'CYC_MESH')
        target_obj = managed(Object('CYC', data=mesh), 'CYC')
        foreign_obj = Object('Foreign', data=mesh)
        target = Scene('Target', [target_obj])
        foreign = Scene('Foreign', [foreign_obj])
        migrations = load_migrations([target, foreign], target)

        with self.assertRaises(ValueError):
            migrations.migrate(target)
        self.assertEqual(target.awful_state.schema_version, 0)
        self.assertEqual(target.awful_state.owner_id, '')
        self.assertNotIn('awful_owner', target_obj)
        self.assertNotIn('awful_owner', mesh)

    def test_metadata_surface_and_idempotence(self):
        material = managed(Block('Material'), 'CYC_MAT')
        mesh = managed(Block('Mesh', materials=[material]), 'CYC_MESH')
        obj = managed(Object('CYC', data=mesh), 'CYC')
        child = managed(Collection('AWFUL_STUDIO'), 'ROOT')
        world = managed(Block('World'), 'WORLD')
        scene = Scene('Target', [obj], [child], world)
        migrations = load_migrations([scene], scene)

        self.assertTrue(migrations.migrate(scene))
        oid = scene.awful_state.owner_id
        self.assertTrue(oid)
        for block in (obj, mesh, material, child, world):
            self.assertEqual(block.get('awful_owner'), oid)
        snapshot = [dict(block) for block in (obj, mesh, material, child, world)]
        self.assertFalse(migrations.migrate(scene))
        self.assertEqual(snapshot, [dict(block) for block in (obj, mesh, material, child, world)])


if __name__ == '__main__':
    unittest.main()
