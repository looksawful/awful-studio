"""The eight physical iPhone 17 vents must have fine circular outer contours.

Checks native Blender delivery as well as actual exported glTF geometry.
Counts distinct boundary angular stations; a former 8-gon must fail.
"""
import bpy, math, sys
from pathlib import Path
from mathutils import Vector
if "--" in sys.argv:
    src=Path(sys.argv[sys.argv.index("--")+1])
    bpy.ops.wm.read_factory_settings(use_empty=True)
    if src.suffix.lower()==".glb":bpy.ops.import_scene.gltf(filepath=str(src))
    else:bpy.ops.wm.open_mainfile(filepath=str(src))
obj=bpy.data.objects["BODY_ALUMINUM"]
verts=[obj.matrix_world @ v.co for v in obj.data.vertices]
spec=[(19.71,.675),(21.965,.675),(24.22,.675),
      (47.23,.675),(49.485,.675),(51.74,.675),
      (53.995,.675),(56.25,.675)]
result=[]
for from_left,radius in spec:
    x=(from_left-71.45/2)
    stations=set()
    for v in verts:
        dx=v.x*1000-x
        dy=v.y*1000
        distance=math.hypot(dx,dy)
        if abs(distance-radius)<.013 and v.z*1000 < -73.8:
            stations.add(round((math.atan2(dy,dx)%(2*math.pi)),5))
    angles=sorted(stations)
    if not angles:raise AssertionError(f"vent at x={x} has no edge ring")
    max_gap=max((angles[(i+1)%len(angles)] + (2*math.pi if i+1==len(angles) else 0))-a
                for i,a in enumerate(angles))
    result.append((round(x,4),len(angles),round(math.degrees(max_gap),3)))
    assert len(angles)>=20 and math.degrees(max_gap)<=19, f"Faceted vent edge: {result}"
print("IPHONE_BOTTOM_VENT_ROUNDNESS_GREEN",result)
