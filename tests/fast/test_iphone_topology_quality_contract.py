import json
import math
import pathlib
import struct
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
GLB = ROOT / "assets/device_mockups/iphone_17/runtime/v30/iphone_17_v30_web.glb"


def read_glb(path):
    raw = path.read_bytes()
    json_len, json_type = struct.unpack_from("<II", raw, 12)
    if json_type != 0x4E4F534A:
        raise AssertionError("first GLB chunk is not JSON")
    doc = json.loads(raw[20:20 + json_len].decode("utf-8").rstrip(" \t\r\n\0"))
    offset = 20 + json_len
    bin_len, bin_type = struct.unpack_from("<II", raw, offset)
    if bin_type != 0x004E4942:
        raise AssertionError("second GLB chunk is not BIN")
    return doc, raw[offset + 8:offset + 8 + bin_len]


_COMPONENT_FORMAT = {5121: "B", 5123: "H", 5125: "I", 5126: "f"}
_COMPONENTS = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}


def accessor_values(doc, blob, accessor_index):
    accessor = doc["accessors"][accessor_index]
    view = doc["bufferViews"][accessor["bufferView"]]
    count = _COMPONENTS[accessor["type"]]
    fmt = "<" + _COMPONENT_FORMAT[accessor["componentType"]] * count
    size = struct.calcsize(fmt)
    offset = view.get("byteOffset", 0) + accessor.get("byteOffset", 0)
    stride = view.get("byteStride", size)
    return [
        struct.unpack_from(fmt, blob, offset + index * stride)
        for index in range(accessor["count"])
    ]


def _length(vector):
    return math.sqrt(sum(value * value for value in vector))


def _subtract(left, right):
    return tuple(left[index] - right[index] for index in range(3))


def _cross(left, right):
    return (
        left[1] * right[2] - left[2] * right[1],
        left[2] * right[0] - left[0] * right[2],
        left[0] * right[1] - left[1] * right[0],
    )


def triangle_metrics(points):
    edges = [
        _length(_subtract(points[(index + 1) % 3], points[index]))
        for index in range(3)
    ]
    angles = []
    for index in range(3):
        first = _subtract(points[(index + 1) % 3], points[index])
        second = _subtract(points[(index + 2) % 3], points[index])
        denominator = _length(first) * _length(second)
        if denominator <= 1e-15:
            angles.append(0.0)
            continue
        cosine = sum(first[axis] * second[axis] for axis in range(3)) / denominator
        angles.append(math.degrees(math.acos(max(-1.0, min(1.0, cosine)))))
    return min(angles), max(edges) / min(edges), max(edges) * 1000.0


def visible_cap_metrics(doc, blob, node_name, normal_axis):
    node = next(node for node in doc["nodes"] if node.get("name") == node_name)
    mesh = doc["meshes"][node["mesh"]]
    metrics = []
    for primitive in mesh["primitives"]:
        positions = accessor_values(doc, blob, primitive["attributes"]["POSITION"])
        indices = [value[0] for value in accessor_values(doc, blob, primitive["indices"])]
        for offset in range(0, len(indices), 3):
            points = [positions[indices[offset + step]] for step in range(3)]
            first = _subtract(points[1], points[0])
            second = _subtract(points[2], points[0])
            normal = _cross(first, second)
            normal_length = _length(normal)
            if normal_length <= 1e-15:
                metrics.append((0.0, float("inf"), 0.0))
                continue
            if abs(normal[normal_axis] / normal_length) < 0.9:
                continue
            metrics.append(triangle_metrics(points))
    if not metrics:
        raise AssertionError(f"{node_name} has no visible-cap triangles")
    return {
        "triangles": len(metrics),
        "min_angle_deg": min(value[0] for value in metrics),
        "max_aspect": max(value[1] for value in metrics),
        "max_edge_mm": max(value[2] for value in metrics),
    }


def material_surface_metrics(doc, blob, node_name, material_name=None, *, excluded_normal_axis=None, required_normal_axis=None, normal_threshold=0.9, centroid_axis=None, centroid_max_mm=None):
    node = next(node for node in doc["nodes"] if node.get("name") == node_name)
    mesh = doc["meshes"][node["mesh"]]
    material_names = [material.get("name") for material in doc.get("materials", [])]
    metrics = []
    for primitive in mesh["primitives"]:
        material_index = primitive.get("material")
        if material_name is not None:
            if material_index is None or material_names[material_index] != material_name:
                continue
        positions = accessor_values(doc, blob, primitive["attributes"]["POSITION"])
        indices = [value[0] for value in accessor_values(doc, blob, primitive["indices"])]
        for offset in range(0, len(indices), 3):
            points = [positions[indices[offset + step]] for step in range(3)]
            first = _subtract(points[1], points[0])
            second = _subtract(points[2], points[0])
            normal = _cross(first, second)
            normal_length = _length(normal)
            if normal_length <= 1e-15:
                metrics.append((0.0, float("inf"), 0.0))
                continue
            unit_axis = [abs(value / normal_length) for value in normal]
            if excluded_normal_axis is not None and unit_axis[excluded_normal_axis] >= normal_threshold:
                continue
            if required_normal_axis is not None and unit_axis[required_normal_axis] < normal_threshold:
                continue
            if centroid_axis is not None and centroid_max_mm is not None:
                centroid_mm = sum(point[centroid_axis] for point in points) / 3.0 * 1000.0
                if centroid_mm > centroid_max_mm:
                    continue
            metrics.append(triangle_metrics(points))
    if not metrics:
        raise AssertionError(f"{node_name}/{material_name} has no target triangles")
    return {
        "triangles": len(metrics),
        "min_angle_deg": min(value[0] for value in metrics),
        "max_aspect": max(value[1] for value in metrics),
        "max_edge_mm": max(value[2] for value in metrics),
    }


class IPhoneTopologyQualityContractTests(unittest.TestCase):
    def test_back_glass_major_caps_use_local_well_shaped_triangles(self):
        doc, blob = read_glb(GLB)
        metrics = visible_cap_metrics(doc, blob, "BACK_GLASS", normal_axis=2)

        self.assertGreaterEqual(metrics["min_angle_deg"], 5.0, metrics)
        self.assertLessEqual(metrics["max_aspect"], 10.0, metrics)
        self.assertLessEqual(metrics["max_edge_mm"], 147.61 * 0.25, metrics)

    def test_body_visible_rail_and_aperture_surfaces_use_well_shaped_triangles(self):
        doc, blob = read_glb(GLB)
        metrics = material_surface_metrics(
            doc,
            blob,
            "BODY_ALUMINUM",
            "MAT_ANODIZED_ALUMINUM",
            required_normal_axis=0,
        )

        self.assertGreaterEqual(metrics["min_angle_deg"], 5.0, metrics)
        self.assertLessEqual(metrics["max_aspect"], 10.0, metrics)

    def test_bottom_visible_cells_use_well_shaped_triangles(self):
        doc, blob = read_glb(GLB)
        metrics = material_surface_metrics(
            doc,
            blob,
            "BODY_ALUMINUM",
            "MAT_ANODIZED_ALUMINUM",
            centroid_axis=1,
            centroid_max_mm=-74.70,
        )
        self.assertGreaterEqual(metrics["min_angle_deg"], 5.0, metrics)
        self.assertLessEqual(metrics["max_aspect"], 10.0, metrics)

    def test_usb_major_visible_surfaces_use_well_shaped_triangles(self):
        doc, blob = read_glb(GLB)
        for node_name in ("USB_C_CAVITY", "USB_C_TONGUE"):
            with self.subTest(node=node_name):
                metrics = material_surface_metrics(
                    doc,
                    blob,
                    node_name,
                    required_normal_axis=1,
                    normal_threshold=0.99,
                )
                self.assertGreaterEqual(metrics["min_angle_deg"], 5.0, metrics)
                self.assertLessEqual(metrics["max_aspect"], 10.0, metrics)


if __name__ == "__main__":
    unittest.main()
