# OMNI ERP Roadmap

## Giai doan 1 - Foundation

- Cau truc du an.
- Google Sheet template.
- Danh muc san pham.
- Mapping SKU.
- Kho.
- Nha cung cap.
- Cau hinh.
- README va tai lieu.

## Giai doan 2 - Warehouse & SKU

- Quan ly san pham.
- Nhieu kho.
- FIFO.
- Phieu nhap/xuat.
- Kiem tra ton kho.

Trang thai trien khai:

- Da co domain model cho `Product`, `Warehouse`, `InventoryLot`, `StockMovement`.
- Da co `WarehouseService` de nhap kho, xuat kho FIFO, tinh ton theo kho/SKU.
- Da co test cho nhieu kho, FIFO, phieu nhap/xuat va loi thieu ton.

## Giai doan 3 - Import da san

- Shopee.
- TikTok Shop.
- Lazada.
- Mapping SKU.
- Chuan hoa du lieu.

Trang thai trien khai:

- Da co model `NormalizedOrderLine` cho dau ra chung cua moi san.
- Da co `SkuMapper` de map SKU san ve SKU noi bo va tinh so luong tru kho.
- Da co default column map va template CSV mau cho Shopee, TikTok Shop, Lazada.
- Da co test cho import tung san va loi SKU chua mapping.

## Giai doan 4 - FIFO Engine

- Tinh gia von.
- Xuat kho tu dong.
- Hoan kho.
- Dieu chinh ton.

Trang thai trien khai:

- Da co `FifoEngine` de xuat kho tu dong tu `NormalizedOrderLine`.
- Da tinh COGS theo tung movement FIFO.
- Da ho tro hoan kho ve dung lot da xuat.
- Da ho tro adjustment tang/giam ton, giam ton theo FIFO.

## Giai doan 5 - Doi soat

- Doanh thu.
- Phi san.
- Voucher.
- COD.
- Tien thuc nhan.
- Loi nhuan.

Trang thai trien khai:

- Da co `ReconciliationResult` cho ket qua doi soat theo dong don.
- Da tinh doanh thu gross, voucher, phi san, phi thanh toan, COD, tien thuc nhan.
- Da tinh loi nhuan tu tien thuc nhan tru COGS.
- Da ho tro nhap tien thuc nhan thuc te tu sao ke/bao cao san.

## Giai doan 6 - Dashboard

- KPI.
- Bieu do.
- Ton kho.
- Doanh thu.
- Loi nhuan.

## Giai doan 7 - Bao cao

- Xuat Excel.
- PDF.
- Bao cao theo thoi gian.
- Bao cao theo san.

## Giai doan 8 - Hoan thien

- Apps Script.
- Tu dong hoa.
- Backup.
- Toi uu hieu nang.
- Dong goi.

## Vong lap moi giai doan

Commit -> kiem tra GitHub -> sua loi -> kiem thu.
