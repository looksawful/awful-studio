"""BODY_ALUMINUM local cell contour preservation contract.

The annulus builder must preserve authored hole contour vertices. Otherwise long
capsules collapse into pointed/diamond-like recesses even while the mesh remains
manifold.
"""
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
DEVICE=ROOT/"assets"/"device_mockups"/"iphone_17"
sys.path.insert(0,str(DEVICE))
import body_topology_v30 as bt

MM=.001
hole=bt._capsule(19.48*MM,3.04*MM,18.26*MM,steps=64)
outer, rebuilt=bt._uniform_annulus_loops(-7.25*MM/2,7.25*MM/2,6*MM,32*MM,hole,segments=44)
xs=[point[0] for point in rebuilt]
ys=[point[1] for point in rebuilt]
report={
    "samples":len(rebuilt),
    "outer_samples":len(outer),
    "min_x_mm":min(xs)/MM,
    "max_x_mm":max(xs)/MM,
    "min_y_mm":min(ys)/MM,
    "max_y_mm":max(ys)/MM,
}
assert len(rebuilt)==44 and len(outer)==44, report
assert abs(report["min_x_mm"] + 1.52) <= 1e-6, report
assert abs(report["max_x_mm"] - 1.52) <= 1e-6, report
assert abs(report["min_y_mm"] - 10.35) <= 1e-6, report
assert abs(report["max_y_mm"] - 28.61) <= 1e-6, report
print("IPHONE_BODY_CELL_SHAPE_GREEN",report)
