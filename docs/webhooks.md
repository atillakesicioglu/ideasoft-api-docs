# Ideasoft Webhooks

**Versiyon:** 1.0.0

# Webhooks

Farklı uygulamalarımızın senkronize bir şekilde çalışabilmesi için uygulama içerisinde oluşan olayları kendine entegre olmuş diğer uygulamalara bildirmek için kullanılan bir teknolojidir. Belirli olaylar meydana geldikten sonra API çağrısı yapmak durumunda kalmadan daha verimli ve hızlı bir şekilde haberleşme sağlanmış olur.

> Webhooklarda sadece değeri değişen alanlar gönderilmektedir. Farklı verilere ihtiyacınız var ise "id" kullanarak API'ye istek atmanız beklenmektedir.

## Kullanılan Webhooklar

| Events             | Topics                                                                 | Fields (V8) |
|--------------------|------------------------------------------------------------------------|--------|
| brand              | `brand/create`, `brand/update`, `brand/delete`                         | `id`, `name`, `slug`, `status`, `updatedAt`, `createdAt` |
| category           | `category/create`, `category/update`, `category/delete`                | `id`, `name`, `slug`, `status`, `updatedAt`, `createdAt` |
| extra pref         | `extra_pref/update` | `exclude_tax_abroad` |
| member             | `member/create`, `member/update`, `member/delete`                      | `id`, `firstname`, `surname`, `email`, `status`, `kvkkStatus`, `allowedToPhone`, `allowedToCampaigns`, `allowedToSms`, `mobilePhoneNumber`, `address`, `location`, `country`, `zipCode`, `lastIp`, `gender`, `birthDate`, `updatedAt`, `createdAt` |
| member group       | `member_group/create`, `member_group/update`, `member_group/delete`    | `id`, `name` |
| order              | `order/create`, `order/update`, `order/delete`                         | `id`, `customerFirstname`, `customerSurname`, `status`, `amount`, `paymentStatus`, `customerEmail`, `customerPhone`, `paymentTypeName`, `paymentProviderCode`, `paymentProviderName`, `paymentGatewayCode`, `paymentGatewayName`, `bankName`, `currency`, `currencyRates`, `couponDiscount`, `taxAmount`, `totalCustomTaxAmount`, `promotionDiscount

**Base URL:** `Webhook bildirimleri`

## Ek Dokümanlar

- **Webhooks** (`5cc9374300b99-webhooks`)

## Webhook Dokümantasyonu

# Webhooks

Farklı uygulamalarımızın senkronize bir şekilde çalışabilmesi için uygulama içerisinde oluşan olayları kendine entegre olmuş diğer uygulamalara bildirmek için kullanılan bir teknolojidir. Belirli olaylar meydana geldikten sonra API çağrısı yapmak durumunda kalmadan daha verimli ve hızlı bir şekilde haberleşme sağlanmış olur.

> Webhooklarda sadece değeri değişen alanlar gönderilmektedir. Farklı verilere ihtiyacınız var ise "id" kullanarak API'ye istek atmanız beklenmektedir.

## Kullanılan Webhooklar

| Events             | Topics                                                                 | Fields (V8) |
|--------------------|------------------------------------------------------------------------|--------|
| brand              | `brand/create`, `brand/update`, `brand/delete`                         | `id`, `name`, `slug`, `status`, `updatedAt`, `createdAt` |
| category           | `category/create`, `category/update`, `category/delete`                | `id`, `name`, `slug`, `status`, `updatedAt`, `createdAt` |
| extra pref         | `extra_pref/update` | `exclude_tax_abroad` |
| member             | `member/create`, `member/update`, `member/delete`                      | `id`, `firstname`, `surname`, `email`, `status`, `kvkkStatus`, `allowedToPhone`, `allowedToCampaigns`, `allowedToSms`, `mobilePhoneNumber`, `address`, `location`, `country`, `zipCode`, `lastIp`, `gender`, `birthDate`, `updatedAt`, `createdAt` |
| member group       | `member_group/create`, `member_group/update`, `member_group/delete`    | `id`, `name` |
| order              | `order/create`, `order/update`, `order/delete`                         | `id`, `customerFirstname`, `customerSurname`, `status`, `amount`, `paymentStatus`, `customerEmail`, `customerPhone`, `paymentTypeName`, `paymentProviderCode`, `paymentProviderName`, `paymentGatewayCode`, `paymentGatewayName`, `bankName`, `currency`, `currencyRates`, `couponDiscount`, `taxAmount`, `totalCustomTaxAmount`, `promotionDiscount`, `generalAmount`, `shippingAmount`, `finalAmount`, `additionalServiceAmount`, `installment`, `installmentRate`, `extraInstallment`, `transactionId`, `hasUserNote`, `errorMessage`, `referrer`, `useGiftPackage`, `usePromotion`, `shippingProviderCode`, `shippingTrackingCode`, `shippingAddress`, `billingAddress`, `orderItems`, `createdAt`, `updatedAt` |
| order refund request | `order_refund_request/create`, `order_refund_request/update`, `order_refund_request/delete` | `id`, `code`, `status`, `fee`, `updatedAt`, `createdAt` |
| product            | `product/create`, `product/update`, `product/delete`                   | `id`, `name`, `fullName`, `barcode`, `brand`, `categories`, `stockTypeLabel`, `digitalProduct`, `hasOption`, `slug`, `sku`, `status`, `stockAmount`, `price1`, `updatedAt`, `createdAt` |
| payment            | `payment/create`, `payment/update`, `payment/delete`                   | `id`, `transactionId`, `memberFirstname`, `memberSurname`, `status`, `amount`, `updatedAt`, `createdAt` |
| theme              | `theme/create`, `theme/update`, `theme/delete`                         | `id`, `name`, `status`, `version`, `updatedAt`, `createdAt` |
| queue process      | `queue_process/create`, `queue_process/update`                         | `id`, `type`, `status`, `updatedAt`, `createdAt` |
| maillist           | `maillist/create`, `maillist/update`, `maillist/delete`                | `id`, `name`, `email`, `lastMailSentDate`, `creatorIpAddress`, `maillistGroup` |
| currency         | `currency/update` | `id`, `status`, `label`, `buyingPrice`, `sellingPrice`, `updatedAt` |
| price_rule         | `price_rule/create`, `price_rule/update`, `price_rule/delete` | `id`, `name` |

## Webhook Özellikleri

- ```topic``` : Webhook’u tetikleyen olay.

- ```address```: Bir olay meydana geldiğinde POST isteği gönderilen hedef url.
- ```fields``` : İstek sonucunda size dönmesini istediğimiz alanlar. **V8 Kaldırıldı**
- ```status``` : Webhook durumu.
- ```created_at``` : Webhook kaydının oluşturulduğu tarih ve saat.
- ```updated_at``` : Webhook kaydının güncellendiği tarih ve saat.

## Webhook Veri Güvenliği

Bir webhook'a yanıt vermeden önce webhook'un  İdeasofttan gönderildiğini doğrulamanız gerekir.  Webhook isteği gönderilirken verilerle birlikte uygulamanın hmac kodu da gönderilir.Gönderilen hmac'i header üzerinden X-Ideashop-Hmac-Sha256  alınır.

```$data = file_get_contents('php://input');```

Datayı aldıklarında  hmacCreator ile applerine ait client_secret değeri ve gelen data ile hmac oluşturup, yine data ile beraber gelen hmac kodu ile verinin İdeasofttan gelip gelmediğini kontrol edebilirler. Gönderilen ve kendi taraflarında oluşturdukları hmac'ler uyuşmuyor ise ilgili verinin ideasoft üzerinden gelmediği anlamına gelmektedir.
 
Örnek hmac oluşturma kodu:
 
 ```base64_encode(hash_hmac('sha256', $data, $secret, true));```

## Webhook Yanıtı

Webhook sisteme tanımlanmış istek sayısına ulaşana ya da ```200 OK!``` yanıtını alana kadar ilgili endpointe çağrıda bulunur. Yapılan her isteğe yanıt için 10 saniye bekler. Yanıt yoksa veya bir hata dönerse istek sayısı kontrol edilir, eğer sistemde tanımlı istek sayısı aşılmadıysa veriyi göndermeyi tekrar dener. İstek sayısı sisteme tanımlanan değerin üzerine çıkması durumunda webhook aboneliği otomatik siler ve isteğin tekrar gönderilmesi gerekir.

## Yeni Bir Webhook Oluşturma

Adres ve topic bilgisiyle yeni bir webhook oluşturur.

```POST https://magaza-adiniz.myideasoft.com/admin-api/client_webhooks```

Body Nesnesi

```json

  {
        "topic": "product/create",
        "address": " https://magaza-adiniz.myideasoft.ide",
        "fields": "{\"fields\": [\"id\",\"sku\",\"fullName\"]}", //V8 Kaldırıldı
        "status": 1
}
```
### Response 

``` json
{
    "id": 1,
    "client": {
        "id": 1,
        "name": "Sendloop"
    },
    "topic": "product/create",
    "address": "https://magaza-adiniz.myideasoft.ide",
    "fields": "{\"fields\": [\"id\",\"sku\",\"fullName\"]}", //V8 Kaldırıldı
    "status": 1,
    "createdAt": "2022-07-26T10:59:04+03:00",
    "updatedAt": "2022-07-26T10:59:04+03:00"
}
```
## Webhook Listesini Alma

Webhook listesini verir.

```GET https://magaza-adiniz.myideasoft.com/admin-api/client_webhooks```

### Response 
```json
        {
        "id": 1,
        "client": {
            "id": 1,
            "name": "Sendloop"
        },
        "topic": "product/create",
        "address": " https://magaza-adiniz.myideasoft.ide",
        "fields": "{\"fields\": [\"id\",\"sku\",\"fullName\"]}", //V8 Kaldırıldı
        "status": 1,
        "createdAt": "2022-07-26T10:58:54+03:00",
        "updatedAt": "2022-07-26T10:58:54+03:00"
    },
    {
        "id": 2,
        "client": {
            "id": 1,
            "name": "Sendloop"
        },
        "topic": "payment/create",
        "address": " https://magaza-adiniz.myideasoft.ide",
        "fields": "{\"fields\": [\"id\",\"transactionId\",\"memberFirstname\"]}", //V8 Kaldırıldı
        "status": 1,
        "createdAt": "2022-07-26T11:05:21+03:00",
        "updatedAt": "2022-07-26T11:05:21+03:00"
    }
```
## Webhook Güncelleme

İlgili webhooku günceller.

```PUT https://magaza-adiniz.myideasoft.com/admin-api/client_webhooks/{webhooks_id}```

Body Nesnesi 
``` json

  {
        "topic": "product/create",
        "address": " https://magaza-adiniz.myideasoft.ide",
        "fields": "{\"fields\": [\"id\", \"status\"]}", //V8 Kaldırıldı
        "status": 1
}
```

### Response 
``` json
{
    "id": 1,
    "topic": "product/create",
    "address": " https://magaza-adiniz.myideasoft.ide",
    "fields": "{\"fields\": [\"id\", \"status\"]}", //V8 Kaldırıldı
    "status": 1,
    "createdAt": "2022-07-26T10:58:54+03:00",
    "updatedAt": "2022-07-26T11:09:11+03:00"
}
```

### Webhook Silme

İlgili webhooku kalıcı olarak siler.

``` DELETE https://magaza-adiniz.myideasoft.com/admin-api/client_webhooks/{webhooks_id} ```

### Response

Silme isteği başarı ile sonuçlandı. (cevapta içerik bulunmaz.)

## Endpoint'ler
