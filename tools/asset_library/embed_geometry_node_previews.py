import bpy,json,sys
from pathlib import Path
BUNDLE=Path(sys.argv[-2]) if '--' in sys.argv else Path(r'F:\AWFUL_ASSETS\3D\AssetBundles\AWFUL\GeometryNodes\blender_official_curated.blend')
MAN=Path(sys.argv[-1]) if '--' in sys.argv else Path(r'F:\AWFUL_ASSETS\_catalog\geometry_nodes_preview_manifest.json')
manifest=json.loads(MAN.read_text(encoding='utf-8'))
bpy.ops.wm.open_mainfile(filepath=str(BUNDLE),load_ui=False,use_scripts=False)
result={'embedded':0,'failed':[]}
for name,path in manifest.items():
 ng=bpy.data.node_groups.get(name)
 if not ng or not ng.asset_data:
  result['failed'].append({'name':name,'error':'asset node group missing'}); continue
 try:
  img=bpy.data.images.load(path,check_existing=False)
  if tuple(img.size)!=(128,128): img.scale(128,128)
  px=list(img.pixels[:])
  prev=ng.preview_ensure(); prev.image_size=(128,128); prev.image_pixels_float=px; prev.is_image_custom=True
  bpy.data.images.remove(img)
  result['embedded']+=1
 except Exception as e: result['failed'].append({'name':name,'error':repr(e)})
if result['failed']: raise RuntimeError(result)
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(BUNDLE),check_existing=False)
print(json.dumps(result,ensure_ascii=False,indent=2))
