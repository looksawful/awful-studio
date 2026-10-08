"""Back-glass and front-hardware source topology contract for iPhone 17 v30."""
import json
import bmesh
import bpy

limits={
    # #147 replaces the sparse strip cap with a local CDT fill. Keep a hard budget
    # so quality cannot regress into unbounded tessellation.
    "BACK_GLASS":800,
    "FRONT_SENSOR_MASK":56,
    # Visible circular caps keep the same perimeter and add one bounded support ring.
    "FRONT_CAMERA_MASK":66,
    "FRONT_CAMERA_GLASS":62,
    "FRONT_CAMERA_INNER":50,
    "FRONT_CAMERA_IRIS":38,
    "FRONT_CAMERA_PUPIL":26,
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
