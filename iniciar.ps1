# Encerra servidor antigo na porta 8765 (se houver) e sobe o novo
Get-NetTCPConnection -LocalPort 8765 -State Listen -ErrorAction SilentlyContinue |
    ForEach-Object { taskkill /PID $_.OwningProcess /F /T | Out-Null }

Set-Location $PSScriptRoot
.\.venv\Scripts\Activate.ps1
uvicorn backend.main:app --host 127.0.0.1 --port 8765