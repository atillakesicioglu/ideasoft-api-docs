"""Commerce domain grouping layer."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from .constants import COMMERCE_GROUPS, HTTP_METHODS, STORE_BASE_URL
from .openapi_normalize import normalize_spec_urls


def _merge_paths(target: dict, source_paths: dict) -> None:
    for path, path_item in source_paths.items():
        target.setdefault(path, {}).update(path_item)


def _merge_schemas(target: dict, source: dict) -> None:
    for key, schema in source.get("components", {}).get("schemas", {}).items():
        target.setdefault("components", {}).setdefault("schemas", {})[key] = schema


def build_commerce_layer(specs: dict[str, dict], domains_dir: Path, commerce_dir: Path) -> dict[str, Any]:
    commerce_dir.mkdir(parents=True, exist_ok=True)
    index: dict[str, Any] = {"generated_at": None, "groups": []}

    # domain slug -> (api_name, spec fragment path)
    domain_sources: dict[str, list[tuple[str, dict]]] = defaultdict(list)
    for api_name in ("admin-api", "store-api"):
        api_domains = domains_dir / api_name
        if not api_domains.exists():
            continue
        for domain_file in api_domains.glob("*.json"):
            if domain_file.name == "_index.json":
                continue
            slug = domain_file.stem
            fragment = json.loads(domain_file.read_text(encoding="utf-8"))
            domain_sources[slug].append((api_name, fragment))

    for group_name, domain_slugs in COMMERCE_GROUPS.items():
        merged: dict[str, Any] = {
            "openapi": "3.0.0",
            "info": {
                "title": f"Ideasoft Commerce — {group_name}",
                "version": specs.get("admin-api", {}).get("info", {}).get("version", "1.0.0"),
                "x-commerce-group": group_name,
                "description": f"AI-friendly commerce grouping: {group_name}",
            },
            "servers": [{"url": STORE_BASE_URL}],
            "paths": {},
            "components": {"schemas": {}, "securitySchemes": {}},
        }
        op_count = 0
        included_domains: list[str] = []

        for slug in domain_slugs:
            for api_name, fragment in domain_sources.get(slug, []):
                _merge_paths(merged["paths"], fragment.get("paths", {}))
                _merge_schemas(merged, fragment)
                if fragment.get("components", {}).get("securitySchemes"):
                    merged["components"]["securitySchemes"].update(fragment["components"]["securitySchemes"])
                included_domains.append(f"{api_name}/{slug}")
                op_count += sum(
                    1
                    for pi in fragment.get("paths", {}).values()
                    if isinstance(pi, dict)
                    for m in pi
                    if m in HTTP_METHODS
                )

        if not merged["paths"]:
            continue

        out_path = commerce_dir / f"{group_name}.json"
        with out_path.open("w", encoding="utf-8") as f:
            json.dump(merged, f, ensure_ascii=False, separators=(",", ":"))

        index["groups"].append(
            {
                "name": group_name,
                "file": f"{group_name}.json",
                "operations": op_count,
                "paths": len(merged["paths"]),
                "source_domains": included_domains,
            }
        )

    index_path = commerce_dir / "_index.json"
    index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
    return index
