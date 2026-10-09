"""iPhone 17 v30 native screen/panel topology contract for ticket #139."""
import math

import bmesh
import bpy


def mesh_report(name):
    obj = bpy.data.objects[name]
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    report = {
        "verts": len(bm.verts),
        "faces": len(bm.faces),
        "ngons": sum(1 for face in bm.faces if len(face.verts) > 4),
        "nonmanifold": sum(1 for edge in bm.edges if not edge.is_manifold),
        "modifiers": [(modifier.name, modifier.type) for modifier in obj.modifiers],
        "materials": [material.name if material else None for material in obj.data.materials],
        "uv_layers": [layer.name for layer in obj.data.uv_layers],
        "dimensions": tuple(obj.dimensions),
        "location": tuple(obj.location),
    }
    bm.free()
    return report


screen_glass = mesh_report("SCREEN_GLASS")
back_glass = mesh_report("BACK_GLASS")
screen_content = mesh_report("SCREEN_CONTENT")
logo = mesh_report("APPLE_LOGO_DECAL")

# The native cover-glass ring is production geometry, not a boolean/modifier
# staging object. Its saved mesh must be explicit and self-contained.
assert screen_glass["ngons"] == 0, screen_glass
assert screen_glass["nonmanifold"] == 0, screen_glass
assert screen_glass["modifiers"] == [], screen_glass
assert screen_glass["materials"] == ["MAT_DISPLAY_GLASS"], screen_glass
assert screen_glass["uv_layers"] == [], screen_glass
assert screen_glass["dimensions"] == (
    0.0694499984383583,
    0.0003499999875202775,
    0.14760999381542206,
), screen_glass
assert screen_glass["location"] == (0.0, -0.003800000064074993, 0.0), screen_glass

# Already-clean panel assets are regression guards. Do not "repair" them while
# changing native cover glass.
assert back_glass["ngons"] == 0 and back_glass["nonmanifold"] == 0, back_glass
assert back_glass["modifiers"] == [], back_glass
assert back_glass["materials"] == ["MAT_BACK_GLASS"], back_glass
assert back_glass["uv_layers"] == ["UVMap"], back_glass

assert screen_content["ngons"] == 0 and screen_content["nonmanifold"] == 0, screen_content
assert screen_content["modifiers"] == [], screen_content
assert screen_content["materials"] == ["MAT_SCREEN_CONTENT", "MAT_SCREEN_EDGE"], screen_content
assert screen_content["uv_layers"] == ["UVMap"], screen_content

# The Apple logo is intentionally an open decal plane. Preserve that contract,
# including its single UV-mapped quad, instead of demanding a closed shell.
assert logo["verts"] == 4 and logo["faces"] == 1 and logo["ngons"] == 0, logo
assert logo["modifiers"] == [], logo
assert logo["materials"] == ["MAT_APPLE_LOGO_DECAL"], logo
assert logo["uv_layers"] == ["UVMap"], logo

# Preserve the accepted screen-state and physical layer stack.
content_obj = bpy.data.objects["SCREEN_CONTENT"]
assert content_obj["screen_state"] == "screen_on"
assert math.isclose(content_obj["screen_on_emission"], 0.85, abs_tol=1e-9)
assert math.isclose(content_obj["screen_off_emission"], 0.0, abs_tol=1e-9)

glass = bpy.data.objects["SCREEN_GLASS"]
bezel = bpy.data.objects["DISPLAY_BEZEL"]
glass_to_content = content_obj.location.y - glass.location.y
content_to_bezel = bezel.location.y - content_obj.location.y
assert glass_to_content > 1e-6 and content_to_bezel > 1e-6, {
    "glass_y": glass.location.y,
    "content_y": content_obj.location.y,
    "bezel_y": bezel.location.y,
    "glass_to_content": glass_to_content,
    "content_to_bezel": content_to_bezel,
}

print(
    "IPHONE_PANEL_STACK_TOPOLOGY_GREEN",
    {
        "SCREEN_GLASS": screen_glass,
        "BACK_GLASS": back_glass,
        "SCREEN_CONTENT": screen_content,
        "APPLE_LOGO_DECAL": logo,
    },
)
