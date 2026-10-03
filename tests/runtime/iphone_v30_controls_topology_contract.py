"""Side-control authored topology contract. Run in Blender on generated v30."""
import json, sys
import bmesh, bpy

CONTROLS=("ACTION_BUTTON","VOL_UP","VOL_DOWN","SIDE_BUTTON","CAMERA_CONTROL")
report={}
for name in CONTROLS:
    obj=bpy.data.objects[name]
    bm=bmesh.new(); bm.from_mesh(obj.data)
    report[name]={
        "verts":len(bm.verts),
        "faces":len(bm.faces),
        "ngons":sum(len(f.verts)>4 for f in bm.faces),
        "nonmanifold_edges":sum(not e.is_manifold for e in bm.edges),
    }
    bm.free()
    assert report[name]["ngons"] == 0, report
    assert report[name]["nonmanifold_edges"] == 0, report
print("IPHONE_CONTROLS_TOPOLOGY_GREEN", json.dumps(report, sort_keys=True))

