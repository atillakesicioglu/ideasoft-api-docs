# Ideasoft API Authentication Rehberi

Bu rehber [Ideasoft API Docs](https://apidoc.ideasoft.dev) kaynaklıdır. **Community mirror** olduğu için canlı mağazanızda test etmeden production'a almayın.

## Genel Bakış

| API | Base URL | Auth |
|-----|----------|------|
| Admin API | `https://{magaza}.myideasoft.com/admin-api` | OAuth 2.0 Bearer |
| Store API | `https://{magaza}.myideasoft.com/api` | OAuth 2.0 Bearer |

Resmi detaylar:
- [Admin Authentication](https://apidoc.ideasoft.dev/docs/admin-api/3x74avtrv8u23-authentication)
- [Store Authentication](https://apidoc.ideasoft.dev/docs/store-api/0c0193c3acbef-authentication-v1)

## 1. Uygulama (Client) Oluşturma

1. Ideasoft panelinize giriş yapın
2. **Uygulamalar / API** bölümünden yeni bir uygulama oluşturun
3. `client_id` ve `client_secret` değerlerini güvenli bir yerde saklayın
4. Gerekli scope / izinleri uygulamanıza atayın

> Scope isimleri ve panel adımları mağaza sürümüne göre değişebilir. Güncel bilgi için resmi dokümantasyona bakın.

## 2. Access Token Alma (Client Credentials)

```bash
curl -X POST "https://magaza-adiniz.myideasoft.com/oauth/v2/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET"
```

**Örnek yanıt:**

```json
{
  "access_token": "eyJhbGciOi...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

## 3. API İsteği Gönderme

```bash
curl -X GET "https://magaza-adiniz.myideasoft.com/admin-api/categories" \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json"
```

Store API için base URL `.../api` olmalıdır:

```bash
curl -X GET "https://magaza-adiniz.myideasoft.com/api/products" \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -H "Accept: application/json"
```

## 4. Token Yenileme

`expires_in` süresi dolduğunda yeni token alın. Client Credentials akışında refresh token olmayabilir; süre dolunca token endpoint'ine tekrar istek atın.

## 5. Webhook Güvenliği (HMAC)

Webhook istekleri `X-Ideashop-Hmac-Sha256` header'ı ile imzalanır:

```php
$computed = base64_encode(hash_hmac('sha256', $rawBody, $clientSecret, true));
if (!hash_equals($computed, $_SERVER['HTTP_X_IDEASHOP_HMAC_SHA256'])) {
    http_response_code(401);
    exit('Invalid signature');
}
```

Detaylar: [`docs/webhooks.md`](./webhooks.md)

## 6. Hata Kodları

| HTTP | Anlam |
|------|-------|
| 401 | Token geçersiz / süresi dolmuş |
| 403 | Yetki yetersiz |
| 404 | Endpoint veya kaynak bulunamadı |
| 422 | Validation hatası |
| 429 | Rate limit |

## 7. Güvenlik Önerileri

- `client_secret` değerini asla repoya veya frontend'e koymayın
- Token'ları secret manager / env variable olarak saklayın
- Webhook endpoint'inizde HMAC doğrulaması zorunlu tutun
- Bu mirror'daki örnekleri production'da doğrulamadan kullanmayın

## Destek

- Resmi API destek: apisupport@ideasoft.com.tr
- Resmi docs: https://apidoc.ideasoft.dev
