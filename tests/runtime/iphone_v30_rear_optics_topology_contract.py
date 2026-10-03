"""Residual rear optics source topology contract for iPhone 17 v30."""
import json
import bmesh
import bpy

limits={
    "CAMERA_1_INNER":66,
    "CAMERA_2_INNER":66,
    "CAMERA_1_IRIS":50,
    "CAMERA_2_IRIS":50,
    "CAMERA_1_PUPIL":34,
    "CAMERA_2_PUPIL":34,
    "REAR_MIC":34,
    "FLASH_RING":66,
    "FLASH":66,
}
report={}
for name,limit in limits.items():
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
    assert report[name]["verts"]<=limit,report
print("IPHONE_REAR_OPTICS_TOPOLOGY_GREEN",json.dumps(report,sort_keys=True))
