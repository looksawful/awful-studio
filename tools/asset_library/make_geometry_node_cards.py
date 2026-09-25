from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,re,sys
CAT=Path(r'F:\AWFUL_ASSETS\_catalog')
SUMMARY=Path(sys.argv[1]) if len(sys.argv)>1 else CAT/'geometry_nodes_curated_summary.json'
OUT=Path(sys.argv[2]) if len(sys.argv)>2 else CAT/'previews'/'geometry_nodes'; OUT.mkdir(parents=True,exist_ok=True)
MANIFEST=Path(sys.argv[3]) if len(sys.argv)>3 else CAT/'geometry_nodes_preview_manifest.json'
data=json.loads(SUMMARY.read_text(encoding='utf-8'))['assets']
colors={'Architecture':'#d9845b','Nature':'#87a96b','Motion & FX':'#8b7bb5','Audio':'#5f9ea0','Procedural':'#c6a15b','Utilities':'#7d8b99','Text':'#b77b9e','Props':'#b38b6d','Environment':'#6b9a8b'}
try:
 bold=ImageFont.truetype(r'C:\Windows\Fonts\segoeuib.ttf',15); tiny=ImageFont.truetype(r'C:\Windows\Fonts\segoeui.ttf',8)
except: bold=tiny=ImageFont.load_default()
manifest={}
for a in data:
 im=Image.new('RGB',(128,128),'#151719'); d=ImageDraw.Draw(im); accent=colors.get(a['category'],'#888888')
 d.rectangle((0,0,128,5),fill=accent); d.text((9,12),a['category'].upper(),font=tiny,fill=accent)
 words=a['name'].split(); lines=[]; line=''
 for w in words:
  cand=(line+' '+w).strip()
  if d.textlength(cand,font=bold)<=108: line=cand
  else:
   if line: lines.append(line)
   line=w
 if line: lines.append(line)
 lines=lines[:3]
 y=38
 for ln in lines: d.text((9,y),ln,font=bold,fill='#f0f0ee'); y+=18
 d.line((9,101,119,101),fill='#34383c',width=1); d.text((9,106),'BLENDER DEMO / CURATED',font=tiny,fill='#8d9296')
 safe=re.sub(r'[^A-Za-z0-9._-]+','_',a['name']).strip('_')+'.png'; path=OUT/safe; im.save(path,optimize=True); manifest[a['name']]=str(path)
MANIFEST.parent.mkdir(parents=True,exist_ok=True); MANIFEST.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print('CARDS',len(manifest),'OUT',OUT)
