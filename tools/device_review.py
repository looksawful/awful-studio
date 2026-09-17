from __future__ import annotations

import argparse
import hashlib
import html
import json
from pathlib import Path
import re
import subprocess
import sys

VIEWS = ("front", "back", "left", "right", "top", "bottom", "front_3q", "back_3q")
MODES = ("material", "clay", "wire", "normals", "silhouette")


def candidate_format(path: Path) -> str | None:
    suffix = path.suffix.lower()
    if suffix == ".blend":
        return "BLEND"
    if suffix == ".glb":
        return "GLB"
    return None


def infer_identity(path: Path) -> dict[str, str]:
    name = path.stem.lower()
    if "iphone_17" in name:
        device = "iphone_17"
    elif "ipad_pro_11" in name:
        device = "ipad_pro_11"
    elif "ipad_pro_13" in name:
        device = "ipad_pro_13"
    elif "macbook_pro_14" in name:
        device = "macbook_pro_14"
    else:
        device = "unknown"
    match = re.search(r"(?:^|_)v(\d+)(?:_|$)", name)
    version = f"v{match.group(1)}" if match else "unversioned"
    return {"device": device, "version": version}

def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def inventory(roots: list[Path]) -> list[dict]:
    by_hash: dict[str, dict] = {}
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            fmt = candidate_format(path)
            if not fmt or not path.is_file():
                continue
            digest = sha256(path)
            if digest in by_hash:
                by_hash[digest]["provenance"].append(str(path.resolve()))
                continue
            identity = infer_identity(path)
            by_hash[digest] = {
                **identity,
                "format": fmt,
                "sha256": digest,
                "size": path.stat().st_size,
                "source": str(path.resolve()),
                "provenance": [str(path.resolve())],
            }
    return sorted(by_hash.values(), key=lambda x: (x["device"], x["version"], x["format"], x["sha256"]))


def slug(item: dict) -> str:
    return f'{item["device"]}__{item["version"]}__{item["format"].lower()}__{item["sha256"][:10]}'


def render_command(blender: Path, renderer: Path, item: dict, output: Path, size: int) -> list[str]:
    common = ["--background", "--python", str(renderer), "--", "--input", item["source"], "--output", str(output), "--size", str(size)]
    if item["format"] == "BLEND":
        return [str(blender), item["source"], *common]
    return [str(blender), "--factory-startup", *common]

def write_html(items: list[dict], output: Path) -> None:
    cards = []
    for item in items:
        sid = slug(item)
        thumbs = "".join(
            f'<figure><img loading="lazy" src="{sid}/{mode}__{view}.png"><figcaption>{mode} · {view}</figcaption></figure>'
            for mode in MODES for view in VIEWS
        )
        provenance = "<br>".join(html.escape(p) for p in item["provenance"])
        cards.append(f'''<article class="card" data-id="{sid}">
<h2>{html.escape(item['device'])} · {html.escape(item['version'])} · {item['format']}</h2>
<p class="hash">{item['sha256'][:16]} · {item['size'] / 1048576:.1f} MB</p>
<div class="actions"><button data-v="KEEP">KEEP</button><button data-v="MAYBE">MAYBE</button><button data-v="REJECT">REJECT</button></div>
<div class="grid">{thumbs}</div><details><summary>provenance ({len(item['provenance'])})</summary>{provenance}</details></article>''')
    body = "\n".join(cards)
    document = f'''<!doctype html><meta charset="utf-8"><title>AWFUL device review</title>
<style>body{{font:14px system-ui;margin:20px;background:#fff;color:#111}}header{{position:sticky;top:0;background:#fffd;padding:12px 0;z-index:2}}.card{{border-top:2px solid;padding:18px 0}}.hash,figcaption,details{{color:#666}}.actions button{{margin:0 8px 12px 0;padding:8px 14px}}.actions button.on{{outline:3px solid #111}}.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:8px}}figure{{margin:0}}img{{width:100%;aspect-ratio:1;object-fit:contain;background:#eee}}figcaption{{font-size:11px}}details{{margin-top:10px;word-break:break-all}}</style>
<header><b>AWFUL device review</b> · {len(items)} unique candidates · decisions stay in this browser</header>{body}
<script>const cards=[...document.querySelectorAll('.card')];function val(c){{return localStorage.getItem('awful-review:'+c.dataset.id)}}function refresh(){{let n=cards.filter(c=>val(c)).length;progress.textContent=n+'/'+cards.length+' decided';cards.forEach(c=>c.querySelectorAll('.actions button').forEach(b=>b.classList.toggle('on',b.dataset.v===val(c))))}}function filterCards(f){{cards.forEach(c=>c.hidden=f==='ALL'?false:f==='UNDECIDED'?!val(c):val(c)!==f)}}function showMode(){{let m=mode.value;cards.forEach(c=>c.querySelectorAll('figure').forEach(f=>f.hidden=!f.textContent.startsWith(m+' ?')))}}cards.forEach(c=>c.querySelectorAll('.actions button').forEach(b=>b.onclick=()=>{{localStorage.setItem('awful-review:'+c.dataset.id,b.dataset.v);refresh();filterCards('UNDECIDED')}}));mode.onchange=showMode;refresh();showMode();</script>'''
    (output / "index.html").write_text(document, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build fast device visual-review sheets")
    parser.add_argument("--root", action="append", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--blender", type=Path)
    parser.add_argument("--size", type=int, default=640)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--inventory-only", action="store_true")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    items = inventory(args.root)
    if args.limit:
        items = items[: args.limit]
    (args.output / "manifest.json").write_text(json.dumps(items, indent=2), encoding="utf-8")
    write_html(items, args.output)
    if args.inventory_only:
        print(f"Inventoried {len(items)} unique candidates")
        return 0
    if not args.blender:
        parser.error("--blender is required unless --inventory-only is used")
    renderer = Path(__file__).with_name("device_review_blender.py")
    for index, item in enumerate(items, 1):
        target = args.output / slug(item)
        target.mkdir(exist_ok=True)
        print(f"[{index}/{len(items)}] {slug(item)}", flush=True)
        subprocess.run(render_command(args.blender, renderer, item, target, args.size), check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())