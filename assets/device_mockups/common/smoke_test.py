import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import bpy
import foundation_common as fc

fc.clear_scene()
fc.setup_scene()
assert bpy.context.scene.render.engine == "BLENDER_EEVEE"
print("FOUNDATION_COMMON_SMOKE_OK")
