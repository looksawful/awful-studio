"""Physical P2 recess contract: each fastener has an inset five-lobed slot.

This test checks the depth of the actual screw head, not a painted glyph.
"""
import bpy,sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
if "--" in sys.argv:
    src=Path(sys.argv[sys.argv.index("--")+1])
    bpy.ops.wm.read_factory_settings(use_empty=True)
    if src.suffix.lower()==".glb":bpy.ops.import_scene.gltf(filepath=str(src))
    else:bpy.ops.wm.open_mainfile(filepath=str(src))
dg=bpy.context.evaluated_depsgraph_get()
report={}
def zhit(o,x,y):
    origin=o.matrix_world.inverted() @ Vector((x,y,-.090))
    direction=o.matrix_world.inverted().to_3x3() @ Vector((0,0,1))
    p,n,f,d=BVHTree.FromObject(o,dg).ray_cast(origin,direction.normalized(),.05)
    assert p is not None, "Screw head missing at test position"
    return (o.matrix_world @ p).z*1000
for side,x in (("L",-6.925),("R",6.925)):
    screw=bpy.data.objects["BOTTOM_SCREW_"+side]
    middle=zhit(screw,x*.001,0)
    rim=zhit(screw,(x+.60)*.001,0)
    inset=middle-rim
    report[side]={"middle_mm":round(middle,5),"rim_mm":round(rim,5),"recess_depth_mm":round(inset,5)}
    assert inset>=.045, f"Flat P2 head / no physical recess: {report}"
    names=[mat.name for mat in screw.data.materials]
    assert "MAT_FASTENER" in names and "MAT_APERTURE_GRILLE" in names, (
        f"Pentalobe slot needs a distinct dark interior material: {side} {names}"
    )
    dark_index=names.index("MAT_APERTURE_GRILLE")
    assert any(face.material_index == dark_index for face in screw.data.polygons), (
        f"Pentalobe slot dark material is not assigned to any faces: {side}"
    )
print("IPHONE_BOTTOM_P2_ENGRAVING_GREEN",report)
