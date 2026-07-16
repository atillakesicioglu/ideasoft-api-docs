# Bundled OpenAPI Artifacts

Tam (bundled) OpenAPI spec dosyaları. **Git'e commit edilmez** — GitHub Releases üzerinden dağıtılır.

| Dosya | Açıklama |
|-------|----------|
| `admin-api.json` | Admin API tam spec (~56 MB) |
| `admin-api.meta.json` | SHA256, operation/path/schema sayıları |
| `store-api.json` | Store API tam spec (~41 MB) |
| `store-api.meta.json` | SHA256, operation/path/schema sayıları |

## Yerel üretim

```bash
python scripts/build_pipeline.py
```

## İndirme

[GitHub Releases](https://github.com/atillakesicioglu/ideasoft-api-docs/releases/latest)

## Not

Domain-split küçük dosyalar için `openapi/domains/` kullanın. Context7 / MCP için çoğu senaryoda domain dosyaları veya markdown yeterlidir.
