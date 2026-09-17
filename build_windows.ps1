# Workflow Automation Hub - Windows build / Windows ビルド
$ErrorActionPreference = "Stop"

if (-not (Test-Path ".venv")) {
    py -3 -m venv .venv
}

$python = Join-Path $PWD ".venv\Scripts\python.exe"
& $python -m pip install --upgrade pip
& $python -m pip install -r requirements-build.txt
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

Write-Host "==> Generate dependency evidence / 依存関係証跡を生成"
& $python generate_dependency_evidence.py --requirements requirements.txt --out-dir dist
if ($LASTEXITCODE -ne 0) {
    throw "Dependency evidence generation failed / 依存関係証跡の生成に失敗しました"
}
& $python -m pip freeze --all | Set-Content -Encoding utf8 "dist\build-dependencies.lock.txt"
if ($LASTEXITCODE -ne 0) {
    throw "Dependency lock snapshot failed / 依存関係ロックの記録に失敗しました"
}

$EvidenceFiles = @(
    "dist\SBOM.spdx.json",
    "dist\THIRD_PARTY_NOTICES_REVIEW.txt",
    "dist\build-dependencies.lock.txt"
)
foreach ($EvidenceFile in $EvidenceFiles) {
    if (-not (Test-Path $EvidenceFile)) {
        throw "Missing dependency evidence / 依存関係証跡がありません: $EvidenceFile"
    }
    $Hash = (Get-FileHash -Algorithm SHA256 $EvidenceFile).Hash.ToLowerInvariant()
    "$Hash  $([IO.Path]::GetFileName($EvidenceFile))" | Set-Content -Encoding ascii "$EvidenceFile.sha256.txt"
}

Write-Host "Build complete / ビルド完了: dist\WorkflowAutomationHub.exe"
Write-Host "Dependency review evidence / 依存関係レビュー証跡: dist\SBOM.spdx.json, dist\THIRD_PARTY_NOTICES_REVIEW.txt, dist\build-dependencies.lock.txt"
Write-Host "NOTE: Product LICENSE and manual third-party license/NOTICE review are still required before sales release."
