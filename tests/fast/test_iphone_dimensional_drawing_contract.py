import json
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


def accessor_vec3(doc, blob, accessor_index):
    accessor = doc["accessors"][accessor_index]
    view = doc["bufferViews"][accessor["bufferView"]]
    offset = view.get("byteOffset", 0) + accessor.get("byteOffset", 0)
    stride = view.get("byteStride", 12)
    return [
        struct.unpack_from("<fff", blob, offset + index * stride)
        for index in range(accessor["count"])
    ]


def rotate_quaternion(point, quaternion):
    x, y, z = point
    qx, qy, qz, qw = quaternion
    # Unit-quaternion rotation matrix, glTF xyzw convention.
    return (
        (1 - 2 * (qy*qy + qz*qz)) * x + 2 * (qx*qy - qz*qw) * y + 2 * (qx*qz + qy*qw) * z,
        2 * (qx*qy + qz*qw) * x + (1 - 2 * (qx*qx + qz*qz)) * y + 2 * (qy*qz - qx*qw) * z,
        2 * (qx*qz - qy*qw) * x + 2 * (qy*qz + qx*qw) * y + (1 - 2 * (qx*qx + qy*qy)) * z,
    )


def node_world_bounds_mm(doc, blob, name):
    node = next(node for node in doc["nodes"] if node.get("name") == name)
    mesh = doc["meshes"][node["mesh"]]
    translation = node.get("translation", [0, 0, 0])
    rotation = node.get("rotation", [0, 0, 0, 1])
    scale = node.get("scale", [1, 1, 1])
    points = []
    for primitive in mesh["primitives"]:
        for point in accessor_vec3(doc, blob, primitive["attributes"]["POSITION"]):
            scaled = tuple(point[index] * scale[index] for index in range(3))
            rotated = rotate_quaternion(scaled, rotation)
            points.append(tuple((rotated[index] + translation[index]) * 1000.0 for index in range(3)))
    return (
        tuple(min(point[index] for point in points) for index in range(3)),
        tuple(max(point[index] for point in points) for index in range(3)),
    )


class IPhoneDimensionalDrawingContractTests(unittest.TestCase):
    def test_rear_camera_depth_matches_apple_detail_d(self):
        """Apple iPhone 17 Dimensional Drawings: back glass→plateau 1.78 mm, →camera glass 3.45 mm."""
        doc, blob = read_glb(GLB)
        back_min, _ = node_world_bounds_mm(doc, blob, "BACK_GLASS")
        housing_min, _ = node_world_bounds_mm(doc, blob, "CAMERA_HOUSING")
        glass_min, _ = node_world_bounds_mm(doc, blob, "CAMERA_1_GLASS")

        plateau_protrusion = back_min[2] - housing_min[2]
        camera_glass_protrusion = back_min[2] - glass_min[2]

        self.assertAlmostEqual(plateau_protrusion, 1.78, delta=0.03)
        self.assertAlmostEqual(camera_glass_protrusion, 3.45, delta=0.03)

    def test_bottom_ports_and_screws_match_apple_detail_c(self):
        """Apple Detail C: 3 mic + 5 speaker Ø1.35 ports and two Ø1.50 screws."""
        doc, blob = read_glb(GLB)
        width_mm = 71.45

        mic_names = [f"BOTTOM_MIC_APERTURE_{index:02d}" for index in range(1, 4)]
        speaker_names = [f"BOTTOM_SPEAKER_APERTURE_{index:02d}" for index in range(1, 6)]
        node_names = {node.get("name") for node in doc["nodes"]}
        self.assertTrue(all(name in node_names for name in mic_names + speaker_names))
        self.assertNotIn("BOTTOM_SPEAKER_APERTURE_06", node_names)

        expected_mic_from_left = [19.71, 21.965, 24.22]
        expected_speaker_from_left = [47.23, 49.485, 51.74, 53.995, 56.25]

        for name, expected in zip(mic_names + speaker_names, expected_mic_from_left + expected_speaker_from_left):
            mins, maxs = node_world_bounds_mm(doc, blob, name)
            center_from_left = width_mm * 0.5 + (mins[0] + maxs[0]) * 0.5
            diameter = maxs[0] - mins[0]
            self.assertAlmostEqual(center_from_left, expected, delta=0.03, msg=name)
            self.assertAlmostEqual(diameter, 1.35, delta=0.03, msg=name)

        for name, expected in (("BOTTOM_SCREW_L", 28.80), ("BOTTOM_SCREW_R", 42.65)):
            mins, maxs = node_world_bounds_mm(doc, blob, name)
            center_from_left = width_mm * 0.5 + (mins[0] + maxs[0]) * 0.5
            diameter = maxs[0] - mins[0]
            self.assertAlmostEqual(center_from_left, expected, delta=0.03, msg=name)
            self.assertAlmostEqual(diameter, 1.50, delta=0.03, msg=name)

    def test_side_controls_match_apple_elevations(self):
        """Apple side elevations: exact center datums, visible lengths and face widths."""
        doc, blob = read_glb(GLB)
        product_half_height_mm = 149.61 * 0.5
        expected = {
            "ACTION_BUTTON": (34.08, 6.90, 2.66),
            "VOL_UP": (48.23, 11.20, 2.66),
            "VOL_DOWN": (62.43, 11.20, 2.66),
            "SIDE_BUTTON": (55.32, 17.70, 2.66),
            "CAMERA_CONTROL": (98.20, 17.10, 3.03),
        }

        for name, (expected_from_top, expected_length, expected_face_width) in expected.items():
            mins, maxs = node_world_bounds_mm(doc, blob, name)
            center_y = (mins[1] + maxs[1]) * 0.5
            center_from_top = product_half_height_mm - center_y
            length = maxs[1] - mins[1]
            face_width = maxs[2] - mins[2]
            self.assertAlmostEqual(center_from_top, expected_from_top, delta=0.03, msg=f"{name} center")
            self.assertAlmostEqual(length, expected_length, delta=0.03, msg=f"{name} length")
            self.assertAlmostEqual(face_width, expected_face_width, delta=0.03, msg=f"{name} face width")

    def test_rear_microphone_matches_apple_detail_d(self):
        """Apple Detail D: rear mic center 20.54 × 22.48 mm from product left/top, Ø1.00."""
        doc, blob = read_glb(GLB)
        mins, maxs = node_world_bounds_mm(doc, blob, "REAR_MIC")
        center_x = (mins[0] + maxs[0]) * 0.5
        center_y = (mins[1] + maxs[1]) * 0.5
        from_left = 71.45 * 0.5 - center_x
        from_top = 149.61 * 0.5 - center_y
        diameter = maxs[0] - mins[0]

        self.assertAlmostEqual(from_left, 20.54, delta=0.03)
        self.assertAlmostEqual(from_top, 22.48, delta=0.03)
        self.assertAlmostEqual(diameter, 1.00, delta=0.03)


if __name__ == "__main__":
    unittest.main()
