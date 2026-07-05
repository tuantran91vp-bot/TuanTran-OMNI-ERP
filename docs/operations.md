# Operations

Giai doan 8 tap trung vao hoan thien van hanh: Apps Script, tu dong hoa, backup, toi uu hieu nang va dong goi.

## Apps Script

Thu muc `apps_script` chua scaffold de gan vao Google Sheet:

- `appsscript.json`: manifest V8, timezone Viet Nam.
- `Code.gs`: menu `OMNI ERP`, setup sheet, refresh dashboard marker, backup marker.

## Automation

Ke hoach mac dinh:

- Sync marketplace orders luc 07:00.
- Refresh dashboard luc 07:15.
- Create backup luc 23:30.

## Backup

Module `omni_erp.operations.backup` tao zip archive cho cac tai san trien khai:

- `config`
- `docs`
- `templates`
- `apps_script`
- `README.md`
- `pyproject.toml`

## Packaging

Module `omni_erp.operations.packaging` kiem tra cac file bat buoc truoc khi dong goi. Package duoc xem la hoan tat khi `PackageManifest.is_complete` la `True`.

## Performance

Giai doan nay giu cac aggregation chinh o dang mot lan duyet du lieu va dung `Decimal` de tranh sai so tien. Cac exporter va backup chi xu ly file theo stream/zip thay vi giu output lon khong can thiet trong domain layer.

## Quality Gate

Xem `docs/quality.md` de chay cung quality gate tren local va GitHub Actions.
