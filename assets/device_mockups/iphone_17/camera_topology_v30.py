"""Frozen Human-PASS camera silhouette and UV policy, in meters.

Bake maps are immutable production inputs, not generated during device builds.
See reference/camera_bake_v30/provenance.json for the accepted bake settings.
"""
import math
from pathlib import Path

import bmesh
import bpy


def circular_cap_topology(radius, segments, inner_ratio=0.5):
    """Return a circular boundary plus a low-valence structured triangular cap."""
    if segments < 8:
        raise ValueError("circular caps require at least 8 boundary segments")
    inner_segments = 4 if segments <= 8 else 6 if segments <= 12 else 8
    outer = [
        (
            radius * math.cos(2 * math.pi * index / segments),
            radius * math.sin(2 * math.pi * index / segments),
        )
        for index in range(segments)
    ]
    inner = [
        (
            radius * inner_ratio * math.cos(2 * math.pi * index / inner_segments),
            radius * inner_ratio * math.sin(2 * math.pi * index / inner_segments),
        )
        for index in range(inner_segments)
    ]
    points = outer + inner + [(0.0, 0.0)]
    cap = []
    outer_index = inner_index = 0
    while outer_index < segments or inner_index < inner_segments:
        outer_next = (
            (outer_index + 1) / segments
            if outer_index < segments
            else float("inf")
        )
        inner_next = (
            (inner_index + 1) / inner_segments
            if inner_index < inner_segments
            else float("inf")
        )
        outer_current = outer_index % segments
        inner_current = segments + inner_index % inner_segments
        if abs(outer_next - inner_next) < 1e-12:
            next_outer = (outer_index + 1) % segments
            next_inner = segments + (inner_index + 1) % inner_segments
            cap.append((outer_current, next_outer, next_inner))
            cap.append((outer_current, next_inner, inner_current))
            outer_index += 1
            inner_index += 1
        elif outer_next < inner_next:
            next_outer = (outer_index + 1) % segments
            cap.append((outer_current, next_outer, inner_current))
            outer_index += 1
        else:
            next_inner = segments + (inner_index + 1) % inner_segments
            cap.append((outer_current, next_inner, inner_current))
            inner_index += 1

    center = len(points) - 1
    for index in range(inner_segments):
        cap.append((
            center,
            segments + index,
            segments + (index + 1) % inner_segments,
        ))
    return points, list(range(segments)), cap


def camera_mesh(name, width, height, depth, material, collection, location, *, capsule=False):
    """Build the accepted 40-class shell, caps and deterministic bake UVs."""
    radius = width / 2
    if capsule:
        straight = height - width
        rows = []
        for step in range(11):
            angle = math.pi / 2 * (1 - step / 10)
            x, z = radius * math.cos(angle), straight / 2 + radius * math.sin(angle)
            rows.append([(0, z)] if step == 0 else [(-x, z), (x, z)])
        for step in range(11):
            angle = math.pi / 2 * step / 10
            x, z = radius * math.cos(angle), -straight / 2 - radius * math.sin(angle)
            rows.append([(0, z)] if step == 10 else [(-x, z), (x, z)])
        points = [p for row in rows for p in row]
        row_indices, offset = [], 0
        for row in rows:
            row_indices.append(list(range(offset, offset + len(row))))
            offset += len(row)
        boundary = [row[-1] for row in row_indices] + [row[0] for row in reversed(row_indices[1:-1])]
        cap = []
        for a, b in zip(row_indices, row_indices[1:]):
            if len(a) == 1:
                cap.append((a[0], b[0], b[1]))
            elif len(b) == 1:
                cap.append((a[0], b[0], a[1]))
            else:
                cap.append((a[0], b[0], b[1], a[1]))
    else:
        points, boundary, cap = circular_cap_topology(radius, 40)
    count = len(points)
    vertices = [(x, y, z) for y in (-depth / 2, depth / 2) for x, z in points]
    faces = cap + [tuple(i + count for i in reversed(face)) for face in cap]
    for i, a in enumerate(boundary):
        b = boundary[(i + 1) % len(boundary)]
        faces.append((a, b, b + count, a + count))
    mesh = bpy.data.meshes.new(name + '_MESH')
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    uv = mesh.uv_layers.new(name='UVMap').data
    for polygon in mesh.polygons:
        polygon.use_smooth = abs(polygon.normal.y) < .72
        for loop_index in polygon.loop_indices:
            co = mesh.vertices[mesh.loops[loop_index].vertex_index].co
            if abs(polygon.normal.y) > .72:
                u0 = .04 if polygon.normal.y < 0 else .54
                coord = (u0 + (co.x / width + .5) * .42, .04 + (co.z / height + .5) * .42)
            else:
                theta = (math.atan2(co.x, co.z) + math.pi) / (2 * math.pi)
                coord = (.04 + .92 * theta, .62 + .34 * (co.y / depth + .5))
            uv[loop_index].uv = coord
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    obj.location = location
    mesh.materials.append(material)
    return obj


def attach_camera_normal(material, part):
    image_path = Path(__file__).parent / 'reference' / 'camera_bake_v30' / f'{part}_40_normal.png'
    image = bpy.data.images.load(str(image_path), check_existing=True)
    image.colorspace_settings.name = 'Non-Color'
    image.pack()
    nodes, links = material.node_tree.nodes, material.node_tree.links
    texture = nodes.new('ShaderNodeTexImage')
    texture.image = image
    normal = nodes.new('ShaderNodeNormalMap')
    normal.inputs['Strength'].default_value = 1.0
    links.new(texture.outputs['Color'], normal.inputs['Color'])
    links.new(normal.outputs['Normal'], nodes.get('Principled BSDF').inputs['Normal'])
