# Ideasoft API — Hızlı Başlangıç

## 1. Gerekli Bilgiler

| Bilgi | Nereden alınır |
|-------|----------------|
| Mağaza URL | `https://magaza-adiniz.myideasoft.com` |
| Admin API Base | `https://magaza-adiniz.myideasoft.com/admin-api` |
| Store API Base | `https://magaza-adiniz.myideasoft.com/api` |
| Client ID / Secret | Ideasoft panel → Uygulama / API ayarları |

## 2. Admin API — Kategori Listeleme

```bash
curl -X GET \
  "https://magaza-adiniz.myideasoft.com/admin-api/categories" \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -H "Content-Type: application/json"
```

## 3. Store API — Ürün Listeleme

```bash
curl -X GET \
  "https://magaza-adiniz.myideasoft.com/api/products" \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -H "Content-Type: application/json"
```

## 4. OAuth 2.0 (Client Credentials)

Token almak için Ideasoft panelinizde tanımlı `client_id` ve `client_secret` kullanılır. Detaylı akış için:

- [Admin API Authentication](https://apidoc.ideasoft.dev/docs/admin-api/3x74avtrv8u23-authentication)
- [Store API Authentication](https://apidoc.ideasoft.dev/docs/store-api/0c0193c3acbef-authentication-v1)

## 5. Webhooks

Webhook'lar mağazanızda oluşan olayları (sipariş, ürün, müşteri vb.) belirlediğiniz URL'ye POST eder.

- HMAC doğrulama header: `X-Ideashop-Hmac-Sha256`
- Detaylar: [`docs/webhooks.md`](./webhooks.md)

## 6. AI Araçlarında Kullanım (Context7)

```
use context7 /atillakesicioglu/ideasoft-api-docs ile admin api sipariş listeleme endpoint'ini göster
```

Kaynak: [https://apidoc.ideasoft.dev](https://apidoc.ideasoft.dev)
