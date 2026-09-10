import ast
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
OWNERSHIP = ROOT / 'extension' / 'awful_studio' / 'ownership.py'
LIFECYCLE = ROOT / 'extension' / 'awful_studio' / '__init__.py'


class OwnershipSafetySourceTests(unittest.TestCase):
    def test_generation_tracking_does_not_use_pointer_identity(self):
        source = OWNERSHIP.read_text(encoding='utf-8')
        self.assertNotIn('as_pointer()', source)

    def test_lifecycle_does_not_use_global_snapshot_marking_bridge(self):
        source = LIFECYCLE.read_text(encoding='utf-8')
        self.assertNotIn('ownership.snapshot()', source)
        self.assertNotIn('ownership.mark_generated(', source)

    def test_mark_accepts_explicit_scene(self):
        tree = ast.parse(OWNERSHIP.read_text(encoding='utf-8'))
        mark = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'mark')
        args = [arg.arg for arg in mark.args.args]
        self.assertIn('scene', args)

    def test_mark_never_falls_back_to_active_context_scene(self):
        source = OWNERSHIP.read_text(encoding='utf-8')
        self.assertNotIn("getattr(bpy.context, 'scene', None)", source)

    def test_build_uses_explicit_scene_ownership_scope(self):
        source = LIFECYCLE.read_text(encoding='utf-8')
        self.assertIn('with ownership.for_scene(scene):', source)

    def test_migrate_uses_explicit_scene_ownership_scope(self):
        source = LIFECYCLE.read_text(encoding='utf-8')
        self.assertIn('with ownership.for_scene(context.scene):', source)

    def test_remove_does_not_scan_all_objects_for_external_children(self):
        tree = ast.parse(OWNERSHIP.read_text(encoding='utf-8'))
        remove = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'remove')
        text = ast.unparse(remove)
        self.assertNotIn('for obj in list(bpy.data.objects)', text)

    def test_remove_detaches_retained_owned_datablocks(self):
        source = OWNERSHIP.read_text(encoding='utf-8')
        self.assertIn('detach_retained', source)

    def test_remove_cleans_owned_unlinked_collections(self):
        tree = ast.parse(OWNERSHIP.read_text(encoding='utf-8'))
        remove = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'remove')
        text = ast.unparse(remove)
        self.assertIn('bpy.data.collections', text)
        self.assertIn('owned(c, scene)', text)

    def test_registry_collection_lookup_includes_owned_unlinked_collections(self):
        source = LIFECYCLE.read_text(encoding='utf-8')
        self.assertIn('def _collection_for_scene_registry(', source)
        self.assertIn('for c in bpy.data.collections', source)
        self.assertIn('ownership.owned(c, scene)', source)
        self.assertIn('legacy.StudioRegistry.collection = _collection_for_scene_registry', source)


if __name__ == '__main__':
    unittest.main()
