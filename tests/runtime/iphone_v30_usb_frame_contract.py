"""USB physical width must span the device X datum, in Blender and compat GLB."""
import bpy
from pathlib import Path
import sys
repo = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(repo / 'tests/fast'))
from test_iphone_dimensional_drawing_contract import read_glb, node_world_bounds_mm

# Independent physical dimensions from the existing USB assembly specification.
expected = {'USB_C_CAVITY': (8.45, 2.38, .12, 1.40),
            'USB_C_TONGUE': (5.25, .48, .18, .80)}
report = {}
for name, (width, thickness, depth, inset) in expected.items():
    obj = bpy.data.objects[name]
    points = [obj.matrix_world @ v.co for v in obj.data.vertices]
    lo = [min(p[a] for p in points) for a in range(3)]
    hi = [max(p[a] for p in points) for a in range(3)]
    dimensions = [(hi[a] - lo[a]) * 1000 for a in range(3)]
    report[name] = {'native_world_dimensions_mm': dimensions}
    assert abs(dimensions[0] - width) < .001, (name, 'USB width spans device X', report)
    assert abs(dimensions[1] - thickness) < .001, (name, 'USB thickness spans device depth', report)
    assert abs(dimensions[2] - depth) < .001, report
    assert abs((lo[2] + hi[2]) * 500 - (-74.805 + inset)) < .001, report
    assert abs((lo[0] + hi[0]) * 500) < .001, report
    assert abs((lo[1] + hi[1]) * 500) < .001, report
print('IPHONE_USB_NATIVE_FRAME_GREEN', report)

doc, blob = read_glb(repo / 'assets/device_mockups/iphone_17/runtime/v30/iphone_17_v30_web.glb')
for name, (width, thickness, depth, inset) in expected.items():
    lo, hi = node_world_bounds_mm(doc, blob, name)
    dimensions = [hi[a] - lo[a] for a in range(3)]
    assert abs(dimensions[0] - width) < .001, (name, 'exported USB width spans device X', dimensions)
    assert abs(dimensions[1] - depth) < .001, (name, dimensions)
    assert abs(dimensions[2] - thickness) < .001, (name, dimensions)
    assert abs((lo[1] + hi[1]) / 2 - (-74.805 + inset)) < .001, (name, lo, hi)
print('IPHONE_USB_EXPORTED_FRAME_GREEN', tuple(expected))
