import json
import re
import sys
from pathlib import Path

site = Path(sys.argv[1])
out = Path(sys.argv[2])
logos_text = (site / "src/data/clients.ts").read_text(encoding="utf-8")
clients_text = (site / "src/data/catalog/clients.ts").read_text(encoding="utf-8")

client_names = dict(re.findall(
    r'id:\s*"([^"]+)"\s*,\s*name:\s*"([^"]+)"',
    clients_text,
))

items = {}
for client_id, file_id in re.findall(
    r'defineClientLogo\("([^"]+)",\s*"(\d+)"',
    logos_text,
):
    items[file_id] = {"id": client_id, "name": client_names.get(client_id, client_id)}
for client_id, name, file_id in re.findall(
    r'\{\s*id:\s*"([^"]+)"\s*,\s*name:\s*"([^"]+)"\s*,\s*file:\s*"(\d+)"',
    logos_text,
):
    items[file_id] = {"id": client_id, "name": name}

payload = {
    "logos": [
        {"file": file_id, **items[file_id]}
        for file_id in sorted(items)
    ]
}
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"AWFUL_CATALOG:{len(payload['logos'])}")
