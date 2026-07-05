# TuanTran OMNI ERP

OMNI ERP la he thong quan tri ban hang da san, tap trung vao Google Sheet, kho, SKU, FIFO, doi soat doanh thu va bao cao loi nhuan.

## Trang thai lo trinh

Da hoan thanh **Giai doan 1 - Foundation**, **Giai doan 2 - Warehouse & SKU**, **Giai doan 3 - Import da san**, **Giai doan 4 - FIFO Engine** va dang bat dau **Giai doan 5 - Doi soat**.

Muc tieu cua giai doan nay:

- Cau truc du an ro rang.
- Google Sheet template co cac sheet cot loi.
- Danh muc san pham, mapping SKU, kho, nha cung cap.
- Cau hinh mau de trien khai moi truong.
- Tai lieu va test nen tang.

## Cau truc

```text
.
├── config/                 # Cau hinh mau
├── docs/                   # Tai lieu van hanh va lo trinh
├── src/omni_erp/           # Ma nguon ung dung
│   └── foundation/         # Schema va validator nen tang
│   └── warehouse/          # San pham, kho, lo hang, phieu nhap/xuat, FIFO
│   └── importers/          # Import Shopee, TikTok Shop, Lazada va mapping SKU
│   └── fifo/               # Gia von FIFO, xuat tu dong, hoan kho, adjustment
│   └── reconciliation/     # Doanh thu, phi, COD, tien thuc nhan, loi nhuan
├── templates/google_sheets # CSV template dung de tao Google Sheet
├── templates/marketplace_imports
└── tests/                  # Kiem thu nen tang
```

## Kiem thu

Chay toan bo test:

```powershell
python -m unittest discover -s tests
```

## Google Sheet template

Thu muc `templates/google_sheets` chua cac file CSV dai dien cho tung sheet:

- `products.csv`
- `sku_mapping.csv`
- `warehouses.csv`
- `suppliers.csv`
- `inventory_lots.csv`
- `settings.csv`

Chi tiet cot va y nghia nam trong `docs/google-sheet-template.md`.

## Nguyen tac phat trien

Moi giai doan duoc thuc hien theo vong lap:

1. Hoan thanh tinh nang trong pham vi giai doan.
2. Chay kiem thu.
3. Commit ro noi dung.
4. Day len GitHub.
5. Kiem tra loi va sua neu co.
