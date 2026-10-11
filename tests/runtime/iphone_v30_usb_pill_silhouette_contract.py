"""Native/exported assembled-body USB-C silhouette should be a rounded pill, never a hexagon.

Measure visibility from exterior directly against the actual BODY_ALUMINUM mesh.
The selected near-corner sample is inside the standard rounded USB opening
but outside the 8-ray straight hexagonal shortcut.
"""
import bpy,sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
arg=sys.argv[sys.argv.index("--")+1] if "--" in sys.argv else None
if arg:
 src=Path(arg)
 bpy.ops.wm.read_factory_settings(use_empty=True)
 if src.suffix.lower()=='.glb':bpy.ops.import_scene.gltf(filepath=str(src))
 else:bpy.ops.wm.open_mainfile(filepath=str(src))
bpy.context.view_layer.update()
o=bpy.data.objects['BODY_ALUMINUM'];dg=bpy.context.evaluated_depsgraph_get()
t=BVHTree.FromObject(o,dg)
def first_z(xmm,ymm):
 origin=o.matrix_world.inverted()@Vector((xmm*.001,ymm*.001,-.090))
 direction=o.matrix_world.inverted().to_3x3()@Vector((0,0,1))
 pos,normal,face,dist=t.ray_cast(origin,direction.normalized(),.05)
 return None if pos is None else (o.matrix_world@pos).z*1000
# right/left near-corner belongs to pill opening of 8.99 x 3.00 mm r0.91.
# Exterior aluminum face is z=-74.805; genuine open sample sees deeper inner shell.
samples=[]
for x,y in [(4.40,.75),(4.40,-.75),(-4.40,.75),(-4.40,-.75)]:
 z=first_z(x,y)
 samples.append((x,y,z))
 assert z is None or z > -74.0, f'USB corner opening masked by polygonal metal shortcut: {samples}'
for x,y in [(4.45,1.20),(-4.45,1.20),(4.45,-1.20),(-4.45,-1.20)]:
 z=first_z(x,y)
 assert z is not None and z < -74.7, f'USB rounded corner exterior material missing: x={x} y={y} z={z}'
print('IPHONE_USB_PILL_SILHOUETTE_GREEN',samples)
