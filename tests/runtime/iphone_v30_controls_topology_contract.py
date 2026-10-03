"""Side-control source topology contract for iPhone 17 v30."""
import json
import bmesh
import bpy

names=("ACTION_BUTTON","VOL_UP","VOL_DOWN","SIDE_BUTTON","CAMERA_CONTROL")
report={}
for name in names:
    obj=bpy.data.objects[name]
    bm=bmesh.new(); bm.from_mesh(obj.data)
    report[name]={
        "verts":len(bm.verts),
        "faces":len(bm.faces),
        "ngons":sum(len(f.verts)>4 for f in bm.faces),
        "nonmanifold":sum(not e.is_manifold for e in bm.edges),
    }
    bm.free()
    assert report[name]["ngons"]==0,report
    assert report[name]["nonmanifold"]==0,report
    assert report[name]["verts"]<=44,report
print("IPHONE_CONTROLS_TOPOLOGY_GREEN",json.dumps(report,sort_keys=True))
