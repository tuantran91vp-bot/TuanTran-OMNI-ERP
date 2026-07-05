# Usage

OMNI ERP hien tai la goi Python + Apps Script scaffold dung cho quan tri kho, SKU, FIFO, doi soat, dashboard va bao cao.

## Chay truc tiep trong repo

Tren Windows PowerShell:

```powershell
$env:PYTHONPATH="src"
python -m omni_erp --version
python -m omni_erp check --project-root .
python -m omni_erp package --project-root .
python -m omni_erp backup --project-root . --output dist/omni-erp-assets.zip
```

## Dong goi nhanh

```powershell
.\scripts\package.ps1
```

Lenh nay se:

- Chay test va compile.
- Kiem tra manifest dong goi.
- Tao file `dist/omni-erp-assets.zip`.

## Web app

Mo file sau bang trinh duyet:

```text
web/index.html
```

Che do nay dung duoc dashboard/demo data. De import `.xlsx`, chay local server:

```powershell
.\scripts\start-web.ps1
```

Sau do mo:

```text
http://127.0.0.1:8765
```

Khi chay bang local server, moi lan them don hoac import file, du lieu duoc ghi vao file:

```text
data/omni-data.json
```

Web app hien co:

- Dashboard KPI.
- Ton kho theo kho/SKU.
- Them don hang demo va luu vao `localStorage`.
- Import don hang `.xlsx`/`.csv` khi chay qua local server.
- Bao cao loc theo ngay/san va tai CSV.
- Trang van hanh xem automation/package status.

## Cai dat dang package Python

Neu muon cai vao moi truong Python:

```powershell
python -m pip install .
omni-erp --version
omni-erp check --project-root .
```

## Google Sheet

1. Tao Google Sheet moi.
2. Copy noi dung trong `apps_script/Code.gs` va `apps_script/appsscript.json` vao Apps Script project.
3. Reload Google Sheet.
4. Dung menu `OMNI ERP` de setup sheet va refresh dashboard marker.
