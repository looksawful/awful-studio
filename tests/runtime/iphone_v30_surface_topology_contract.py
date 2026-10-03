"""Back/front authored topology contract for iPhone 17 v30."""
import json
import bmesh
import bpy

SURFACES=(
    "BACK_GLASS",
    "SCREEN_CONTENT",
    "FRONT_SENSOR_MASK",
    "FRONT_CAMERA_MASK",
    "FRONT_CAMERA_GLASS",
)
report={}
for name in SURFACES:
    obj=bpy.data.objects[name]
    bm=bmesh.new(); bm.from_mesh(obj.data)
    report[name]={
        "verts":len(bm.verts),
        "faces":len(bm.faces),
        "ngons":sum(len(face.verts)>4 for face in bm.faces),
        "nonmanifold_edges":sum(not edge.is_manifold for edge in bm.edges),
    }
    bm.free()
    assert report[name]["ngons"] == 0, report
    assert report[name]["nonmanifold_edges"] == 0, report
print("IPHONE_SURFACE_TOPOLOGY_GREEN",json.dumps(report,sort_keys=True))

