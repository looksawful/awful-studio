import json
import os
import sys
import bpy

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
COMMON = os.path.join(ROOT, "assets", "device_mockups", "common")
if COMMON not in sys.path:
    sys.path.insert(0, COMMON)

import material_pipeline as mp


def arg(flag, default=None):
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    return argv[argv.index(flag) + 1] if flag in argv else default

out_path = arg("--out")
report_path = arg("--report")
stage = arg("--stage", "LOW_DRAFT")
if not out_path or not report_path:
    raise RuntimeError("--out and --report are required")

report = mp.auto_tag_scene(bpy)
roots = [o for o in bpy.data.objects if o.type == "EMPTY" and o.name.startswith("CTRL_")]
for root in roots:
    root["material_contract_version"] = mp.CONTRACT["version"]
    root["stage"] = stage
report["stage"] = stage
report["contract_version"] = mp.CONTRACT["version"]
report["root_objects"] = [o.name for o in roots]
report["object_count"] = len([o for o in bpy.data.objects if o.type == "MESH"])
report["material_count"] = len(bpy.data.materials)

os.makedirs(os.path.dirname(os.path.abspath(report_path)), exist_ok=True)
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(report, handle, indent=2, sort_keys=True)

os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(out_path))
print("AWFUL_MATERIAL_CONTRACT", json.dumps({
    "contract_version": report["contract_version"],
    "tagged_objects": len(report["objects"]),
    "tagged_materials": len(report["materials"]),
    "unclassified_materials": len(report["unclassified_materials"]),
    "unclassified_objects": len(report["unclassified_objects"]),
    "out": os.path.abspath(out_path),
}, sort_keys=True))
