param(
    [string]$SiteRepo = "$env:USERPROFILE\projects\looksawful.ru",
    [string]$StudioRepo = "$env:USERPROFILE\projects\awful-studio-production",
    [string]$UnityProject = (Split-Path $PSScriptRoot -Parent),
    [string]$Blender = "$env:USERPROFILE\.local\bin\blender.cmd"
)

$ErrorActionPreference = 'Stop'
$generated = Join-Path $UnityProject 'Assets\AwfulViewer\Generated'
$studioOut = Join-Path $generated 'Models\Studio'
$siteOut = Join-Path $generated 'Models\Site'
$logoOut = Join-Path $generated 'Logos'

@($studioOut, $siteOut, $logoOut) | ForEach-Object {
    New-Item -ItemType Directory -Force -Path $_ | Out-Null
}

if (!(Test-Path $SiteRepo)) { throw "Site repo not found: $SiteRepo" }
if (!(Test-Path $StudioRepo)) { throw "Studio repo not found: $StudioRepo" }
if (!(Test-Path $Blender)) { throw "Blender CLI not found: $Blender" }

Get-ChildItem $studioOut -Filter '*.fbx' -ErrorAction SilentlyContinue | Remove-Item -Force
Get-ChildItem $siteOut -Filter '*.fbx' -ErrorAction SilentlyContinue | Remove-Item -Force
Get-ChildItem $logoOut -Filter '*.png' -ErrorAction SilentlyContinue | Remove-Item -Force

$magick = (Get-Command magick -ErrorAction Stop).Source
$logoSource = Join-Path $SiteRepo 'public\media\clients\logo-wall'
$logos = Get-ChildItem $logoSource -Filter 'client-logo-*.webp' | Sort-Object Name
foreach ($logo in $logos) {
    $target = Join-Path $logoOut ($logo.BaseName + '.png')
    & $magick $logo.FullName $target
    if ($LASTEXITCODE -ne 0) { throw "Logo conversion failed: $($logo.Name)" }
}

$python = (Get-Command python -ErrorAction Stop).Source
$catalogScript = Join-Path $PSScriptRoot 'sync_catalog.py'
$catalogOut = Join-Path $generated 'catalog.json'
& $python $catalogScript $SiteRepo $catalogOut
if ($LASTEXITCODE -ne 0) { throw "Catalog sync failed with exit code $LASTEXITCODE" }

$blenderScript = Join-Path $PSScriptRoot 'sync_blender_assets.py'
& $Blender --background --factory-startup --python $blenderScript -- `
    --studio $StudioRepo --site $SiteRepo --out $generated
if ($LASTEXITCODE -ne 0) { throw "Blender asset sync failed with exit code $LASTEXITCODE" }

$studioCount = @(Get-ChildItem $studioOut -Filter '*.fbx').Count
$siteCount = @(Get-ChildItem $siteOut -Filter '*.fbx').Count
$logoCount = @(Get-ChildItem $logoOut -Filter '*.png').Count

$report = [ordered]@{
    generatedAt = (Get-Date).ToString('o')
    studioModels = $studioCount
    siteModels = $siteCount
    logos = $logoCount
    sources = [ordered]@{
        site = $SiteRepo
        studio = $StudioRepo
    }
}
$report | ConvertTo-Json -Depth 4 | Set-Content -Encoding utf8 (Join-Path $generated 'sync-report.json')

Write-Host "AWFUL sync complete: $studioCount studio models, $siteCount site models, $logoCount logos"
