"""Intentional display-frame topology for iPhone 17 v30."""
import math

import bmesh
import bpy


def display_frame_prism_y(
    name,
    width,
    height,
    depth,
    radius,
    material,
    collection,
    location=(0, 0, 0),
    outer_segments=24,
    inner_segments=6,
    inner_ratio=0.5,
):
    """Build sparse, quality-bounded display-frame caps without n-gons."""
    if outer_segments % inner_segments:
        raise ValueError("outer_segments must be divisible by inner_segments")
    if not 0.0 < inner_ratio < 1.0:
        raise ValueError("inner_ratio must be between zero and one")

    half_w, half_h = width * 0.5, height * 0.5
    cx, cz = half_w - radius, half_h - radius
    points = []
    point_indices = {}

    def point_index(x, z):
        key = (round(x, 12), round(z, 12))
        if key not in point_indices:
            point_indices[key] = len(points)
            points.append((x, z))
        return point_indices[key]

    xs = (-cx, 0.0, cx)
    zs = (-cz, -cz * 0.5, 0.0, cz * 0.5, cz)
    grid = {
        (x_index, z_index): point_index(x, z)
        for x_index, x in enumerate(xs)
        for z_index, z in enumerate(zs)
    }

    cap_faces = []

    # Keep the flat center intentionally coarse and balanced.
    for x_index in range(2):
        for z_index in range(4):
            cap_faces.append((
                grid[(x_index, z_index)],
                grid[(x_index + 1, z_index)],
                grid[(x_index + 1, z_index + 1)],
                grid[(x_index, z_index + 1)],
            ))

    inner_radius = radius * inner_ratio
    top_inner = [point_index(x, cz + inner_radius) for x in xs]
    top_outer = [point_index(x, half_h) for x in xs]
    bottom_inner = [point_index(x, -cz - inner_radius) for x in xs]
    bottom_outer = [point_index(x, -half_h) for x in xs]
    left_inner = [point_index(-cx - inner_radius, z) for z in zs]
    left_outer = [point_index(-half_w, z) for z in zs]
    right_inner = [point_index(cx + inner_radius, z) for z in zs]
    right_outer = [point_index(half_w, z) for z in zs]

    for x_index in range(2):
        cap_faces.append((
            grid[(x_index, 4)],
            grid[(x_index + 1, 4)],
            top_inner[x_index + 1],
            top_inner[x_index],
        ))
        cap_faces.append((
            top_inner[x_index],
            top_inner[x_index + 1],
            top_outer[x_index + 1],
            top_outer[x_index],
        ))
        cap_faces.append((
            bottom_outer[x_index],
            bottom_outer[x_index + 1],
            bottom_inner[x_index + 1],
            bottom_inner[x_index],
        ))
        cap_faces.append((
            bottom_inner[x_index],
            bottom_inner[x_index + 1],
            grid[(x_index + 1, 0)],
            grid[(x_index, 0)],
        ))

    for z_index in range(4):
        cap_faces.append((
            left_outer[z_index],
            left_inner[z_index],
            left_inner[z_index + 1],
            left_outer[z_index + 1],
        ))
        cap_faces.append((
            left_inner[z_index],
            grid[(0, z_index)],
            grid[(0, z_index + 1)],
            left_inner[z_index + 1],
        ))
        cap_faces.append((
            grid[(2, z_index)],
            right_inner[z_index],
            right_inner[z_index + 1],
            grid[(2, z_index + 1)],
        ))
        cap_faces.append((
            right_inner[z_index],
            right_outer[z_index],
            right_outer[z_index + 1],
            right_inner[z_index + 1],
        ))

    corner_specs = (
        (cx, cz, 0.0, grid[(2, 4)]),
        (-cx, cz, 90.0, grid[(0, 4)]),
        (-cx, -cz, 180.0, grid[(0, 0)]),
        (cx, -cz, 270.0, grid[(2, 0)]),
    )
    outer_arcs = []
    transition_ratio = outer_segments // inner_segments

    for corner_x, corner_z, start_degrees, center_index in corner_specs:
        outer_arc = []
        for step in range(outer_segments + 1):
            angle = math.radians(start_degrees + 90.0 * step / outer_segments)
            outer_arc.append(point_index(
                corner_x + radius * math.cos(angle),
                corner_z + radius * math.sin(angle),
            ))

        inner_arc = []
        inner_radius = radius * inner_ratio
        for step in range(inner_segments + 1):
            angle = math.radians(start_degrees + 90.0 * step / inner_segments)
            inner_arc.append(point_index(
                corner_x + inner_radius * math.cos(angle),
                corner_z + inner_radius * math.sin(angle),
            ))

        for step in range(inner_segments):
            cap_faces.append((center_index, inner_arc[step], inner_arc[step + 1]))

        for step in range(inner_segments):
            inner_a = inner_arc[step]
            inner_b = inner_arc[step + 1]
            outer_start = step * transition_ratio
            outer = outer_arc[outer_start:outer_start + transition_ratio + 1]
            midpoint = transition_ratio // 2
            for offset in range(midpoint):
                cap_faces.append((inner_a, outer[offset], outer[offset + 1]))
            cap_faces.append((inner_a, outer[midpoint], inner_b))
            for offset in range(midpoint, transition_ratio):
                cap_faces.append((inner_b, outer[offset], outer[offset + 1]))

        outer_arcs.append(outer_arc)

    boundary = []

    def extend_boundary(indices):
        for index in indices:
            if not boundary or boundary[-1] != index:
                boundary.append(index)

    extend_boundary(outer_arcs[0])
    extend_boundary((top_outer[1], top_outer[0]))
    extend_boundary(outer_arcs[1][1:])
    extend_boundary((left_outer[3], left_outer[2], left_outer[1], left_outer[0]))
    extend_boundary(outer_arcs[2][1:])
    extend_boundary((bottom_outer[1], bottom_outer[2]))
    extend_boundary(outer_arcs[3][1:])
    extend_boundary((right_outer[1], right_outer[2], right_outer[3], right_outer[4]))
    if boundary[-1] == boundary[0]:
        boundary.pop()

    count = len(points)
    verts = (
        [(x, -depth * 0.5, z) for x, z in points]
        + [(x, depth * 0.5, z) for x, z in points]
    )
    faces = list(cap_faces)
    faces.extend(
        tuple(index + count for index in reversed(face))
        for face in cap_faces
    )
    for boundary_index, first in enumerate(boundary):
        second = boundary[(boundary_index + 1) % len(boundary)]
        faces.append((first, second, second + count, first + count))

    mesh = bpy.data.meshes.new(f"{name}_MESH")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    obj.location = location
    if material:
        mesh.materials.append(material)

    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    return obj


def _rounded_outline(width, height, radius, segments):
    half_w = width * 0.5
    half_h = height * 0.5
    corner_x = half_w - radius
    corner_z = half_h - radius
    corners = (
        (corner_x, corner_z, 0.0),
        (-corner_x, corner_z, 90.0),
        (-corner_x, -corner_z, 180.0),
        (corner_x, -corner_z, 270.0),
    )
    points = []
    for center_x, center_z, start_degrees in corners:
        for step in range(segments):
            angle = math.radians(start_degrees + 90.0 * step / segments)
            points.append(
                (
                    center_x + radius * math.cos(angle),
                    center_z + radius * math.sin(angle),
                )
            )
    return points


def screen_glass_ring_y(
    name,
    outer_width,
    outer_height,
    outer_radius,
    inner_width,
    inner_height,
    inner_radius,
    depth,
    material,
    collection,
    location=(0, 0, 0),
    segments=24,
    edge_bevel=0.0,
):
    """Build the native cover-glass ring directly, without boolean caps."""
    outer = _rounded_outline(outer_width, outer_height, outer_radius, segments)
    inner = _rounded_outline(inner_width, inner_height, inner_radius, segments)
    if len(outer) != len(inner):
        raise ValueError("outer and inner screen-glass outlines must match")

    count = len(outer)
    front_outer = 0
    front_inner = count
    back_outer = count * 2
    back_inner = count * 3

    verts = (
        [(x, -depth * 0.5, z) for x, z in outer]
        + [(x, -depth * 0.5, z) for x, z in inner]
        + [(x, depth * 0.5, z) for x, z in outer]
        + [(x, depth * 0.5, z) for x, z in inner]
    )

    faces = []
    for index in range(count):
        next_index = (index + 1) % count
        # Front/back annulus.
        faces.append(
            (
                front_outer + index,
                front_outer + next_index,
                front_inner + next_index,
                front_inner + index,
            )
        )
        faces.append(
            (
                back_outer + index,
                back_inner + index,
                back_inner + next_index,
                back_outer + next_index,
            )
        )
        # Outer shell and inner active-area wall.
        faces.append(
            (
                front_outer + index,
                back_outer + index,
                back_outer + next_index,
                front_outer + next_index,
            )
        )
        faces.append(
            (
                front_inner + index,
                front_inner + next_index,
                back_inner + next_index,
                back_inner + index,
            )
        )

    mesh = bpy.data.meshes.new(f"{name}_MESH")
    mesh.from_pydata(verts, [], faces)
    mesh.update()

    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    obj.location = location
    if material:
        mesh.materials.append(material)

    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()

    if edge_bevel > 0.0:
        bevel = obj.modifiers.new("EDGE_BEVEL", "BEVEL")
        bevel.width = edge_bevel
        bevel.segments = 4
        bevel.limit_method = "ANGLE"
    return obj
