"""USB-C bottom visibility guard on assembled native and exported geometry.

The body recess must not cover the USB Cavity face when seen from the exterior.
Use independent geometric raycasts, not the presence/dimensions of named nodes.
"""
import bpy,sys,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
argv=sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
if argv:
    source=Path(argv[0])
    if source.suffix.lower()==".glb":
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.gltf(filepath=str(source))
    else:
        bpy.ops.wm.open_mainfile(filepath=str(source))
bpy.context.view_layer.update()
dg=bpy.context.evaluated_depsgraph_get()
body=bpy.data.objects["BODY_ALUMINUM"]
cavity=bpy.data.objects["USB_C_CAVITY"]
tongue=bpy.data.objects["USB_C_TONGUE"]
def hit(o,xmm,ymm):
    src=o.matrix_world.inverted()@Vector((xmm/1000,ymm/1000,-.090))
    vec=o.matrix_world.inverted().to_3x3()@Vector((0,0,1))
    loc,n,idx,dist=BVHTree.FromObject(o,dg).ray_cast(src,vec.normalized(),.05)
    return None if loc is None else round((o.matrix_world@loc).z*1000,5)
report=[]
for x,y in ((-3,0),(0,0),(3,0),(0,-.8),(0,.8)):
    bz=hit(body,x,y)
    cz=hit(cavity,x,y)
    assert bz is not None,(x,y,bz,cz)
    # Independent Apple bottom design datum: the finished cavity face is z=-73.465 mm.
    # Allow >=0.1 mm clear depth behind it, including historical fixture variants.
    clearance=bz-(-73.465)
    report.append(dict(x=x,y=y,bodyZ=bz,cavityZ=cz,clearance=round(clearance,5)))
    assert clearance > 0.10, f"BODY_ALUMINUM occludes USB_C_CAVITY at x={x} y={y}: {report}"
    if cz is not None: assert abs(cz - (-73.465)) < 0.01, report
assert hit(tongue,0,0) is not None,"USB tongue missing"
print("IPHONE_USB_CAVITY_VISIBLE_GREEN",json.dumps(report))
