from pathlib import Path
import sys
p=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).with_name('generate_low_v30.py')
s=p.read_text(encoding='utf-8')
assert 'def capsule_prism_x(' in s, 'controls require capsule mesh geometry'
for name in ('ACTION_BUTTON','VOL_UP','VOL_DOWN','SIDE_BUTTON'):
    assert f'physical_side_button("{name}"' in s
assert '2.56,0.45)' in s or '2.56, 0.45)' in s
assert 'camera_control("RIGHT",-23.40,17.5,3.00,0.06)' in s.replace(' ','') or 'camera_control("RIGHT", -23.40, 17.5, 3.00, 0.06)' in s
assert 'diameter_mm=2.55' not in s, 'Camera Control must not regress to circular proxy'
print('SIDE_CONTROL_CONTRACT_V30 PASS',p.name)
