"""Ideasoft API dokümantasyon pipeline — extract, split, validate metadata, reports."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

# extract_docs ve lib modüllerini yeniden kullan
_SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPTS))
from lib.commerce_layer import build_commerce_layer  # noqa: E402
from lib.constants import STORE_BASE_URL  # noqa: E402
from lib.metadata_writers import (  # noqa: E402
    write_capabilities_matrix,
    write_commerce_tools,
    write_domain_stats,
    write_mcp_endpoint_candidates,
)
from lib.openapi_normalize import normalize_spec_urls  # noqa: E402
from extract_docs import (  # noqa: E402
    PROJECTS,
    build_markdown,
    build_openapi_from_project,
    count_endpoints,
    clean_description,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE_URL = "https://apidoc.ideasoft.dev"
REPO_URL = "https://github.com/atillakesicioglu/ideasoft-api-docs"
EXTRACTED_AT = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

HTTP_METHODS = {"get", "post", "put", "patch", "delete"}


def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "other"


def path_domain(api_name: str, path: str) -> str:
    parts = [p for p in path.strip("/").split("/") if p]
    if len(parts) > 1 and parts[0] in {"admin-api", "api"}:
        return slugify(parts[1])
    return slugify(parts[0]) if parts else "root"


def collect_schema_refs(obj: Any, refs: set[str]) -> None:
    if isinstance(obj, dict):
        ref = obj.get("$ref")
        if isinstance(ref, str) and ref.startswith("#/components/schemas/"):
            refs.add(ref.rsplit("/", 1)[-1])
        for value in obj.values():
            collect_schema_refs(value, refs)
    elif isinstance(obj, list):
        for item in obj:
            collect_schema_refs(item, refs)


def add_operation_metadata(
    operation: dict,
    *,
    api_name: str,
    method: str,
    path: str,
    node_slug: str | None,
    project_id: str,
) -> dict:
    operation["x-source"] = {
        "provider": "ideasoft",
        "api": api_name,
        "documentation": SOURCE_URL,
        "stoplight_project_id": project_id,
        "stoplight_node_slug": node_slug,
        "extracted_at": EXTRACTED_AT,
        "mirror_repository": REPO_URL,
    }
    operation["x-verification"] = {
        "status": "documentation-only",
        "live_tested": False,
        "last_verified_at": None,
        "notes": "Community mirror — not validated against a live Ideasoft store.",
    }
    operation.setdefault("operationId", operation.get("operationId") or f"{method}_{path}".replace("/", "_"))
    return operation


def attach_metadata_to_spec(spec: dict, api_name: str, project_id: str, slug_map: dict[str, str]) -> None:
    for path, path_item in spec.get("paths", {}).items():
        if not isinstance(path_item, dict):
            continue
        for method, operation in path_item.items():
            if method not in HTTP_METHODS or not isinstance(operation, dict):
                continue
            op_id = operation.get("operationId", "")
            node_slug = slug_map.get(f"{method.upper()} {path}") or slug_map.get(op_id)
            add_operation_metadata(operation, api_name=api_name, method=method, path=path, node_slug=node_slug, project_id=project_id)


def build_slug_map(cache_dir: Path, project_id: str) -> dict[str, str]:
    mapping: dict[str, str] = {}
    if not cache_dir.exists():
        return mapping
    for cache_file in cache_dir.glob(f"{project_id}__*.json"):
        slug = cache_file.stem.split("__", 1)[-1]
        try:
            node = json.loads(cache_file.read_text(encoding="utf-8"))
            if node.get("type") != "http_operation":
                continue
            data = json.loads(node["data"])
            method = data.get("method", "").upper()
            path = data.get("path", "")
            mapping[f"{method} {path}"] = slug
            if data.get("id"):
                mapping[data["id"]] = slug
        except (json.JSONDecodeError, KeyError):
            continue
    return mapping


def split_spec_by_domain(spec: dict, api_name: str) -> dict[str, dict]:
    domains: dict[str, dict] = defaultdict(lambda: {"paths": {}})
    all_components = spec.get("components", {})
    all_schemas = all_components.get("schemas", {})

    for path, path_item in spec.get("paths", {}).items():
        domain = path_domain(api_name, path)
        domains[domain]["paths"][path] = path_item

    result: dict[str, dict] = {}
    for domain, chunk in domains.items():
        refs: set[str] = set()
        collect_schema_refs(chunk["paths"], refs)
        domain_components = {
            "schemas": {k: all_schemas[k] for k in refs if k in all_schemas},
            "securitySchemes": all_components.get("securitySchemes", {}),
        }
        domain_spec = {
            "openapi": spec.get("openapi", "3.0.0"),
            "info": {
                **spec.get("info", {}),
                "title": f"{spec.get('info', {}).get('title', api_name)} — {domain}",
                "x-domain": domain,
                "x-parent-api": api_name,
            },
            "servers": spec.get("servers", []),
            "security": spec.get("security", []),
            "paths": chunk["paths"],
            "components": domain_components,
        }
        result[domain] = normalize_spec_urls(domain_spec, api_name)
    return result


def compute_stats(specs: dict[str, dict]) -> dict:
    stats: dict[str, Any] = {
        "generated_at": EXTRACTED_AT,
        "source": SOURCE_URL,
        "apis": {},
        "totals": {"operations": 0, "paths": 0, "schemas": 0, "domains": 0},
    }
    for api_name, spec in specs.items():
        paths = spec.get("paths", {})
        operations = count_endpoints(spec)
        schemas = len(spec.get("components", {}).get("schemas", {}))
        domains = len(split_spec_by_domain(spec, api_name)) if paths else 0
        stats["apis"][api_name] = {
            "operations": operations,
            "paths": len(paths),
            "schemas": schemas,
            "domains": domains,
            "title": spec.get("info", {}).get("title"),
            "version": spec.get("info", {}).get("version"),
        }
        stats["totals"]["operations"] += operations
        stats["totals"]["paths"] += len(paths)
        stats["totals"]["schemas"] += schemas
        stats["totals"]["domains"] += domains
    return stats


def endpoint_manifest(specs: dict[str, dict]) -> list[dict]:
    rows: list[dict] = []
    for api_name, spec in specs.items():
        for path, path_item in spec.get("paths", {}).items():
            if not isinstance(path_item, dict):
                continue
            for method, operation in path_item.items():
                if method not in HTTP_METHODS:
                    continue
                rows.append(
                    {
                        "api": api_name,
                        "method": method.upper(),
                        "path": path,
                        "operation_id": operation.get("operationId"),
                        "summary": operation.get("summary"),
                        "domain": path_domain(api_name, path),
                    }
                )
    rows.sort(key=lambda r: (r["api"], r["path"], r["method"]))
    return rows


def diff_endpoints(old: list[dict], new: list[dict]) -> dict:
    def key(r: dict) -> str:
        return f"{r['api']}:{r['method']}:{r['path']}"

    old_map = {key(r): r for r in old}
    new_map = {key(r): r for r in new}
    added = [new_map[k] for k in new_map.keys() - old_map.keys()]
    removed = [old_map[k] for k in old_map.keys() - new_map.keys()]
    changed = []
    for k in old_map.keys() & new_map.keys():
        if old_map[k].get("summary") != new_map[k].get("summary"):
            changed.append({"before": old_map[k], "after": new_map[k]})
    return {"added": added, "removed": removed, "changed": changed}


def write_endpoint_diff_report(diff: dict, path: Path) -> None:
    lines = [
        "# Endpoint Diff Report",
        "",
        f"**Generated:** {EXTRACTED_AT}",
        "",
        f"- Added: **{len(diff['added'])}**",
        f"- Removed: **{len(diff['removed'])}**",
        f"- Changed: **{len(diff['changed'])}**",
        "",
    ]
    if diff["added"]:
        lines.extend(["## Added", ""])
        for row in diff["added"][:200]:
            lines.append(f"- `{row['method']}` `{row['path']}` ({row['api']}) — {row.get('summary', '')}")
        if len(diff["added"]) > 200:
            lines.append(f"- ... and {len(diff['added']) - 200} more")
        lines.append("")
    if diff["removed"]:
        lines.extend(["## Removed", ""])
        for row in diff["removed"][:200]:
            lines.append(f"- `{row['method']}` `{row['path']}` ({row['api']})")
        lines.append("")
    if diff["changed"]:
        lines.extend(["## Changed summaries", ""])
        for item in diff["changed"][:100]:
            b, a = item["before"], item["after"]
            lines.append(f"- `{a['method']}` `{a['path']}`: `{b.get('summary')}` → `{a.get('summary')}`")
        lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def update_changelog(diff: dict, stats: dict, path: Path) -> None:
    entry = [
        f"## [{EXTRACTED_AT[:10]}] — Automated sync",
        "",
        f"- Operations: **{stats['totals']['operations']}**",
        f"- Paths: **{stats['totals']['paths']}**",
        f"- Schemas: **{stats['totals']['schemas']}**",
        f"- Domains: **{stats['totals']['domains']}**",
        f"- Added endpoints: {len(diff['added'])}",
        f"- Removed endpoints: {len(diff['removed'])}",
        f"- Changed summaries: {len(diff['changed'])}",
        "",
    ]
    if path.exists():
        content = path.read_text(encoding="utf-8")
        marker = "## ["
        idx = content.find(marker)
        if idx != -1:
            content = content[:idx] + "\n".join(entry) + "\n" + content[idx:]
        else:
            content = content.rstrip() + "\n\n" + "\n".join(entry)
    else:
        content = "# Changelog\n\nCommunity mirror changelog for Ideasoft API docs.\n\n" + "\n".join(entry)
    path.write_text(content, encoding="utf-8")


def save_json(path: Path, data: Any, compact: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        if compact:
            json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
        else:
            json.dump(data, f, ensure_ascii=False, indent=2)


def write_domain_specs(spec: dict, api_name: str, out_dir: Path) -> list[str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    domains = split_spec_by_domain(spec, api_name)
    written: list[str] = []
    index: dict[str, Any] = {"api": api_name, "domains": []}
    for domain, domain_spec in sorted(domains.items()):
        rel = f"{domain}.json"
        target = out_dir / rel
        save_json(target, domain_spec, compact=True)
        ops = count_endpoints(domain_spec)
        index["domains"].append({"name": domain, "file": rel, "operations": ops, "paths": len(domain_spec["paths"])})
        written.append(rel)
    save_json(out_dir / "_index.json", index)
    return written


def write_bundled_artifact(spec: dict, path: Path) -> str:
    save_json(path, spec, compact=True)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    meta = {
        "file": path.name,
        "sha256": digest,
        "bytes": path.stat().st_size,
        "generated_at": EXTRACTED_AT,
        "operations": count_endpoints(spec),
        "paths": len(spec.get("paths", {})),
        "schemas": len(spec.get("components", {}).get("schemas", {})),
    }
    save_json(path.with_suffix(".meta.json"), meta)
    return digest


def run_redocly_lint(root: Path) -> bool:
    config = root / "redocly.yaml"
    if not config.exists():
        return True
    try:
        subprocess.run(["npm", "ci"], cwd=root, check=True, capture_output=True, text=True)
        subprocess.run(
            ["npm", "run", "lint"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        print("Redocly lint warning:", exc)
        return False


def build_llms_txt(stats: dict, root: Path) -> None:
    totals = stats["totals"]
    content = f"""# Ideasoft API

> Community mirror of Ideasoft Admin API, Store API and Webhooks documentation.

⚠️ **Unofficial community mirror** — see README.md.

Base URL: `{STORE_BASE_URL}`
Admin paths: `/admin-api/...` | Store paths: `/api/...`
Source: {SOURCE_URL}

## Stats (auto-generated)

- Operations: {totals['operations']}
- Paths: {totals['paths']}
- Schemas: {totals['schemas']}
- Domains: {totals['domains']}

## Docs

- [Authentication]({REPO_URL}/blob/main/docs/AUTHENTICATION.md)
- [Admin API]({REPO_URL}/blob/main/docs/admin-api.md)
- [Store API]({REPO_URL}/blob/main/docs/store-api.md)
- [Webhooks]({REPO_URL}/blob/main/docs/webhooks.md)
- [Capabilities matrix]({REPO_URL}/blob/main/metadata/capabilities.yaml)
- [Commerce tools (curated MCP)]({REPO_URL}/blob/main/metadata/commerce-tools.yaml)
- [MCP endpoint candidates (raw)]({REPO_URL}/blob/main/metadata/mcp-endpoint-candidates.yaml)
- [Raw domain OpenAPI]({REPO_URL}/blob/main/openapi/domains/)
- [Commerce grouped OpenAPI]({REPO_URL}/blob/main/openapi/commerce/)
- [Bundled release specs]({REPO_URL}/releases/latest)
"""
    (root / "llms.txt").write_text(content, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--only", choices=list(PROJECTS.keys()))
    parser.add_argument("--skip-extract", action="store_true", help="Use existing bundled specs in artifacts/")
    parser.add_argument("--skip-lint", action="store_true")
    args = parser.parse_args()
    root = args.root
    cache_dir = root / ".cache" / "nodes"
    artifacts_dir = root / "artifacts" / "bundled"
    domains_dir = root / "openapi" / "domains"
    commerce_dir = root / "openapi" / "commerce"
    metadata_dir = root / "metadata"
    reports_dir = root / "reports"
    docs_dir = root / "docs"

    artifacts_dir.mkdir(parents=True, exist_ok=True)
    metadata_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    targets = [args.only] if args.only else list(PROJECTS.keys())
    specs: dict[str, dict] = {}

    manifest_path = metadata_dir / "endpoint-manifest.json"
    old_manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else []

    for key in targets:
        print(f"Processing {key}...")
        meta = PROJECTS[key]
        if args.skip_extract and (artifacts_dir / f"{key}.json").exists():
            spec = json.loads((artifacts_dir / f"{key}.json").read_text(encoding="utf-8"))
            if meta.get("service_slug"):
                slug_map = build_slug_map(cache_dir, meta["project_id"])
                attach_metadata_to_spec(spec, key, meta["project_id"], slug_map)
        else:
            spec = build_openapi_from_project(meta, cache_dir)
            if meta.get("service_slug"):
                slug_map = build_slug_map(cache_dir, meta["project_id"])
                attach_metadata_to_spec(spec, key, meta["project_id"], slug_map)

        if key != "webhooks":
            spec = normalize_spec_urls(spec, key)
            write_bundled_artifact(spec, artifacts_dir / f"{key}.json")
        specs[key] = spec

        if key != "webhooks":
            write_domain_specs(spec, key, domains_dir / key)
        (docs_dir / f"{key}.md").write_text(build_markdown(spec, meta), encoding="utf-8")

    stats = compute_stats(specs)
    save_json(metadata_dir / "stats.json", stats)

    new_manifest = endpoint_manifest(specs)
    save_json(manifest_path, new_manifest)
    diff = diff_endpoints(old_manifest, new_manifest)
    write_endpoint_diff_report(diff, reports_dir / "endpoint-diff.md")
    update_changelog(diff, stats, root / "CHANGELOG.md")
    write_domain_stats(specs, path_domain, metadata_dir / "domain-stats.yaml")
    commerce_tools = write_commerce_tools(specs, metadata_dir / "commerce-tools.yaml")
    write_capabilities_matrix(specs, commerce_tools, metadata_dir / "capabilities.yaml")
    write_mcp_endpoint_candidates(specs, metadata_dir / "mcp-endpoint-candidates.yaml", slugify, limit_per_api=300)
    build_commerce_layer(specs, domains_dir, commerce_dir)
    build_llms_txt(stats, root)

    # openapi/index.json — raw domains + commerce groups
    index = {
        "raw_domains": {
            api: {"root": f"openapi/domains/{api}/_index.json"}
            for api in specs
            if api != "webhooks" and (domains_dir / api).exists()
        },
        "commerce_groups": {"root": "openapi/commerce/_index.json"},
        "bundled_release": {
            api: f"artifacts/bundled/{api}.json"
            for api in ("admin-api", "store-api")
        },
    }
    save_json(root / "openapi" / "index.json", index)

    # Eski dosya adı kaldırıldı (v2.1)
    legacy_mcp = metadata_dir / "mcp-tools-candidate.yaml"
    if legacy_mcp.exists():
        legacy_mcp.unlink()

    if not args.skip_lint:
        run_redocly_lint(root)

    print("Done.")
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
