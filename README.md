# Ideasoft API Dokümantasyonu

[Ideasoft API Docs](https://apidoc.ideasoft.dev) resmi Stoplight dokümantasyonunun AI araçları ve geliştiriciler için optimize edilmiş versiyonu.

## İçerik

| Dosya | Açıklama |
|-------|----------|
| [`openapi/admin-api.json`](openapi/admin-api.json) | Admin API OpenAPI spec (903 endpoint) |
| [`openapi/store-api.json`](openapi/store-api.json) | Store API OpenAPI spec (333 endpoint) |
| [`openapi/webhooks.yaml`](openapi/webhooks.yaml) | Webhooks dokümantasyonu |
| [`docs/admin-api.md`](docs/admin-api.md) | Admin API referansı + örnekler |
| [`docs/store-api.md`](docs/store-api.md) | Store API referansı + örnekler |
| [`docs/webhooks.md`](docs/webhooks.md) | Webhook event'leri, güvenlik, örnekler |
| [`docs/QUICKSTART.md`](docs/QUICKSTART.md) | Hızlı başlangıç rehberi |
| [`llms.txt`](llms.txt) | AI araçları için indeks |

## API Özeti

| API | Base URL | Endpoint |
|-----|----------|----------|
| **Admin API** | `https://magaza-adiniz.myideasoft.com/admin-api` | 903 |
| **Store API** | `https://magaza-adiniz.myideasoft.com/api` | 333 |
| **Webhooks** | Mağazanıza POST bildirimleri | Event tabanlı |

**Auth:** OAuth 2.0 (Client Credentials) — detaylar Admin/Store API auth sayfalarında.

## Context7'a Ekleme

1. [context7.com/add-library](https://context7.com/add-library) → GitHub sekmesi
2. Repo URL: `https://github.com/atillakesicioglu/ideasoft-api-docs`
3. Library ID: `/atillakesicioglu/ideasoft-api-docs`

Alternatif: `openapi/admin-api.json` dosyasını OpenAPI Upload ile yükleyin.

## Güncelleme

```bash
python scripts/extract_docs.py
```

Kaynak: https://apidoc.ideasoft.dev (Stoplight)

## Kaynak

- Resmi docs: https://apidoc.ideasoft.dev
- Ideasoft: https://www.ideasoft.com.tr/
- API destek: apisupport@ideasoft.com.tr
