# Ideasoft API Dokümantasyonu (Community Mirror)

> **⚠️ Resmi olmayan community mirror** — Bu repo [Ideasoft](https://www.ideasoft.com.tr/) veya [Ideasoft API Docs](https://apidoc.ideasoft.dev) tarafından işletilmez, onaylanmaz ve desteklenmez. Production entegrasyonlarında her zaman [resmi dokümantasyonu](https://apidoc.ideasoft.dev) ve `apisupport@ideasoft.com.tr` adresini esas alın. Ayrıntılar: [DATA_SOURCE.md](DATA_SOURCE.md).

Stoplight kaynaklı Ideasoft Admin API, Store API ve Webhooks dokümantasyonunun AI/MCP/Context7 uyumlu community mirror'ı (schema v2.1).

## Base URL standardı

| Alan | Değer |
|------|-------|
| **Base URL** | `https://magaza-adiniz.myideasoft.com` |
| **Admin path prefix** | `/admin-api/...` |
| **Store path prefix** | `/api/...` |

Path'ler operation tanımında tam yol olarak yer alır; base URL yalnızca mağaza köküdür. Birleşimde `/admin-api/admin-api` veya `/api/api` oluşmaz (CI'da otomatik test edilir).

## Üç kullanım seviyesi

### 1. Raw domain specs (`openapi/domains/`)

Stoplight kaynağından path segmentine göre bölünmüş **ham** OpenAPI parçaları. Git'te versiyonlanır; ince taneli arama ve domain bazlı lint için uygundur.

- `openapi/domains/admin-api/` — 178 domain dosyası
- `openapi/domains/store-api/` — 74 domain dosyası

### 2. Commerce grouped specs (`openapi/commerce/`)

AI/MCP için **iş alanına göre gruplanmış** OpenAPI katmanı:

| Dosya | İçerik |
|-------|--------|
| `products.json` | Ürünler, fiyatlar, görseller |
| `catalog.json` | Kategoriler, markalar, etiketler |
| `inventory.json` | Stok, sevkiyat |
| `orders.json` | Siparişler, sepetler, ödemeler |
| `customers.json` | Üyeler, adresler |
| `marketing.json` | Kampanyalar, kuponlar |
| `content.json` | Blog, sayfalar, banner |
| `shipping.json` | Kargo, bölgeler |
| `analytics.json` | İstatistik, raporlar |
| `store-settings.json` | Tema, dil, SEO tercihleri |

Ham `openapi/domains/` ayrımı korunur; commerce katmanı üzerine inşa edilir.

### 3. Bundled release specs (`artifacts/bundled/`)

Tam Admin + Store OpenAPI (~97 MB toplam). **Git'te değil** — [GitHub Releases](https://github.com/atillakesicioglu/ideasoft-api-docs/releases/latest) (`v*` tag) veya haftalık workflow manuel çalıştırmasında artifact olarak.

- `admin-api.json` + `admin-api.meta.json` (SHA256)
- `store-api.json` + `store-api.meta.json` (SHA256)

## İstatistikler

```bash
python -c "import json; print(json.dumps(json.load(open('metadata/stats.json'))['totals'], indent=2))"
python -c "import yaml; print(yaml.safe_dump(yaml.safe_load(open('metadata/domain-stats.yaml'))))"
```

## Metadata

| Dosya | Açıklama |
|-------|----------|
| [`metadata/stats.json`](metadata/stats.json) | Operation / path / schema sayıları |
| [`metadata/domain-stats.yaml`](metadata/domain-stats.yaml) | Domain bazlı sayılar (eski capabilities'den taşındı) |
| [`metadata/capabilities.yaml`](metadata/capabilities.yaml) | Semantik yetenek matrisi (`products.list`, `orders.update_status`, …) |
| [`metadata/commerce-tools.yaml`](metadata/commerce-tools.yaml) | Küratörlü, platformdan bağımsız MCP tool'lar (14 adet) |
| [`metadata/mcp-endpoint-candidates.yaml`](metadata/mcp-endpoint-candidates.yaml) | **Ham** endpoint-to-tool aday çıktısı (otomatik üretim) |
| [`reports/endpoint-diff.md`](reports/endpoint-diff.md) | Endpoint diff raporu |

### MCP güvenlik modeli (v2.1)

- `access_token` ve `base_url` **tool input schema'sında yoktur**; `runtime_configuration` / `authentication` metadata'sında `expose_to_model: false` ile tanımlıdır.
- Token tool input'u, çıktısı veya loglarda bulunmamalıdır.
- MCP input schema'ları OpenAPI `parameters` ve `requestBody`'den gerçek property/tip/required bilgisiyle üretilir.

## Endpoint metadata

Her operation'da:

- `x-source` — Stoplight kaynağı, extract zamanı, mirror repo
- `x-verification` — `documentation-only`, canlı test edilmedi

## Doğrulama

```bash
pip install -r requirements.txt
npm ci
python scripts/build_pipeline.py --skip-extract
python scripts/validate_quality.py
npm run lint:domains
```

CI (`.github/workflows/validate.yml`): pipeline → Redocly lint → quality gates → `git diff --exit-code`

## Güncelleme

```bash
python scripts/build_pipeline.py              # tam extract (~3-5 dk)
python scripts/build_pipeline.py --skip-extract  # mevcut artifact ile hızlı
```

Haftalık otomatik PR: `.github/workflows/weekly-sync.yml` (Pazartesi 06:00 UTC). Manuel çalıştırmada bundled artifact `upload-artifact` ile yüklenir; GitHub Release yalnızca `v*` tag ile `release-artifacts.yml` üzerinden oluşturulur.

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
