from pathlib import Path
import hashlib, os, subprocess, sys

ROOT=Path(r"F:\AWFUL_ASSETS")
HERE=Path(__file__).resolve().parent
REBUILD=HERE/"rebuild_geometry_nodes.py"
BUNDLE=ROOT/"3D"/"AssetBundles"/"AWFUL"/"GeometryNodes"/"blender_official_curated.blend"
CATALOG=ROOT/"3D"/"blender_assets.cats.txt"
SUMMARY=ROOT/"_catalog"/"geometry_nodes_curated_summary.json"
SOURCE=BUNDLE.parent/"SOURCE.txt"
PREVIEWS=ROOT/"_catalog"/"previews"/"geometry_nodes"
MANIFEST=ROOT/"_catalog"/"geometry_nodes_preview_manifest.json"
CHECKPOINT=ROOT/"_checkpoints"/"geometry_nodes_curated_last_good"/"blender_official_curated.blend"
TARGETS=(BUNDLE,CATALOG,SUMMARY,SOURCE,PREVIEWS,MANIFEST,CHECKPOINT)

def digest(path):
    if not path.exists():
        return None
    if path.is_file():
        return hashlib.sha256(path.read_bytes()).hexdigest()
    return tuple(sorted((p.relative_to(path).as_posix(),hashlib.sha256(p.read_bytes()).hexdigest()) for p in path.rglob("*") if p.is_file()))

before={str(p):digest(p) for p in TARGETS}
for stage in ("publish_catalog","publish_previews","publish_manifest","publish_source","publish_summary","publish_checkpoint","publish_bundle"):
    env=os.environ.copy()
    env["AWFUL_GN_FAIL_STAGE"]=stage
    result=subprocess.run([sys.executable,str(REBUILD)],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    assert result.returncode!=0,(stage,result.returncode)
    after={str(p):digest(p) for p in TARGETS}
    assert after==before,(stage,[p for p in before if before[p]!=after[p]])
    print("OK",stage)
