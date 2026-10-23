from pathlib import Path
import csv, hashlib, json
from collections import defaultdict, Counter
ROOT=Path(r'F:\AWFUL_ASSETS')
OUT=ROOT/'_catalog'
GENERATED={'asset_index.csv','asset_index_summary.json','exact_duplicates.csv','exact_duplicates.json'}
files=[]
for p in ROOT.rglob('*'):
    if not p.is_file(): continue
    try: st=p.stat()
    except OSError: continue
    rel=p.relative_to(ROOT)
    parts=rel.parts
    if len(parts)==2 and parts[0]=='_catalog' and parts[1] in GENERATED: continue
    top=parts[0] if parts else ''
    category=parts[1] if top=='3D' and len(parts)>1 else top
    source=parts[2] if top=='3D' and len(parts)>2 else ''
    files.append({'path':str(p),'relative':str(rel),'top':top,'category':category,'source':source,'ext':p.suffix.lower(),'size':st.st_size,'mtime':int(st.st_mtime),'dev':st.st_dev,'ino':st.st_ino})
with (OUT/'asset_index.csv').open('w',newline='',encoding='utf-8-sig') as f:
    w=csv.DictWriter(f,fieldnames=files[0].keys()); w.writeheader(); w.writerows(files)
# Hash only size-collision groups, skipping zero-byte files.
by_size=defaultdict(list)
for x in files:
    if x['size']>0: by_size[x['size']].append(x)
collisions=[g for g in by_size.values() if len(g)>1]
by_hash=defaultdict(list)
bytes_hashed=0
hash_by_inode={}
for group in collisions:
    for x in group:
        inode=(x['dev'],x['ino'])
        digest=hash_by_inode.get(inode)
        if digest is None:
            h=hashlib.sha256()
            try:
                with open(x['path'],'rb') as f:
                    for chunk in iter(lambda:f.read(4*1024*1024),b''):
                        h.update(chunk); bytes_hashed+=len(chunk)
            except OSError: continue
            digest=h.hexdigest(); hash_by_inode[inode]=digest
        by_hash[digest].append(x)
dups=[]
for h,g in by_hash.items():
    if len(g)>1:
        g=sorted(g,key=lambda x:x['relative'])
        physical=len({(x['dev'],x['ino']) for x in g})
        logical_wasted=g[0]['size']*(len(g)-1)
        reclaimable=g[0]['size']*max(0,physical-1)
        dups.append({'sha256':h,'size':g[0]['size'],'count':len(g),'physical_copies':physical,'hardlinked_paths':len(g)-physical,'wasted_bytes':logical_wasted,'reclaimable_bytes':reclaimable,'files':[x['relative'] for x in g]})
dups.sort(key=lambda x:x['reclaimable_bytes'],reverse=True)
(OUT/'exact_duplicates.json').write_text(json.dumps(dups,ensure_ascii=False,indent=2),encoding='utf-8')
with (OUT/'exact_duplicates.csv').open('w',newline='',encoding='utf-8-sig') as f:
    w=csv.writer(f); w.writerow(['sha256','size','count','physical_copies','hardlinked_paths','wasted_bytes','reclaimable_bytes','file'])
    for d in dups:
        for p in d['files']: w.writerow([d['sha256'],d['size'],d['count'],d['physical_copies'],d['hardlinked_paths'],d['wasted_bytes'],d['reclaimable_bytes'],p])
summary={'files':len(files),'bytes':sum(x['size'] for x in files),'extensions':Counter(x['ext'] for x in files).most_common(),'duplicate_groups':len(dups),'duplicate_files':sum(d['count'] for d in dups),'logical_duplicate_bytes':sum(d['wasted_bytes'] for d in dups),'hardlinked_paths':sum(d['hardlinked_paths'] for d in dups),'potential_reclaim_bytes':sum(d['reclaimable_bytes'] for d in dups),'bytes_hashed':bytes_hashed}
(OUT/'asset_index_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
print('TOP_DUPLICATES')
for d in dups[:20]: print(round(d['reclaimable_bytes']/1024/1024,2),'MB reclaimable',d['physical_copies'],'physical /',d['count'],'paths',d['files'][:4])
