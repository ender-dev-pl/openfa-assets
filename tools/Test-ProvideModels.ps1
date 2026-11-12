$ErrorActionPreference = 'Stop'
$repositoryRoot = Split-Path -Parent $PSScriptRoot
$testRoot = Join-Path $repositoryRoot ('artifacts/provide models test ' + [Guid]::NewGuid().ToString('N'))
$actionDirectory = Join-Path $testRoot '.github/actions/provide-models'
New-Item -ItemType Directory -Path $actionDirectory -Force | Out-Null
$sourceScript = Join-Path $repositoryRoot '.github/actions/provide-models/Provide-Models.ps1'
$fixtureScript = Join-Path $actionDirectory 'Provide-Models.ps1'
Copy-Item -LiteralPath $sourceScript -Destination $fixtureScript
$previousEnvironmentFile = $env:GITHUB_ENV
try {
    foreach ($relative in @('gallery/catalogue.json', 'project/layout.json')) {
        $path = Join-Path $testRoot $relative
        New-Item -ItemType Directory -Path (Split-Path -Parent $path) -Force | Out-Null
        '{}' | Set-Content -LiteralPath $path
    }
    $env:GITHUB_ENV = Join-Path $testRoot 'environment.txt'
    'EXISTING_VALUE=preserved' | Set-Content -LiteralPath $env:GITHUB_ENV
    & $fixtureScript
    $lines = @(Get-Content -LiteralPath $env:GITHUB_ENV)
    if ($lines.Count -ne 2 -or $lines[0] -ne 'EXISTING_VALUE=preserved' -or
        $lines[1] -cne "OpenFaAssetSourceRoot=$([IO.Path]::GetFullPath($testRoot))") {
        throw 'The action did not append the correct source path containing spaces.'
    }
    # A second invocation must fail before exporting an incomplete source checkout.
    Remove-Item -LiteralPath (Join-Path $testRoot 'project/layout.json')
    $rejected = $false
    try { & $fixtureScript }
    catch {
        if ($_.Exception.Message -notlike '*missing required input: project/layout.json*') { throw }
        $rejected = $true
    }
    if (-not $rejected -or @(Get-Content -LiteralPath $env:GITHUB_ENV).Count -ne 2) {
        throw 'Missing model inputs were not rejected before exporting the path.'
    }
    $env:GITHUB_ENV = ''
    $rejected = $false
    try { & $sourceScript }
    catch {
        if ($_.Exception.Message -notlike '*GITHUB_ENV is required*') { throw }
        $rejected = $true
    }
    if (-not $rejected) { throw 'The action accepted a missing Actions environment file.' }
    Write-Host 'PROVIDE_MODELS_TEST_PASSED'
}
finally {
    $env:GITHUB_ENV = $previousEnvironmentFile
}
