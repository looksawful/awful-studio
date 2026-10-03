import bpy, json, math, os
from mathutils import Vector

MM = 0.001
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
TEX = os.path.join(OUT, "textures")
os.makedirs(TEX, exist_ok=True)

VARIANTS = (16, 24, 32, 40)
HIGH_N = 192
OW, OH, IW, IH = 24.88*MM, 42.28*MM, 19.66*MM, 37.02*MM
PLATEAU = 1.78*MM
GLASS_TOP = 3.45*MM
DZ = 8.86*MM

def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for blocks in (bpy.data.meshes, bpy.data.materials, bpy.data.images,
                   bpy.data.cameras, bpy.data.lights):
        for block in list(blocks):
            if block.users == 0:
                blocks.remove(block)

def material(name, color, metallic=0.0, roughness=0.3):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Metallic"].default_value = metallic
    b.inputs["Roughness"].default_value = roughness
    return m

def apply_bevel(obj, width, segments=6):
    mod = obj.modifiers.new("SOURCE_BEVEL", "BEVEL")
    mod.width = width
    mod.segments = segments
    mod.limit_method = "ANGLE"
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.modifier_apply(modifier=mod.name)
    obj.select_set(False)

def capsule_outline(width, height, count):
    radius = width * 0.5
    straight = max(0.0, height - 2.0 * radius)
    half = count // 2
    pts = []
    for i in range(half + 1):
        a = math.pi * i / half
        pts.append((radius * math.cos(a), straight*0.5 + radius*math.sin(a)))
    for i in range(1, half):
        a = math.pi + math.pi * i / half
        pts.append((radius * math.cos(a), -straight*0.5 + radius*math.sin(a)))
    return pts

def prism(name, outline, depth, collection, y=0.0):
    count = len(outline)
    verts = [(x, -depth/2, z) for x,z in outline] + [(x, depth/2, z) for x,z in outline]
    faces = []
    for cap, reverse in ((0, True), (count, False)):
        center = len(verts)
        verts.append((0.0, (-depth/2 if cap == 0 else depth/2), 0.0))
        for i in range(count):
            j = (i+1) % count
            face = (center, cap+i, cap+j)
            faces.append(tuple(reversed(face)) if reverse else face)
    for i in range(count):
        j = (i+1) % count
        faces.append((i, j, count+j, count+i))
    mesh = bpy.data.meshes.new(name+"_MESH")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    obj.location.y = y
    return obj

def cylinder(name, radius, depth, count, collection, y=0.0, z=0.0):
    outline = [(radius*math.cos(2*math.pi*i/count),
                z + radius*math.sin(2*math.pi*i/count)) for i in range(count)]
    return prism(name, outline, depth, collection, y)

def smart_uv(obj):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(55), island_margin=0.03)
    bpy.ops.object.mode_set(mode="OBJECT")
    obj.select_set(False)

def smooth_for_bake(obj):
    for p in obj.data.polygons:
        p.use_smooth = True
    try:
        obj.data.set_sharp_from_angle(angle=math.radians(48))
    except Exception:
        pass
def bake_material(name, low, high, color, metallic, roughness, size=512):
    smart_uv(low)
    smooth_for_bake(low)
    m = material(name, color, metallic, roughness)
    low.data.materials.clear()
    low.data.materials.append(m)
    img = bpy.data.images.new(name+"_NORMAL", width=size, height=size)
    img.colorspace_settings.name = "Non-Color"
    tex = m.node_tree.nodes.new("ShaderNodeTexImage")
    tex.image = img
    tex.select = True
    m.node_tree.nodes.active = tex
    bpy.ops.object.select_all(action="DESELECT")
    high.hide_render = False
    high.select_set(True)
    low.select_set(True)
    bpy.context.view_layer.objects.active = low
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.render.bake.use_selected_to_active = True
    scene.render.bake.cage_extrusion = 0.35 * MM
    scene.render.bake.max_ray_distance = 0.55 * MM
    scene.render.bake.margin = 8
    scene.render.bake.normal_space = "TANGENT"
    bpy.ops.object.bake(type="NORMAL")
    high.hide_render = True
    normal = m.node_tree.nodes.new("ShaderNodeNormalMap")
    normal.inputs["Strength"].default_value = 1.0
    m.node_tree.links.new(tex.outputs["Color"], normal.inputs["Color"])
    m.node_tree.links.new(normal.outputs["Normal"], m.node_tree.nodes["Principled BSDF"].inputs["Normal"])
    img.filepath_raw = os.path.join(TEX, name+"_normal.png")
    img.file_format = "PNG"
    img.save()
    return m, img

def build_sources():
    c = bpy.data.collections.new("HIGH_SOURCE")
    bpy.context.scene.collection.children.link(c)
    shapes = {}
    shapes["seat"] = prism("HP_SEAT", capsule_outline(OW,OH,HIGH_N), .30*MM, c, .15*MM)
    shapes["housing"] = prism("HP_HOUSING", capsule_outline(IW,IH,HIGH_N), PLATEAU, c, PLATEAU/2)
    shapes["ring"] = cylinder("HP_RING", 8.00*MM, 1.10*MM, HIGH_N, c, 2.20*MM)
    shapes["bevel"] = cylinder("HP_BEVEL", 7.44*MM, .70*MM, HIGH_N, c, 2.75*MM)
    shapes["glass"] = cylinder("HP_GLASS", 6.81*MM, .70*MM, HIGH_N, c, GLASS_TOP-.35*MM)
    for key, width in (("seat",.10),("housing",.18),("ring",.13),("bevel",.07),("glass",.06)):
        apply_bevel(shapes[key], width*MM, 6)
        smooth_for_bake(shapes[key])
        shapes[key].hide_render = True
    return c, shapes

def copy_object(source, name, collection, z=0.0):
    obj = source.copy()
    obj.data = source.data.copy()
    obj.name = name
    collection.objects.link(obj)
    obj.location.z += z
    return obj

def build_variant(n, high):
    c = bpy.data.collections.new("LOW_"+str(n))
    bpy.context.scene.collection.children.link(c)
    raw = {
        "seat": prism("LP_SEAT_"+str(n), capsule_outline(OW,OH,n), .30*MM, c, .15*MM),
        "housing": prism("LP_HOUSING_"+str(n), capsule_outline(IW,IH,n), PLATEAU, c, PLATEAU/2),
        "ring": cylinder("LP_RING_"+str(n), 8.00*MM, 1.10*MM, n, c, 2.20*MM),
        "bevel": cylinder("LP_BEVEL_"+str(n), 7.44*MM, .70*MM, n, c, 2.75*MM),
        "glass": cylinder("LP_GLASS_"+str(n), 6.81*MM, .70*MM, n, c, GLASS_TOP-.35*MM),
    }
    params = {
        "seat": ((.42,.43,.46), .35, .30),
        "housing": ((.55,.56,.59), .25, .28),
        "ring": ((.08,.09,.11), .88, .18),
        "bevel": ((.34,.35,.38), .82, .19),
        "glass": ((.012,.018,.028), .05, .055),
    }
    images = []
    for key,obj in raw.items():
        color,metal,rough = params[key]
        _, img = bake_material(key+"_"+str(n), obj, high[key], color, metal, rough)
        images.append(img)
    assembly = [raw["seat"], raw["housing"]]
    for z in (DZ, -DZ):
        for key in ("ring","bevel","glass"):
            name = key+"_"+str(n)+"_"+str(round(z/MM,2))
            assembly.append(copy_object(raw[key], name, c, z))
    for key in ("ring","bevel","glass"):
        raw[key].hide_render = True
    return c, assembly, images

def stats(objects, n, images):
    meshes = [o for o in objects if o.type == "MESH" and not o.hide_render]
    verts = sum(len(o.data.vertices) for o in meshes)
    faces = sum(len(o.data.polygons) for o in meshes)
    tris = 0
    for o in meshes:
        o.data.calc_loop_triangles()
        tris += len(o.data.loop_triangles)
    mm_error = max(r*(1-math.cos(math.pi/n)) for r in (OW/MM/2, IW/MM/2, 8.0, 7.44, 6.81))
    tex_bytes = sum(os.path.getsize(i.filepath_raw) for i in images if os.path.exists(i.filepath_raw))
    return {
        "verts": verts,
        "faces": faces,
        "tris": tris,
        "silhouette_error_mm": mm_error,
        "texture_bytes": tex_bytes,
    }

def look_at(obj, target=(0,.0015,0)):
    obj.rotation_euler = (Vector(target)-obj.location).to_track_quat("-Z","Y").to_euler()

def setup_render():
    s=bpy.context.scene
    s.render.engine="BLENDER_EEVEE"
    s.render.resolution_x=1200
    s.render.resolution_y=900
    s.render.resolution_percentage=100
    s.render.image_settings.file_format="PNG"
    s.world.use_nodes=True
    bg=s.world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value=(.015,.015,.02,1)
    bg.inputs["Strength"].default_value=.32
    cd=bpy.data.cameras.new("CAM")
    cam=bpy.data.objects.new("CAM",cd)
    bpy.context.scene.collection.objects.link(cam)
    cam.location=(.052,.115,.045)
    cd.lens=86
    look_at(cam)
    s.camera=cam
    for name,loc,en,size in (
        ("KEY",(.07,.08,.10),130,.10),
        ("FILL",(-.06,.04,.02),55,.08),
        ("RIM",(-.02,-.05,.08),90,.06),
    ):
        ld=bpy.data.lights.new(name,"AREA")
        ld.energy=en
        ld.shape="DISK"
        ld.size=size
        lo=bpy.data.objects.new(name,ld)
        lo.location=loc
        look_at(lo)
        bpy.context.scene.collection.objects.link(lo)
    return cam

def set_visible(collections, target):
    for c in collections:
        c.hide_render = c != target
def make_wire_material():
    m=bpy.data.materials.new("WIRE_MAT")
    m.use_nodes=True
    n=m.node_tree.nodes
    l=m.node_tree.links
    for node in list(n):
        n.remove(node)
    out=n.new("ShaderNodeOutputMaterial")
    wire=n.new("ShaderNodeWireframe")
    wire.inputs["Size"].default_value=.000028
    bg=n.new("ShaderNodeBackground")
    bg.inputs["Color"].default_value=(.92,.95,1,1)
    bg.inputs["Strength"].default_value=2.0
    black=n.new("ShaderNodeBackground")
    black.inputs["Color"].default_value=(.015,.015,.02,1)
    mix=n.new("ShaderNodeMixShader")
    l.new(wire.outputs["Fac"],mix.inputs[0]); l.new(black.outputs["Background"],mix.inputs[1]); l.new(bg.outputs["Background"],mix.inputs[2]); l.new(mix.outputs[0],out.inputs[0])
    return m
def swap_material(objects, replacement):
    original=[]
    for o in objects:
        if o.hide_render or o.type!="MESH":
            continue
        old=o.data.materials[0] if len(o.data.materials) else None
        original.append((o,old))
        if len(o.data.materials):
            o.data.materials[0]=replacement
        else:
            o.data.materials.append(replacement)
    return original

def restore_material(saved):
    for o,m in saved:
        if m is not None:
            o.data.materials[0]=m

def export_glb(objects, path):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objects:
        if not o.hide_render:
            o.select_set(True)
    bpy.ops.export_scene.gltf(
        filepath=path,
        export_format="GLB",
        use_selection=True,
        export_apply=True,
        export_texcoords=True,
        export_normals=True,
        export_tangents=True,
    )
clear_scene()
cam=setup_render()
_,high=build_sources()
collections=[]
variants={}
metrics={}
wiremat=make_wire_material()
for n in VARIANTS:
    c,objects,images=build_variant(n,high)
    collections.append(c)
    variants[n]=(c,objects,images)

for n,(c,objects,images) in variants.items():
    set_visible(collections,c)
    bpy.context.scene.render.engine="BLENDER_EEVEE"
    bpy.context.scene.render.filepath=os.path.join(OUT,"camera_"+str(n)+"_baked.png")
    bpy.ops.render.render(write_still=True)
    saved=swap_material(objects,wiremat)
    bpy.context.scene.render.filepath=os.path.join(OUT,"camera_"+str(n)+"_wire.png")
    bpy.ops.render.render(write_still=True)
    restore_material(saved)
    glb=os.path.join(OUT,"camera_"+str(n)+".glb")
    export_glb(objects,glb)
    m=stats(objects,n,images)
    m["glb_bytes"]=os.path.getsize(glb)
    metrics[str(n)]=m

cam=bpy.context.scene.camera
distance=(cam.location-Vector((0,.0015,0))).length/MM
sensor=cam.data.sensor_width
focal_px=bpy.context.scene.render.resolution_x*cam.data.lens/sensor
for n,m in metrics.items():
    m["estimated_macro_error_px"]=m["silhouette_error_mm"]*focal_px/distance

with open(os.path.join(OUT,"metrics.json"),"w",encoding="utf-8") as f:
    json.dump(metrics,f,indent=2)
for n,(c,_,_) in variants.items():
    c.hide_viewport = n != 32
    c.hide_render = n != 32
for o in high.values():
    o.hide_viewport=True
    o.hide_render=True
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,"camera_lowpoly_bake_variants.blend"))
print("METRICS="+json.dumps(metrics,sort_keys=True))

