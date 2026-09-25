from pathlib import Path
import csv, json
from collections import Counter, defaultdict
ROOT=Path(r'F:\AWFUL_ASSETS\3D')
OUT=Path(r'F:\AWFUL_ASSETS\_catalog')
definitions=[]
catalog_errors=[]
for p in ROOT.rglob('blender_assets.cats.txt'):
    try:
        for lineno,line in enumerate(p.read_text(encoding='utf-8-sig',errors='strict').splitlines(),1):
            s=line.strip()
            if not s or s.startswith('#') or s.startswith('VERSION '): continue
            parts=s.split(':',2)
            if len(parts)!=3 or not all(parts):
                catalog_errors.append({'file':str(p.relative_to(ROOT)),'line':lineno,'error':'malformed catalog definition','text':s}); continue
            definitions.append({'uuid':parts[0].lower(),'path':parts[1],'name':parts[2],'file':str(p.relative_to(ROOT)),'line':lineno})
    except Exception as e:
        catalog_errors.append({'file':str(p.relative_to(ROOT)),'line':None,'error':repr(e),'text':''})
by_uuid=defaultdict(list); by_path=defaultdict(list)
for d in definitions:
    by_uuid[d['uuid']].append(d); by_path[d['path']].append(d)
duplicate_uuids={k:v for k,v in by_uuid.items() if len(v)>1}
duplicate_paths={k:v for k,v in by_path.items() if len(v)>1}
def_ids={d['uuid']:d for d in definitions}
rows=[]
with (OUT/'asset_metadata.csv').open(encoding='utf-8-sig') as f: rows=list(csv.DictReader(f))
zero={'','00000000-0000-0000-0000-000000000000'}
for r in rows:
    cid=r['catalog_id'].lower()
    r['resolved']=cid in def_ids
    r['catalog_path']=def_ids.get(cid,{}).get('path','')
unresolved=[r for r in rows if r['type']!='ERROR' and (r['catalog_id'].lower() in zero or not r['resolved'])]
summary={'defined_catalogs':len(definitions),'asset_rows':sum(r['type']!='ERROR' for r in rows),'resolved_assets':sum(r['type']!='ERROR' and r['resolved'] for r in rows),'unresolved_assets':len(unresolved),'catalog_errors':catalog_errors,'duplicate_uuid_groups':duplicate_uuids,'duplicate_path_groups':duplicate_paths,'unresolved_by_prefix':Counter(r['file'].split('\\')[0] for r in unresolved),'unresolved_by_source':Counter('\\'.join(r['file'].split('\\')[:2]) for r in unresolved),'used_catalogs':Counter(r['catalog_path'] for r in rows if r.get('resolved'))}
(OUT/'catalog_resolution_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2,default=dict),encoding='utf-8')
with (OUT/'catalog_unresolved.csv').open('w',newline='',encoding='utf-8-sig') as f:
    w=csv.DictWriter(f,fieldnames=['file','type','name','catalog_id','description']); w.writeheader(); w.writerows([{k:r[k] for k in ['file','type','name','catalog_id','description']} for r in unresolved])
print(json.dumps(summary,ensure_ascii=False,indent=2,default=dict))
print('UNRESOLVED_SAMPLE')
for r in unresolved[:40]: print(r['file'],'|',r['type'],'|',r['name'],'|',r['catalog_id'])
if catalog_errors or duplicate_uuids or duplicate_paths: raise SystemExit(1)
