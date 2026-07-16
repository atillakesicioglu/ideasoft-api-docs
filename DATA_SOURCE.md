# Veri Kaynağı ve Kullanım Notu

## Kaynak

| Alan | Değer |
|------|-------|
| Resmi dokümantasyon | https://apidoc.ideasoft.dev |
| Platform | Stoplight |
| Admin API Stoplight project | `cHJqOjIzODAzMw` |
| Store API Stoplight project | `cHJqOjI2NjA2OA` |
| Webhooks Stoplight project | `cHJqOjE0NzQyOQ` |

Bu repository içerikleri Stoplight public API'sinden ve resmi dokümantasyon sitesinden **otomatik extract** edilir.

## Community Mirror Uyarısı

Bu repo **Ideasoft tarafından onaylanmamış**, **resmi olmayan** bir community mirror'dır.

- Endpoint davranışları canlı API ile farklılık gösterebilir
- Örnekler yalnızca dokümantasyon amaçlıdır; `x-verification.status: documentation-only`
- Ticari veya production entegrasyonlarda [resmi dokümantasyonu](https://apidoc.ideasoft.dev) ve Ideasoft desteğini esas alın

## Telif ve marka

- **Ideasoft**, **Ideashop** ve ilgili markalar Ideasoft'a aittir
- Bu repo Ideasoft ile bağlantılı değildir
- API spesifikasyonunun fikri mülkiyeti ve kullanım koşulları Ideasoft'un kendi şartlarına tabidir

## Bu repoda ne var?

| İçerik | Açıklama |
|--------|----------|
| `openapi/domains/` | Domain bazlı küçük OpenAPI parçaları (git'te) |
| `artifacts/bundled/` | Tam bundled spec (GitHub Release artifact) |
| `metadata/` | stats, capabilities, MCP adayları, endpoint manifest |
| `reports/` | Endpoint diff raporu |

## İzin verilen kullanım

- AI / MCP / Context7 ile entegrasyon geliştirme
- İç araçlar ve test ortamları için referans
- Kendi riskinizle otomasyon prototipleri

## Yasak / önerilmeyen kullanım

- Resmi Ideasoft dokümantasyonunun yerine geçirme iddiası
- Credential veya müşteri verisi commit'leme
- Kaynak göstermeden ticari yeniden dağıtım

## Güncelleme sıklığı

Haftalık otomatik sync (GitHub Actions). Son extract zamanı: `metadata/stats.json` → `generated_at`.

## İletişim

- Ideasoft API destek: apisupport@ideasoft.com.tr
- Bu mirror için: GitHub Issues
