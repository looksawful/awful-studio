import bpy, os
HERE=os.path.dirname(os.path.abspath(__file__))
OUT=os.path.join(HERE,"out")
scene=bpy.context.scene
scene.render.engine="BLENDER_EEVEE"
scene.view_settings.look="AgX - Medium High Contrast"
scene.view_settings.exposure=-2.2
scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value=.16
for name in ("KEY","FILL","RIM"):
    obj=bpy.data.objects.get(name)
    if obj and obj.type=="LIGHT":
        obj.data.energy *= .28
for n in (16,24,32,40):
    for c in bpy.data.collections:
        if c.name.startswith("LOW_"):
            c.hide_render = c.name != "LOW_"+str(n)
    scene.render.filepath=os.path.join(OUT,"camera_"+str(n)+"_baked.png")
    bpy.ops.render.render(write_still=True)
print("RERENDER_DONE")
