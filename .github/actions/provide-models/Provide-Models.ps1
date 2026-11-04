$ErrorActionPreference = 'Stop'

if ([string]::IsNullOrWhiteSpace($env:GITHUB_ENV)) {
    throw 'GITHUB_ENV is required to export model build inputs.'
}
$sourceRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
foreach ($relative in @('gallery/catalogue.json', 'project/layout.json')) {
    if (-not (Test-Path -LiteralPath (Join-Path $sourceRoot $relative) -PathType Leaf)) {
        throw "Model action repository is missing required input: $relative"
    }
}
if ($sourceRoot.Contains("`r") -or $sourceRoot.Contains("`n")) {
    throw 'Model source path cannot contain a newline.'
}
"OpenFaAssetSourceRoot=$sourceRoot" | Out-File -LiteralPath $env:GITHUB_ENV -Encoding utf8 -Append
Write-Host "Model build inputs: $sourceRoot"
