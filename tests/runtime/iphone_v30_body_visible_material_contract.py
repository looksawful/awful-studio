"""Visible BODY_ALUMINUM material assignment contract.

Outer rail faces must stay on the anodized-metal slot. This specifically
guards against face reordering during BMesh normal recalculation assigning the
dark tray material to visible panel cells.
"""
import bpy

obj=bpy.data.objects["BODY_ALUMINUM"]
mesh=obj.data

visible_bad=[]
for poly in mesh.polygons:
    coords=[mesh.vertices[mesh.loops[li].vertex_index].co for li in poly.loop_indices]
    # Flat side faces on the exterior rail.
    if all(abs(abs(co.x)-71.45e-3*0.5)<1e-8 for co in coords) and abs(poly.normal.x)>0.9:
        if poly.material_index!=0:
            visible_bad.append((poly.index,"side",poly.material_index,tuple(round(v,4) for v in poly.normal)))
    # Flat bottom faces on the exterior rail.
    if all(abs(co.z+149.61e-3*0.5)<1e-8 for co in coords) and poly.normal.z<-0.9:
        if poly.material_index!=0:
            visible_bad.append((poly.index,"bottom",poly.material_index,tuple(round(v,4) for v in poly.normal)))

assert not visible_bad, visible_bad[:20]
print("IPHONE_BODY_VISIBLE_MATERIAL_GREEN", {"checked_bad":len(visible_bad),"materials":[m.name for m in mesh.materials]})
