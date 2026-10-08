"""Structured rounded-rectangle cap topology for iPad Pro v6."""

import math

import bmesh
import bpy


def structured_rounded_prism_y(
    name,
    width,
    height,
    depth,
    radius,
    material,
    collection,
    location=(0, 0, 0),
    *,
    corner_rows=8,
):
    """Build rounded-rectangle caps as a bounded row/column grid."""
    if corner_rows < 2:
        raise ValueError("corner_rows must be at least 2")

    half_w, half_h = width * 0.5, height * 0.5
    cx, cz = half_w - radius, half_h - radius
    if cx <= 0.0 or cz <= 0.0:
        raise ValueError("rounded rectangle radius must fit inside width/height")

    target_step = radius
    columns = max(4, math.ceil(width / target_step))
    middle_rows = max(2, math.ceil((2.0 * cz) / target_step))

    rows = []
    for index in range(corner_rows + 1):
        offset = radius * index / corner_rows
        z = half_h - offset
        x = cx + math.sqrt(max(0.0, radius * radius - (z - cz) ** 2))
        rows.append((z, x))

    for index in range(1, middle_rows):
        z = cz - (2.0 * cz) * index / middle_rows
        rows.append((z, half_w))

    for index in range(corner_rows + 1):
        offset = radius * index / corner_rows
        z = -cz - offset
        x = cx + math.sqrt(max(0.0, radius * radius - (z + cz) ** 2))
        if rows and abs(rows[-1][0] - z) < 1e-12:
            continue
        rows.append((z, x))

    points = []
    row_indices = []
    for z, half_span in rows:
        indices = []
        for column in range(columns + 1):
            x = -half_span + (2.0 * half_span) * column / columns
            indices.append(len(points))
            points.append((x, z))
        row_indices.append(indices)

    cap_faces = []
    for row_index in range(len(row_indices) - 1):
        upper = row_indices[row_index]
        lower = row_indices[row_index + 1]
        for column in range(columns):
            cap_faces.append((
                upper[column],
                upper[column + 1],
                lower[column + 1],
                lower[column],
            ))

    boundary = []
    boundary.extend(row_indices[0])
    boundary.extend(row[-1] for row in row_indices[1:])
    boundary.extend(reversed(row_indices[-1][:-1]))
    boundary.extend(row[0] for row in reversed(row_indices[1:-1]))

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
