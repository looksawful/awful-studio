from pathlib import Path
import csv, hashlib, json, subprocess, sys

CAT=Path(r"F:\AWFUL_ASSETS\_catalog")
BUILD=Path(__file__).resolve().parent/"build_asset_index.py"
OUTPUTS=["asset_index.csv","asset_index_summary.json","exact_duplicates.csv","exact_duplicates.json"]

def hashes():
    return {name:hashlib.sha256((CAT/name).read_bytes()).hexdigest() for name in OUTPUTS}

subprocess.run([sys.executable,str(BUILD)],check=True,stdout=subprocess.DEVNULL)
first=hashes()
summary=json.loads((CAT/"asset_index_summary.json").read_text(encoding="utf-8"))
subprocess.run([sys.executable,str(BUILD)],check=True,stdout=subprocess.DEVNULL)
second=hashes()
assert first==second,(first,second)

with (CAT/"asset_index.csv").open(encoding="utf-8-sig") as f:
    rows=list(csv.DictReader(f))
self_paths={f"_catalog\\{name}" for name in OUTPUTS}
found=[r["relative"] for r in rows if r["relative"] in self_paths]
assert not found,found
print("OK",summary["files"],summary["bytes"],summary["hardlinked_paths"],summary["potential_reclaim_bytes"])
