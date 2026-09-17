$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Manifest = Join-Path $Root "MANIFEST_SHA256.txt"

if (-not (Test-Path $Manifest)) {
    throw "MANIFEST_SHA256.txt is missing"
}

$Checked = 0
foreach ($Line in Get-Content -LiteralPath $Manifest -Encoding utf8) {
    if ([string]::IsNullOrWhiteSpace($Line)) { continue }
    if ($Line -notmatch '^([0-9a-fA-F]{64})  (.+)$') {
        throw "Invalid manifest line: $Line"
    }
    $Expected = $Matches[1].ToLowerInvariant()
    $Relative = $Matches[2]
    if ($Relative -match '(^|[\\/])\.\.([\\/]|$)' -or [IO.Path]::IsPathRooted($Relative)) {
        throw "Unsafe manifest path: $Relative"
    }
    $Target = Join-Path $Root ($Relative -replace '/', '\\')
    if (-not (Test-Path -LiteralPath $Target -PathType Leaf)) {
        throw "Missing file: $Relative"
    }
    $Actual = (Get-FileHash -Algorithm SHA256 -LiteralPath $Target).Hash.ToLowerInvariant()
    if ($Actual -ne $Expected) {
        throw "Hash mismatch: $Relative"
    }
    $Checked++
}

if ($Checked -le 0) {
    throw "No files were verified"
}

Write-Host "PASS: verified $Checked file(s) against MANIFEST_SHA256.txt"

