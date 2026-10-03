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
hole=bt._capsule(19.48*MM,3.04*MM,18.26*MM,steps=8)
_, rebuilt=bt._matched_annulus_loops(-7.25*MM/2,7.25*MM/2,6*MM,32*MM,hole)
max_error=max(min(((a[0]-b[0])**2+(a[1]-b[1])**2)**0.5 for b in rebuilt) for a in hole)
assert max_error <= 1e-8, {"max_authored_contour_loss_m":max_error,"authored":len(hole),"rebuilt":len(rebuilt)}
print("IPHONE_BODY_CELL_SHAPE_GREEN",{"max_authored_contour_loss_m":max_error,"authored":len(hole),"rebuilt":len(rebuilt)})
