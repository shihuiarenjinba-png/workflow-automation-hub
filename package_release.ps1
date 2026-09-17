param(
    [ValidateSet("RC", "Sales")]
    [string]$Mode = "RC",
    [string]$Version = "0.1.0",
    [string]$SourceCommit = ""
)

$ErrorActionPreference = "Stop"

function Require-File([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "Required file missing / 必須ファイルがありません: $Path"
    }
}

if (-not $SourceCommit) {
    $SourceCommit = (& git rev-parse HEAD).Trim()
}
if ($SourceCommit -notmatch '^[0-9a-fA-F]{40}$') {
    throw "SourceCommit must be an exact 40-character Git SHA."
}
$SourceCommit = $SourceCommit.ToLowerInvariant()

$GitHead = (& git rev-parse HEAD).Trim().ToLowerInvariant()
if ($GitHead -ne $SourceCommit) {
    throw "Checked-out source does not match SourceCommit: HEAD=$GitHead expected=$SourceCommit"
}

Require-File "dist\WorkflowAutomationHub.exe"
Require-File "dist\SBOM.spdx.json"
Require-File "dist\THIRD_PARTY_NOTICES_REVIEW.txt"
Require-File "dist\build-dependencies.lock.txt"
Require-File "02_SUPPORT_DIAGNOSTICS.bat"
Require-File "VERIFY_FILES.ps1"
Require-File "SUPPORT_JA.md"
Require-File "SUPPORT_EN.md"
Require-File "README.md"
Require-File "COMPLIANCE.md"
Require-File "CODE_OPERATOR_HANDOFF.md"
Require-File "SALES_RELEASE_CHECKLIST.md"

if ($Mode -eq "Sales") {
    Require-File "LICENSE"
    Require-File "THIRD_PARTY_NOTICES.txt"
    Require-File "SALES_RELEASE_APPROVED.txt"
    $Approval = Get-Content -LiteralPath "SALES_RELEASE_APPROVED.txt" -Raw -Encoding utf8
    if ($Approval -notmatch "(?m)^source_commit=$SourceCommit$") {
        throw "SALES_RELEASE_APPROVED.txt does not approve this exact source commit."
    }
    if ($Approval -notmatch "(?m)^manual_acceptance=PASS$") {
        throw "SALES_RELEASE_APPROVED.txt does not record manual_acceptance=PASS."
    }
}

$Label = if ($Mode -eq "Sales") { "Windows-x64" } else { "Windows-x64-RC" }
$BaseName = "WorkflowAutomationHub-v$Version-$Label"
$ReleaseDir = Join-Path $PWD "release"
$Stage = Join-Path $ReleaseDir $BaseName
$Zip = Join-Path $ReleaseDir "$BaseName.zip"
$ZipHashFile = "$Zip.sha256.txt"

if (Test-Path $Stage) { Remove-Item -Recurse -Force $Stage }
if (Test-Path $Zip) { Remove-Item -Force $Zip }
if (Test-Path $ZipHashFile) { Remove-Item -Force $ZipHashFile }
New-Item -ItemType Directory -Force -Path $Stage | Out-Null

$CommonFiles = @(
    "dist\WorkflowAutomationHub.exe",
    "02_SUPPORT_DIAGNOSTICS.bat",
    "VERIFY_FILES.ps1",
    "SUPPORT_JA.md",
    "SUPPORT_EN.md",
    "README.md",
    "COMPLIANCE.md",
    "CODE_OPERATOR_HANDOFF.md",
    "SALES_RELEASE_CHECKLIST.md",
    "dist\SBOM.spdx.json",
    "dist\THIRD_PARTY_NOTICES_REVIEW.txt",
    "dist\build-dependencies.lock.txt"
)
foreach ($File in $CommonFiles) {
    Copy-Item -LiteralPath $File -Destination (Join-Path $Stage ([IO.Path]::GetFileName($File)))
}
if ($Mode -eq "Sales") {
    Copy-Item -LiteralPath "LICENSE" -Destination (Join-Path $Stage "LICENSE")
    Copy-Item -LiteralPath "THIRD_PARTY_NOTICES.txt" -Destination (Join-Path $Stage "THIRD_PARTY_NOTICES.txt")
}

$ExeHash = (Get-FileHash -Algorithm SHA256 -LiteralPath "dist\WorkflowAutomationHub.exe").Hash.ToLowerInvariant()
$LicenseStatus = if ($Mode -eq "Sales") { "Included and operator-reviewed" } else { "Formal product license not included in RC; sales mode is fail-closed until provided" }
$SalesStatus = if ($Mode -eq "Sales") { "SALES PACKAGE - exact commit manually approved" } else { "RELEASE CANDIDATE - NOT APPROVED FOR SALES" }

@"
Product: Workflow Automation Hub
Version: $Version
Package mode: $Mode
Architecture: Windows x64 target
Source commit: $SourceCommit
WorkflowAutomationHub.exe SHA-256: $ExeHash
Authenticode: DEFERRED / NOT VERIFIED
Product license: $LicenseStatus
Sales status: $SalesStatus
"@ | Set-Content -LiteralPath (Join-Path $Stage "RELEASE_INFO.txt") -Encoding utf8

$ManifestLines = @()
Get-ChildItem -LiteralPath $Stage -File | Where-Object { $_.Name -ne "MANIFEST_SHA256.txt" } | Sort-Object Name | ForEach-Object {
    $Hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $_.FullName).Hash.ToLowerInvariant()
    $ManifestLines += "$Hash  $($_.Name)"
}
$ManifestLines | Set-Content -LiteralPath (Join-Path $Stage "MANIFEST_SHA256.txt") -Encoding ascii

& powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $Stage "VERIFY_FILES.ps1")
if ($LASTEXITCODE -ne 0) {
    throw "Staging manifest verification failed / 配布前マニフェスト検証失敗"
}

Compress-Archive -Path (Join-Path $Stage "*") -DestinationPath $Zip -CompressionLevel Optimal
Require-File $Zip

$ZipHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $Zip).Hash.ToLowerInvariant()
"$ZipHash  $([IO.Path]::GetFileName($Zip))" | Set-Content -LiteralPath $ZipHashFile -Encoding ascii

$VerifyRoot = Join-Path $env:TEMP ("WorkflowAutomationHub-package-verify-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Force -Path $VerifyRoot | Out-Null
try {
    Expand-Archive -LiteralPath $Zip -DestinationPath $VerifyRoot -Force
    & powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $VerifyRoot "VERIFY_FILES.ps1")
    if ($LASTEXITCODE -ne 0) { throw "Extracted package manifest verification failed." }

    $SelfTest = Start-Process -FilePath (Join-Path $VerifyRoot "WorkflowAutomationHub.exe") -ArgumentList "--self-test" -Wait -PassThru
    if ($SelfTest.ExitCode -ne 0) { throw "Extracted packaged EXE self-test failed: $($SelfTest.ExitCode)" }

    $ReportPath = Join-Path $VerifyRoot "support_report-ci.txt"
    $DiagnoseArgs = "--diagnose `"$ReportPath`""
    $Diagnose = Start-Process -FilePath (Join-Path $VerifyRoot "WorkflowAutomationHub.exe") -ArgumentList $DiagnoseArgs -Wait -PassThru
    if ($Diagnose.ExitCode -ne 0) { throw "Extracted packaged EXE diagnostics failed: $($Diagnose.ExitCode)" }
    Require-File $ReportPath
    $Report = Get-Content -LiteralPath $ReportPath -Raw -Encoding utf8 | ConvertFrom-Json
    if (-not $Report.overall_ok) { throw "Extracted packaged EXE diagnostics reported overall_ok=false" }
    if ($Report.privacy.contains_oauth_token -or $Report.privacy.contains_client_secret -or $Report.privacy.contains_username -or $Report.privacy.contains_full_paths) {
        throw "Support report privacy contract failed."
    }
}
finally {
    if (Test-Path $VerifyRoot) { Remove-Item -Recurse -Force $VerifyRoot }
}

Write-Host "Package verified / ZIP検証完了: $Zip"
Write-Host "ZIP SHA-256: $ZipHash"
