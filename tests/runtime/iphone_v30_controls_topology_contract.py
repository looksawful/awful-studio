"""Side-control low-poly+bake contract for iPhone 17 v30."""
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
        "uv_layers":len(obj.data.uv_layers),
        "modifiers":[mod.type for mod in obj.modifiers],
    }
    bm.free()
    assert report[name]["ngons"]==0,report
    assert report[name]["nonmanifold"]==0,report
    assert report[name]["verts"]<=44,report
    assert report[name]["uv_layers"]>=1,report
    assert "BEVEL" not in report[name]["modifiers"],report
    assert obj.data.materials,report
    bsdf=obj.data.materials[0].node_tree.nodes.get("Principled BSDF")
    assert bsdf.inputs["Normal"].is_linked,report
print("IPHONE_CONTROLS_BAKE_GREEN",json.dumps(report,sort_keys=True))
