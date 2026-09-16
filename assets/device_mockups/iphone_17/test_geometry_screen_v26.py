from pathlib import Path

root = Path(__file__).parent
text = (root / "generate_low_v26.py").read_text(encoding="utf-8") if (root / "generate_low_v26.py").exists() else ""

assert "71.45 * MM, 149.61 * MM, 7.95 * MM" in text, "use exact Apple drawing product dimensions"
assert '"reference", "ios26_home_screen_1206x2622.png"' in text, "screen must use an image texture"
assert 'ShaderNodeTexImage' in text and 'screen_tex.image' in text, "screen image must be wired into material"
assert 'root["screen_texture"]' in text, "screen texture provenance must be recorded"
assert 'BOTTOM_SPEAKER_APERTURE_06' in text, "Apple bottom drawing shows six speaker ports"
assert '"3_mic + usb_c + 6_speaker"' in text, "bottom layout metadata must match geometry"
print("GEOMETRY_SCREEN_V26 PASS")

assert '((0,0),(1,0),(1,1),(0,1))' in text, 'screen UV must remain portrait'
assert '20.54*MM, 43.62*MM' in text, 'camera plateau must follow drawing envelope'
assert 'housing_x = W*0.5 - 20.54*MM*0.5' in text, 'camera plateau must seat against product side edge'
assert 'housing_z = H*0.5 - 43.62*MM*0.5' in text, 'camera plateau must seat against product top edge'

