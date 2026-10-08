import json
import math
from pathlib import Path
import struct
import unittest

ROOT = Path(__file__).resolve().parents[2]
RUNTIME = ROOT / "assets/device_mockups/ipad_pro/runtime/v6"
GLBS = {
    "11": RUNTIME / "ipad_pro_11_m5_v6_web.glb",
    "13": RUNTIME / "ipad_pro_13_m5_v6_web.glb",
}
VISIBLE_Y_CAPS = (
    "FRONT_CAMERA_GLASS",
    "REAR_CAMERA_GLASS",
    "FLASH",
    "LIDAR",
    "REAR_MIC",
    "SMART_CONNECTOR_1",
    "SMART_CONNECTOR_2",
    "SMART_CONNECTOR_3",
)

_COMPONENT_FORMAT = {5121: "B", 5123: "H", 5125: "I", 5126: "f"}
_COMPONENTS = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}


def read_glb(path):
    raw = path.read_bytes()
    json_len, json_type = struct.unpack_from("<II", raw, 12)
    if json_type != 0x4E4F534A:
        raise AssertionError(f"{path} first GLB chunk is not JSON")
    doc = json.loads(raw[20:20 + json_len].decode("utf-8").rstrip(" \t\r\n\0"))
    offset = 20 + json_len
    bin_len, bin_type = struct.unpack_from("<II", raw, offset)
    if bin_type != 0x004E4942:
        raise AssertionError(f"{path} second GLB chunk is not BIN")
    return doc, raw[offset + 8:offset + 8 + bin_len]


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


def _subtract(left, right):
    return tuple(left[index] - right[index] for index in range(3))


def _cross(left, right):
    return (
        left[1] * right[2] - left[2] * right[1],
        left[2] * right[0] - left[0] * right[2],
        left[0] * right[1] - left[1] * right[0],
    )


def _length(vector):
    return math.sqrt(sum(value * value for value in vector))


def cap_fan_fraction(doc, blob, node_name, normal_axis=2, normal_threshold=0.9):
    node = next(node for node in doc["nodes"] if node.get("name") == node_name)
    mesh = doc["meshes"][node["mesh"]]
    groups = {}
    for primitive_index, primitive in enumerate(mesh["primitives"]):
        positions = accessor_values(doc, blob, primitive["attributes"]["POSITION"])
        indices = [value[0] for value in accessor_values(doc, blob, primitive["indices"])]
        for offset in range(0, len(indices), 3):
            triangle = indices[offset:offset + 3]
            points = [positions[index] for index in triangle]
            first = _subtract(points[1], points[0])
            second = _subtract(points[2], points[0])
            normal = _cross(first, second)
            normal_length = _length(normal)
            if normal_length <= 1e-15:
                continue
            if abs(normal[normal_axis] / normal_length) < normal_threshold:
                continue
            plane = round(sum(point[normal_axis] for point in points) / 3.0, 7)
            groups.setdefault(plane, []).append(
                tuple((primitive_index, index) for index in triangle)
            )
    if not groups:
        raise AssertionError(f"{node_name} has no visible cap triangles")

    worst = None
    for plane, triangles in groups.items():
        incidence = {}
        for triangle in triangles:
            for vertex in triangle:
                incidence[vertex] = incidence.get(vertex, 0) + 1
        candidate = {
            "plane": plane,
            "triangles": len(triangles),
            "max_vertex_incidence": max(incidence.values()),
            "fan_fraction": max(incidence.values()) / len(triangles),
        }
        if worst is None or candidate["fan_fraction"] > worst["fan_fraction"]:
            worst = candidate
    return worst


class IPadTopologyQualityContractTests(unittest.TestCase):
    def test_visible_circular_caps_do_not_collapse_into_single_vertex_fans(self):
        for size, path in GLBS.items():
            doc, blob = read_glb(path)
            for node_name in VISIBLE_Y_CAPS:
                with self.subTest(size=size, node=node_name):
                    metrics = cap_fan_fraction(doc, blob, node_name)
                    self.assertLess(metrics["fan_fraction"], 0.75, metrics)


if __name__ == "__main__":
    unittest.main()
