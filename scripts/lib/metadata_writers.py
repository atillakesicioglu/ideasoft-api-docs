"""Metadata YAML/JSON writers for v2.1."""

from __future__ import annotations

from collections import Counter
from typing import Any

import yaml

from .constants import (
    CAPABILITY_DEFINITIONS,
    COMMERCE_TOOL_RULES,
    REPO_URL,
    SECRET_FIELD_NAMES,
    FORBIDDEN_MCP_INPUT_FIELDS,
    SOURCE_URL,
    STORE_BASE_URL,
)
from .openapi_normalize import iter_operations
from .schema_builder import build_input_schema


RUNTIME_CONFIGURATION = {
    "base_url": {
        "description": "Mağaza base URL (ör. https://magaza-adiniz.myideasoft.com)",
        "default": STORE_BASE_URL,
        "expose_to_model": False,
    },
    "access_token": {
        "description": "OAuth 2.0 Bearer token — MCP runtime tarafından enjekte edilir",
        "expose_to_model": False,
        "security_note": "Token tool input, tool output veya loglarda bulunmamalıdır.",
    },
}

AUTHENTICATION_METADATA = {
    "type": "oauth2",
    "flow": "client_credentials",
    "token_url": f"{STORE_BASE_URL}/oauth/v2/token",
    "expose_to_model": False,
}


def _match_rule(rule: dict, api: str, method: str, path: str, summary: str) -> bool:
    if rule.get("api") and rule["api"] != api:
        return False
    if rule.get("method") and rule["method"] != method:
        return False
    if rule.get("path") and rule["path"] != path:
        return False
    if rule.get("path_contains") and rule["path_contains"] not in path:
        return False
    if rule.get("summary_contains") and rule["summary_contains"].upper() not in (summary or "").upper():
        return False
    return True


def find_operations_for_rules(specs: dict[str, dict], rules: list[dict]) -> list[dict]:
    mappings: list[dict] = []
    seen: set[str] = set()
    for rule in rules:
        for api_name, spec in specs.items():
            if rule.get("api") and rule["api"] != api_name:
                continue
            for api, method, path, operation in iter_operations(spec, api_name):
                if not _match_rule(rule, api, method, path, operation.get("summary", "")):
                    continue
                key = f"{api}:{method}:{path}"
                if key in seen:
                    continue
                seen.add(key)
                mappings.append(
                    {
                        "api": api,
                        "method": method,
                        "path": path,
                        "operation_id": operation.get("operationId"),
                        "summary": operation.get("summary"),
                    }
                )
    return mappings


def write_domain_stats(specs: dict[str, dict], path_domain_fn, out_path) -> dict:
    from pathlib import Path

    data: dict[str, Any] = {
        "source": SOURCE_URL,
        "mirror": REPO_URL,
        "base_url": STORE_BASE_URL,
        "apis": {},
    }
    for api_name, spec in specs.items():
        domain_counts = Counter()
        for path in spec.get("paths", {}):
            domain_counts[path_domain_fn(api_name, path)] += 1
        data["apis"][api_name] = {
            "operations": sum(domain_counts.values()),
            "paths": len(spec.get("paths", {})),
            "schemas": len(spec.get("components", {}).get("schemas", {})),
            "domains": [
                {"name": name, "operations": count}
                for name, count in sorted(domain_counts.items(), key=lambda x: (-x[1], x[0]))
            ],
        }
    Path(out_path).write_text(yaml.dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return data


def write_capabilities_matrix(specs: dict[str, dict], commerce_tools: dict, out_path) -> None:
    from pathlib import Path

    tool_map = {t["name"]: t for t in commerce_tools.get("tools", [])}
    capabilities: dict[str, Any] = {
        "schema_version": "2.1",
        "source": SOURCE_URL,
        "verification_default": "documentation-only",
        "capabilities": {},
    }
    for cap_def in CAPABILITY_DEFINITIONS:
        cap_id = cap_def["id"]
        tool_name = cap_def.get("tool")
        mapped = tool_map.get(tool_name, {}).get("mappings", []) if tool_name else []
        capabilities["capabilities"][cap_id] = {
            "supported": bool(mapped) if tool_name else cap_id.startswith("inventory.read"),
            "verification_status": "documentation-only",
            "read_or_write": cap_def["read_or_write"],
            "risk_level": cap_def["risk_level"],
            "mapped_operations": mapped,
        }
    Path(out_path).write_text(yaml.dump(capabilities, allow_unicode=True, sort_keys=False), encoding="utf-8")


def write_commerce_tools(specs: dict[str, dict], out_path) -> dict:
    from pathlib import Path

    tools: list[dict] = []
    for tool_def in COMMERCE_TOOL_RULES:
        mappings = find_operations_for_rules(specs, tool_def["rules"])
        tools.append(
            {
                "name": tool_def["name"],
                "description": tool_def["description"],
                "platform_agnostic": True,
                "authentication": AUTHENTICATION_METADATA,
                "runtime_configuration": RUNTIME_CONFIGURATION,
                "mappings": mappings,
            }
        )
    doc = {
        "schema_version": "2.1",
        "description": "Küratörlü, platformdan bağımsız MCP commerce tool tanımları.",
        "tools": tools,
    }
    Path(out_path).write_text(yaml.dump(doc, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return doc


def write_mcp_endpoint_candidates(specs: dict[str, dict], out_path, slugify_fn, limit_per_api: int = 300) -> dict:
    from pathlib import Path

    tools: list[dict] = []
    unresolved_report: list[dict] = []
    used_names: set[str] = set()

    for api_name, spec in specs.items():
        if api_name == "webhooks":
            continue
        count = 0
        for api, method, path, operation in iter_operations(spec, api_name):
            if count >= limit_per_api:
                break
            base_name = slugify_fn(f"ideasoft_{api_name}_{method}_{path}")[:80]
            name = base_name
            if name in used_names:
                suffix = 2
                while True:
                    candidate = f"{base_name[:75]}-{suffix}"
                    if candidate not in used_names:
                        name = candidate
                        break
                    suffix += 1
            used_names.add(name)
            input_schema = build_input_schema(operation, spec)
            if input_schema.get("x-unresolved-refs"):
                unresolved_report.append({"tool": name, "refs": input_schema["x-unresolved-refs"]})
            tools.append(
                {
                    "name": name,
                    "description": operation.get("summary") or f"{method} {path}",
                    "api": api_name,
                    "method": method,
                    "path": path,
                    "operation_id": operation.get("operationId"),
                    "input_schema": input_schema,
                    "authentication": AUTHENTICATION_METADATA,
                    "runtime_configuration": RUNTIME_CONFIGURATION,
                    "source": operation.get("x-source", {}),
                    "verification": operation.get("x-verification", {}),
                }
            )
            count += 1

    doc = {
        "schema_version": "2.1",
        "description": (
            "Ham endpoint-to-tool aday çıktısı. Her OpenAPI operation için otomatik üretilmiştir. "
            "Küratörlü MCP tool'lar için metadata/commerce-tools.yaml kullanın."
        ),
        "security_policy": {
            "expose_to_model": False,
            "forbidden_in_input_schema": sorted(FORBIDDEN_MCP_INPUT_FIELDS),
            "note": "access_token ve base_url yalnızca runtime_configuration içindedir; loglanmamalıdır.",
        },
        "unresolved_refs_sample": unresolved_report[:50],
        "unresolved_refs_count": len(unresolved_report),
        "tools": tools,
    }
    Path(out_path).write_text(yaml.dump(doc, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return doc


def schema_contains_secrets(schema: Any, path: str = "") -> list[str]:
    hits: list[str] = []
    if isinstance(schema, dict):
        for key, value in schema.items():
            current = f"{path}.{key}" if path else key
            if key in SECRET_FIELD_NAMES:
                hits.append(current)
            hits.extend(schema_contains_secrets(value, current))
    elif isinstance(schema, list):
        for i, item in enumerate(schema):
            hits.extend(schema_contains_secrets(item, f"{path}[{i}]"))
    return hits
