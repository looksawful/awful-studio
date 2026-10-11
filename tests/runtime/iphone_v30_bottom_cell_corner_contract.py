"""The visible lower-cell outer loops must meet at exact rectangular boundary corners."""
import bpy,sys
from pathlib import Path
if "--" in sys.argv:
    source=Path(sys.argv[sys.argv.index("--")+1])
    if source.suffix.lower()==".glb":
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.gltf(filepath=str(source))
    else:
        bpy.ops.wm.open_mainfile(filepath=str(source))
body=bpy.data.objects['BODY_ALUMINUM']
verts=[body.matrix_world@vertex.co for vertex in body.data.vertices]
flat_bounds=(-15.0,-12.6325,-9.215,-5.2,5.2,9.215,12.6325,15.0)
missing=[]
for x in flat_bounds:
 for y in (-3.625,3.625):
  if not any(abs(v.x*1000-x)<0.003 and abs(v.y*1000-y)<0.003 and abs(v.z*1000+74.805)<0.003 for v in verts):
   missing.append((x,y))
assert not missing, f"Bottom cell shared outer corners absent: {missing}"
print("IPHONE_BOTTOM_CELL_CORNER_GREEN",len(flat_bounds)*2)
