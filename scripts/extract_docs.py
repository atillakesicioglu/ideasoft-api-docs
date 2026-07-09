"""Ideasoft Stoplight API dokümantasyonunu OpenAPI + Markdown olarak üretir."""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

import requests
import yaml

PROJECTS = {
    "admin-api": {
        "project_id": "cHJqOjIzODAzMw",
        "service_slug": "vybqnioh8g80n-ideashop-api",
        "title": "Ideasoft Admin API",
        "base_path_note": "https://magaza-adiniz.myideasoft.com/admin-api",
    },
    "store-api": {
        "project_id": "cHJqOjI2NjA2OA",
        "service_slug": "sjv3ev4jzsfqj-ideashop-api",
        "title": "Ideasoft Store API",
        "base_path_note": "https://magaza-adiniz.myideasoft.com/api",
    },
    "webhooks": {
        "project_id": "cHJqOjE0NzQyOQ",
        "article_slug": "5cc9374300b99-webhooks",
        "title": "Ideasoft Webhooks",
        "base_path_note": "Webhook bildirimleri",
    },
}

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "ideasoft-api-docs-extractor/1.0"})


def clean_description(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"<a[^>]*>.*?</a>", "", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("__", "")
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def fetch_json(url: str, retries: int = 3) -> Any:
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            response = SESSION.get(url, timeout=60)
            response.raise_for_status()
            return response.json()
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            time.sleep(1 + attempt)
    raise RuntimeError(f"Failed to fetch {url}: {last_error}")


def walk_toc(nodes: list[dict], found: list[dict]) -> None:
    for node in nodes:
        if not isinstance(node, dict):
            continue
        node_type = node.get("type") or node.get("nodeType")
        if node_type in {"http_operation", "http_service", "article"}:
            found.append(
                {
                    "type": node_type,
                    "slug": node.get("slug") or node.get("id"),
                    "title": node.get("title") or node.get("name"),
                }
            )
        walk_toc(node.get("children") or node.get("items") or [], found)


def fetch_node(project_id: str, slug: str, cache_dir: Path | None = None) -> dict:
    if cache_dir:
        cache_file = cache_dir / f"{project_id}__{slug}.json"
        if cache_file.exists():
            return json.loads(cache_file.read_text(encoding="utf-8"))
    url = f"https://stoplight.io/api/v1/projects/{project_id}/nodes/{slug}?branch=main"
    data = fetch_json(url)
    if cache_dir:
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache_file.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return data


def deep_merge(base: dict, extra: dict) -> dict:
    for key, value in extra.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            deep_merge(base[key], value)
        elif key in base and isinstance(base[key], list) and isinstance(value, list):
            base[key].extend(value)
        else:
            base[key] = value
    return base


def collect_bundled_map(*bundled_sources: dict | None) -> dict[str, Any]:
    merged: dict[str, Any] = {}
    for source in bundled_sources:
        if isinstance(source, dict):
            merged.update(source)
    return merged


def resolve_bundled_refs(obj: Any, bundled: dict[str, Any], _stack: set[str] | None = None) -> Any:
    if _stack is None:
        _stack = set()
    if isinstance(obj, dict):
        ref = obj.get("$ref")
        if isinstance(ref, str) and ref.startswith("#/__bundled__/"):
            key = ref.rsplit("/", 1)[-1]
            if key in _stack:
                return obj
            target = bundled.get(key)
            if target is None:
                return obj
            _stack.add(key)
            resolved = resolve_bundled_refs(target, bundled, _stack)
            _stack.remove(key)
            return resolved
        return {key: resolve_bundled_refs(value, bundled, _stack) for key, value in obj.items()}
    if isinstance(obj, list):
        return [resolve_bundled_refs(item, bundled, _stack) for item in obj]
    return obj


def replace_bundled_refs(obj: Any, bundled: dict[str, Any]) -> Any:
  """$ref'leri inline etmek yerine components altına yönlendirir."""
  if isinstance(obj, dict):
    ref = obj.get("$ref")
    if isinstance(ref, str) and ref.startswith("#/__bundled__/"):
      key = ref.rsplit("/", 1)[-1]
      item = bundled.get(key)
      if isinstance(item, dict) and item.get("name") and item.get("in"):
        return replace_bundled_refs(item, bundled)
      if isinstance(item, dict) and item.get("name") and "schema" in item:
        return replace_bundled_refs(item, bundled)
      return {"$ref": f"#/components/schemas/{key}"}
    return {key: replace_bundled_refs(value, bundled) for key, value in obj.items()}
  if isinstance(obj, list):
    return [replace_bundled_refs(item, bundled) for item in obj]
  return obj


def normalize_components(spec: dict[str, Any], bundled: dict[str, Any]) -> dict[str, Any]:
  components = spec.setdefault("components", {})
  schemas = components.setdefault("schemas", {})
  security_schemes = components.setdefault("securitySchemes", {})

  for key, value in bundled.items():
    if not isinstance(value, dict):
      continue
    resolved = resolve_bundled_refs(value, bundled)
    value_type = resolved.get("type")
    if value_type in {"apiKey", "http", "oauth2", "openIdConnect"} or resolved.get("scheme"):
      name = resolved.get("name") or resolved.get("id") or key
      security_schemes[name] = resolved
    elif "properties" in resolved or "items" in resolved or value_type in {
      "string",
      "integer",
      "number",
      "boolean",
      "array",
      "object",
    }:
      schemas[key] = resolved

  if isinstance(components.get("securitySchemes"), dict):
    fixed_schemes = {}
    for name, scheme in components["securitySchemes"].items():
      fixed_schemes[name] = replace_bundled_refs(scheme, bundled)
    components["securitySchemes"] = fixed_schemes

  spec["paths"] = replace_bundled_refs(spec.get("paths", {}), bundled)
  if spec.get("security"):
    spec["security"] = replace_bundled_refs(spec["security"], bundled)
  return spec


def operation_to_path_item(operation_data: dict) -> tuple[str, str, dict, dict]:
    method = operation_data["method"].lower()
    path = operation_data["path"]
    op: dict[str, Any] = {
        "operationId": operation_data.get("id"),
        "summary": operation_data.get("summary"),
        "description": operation_data.get("description"),
        "tags": operation_data.get("tags") or [],
        "parameters": [],
        "responses": {},
    }

    request = operation_data.get("request") or {}
    for param in request.get("path") or []:
        op["parameters"].append(param)
    for param in request.get("query") or []:
        op["parameters"].append(param)
    for param in request.get("header") or []:
        op["parameters"].append(param)
    for param in request.get("cookie") or []:
        op["parameters"].append(param)

    body = request.get("body")
    if body:
        op["requestBody"] = body

    responses_raw = operation_data.get("responses") or {}
    if isinstance(responses_raw, list):
        responses_map = {}
        for item in responses_raw:
            if isinstance(item, dict):
                code = str(item.get("code") or item.get("status") or item.get("statusCode") or "default")
                responses_map[code] = item
        responses_raw = responses_map

    for status, response in responses_raw.items():
        op["responses"][str(status)] = response

    if operation_data.get("security"):
        op["security"] = operation_data["security"]
    if operation_data.get("servers"):
        op["servers"] = operation_data["servers"]
    if operation_data.get("callbacks"):
        op["callbacks"] = operation_data["callbacks"]

    return path, method, op, operation_data.get("__bundled__") or {}


def build_openapi_from_project(meta: dict, cache_dir: Path | None = None) -> dict:
    project_id = meta["project_id"]
    toc = fetch_json(
        f"https://stoplight.io/api/v1/projects/{project_id}/table-of-contents?branch=main"
    )
    toc_items = toc.get("items", [])
    nodes_meta: list[dict] = []
    walk_toc(toc_items, nodes_meta)

    if meta.get("service_slug"):
        service = fetch_node(project_id, meta["service_slug"], cache_dir)
        service_data = json.loads(service["data"])
        spec: dict[str, Any] = {
            "openapi": "3.0.0",
            "info": {
                "title": service_data.get("name") or meta["title"],
                "version": str(service_data.get("version") or "1.0.0"),
                "description": clean_description(service_data.get("description", "")),
            },
            "servers": service_data.get("servers") or [],
            "tags": service_data.get("tags") or [],
            "paths": {},
            "components": {"securitySchemes": {}},
        }
        if service_data.get("security"):
            spec["security"] = service_data["security"]
        if service_data.get("securitySchemes"):
            schemes = service_data["securitySchemes"]
            if isinstance(schemes, list):
                spec["components"]["securitySchemes"] = {
                    str(item.get("id") or item.get("name") or i): item
                    for i, item in enumerate(schemes)
                    if isinstance(item, dict)
                }
            else:
                spec["components"]["securitySchemes"] = schemes
        all_bundled = collect_bundled_map(service_data.get("__bundled__") or {})

        operation_slugs = [
            n["slug"] for n in nodes_meta if n["type"] == "http_operation" and n["slug"]
        ]
        print(f"  fetching {len(operation_slugs)} operations...")

        with ThreadPoolExecutor(max_workers=12) as executor:
            futures = {
                executor.submit(fetch_node, project_id, slug, cache_dir): slug
                for slug in operation_slugs
            }
            for future in as_completed(futures):
                slug = futures[future]
                node = future.result()
                op_data = json.loads(node["data"])
                path, method, op, op_bundled = operation_to_path_item(op_data)
                spec["paths"].setdefault(path, {})[method] = op
                all_bundled.update(op_bundled)

        spec = normalize_components(spec, all_bundled)

        articles = [n for n in nodes_meta if n["type"] == "article"]
        spec["x-articles"] = articles
        return spec

    article_slug = meta["article_slug"]
    article = fetch_node(project_id, article_slug, cache_dir)
    raw_content = article.get("data") or ""
    if isinstance(raw_content, str):
        try:
            article_data = json.loads(raw_content)
            markdown = article_data.get("content") or raw_content
        except json.JSONDecodeError:
            article_data = {}
            markdown = raw_content
    else:
        article_data = raw_content if isinstance(raw_content, dict) else {}
        markdown = article_data.get("content") or article.get("title", "")

    return {
        "openapi": "3.0.0",
        "info": {
            "title": meta["title"],
            "version": "1.0.0",
            "description": clean_description(markdown[:2000]),
        },
        "paths": {},
        "x-articles": [{"slug": article_slug, "title": article.get("title"), "type": "article"}],
        "x-markdown": markdown,
    }


def get_example(schema: dict | None) -> object | None:
    if not schema:
        return None
    if "example" in schema:
        return schema["example"]
    if "examples" in schema and isinstance(schema["examples"], dict) and schema["examples"]:
        first = next(iter(schema["examples"].values()))
        if isinstance(first, dict):
            return first.get("value", first)
        return first
    return None


def build_markdown(spec: dict, meta: dict) -> str:
    info = spec.get("info", {})
    lines = [
        f"# {info.get('title', meta['title'])}",
        "",
        f"**Versiyon:** {info.get('version', 'N/A')}",
        "",
        clean_description(info.get("description", "")),
        "",
        f"**Base URL:** `{meta['base_path_note']}`",
        "",
    ]

    articles = spec.get("x-articles") or []
    if articles:
        lines.extend(["## Ek Dokümanlar", ""])
        for article in articles:
            lines.append(f"- **{article.get('title', article.get('slug'))}** (`{article.get('slug')}`)")
        lines.append("")

    if spec.get("x-markdown"):
        lines.extend(["## Webhook Dokümantasyonu", "", clean_description(spec["x-markdown"]), ""])

    servers = spec.get("servers", [])
    if servers:
        lines.extend(["## Sunucular", ""])
        for server in servers:
            url = server.get("url", "")
            desc = server.get("description", "")
            lines.append(f"- `{url}` {desc}")
        lines.append("")

    security = spec.get("components", {}).get("securitySchemes", {})
    if isinstance(security, list):
        security = {
            str(item.get("name") or item.get("id") or i): item
            for i, item in enumerate(security)
            if isinstance(item, dict)
        }
    if security:
        lines.extend(["## Kimlik Doğrulama", ""])
        for name, scheme in security.items():
            lines.append(f"### {name}")
            lines.append(f"- Tip: `{scheme.get('type', '')}`")
            if scheme.get("scheme"):
                lines.append(f"- Şema: `{scheme.get('scheme')}`")
            if scheme.get("description"):
                lines.append(f"- {clean_description(scheme['description'])}")
            lines.append("")

    endpoints_by_tag: dict[str, list[dict]] = defaultdict(list)
    for path, path_item in spec.get("paths", {}).items():
        if not isinstance(path_item, dict):
            continue
        for method, operation in path_item.items():
            if method not in {"get", "post", "put", "patch", "delete"}:
                continue
            tag = (operation.get("tags") or ["Diğer"])[0]
            endpoints_by_tag[tag].append(
                {"method": method.upper(), "path": path, "operation": operation}
            )

    lines.extend(["## Endpoint'ler", ""])
    tag_order = [t.get("name") for t in spec.get("tags", []) if isinstance(t, dict)]
    tag_order += sorted(set(endpoints_by_tag.keys()) - set(tag_order))

    for tag in tag_order:
        if tag not in endpoints_by_tag:
            continue
        lines.extend([f"### {tag}", "", f"**{len(endpoints_by_tag[tag])} endpoint**", ""])
        for item in endpoints_by_tag[tag]:
            op = item["operation"]
            lines.extend(
                [
                    f"#### `{item['method']}` `{item['path']}`",
                    "",
                    f"**Özet:** {op.get('summary', '-')}",
                    "",
                ]
            )
            if op.get("description"):
                lines.append(clean_description(op["description"]))
                lines.append("")

            params = op.get("parameters", [])
            if params:
                lines.append("**Parametreler:**")
                lines.append("")
                lines.append("| Ad | Konum | Zorunlu | Açıklama |")
                lines.append("|----|-------|---------|----------|")
                for param in params:
                    if isinstance(param, dict) and "name" in param:
                        lines.append(
                            f"| `{param.get('name', '')}` | {param.get('in', '')} | "
                            f"{'Evet' if param.get('required') else 'Hayır'} | "
                            f"{clean_description(param.get('description', '')).replace('|', '/')} |"
                        )
                lines.append("")

            request_body = op.get("requestBody")
            if request_body:
                content = request_body.get("content", {})
                json_content = content.get("application/json", {})
                example = get_example(json_content.get("schema"))
                lines.append("**Request Body:**")
                lines.append("")
                if example is not None:
                    lines.append("```json")
                    lines.append(json.dumps(example, ensure_ascii=False, indent=2))
                    lines.append("```")
                    lines.append("")

            responses = op.get("responses", {})
            success = responses.get("200") or responses.get("201")
            if success:
                content = success.get("content", {})
                json_content = content.get("application/json", {})
                example = get_example(json_content.get("schema"))
                if example is not None:
                    lines.append("**Örnek Yanıt:**")
                    lines.append("")
                    lines.append("```json")
                    lines.append(json.dumps(example, ensure_ascii=False, indent=2))
                    lines.append("```")
                    lines.append("")

            lines.append("---")
            lines.append("")

    return "\n".join(lines)


def count_endpoints(spec: dict) -> int:
    return sum(
        1
        for path_item in spec.get("paths", {}).values()
        if isinstance(path_item, dict)
        for method in path_item
        if method in {"get", "post", "put", "patch", "delete"}
    )


def save_spec(root: Path, name: str, spec: dict, meta: dict) -> int:
    openapi_dir = root / "openapi"
    docs_dir = root / "docs"
    openapi_dir.mkdir(parents=True, exist_ok=True)
    docs_dir.mkdir(parents=True, exist_ok=True)

    clean_spec = {k: v for k, v in spec.items() if not str(k).startswith("x-")}
    yaml_path = openapi_dir / f"{name}.yaml"
    json_path = openapi_dir / f"{name}.json"
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(
            clean_spec,
            f,
            ensure_ascii=False,
            indent=2 if len(clean_spec.get("paths", {})) < 200 else None,
            separators=(",", ":") if len(clean_spec.get("paths", {})) >= 200 else (", ", ": "),
        )
    json_size = json_path.stat().st_size
    if json_size < 30_000_000:
        with yaml_path.open("w", encoding="utf-8") as f:
            yaml.dump(clean_spec, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
    elif yaml_path.exists():
        try:
            yaml_path.unlink()
        except OSError:
            pass

    (docs_dir / f"{name}.md").write_text(build_markdown(spec, meta), encoding="utf-8")
    endpoint_count = count_endpoints(spec)
    print(f"  saved {name}: {endpoint_count} endpoints")
    return endpoint_count


def build_llms_txt(root: Path, stats: dict[str, int]) -> None:
    repo = os.environ.get("REPO_URL", "https://github.com/atillakesicioglu/ideasoft-api-docs")
    content = """# Ideasoft API

> Ideasoft e-ticaret platformu Admin API, Store API ve Webhooks dokümantasyonu.

Base URL (Admin): `https://magaza-adiniz.myideasoft.com/admin-api`
Base URL (Store): `https://magaza-adiniz.myideasoft.com/api`
Kaynak: https://apidoc.ideasoft.dev

## Docs

- [Admin API]({repo}/blob/main/docs/admin-api.md): Yönetim paneli API ({admin_count} endpoint)
- [Store API]({repo}/blob/main/docs/store-api.md): Mağaza vitrin API ({store_count} endpoint)
- [Webhooks]({repo}/blob/main/docs/webhooks.md): Webhook bildirimleri
- [Hızlı Başlangıç]({repo}/blob/main/docs/QUICKSTART.md): İlk API çağrısı rehberi
- [OpenAPI Specs]({repo}/blob/main/openapi/): Makine okunabilir kaynak dosyalar

## API Grupları

- **Admin API**: Ürün, sipariş, kategori, müşteri, kampanya ve tüm yönetim işlemleri
- **Store API**: Mağaza vitrin tarafı (ürün listeleme, sepet, sipariş vb.)
- **Webhooks**: Olay bazlı bildirimler ve entegrasyon
""".format(
        repo=repo,
        admin_count=stats.get("admin-api", 0),
        store_count=stats.get("store-api", 0),
    )
    (root / "llms.txt").write_text(content, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        default=r"C:\Users\atill\OneDrive\Masaüstü\projects\ideasoft-api-docs",
    )
    parser.add_argument("--only", choices=list(PROJECTS.keys()), default=None)
    args = parser.parse_args()
    root = Path(args.root)
    root.mkdir(parents=True, exist_ok=True)

    stats: dict[str, int] = {}
    cache_dir = root / ".cache" / "nodes"
    targets = [args.only] if args.only else list(PROJECTS.keys())
    for key in targets:
        print(f"Processing {key}...")
        spec = build_openapi_from_project(PROJECTS[key], cache_dir)
        stats[key] = save_spec(root, key, spec, PROJECTS[key])

    build_llms_txt(root, stats)
    print("Done:", stats)


if __name__ == "__main__":
    main()
