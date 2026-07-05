# Quality

Quality gate hien tai dung thu vien chuan Python, khong can cai dependency ngoai.

## Local

Chay tren Windows PowerShell:

```powershell
.\scripts\check.ps1
```

Lenh nay se chay:

- `python -m unittest discover -s tests`
- `python -m compileall src tests`

## GitHub Actions

Workflow `.github/workflows/ci.yml` tu dong chay tren:

- Push vao `main`.
- Pull request vao `main`.

CI dung Python 3.11 va chay cung quality gate voi local.
