"""Package a validated device source blend into one clean Extension library."""
import os
import sys
import bpy

argv = sys.argv[sys.argv.index('--') + 1:]

def arg(name):
    return argv[argv.index(name) + 1]

output = os.path.abspath(arg('--output'))
entry_name = arg('--entry')
root_name = arg('--root')
device_key = arg('--key')
stage = arg('--stage')
variant = arg('--variant')
revision = arg('--revision')
root = bpy.data.objects.get(root_name)
if root is None:
    raise RuntimeError(f'missing root {root_name}')

def belongs(obj):
    cur = obj
    while cur is not None:
        if cur is root:
            return True
        cur = cur.parent
    return False
device_objects = [obj for obj in bpy.data.objects if belongs(obj)]
for obj in list(bpy.data.objects):
    if not belongs(obj):
        bpy.data.objects.remove(obj, do_unlink=True)
entry = bpy.data.collections.get(entry_name) or bpy.data.collections.new(entry_name)
if entry.name not in bpy.context.scene.collection.children:
    bpy.context.scene.collection.children.link(entry)
for obj in device_objects:
    for collection in list(obj.users_collection):
        collection.objects.unlink(obj)
    entry.objects.link(obj)
root['awful_asset_id'] = str(root.get('asset_id', ''))
root['awful_asset_stage'] = stage
root['awful_asset_variant'] = variant
root['awful_device_key'] = device_key
root['awful_packaging_contract'] = '1.1'
root['awful_source_revision'] = revision
for collection in list(bpy.data.collections):
    if collection != entry and not collection.objects and not collection.children:
        bpy.data.collections.remove(collection)
try:
    bpy.ops.file.pack_all()
except Exception as exc:
    print('PACK_WARNING', exc)
os.makedirs(os.path.dirname(output), exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=output)
print('AWFUL_DEVICE_PACKAGE_OK', entry_name, len(device_objects), stage, variant, revision)
