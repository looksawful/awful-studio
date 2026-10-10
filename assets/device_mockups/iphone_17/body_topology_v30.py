"""Intentional low-poly BODY_ALUMINUM topology for iPhone 17 v30.

The dimensional/boolean body remains the high-poly bake source. This module
constructs the runtime body directly from Apple Detail A silhouette plus
localized manifold panel cells for controls and bottom apertures.
"""
import math

import bmesh
import bpy
from mathutils import Vector


def _point_in_polygon(px, py, polygon):
    inside = False
    j = len(polygon) - 1
    for i, (xi, yi) in enumerate(polygon):
        xj, yj = polygon[j]
        crosses = ((yi > py) != (yj > py)) and (
            px < (xj - xi) * (py - yi) / (yj - yi + 1e-30) + xi
        )
        if crosses:
            inside = not inside
        j = i
    return inside


def _matched_annulus_loops(xa, xb, ya, yb, hole, base_segments=16):
    cx = sum(x for x, _ in hole) / len(hole)
    cy = sum(y for _, y in hole) / len(hole)
    period = round(2 * math.pi, 12)

    def angle_key(x, y):
        angle = round(math.atan2(y - cy, x - cx) % (2 * math.pi), 12)
        return 0.0 if angle >= period else angle

    angles = {round(2 * math.pi * i / base_segments, 12) for i in range(base_segments)}
    # Preserve every authored hole vertex direction. Without these angles,
    # elongated capsules collapse into pointed/diamond-like openings even
    # though the resulting shell remains manifold.
    for x, y in hole:
        angles.add(angle_key(x, y))
    for x, y in ((xa, ya), (xb, ya), (xb, yb), (xa, yb)):
        angles.add(angle_key(x, y))

    outer, inner = [], []
    for angle in sorted(angles):
        dx, dy = math.cos(angle), math.sin(angle)
        tx = ((xb - cx) if dx > 0 else (xa - cx)) / dx if abs(dx) > 1e-12 else 1e30
        ty = ((yb - cy) if dy > 0 else (ya - cy)) / dy if abs(dy) > 1e-12 else 1e30
        outer_t = min(value for value in (tx, ty) if value > 0)
        outer.append((cx + dx * outer_t, cy + dy * outer_t))

        lo, hi = 0.0, outer_t
        for _ in range(60):
            mid = (lo + hi) * 0.5
            if _point_in_polygon(cx + dx * mid, cy + dy * mid, hole):
                lo = mid
            else:
                hi = mid
        inner.append((cx + dx * lo, cy + dy * lo))
    return outer, inner


def _uniform_annulus_loops(xa, xb, ya, yb, hole, segments=44, *, pin_corners=False):
    """Sample a convex hole and rectangular cell on the same uniform rays.

    Unlike _matched_annulus_loops, this deliberately avoids injecting every
    authored/corner angle into the correspondence. Those clustered angles are
    what created needle-like radial cells around narrow controls.
    """
    cx = sum(x for x, _ in hole) / len(hole)
    cy = sum(y for _, y in hole) / len(hole)
    angles = [2.0 * math.pi * index / segments for index in range(segments)]
    if pin_corners:
        # Consecutive bottom cells must meet at exact rectangle corners.
        # Redistribute the SAME number of rays between those four anchors;
        # snapping a nearby uniform ray produced 3-degree needle triangles.
        circle = 2.0 * math.pi
        anchors = sorted(math.atan2(y - cy, x - cx) % circle
                         for x, y in ((xa, ya), (xb, ya), (xb, yb), (xa, yb)))
        spans = [
            (anchors[(i + 1) % 4] + (circle if i == 3 else 0.0)) - anchors[i]
            for i in range(4)
        ]
        counts = [1, 1, 1, 1]
        for _ in range(segments - 4):
            widest = max(range(4), key=lambda i: spans[i] / counts[i])
            counts[widest] += 1
        angles = sorted(
            (anchors[i] + spans[i] * j / counts[i]) % circle
            for i in range(4) for j in range(counts[i])
        )
    outer, inner = [], []
    for angle in angles:
        dx, dy = math.cos(angle), math.sin(angle)
        tx = ((xb - cx) if dx > 0 else (xa - cx)) / dx if abs(dx) > 1e-12 else 1e30
        ty = ((yb - cy) if dy > 0 else (ya - cy)) / dy if abs(dy) > 1e-12 else 1e30
        outer_t = min(value for value in (tx, ty) if value > 0)
        outer.append((cx + dx * outer_t, cy + dy * outer_t))

        lo, hi = 0.0, outer_t
        for _ in range(64):
            mid = (lo + hi) * 0.5
            if _point_in_polygon(cx + dx * mid, cy + dy * mid, hole):
                lo = mid
            else:
                hi = mid
        inner.append((cx + dx * lo, cy + dy * lo))
    return outer, inner


def _triangle_quality_2d(a, b, c):
    lengths = (
        math.dist(a, b),
        math.dist(b, c),
        math.dist(c, a),
    )
    if min(lengths) <= 1e-14:
        return 0.0, float("inf")
    angles = []
    for point, first, second in ((a, b, c), (b, c, a), (c, a, b)):
        ux, uy = first[0] - point[0], first[1] - point[1]
        vx, vy = second[0] - point[0], second[1] - point[1]
        denominator = math.hypot(ux, uy) * math.hypot(vx, vy)
        cosine = (ux * vx + uy * vy) / denominator
        angles.append(math.degrees(math.acos(max(-1.0, min(1.0, cosine)))))
    return min(angles), max(lengths) / min(lengths)


def _quality_shell_faces(outer_loop, hole_loop):
    """Extrude an annulus while pinning the better cap diagonal per segment."""
    count = len(hole_loop)
    if len(outer_loop) != count:
        raise ValueError("annulus loops must have the same vertex count")
    faces, materials = [], []
    for index in range(count):
        nxt = (index + 1) % count
        oi, oj = outer_loop[index], outer_loop[nxt]
        hi, hj = hole_loop[index], hole_loop[nxt]
        first = (
            _triangle_quality_2d(oi, oj, hj),
            _triangle_quality_2d(oi, hj, hi),
        )
        second = (
            _triangle_quality_2d(oi, oj, hi),
            _triangle_quality_2d(oj, hj, hi),
        )
        first_min = min(metric[0] for metric in first)
        second_min = min(metric[0] for metric in second)
        if first_min >= second_min:
            faces.extend((
                (index, nxt, count + nxt),
                (index, count + nxt, count + index),
                (3 * count + nxt, 3 * count + index, 2 * count + index),
                (3 * count + nxt, 2 * count + index, 2 * count + nxt),
            ))
        else:
            faces.extend((
                (index, nxt, count + index),
                (nxt, count + nxt, count + index),
                (3 * count + nxt, 3 * count + index, 2 * count + nxt),
                (3 * count + index, 2 * count + index, 2 * count + nxt),
            ))
        faces.extend((
            (nxt, index, 2 * count + index, 2 * count + nxt),
            (count + index, count + nxt, 3 * count + nxt, 3 * count + index),
        ))
        materials.extend((0, 0, 1, 1, 1, 1))
    return faces, materials


def _circle(cx, radius, segments=16):
    return [
        (
            cx + radius * math.cos(2 * math.pi * index / segments),
            radius * math.sin(2 * math.pi * index / segments),
        )
        for index in range(segments)
    ]


def _rounded_rect(cx, width, height, radius, steps=4):
    half_x = width * 0.5 - radius
    half_y = height * 0.5 - radius
    points = []
    for ox, oy, start, end in (
        (half_x, half_y, 0, math.pi / 2),
        (-half_x, half_y, math.pi / 2, math.pi),
        (-half_x, -half_y, math.pi, 3 * math.pi / 2),
        (half_x, -half_y, 3 * math.pi / 2, 2 * math.pi),
    ):
        for step in range(steps):
            angle = start + (end - start) * step / steps
            points.append(
                (
                    cx + ox + radius * math.cos(angle),
                    oy + radius * math.sin(angle),
                )
            )
    return points


def _capsule(center, width, length, steps=16):
    radius = width * 0.5
    straight = length - width
    top = center + straight * 0.5
    bottom = center - straight * 0.5
    points = []
    for step in range(steps + 1):
        angle = math.pi * step / steps
        points.append((radius * math.cos(angle), top + radius * math.sin(angle)))
    for step in range(steps + 1):
        angle = math.pi + math.pi * step / steps
        points.append((radius * math.cos(angle), bottom + radius * math.sin(angle)))
    return points


def _append_component(master_vertices, master_faces, master_materials, vertices, faces, material_indices):
    offset = len(master_vertices)
    master_vertices.extend(vertices)
    master_faces.extend(tuple(index + offset for index in face) for face in faces)
    master_materials.extend(material_indices)


def _shell_faces(count):
    faces = []
    for index in range(count):
        nxt = (index + 1) % count
        faces.extend(
            (
                (index, nxt, count + nxt, count + index),
                (3 * count + nxt, 3 * count + index, 2 * count + index, 2 * count + nxt),
                (nxt, index, 2 * count + index, 2 * count + nxt),
                (count + index, count + nxt, 3 * count + nxt, 3 * count + index),
            )
        )
    return faces


def _refine_main_rail_edges(bm, target_length):
    """Bound straight main-shell rails without touching disconnected local cells."""
    bm.normal_update()
    if any(len(face.verts) > 4 for face in bm.faces):
        raise RuntimeError("body rail refinement expects n-gon-free authored input")

    bm.verts.ensure_lookup_table()
    seed = bm.verts[0]
    seed_position = seed.co.copy()
    component = {seed}
    queue = [seed]
    while queue:
        vertex = queue.pop()
        for edge in vertex.link_edges:
            other = edge.other_vert(vertex)
            if other not in component:
                component.add(other)
                queue.append(other)

    groups = {}
    for edge in list(bm.edges):
        if edge.verts[0] not in component or edge.verts[1] not in component:
            continue
        length = edge.calc_length()
        if length <= target_length:
            continue
        cuts = math.ceil(length / target_length) - 1
        groups.setdefault(cuts, []).append(edge)

    for cuts in sorted(groups, reverse=True):
        live = [edge for edge in groups[cuts] if edge.is_valid]
        if live:
            bmesh.ops.subdivide_edges(
                bm,
                edges=live,
                cuts=cuts,
                use_grid_fill=True,
            )

    # Subdivision can replace the original BMVerts. Re-resolve the main
    # connected component before selecting depth edges.
    seed = min(bm.verts, key=lambda vertex: (vertex.co - seed_position).length_squared)
    component = {seed}
    queue = [seed]
    while queue:
        vertex = queue.pop()
        for edge in vertex.link_edges:
            other = edge.other_vert(vertex)
            if other not in component:
                component.add(other)
                queue.append(other)

    # The curved outer rail uses short Apple-profile segments across the full
    # 7.25 mm device depth. Split only those main-shell depth edges once so
    # exported corner triangles do not become long needles.
    component_depth_edges = []
    for edge in list(bm.edges):
        if edge.verts[0] not in component or edge.verts[1] not in component:
            continue
        delta = edge.verts[1].co - edge.verts[0].co
        length = delta.length
        if length > 4.0 * 0.001 and abs(delta.y) / length > 0.98:
            component_depth_edges.append(edge)
    if component_depth_edges:
        bmesh.ops.subdivide_edges(
            bm,
            edges=component_depth_edges,
            cuts=1,
            use_grid_fill=True,
        )

    bm.normal_update()
    introduced_ngons = [face for face in bm.faces if len(face.verts) > 4]
    if introduced_ngons:
        bmesh.ops.triangulate(
            bm,
            faces=introduced_ngons,
            quad_method="BEAUTY",
            ngon_method="BEAUTY",
        )
    bm.normal_update()
    # Subdivision can replace the seed BMVert. Resolve its preserved corner
    # coordinate before collecting the new straight-rail vertices.
    seed = min(bm.verts, key=lambda vertex: (vertex.co - seed_position).length_squared)
    if (seed.co - seed_position).length > 1e-9:
        raise RuntimeError("body rail subdivision lost the authored corner seed")
    component = {seed}
    queue = [seed]
    while queue:
        vertex = queue.pop()
        for edge in vertex.link_edges:
            other = edge.other_vert(vertex)
            if other not in component:
                component.add(other)
                queue.append(other)
    # Persist deliberate cap diagonals; the exporter must not choose a new
    # tessellation that reintroduces corner slivers on these thin strips.
    cap_faces = [
        face for face in bm.faces
        if all(vertex in component for vertex in face.verts)
        and abs(face.normal.y) > 0.99
    ]
    bmesh.ops.triangulate(
        bm, faces=cap_faces, quad_method="BEAUTY", ngon_method="BEAUTY"
    )
    bm.normal_update()


def build_body_mesh(
    name,
    width,
    height,
    depth,
    inner_width,
    inner_height,
    inner_radius,
    metal_material,
    dark_material,
    collection,
    corner_profile,
    *,
    segments=24,
):
    """Build the v30 runtime body as clean disconnected manifold shells."""
    mm = 0.001
    outer = _apple_outline(width, height, corner_profile, segments)
    inner = _rounded_outline(inner_width, inner_height, inner_radius, segments)
    count = len(outer)
    if count != 4 * (segments + 1):
        raise RuntimeError("unexpected Apple outline vertex count")

    vertices = []
    for y in (-depth * 0.5, depth * 0.5):
        vertices.extend((x, y, z) for x, z in outer)
        vertices.extend((x, y, z) for x, z in inner)

    outer_front = 0
    inner_front = count
    outer_back = 2 * count
    inner_back = 3 * count
    faces, material_indices = [], []

    quarter_count = segments + 1
    left_side_edge = 2 * quarter_count - 1
    bottom_left_edge = 3 * quarter_count - 2
    bottom_flat_edge = 3 * quarter_count - 1
    bottom_right_edge_1 = 3 * quarter_count
    bottom_right_edge_2 = 3 * quarter_count + 1
    right_side_edge = 4 * quarter_count - 1
    bottom_edges = (bottom_left_edge, bottom_flat_edge, bottom_right_edge_1, bottom_right_edge_2)
    replace = {left_side_edge, *bottom_edges, right_side_edge}
    for index in range(count):
        nxt = (index + 1) % count
        if index not in replace:
            faces.append((outer_front + index, outer_front + nxt, outer_back + nxt, outer_back + index))
            material_indices.append(0)
        faces.append((inner_front + nxt, inner_front + index, inner_back + index, inner_back + nxt))
        material_indices.append(0)
        faces.append((outer_front + nxt, outer_front + index, inner_front + index, inner_front + nxt))
        material_indices.append(0)
        faces.append((outer_back + index, outer_back + nxt, inner_back + nxt, inner_back + index))
        material_indices.append(0)

    def add_edge_tray(edge_index, inset_depth):
        nxt = (edge_index + 1) % count
        p0 = Vector((outer[edge_index][0], 0, outer[edge_index][1]))
        p1 = Vector((outer[nxt][0], 0, outer[nxt][1]))
        tangent = (p1 - p0).normalized()
        normal = Vector((tangent.z, 0, -tangent.x)).normalized()
        if normal.dot((p0 + p1) * 0.5) < 0:
            normal = -normal
        inward = -normal * inset_depth
        source = (
            outer_front + edge_index,
            outer_front + nxt,
            outer_back + nxt,
            outer_back + edge_index,
        )
        inset = []
        for vertex_index in source:
            coord = Vector(vertices[vertex_index]) + inward
            inset.append(len(vertices))
            vertices.append(tuple(coord))
        for local_index, vertex_index in enumerate(source):
            next_local = (local_index + 1) % 4
            faces.append((vertex_index, source[next_local], inset[next_local], inset[local_index]))
            material_indices.append(1)
        faces.append(tuple(reversed(inset)))
        material_indices.append(1)

    for edge in bottom_edges:
        add_edge_tray(edge, 1.60 * mm)
    for edge in (left_side_edge, right_side_edge):
        add_edge_tray(edge, 0.60 * mm)

    master_vertices = list(vertices)
    master_faces = list(faces)
    master_materials = list(material_indices)

    y0, y1 = -depth * 0.5, depth * 0.5
    bottom_z = -height * 0.5

    def flat_bottom_cell(xa, xb, hole, thickness=0.01 * mm):
        outer_loop, hole_loop = _uniform_annulus_loops(xa, xb, y0, y1, hole, segments=8, pin_corners=True)
        verts = []
        for z in (bottom_z, bottom_z + thickness):
            verts.extend((x, y, z) for x, y in outer_loop)
            verts.extend((x, y, z) for x, y in hole_loop)
        fs, mats = _quality_shell_faces(outer_loop, hole_loop)
        _append_component(master_vertices, master_faces, master_materials, verts, fs, mats)

    def curved_bottom_cell(xa, xb, hole, thickness=0.01 * mm):
        outer_loop, hole_loop = _uniform_annulus_loops(xa, xb, y0, y1, hole, segments=8, pin_corners=True)

        def surface(point, back=False):
            x, y = point
            z, normal = apple_bottom_surface(x, width, height, corner_profile)
            coord = Vector((x, y, z))
            if back:
                coord -= normal * thickness
            return tuple(coord)

        verts = (
            [surface(point, False) for point in outer_loop]
            + [surface(point, False) for point in hole_loop]
            + [surface(point, True) for point in outer_loop]
            + [surface(point, True) for point in hole_loop]
        )
        fs, mats = _quality_shell_faces(outer_loop, hole_loop)
        _append_component(master_vertices, master_faces, master_materials, verts, fs, mats)

    def side_cell(side, zlo, zhi, hole, thickness=0.01 * mm):
        outer_x = -width * 0.5 if side == "L" else width * 0.5
        inward = 1 if side == "L" else -1
        outer_loop, hole_loop = _uniform_annulus_loops(y0, y1, zlo, zhi, hole, segments=44)
        verts = []
        for x in (outer_x, outer_x + inward * thickness):
            verts.extend((x, y, z) for y, z in outer_loop)
            verts.extend((x, y, z) for y, z in hole_loop)
        fs, mats = _quality_shell_faces(outer_loop, hole_loop)
        _append_component(master_vertices, master_faces, master_materials, verts, fs, mats)

    def side_fill(side, zlo, zhi, thickness=0.01 * mm):
        x = -width * 0.5 if side == "L" else width * 0.5
        inner_x = x + (thickness if side == "L" else -thickness)
        verts = [
            (x, y0, zlo), (x, y1, zlo), (x, y1, zhi), (x, y0, zhi),
            (inner_x, y0, zlo), (inner_x, y1, zlo), (inner_x, y1, zhi), (inner_x, y0, zhi),
        ]
        fs = [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
        mats = [0,1,1,1,1,1]
        _append_component(master_vertices, master_faces, master_materials, verts, fs, mats)

    for xa, xb, hole in (
        (-15.0*mm, -12.6325*mm, _circle(-13.760*mm, .675*mm, segments=64)),
        (-12.6325*mm, -9.215*mm, _circle(-11.505*mm, .675*mm, segments=64)),
        (-9.215*mm, -5.2*mm, _circle(-6.925*mm, .78*mm, segments=64)),
        (-5.2*mm, 5.2*mm, _rounded_rect(0, 8.99*mm, 3.00*mm, .91*mm, steps=16)),
        (5.2*mm, 9.215*mm, _circle(6.925*mm, .78*mm, segments=64)),
        (9.215*mm, 12.6325*mm, _circle(11.505*mm, .675*mm, segments=64)),
        (12.6325*mm, 15.0*mm, _circle(13.760*mm, .675*mm, segments=64)),
    ):
        flat_bottom_cell(xa, xb, hole)

    left_curve_start = outer[bottom_left_edge][0]
    right_curve_end = outer[(bottom_right_edge_2 + 1) % count][0]
    curved_bottom_cell(left_curve_start, -15.0*mm, _circle(-16.015*mm, .675*mm, segments=64))
    curved_bottom_cell(15.0*mm, 17.1425*mm, _circle(16.015*mm, .675*mm, segments=64))
    curved_bottom_cell(17.1425*mm, 19.3975*mm, _circle(18.270*mm, .675*mm, segments=64))
    curved_bottom_cell(19.3975*mm, right_curve_end, _circle(20.525*mm, .675*mm, segments=64))

    flat_lo, flat_hi = -55.575*mm, 55.575*mm
    side_fill("L", flat_lo, 4*mm)
    side_cell("L", 4*mm, 19.47*mm, _capsule(12.37*mm, 3.04*mm, 11.76*mm, steps=64))
    side_cell("L", 19.47*mm, 33.645*mm, _capsule(26.57*mm, 3.04*mm, 11.76*mm, steps=64))
    side_cell("L", 33.645*mm, 48*mm, _capsule(40.72*mm, 3.04*mm, 7.46*mm, steps=64))
    side_fill("L", 48*mm, flat_hi)

    side_fill("R", flat_lo, -36*mm)
    side_cell("R", -36*mm, -10*mm, _capsule(-23.40*mm, 3.41*mm, 17.66*mm, steps=64))
    side_fill("R", -10*mm, 6*mm)
    side_cell("R", 6*mm, 32*mm, _capsule(19.48*mm, 3.04*mm, 18.26*mm, steps=64))
    side_fill("R", 32*mm, flat_hi)

    mesh = bpy.data.meshes.new(name + "_MESH")
    mesh.from_pydata(master_vertices, [], master_faces)
    mesh.update()
    mesh.materials.append(metal_material)
    mesh.materials.append(dark_material)
    for index, polygon in enumerate(mesh.polygons):
        polygon.material_index = master_materials[index]

    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    _refine_main_rail_edges(bm, 12.0 * mm)
    # Only the hidden lower inner-wall segment over USB needs rear clearance.
    # Adjust subdivided inner-contour stations, not the exposed Apple outline,
    # outer bottom cells or the unrelated mic/speaker aperture geometry.
    inner_bottom_z = -inner_height * 0.5
    for vertex in bm.verts:
        x, y, z = vertex.co
        if abs(z - inner_bottom_z) <= 1e-7 and abs(x) < 16.0 * mm:
            u = abs(x) / (16.0 * mm)
            vertex.co.z += 0.90 * mm * (1.0 - u * u) ** 2
    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()

    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    return obj


def _apple_outline(width, height, corner_profile, segments):
    half_w, half_h = width * 0.5, height * 0.5
    quarter = [corner_profile(step / segments) for step in range(segments + 1)]
    return (
        [(half_w - dx, half_h - dz) for dx, dz in quarter]
        + [(-half_w + dx, half_h - dz) for dx, dz in reversed(quarter)]
        + [(-half_w + dx, -half_h + dz) for dx, dz in quarter]
        + [(half_w - dx, -half_h + dz) for dx, dz in reversed(quarter)]
    )


def _rounded_outline(width, height, radius, segments):
    half_w, half_h = width * 0.5, height * 0.5
    cx, cz = half_w - radius, half_h - radius
    quarter = [
        (radius * math.sin(math.pi * 0.5 * step / segments),
         radius * math.cos(math.pi * 0.5 * step / segments))
        for step in range(segments + 1)
    ]
    return (
        [(cx + dx, cz + dz) for dx, dz in reversed(quarter)]
        + [(-cx - dx, cz + dz) for dx, dz in quarter]
        + [(-cx - dx, -cz - dz) for dx, dz in reversed(quarter)]
        + [(cx + dx, -cz - dz) for dx, dz in quarter]
    )


def apple_bottom_surface(x, width, height, corner_profile):
    extent = 19.23 * 0.001
    abs_x = abs(x)
    flat = width * 0.5 - extent
    if abs_x <= flat + 1e-12:
        return -height * 0.5, Vector((0, 0, -1))

    lo, hi = 0.0, 1.0
    for _ in range(64):
        t = (lo + hi) * 0.5
        dx, dz = corner_profile(t)
        px = width * 0.5 - dx
        if px > abs_x:
            lo = t
        else:
            hi = t
    t = (lo + hi) * 0.5
    dx, dz = corner_profile(t)
    z = -height * 0.5 + dz

    epsilon = 1e-5
    t0, t1 = max(0, t - epsilon), min(1, t + epsilon)
    dx0, dz0 = corner_profile(t0)
    dx1, dz1 = corner_profile(t1)
    x0, z0 = width * 0.5 - dx0, -height * 0.5 + dz0
    x1, z1 = width * 0.5 - dx1, -height * 0.5 + dz1
    tangent = Vector((x1 - x0, 0, z1 - z0)).normalized()
    normal = Vector((tangent.z, 0, -tangent.x)).normalized()
    if normal.z > 0:
        normal = -normal
    if x < 0:
        normal.x = -normal.x
    return z, normal
