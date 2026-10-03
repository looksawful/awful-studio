import bmesh
import bpy
import json
import math
import os
import sys

argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []


def arg(flag, default):
    return argv[argv.index(flag) + 1] if flag in argv else default


OUT = os.path.abspath(
    arg(
        "--out",
        os.path.join(os.path.dirname(bpy.data.filepath), "hinge_clearance.json"),
    )
)
REPO_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..")
)
ANGLES = tuple(range(103))
MAX_INTERSECTION_MM3 = 0.01
PAIRS = (
    ("lid_base", "LID_UNIBODY", "BASE_UNIBODY"),
    ("barrel_l_base", "HINGE_BARREL_L", "BASE_UNIBODY"),
    ("barrel_r_base", "HINGE_BARREL_R", "BASE_UNIBODY"),
    ("lid_cover_l", "LID_UNIBODY", "HINGE_COVER_L"),
    ("lid_cover_r", "LID_UNIBODY", "HINGE_COVER_R"),
)
scene = bpy.context.scene
LOCAL_GEOMETRY = {}
CLOSED_GEOMETRY = {}


def baked_copy(name, suffix):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    source = bpy.data.objects[name].evaluated_get(depsgraph)
    # This contract animates rigid transforms only; bake local modifiers once.
    if name not in LOCAL_GEOMETRY:
        local=bpy.data.meshes.new_from_object(source,depsgraph=depsgraph)
        bm=bmesh.new(); bm.from_mesh(local)
        bmesh.ops.triangulate(bm,faces=list(bm.faces))
        CLOSED_GEOMETRY[name]=all(edge.is_manifold for edge in bm.edges)
        bm.to_mesh(local); bm.free(); LOCAL_GEOMETRY[name]=local
    mesh = LOCAL_GEOMETRY[name].copy()
    mesh.transform(source.matrix_world)
    obj = bpy.data.objects.new(f"_HINGE_CHECK_{suffix}", mesh)
    obj['_clearance_closed']=CLOSED_GEOMETRY[name]
    scene.collection.objects.link(obj)
    return obj


def intersection_volume_mm3(a_name, b_name, suffix, solver='MANIFOLD'):
    a = baked_copy(a_name, suffix + "_a")
    b = baked_copy(b_name, suffix + "_b")
    modifier = a.modifiers.new("HINGE_INTERSECT", "BOOLEAN")
    modifier.operation = "INTERSECT"
    for obj in (a,b):
        if not obj['_clearance_closed']: solver='EXACT'
    modifier.solver = solver
    modifier.object = b
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = a.evaluated_get(depsgraph)
    mesh = bpy.data.meshes.new_from_object(evaluated, depsgraph=depsgraph)
    bm = bmesh.new()
    bm.from_mesh(mesh)
    volume = abs(bm.calc_volume(signed=False)) * 1e9 if bm.faces else 0.0
    bm.free()
    bpy.data.meshes.remove(mesh)
    for obj in (a,b):
        temporary_mesh=obj.data
        bpy.data.objects.remove(obj,do_unlink=True)
        bpy.data.meshes.remove(temporary_mesh)
    return round(volume, 6)


def main():
    hinge=bpy.data.objects['CTRL_HINGE']
    source_path=os.path.relpath(bpy.data.filepath,REPO_ROOT).replace(os.sep,'/')
    result={'source':source_path,'states':[],'solver':'MANIFOLD for closed meshes; EXACT fallback'}
    failed=False
    for angle in ANGLES:
        if hinge.animation_data: hinge.animation_data.action=None
        hinge.rotation_euler.x=math.radians(90.0-angle)
        scene.frame_set(1); bpy.context.view_layer.update()
        volumes={key:intersection_volume_mm3(a,b,f'{angle}_{key}') for key,a,b in PAIRS}
        state_pass=all(value<=MAX_INTERSECTION_MM3 for value in volumes.values())
        failed=failed or not state_pass
        result['states'].append({'angle_deg':angle,'pass':state_pass,'intersection_mm3':volumes})
        if angle%10==0: print('MACBOOK_HINGE_SAMPLE',angle,state_pass,flush=True)
    result['passed']=not failed
    os.makedirs(os.path.dirname(OUT),exist_ok=True)
    with open(OUT,'w',encoding='utf-8') as handle: json.dump(result,handle,indent=2)
    print('MACBOOK_HINGE_CLEARANCE',json.dumps(result,sort_keys=True))
    if failed: raise RuntimeError('MacBook hinge solid collision detected')


if __name__=='__main__': main()
