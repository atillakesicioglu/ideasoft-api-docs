"""OpenAPI operation -> MCP input JSON Schema."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

UNRESOLVED_REFS: list[str] = []


def clear_unresolved_refs() -> None:
    UNRESOLVED_REFS.clear()


def resolve_schema(schema: Any, spec: dict, depth: int = 0) -> Any:
    if depth > 12 or schema is None:
        return schema
    if isinstance(schema, dict):
        ref = schema.get("$ref")
        if isinstance(ref, str):
            if ref.startswith("#/components/schemas/"):
                key = ref.rsplit("/", 1)[-1]
                target = spec.get("components", {}).get("schemas", {}).get(key)
                if target is None:
                    UNRESOLVED_REFS.append(ref)
                    return {"type": "object", "description": f"Unresolved: {ref}"}
                return resolve_schema(deepcopy(target), spec, depth + 1)
            UNRESOLVED_REFS.append(ref)
            return {"type": "object", "description": f"Unresolved: {ref}"}
        out: dict[str, Any] = {}
        for k, v in schema.items():
            if k == "x-stoplight":
                continue
            out[k] = resolve_schema(v, spec, depth + 1)
        return out
    if isinstance(schema, list):
        return [resolve_schema(item, spec, depth + 1) for item in schema]
    return schema


def parameter_to_property(param: dict, spec: dict) -> dict[str, Any]:
    prop: dict[str, Any] = {}
    if param.get("description"):
        prop["description"] = param["description"]
    schema = param.get("schema") or {}
    resolved = resolve_schema(schema, spec)
    if isinstance(resolved, dict):
        prop.update({k: v for k, v in resolved.items() if k != "description"})
        if resolved.get("description") and "description" not in prop:
            prop["description"] = resolved["description"]
    if not prop.get("type"):
        prop.setdefault("type", "string")
    if param.get("required"):
        prop["x-required"] = True
    return prop


def build_input_schema(operation: dict, spec: dict) -> dict[str, Any]:
    clear_unresolved_refs()
    properties: dict[str, Any] = {}
    required: list[str] = []

    for param in operation.get("parameters") or []:
        if not isinstance(param, dict):
            continue
        name = param.get("name")
        if not name:
            continue
        loc = param.get("in", "query")
        key = name if loc == "query" else f"{loc}__{name}"
        properties[key] = {
            **parameter_to_property(param, spec),
            "x-parameter-in": loc,
        }
        if param.get("required"):
            required.append(key)

    body = operation.get("requestBody")
    if isinstance(body, dict):
        content = body.get("content", {})
        json_content = content.get("application/json") or content.get("application/ld+json") or {}
        if not json_content and content:
            json_content = next(iter(content.values()), {})
        schema = json_content.get("schema")
        if schema:
            resolved = resolve_schema(schema, spec)
            if resolved.get("type") == "object" and "properties" in resolved:
                for pname, pschema in resolved["properties"].items():
                    properties[f"body__{pname}"] = {**pschema, "x-parameter-in": "body"}
                if resolved.get("required"):
                    for r in resolved["required"]:
                        required.append(f"body__{r}")
            else:
                properties["body"] = {**(resolved if isinstance(resolved, dict) else {}), "x-parameter-in": "body"}
                if body.get("required"):
                    required.append("body")

    schema_out: dict[str, Any] = {"type": "object", "properties": properties}
    if required:
        schema_out["required"] = sorted(set(required))
    if UNRESOLVED_REFS:
        schema_out["x-unresolved-refs"] = list(dict.fromkeys(UNRESOLVED_REFS))
    return schema_out
