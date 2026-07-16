"""Shared constants for Ideasoft API docs pipeline."""

STORE_BASE_URL = "https://magaza-adiniz.myideasoft.com"
ADMIN_PATH_PREFIX = "/admin-api"
STORE_PATH_PREFIX = "/api"
SOURCE_URL = "https://apidoc.ideasoft.dev"
REPO_URL = "https://github.com/atillakesicioglu/ideasoft-api-docs"

HTTP_METHODS = frozenset({"get", "post", "put", "patch", "delete"})

SECRET_FIELD_NAMES = frozenset(
    {
        "access_token",
        "base_url",
        "client_secret",
        "password",
        "api_key",
        "authorization",
        "token",
    }
)

# MCP input schema'sında kesinlikle bulunmaması gereken runtime alanları
FORBIDDEN_MCP_INPUT_FIELDS = frozenset({"access_token", "base_url"})

# Raw domain slug -> commerce group file
COMMERCE_GROUPS: dict[str, list[str]] = {
    "products": [
        "products",
        "product-details",
        "product-images",
        "product-prices",
        "product-buttons",
        "product-comments",
        "product-protections",
        "product-special-infos",
        "product-to-categories",
        "product-to-tags",
        "product-to-count-downs",
        "combine-products",
        "offered-products",
        "closing-product",
        "favourited-product",
        "favourited-products",
    ],
    "catalog": [
        "categories",
        "category-mappings",
        "brands",
        "tags",
        "labels",
        "label-to-products",
        "collections",
        "collection",
        "spec-groups",
        "spec-names",
        "spec-values",
        "spec-to-products",
        "option-groups",
        "options",
        "option-to-products",
    ],
    "inventory": ["stock-warnings", "shipments", "shipment-items"],
    "orders": [
        "orders",
        "order-details",
        "order-items",
        "order-refund-requests",
        "order-refund-request-items",
        "order-user-notes",
        "order-custom-tax-lines",
        "draft-orders",
        "payments",
        "pre-order-infos",
        "quick-carts",
        "carts",
        "cart-items",
        "active-carts",
        "abandoned-carts",
        "abandoned-orders",
    ],
    "customers": [
        "members",
        "member-groups",
        "member-addresses",
        "member-group-emails",
        "billing-addresses",
        "shipping-addresses",
        "maillists",
        "maillist-groups",
        "current-accounts",
    ],
    "marketing": [
        "promotions",
        "promotion-bars",
        "coupons",
        "price-rules",
        "price-gaps",
        "pos-campaigns",
        "polls",
        "popups",
    ],
    "content": [
        "blogs",
        "blog-categories",
        "blog-tags",
        "pages",
        "blocks",
        "banners",
        "sliders",
        "midblocks",
        "site-contents",
    ],
    "shipping": [
        "shipping-companies",
        "shipping-providers",
        "shipping-rates",
        "shipping-provider-settings",
        "tracking-codes",
        "towns",
        "town-groups",
        "regions",
        "countries",
        "locations",
    ],
    "analytics": ["statistics", "report"],
    "store-settings": [
        "preferences",
        "themes",
        "languages",
        "currencies",
        "common-pref",
        "extra-pref",
        "checkout-design-pref",
        "search-engine-pref",
        "seo-pref",
        "seo-settings",
    ],
}

# Curated commerce MCP tools -> match rules (method, path suffix or exact path, summary keyword)
COMMERCE_TOOL_RULES: list[dict] = [
    {
        "name": "search_products",
        "description": "Ürünleri listele veya filtrele.",
        "rules": [
            {"api": "admin-api", "method": "GET", "path": "/admin-api/products", "summary_contains": "LIST"},
            {"api": "store-api", "method": "GET", "path": "/api/products", "summary_contains": "LIST"},
        ],
    },
    {
        "name": "get_product",
        "description": "Tek ürün detayını getir.",
        "rules": [
            {"api": "admin-api", "method": "GET", "path": "/admin-api/products/{id}", "summary_contains": "GET"},
            {"api": "store-api", "method": "GET", "path": "/api/products/{id}", "summary_contains": "GET"},
        ],
    },
    {
        "name": "create_product",
        "description": "Yeni ürün oluştur.",
        "rules": [{"api": "admin-api", "method": "POST", "path": "/admin-api/products", "summary_contains": "POST"}],
    },
    {
        "name": "update_product",
        "description": "Mevcut ürünü güncelle.",
        "rules": [
            {"api": "admin-api", "method": "PUT", "path": "/admin-api/products/{id}", "summary_contains": "PUT"},
            {"api": "store-api", "method": "PUT", "path": "/api/products/{id}", "summary_contains": "PUT"},
        ],
    },
    {
        "name": "update_product_price",
        "description": "Ürün fiyatını güncelle.",
        "rules": [
            {"api": "admin-api", "method": "PUT", "path_contains": "product-prices"},
            {"api": "admin-api", "method": "POST", "path_contains": "product-prices"},
        ],
    },
    {
        "name": "update_inventory",
        "description": "Stok / envanter güncelle.",
        "rules": [
            {"api": "admin-api", "method": "PUT", "path_contains": "stock"},
            {"api": "admin-api", "method": "PUT", "path_contains": "products/{id}", "summary_contains": "stock"},
        ],
    },
    {
        "name": "list_categories",
        "description": "Kategorileri listele.",
        "rules": [
            {"api": "admin-api", "method": "GET", "path": "/admin-api/categories", "summary_contains": "LIST"},
            {"api": "store-api", "method": "GET", "path": "/api/categories", "summary_contains": "LIST"},
        ],
    },
    {
        "name": "create_category",
        "description": "Yeni kategori oluştur.",
        "rules": [{"api": "admin-api", "method": "POST", "path": "/admin-api/categories", "summary_contains": "POST"}],
    },
    {
        "name": "list_orders",
        "description": "Siparişleri listele.",
        "rules": [
            {"api": "admin-api", "method": "GET", "path": "/admin-api/orders", "summary_contains": "LIST"},
            {"api": "store-api", "method": "GET", "path": "/api/orders", "summary_contains": "LIST"},
        ],
    },
    {
        "name": "get_order",
        "description": "Tek sipariş detayını getir.",
        "rules": [
            {"api": "admin-api", "method": "GET", "path": "/admin-api/orders/{id}", "summary_contains": "GET"},
            {"api": "store-api", "method": "GET", "path": "/api/orders/{id}", "summary_contains": "GET"},
        ],
    },
    {
        "name": "update_order_status",
        "description": "Sipariş durumunu güncelle.",
        "rules": [
            {"api": "admin-api", "method": "PUT", "path_contains": "/orders/", "summary_contains": "PUT"},
        ],
    },
    {
        "name": "list_customers",
        "description": "Müşterileri / üyeleri listele.",
        "rules": [
            {"api": "admin-api", "method": "GET", "path": "/admin-api/members", "summary_contains": "LIST"},
            {"api": "store-api", "method": "GET", "path": "/api/members", "summary_contains": "LIST"},
        ],
    },
    {
        "name": "create_discount",
        "description": "İndirim / kupon oluştur.",
        "rules": [
            {"api": "admin-api", "method": "POST", "path_contains": "coupons"},
            {"api": "admin-api", "method": "POST", "path_contains": "promotions"},
        ],
    },
    {
        "name": "get_sales_summary",
        "description": "Satış özeti / istatistik getir.",
        "rules": [
            {"api": "admin-api", "method": "GET", "path_contains": "statistics"},
            {"api": "admin-api", "method": "GET", "path_contains": "report"},
        ],
    },
]

CAPABILITY_DEFINITIONS: list[dict] = [
    {"id": "products.list", "read_or_write": "read", "risk_level": "low", "tool": "search_products"},
    {"id": "products.create", "read_or_write": "write", "risk_level": "medium", "tool": "create_product"},
    {"id": "products.update", "read_or_write": "write", "risk_level": "medium", "tool": "update_product"},
    {"id": "products.update_price", "read_or_write": "write", "risk_level": "high", "tool": "update_product_price"},
    {"id": "inventory.read", "read_or_write": "read", "risk_level": "low", "tool": None},
    {"id": "inventory.update", "read_or_write": "write", "risk_level": "high", "tool": "update_inventory"},
    {"id": "orders.list", "read_or_write": "read", "risk_level": "low", "tool": "list_orders"},
    {"id": "orders.update_status", "read_or_write": "write", "risk_level": "high", "tool": "update_order_status"},
]
