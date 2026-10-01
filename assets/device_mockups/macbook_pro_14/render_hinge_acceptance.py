import bpy
import math
import os
import sys
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []


def arg(flag, default):
    return argv[argv.index(flag) + 1] if flag in argv else default


OUT = os.path.abspath(
    arg(
        "--out",
        os.path.join(os.path.dirname(bpy.data.filepath), "hinge_acceptance"),
    )
)
os.makedirs(OUT, exist_ok=True)

scene = bpy.context.scene
hinge = bpy.data.objects["CTRL_HINGE"]

scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 1400
scene.render.resolution_y = 1050
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.view_settings.exposure = -1.35

scene.world.use_nodes = True
background = scene.world.node_tree.nodes.get("Background")
background.inputs["Color"].default_value = (0.012, 0.014, 0.018, 1)
background.inputs["Strength"].default_value = 0.08

for obj in list(bpy.data.objects):
    if obj.type in {"LIGHT", "CAMERA"}:
        bpy.data.objects.remove(obj, do_unlink=True)


def aim(obj, point):
    obj.rotation_euler = (
        Vector(point) - obj.location
    ).to_track_quat("-Z", "Y").to_euler()


def area(name, location, energy, size, point):
    data = bpy.data.lights.new(name, "AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    obj = bpy.data.objects.new(name, data)
    scene.collection.objects.link(obj)
    obj.location = location
    aim(obj, point)
    return obj


area("ACC_KEY", (0.38, -0.42, 0.42), 75, 0.32, (0, 0.02, 0.09))
area("ACC_FILL", (-0.34, -0.28, 0.24), 28, 0.30, (0, 0.02, 0.08))
area("ACC_RIM", (0.28, 0.30, 0.34), 60, 0.26, (0, 0.08, 0.11))
area("ACC_TOP", (-0.06, 0.02, 0.52), 34, 0.34, (0, 0.02, 0.08))

camera_data = bpy.data.cameras.new("ACC_CAMERA")
camera_data.type = "ORTHO"
camera_data.ortho_scale = 0.46
camera_data.clip_start = 0.01
camera_data.clip_end = 2.0  # Orthographic depth steps <0.12 micron, below 10-micron legend seating.
camera = bpy.data.objects.new("ACC_CAMERA", camera_data)
scene.collection.objects.link(camera)
camera.location = (0.43, -0.57, 0.34)
aim(camera, (0, 0.025, 0.082))
scene.camera = camera


def render_current():
    only=arg('--only','')
    if not only or os.path.basename(scene.render.filepath)==only:
        bpy.ops.render.render(write_still=True)


def set_angle(degrees):
    if hinge.animation_data:
        hinge.animation_data.action = None
    hinge.rotation_euler.x = math.radians(90.0 - degrees)
    scene.frame_set(1)
    bpy.context.view_layer.update()


for angle in (0, 30, 60, 90, 102):
    set_angle(angle)
    scene.render.filepath = os.path.join(
        OUT, f"macbook_hinge_{angle:03d}.png"
    )
    render_current()

set_angle(30)
camera.data.ortho_scale = 0.19
camera.location = (0.27, 0.20, 0.16)
aim(camera, (0, 0.105, 0.035))
scene.render.filepath = os.path.join(OUT, "macbook_hinge_macro_030.png")
render_current()

set_angle(102)
for label, location, target, scale in (
    ('deck', (0, -.035, .48), (0, .035, .01), .38),
    ('ports_left', (-.28, .008, .055), (-.152, .008, .004), .17),
    ('ports_right', (.28, .008, .055), (.152, .008, .004), .17),
):
    camera.data.ortho_scale = scale
    camera.location = location
    aim(camera, target)
    scene.render.filepath = os.path.join(OUT, f'macbook_{label}.png')
    render_current()

for label, location, target, scale in (
    ('hero_full', (.43,-.57,.34), (0,.025,.102), .51),
    ('camera_macro', (.014,-.13,.253), (0,.060,.214), .055),
    ('keycap_macro', (-.07,-.10,.15), (-.075,.05,.009), .055),
    ('speaker_macro', (.16,-.030,.120), (.1463,.04,.0083), .060),
    ('front_recess', (0,-.25,.024), (0,-.108,.006), .058),
    ('lid_back', (.03,.40,.23), (0,.11,.115), .34),
):
    camera.data.ortho_scale=scale; camera.location=location; aim(camera,target)
    scene.render.filepath=os.path.join(OUT,f'macbook_{label}.png')
    render_current()

set_angle(0)
camera.data.ortho_scale=.36; camera.location=(0,-.05,-.50); aim(camera,(0,0,0))
scene.render.filepath=os.path.join(OUT,'macbook_underside.png')
area('ACC_UNDERSIDE_DIAGNOSTIC',(.12,-.20,-.26),18,.23,(0,0,0))
render_current()

print("MACBOOK_HINGE_ACCEPTANCE_RENDERS", OUT)
