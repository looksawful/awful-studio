"""SCREEN_CONTENT topology contract."""
import bmesh
import bpy

screen = bpy.data.objects["SCREEN_CONTENT"]
bm = bmesh.new()
bm.from_mesh(screen.data)
ngons = [face for face in bm.faces if len(face.verts) > 4]
nonmanifold = [edge for edge in bm.edges if not edge.is_manifold]
xs = [v.co.x for v in bm.verts]
ys = [v.co.y for v in bm.verts]
zs = [v.co.z for v in bm.verts]
assert not ngons, f"SCREEN_CONTENT has {len(ngons)} n-gons"
assert not nonmanifold, f"SCREEN_CONTENT has {len(nonmanifold)} nonmanifold edges"
assert len(screen.data.materials) == 2, "screen material seam changed"
assert bpy.data.objects.get("FRONT_SENSOR_MASK") is not None
assert bpy.data.objects.get("FRONT_CAMERA_MASK") is not None
assert max(xs) - min(xs) > 0.066
assert max(zs) - min(zs) > 0.144
assert max(ys) - min(ys) > 0
print("SCREEN_CONTENT_TOPOLOGY_GREEN", {"verts": len(bm.verts), "faces": len(bm.faces)})
bm.free()
