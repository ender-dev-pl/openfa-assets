param(
    [string]$Version = '4.5.15',
    [string]$InstallRoot = 'C:/tools/blender',
    [string]$CacheDirectory = (Join-Path $PSScriptRoot '../artifacts/blender-downloads')
)

$ErrorActionPreference = 'Stop'
if ($Version -notmatch '^4\.5\.\d+$') { throw 'Specify an official Blender 4.5 LTS patch version.' }
$InstallRoot = [IO.Path]::GetFullPath($InstallRoot)
$CacheDirectory = [IO.Path]::GetFullPath($CacheDirectory)
$archiveName = "blender-$Version-windows-x64.zip"
$releaseUrl = 'https://download.blender.org/release/Blender4.5'
$destination = Join-Path $InstallRoot "blender-$Version-windows-x64"
$executable = Join-Path $destination 'blender.exe'
New-Item -ItemType Directory -Force $InstallRoot, $CacheDirectory | Out-Null
if (-not (Test-Path -LiteralPath $executable)) {
    $checksums = (Invoke-WebRequest "$releaseUrl/blender-$Version.sha256").Content
    $line = @($checksums -split "`n" | Where-Object { $_ -match ([regex]::Escape($archiveName) + '$') })
    if ($line.Count -ne 1 -or $line[0] -notmatch '^([0-9a-fA-F]{64})\s+\*?') {
        throw 'Official SHA-256 entry is missing or ambiguous.'
    }
    $expected = $Matches[1]
    $archive = Join-Path $CacheDirectory $archiveName
    if (-not (Test-Path -LiteralPath $archive)) {
        Invoke-WebRequest "$releaseUrl/$archiveName" -OutFile $archive
    }
    $actual = (Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash
    if ($actual -ne $expected) { throw "Blender archive checksum mismatch: $archive" }
    if (Test-Path -LiteralPath $destination) { throw "Incomplete installation already exists: $destination" }
    Expand-Archive -LiteralPath $archive -DestinationPath $InstallRoot
    [ordered]@{ version = $Version; source = "$releaseUrl/$archiveName"; sha256 = $actual } |
        ConvertTo-Json | Set-Content (Join-Path $destination 'openfa-installation.json')
}
New-Item -ItemType Directory -Force (Join-Path $destination '4.5/config') | Out-Null
$launcher = @'
param(
    [string]$PythonScript,
    [string[]]$ScriptArguments = @(),
    [switch]$Background,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$BlenderArguments = @()
)
$ErrorActionPreference = 'Stop'
$installation = Join-Path $PSScriptRoot 'INSTALLATION'
$env:BLENDER_USER_CONFIG = Join-Path $installation '4.5/config'
$invokeArguments = @($BlenderArguments)
if ($Background) { $invokeArguments += '--background' }
if ($PythonScript) {
    $invokeArguments += @('--python-exit-code', '1', '--python', [IO.Path]::GetFullPath($PythonScript))
    if ($ScriptArguments.Count) { $invokeArguments += @('--') + $ScriptArguments }
}
& (Join-Path $installation 'blender.exe') @invokeArguments
exit $LASTEXITCODE
'@
$launcher.Replace('INSTALLATION', "blender-$Version-windows-x64") |
    Set-Content (Join-Path $InstallRoot 'openfa-blender.ps1')
& $executable --version
if ($LASTEXITCODE -ne 0) { throw 'Blender version verification failed.' }
Write-Host "OpenFA launcher: $(Join-Path $InstallRoot 'openfa-blender.ps1')"
