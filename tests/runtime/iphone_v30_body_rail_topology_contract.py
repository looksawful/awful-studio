"""Saved BODY_ALUMINUM main-shell triangle contract; no diagnostic retriangulation."""
import math
import bmesh
import bpy

obj = bpy.data.objects["BODY_ALUMINUM"]
mesh = obj.data
source = bmesh.new()
source.from_mesh(mesh)
source.verts.ensure_lookup_table()
assert not any(len(face.verts) > 4 for face in source.faces)
assert not any(not edge.is_manifold for edge in source.edges)
assert not any(edge.calc_length() < 1e-10 for edge in source.edges)
assert not any(face.calc_area() < 1e-14 for face in source.faces)
component = {source.verts[0]}
queue = list(component)
while queue:
    vertex = queue.pop()
    for edge in vertex.link_edges:
        other = edge.other_vert(vertex)
        if other not in component:
            component.add(other)
            queue.append(other)
indices = {vertex.index for vertex in component}
cap_indices = {
    polygon.index for polygon in mesh.polygons
    if all(index in indices for index in polygon.vertices)
    and abs(polygon.normal.y) > 0.99
}
mesh.calc_loop_triangles()
triangles = [triangle for triangle in mesh.loop_triangles if triangle.polygon_index in cap_indices]

def triangle_metrics(triangle):
    verts = [mesh.vertices[index].co for index in triangle.vertices]
    lengths = [(verts[(index + 1) % 3] - verts[index]).length for index in range(3)]
    angles = []
    for opposite, first, second in (
        (lengths[0], lengths[1], lengths[2]),
        (lengths[1], lengths[2], lengths[0]),
        (lengths[2], lengths[0], lengths[1]),
    ):
        cosine = (first * first + second * second - opposite * opposite) / (2 * first * second)
        angles.append(math.degrees(math.acos(max(-1.0, min(1.0, cosine)))))
    return min(angles), max(lengths) / min(lengths), max(lengths)

def verify_annulus_coverage():
    # The two physical contours are convex. Polar sorting is independent of
    # authored correspondence, so a reversed inner loop cannot satisfy this
    # projected-area check merely by retaining valid faces/manifold edges.
    from collections import Counter
    by_plane = {}
    for triangle in triangles:
        if mesh.polygons[triangle.polygon_index].material_index != 0:
            continue
        points = [mesh.vertices[index].co for index in triangle.vertices]
        plane = round(sum(point.y for point in points) / 3, 8)
        by_plane.setdefault(plane, []).append(points)
    assert len(by_plane) == 2, by_plane.keys()
    for plane, cells in by_plane.items():
        edges = Counter()
        total_area = 0.0
        for points in cells:
            flat = [(round(point.x, 9), round(point.z, 9)) for point in points]
            total_area += abs(sum(
                flat[index][0] * flat[(index + 1) % 3][1]
                - flat[(index + 1) % 3][0] * flat[index][1]
                for index in range(3)
            )) / 2
            for index in range(3):
                edges[tuple(sorted((flat[index], flat[(index + 1) % 3])))] += 1
        neighbors = {}
        for (first, second), count in edges.items():
            if count == 1:
                neighbors.setdefault(first, set()).add(second)
                neighbors.setdefault(second, set()).add(first)
        assert all(len(links) == 2 for links in neighbors.values()), "broken cap contour"
        remaining = set(neighbors)
        areas = []
        while remaining:
            seed = next(iter(remaining))
            loop, queue = {seed}, [seed]
            while queue:
                for point in neighbors[queue.pop()]:
                    if point not in loop:
                        loop.add(point)
                        queue.append(point)
            remaining -= loop
            outline = sorted(loop, key=lambda point: math.atan2(point[1], point[0]))
            areas.append(abs(sum(
                outline[index][0] * outline[(index + 1) % len(outline)][1]
                - outline[(index + 1) % len(outline)][0] * outline[index][1]
                for index in range(len(outline))
            )) / 2)
        assert len(areas) == 2, areas
        expected_area = max(areas) - min(areas)
        assert abs(total_area - expected_area) <= 1e-9, {
            "plane": plane, "triangle_area": total_area,
            "physical_annulus_area": expected_area,
        }
    print("IPHONE_BODY_ANNULUS_COVERAGE_GREEN", len(by_plane))

verify_annulus_coverage()

metrics = [triangle_metrics(triangle) for triangle in triangles]
assert metrics, "main shell cap triangles missing"
report = {
    "component_verts": len(component),
    "cap_triangles": len(triangles),
    "min_angle_deg": min(item[0] for item in metrics),
    "max_aspect": max(item[1] for item in metrics),
    "max_edge_m": max(item[2] for item in metrics),
}
source.free()
# Broad local quality limits reject the reproduced crossed-strip/sliver defect.
# These are diagnostic limits, not whole-device topology or visual acceptance.
assert report["max_aspect"] <= 25.0, report
assert report["max_edge_m"] <= 0.025, report
assert report["min_angle_deg"] >= 1.0, report
print("IPHONE_BODY_RAIL_TOPOLOGY_GREEN", report)

# Verify the saved cap diagonals survive the existing compat GLB export.
from collections import Counter
from pathlib import Path
import struct
import sys

repo = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(repo / "tests" / "fast"))
from test_iphone_dimensional_drawing_contract import read_glb, accessor_vec3

doc, blob = read_glb(repo / "assets/device_mockups/iphone_17/runtime/v30/iphone_17_v30_web.glb")
node = next(node for node in doc["nodes"] if node.get("name") == "BODY_ALUMINUM")
assert not any(key in node for key in ("matrix", "translation", "rotation", "scale")), node

def signature(points):
    return tuple(sorted(tuple(round(value, 7) for value in point) for point in points))

expected = Counter(
    signature((mesh.vertices[index].co.x, mesh.vertices[index].co.z, -mesh.vertices[index].co.y)
              for index in triangle.vertices)
    for triangle in triangles
)
exported = Counter()
for primitive in doc["meshes"][node["mesh"]]["primitives"]:
    positions = accessor_vec3(doc, blob, primitive["attributes"]["POSITION"])
    accessor = doc["accessors"][primitive["indices"]]
    view = doc["bufferViews"][accessor["bufferView"]]
    code = {5121: "B", 5123: "H", 5125: "I"}[accessor["componentType"]]
    size = struct.calcsize("<" + code)
    offset = view.get("byteOffset", 0) + accessor.get("byteOffset", 0)
    indices = [struct.unpack_from("<" + code, blob, offset + index * size)[0]
               for index in range(accessor["count"])]
    for index in range(0, len(indices), 3):
        exported[signature(positions[vertex] for vertex in indices[index:index + 3])] += 1
assert not expected - exported, "GLB changed or lost authored main-cap triangle buffers"
print("IPHONE_BODY_EXPORTED_CAPS_GREEN", sum(expected.values()))
