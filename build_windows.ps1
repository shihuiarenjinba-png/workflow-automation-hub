# Workflow Automation Hub - Windows build / Windows ビルド
$ErrorActionPreference = "Stop"

if (-not (Test-Path ".venv")) {
    py -3 -m venv .venv
}

$python = Join-Path $PWD ".venv\Scripts\python.exe"
& $python -m pip install --upgrade pip
& $python -m pip install -r requirements.txt pyinstaller

& $python -m PyInstaller `
    --noconfirm `
    --clean `
    --onefile `
    --windowed `
    --name WorkflowAutomationHub `
    --add-data "resources;resources" `
    --collect-all googleapiclient `
    --collect-all google_auth_oauthlib `
    desktop_app.py

Write-Host "Build complete / ビルド完了: dist\WorkflowAutomationHub.exe"
