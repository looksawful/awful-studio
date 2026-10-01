"""Known volume fixtures validate the faster closed-mesh solver against EXACT."""
import bpy
import math
import runpy
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
contract=runpy.run_path(str(ROOT/'assets/device_mockups/macbook_pro_14/validate_hinge_clearance.py'),run_name='solver_contract')
volume=contract['intersection_volume_mm3']
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
bpy.ops.mesh.primitive_cube_add(size=.001); a=bpy.context.object; a.name='FIXTURE_A'
bpy.ops.mesh.primitive_cube_add(size=.001); b=bpy.context.object; b.name='FIXTURE_B'
mesh_counts=[]
for offset,expected in ((.0005,.5),(.001,0),(.002,0)):
    b.location.x=offset; bpy.context.view_layer.update()
    fast=volume(a.name,b.name,'fast','MANIFOLD'); exact=volume(a.name,b.name,'exact','EXACT')
    assert abs(fast-expected)<.00001 and abs(fast-exact)<.00001,(offset,fast,exact,expected)
    mesh_counts.append(len(bpy.data.meshes))
assert len(set(mesh_counts))==1, f'Clearance samples leak temporary meshes: {mesh_counts}'
bpy.ops.mesh.primitive_torus_add(major_radius=.00353,minor_radius=.00012,major_segments=64,minor_segments=12,rotation=(0,math.pi/2,0))
ring=bpy.context.object; ring.name='FIXTURE_RING'
bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=.0033,depth=.005,rotation=(0,math.pi/2,0))
barrel=bpy.context.object; barrel.name='FIXTURE_BARREL'; bpy.context.view_layer.update()
assert volume(ring.name,barrel.name,'annulus_fast','MANIFOLD')==0
assert volume(ring.name,barrel.name,'annulus_exact','EXACT')==0
print('MACBOOK_CLEARANCE_SOLVER_CONTRACT_PASS',bpy.app.version_string)
