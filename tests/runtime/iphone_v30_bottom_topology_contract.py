"""Bottom I/O authored topology contract. Run in Blender on generated v30."""
import json
import bmesh
import bpy

BOTTOM = (
    "USB_C_CAVITY", "USB_C_TONGUE",
    "BOTTOM_MIC_APERTURE_01", "BOTTOM_MIC_APERTURE_02", "BOTTOM_MIC_APERTURE_03",
    "BOTTOM_SPEAKER_APERTURE_01", "BOTTOM_SPEAKER_APERTURE_02",
    "BOTTOM_SPEAKER_APERTURE_03", "BOTTOM_SPEAKER_APERTURE_04",
    "BOTTOM_SPEAKER_APERTURE_05", "BOTTOM_SCREW_L", "BOTTOM_SCREW_R",
)
report = {}
for name in BOTTOM:
    obj = bpy.data.objects[name]
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    report[name] = {
        "verts": len(bm.verts),
        "faces": len(bm.faces),
        "ngons": sum(len(face.verts) > 4 for face in bm.faces),
        "nonmanifold_edges": sum(not edge.is_manifold for edge in bm.edges),
    }
    bm.free()
    assert report[name]["ngons"] == 0, report
    assert report[name]["nonmanifold_edges"] == 0, report
print("IPHONE_BOTTOM_TOPOLOGY_GREEN", json.dumps(report, sort_keys=True))
