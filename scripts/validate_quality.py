#!/usr/bin/env python3
"""Quality gates for Ideasoft API docs v2.1."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import yaml

SCRIPTS = Path(__file__).resolve().parent
ROOT = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))

from lib.constants import FORBIDDEN_MCP_INPUT_FIELDS, STORE_BASE_URL  # noqa: E402
from lib.openapi_normalize import collect_url_pairs, has_duplicate_path_segments  # noqa: E402


def load_specs_from_artifacts() -> dict[str, dict]:
    specs = {}
    for name in ("admin-api", "store-api"):
        p = ROOT / "artifacts" / "bundled" / f"{name}.json"
        if p.exists():
            specs[name] = json.loads(p.read_text(encoding="utf-8"))
    return specs


def test_base_url_no_duplication(specs: dict) -> list[str]:
    errors: list[str] = []
    for api_name, spec in specs.items():
        for method, path, full_url in collect_url_pairs(spec):
            if has_duplicate_path_segments(full_url):
                errors.append(f"Duplicate path segment: {method} {full_url}")
            if not full_url.startswith(STORE_BASE_URL):
                errors.append(f"Unexpected base: {full_url}")
    return errors


def test_sha256_meta() -> list[str]:
    errors: list[str] = []
    bundled_dir = ROOT / "artifacts" / "bundled"
    for name in ("admin-api", "store-api"):
        artifact = bundled_dir / f"{name}.json"
        meta_path = bundled_dir / f"{name}.meta.json"
        if not artifact.exists() or not meta_path.exists():
            errors.append(f"Missing artifact or meta: {name}")
            continue
        actual = hashlib.sha256(artifact.read_bytes()).hexdigest()
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        if meta.get("sha256") != actual:
            errors.append(f"SHA256 mismatch for {name}: meta={meta.get('sha256')[:16]}... actual={actual[:16]}...")
    return errors


def test_duplicate_operation_ids(specs: dict) -> list[str]:
    seen: dict[str, str] = {}
    errors: list[str] = []
    for api_name, spec in specs.items():
        for path, path_item in spec.get("paths", {}).items():
            if not isinstance(path_item, dict):
                continue
            for method, op in path_item.items():
                if method not in {"get", "post", "put", "patch", "delete"}:
                    continue
                op_id = op.get("operationId")
                if not op_id:
                    continue
                key = f"{api_name}:{op_id}"
                if key in seen:
                    errors.append(f"Duplicate operationId {op_id} in {api_name}: {seen[key]} and {path}")
                seen[key] = path
    return errors


def test_mcp_tool_name_uniqueness() -> list[str]:
    path = ROOT / "metadata" / "mcp-endpoint-candidates.yaml"
    if not path.exists():
        return [f"Missing {path}"]
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    seen: dict[str, int] = {}
    for tool in doc.get("tools", []):
        name = tool.get("name")
        seen[name] = seen.get(name, 0) + 1
    return [f"Duplicate MCP tool name: {n} ({c}x)" for n, c in seen.items() if c > 1]


def test_no_secrets_in_mcp_input() -> list[str]:
    path = ROOT / "metadata" / "mcp-endpoint-candidates.yaml"
    if not path.exists():
        return []
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    errors: list[str] = []
    for tool in doc.get("tools", []):
        schema = tool.get("input_schema", {})
        for forbidden in FORBIDDEN_MCP_INPUT_FIELDS:
            if forbidden in (schema.get("properties") or {}):
                errors.append(f"Forbidden property '{forbidden}' in {tool.get('name')}")
            for prop_name in (schema.get("properties") or {}):
                if forbidden in prop_name:
                    errors.append(f"Forbidden property '{forbidden}' in {tool.get('name')} -> {prop_name}")
    return errors


def main() -> int:
    specs = load_specs_from_artifacts()
    all_errors: list[str] = []
    all_errors.extend(test_base_url_no_duplication(specs))
    all_errors.extend(test_sha256_meta())
    all_errors.extend(test_duplicate_operation_ids(specs))
    all_errors.extend(test_mcp_tool_name_uniqueness())
    all_errors.extend(test_no_secrets_in_mcp_input())

    if all_errors:
        print("VALIDATION FAILED:")
        for err in all_errors:
            print(f"  - {err}")
        return 1
    print("All quality checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
