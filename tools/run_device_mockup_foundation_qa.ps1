param(
    [string]$Blender = "D:\Blender Foundation\Blender 5.2\blender.exe"
)

$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $PSScriptRoot

if (-not (Test-Path -LiteralPath $Blender -PathType Leaf)) {
    throw "Blender executable not found: $Blender"
}

function Invoke-BlenderScript {
    param([string]$Script, [string[]]$Args = @())
    $full = Join-Path $repo $Script
    & $Blender --background --factory-startup --python-exit-code 1 --python $full -- @Args
    if ($LASTEXITCODE -ne 0) {
        throw "Blender QA failed for $Script with exit code $LASTEXITCODE"
    }
}

Invoke-BlenderScript "assets/device_mockups/common/smoke_test.py"
Invoke-BlenderScript "assets/device_mockups/iphone_17/generate_foundation.py"
Invoke-BlenderScript "assets/device_mockups/ipad_pro/generate_foundation.py" @("--size", "11")
Invoke-BlenderScript "assets/device_mockups/ipad_pro/generate_foundation.py" @("--size", "13")
Invoke-BlenderScript "assets/device_mockups/macbook_pro_14/generate_foundation.py"

$evidenceFiles = @(
    "assets/device_mockups/iphone_17/evidence/foundation_validation.json",
    "assets/device_mockups/ipad_pro/evidence/ipad_pro_11_m5_validation.json",
    "assets/device_mockups/ipad_pro/evidence/ipad_pro_13_m5_validation.json",
    "assets/device_mockups/macbook_pro_14/evidence/foundation_validation.json"
)

$results = foreach ($relative in $evidenceFiles) {
    $path = Join-Path $repo $relative
    $item = Get-Content -LiteralPath $path -Raw | ConvertFrom-Json
    if (-not $item.passed) { throw "Validation JSON reports failure: $relative" }
    [ordered]@{ asset_id = $item.asset_id; passed = [bool]$item.passed; evidence = $relative }
}

$suitePath = Join-Path $repo "assets/device_mockups/foundation_suite_validation.json"
[ordered]@{ blender = $Blender; passed = $true; assets = $results } |
    ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $suitePath -Encoding utf8
Write-Host "AWFUL device foundation QA passed: $suitePath"
