# TuanTran OMNI ERP

OMNI ERP la he thong quan tri ban hang da san, tap trung vao Google Sheet, kho, SKU, FIFO, doi soat doanh thu va bao cao loi nhuan.

## Trang thai lo trinh

Da hoan thanh **Giai doan 1 - Foundation**, **Giai doan 2 - Warehouse & SKU**, **Giai doan 3 - Import da san**, **Giai doan 4 - FIFO Engine**, **Giai doan 5 - Doi soat**, **Giai doan 6 - Dashboard**, **Giai doan 7 - Bao cao** va dang hoan thien **Giai doan 8 - Hoan thien**.

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
│   └── dashboard/          # KPI, bieu do, ton kho, doanh thu, loi nhuan
│   └── reports/            # Bao cao theo thoi gian/san, CSV Excel, PDF
│   └── operations/         # Apps Script, automation, backup, packaging
├── apps_script/            # Google Apps Script scaffold
├── templates/google_sheets # CSV template dung de tao Google Sheet
├── templates/marketplace_imports
└── tests/                  # Kiem thu nen tang
```

## Kiem thu

Chay toan bo test:

```powershell
python -m unittest discover -s tests
```

Chay quality gate day du:

```powershell
.\scripts\check.ps1
```

GitHub Actions se tu dong chay test va compile tren moi push/pull request vao `main`.

## Su dung phan mem

Mo web app:

```text
web/index.html
```

Web app co the import `.xlsx/.csv` ngay khi mo `web/index.html`. Neu trinh duyet khong ho tro giai nen XLSX truc tiep, chay qua local server:

```powershell
.\scripts\start-web.ps1
```

Sau do mo:

```text
http://127.0.0.1:8765
```

Khi chay bang server local, du lieu se duoc luu truc tiep vao:

```text
data/omni-data.json
```

Chay truc tiep trong repo:

```powershell
$env:PYTHONPATH="src"
python -m omni_erp --version
python -m omni_erp check --project-root .
python -m omni_erp package --project-root .
```

Dong goi nhanh:

```powershell
.\scripts\package.ps1
```

Huong dan chi tiet nam trong `docs/usage.md`.

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
