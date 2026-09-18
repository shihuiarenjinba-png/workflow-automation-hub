# Workflow Automation Hub - Windows build / Windows ビルド
$ErrorActionPreference = "Stop"
$LockFile = Join-Path $PSScriptRoot "requirements-lock.txt"

if (-not (Test-Path $LockFile)) {
    throw "Dependency lock not found / dependency lockがありません: $LockFile"
}

if (-not (Test-Path ".venv")) {
    py -3 -m venv .venv
}

$python = Join-Path $PWD ".venv\Scripts\python.exe"
& $python -m pip install --require-hashes -r $LockFile
if ($LASTEXITCODE -ne 0) {
    throw "Locked dependency installation failed / 固定依存の導入に失敗しました"
}
& $python -m pip check
& $python -m unittest discover -s tests -v
& $python desktop_app.py --self-test

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

if (-not (Test-Path "dist\WorkflowAutomationHub.exe")) {
    throw "EXE was not created / EXEが作成されませんでした"
}

$process = Start-Process -FilePath ".\dist\WorkflowAutomationHub.exe" -ArgumentList "--self-test" -Wait -PassThru
if ($process.ExitCode -ne 0) {
    throw "Packaged EXE self-test failed / EXE自己診断に失敗しました (exit=$($process.ExitCode))"
}

Write-Host "Build complete / ビルド完了: dist\WorkflowAutomationHub.exe"
