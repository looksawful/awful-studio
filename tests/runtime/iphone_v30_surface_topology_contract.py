"""Back-glass and front-hardware source topology contract for iPhone 17 v30."""
import json
import bmesh
import bpy

limits={
    "BACK_GLASS":136,
    "FRONT_SENSOR_MASK":56,
    "FRONT_CAMERA_MASK":50,
    "FRONT_CAMERA_GLASS":46,
    "FRONT_CAMERA_INNER":34,
    "FRONT_CAMERA_IRIS":26,
    "FRONT_CAMERA_PUPIL":18,
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
print("IPHONE_SURFACE_TOPOLOGY_GREEN",json.dumps(report,sort_keys=True))
