from pathlib import Path
p=Path(__file__).with_name("generate_low_v27.py")
s=p.read_text(encoding="utf-8")
assert 'SCREEN_UI_DECAL' not in s, 'v27 must remove duplicate SCREEN_UI_DECAL geometry'
assert 'screen_ui.location' not in s, 'v27 must not retain near-coplanar screen decal'
assert 'camera_control_protrusion_mm' in s, 'v27 must report Camera Control protrusion'
assert 'and 0.0 <= camera_control_protrusion_mm <= 0.20' in s, 'v27 validation must reject negative protrusion'
assert 'max(0.0, round(camera_control_protrusion_mm' not in s, 'v27 evidence must report raw protrusion, not clamp it'
assert 'awful_screen_gradient_1440x3132.png' in s, 'v27 must use the high-resolution neutral QA screen'
assert 'DISPLAY_SURFACE_T = 0.030 * MM' in s, 'v27 display artwork must be a thin surface, not a second glass slab'
assert 'DISPLAY_GAP = 0.080 * MM' in s, 'v27 display must sit behind the cover-glass ring with a real gap'
assert 'CAMERA_HOUSING_R = 10.27 * MM' in s, 'camera housing must use the capsule radius from the 20.54 mm envelope'
assert 'CAMERA_HOUSING_SEAT_R = 10.37 * MM' in s, 'camera seat must follow the capsule housing envelope'
assert '3.25*MM, camera_housing_mat' not in s and '3.25 * MM, camera_housing_mat' not in s, 'connector R3.25 must not be reused as the camera housing corner radius'
assert 'CAMERA_CONTROL_LENGTH = 17.10 * MM' in s, 'Apple side drawing gives Camera Control 2x8.55 mm length'
assert 'CAMERA_CONTROL_FACE_W = 3.03 * MM' in s, 'Apple side drawing gives Camera Control 3.03 mm face width'
assert 'def side_capsule(' in s, 'Camera Control must be a side capsule, not a circular plug'
assert 'CAMERA_CONTROL_CUTTER",' in s and 'side_capsule(' in s, 'Camera Control cutter must follow the capsule profile'
assert 'fc.cylinder("CAMERA_CONTROL"' not in s, 'Camera Control must not be modeled as a cylinder'
print('DISPLAY_CAMERA_V27 PASS')
