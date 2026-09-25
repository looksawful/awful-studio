from pathlib import Path
import json, os, shutil, subprocess, sys, tempfile

ROOT=Path(r"F:\AWFUL_ASSETS")
CAT=ROOT/"_catalog"
CODE=Path(__file__).resolve().parent
BLENDER=Path(os.environ.get("AWFUL_BLENDER",shutil.which("blender") or ""))
if not BLENDER.is_file():
    raise FileNotFoundError("Set AWFUL_BLENDER to the Blender 5.2 executable")
BUNDLE=ROOT/"3D"/"AssetBundles"/"AWFUL"/"GeometryNodes"/"blender_official_curated.blend"
CATALOG=ROOT/"3D"/"blender_assets.cats.txt"
FINAL_SUMMARY=CAT/"geometry_nodes_curated_summary.json"
FINAL_SOURCE=BUNDLE.parent/"SOURCE.txt"
FINAL_PREVIEWS=CAT/"previews"/"geometry_nodes"
FINAL_MANIFEST=CAT/"geometry_nodes_preview_manifest.json"
CHECKPOINT=ROOT/"_checkpoints"/"geometry_nodes_curated_last_good"/"blender_official_curated.blend"
FAIL=os.environ.get("AWFUL_GN_FAIL_STAGE","")

def run(args, env=None):
    subprocess.run([str(x) for x in args], check=True, env=env)

def fail(stage):
    if FAIL==stage:
        raise RuntimeError(f"injected failure after {stage}")

def validate(bundle):
    code=("import bpy,sys; bpy.ops.wm.open_mainfile(filepath=r'"+str(bundle)+"',load_ui=False,use_scripts=False); "
          "a=[x for x in bpy.data.node_groups if x.asset_data]; "
          "bad=[x.name for x in a if not x.preview or tuple(x.preview.image_size)!=(128,128)]; "
          "print('ASSETS',len(a),'BAD_PREVIEWS',bad); sys.exit(0 if len(a)==22 and not bad else 1)")
    run([BLENDER,"--background","--factory-startup","--python-exit-code","1","--python-expr",code])

def replace_set(replacements, backup_dir):
    done=[]
    try:
        for source,target in replacements:
            backup=backup_dir/str(len(done))
            existed=target.exists()
            if existed:
                if target.is_dir():
                    shutil.copytree(target,backup)
                else:
                    backup.parent.mkdir(parents=True,exist_ok=True)
                    shutil.copy2(target,backup)
            target.parent.mkdir(parents=True,exist_ok=True)
            if target.exists():
                if target.is_dir():
                    shutil.rmtree(target)
                else:
                    target.unlink()
            if source.is_dir():
                shutil.copytree(source,target)
            else:
                os.replace(source,target)
            done.append((target,backup,existed))
    except Exception:
        for target,backup,existed in reversed(done):
            if target.exists():
                shutil.rmtree(target) if target.is_dir() else target.unlink()
            if existed:
                if backup.is_dir():
                    shutil.copytree(backup,target)
                else:
                    target.parent.mkdir(parents=True,exist_ok=True)
                    shutil.copy2(backup,target)
        raise

with tempfile.TemporaryDirectory(dir=BUNDLE.parent,prefix=".awful-gn-stage-") as td:
    stage=Path(td)
    staged_bundle=stage/"blender_official_curated.blend"
    staged_summary=stage/"summary.json"
    staged_source=stage/"SOURCE.txt"
    staged_previews=stage/"cards"
    staged_manifest=stage/"manifest.json"

    env=os.environ.copy()
    env.update({
        "AWFUL_GN_DEST":str(staged_bundle),
        "AWFUL_GN_SUMMARY":str(staged_summary),
        "AWFUL_GN_SOURCE":str(staged_source),
    })
    run([BLENDER,"--background","--factory-startup","--python-exit-code","1","--python",CODE/"build_curated_geometry_nodes.py"],env)
    fail("build")

    run([sys.executable,CODE/"make_geometry_node_cards.py",staged_summary,staged_previews,staged_manifest])
    fail("cards")

    run([BLENDER,"--background","--factory-startup","--python-exit-code","1","--python",CODE/"embed_geometry_node_previews.py","--",staged_bundle,staged_manifest])
    fail("embed")

    validate(staged_bundle)
    fail("validate")

    summary=json.loads(staged_summary.read_text(encoding="utf-8"))
    assert summary["asset_count"]==22 and not summary["errors"],summary

    lines=summary.pop("catalog_lines",[])
    staged_catalog=stage/"blender_assets.cats.txt"
    text=CATALOG.read_text(encoding="utf-8-sig")
    existing={line.split(":",1)[0].lower() for line in text.splitlines() if ":" in line and not line.lstrip().startswith("#")}
    additions=[line for line in lines if line.split(":",1)[0].lower() not in existing]
    staged_catalog.write_text(text.rstrip()+("\n"+"\n".join(additions) if additions else "")+"\n",encoding="utf-8")
    fail("publish_catalog")

    publish_previews=stage/"publish_previews"
    shutil.copytree(staged_previews,publish_previews)
    fail("publish_previews")

    publish_manifest=stage/"publish_manifest.json"
    shutil.copy2(staged_manifest,publish_manifest)
    fail("publish_manifest")

    publish_source=stage/"publish_SOURCE.txt"
    shutil.copy2(staged_source,publish_source)
    fail("publish_source")

    summary["bundle"]=str(BUNDLE)
    summary["catalogs_added"]=len(additions)
    summary["size_mb"]=round(staged_bundle.stat().st_size/1024**2,2)
    publish_summary=stage/"publish_summary.json"
    publish_summary.write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
    fail("publish_summary")

    publish_checkpoint=stage/"checkpoint.blend"
    if BUNDLE.exists():
        shutil.copy2(BUNDLE,publish_checkpoint)
    else:
        shutil.copy2(staged_bundle,publish_checkpoint)
    fail("publish_checkpoint")
    fail("publish_bundle")

    replacements=[
        (staged_catalog,CATALOG),
        (publish_previews,FINAL_PREVIEWS),
        (publish_manifest,FINAL_MANIFEST),
        (publish_source,FINAL_SOURCE),
        (publish_summary,FINAL_SUMMARY),
        (publish_checkpoint,CHECKPOINT),
        (staged_bundle,BUNDLE),
    ]
    replace_set(replacements,stage/"rollback")

print("OK: staged publish complete; 22 curated Geometry Nodes assets with 22 previews")
