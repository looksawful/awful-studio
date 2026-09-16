# SPDX-License-Identifier: GPL-3.0-or-later
"""Declarative integration catalog for optional Blender tooling.

No add-on is downloaded, installed or enabled by importing this module. The
catalog exists so UI/tooling can report what AWFUL Studio knows how to coexist
with without taking ownership of a user's Blender profile.
"""
from __future__ import annotations

from pathlib import Path
import json

_MANIFEST = Path(__file__).with_name("integrations") / "blender_tools.json"
_CONTENT_POLICY = Path(__file__).with_name("integrations") / "blender_content_policy.json"
_ALLOWED_AUTOMATION = {"builtin", "extension-repository", "manual"}
_ALLOWED_TIERS = {"core", "useful", "optional"}


def load_tool_catalog(path: Path = _MANIFEST) -> tuple[dict, ...]:
    data = json.loads(path.read_text(encoding="utf-8"))
    tools = data.get("tools")
    if not isinstance(tools, list):
        raise ValueError("blender tool manifest must contain a tools list")
    ids: set[str] = set()
    result = []
    for item in tools:
        if not isinstance(item, dict) or not item.get("id"):
            raise ValueError("every blender tool entry needs an id")
        if item["id"] in ids:
            raise ValueError(f"duplicate blender tool id: {item['id']}")
        ids.add(item["id"])
        if item.get("automation") not in _ALLOWED_AUTOMATION:
            raise ValueError(f"invalid automation policy for {item['id']}")
        if item.get("tier") not in _ALLOWED_TIERS:
            raise ValueError(f"invalid tooling tier for {item['id']}")
        purposes = item.get("purpose")
        if not isinstance(purposes, list) or not purposes:
            raise ValueError(f"tool {item['id']} needs at least one purpose")
        result.append(item)
    return tuple(result)


def load_content_policy(path: Path = _CONTENT_POLICY) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema") != 1:
        raise ValueError("unsupported blender content policy schema")
    if data.get("policy") != "awful-owned-declarative-content-no-user-profile-overwrite":
        raise ValueError("unexpected blender content policy")
    return data
