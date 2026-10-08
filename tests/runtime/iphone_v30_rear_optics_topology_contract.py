"""Rear system authored/exported topology contract for iPhone 17 v30."""
import json
import bmesh
import bpy

limits={
    # Low-valence circular caps add one bounded inner support ring.
    "CAMERA_1_INNER":82,
    "CAMERA_2_INNER":82,
    "CAMERA_1_IRIS":66,
    "CAMERA_2_IRIS":66,
    "CAMERA_1_PUPIL":50,
    "CAMERA_2_PUPIL":50,
    "REAR_MIC":50,
    "FLASH_RING":82,
    "FLASH":82,
}
names=list(limits)+['CAMERA_HOUSING','CAMERA_HOUSING_SEAT']+[
    f'CAMERA_{i}_{part}' for i in (1,2) for part in ('RING','BEVEL','GLASS')]
report={}
for name in names:
    obj=bpy.data.objects[name]
    bm=bmesh.new(); bm.from_mesh(obj.data)
    report[name]={
        "verts":len(bm.verts),
        "faces":len(bm.faces),
        "ngons":sum(len(f.verts)>4 for f in bm.faces),
        "nonmanifold":sum(not e.is_manifold for e in bm.edges),
        "zero_edges":sum(e.calc_length()<1e-12 for e in bm.edges),
        "degenerate_faces":sum(f.calc_area()<1e-16 for f in bm.faces),
        "modifiers":[m.type for m in obj.modifiers],
        "signed_volume":bm.calc_volume(signed=True),
    }
    bm.free()
    assert report[name]["ngons"]==0,report
    assert report[name]["nonmanifold"]==0,report
    assert not any(report[name][k] for k in ('zero_edges','degenerate_faces','modifiers')),report
    assert report[name]['signed_volume']>0,report
    assert obj.parent.name=='CTRL_IPHONE_17',name
    assert obj.data.materials and all(obj.data.materials), (name, 'empty material slot')
    if name in limits:
        assert report[name]["verts"]<=limits[name],report
print("IPHONE_REAR_OPTICS_TOPOLOGY_GREEN",json.dumps(report,sort_keys=True))


# Quads may use either diagonal. Every actual GLB triangle must cover its authored
# face exactly, with correct winding, area and boundary; no proxy mesh is accepted.
from pathlib import Path
from collections import Counter
import struct
import sys
from mathutils import Vector
repo=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(repo/'tests/fast'))
from test_iphone_dimensional_drawing_contract import read_glb,accessor_vec3
doc,blob=read_glb(repo/'assets/device_mockups/iphone_17/runtime/v30/iphone_17_v30_web.glb')

def key(point):
    return tuple(round(v,7) for v in point)

def boundary(points):
    edges=Counter()
    for a,b in zip(points,points[1:]+points[:1]):
        edges[tuple(sorted((a,b)))]+=1 if a<b else -1
    return edges

for name in names:
    mesh=bpy.data.objects[name].data
    faces=[[key((mesh.vertices[i].co.x,mesh.vertices[i].co.z,-mesh.vertices[i].co.y))
            for i in poly.vertices] for poly in mesh.polygons]
    assigned=[[] for face in faces]
    node=next(n for n in doc['nodes'] if n.get('name')==name)
    for primitive in doc['meshes'][node['mesh']]['primitives']:
        positions=accessor_vec3(doc,blob,primitive['attributes']['POSITION'])
        accessor=doc['accessors'][primitive['indices']]
        view=doc['bufferViews'][accessor['bufferView']]
        code={5121:'B',5123:'H',5125:'I'}[accessor['componentType']]
        size=struct.calcsize('<'+code)
        offset=view.get('byteOffset',0)+accessor.get('byteOffset',0)
        indices=[struct.unpack_from('<'+code,blob,offset+i*size)[0]
                 for i in range(accessor['count'])]
        for i in range(0,len(indices),3):
            points=[Vector(positions[j]) for j in indices[i:i+3]]
            keys=[key(p) for p in points]
            matches=[j for j,face in enumerate(faces) if set(keys)<=set(face)]
            assert len(matches)==1,(name,'triangle outside unique authored face')
            j=matches[0]
            cross=(points[1]-points[0]).cross(points[2]-points[0])
            assert cross.length>2e-16,(name,'degenerate exported triangle')
            normal=mesh.polygons[j].normal
            assert cross.normalized().dot(Vector((normal.x,normal.z,-normal.y)))>.999,(name,'winding')
            assigned[j].append((keys,cross.length/2))
    for face,poly,triangles in zip(faces,mesh.polygons,assigned):
        assert len(triangles)==len(face)-2,(name,'triangle coverage count')
        edges=Counter()
        for keys,area in triangles:
            for edge,count in boundary(keys).items():
                edges[edge]+=count
        assert {e:v for e,v in edges.items() if v}==dict(boundary(face)),(name,'face boundary mismatch')
        assert abs(sum(area for keys,area in triangles)-poly.area)<=max(1e-14,poly.area*1e-4),(name,'area coverage')
print('IPHONE_REAR_AUTHORED_EXPORT_COVERAGE_GREEN',names)


# Drawing Detail D marks a 1mm rear microphone port on the camera plateau.
# An opaque plateau surface may not cover the microphone's central aperture.
from mathutils.bvhtree import BVHTree
import math
mic=bpy.data.objects['REAR_MIC']
center=mic.matrix_world @ Vector((0,0,0))
trees={}
for name in ('CAMERA_HOUSING','CAMERA_HOUSING_SEAT','REAR_MIC'):
    obj=bpy.data.objects[name]
    trees[name]=BVHTree.FromPolygons([obj.matrix_world @ v.co for v in obj.data.vertices],
                                    [tuple(p.vertices) for p in obj.data.polygons])
visibility=[]
for dx,dz in [(0,0)]+[(.00035*math.cos(i*math.pi/4),.00035*math.sin(i*math.pi/4)) for i in range(8)]:
    origin=Vector((center.x+dx,.02,center.z+dz))
    hits=[]
    for name,tree in trees.items():
        location,normal,index,distance=tree.ray_cast(origin,Vector((0,-1,0)))
        if location is not None:
            hits.append((distance,name,tuple(location)))
    first=min(hits)
    visibility.append({'first':first[1],'native_y':first[2][1],'offset_xz':(dx,dz)})
assert all(row['first']=='REAR_MIC' for row in visibility),('rear microphone aperture occluded',visibility)
print('IPHONE_REAR_MIC_APERTURE_VISIBLE_GREEN',visibility)
