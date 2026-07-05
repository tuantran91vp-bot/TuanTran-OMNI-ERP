# Google Sheet Template

Foundation template gom 6 sheet cot loi. Moi sheet co the duoc tao tu file CSV trong `templates/google_sheets`.

## products

Danh muc san pham noi bo.

| Column | Purpose |
| --- | --- |
| product_id | Ma san pham noi bo, duy nhat. |
| product_name | Ten san pham. |
| category | Nhom san pham. |
| brand | Thuong hieu. |
| unit | Don vi tinh. |
| status | `active` hoac `inactive`. |
| created_at | Ngay tao theo dinh dang `YYYY-MM-DD`. |
| notes | Ghi chu. |

## sku_mapping

Lien ket SKU san voi SKU noi bo.

| Column | Purpose |
| --- | --- |
| platform | Ten san: `Shopee`, `TikTok Shop`, `Lazada`. |
| platform_sku | SKU tren san. |
| internal_sku | SKU noi bo dung cho kho/FIFO. |
| product_id | Tham chieu sang `products.product_id`. |
| variant_name | Ten phan loai. |
| conversion_qty | So luong quy doi ve SKU noi bo. |
| status | `active` hoac `inactive`. |

## warehouses

Danh muc kho.

| Column | Purpose |
| --- | --- |
| warehouse_id | Ma kho duy nhat. |
| warehouse_name | Ten kho. |
| warehouse_type | `main`, `branch`, `fulfillment`, hoac `virtual`. |
| address | Dia chi kho. |
| manager | Nguoi phu trach. |
| status | `active` hoac `inactive`. |

## suppliers

Danh muc nha cung cap.

| Column | Purpose |
| --- | --- |
| supplier_id | Ma nha cung cap duy nhat. |
| supplier_name | Ten nha cung cap. |
| contact_name | Nguoi lien he. |
| phone | So dien thoai. |
| email | Email. |
| address | Dia chi. |
| status | `active` hoac `inactive`. |

## inventory_lots

Ton kho theo lo nhap, la nen cho FIFO.

| Column | Purpose |
| --- | --- |
| lot_id | Ma lo duy nhat. |
| warehouse_id | Tham chieu sang `warehouses.warehouse_id`. |
| internal_sku | SKU noi bo. |
| supplier_id | Tham chieu sang `suppliers.supplier_id`. |
| received_date | Ngay nhap kho theo dinh dang `YYYY-MM-DD`. |
| qty_received | So luong nhap ban dau. |
| qty_available | So luong con kha dung. |
| unit_cost | Gia von moi don vi. |
| currency | Don vi tien te. |

## settings

Cau hinh van hanh.

| Column | Purpose |
| --- | --- |
| setting_key | Ten cau hinh. |
| setting_value | Gia tri cau hinh. |
| description | Mo ta. |
