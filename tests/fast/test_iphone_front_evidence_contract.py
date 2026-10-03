import json
from pathlib import Path
import re
import unittest

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
GENERATOR = ROOT / "assets/device_mockups/iphone_17/generate_low_v30.py"
LEDGER = ROOT / "assets/device_mockups/iphone_17/reference/iphone_17_dimensional_ledger.json"
SCREEN = ROOT / "assets/device_mockups/iphone_17/reference/ios26_home_screen_1206x2622.png"
SCREEN_STATE = ROOT / "assets/device_mockups/iphone_17/reference/ios26_home_screen_dynamic_state_1206x2622.png"
PRESENTATION = ROOT / "preview/src/iphone-presentation.mjs"

BODY_H_MM = 149.61
SCREEN_W_MM = 66.57
SCREEN_H_MM = 144.79
BODY_H_M = BODY_H_MM / 1000.0


def ledger_reference(element: str) -> float:
    data = json.loads(LEDGER.read_text(encoding="utf-8"))
    row = next((item for item in data["dimensions"] if item["element"] == element), None)
    if row is None:
        raise AssertionError(f"missing dimensional ledger entry: {element}")
    return float(row["reference"])


def raster_dynamic_island_contract(path: Path = SCREEN) -> tuple[float, float, float]:
    image = Image.open(path).convert("L")
    left, top, right, bottom = 350, 0, 856, 180
    crop = image.crop((left, top, right, bottom))
    width, height = crop.size
    pixels = crop.load()
    seen = set()
    components = []

    for y in range(height):
        for x in range(width):
            if (x, y) in seen or pixels[x, y] >= 28:
                continue
            stack = [(x, y)]
            seen.add((x, y))
            xs, ys = [], []
            while stack:
                px, py = stack.pop()
                xs.append(px)
                ys.append(py)
                for nx, ny in ((px + 1, py), (px - 1, py), (px, py + 1), (px, py - 1)):
                    if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in seen and pixels[nx, ny] < 28:
                        seen.add((nx, ny))
                        stack.append((nx, ny))
            components.append((len(xs), min(xs), min(ys), max(xs) + 1, max(ys) + 1))

    if not components:
        raise AssertionError("could not locate Dynamic Island in screen raster")

    _, x0, y0, x1, y1 = max(components)
    center_y_px = top + (y0 + y1) / 2.0
    width_mm = (x1 - x0) / image.width * SCREEN_W_MM
    height_mm = (y1 - y0) / image.height * SCREEN_H_MM
    center_from_body_top_mm = (
        (BODY_H_MM - SCREEN_H_MM) / 2.0
        + center_y_px / image.height * SCREEN_H_MM
    )
    return width_mm, height_mm, center_from_body_top_mm


class IPhoneFrontEvidenceContractTests(unittest.TestCase):
    def test_clean_screen_preserves_artwork_and_removes_baked_island(self):
        from PIL import ImageChops
        original = Image.open(SCREEN).convert('RGB')
        clean = Image.open(SCREEN.with_name('ios26_home_screen_clean_1206x2622.png')).convert('RGB')
        self.assertEqual(clean.size, original.size)
        delta = ImageChops.difference(original, clean)
        box = delta.getbbox()
        self.assertIsNotNone(box)
        self.assertGreaterEqual(box[0], 350)
        self.assertLessEqual(box[2], 856)
        self.assertGreaterEqual(box[1], 0)
        self.assertLessEqual(box[3], 160)
        crop = clean.crop((410, 14, 798, 125))
        pixels = crop.tobytes()
        black_pixels = sum(max(pixels[i:i+3]) < 16 for i in range(0, len(pixels), 3))
        self.assertLess(black_pixels, 100, 'screen still contains a black island')

    def test_default_screen_uses_clean_artwork_while_physical_apertures_remain(self):
        source = GENERATOR.read_text(encoding="utf-8")
        self.assertIn('screen_texture_path = os.path.join(HERE, "reference", "ios26_home_screen_clean_1206x2622.png")', source)
        self.assertNotIn('screen_texture_path = os.path.join(HERE, "reference", "ios26_home_screen_dynamic_state_1206x2622.png")', source)
        self.assertIn('FRONT_SENSOR_MASK', source)
        self.assertIn('FRONT_CAMERA_MASK', source)
        self.assertNotIn('outward_prism("DYNAMIC_ISLAND"', source)

    def test_runtime_idle_mask_matches_independent_screen_reference_delta(self):
        from PIL import ImageChops
        clean = Image.open(SCREEN_STATE.with_name("ios26_home_screen_clean_1206x2622.png")).convert("RGB")
        dynamic = Image.open(SCREEN_STATE).convert("RGB")
        diff = ImageChops.difference(clean, dynamic).convert("L")
        mask = diff.point(lambda value: 255 if value > 8 else 0)
        pixels = mask.load()
        seen, components = set(), []
        for py in range(180):
            for px in range(mask.width):
                if (px, py) in seen or pixels[px, py] == 0:
                    continue
                stack, xs, ys = [(px, py)], [], []
                seen.add((px, py))
                while stack:
                    cx, cy = stack.pop()
                    xs.append(cx); ys.append(cy)
                    for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                        if 0 <= nx < mask.width and 0 <= ny < 180 and (nx, ny) not in seen and pixels[nx, ny]:
                            seen.add((nx, ny)); stack.append((nx, ny))
                components.append((len(xs), min(xs), min(ys), max(xs) + 1, max(ys) + 1))
        self.assertTrue(components)
        _, x0, y0, x1, y1 = max(components)
        bbox = (x0, y0, x1, y1)
        source = PRESENTATION.read_text(encoding="utf-8")
        match = re.search(
            r"idleDynamicIslandRaster = Object\.freeze\(\{ x: ([0-9.]+), y: ([0-9.]+), width: ([0-9.]+), height: ([0-9.]+), radius: ([0-9.]+) \}\)",
            source,
        )
        self.assertIsNotNone(match, "runtime idle Dynamic Island raster contract is missing")
        x, y, width, height, radius = map(float, match.groups())
        self.assertEqual((x, y, width, height), (bbox[0], bbox[1], bbox[2] - bbox[0], bbox[3] - bbox[1]))
        self.assertAlmostEqual(radius, height / 2.0, places=6)

    def test_dynamic_state_reference_preserves_outer_island_and_privacy_indicator_for_measurement(self):
        image = Image.open(SCREEN_STATE).convert("RGB")
        self.assertEqual(image.size, (1206, 2622))

        for point in ((500, 80), (550, 80), (705, 80), (760, 80)):
            self.assertLess(
                max(image.getpixel(point)),
                16,
                f"outer Dynamic Island missing at raster point {point}",
            )

        orange = image.getpixel((648, 97))
        self.assertGreater(orange[0], 220)
        self.assertGreater(orange[1], 80)
        self.assertLess(orange[2], 40)

        self.assertGreater(max(image.getpixel((390, 80))), 40, "outer island accidentally covers the full top row")

    def test_screen_artwork_is_clean_and_physical_front_hardware_is_independent(self):
        source = GENERATOR.read_text(encoding="utf-8")
        self.assertNotIn("FRONT_SENSOR_SCREEN_CUTTER", source)
        self.assertNotIn("FRONT_CAMERA_SCREEN_CUTTER", source)
        self.assertNotIn("CUT_FRONT_SENSOR_SCREEN", source)
        self.assertNotIn("CUT_FRONT_CAMERA_SCREEN", source)
        self.assertRegex(source, r'FRONT_SENSOR_MASK",\s*7\.10\*MM,\s*2\.30\*MM')
        self.assertRegex(source, r'FRONT_CAMERA_MASK",\s*1\.15\*MM')

    def test_dynamic_state_island_center_matches_official_hardware_datum(self):
        _, _, raster_center_mm = raster_dynamic_island_contract(SCREEN_STATE)
        official_center_mm = ledger_reference("front_camera_keepout.center_from_top")
        self.assertLessEqual(
            abs(raster_center_mm - official_center_mm),
            0.10,
            f"Dynamic Island raster center {raster_center_mm:.3f} mm does not align with "
            f"official hardware datum {official_center_mm:.3f} mm",
        )

    def test_front_hardware_uses_official_vertical_datum(self):
        source = GENERATOR.read_text(encoding="utf-8")
        hardware_match = re.search(
            r"front_hardware_z\s*=\s*H\*0\.5\s*-\s*([0-9.]+)\*MM",
            source,
        )
        self.assertIsNotNone(hardware_match)
        self.assertAlmostEqual(
            float(hardware_match.group(1)),
            ledger_reference("front_camera_keepout.center_from_top"),
            places=2,
        )

    def test_front_camera_keepout_dimensions_match_official_drawing(self):
        self.assertAlmostEqual(
            ledger_reference("front_camera_keepout.width"),
            20.75,
            places=6,
        )
        self.assertAlmostEqual(
            ledger_reference("front_camera_keepout.height"),
            5.12,
            places=6,
        )
        self.assertAlmostEqual(
            ledger_reference("front_camera_keepout.center_from_top"),
            7.79,
            places=6,
        )

    def test_bottom_macro_camera_proves_full_bottom_hardware(self):
        source = GENERATOR.read_text(encoding="utf-8")
        match = re.search(
            r'cam_bottom\s*=\s*persp\("CAM_BOTTOM_MACRO",\s*'
            r'\(0\.0,\s*([-0-9.]+),\s*([-0-9.]+)\),\s*'
            r'\(0,0,-H\*([0-9.]+)\),\s*([0-9.]+)\)',
            source,
        )
        self.assertIsNotNone(match, "bottom macro camera contract must remain explicit")
        camera_y = float(match.group(1))
        camera_z = float(match.group(2))
        target_fraction = float(match.group(3))
        lens_mm = float(match.group(4))
        target_z = -BODY_H_M * target_fraction
        vertical = abs(camera_z - target_z)
        depth = abs(camera_y)
        self.assertGreaterEqual(
            vertical / depth,
            1.5,
            "bottom macro camera is too face-on to prove underside hardware",
        )
        target_distance = (vertical ** 2 + depth ** 2) ** 0.5
        horizontal_span_m = target_distance * 36.0 / lens_mm
        self.assertGreaterEqual(
            horizontal_span_m,
            0.061,
            "bottom macro crop cannot contain USB-C + 3 mic + 6 speaker apertures + screws",
        )


if __name__ == "__main__":
    unittest.main()
