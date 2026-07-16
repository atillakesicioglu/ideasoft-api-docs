# Contributing

Teşekkürler! Bu repo Ideasoft'un **resmi olmayan community mirror**'ıdır.

## Ne kabul ediyoruz

- Extract / pipeline script iyileştirmeleri
- Redocly kural düzeltmeleri
- Dokümantasyon netliği (README, AUTHENTICATION, DATA_SOURCE)
- CI workflow düzeltmeleri
- Typo ve metadata düzeltmeleri

## Ne kabul etmiyoruz

- Canlı API anahtarı, `client_secret`, gerçek mağaza URL credential'ları
- Ideasoft'un resmi API davranışını değiştiren "fix" PR'ları (kaynak Stoplight'tır)
- Büyük bundled JSON dosyalarının doğrudan git'e eklenmesi (Release artifact kullanın)

## Geliştirme

```bash
pip install pyyaml requests
python scripts/build_pipeline.py          # tam extract (uzun sürer)
python scripts/build_pipeline.py --skip-extract   # mevcut artifact ile
```

### Redocly

```bash
npx @redocly/cli lint --config redocly.yaml
# veya tek domain:
npx @redocly/cli lint openapi/domains/admin-api/products.json
```

## PR checklist

- [ ] `metadata/stats.json` güncellendi
- [ ] `reports/endpoint-diff.md` incelendi
- [ ] Secret / credential yok
- [ ] `CHANGELOG.md` otomatik veya manuel güncellendi

## Otomatik sync

Haftalık GitHub Action (`weekly-sync.yml`) Stoplight kaynağından PR açar. Manuel müdahale gerekmez; diff raporunu review edin.

## Lisans

Katkılar MIT lisansı altındadır. Ideasoft API'nin kendisi Ideasoft'a aittir — bkz. [DATA_SOURCE.md](DATA_SOURCE.md).
