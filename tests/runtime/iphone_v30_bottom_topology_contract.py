"""Bottom hardware source topology contract for iPhone 17 v30."""
import json
import bmesh
import bpy

apertures=tuple(f"BOTTOM_MIC_APERTURE_{i:02d}" for i in range(1,4))+tuple(f"BOTTOM_SPEAKER_APERTURE_{i:02d}" for i in range(1,6))
screws=("BOTTOM_SCREW_L","BOTTOM_SCREW_R")
report={}
for name in apertures+screws:
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
    limit=34 if name in apertures else 42
    assert report[name]["verts"]<=limit,report
print("IPHONE_BOTTOM_TOPOLOGY_GREEN",json.dumps(report,sort_keys=True))
