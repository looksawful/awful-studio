from pathlib import Path
import re

SOURCE = Path(__file__).with_name("generate_low_v22.py")
text = SOURCE.read_text(encoding="utf-8") if SOURCE.exists() else ""

assert 'def physical_side_button(' in text, "physical buttons need dedicated geometry"
assert 'def camera_control(' in text, "Camera Control must not reuse physical button geometry"
assert 'physical_side_button("ACTION_BUTTON", "LEFT", 40.72, 11.6' in text
assert 'physical_side_button("VOL_UP", "LEFT", 26.57, 9.2' in text
assert 'physical_side_button("VOL_DOWN", "LEFT", 12.37, 9.2' in text
assert 'physical_side_button("SIDE_BUTTON", "RIGHT", 19.48, 17.7' in text
assert 'camera_control("RIGHT", -23.40, 17.5' in text
assert 'button_protrusion_mm >= 0.45' in text, "physical buttons need visible tactile protrusion validation"
assert 'camera_control_protrusion_mm <= 0.20' in text, "Camera Control must remain near-flush"
assert 'side_control(' not in text, "legacy near-flat generic side control must be removed"
print("SIDE_CONTROL_CONTRACT_V22 PASS")
