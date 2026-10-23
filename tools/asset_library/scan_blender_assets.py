from pathlib import Path
import bpy, csv, json
ROOT=Path(r'F:\AWFUL_ASSETS\3D')
OUT=Path(r'F:\AWFUL_ASSETS\_catalog')
fields=['actions','armatures','brushes','collections','curves','grease_pencils','images','materials','meshes','node_groups','objects','worlds']
rows=[]
for i,p in enumerate(ROOT.rglob('*.blend'),1):
    rel=str(p.relative_to(ROOT))
    rec={'file':rel,'size':p.stat().st_size,'asset_count':0,'types':'','error':''}
    found=[]
    try:
        with bpy.data.libraries.load(str(p),assets_only=True) as (src,dst):
            for k in fields:
                vals=getattr(src,k,[]) if hasattr(src,k) else []
                if vals:
                    found.append(f'{k}:{len(vals)}')
                    rec['asset_count']+=len(vals)
        rec['types']=';'.join(found)
    except Exception as e:
        rec['error']=f'{type(e).__name__}: {e}'
    rows.append(rec)
    if i%25==0: print('SCANNED',i)
with (OUT/'blender_asset_inventory.csv').open('w',newline='',encoding='utf-8-sig') as f:
    w=csv.DictWriter(f,fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
summary={'blend_files':len(rows),'files_with_assets':sum(r['asset_count']>0 for r in rows),'total_assets':sum(r['asset_count'] for r in rows),'errors':sum(bool(r['error']) for r in rows),'top_files':sorted([r for r in rows if r['asset_count']],key=lambda r:r['asset_count'],reverse=True)[:30]}
(OUT/'blender_asset_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print('SUMMARY',json.dumps(summary,ensure_ascii=False,indent=2))
