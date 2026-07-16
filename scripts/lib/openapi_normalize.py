"""OpenAPI URL normalization and path utilities."""

from __future__ import annotations

from .constants import ADMIN_PATH_PREFIX, HTTP_METHODS, STORE_BASE_URL, STORE_PATH_PREFIX


def normalize_spec_urls(spec: dict, api_name: str) -> dict:
    """Base URL mağaza kökü; path'ler /admin-api veya /api ile başlar."""
    spec["servers"] = [
        {
            "url": STORE_BASE_URL,
            "description": (
                f"Ideasoft mağaza base URL. "
                f"{'Admin' if api_name == 'admin-api' else 'Store' if api_name == 'store-api' else 'API'} "
                f"path prefix operation path içindedir."
            ),
        }
    ]
    return spec


def join_url(base: str, path: str) -> str:
    return f"{base.rstrip('/')}/{path.lstrip('/')}"


def has_duplicate_path_segments(full_url: str) -> bool:
    return (
        f"{ADMIN_PATH_PREFIX}{ADMIN_PATH_PREFIX}" in full_url
        or f"{STORE_PATH_PREFIX}{STORE_PATH_PREFIX}" in full_url
        or "/admin-api/admin-api/" in full_url
        or "/api/api/" in full_url
    )


def collect_url_pairs(spec: dict) -> list[tuple[str, str, str]]:
    """(method, path, full_url) listesi."""
    base = spec.get("servers", [{}])[0].get("url", STORE_BASE_URL)
    pairs: list[tuple[str, str, str]] = []
    for path, path_item in spec.get("paths", {}).items():
        if not isinstance(path_item, dict):
            continue
        for method in path_item:
            if method in HTTP_METHODS:
                pairs.append((method.upper(), path, join_url(base, path)))
    return pairs


def iter_operations(spec: dict, api_name: str):
    for path, path_item in spec.get("paths", {}).items():
        if not isinstance(path_item, dict):
            continue
        for method, operation in path_item.items():
            if method in HTTP_METHODS and isinstance(operation, dict):
                yield api_name, method.upper(), path, operation
