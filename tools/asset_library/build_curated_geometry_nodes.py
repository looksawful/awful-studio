from pathlib import Path
import bpy,uuid,json,os
ROOT=Path(r'F:\AWFUL_ASSETS\3D'); CAT=Path(r'F:\AWFUL_ASSETS\_catalog'); SRC=ROOT/'GeometryNodes'/'BlenderOfficial'; OUT=ROOT/'AssetBundles'/'AWFUL'/'GeometryNodes'; OUT.mkdir(parents=True,exist_ok=True)
DEST=Path(os.environ.get('AWFUL_GN_DEST',str(OUT/'blender_official_curated.blend')))
SUMMARY=Path(os.environ.get('AWFUL_GN_SUMMARY',str(CAT/'geometry_nodes_curated_summary.json')))
SOURCE=Path(os.environ.get('AWFUL_GN_SOURCE',str(OUT/'SOURCE.txt')))
plan={
'abstract_monkey_geometry-nodes_demo.blend': [('geonodes_wipe','Abstract Monkey Wipe','Motion & FX')],
'accumulate_field.blend': [('Geometry Nodes','Accumulate Field','Utilities'),('Random Pillar Graph','Random Pillar Graph','Procedural')],
'ball-in-grass_geometry-nodes_demo.blend': [('GrassAndFlowersInTheWind','Grass & Flowers Wind','Nature')],
'blender-geometry-nodes_procedural-buildings.blend': [('Procedural Building','Procedural Building','Architecture')],
'ripple_dreams_geometry-nodes_demo.blend': [('geonodes_bubbles','Ripple Bubbles','Motion & FX'),('geonodes_droplets','Ripple Droplets','Motion & FX'),('geonodes_floating','Ripple Floating','Motion & FX'),('geonodes_pebbles','Ripple Pebbles','Motion & FX'),('geonodes_water','Ripple Water','Motion & FX')],
'sample_sound_frequencies.blend': [('Sound Waves','Sound Waves','Audio')],
'spherical-eye_geometry-nodes-demo.blend': [('Geometry Nodes','Spherical Eye','Procedural')],
'string_to_curves_motion_graphics_text.blend': [('Animate Text','Animate Text','Text')],
'text-morph_geometry-nodes-demo.blend': [('Geometry Nodes','Text Morph','Text')],
'transform_socket-pizza_delivery.blend': [('Pizza Stack Generator','Pizza Stack Generator','Props'),('cobblestone','Cobblestone','Architecture'),('GN-scatter_debris','Scatter Debris','Environment'),('GN-bush','Bush Generator','Nature'),('lamps','Lamps','Environment')],
'tree_leaves_moss_geo-nodes-demo.blend': [('Moss - Add','Moss Add','Nature'),('Tree Leaves','Tree Leaves','Nature'),('Tree Moss','Tree Moss','Nature')]
}
categories=sorted({cat for xs in plan.values() for _,_,cat in xs})
cat_ids={cat:str(uuid.uuid5(uuid.NAMESPACE_URL,'https://looksawful.ru/assets/catalog/AWFUL/Geometry Nodes/Curated/'+cat)) for cat in categories}
catfile=ROOT/'blender_assets.cats.txt'; text=catfile.read_text(encoding='utf-8-sig'); existing={line.split(':',1)[0].lower() for line in text.splitlines() if ':' in line and not line.lstrip().startswith('#')}; add=[]
for cat,cid in cat_ids.items():
 path='AWFUL/Geometry Nodes/Curated/'+cat
 if cid.lower() not in existing: add.append(f'{cid}:{path}:{cat}')
DEST.parent.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
assets=[]; errors=[]
for filename,items in plan.items():
 src=SRC/filename; names=[x[0] for x in items]
 try:
  with bpy.data.libraries.load(str(src),link=False) as (df,dt):
   missing=[n for n in names if n not in df.node_groups]
   if missing: raise RuntimeError('missing node groups: '+repr(missing))
   dt.node_groups=names
  loaded=list(dt.node_groups)
  for ng,(orig,new,cat) in zip(loaded,items):
   if ng is None: raise RuntimeError(f'failed append {orig}')
   ng.name=new; ng.use_fake_user=True
   if not ng.asset_data: ng.asset_mark()
   ad=ng.asset_data; ad.catalog_id=cat_ids[cat]; ad.author='Blender Foundation / Blender community'; ad.description=f'Curated from official Blender demo: {filename}. Preserve/check upstream per-file licensing and credits.'
   ad['source_file']=filename; ad['source_url']='https://download.blender.org/demo/geometry-nodes/'
   for tag in ['Blender Demo','Geometry Nodes','Curated',cat]:
    try:
     if tag not in {t.name for t in ad.tags}: ad.tags.new(tag)
    except: pass
   assets.append({'name':ng.name,'source':filename,'category':cat})
 except Exception as e: errors.append({'file':filename,'error':repr(e)})
if errors:
 raise RuntimeError('curated Geometry Nodes build failed before save: '+repr(errors))
# dependencies appended with curated node groups may carry upstream asset metadata.
# Keep only explicitly curated entries as first-class Asset Browser assets.
curated_names={a['name'] for a in assets}
for ng in bpy.data.node_groups:
 if ng.name not in curated_names and ng.asset_data:
  ng.asset_clear()
bpy.ops.wm.save_as_mainfile(filepath=str(DEST),check_existing=False)
# provenance sidecar
lines=['Source: https://download.blender.org/demo/geometry-nodes/','Provider: Blender Foundation / Blender community','License: preserve/check upstream per-file licensing and credits. Curated bundle does not override source licenses.','','Included assets:']
for a in assets: lines.append(f"- {a['name']} <- {a['source']} [{a['category']}]")
SOURCE.parent.mkdir(parents=True,exist_ok=True); SOURCE.write_text('\n'.join(lines)+'\n',encoding='utf-8')
result={'bundle':str(DEST),'assets':assets,'asset_count':len(assets),'errors':errors,'catalogs_added':len(add),'catalog_lines':add,'size_mb':round(DEST.stat().st_size/1024**2,2)}
SUMMARY.parent.mkdir(parents=True,exist_ok=True); SUMMARY.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print('RESULT',json.dumps(result,ensure_ascii=False,indent=2))
