param(
    [Parameter(Mandatory = $true)]
    [string]$Blender,

    [Parameter(Mandatory = $true)]
    [string]$Source,

    [string]$Output = "evidence/runtime-probe.json"
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$probe = Join-Path $PSScriptRoot "blender_runtime_probe.py"

if (-not (Test-Path -LiteralPath $Blender -PathType Leaf)) {
    throw "Blender executable not found: $Blender"
}
if (-not (Test-Path -LiteralPath $Source -PathType Leaf)) {
    throw "AWFUL source not found: $Source"
}
if (-not (Test-Path -LiteralPath $probe -PathType Leaf)) {
    throw "Runtime probe not found: $probe"
}

if (-not [System.IO.Path]::IsPathRooted($Output)) {
    $Output = Join-Path $repoRoot $Output
}

$outputDir = Split-Path -Parent $Output
if ($outputDir) {
    New-Item -ItemType Directory -Force -Path $outputDir | Out-Null
}

& $Blender `
    --background `
    --factory-startup `
    --disable-autoexec `
    --python-exit-code 1 `
    --python $probe `
    -- `
    --source $Source `
    --output $Output

if ($LASTEXITCODE -ne 0) {
    throw "AWFUL Blender runtime probe failed with exit code $LASTEXITCODE. Evidence: $Output"
}

Write-Host "AWFUL Blender runtime probe passed: $Output"
