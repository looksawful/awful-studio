"""The dark native USB recess must be rounded, not a nearly square-cornered box."""
import bpy,sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
if '--' in sys.argv:
 p=Path(sys.argv[sys.argv.index('--')+1])
 bpy.ops.wm.read_factory_settings(use_empty=True)
 if p.suffix.lower()=='.glb':bpy.ops.import_scene.gltf(filepath=str(p))
 else:bpy.ops.wm.open_mainfile(filepath=str(p))
bpy.context.view_layer.update()
obj=bpy.data.objects['USB_C_CAVITY']
tree=BVHTree.FromObject(obj,bpy.context.evaluated_depsgraph_get())
def hit(x,y):
 ori=obj.matrix_world.inverted()@Vector((x*.001,y*.001,-.090))
 vec=obj.matrix_world.inverted().to_3x3()@Vector((0,0,1))
 pos,_,_,_=tree.ray_cast(ori,vec.normalized(),.05)
 return None if pos is None else (obj.matrix_world@pos).z*1000
for x,y in ((4.0,1.10),(-4.0,1.10),(4.0,-1.10),(-4.0,-1.10)):
 assert hit(x,y) is None, f'USB-C cavity wrong sharp corner at {(x,y)} z={hit(x,y)}'
for x,y in ((3.5,.75),(-3.5,.75),(0,0)):
 assert hit(x,y) is not None, f'USB-C cavity missing inside rounded pill at {(x,y)}'
print('IPHONE_USB_CAVITY_ROUNDED_GREEN')
