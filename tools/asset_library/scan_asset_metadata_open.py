from pathlib import Path
import bpy, csv, json
ROOT=Path(r'F:\AWFUL_ASSETS\3D')
OUT=Path(r'F:\AWFUL_ASSETS\_catalog')
inv=[]
with (OUT/'blender_asset_inventory.csv').open(encoding='utf-8-sig') as f:
    inv=[r for r in csv.DictReader(f) if int(r['asset_count'])>0]
collections=['actions','armatures','brushes','collections','curves','grease_pencils','images','materials','meshes','node_groups','objects','worlds']
rows=[]
for i,r in enumerate(inv,1):
    p=ROOT/r['file']
    try:
        bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False,use_scripts=False)
        for key in collections:
            for item in getattr(bpy.data,key):
                ad=getattr(item,'asset_data',None)
                if ad:
                    rows.append({'file':r['file'],'type':key,'name':item.name,'catalog_id':str(getattr(ad,'catalog_id','')),'description':str(getattr(ad,'description',''))})
    except Exception as e:
        rows.append({'file':r['file'],'type':'ERROR','name':'','catalog_id':'','description':repr(e)})
    if i%10==0: print('OPENED',i,'OF',len(inv))
expected=sum(int(r['asset_count']) for r in inv)
actual=sum(r['type']!='ERROR' for r in rows)
assert actual==expected, f'asset metadata coverage mismatch: inventory={expected}, metadata={actual}'
with (OUT/'asset_metadata.csv').open('w',newline='',encoding='utf-8-sig') as f:
    w=csv.DictWriter(f,fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
zero={'','00000000-0000-0000-0000-000000000000'}
unc=[x for x in rows if x['type']!='ERROR' and x['catalog_id'] in zero]
summary={'asset_rows':sum(x['type']!='ERROR' for x in rows),'uncategorized':len(unc),'errors':sum(x['type']=='ERROR' for x in rows),'uncategorized_by_type':{k:sum(x['type']==k for x in unc) for k in sorted(set(x['type'] for x in unc))},'uncategorized_files':sorted(set(x['file'] for x in unc)),'categorized':sum(x['type']!='ERROR' and x['catalog_id'] not in zero for x in rows)}
(OUT/'asset_metadata_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print('SUMMARY',json.dumps(summary,ensure_ascii=False,indent=2))
