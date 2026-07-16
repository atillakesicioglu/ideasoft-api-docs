# Ideasoft API Dokümantasyonu (Community Mirror)

> **⚠️ Resmi olmayan community mirror** — Bu repo [Ideasoft](https://www.ideasoft.com.tr/) veya [Ideasoft API Docs](https://apidoc.ideasoft.dev) tarafından işletilmez, onaylanmaz ve desteklenmez. Production entegrasyonlarında her zaman [resmi dokümantasyonu](https://apidoc.ideasoft.dev) ve `apisupport@ideasoft.com.tr` adresini esas alın. Ayrıntılar: [DATA_SOURCE.md](DATA_SOURCE.md).

Stoplight kaynaklı Ideasoft Admin API, Store API ve Webhooks dokümantasyonunun AI/MCP/Context7 uyumlu community mirror'ı.

## İstatistikler (otomatik)

`metadata/stats.json` dosyasından üretilir. Pipeline çalıştırdıktan sonra güncel sayılar orada yer alır.

| API | Base URL |
|-----|----------|
| **Admin API** | `https://magaza-adiniz.myideasoft.com/admin-api` |
| **Store API** | `https://magaza-adiniz.myideasoft.com/api` |
| **Webhooks** | Mağazanıza POST bildirimleri |

```bash
python -c "import json; print(json.dumps(json.load(open('metadata/stats.json'))['apis'], indent=2))"
```

## Repo yapısı

| Yol | Açıklama |
|-----|----------|
| [`openapi/domains/`](openapi/domains/) | Domain bazlı küçük OpenAPI dosyaları (git'te) |
| [`artifacts/bundled/`](artifacts/bundled/) | Tam bundled spec (~59 MB) — **GitHub Release artifact** |
| [`metadata/stats.json`](metadata/stats.json) | operation / path / schema / domain sayıları |
| [`metadata/capabilities.yaml`](metadata/capabilities.yaml) | API yetenek özeti |
| [`metadata/mcp-tools-candidate.yaml`](metadata/mcp-tools-candidate.yaml) | MCP tool adayları |
| [`docs/AUTHENTICATION.md`](docs/AUTHENTICATION.md) | Tam kimlik doğrulama rehberi |
| [`reports/endpoint-diff.md`](reports/endpoint-diff.md) | Endpoint diff raporu |
| [`CHANGELOG.md`](CHANGELOG.md) | Değişiklik günlüğü |

### Bundled tam spec indirme

Büyük dosyalar git'te değil, [GitHub Releases](https://github.com/atillakesicioglu/ideasoft-api-docs/releases/latest) üzerinden:

- `admin-api.json` (~56 MB)
- `store-api.json` (~41 MB)

## Endpoint metadata

Her operation'da:

- `x-source` — Stoplight kaynağı, extract zamanı, mirror repo
- `x-verification` — `documentation-only`, canlı test edilmedi

## Doğrulama (Redocly)

```bash
npx @redocly/cli lint --config redocly.yaml
```

CI: `.github/workflows/validate.yml`

## Güncelleme

```bash
pip install pyyaml requests
python scripts/build_pipeline.py              # tam extract (~3-5 dk)
python scripts/build_pipeline.py --skip-extract  # mevcut artifact ile hızlı
```

Haftalık otomatik PR: `.github/workflows/weekly-sync.yml` (Pazartesi 06:00 UTC)

## Context7

1. [context7.com/add-library](https://context7.com/add-library) → GitHub
2. `https://github.com/atillakesicioglu/ideasoft-api-docs`
3. Library ID: `/atillakesicioglu/ideasoft-api-docs`

## Katkı & Lisans

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [LICENSE](LICENSE) (MIT + unofficial mirror disclaimer)
- [DATA_SOURCE.md](DATA_SOURCE.md)

## Kaynak

- Resmi docs: https://apidoc.ideasoft.dev
- API destek: apisupport@ideasoft.com.tr
