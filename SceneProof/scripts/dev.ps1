# SceneProof local demo: API + Vite (two windows). Requires Python and Node on PATH.
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

Write-Host "Starting SceneProof API on http://127.0.0.1:8000 ..."
Start-Process powershell -ArgumentList @(
  '-NoExit', '-Command',
  "Set-Location '$root\backend'; python -m uvicorn app.main:app --reload --port 8000"
)

Start-Sleep -Seconds 2

Write-Host "Starting Vite on http://127.0.0.1:5173 ..."
Set-Location "$root\frontend"
npm run dev
