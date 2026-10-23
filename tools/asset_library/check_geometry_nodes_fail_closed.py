from pathlib import Path
import hashlib, os, subprocess, sys

ROOT=Path(r"F:\AWFUL_ASSETS")
HERE=Path(__file__).resolve().parent
REBUILD=HERE/"rebuild_geometry_nodes.py"
BUNDLE=ROOT/"3D"/"AssetBundles"/"AWFUL"/"GeometryNodes"/"blender_official_curated.blend"
CHECKPOINT=ROOT/"_checkpoints"/"geometry_nodes_curated_last_good"/"blender_official_curated.blend"

def state(path):
    if not path.exists():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest(),path.stat().st_mtime_ns

for stage in ("build","cards","embed","validate"):
    bundle_before=state(BUNDLE)
    checkpoint_before=state(CHECKPOINT)
    env=os.environ.copy()
    env["AWFUL_GN_FAIL_STAGE"]=stage
    result=subprocess.run([sys.executable,str(REBUILD)],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    assert result.returncode!=0,(stage,result.returncode)
    assert state(BUNDLE)==bundle_before,(stage,"canonical bundle changed")
    assert state(CHECKPOINT)==checkpoint_before,(stage,"checkpoint changed")
    print("OK",stage)
