"""Display-frame source topology contract for iPhone 17 v30.

The contract is intentionally independent from the production builder:
- Apple-facing dimensions/material identity are fixed literals.
- contour error is measured against an ideal rounded rectangle sampled more
  finely than the production mesh;
- cap quality is measured after deterministic triangulation so a source quad
  cannot hide a bad exported triangle.
"""
import json
import math

import bmesh
import bpy

EXPECTED = {
    "DISPLAY_GLASS_SEAT": {
        "material": "MAT_ASSEMBLY_GAP",
        "dimensions_m": (0.06955, 0.00007, 0.14771),
        "location_m": (0.0, -0.003635, 0.0),
        "radius_m": 0.01205,
    },
    "DISPLAY_BEZEL": {
        "material": "MAT_DISPLAY_BEZEL",
        "dimensions_m": (0.06725, 0.00008, 0.14547),
        "location_m": (0.0, -0.00372, 0.0),
        "radius_m": 0.01087,
    },
    "SCREEN_CONTENT": {
        "materials": ["MAT_SCREEN_CONTENT", "MAT_SCREEN_EDGE"],
        "dimensions_m": (0.06657, 0.000325, 0.14479),
        "location_m": (0.0, -0.00379, 0.0),
        "radius_m": 0.01055,
        "max_vertices": 480,
        "max_cap_edge_m": 0.020,
    },
}

REJECTED_BASELINE_VERTS = 392
REJECTED_BASELINE_OUTLINE_POINTS = 196
MAX_CONTOUR_ERROR_M = 0.00001
MIN_TRIANGLE_ANGLE_DEG = 7.0
MAX_TRIANGLE_ASPECT = 8.0


def ideal_outline(width, height, radius, segments=48):
    half_w, half_h = width * 0.5, height * 0.5
    corners = (
        (half_w - radius, half_h - radius, 0.0),
        (-half_w + radius, half_h - radius, 90.0),
        (-half_w + radius, -half_h + radius, 180.0),
        (half_w - radius, -half_h + radius, 270.0),
    )
    points = []
    for cx, cz, start in corners:
        for step in range(segments + 1):
            angle = math.radians(start + 90.0 * step / segments)
            points.append((cx + math.cos(angle) * radius, cz + math.sin(angle) * radius))
    return points


def point_segment_distance(point, start, end):
    px, pz = point
    ax, az = start
    bx, bz = end
    dx, dz = bx - ax, bz - az
    denom = dx * dx + dz * dz
    if denom == 0.0:
        return math.hypot(px - ax, pz - az)
    t = max(0.0, min(1.0, ((px - ax) * dx + (pz - az) * dz) / denom))
    return math.hypot(px - (ax + t * dx), pz - (az + t * dz))


def outline_from_depth_edges(bm):
    points = set()
    for edge in bm.edges:
        first, second = edge.verts
        if abs(first.co.y - second.co.y) > 1e-9:
            points.add((round(first.co.x, 12), round(first.co.z, 12)))
            points.add((round(second.co.x, 12), round(second.co.z, 12)))
    ordered = sorted(points, key=lambda point: math.atan2(point[1], point[0]))
    assert len(ordered) >= 8, f"not enough outline points: {len(ordered)}"
    return ordered


def triangle_quality(face):
    verts = [vertex.co.copy() for vertex in face.verts]
    lengths = [
        (verts[(index + 1) % 3] - verts[index]).length
        for index in range(3)
    ]
    shortest = min(lengths)
    if shortest <= 1e-12:
        return 0.0, math.inf
    angles = []
    for opposite, first, second in (
        (lengths[0], lengths[1], lengths[2]),
        (lengths[1], lengths[2], lengths[0]),
        (lengths[2], lengths[0], lengths[1]),
    ):
        cosine = (first * first + second * second - opposite * opposite) / (2.0 * first * second)
        angles.append(math.degrees(math.acos(max(-1.0, min(1.0, cosine)))))
    return min(angles), max(lengths) / shortest


report = {}
for name, expected in EXPECTED.items():
    obj = bpy.data.objects[name]
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.normal_update()

    ngons = sum(len(face.verts) > 4 for face in bm.faces)
    nonmanifold = sum(not edge.is_manifold for edge in bm.edges)
    outline = outline_from_depth_edges(bm)
    outline_segments = list(zip(outline, outline[1:] + outline[:1]))
    reference = ideal_outline(
        expected["dimensions_m"][0],
        expected["dimensions_m"][2],
        expected["radius_m"],
    )
    contour_error = max(
        min(point_segment_distance(point, start, end) for start, end in outline_segments)
        for point in reference
    )

    quality = bm.copy()
    quality.normal_update()
    cap_faces = [face for face in quality.faces if abs(face.normal.y) > 0.99]
    bmesh.ops.triangulate(
        quality,
        faces=cap_faces,
        quad_method="BEAUTY",
        ngon_method="BEAUTY",
    )
    quality.normal_update()
    cap_triangles = [
        face
        for face in quality.faces
        if len(face.verts) == 3 and abs(face.normal.y) > 0.99
    ]
    triangle_metrics = [triangle_quality(face) for face in cap_triangles]
    max_cap_edge = max((edge.verts[0].co - edge.verts[1].co).length for face in cap_triangles for edge in face.edges)
    min_angle = min(metric[0] for metric in triangle_metrics)
    max_aspect = max(metric[1] for metric in triangle_metrics)
    quality.free()

    report[name] = {
        "verts": len(bm.verts),
        "faces": len(bm.faces),
        "ngons": ngons,
        "nonmanifold": nonmanifold,
        "outline_points": len(outline),
        "contour_error_m": contour_error,
        "cap_triangles": len(cap_triangles),
        "min_triangle_angle_deg": min_angle,
        "max_triangle_aspect": max_aspect,
        "max_cap_edge_m": max_cap_edge,
        "materials": [material.name for material in obj.data.materials],
        "dimensions_m": tuple(obj.dimensions),
        "location_m": tuple(obj.location),
    }
    bm.free()

    assert report[name]["ngons"] == 0, report
    assert report[name]["nonmanifold"] == 0, report
    assert report[name]["verts"] < expected.get("max_vertices", REJECTED_BASELINE_VERTS), report
    assert report[name]["outline_points"] < REJECTED_BASELINE_OUTLINE_POINTS, report
    assert report[name]["contour_error_m"] <= MAX_CONTOUR_ERROR_M, report
    assert report[name]["min_triangle_angle_deg"] >= MIN_TRIANGLE_ANGLE_DEG, report
    assert report[name]["max_triangle_aspect"] <= MAX_TRIANGLE_ASPECT, report
    assert report[name]["materials"] == expected.get("materials", [expected.get("material")]), report
    if "max_cap_edge_m" in expected:
        assert report[name]["max_cap_edge_m"] <= expected["max_cap_edge_m"], report
    assert all(
        math.isclose(actual, target, abs_tol=1e-7)
        for actual, target in zip(report[name]["dimensions_m"], expected["dimensions_m"])
    ), report
    assert all(
        math.isclose(actual, target, abs_tol=1e-7)
        for actual, target in zip(report[name]["location_m"], expected["location_m"])
    ), report

print("IPHONE_DISPLAY_FRAME_TOPOLOGY_GREEN", json.dumps(report, sort_keys=True))
