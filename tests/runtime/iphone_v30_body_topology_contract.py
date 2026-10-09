"""Canonical low-poly BODY_ALUMINUM topology contract."""
import bmesh
import bpy

obj=bpy.data.objects["BODY_ALUMINUM"]
bm=bmesh.new();bm.from_mesh(obj.data)
obj.data.calc_loop_triangles()
report={
    "verts":len(bm.verts),
    "faces":len(bm.faces),
    "tris":len(obj.data.loop_triangles),
    "ngons":sum(len(face.verts)>4 for face in bm.faces),
    "nonmanifold":sum(not edge.is_manifold for edge in bm.edges),
    "zero_edges":sum((edge.verts[0].co-edge.verts[1].co).length<1e-10 for edge in bm.edges),
    "tiny_faces":sum(face.calc_area()<1e-14 for face in bm.faces),
    "uv_layers":len(obj.data.uv_layers),
    "modifiers":[modifier.type for modifier in obj.modifiers],
}
bm.free()
assert report["ngons"]==0,report
assert report["nonmanifold"]==0,report
assert report["zero_edges"]==0,report
assert report["tiny_faces"]==0,report
assert report["tris"]<7308,report
assert report["uv_layers"]>=1,report
assert "BEVEL" not in report["modifiers"],report
assert "WEIGHTED_NORMAL" not in report["modifiers"],report
print("IPHONE_BODY_TOPOLOGY_GREEN",report)
