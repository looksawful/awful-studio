"""Deterministic device-delivery provenance and stale-artifact checks."""
from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path
from typing import Iterable


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def source_fingerprint(root: Path, relative_paths: Iterable[str]) -> tuple[str, dict[str, str]]:
    hashes: dict[str, str] = {}
    for relative in sorted(relative_paths):
        path = root / relative
        if not path.is_file():
            raise FileNotFoundError(path)
        hashes[relative] = sha256_file(path)
    canonical = json.dumps(hashes, sort_keys=True, separators=(',', ':')).encode('utf-8')
    return hashlib.sha256(canonical).hexdigest(), hashes


def load_manifest(path: Path) -> dict:
    data = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(data, dict):
        raise ValueError(f'Device delivery manifest must be an object: {path}')
    return data


def delivery_matches(manifest: dict, asset_id: str, stage: str, source_revision: str) -> bool:
    return (
        manifest.get('asset_id') == asset_id
        and manifest.get('stage') == stage
        and manifest.get('source_revision') == source_revision
    )


def verify_manifest(root: Path, manifest: dict) -> list[str]:
    errors: list[str] = []
    source_files = manifest.get('source_files')
    if not isinstance(source_files, dict) or not source_files:
        return ['source_files missing or empty']
    for relative, expected in sorted(source_files.items()):
        path = root / relative
        if not path.is_file():
            errors.append(f'missing source file: {relative}')
        elif sha256_file(path) != expected:
            errors.append(f'source hash mismatch: {relative}')
    fingerprint, _ = source_fingerprint(root, source_files.keys())
    if manifest.get('source_revision') != fingerprint:
        errors.append('source_revision mismatch')
    artifacts = manifest.get('artifacts')
    if not isinstance(artifacts, dict) or not artifacts:
        errors.append('artifacts missing or empty')
        return errors
    for name, item in sorted(artifacts.items()):
        if not isinstance(item, dict) or 'path' not in item or 'sha256' not in item:
            errors.append(f'invalid artifact entry: {name}')
            continue
        path = root / item['path']
        if not path.is_file():
            errors.append(f'missing artifact: {item["path"]}')
        elif sha256_file(path) != item['sha256']:
            errors.append(f'artifact hash mismatch: {name}')
    return errors


def load_glb_document(path: Path) -> dict:
    raw = path.read_bytes()
    if len(raw) < 20 or raw[:4] != b'glTF':
        raise ValueError(f'Invalid GLB header: {path}')
    version, total_length = struct.unpack_from('<II', raw, 4)
    if version != 2 or total_length != len(raw):
        raise ValueError(f'Invalid GLB envelope: {path}')
    json_length, json_type = struct.unpack_from('<II', raw, 12)
    if json_type != 0x4E4F534A or 20 + json_length > len(raw):
        raise ValueError(f'Invalid GLB JSON chunk: {path}')
    payload = raw[20:20 + json_length].decode('utf-8').rstrip(' \t\r\n\0')
    document = json.loads(payload)
    if not isinstance(document, dict):
        raise ValueError(f'GLB JSON document must be an object: {path}')
    return document


def verify_glb_provenance(path: Path, manifest: dict) -> list[str]:
    try:
        document = load_glb_document(path)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        return [str(error)]

    root_name = manifest.get('root')
    root_node = next(
        (node for node in document.get('nodes', []) if node.get('name') == root_name),
        None,
    )
    if root_node is None:
        return [f'GLB root node missing: {root_name}']

    extras = root_node.get('extras')
    if not isinstance(extras, dict):
        return [f'GLB root extras missing: {root_name}']

    expected = {
        'delivery_version': manifest.get('version'),
        'delivery_stage': manifest.get('stage'),
        'delivery_source_revision': manifest.get('source_revision'),
        'delivery_source_commit': manifest.get('source_commit'),
    }
    errors: list[str] = []
    for key, value in expected.items():
        if extras.get(key) != value:
            errors.append(f'GLB provenance mismatch: {key}')
    return errors


def _glb_triangle_count(document: dict) -> int:
    accessors = document.get('accessors', [])
    triangles = 0
    for mesh in document.get('meshes', []):
        for primitive in mesh.get('primitives', []):
            if primitive.get('mode', 4) != 4:
                continue
            accessor_index = primitive.get('indices')
            if accessor_index is None:
                accessor_index = primitive.get('attributes', {}).get('POSITION')
            if accessor_index is None or accessor_index < 0 or accessor_index >= len(accessors):
                raise ValueError('GLB triangle primitive is missing a valid accessor')
            triangles += int(accessors[accessor_index].get('count', 0)) // 3
    return triangles


def verify_glb_round_trip(path: Path, manifest: dict) -> list[str]:
    try:
        document = load_glb_document(path)
        triangle_count = _glb_triangle_count(document)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        return [str(error)]

    qa = manifest.get('glb_qa')
    if not isinstance(qa, dict) or not qa:
        return ['glb_qa missing or empty']

    errors: list[str] = []
    node_names = {node.get('name') for node in document.get('nodes', []) if node.get('name')}
    required_nodes = set(qa.get('required_nodes', []))
    missing_nodes = sorted(required_nodes - node_names)
    if missing_nodes:
        errors.append(f'GLB required nodes missing: {", ".join(missing_nodes)}')

    expected_materials = set(manifest.get('materials', []))
    actual_materials = {
        material.get('name')
        for material in document.get('materials', [])
        if material.get('name')
    }
    if actual_materials != expected_materials:
        errors.append('GLB material IDs mismatch')

    if len(document.get('nodes', [])) != qa.get('node_count'):
        errors.append('GLB node count mismatch')
    if len(document.get('materials', [])) != qa.get('material_count'):
        errors.append('GLB material count mismatch')
    if triangle_count != qa.get('triangle_count'):
        errors.append('GLB triangle count mismatch')

    try:
        actual_bounds = _glb_runtime_bounds_mm(document)
    except ValueError as error:
        errors.append(str(error))
        return errors
    expected_bounds = qa.get('runtime_bounds_mm')
    if (
        not isinstance(expected_bounds, list)
        or len(expected_bounds) != 3
        or any(abs(float(actual) - float(expected)) > 0.01
               for actual, expected in zip(actual_bounds, expected_bounds))
    ):
        errors.append('GLB runtime bounds mismatch')

    expected_backing = qa.get('camera_backing_protrusion_mm')
    if expected_backing is not None:
        try:
            actual_backing = _iphone_camera_backing_protrusion_mm(document)
        except ValueError as error:
            errors.append(str(error))
        else:
            if abs(actual_backing - float(expected_backing)) > 0.01:
                errors.append('GLB camera backing protrusion mismatch')
    return errors


def _matrix_multiply(left, right):
    return tuple(
        tuple(sum(left[row][index] * right[index][column] for index in range(4))
              for column in range(4))
        for row in range(4)
    )


def _node_local_matrix(node: dict):
    if 'matrix' in node:
        values = node['matrix']
        if len(values) != 16:
            raise ValueError('GLB node matrix must contain 16 values')
        return tuple(
            tuple(float(values[column * 4 + row]) for column in range(4))
            for row in range(4)
        )

    tx, ty, tz = (list(node.get('translation', [0.0, 0.0, 0.0])) + [0.0, 0.0, 0.0])[:3]
    sx, sy, sz = (list(node.get('scale', [1.0, 1.0, 1.0])) + [1.0, 1.0, 1.0])[:3]
    qx, qy, qz, qw = (list(node.get('rotation', [0.0, 0.0, 0.0, 1.0])) + [0.0, 0.0, 0.0, 1.0])[:4]
    norm = (qx * qx + qy * qy + qz * qz + qw * qw) ** 0.5
    if norm == 0:
        raise ValueError('GLB node quaternion has zero length')
    qx, qy, qz, qw = (value / norm for value in (qx, qy, qz, qw))

    xx, yy, zz = qx * qx, qy * qy, qz * qz
    xy, xz, yz = qx * qy, qx * qz, qy * qz
    xw, yw, zw = qx * qw, qy * qw, qz * qw
    return (
        ((1 - 2 * (yy + zz)) * sx, (2 * (xy - zw)) * sy, (2 * (xz + yw)) * sz, float(tx)),
        ((2 * (xy + zw)) * sx, (1 - 2 * (xx + zz)) * sy, (2 * (yz - xw)) * sz, float(ty)),
        ((2 * (xz - yw)) * sx, (2 * (yz + xw)) * sy, (1 - 2 * (xx + yy)) * sz, float(tz)),
        (0.0, 0.0, 0.0, 1.0),
    )


def _world_matrices(document: dict):
    nodes = document.get('nodes', [])
    parents: dict[int, int] = {}
    for parent_index, node in enumerate(nodes):
        for child_index in node.get('children', []):
            parents[child_index] = parent_index

    cache = {}
    visiting = set()

    def resolve(index: int):
        if index in cache:
            return cache[index]
        if index in visiting:
            raise ValueError('GLB node hierarchy contains a cycle')
        if index < 0 or index >= len(nodes):
            raise ValueError(f'GLB node index out of range: {index}')
        visiting.add(index)
        local = _node_local_matrix(nodes[index])
        parent = parents.get(index)
        world = local if parent is None else _matrix_multiply(resolve(parent), local)
        visiting.remove(index)
        cache[index] = world
        return world

    return [resolve(index) for index in range(len(nodes))]


def _transform_point(matrix, point):
    x, y, z = point
    return (
        matrix[0][0] * x + matrix[0][1] * y + matrix[0][2] * z + matrix[0][3],
        matrix[1][0] * x + matrix[1][1] * y + matrix[1][2] * z + matrix[1][3],
        matrix[2][0] * x + matrix[2][1] * y + matrix[2][2] * z + matrix[2][3],
    )


def _normalize_accessor_component(value: float, component_type: int) -> float:
    if component_type == 5120:
        return max(float(value) / 127.0, -1.0)
    if component_type == 5121:
        return float(value) / 255.0
    if component_type == 5122:
        return max(float(value) / 32767.0, -1.0)
    if component_type == 5123:
        return float(value) / 65535.0
    return float(value)


def _accessor_bounds(accessor: dict):
    minimum = accessor.get('min')
    maximum = accessor.get('max')
    if not isinstance(minimum, list) or not isinstance(maximum, list) or len(minimum) < 3 or len(maximum) < 3:
        raise ValueError('GLB POSITION accessor is missing min/max bounds')
    if accessor.get('normalized'):
        component_type = accessor.get('componentType')
        minimum = [_normalize_accessor_component(value, component_type) for value in minimum]
        maximum = [_normalize_accessor_component(value, component_type) for value in maximum]
    else:
        minimum = [float(value) for value in minimum]
        maximum = [float(value) for value in maximum]
    return minimum, maximum


def _node_mesh_bounds(document: dict, world_matrices, node_index: int):
    nodes = document.get('nodes', [])
    meshes = document.get('meshes', [])
    accessors = document.get('accessors', [])
    node = nodes[node_index]
    mesh_index = node.get('mesh')
    if mesh_index is None:
        return None
    if mesh_index < 0 or mesh_index >= len(meshes):
        raise ValueError(f'GLB mesh index out of range: {mesh_index}')

    points = []
    for primitive in meshes[mesh_index].get('primitives', []):
        accessor_index = primitive.get('attributes', {}).get('POSITION')
        if accessor_index is None or accessor_index < 0 or accessor_index >= len(accessors):
            raise ValueError('GLB mesh primitive is missing a valid POSITION accessor')
        accessor = accessors[accessor_index]
        minimum, maximum = _accessor_bounds(accessor)
        for x in (minimum[0], maximum[0]):
            for y in (minimum[1], maximum[1]):
                for z in (minimum[2], maximum[2]):
                    points.append(_transform_point(world_matrices[node_index], (x, y, z)))

    if not points:
        return None
    minimum = tuple(min(point[axis] for point in points) for axis in range(3))
    maximum = tuple(max(point[axis] for point in points) for axis in range(3))
    return minimum, maximum


def _glb_runtime_bounds_mm(document: dict) -> list[float]:
    world = _world_matrices(document)
    bounds = [
        _node_mesh_bounds(document, world, index)
        for index in range(len(document.get('nodes', [])))
    ]
    bounds = [item for item in bounds if item is not None]
    if not bounds:
        raise ValueError('GLB has no mesh bounds')
    minimum = tuple(min(item[0][axis] for item in bounds) for axis in range(3))
    maximum = tuple(max(item[1][axis] for item in bounds) for axis in range(3))
    return [round((maximum[axis] - minimum[axis]) * 1000.0, 3) for axis in range(3)]


def _named_node_bounds(document: dict, name: str):
    nodes = document.get('nodes', [])
    index = next((index for index, node in enumerate(nodes) if node.get('name') == name), None)
    if index is None:
        raise ValueError(f'GLB node missing for geometry QA: {name}')
    bounds = _node_mesh_bounds(document, _world_matrices(document), index)
    if bounds is None:
        raise ValueError(f'GLB node has no mesh bounds: {name}')
    return bounds


def _iphone_camera_backing_protrusion_mm(document: dict) -> float:
    back_glass = _named_node_bounds(document, 'BACK_GLASS')
    backing = _named_node_bounds(document, 'CAMERA_HOUSING_SEAT')
    return round((back_glass[0][2] - backing[0][2]) * 1000.0, 4)
