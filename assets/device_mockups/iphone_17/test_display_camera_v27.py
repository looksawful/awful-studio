from pathlib import Path
p=Path(__file__).with_name("generate_low_v27.py")
s=p.read_text(encoding="utf-8")
assert 'SCREEN_UI_DECAL' not in s, 'v27 must remove duplicate SCREEN_UI_DECAL geometry'
assert 'screen_ui.location' not in s, 'v27 must not retain near-coplanar screen decal'
assert 'camera_control_protrusion_mm' in s, 'v27 must report Camera Control protrusion'
assert 'camera_control_protrusion_mm": max(0.0' in s or "camera_control_protrusion_mm': max(0.0" in s, 'v27 validation must reject/clamp negative protrusion'
print('DISPLAY_CAMERA_V27 PASS')
