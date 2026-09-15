import json
import os
import sys
import bmesh
import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
COMMON = os.path.normpath(os.path.join(HERE, "..", "common"))
if COMMON not in sys.path:
    sys.path.insert(0, COMMON)
import foundation_common as fc

MM = fc.MM
W, H, D = 71.5 * MM, 149.6 * MM, 7.95 * MM
BODY_R = 13.6 * MM
METAL_D = 7.25 * MM
GLASS_T = 0.35 * MM
COVER_W, COVER_H, COVER_R = 69.45 * MM, 147.61 * MM, 12.0 * MM
SCREEN_W, SCREEN_H, SCREEN_R = 66.57 * MM, 144.79 * MM, 10.55 * MM

def cli(flag, default):
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    return argv[argv.index(flag) + 1] if flag in argv else default

OUT = os.path.abspath(cli("--out", os.path.join(HERE, "generated", "iphone_17_low_v21.blend")))
EVIDENCE = os.path.abspath(cli("--evidence", os.path.join(HERE, "evidence", "low_v21_validation.json")))
PREVIEWS = os.path.abspath(cli("--previews", os.path.join(HERE, "previews", "low_v21")))
fc.clear_scene()
fc.setup_scene()
scene = bpy.context.scene
scene.render.resolution_x = 1600
scene.render.resolution_y = 1600
scene.render.resolution_percentage = 100
scene.render.film_transparent = False
scene.view_settings.exposure = -1.35
scene.world.use_nodes = True
bg = scene.world.node_tree.nodes.get('Background')
bg.inputs['Color'].default_value = (0.001, 0.001, 0.001, 1.0)
bg.inputs['Strength'].default_value = 0.025
body_c = fc.make_collection("IPHONE_17_LOW_BODY")
detail_c = fc.make_collection("IPHONE_17_LOW_DETAILS")
screen_c = fc.make_collection("IPHONE_17_LOW_SCREEN")
ctrl_c = fc.make_collection("IPHONE_17_CONTROLLERS")

metal = fc.make_material("MAT_ANODIZED_ALUMINUM", (0.006, 0.007, 0.010), 1.0, 0.31)
metal_dark = fc.make_material("MAT_ALUMINUM_EDGE", (0.012, 0.014, 0.020), 1.0, 0.24)
camera_housing_mat = fc.make_material("MAT_CAMERA_HOUSING", (0.010, 0.013, 0.020), 1.0, 0.27)
back_mat = fc.make_material("MAT_BACK_GLASS", (0.00008, 0.00010, 0.00014), 0.0, 0.38)
back_bsdf = back_mat.node_tree.nodes.get("Principled BSDF")
back_bsdf.inputs["Coat Weight"].default_value = 0.22
back_bsdf.inputs["Coat Roughness"].default_value = 0.09
if back_bsdf.inputs.get("Specular IOR Level"):
    back_bsdf.inputs["Specular IOR Level"].default_value = 0.18
black = fc.make_material("MAT_OPTICS_BLACK", (0.0008, 0.0010, 0.0014), 0.0, 0.07)
island_mat = fc.make_material("MAT_DYNAMIC_ISLAND", (0.00001, 0.000012, 0.000016), 0.0, 0.11)
island_bsdf = island_mat.node_tree.nodes.get("Principled BSDF")
island_bsdf.inputs["Coat Weight"].default_value = 0.42
island_bsdf.inputs["Coat Roughness"].default_value = 0.025
front_optic = fc.make_material("MAT_FRONT_OPTIC", (0.055, 0.072, 0.105), 0.0, 0.075)
front_bsdf = front_optic.node_tree.nodes.get("Principled BSDF")
front_bsdf.inputs["Coat Weight"].default_value = 0.58
front_bsdf.inputs["Coat Roughness"].default_value = 0.012
sensor_pill_mat = fc.make_material("MAT_FRONT_SENSOR_PILL", (0.00005, 0.00006, 0.00009), 0.0, 0.19)
sensor_pill_bsdf = sensor_pill_mat.node_tree.nodes.get("Principled BSDF")
sensor_pill_bsdf.inputs["Coat Weight"].default_value = 0.20
sensor_pill_bsdf.inputs["Coat Roughness"].default_value = 0.075
lens_glass = fc.make_material("MAT_LENS_GLASS", (0.00012, 0.00016, 0.00024), 0.0, 0.020)
lbsdf = lens_glass.node_tree.nodes.get("Principled BSDF")
lbsdf.inputs["Coat Weight"].default_value = 0.62
lbsdf.inputs["Coat Roughness"].default_value = 0.008
gap_mat = fc.make_material("MAT_ASSEMBLY_GAP", (0.0005, 0.0006, 0.0008), 0.0, 0.32)
bezel_mat = fc.make_material("MAT_DISPLAY_BEZEL", (0.001, 0.0012, 0.0015), 0.0, 0.10)
screen_mat = fc.make_material("MAT_SCREEN_CONTENT", (0.0038, 0.0052, 0.0078), 0.0, 0.085)
optic_glass = fc.make_material("MAT_OPTICAL_GLASS", (0.0010, 0.0014, 0.0024), 0.0, 0.030)
flash_mat = fc.make_material("MAT_FLASH", (0.86, 0.80, 0.62), 0.0, 0.14)
screw_mat = fc.make_material("MAT_FASTENER", (0.10, 0.11, 0.13), 0.92, 0.24)

glass = fc.make_material("MAT_DISPLAY_GLASS", (0.0015, 0.0020, 0.0030), 0.0, 0.045)
gbsdf = glass.node_tree.nodes.get("Principled BSDF")
gbsdf.inputs["IOR"].default_value = 1.46
gbsdf.inputs["Transmission Weight"].default_value = 0.0
gbsdf.inputs["Coat Weight"].default_value = 0.18
gbsdf.inputs["Coat Roughness"].default_value = 0.028


body = fc.rounded_prism("BODY_ALUMINUM", W, H, METAL_D, BODY_R, metal, body_c, axis="Y", outline_segments=48)
front_y = -(D * 0.5 - GLASS_T * 0.5)
front_surface = -D * 0.5
back_y = D * 0.5 - GLASS_T * 0.5

# Official Apple drawing: cover glass 69.45 x 147.61 mm, active area 66.57 x 144.79 mm.
pocket = fc.rounded_prism("DISPLAY_POCKET_CUTTER", COVER_W + 0.12*MM, COVER_H + 0.12*MM, 0.72*MM,
                          COVER_R + 0.06*MM, None, detail_c, axis="Y",
                          location=(0, -METAL_D*0.5 + 0.16*MM, 0), outline_segments=48)
fc.boolean_difference(body, pocket, name="CUT_DISPLAY_POCKET")

back_seat = fc.rounded_prism("BACK_GLASS_SEAT", COVER_W + 0.12*MM, COVER_H + 0.12*MM, 0.07*MM,
                             COVER_R + 0.06*MM, gap_mat, body_c, axis="Y",
                             location=(0, METAL_D*0.5 + 0.012*MM, 0), outline_segments=48)
back_seat.hide_render = True
back_glass = fc.rounded_prism("BACK_GLASS", COVER_W, COVER_H, GLASS_T, COVER_R,
                              back_mat, body_c, axis="Y", location=(0, back_y, 0),
                              edge_bevel=0.0, outline_segments=48)

front_seat = fc.rounded_prism("DISPLAY_GLASS_SEAT", COVER_W + 0.10*MM, COVER_H + 0.10*MM, 0.07*MM,
                              COVER_R + 0.05*MM, gap_mat, screen_c, axis="Y",
                              location=(0, -METAL_D*0.5 - 0.010*MM, 0), outline_segments=48)
bezel = fc.rounded_prism("DISPLAY_BEZEL", SCREEN_W + 0.68*MM, SCREEN_H + 0.68*MM, 0.08*MM,
                         SCREEN_R + 0.32*MM, bezel_mat, screen_c, axis="Y",
                         location=(0, front_y + 0.08*MM, 0), outline_segments=48)

screen_glass = fc.rounded_prism("SCREEN_GLASS", COVER_W, COVER_H, GLASS_T, COVER_R,
                                glass, screen_c, axis="Y", location=(0, front_y, 0),
                                edge_bevel=0.00006, outline_segments=48)
active_cut = fc.rounded_prism("SCREEN_ACTIVE_CUTTER", SCREEN_W + 0.12*MM, SCREEN_H + 0.12*MM,
                              GLASS_T + 0.25*MM, SCREEN_R + 0.06*MM, None, detail_c, axis="Y",
                              location=(0, front_y, 0), outline_segments=48)
fc.boolean_difference(screen_glass, active_cut, name="CUT_ACTIVE_AREA")

screen_content = fc.rounded_prism("SCREEN_CONTENT", SCREEN_W, SCREEN_H, GLASS_T - 0.025*MM,
                                  SCREEN_R, screen_mat, screen_c, axis="Y",
                                  location=(0, front_y + 0.010*MM, 0), edge_bevel=0.00004,
                                  outline_segments=48)

def hard_surface_glass(obj):
    bevel = obj.modifiers.get("EDGE_BEVEL")
    if bevel:
        bevel.harden_normals = True
    for poly in obj.data.polygons[2:]:
        poly.use_smooth = True
    weighted = obj.modifiers.new("WEIGHTED_NORMAL", "WEIGHTED_NORMAL")
    weighted.keep_sharp = True
    weighted.weight = 50

for poly in back_glass.data.polygons:
    poly.use_smooth = False
hard_surface_glass(screen_glass)
# Screen material doubles as the clean glossy active glass surface for the current publishable LOW asset.
sbsdf = screen_mat.node_tree.nodes.get("Principled BSDF")
sbsdf.inputs["Coat Weight"].default_value = 0.16
sbsdf.inputs["Coat Roughness"].default_value = 0.035

# Front camera / TrueDepth assembly from Apple dimensional drawing.
island_z = H*0.5 - 10.35*MM
island_y = front_surface - 0.012*MM
detail_y = front_surface - 0.024*MM
island = fc.rounded_prism("DYNAMIC_ISLAND", 20.75*MM, 5.12*MM, 0.012*MM, 2.55*MM, island_mat, detail_c, axis="Y", location=(0, island_y, island_z), outline_segments=96)
fc.rounded_prism("FRONT_SENSOR_PILL", 7.10*MM, 2.30*MM, 0.016*MM, 1.15*MM, sensor_pill_mat, detail_c, axis="Y", location=(-4.15*MM, detail_y, island_z), outline_segments=64)
cam_x = 5.05*MM
fc.cylinder("FRONT_CAMERA_RING", 1.15*MM, 0.014*MM, metal_dark, detail_c, (cam_x, detail_y, island_z), axis="Y", vertices=128)
fc.cylinder("FRONT_CAMERA_GLASS", 0.84*MM, 0.012*MM, front_optic, detail_c, (cam_x, detail_y - 0.004*MM, island_z), axis="Y", vertices=128)
fc.cylinder("FRONT_CAMERA_INNER", 0.52*MM, 0.010*MM, black, detail_c, (cam_x, detail_y - 0.010*MM, island_z), axis="Y", vertices=96)
fc.cylinder("FRONT_CAMERA_IRIS", 0.28*MM, 0.008*MM, front_optic, detail_c, (cam_x, detail_y - 0.016*MM, island_z), axis="Y", vertices=80)
fc.cylinder("FRONT_CAMERA_PUPIL", 0.12*MM, 0.006*MM, black, detail_c, (cam_x, detail_y - 0.021*MM, island_z), axis="Y", vertices=64)
receiver = fc.rounded_cube("FRONT_RECEIVER_MIC", (14.02*MM, 0.020*MM, 0.30*MM), 0.14*MM, black, detail_c, location=(0, front_surface - 0.012*MM, H*0.5 - 0.62*MM))

housing_x = 20.55*MM
housing_z = 52.32*MM
housing_seat = fc.rounded_prism("CAMERA_HOUSING_SEAT", 20.74*MM, 43.82*MM, 0.10*MM, 10.27*MM, gap_mat, detail_c, axis="Y", location=(housing_x, D*0.5 + 0.08*MM, housing_z), outline_segments=96)
housing_seat.hide_render = True
housing = fc.rounded_prism("CAMERA_HOUSING", 20.54*MM, 43.62*MM, 0.94*MM, 10.27*MM, camera_housing_mat, detail_c, axis="Y", location=(housing_x, D*0.5 + 0.54*MM, housing_z), edge_bevel=0.00018, outline_segments=96)
for idx,(x_mm,z_mm) in enumerate(((22.13,61.18),(22.13,43.46)),1):
    seat=fc.cylinder(f"CAMERA_{idx}_SEAT",8.18*MM,0.14*MM,gap_mat,detail_c,(x_mm*MM,D*0.5+0.88*MM,z_mm*MM),axis="Y",vertices=192); seat.hide_render=True
    fc.cylinder(f"CAMERA_{idx}_RING",8.00*MM,0.36*MM,metal_dark,detail_c,(x_mm*MM,D*0.5+1.09*MM,z_mm*MM),axis="Y",vertices=192)
    fc.cylinder(f"CAMERA_{idx}_BEVEL",7.44*MM,0.18*MM,metal,detail_c,(x_mm*MM,D*0.5+1.36*MM,z_mm*MM),axis="Y",vertices=192)
    fc.cylinder(f"CAMERA_{idx}_GLASS",6.81*MM,0.16*MM,lens_glass,detail_c,(x_mm*MM,D*0.5+1.53*MM,z_mm*MM),axis="Y",vertices=192)
    fc.cylinder(f"CAMERA_{idx}_INNER",5.20*MM,0.09*MM,black,detail_c,(x_mm*MM,D*0.5+1.65*MM,z_mm*MM),axis="Y",vertices=160)
    fc.cylinder(f"CAMERA_{idx}_IRIS",3.00*MM,0.070*MM,lens_glass,detail_c,(x_mm*MM,D*0.5+1.73*MM,z_mm*MM),axis="Y",vertices=128)
    fc.cylinder(f"CAMERA_{idx}_PUPIL",1.18*MM,0.045*MM,black,detail_c,(x_mm*MM,D*0.5+1.79*MM,z_mm*MM),axis="Y",vertices=96)
fc.cylinder("REAR_MIC",0.50*MM,0.14*MM,black,detail_c,(13.05*MM,D*0.5+1.02*MM,52.30*MM),axis="Y",vertices=80)
fc.cylinder("FLASH_RING",3.30*MM,0.12*MM,metal_dark,detail_c,(5.00*MM,D*0.5+0.30*MM,52.30*MM),axis="Y",vertices=128)
fc.cylinder("FLASH",3.14*MM,0.14*MM,flash_mat,detail_c,(5.00*MM,D*0.5+0.43*MM,52.30*MM),axis="Y",vertices=128)

# Apple mark decal. Bounding box and vertical datum follow the Apple dimensional drawing.
logo_img_path = os.path.join(HERE, "reference", "apple_logo_glb_mask.png")
logo_mat = bpy.data.materials.new("MAT_APPLE_LOGO_DECAL")
logo_mat.use_nodes = True
nodes = logo_mat.node_tree.nodes
links = logo_mat.node_tree.links
for node in list(nodes):
    nodes.remove(node)
out = nodes.new("ShaderNodeOutputMaterial")
bsdf = nodes.new("ShaderNodeBsdfPrincipled")
tex = nodes.new("ShaderNodeTexImage")
tex.image = bpy.data.images.load(logo_img_path, check_existing=True)
bsdf.inputs["Base Color"].default_value = (0.14, 0.15, 0.17, 1.0)
bsdf.inputs["Roughness"].default_value = 0.16
bsdf.inputs["Coat Weight"].default_value = 0.12
bsdf.inputs["Coat Roughness"].default_value = 0.045
bsdf.inputs["Metallic"].default_value = 0.86
links.new(tex.outputs["Alpha"], bsdf.inputs["Alpha"])
links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
try:
    logo_mat.surface_render_method = "DITHERED"
except Exception:
    pass
lw, lh = 15.75*MM, 19.34*MM
verts = [(-lw/2,0,-lh/2),(lw/2,0,-lh/2),(lw/2,0,lh/2),(-lw/2,0,lh/2)]
mesh = bpy.data.meshes.new("APPLE_LOGO_MESH")
mesh.from_pydata(verts, [], [(0,3,2,1)])
mesh.update()
logo = bpy.data.objects.new("APPLE_LOGO_DECAL", mesh)
detail_c.objects.link(logo)
logo.location = (0, D*0.5 + 0.006*MM, (H*0.5 - 73.18*MM))
logo.data.materials.append(logo_mat)
uv = mesh.uv_layers.new(name="UVMap")
for loop, coord in zip(mesh.loops, ((1,0),(1,1),(0,1),(0,0))):
    uv.data[loop.index].uv = coord

boolean_cuts = ["DISPLAY_POCKET", "SCREEN_ACTIVE"]

def side_control(name, edge, z_mm, length_mm, face_width_mm, protrusion_mm=0.18, material=metal):
    cutter = fc.rounded_cube(f"{name}_CUTTER", (1.10*MM, (face_width_mm+0.55)*MM, (length_mm+0.82)*MM),
                             0.30*MM, None, detail_c)
    fc.place_on_rounded_edge(cutter, W, H, BODY_R, edge, z_mm*MM, outward=-0.30*MM, local_normal=(1,0,0))
    fc.boolean_difference(body, cutter, name=f"CUT_{name}")
    boolean_cuts.append(name)
    seat = fc.rounded_cube(f"{name}_SEAT", (0.12*MM, (face_width_mm+0.24)*MM, (length_mm+0.30)*MM),
                           0.06*MM, gap_mat, detail_c)
    fc.place_on_rounded_edge(seat, W, H, BODY_R, edge, z_mm*MM, outward=-0.045*MM, local_normal=(1,0,0))
    seat.hide_render = True
    thickness = 0.12*MM if name != "CAMERA_CONTROL" else 0.06*MM
    button = fc.rounded_cube(name, (thickness, face_width_mm*MM, length_mm*MM),
                             min(0.42*MM, face_width_mm*0.40*MM), material, detail_c)
    center_out = max(-0.02, protrusion_mm - thickness/MM*0.5) * MM
    fc.place_on_rounded_edge(button, W, H, BODY_R, edge, z_mm*MM, outward=center_out, local_normal=(1,0,0))
    return button

# Center positions come from Apple's iPhone 17 dimensional drawing (top datum).
side_control("ACTION_BUTTON", "LEFT", 40.72, 11.6, 0.72, protrusion_mm=0.020)
side_control("VOL_UP", "LEFT", 26.57, 9.2, 0.72, protrusion_mm=0.020)
side_control("VOL_DOWN", "LEFT", 12.37, 9.2, 0.72, protrusion_mm=0.020)
side_control("SIDE_BUTTON", "RIGHT", 19.48, 17.7, 0.82, protrusion_mm=0.020)
side_control("CAMERA_CONTROL", "RIGHT", -23.40, 17.5, 0.95, protrusion_mm=0.002, material=metal_dark)

for side, edge in (("L", "LEFT"), ("R", "RIGHT")):
    for z_mm in (55.0, -55.0):
        strip = fc.rounded_cube(f"ANTENNA_SIDE_{side}_{int(z_mm)}", (0.10*MM, 1.02*MM, 4.3*MM),
                                0.06*MM, black, detail_c)
        fc.place_on_rounded_edge(strip, W, H, BODY_R, edge, z_mm*MM, outward=-0.018*MM, local_normal=(1,0,0))

for x_mm in (-31.0, 31.0):
    strip = fc.rounded_cube(f"ANTENNA_BOTTOM_{int(x_mm)}", (3.4*MM, 0.96*MM, 0.11*MM),
                            0.06*MM, black, detail_c)
    fc.place_on_rounded_edge(strip, W, H, BODY_R, "BOTTOM", x_mm*MM, outward=-0.018*MM, local_normal=(0,0,1))

usb_cutter = fc.rounded_cube("USB_C_CUTTER", (9.35*MM, 3.18*MM, 2.05*MM), 0.72*MM, None, detail_c)
fc.place_on_rounded_edge(usb_cutter, W, H, BODY_R, "BOTTOM", 0.0, outward=-0.70*MM, local_normal=(0,0,1))
fc.boolean_difference(body, usb_cutter, name="CUT_USB_C")
boolean_cuts.append("USB_C")
usb_cavity = fc.rounded_cube("USB_C_CAVITY", (8.65*MM, 2.62*MM, 0.72*MM), 0.48*MM, black, detail_c)
fc.place_on_rounded_edge(usb_cavity, W, H, BODY_R, "BOTTOM", 0.0, outward=-0.67*MM, local_normal=(0,0,1))
usb_tongue = fc.rounded_cube("USB_C_TONGUE", (5.25*MM, 0.48*MM, 0.18*MM), 0.08*MM, metal_dark, detail_c)
fc.place_on_rounded_edge(usb_tongue, W, H, BODY_R, "BOTTOM", 0.0, outward=-0.49*MM, local_normal=(0,0,1))

def bottom_aperture(name, x_mm):
    cutter = fc.cylinder(f"{name}_CUTTER", 0.675*MM, 1.80*MM, None, detail_c, vertices=40)
    fc.place_on_rounded_edge(cutter, W, H, BODY_R, "BOTTOM", x_mm*MM, outward=-0.52*MM, local_normal=(0,0,1))
    fc.boolean_difference(body, cutter, name=f"CUT_{name}")
    boolean_cuts.append(name)
    cavity = fc.cylinder(name, 0.56*MM, 0.50*MM, black, detail_c, vertices=40)
    fc.place_on_rounded_edge(cavity, W, H, BODY_R, "BOTTOM", x_mm*MM, outward=-0.45*MM, local_normal=(0,0,1))

# iPhone 17: 3 microphone ports on the left, 5 speaker ports on the right, 8 x 1.35 mm total.
for idx, x_mm in enumerate((-18.2, -15.1, -12.0), 1):
    bottom_aperture(f"BOTTOM_MIC_APERTURE_{idx:02d}", x_mm)
for idx, x_mm in enumerate((12.0, 15.1, 18.2, 21.3, 24.4), 1):
    bottom_aperture(f"BOTTOM_SPEAKER_APERTURE_{idx:02d}", x_mm)

for side, x_mm in (("L", -7.15), ("R", 7.15)):
    recess = fc.cylinder(f"BOTTOM_SCREW_{side}_RECESS", 0.75*MM, 0.90*MM, None, detail_c, vertices=48)
    fc.place_on_rounded_edge(recess, W, H, BODY_R, "BOTTOM", x_mm*MM, outward=-0.38*MM, local_normal=(0,0,1))
    fc.boolean_difference(body, recess, name=f"CUT_SCREW_{side}")
    boolean_cuts.append(f"SCREW_{side}")
    screw = fc.cylinder(f"BOTTOM_SCREW_{side}", 0.66*MM, 0.24*MM, screw_mat, detail_c, vertices=48)
    fc.place_on_rounded_edge(screw, W, H, BODY_R, "BOTTOM", x_mm*MM, outward=-0.15*MM, local_normal=(0,0,1))

bev = fc.add_bevel(body, 0.00034, segments=6)
bev.harden_normals = True
for poly in body.data.polygons[2:]:
    poly.use_smooth = True
body_wn = body.modifiers.new("WEIGHTED_NORMAL", "WEIGHTED_NORMAL")
body_wn.keep_sharp = True
body_wn.weight = 50
housing_bevel = housing.modifiers.get("EDGE_BEVEL")
if housing_bevel:
    housing_bevel.harden_normals = True
for poly in housing.data.polygons[2:]:
    poly.use_smooth = True
housing_wn = housing.modifiers.new("WEIGHTED_NORMAL", "WEIGHTED_NORMAL")
housing_wn.keep_sharp = True
housing_wn.weight = 50
root = fc.empty("CTRL_IPHONE_17", ctrl_c)
for collection in (body_c, detail_c, screen_c):
    for obj in collection.objects:
        obj.parent = root
root["asset_id"] = "iphone_17"
root["asset_version"] = "low_v21_0.7"
root["stage"] = "LOW_DRAFT"
root["dimensions_mm"] = "71.5 x 149.6 x 7.95"
root["screen_object"] = "SCREEN_CONTENT"
root["surface_aware_controls"] = True
root["surface_aware_bottom"] = True
root["real_display_pocket"] = True
root["front_camera_present"] = True
root["apple_logo_decal"] = True
root["rear_camera_outer_diameter_mm"] = 16.0
root["rear_camera_optical_diameter_mm"] = 13.62
root["publish_preview_material"] = "black_anodized"
root["source_drawing"] = "Apple iPhone 17 Dimensional Drawings 2025-09-09"
root["cover_glass_mm"] = "69.45 x 147.61"
root["display_active_area_mm"] = "66.57 x 144.79"
root["button_top_datums_mm"] = "34.08, 48.23, 62.43, 55.32, 98.20"
root["bottom_layout"] = "3_mic + usb_c + 5_speaker"
root["apple_logo_decal"] = "reference/apple_logo_glb_mask.png"

studio = fc.make_collection("_STUDIO_RIG")
fc.add_area_light("KEY_SOFTBOX", (0.30, -0.22, 0.25), 82, 0.38, studio, target=(0,0,0.020))
fc.add_area_light("FILL_SOFTBOX", (-0.24, -0.14, 0.02), 14, 0.32, studio, target=(0,0,0.0))
fc.add_area_light("RIM_STRIP", (0.22, 0.26, 0.13), 94, 0.14, studio, target=(0,0,0.015))
fc.add_area_light("TOP_STRIP", (-0.10, 0.03, 0.34), 42, 0.28, studio, target=(0,0,0.035))

camera_c = fc.make_collection("_DIAGNOSTIC_CAMERAS")
def persp(name, location, target, lens=78):
    data = bpy.data.cameras.new(name)
    data.type = "PERSP"
    data.lens = lens
    data.sensor_width = 36.0
    cam = bpy.data.objects.new(name, data)
    cam.location = location
    cam.rotation_euler = (fc.Vector(target) - fc.Vector(location)).to_track_quat("-Z", "Y").to_euler()
    camera_c.objects.link(cam)
    return cam

cam_front = persp("CAM_FRONT", (0, -0.42, 0), (0,0,0), 92)
cam_back = persp("CAM_BACK", (0, 0.42, 0), (0,0,0), 92)
cam_three = persp("CAM_THREE_QUARTER", (0.20, -0.30, 0.15), (0,0,0.010), 82)
cam_left = persp("CAM_LEFT_SIDE", (-0.22, -0.07, 0.020), (-W*0.48,0,0.020), 92)
cam_right = persp("CAM_RIGHT_SIDE", (0.22, -0.07, -0.004), (W*0.48,0,-0.004), 92)
cam_bottom = persp("CAM_BOTTOM_MACRO", (0.0, -0.16, -0.125), (0,0,-H*0.485), 105)
cam_screen = persp("CAM_SCREEN_EDGE_MACRO", (0.095, -0.13, 0.096), (W*0.39,front_surface,H*0.40), 110)
cam_camera = persp("CAM_CAMERA_MACRO", (0.070, 0.18, 0.100), (0.020,0.004,0.052), 115)
cam_front_sensor = persp("CAM_FRONT_SENSOR_MACRO", (0.0, -0.125, 0.082), (0, front_surface, island_z), 120)
cam_back_three = persp("CAM_BACK_THREE_QUARTER", (0.18, 0.30, 0.13), (0.010,0.002,0.020), 84)

bpy.context.view_layer.update()

assembly = (body, back_glass, screen_glass)
mins = [1e9, 1e9, 1e9]
maxs = [-1e9, -1e9, -1e9]
for obj in assembly:
    for corner in obj.bound_box:
        p = obj.matrix_world @ fc.Vector(corner)
        for axis in range(3):
            mins[axis] = min(mins[axis], p[axis])
            maxs[axis] = max(maxs[axis], p[axis])
actual_mm = {"width": (maxs[0]-mins[0])/MM, "depth": (maxs[1]-mins[1])/MM, "height": (maxs[2]-mins[2])/MM}
expected_mm = {"width": 71.5, "depth": 7.95, "height": 149.6}
delta_mm = {k: actual_mm[k] - expected_mm[k] for k in expected_mm}

bm = bmesh.new()
bm.from_mesh(body.data)
non_manifold = sum(1 for edge in bm.edges if not edge.is_manifold)
body_vertices = len(bm.verts)
body_faces = len(bm.faces)
bm.free()
mandatory = [
    "BODY_ALUMINUM", "SCREEN_GLASS", "SCREEN_CONTENT", "DISPLAY_BEZEL", "DISPLAY_GLASS_SEAT",
    "DYNAMIC_ISLAND", "FRONT_SENSOR_PILL", "FRONT_CAMERA_RING", "FRONT_CAMERA_GLASS", "FRONT_CAMERA_IRIS", "FRONT_CAMERA_PUPIL", "FRONT_RECEIVER_MIC", "APPLE_LOGO_DECAL",
    "ACTION_BUTTON", "VOL_UP", "VOL_DOWN", "SIDE_BUTTON", "CAMERA_CONTROL",
    "USB_C_CAVITY", "BOTTOM_MIC_APERTURE_03", "BOTTOM_SPEAKER_APERTURE_05",
    "CAMERA_HOUSING", "CAMERA_1_GLASS", "CAMERA_2_GLASS", "FLASH", "REAR_MIC"
]
missing = [name for name in mandatory if bpy.data.objects.get(name) is None]
forbidden = [name for name in ("FRONT_SENSOR_L", "FRONT_SENSOR_R", "FRONT_SENSOR_DOT") if bpy.data.objects.get(name) is not None]
expected_boolean_cuts = 2 + 5 + 1 + 8 + 2
passed = (
    non_manifold == 0
    and not missing
    and not forbidden
    and len(boolean_cuts) == expected_boolean_cuts
    and all(abs(v) <= 0.01 for v in delta_mm.values())
)
evidence = {
    "asset_id": "iphone_17",
    "stage": "LOW_DRAFT",
    "revision": "hard_surface_camera_housing_v21",
    "blender_version": bpy.app.version_string,
    "expected_mm": expected_mm,
    "actual_mm": {k: round(v, 6) for k, v in actual_mm.items()},
    "delta_mm": {k: round(v, 6) for k, v in delta_mm.items()},
    "body_non_manifold_edges": non_manifold,
    "body_vertices": body_vertices,
    "body_faces": body_faces,    "boolean_cuts": boolean_cuts,
    "boolean_cut_count": len(boolean_cuts),
    "mandatory_missing": missing,
    "forbidden_front_nodes": forbidden,
    "object_count": len(bpy.data.objects),
    "material_count": len(bpy.data.materials),
    "official_reference": "Apple iPhone 17 Dimensional Drawings 2025-09-09",
    "cover_glass_mm": [69.45, 147.61],
    "display_active_area_mm": [66.57, 144.79],
    "passed": passed,
}
os.makedirs(os.path.dirname(EVIDENCE), exist_ok=True)
with open(EVIDENCE, "w", encoding="utf-8") as handle:
    json.dump(evidence, handle, indent=2)

fc.save_blend(OUT)
renders = (
    (cam_front, "iphone_17_low_v21_front.png"),
    (cam_back, "iphone_17_low_v21_back.png"),
    (cam_three, "iphone_17_low_v21_three_quarter.png"),
    (cam_left, "iphone_17_low_v21_left_side.png"),
    (cam_right, "iphone_17_low_v21_right_side.png"),
    (cam_bottom, "iphone_17_low_v21_bottom_macro.png"),
    (cam_screen, "iphone_17_low_v21_screen_edge_macro.png"),
    (cam_camera, "iphone_17_low_v21_camera_macro.png"),
    (cam_front_sensor, "iphone_17_low_v21_front_sensor_macro.png"),
    (cam_back_three, "iphone_17_low_v21_back_three_quarter.png"),
)
def set_light(name, energy):
    obj = bpy.data.objects.get(name)
    if obj and getattr(obj, "data", None):
        obj.data.energy = energy

def render_profile(cam, filename):
    if "back" in filename or "camera_macro" in filename:
        profile = {"KEY_SOFTBOX": 38, "FILL_SOFTBOX": 7, "RIM_STRIP": 32, "TOP_STRIP": 16}
    elif "front_sensor_macro" in filename:
        profile = {"KEY_SOFTBOX": 118, "FILL_SOFTBOX": 24, "RIM_STRIP": 46, "TOP_STRIP": 34}
    else:
        profile = {"KEY_SOFTBOX": 82, "FILL_SOFTBOX": 14, "RIM_STRIP": 94, "TOP_STRIP": 42}
    for light_name, energy in profile.items():
        set_light(light_name, energy)
    fc.render_camera(cam, os.path.join(PREVIEWS, filename))

for cam, filename in renders:
    render_profile(cam, filename)
print("AWFUL_IPHONE17_V21_VALIDATION", json.dumps(evidence, sort_keys=True))
if not passed:
    raise RuntimeError("iPhone 17 LOW v21 validation failed")
