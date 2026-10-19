param([Parameter(Mandatory=$true)][string]$Archive)
$ErrorActionPreference = 'Stop'
if (Get-NetTCPConnection -LocalPort 8501 -State Listen -ErrorAction SilentlyContinue) { throw 'Port 8501 zajęty.' }
$archivePath = (Resolve-Path -LiteralPath $Archive).Path
$repo = Split-Path $PSScriptRoot -Parent
$testRoot = Join-Path $repo ('build\first-use-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '\Świeża paczka ze spacjami')
New-Item -ItemType Directory -Path $testRoot -Force | Out-Null
Expand-Archive -LiteralPath $archivePath -DestinationPath $testRoot
$exe = Join-Path $testRoot 'AutoReportAnalyst\AutoReportAnalyst.exe'
if (!(Test-Path -LiteralPath $exe)) { throw 'Brak EXE w paczce.' }
$freshHome = Join-Path $testRoot 'fresh-user'
New-Item -ItemType Directory -Path $freshHome -Force | Out-Null
$names = @('PATH','PYTHONPATH','PYTHONHOME','PYTHONNOUSERSITE','AUTOREPORT_HOME','APPDATA','LOCALAPPDATA','STREAMLIT_SERVER_HEADLESS')
$saved = @{}
foreach ($name in $names) { $saved[$name] = [Environment]::GetEnvironmentVariable($name,'Process') }
try {
 $env:PATH = "$env:WINDIR\System32"
 $env:PYTHONPATH = $null
 $env:PYTHONHOME = $null
 $env:PYTHONNOUSERSITE = '1'
 $env:AUTOREPORT_HOME = $freshHome
 $env:APPDATA = $freshHome
 $env:LOCALAPPDATA = $freshHome
 $env:STREAMLIT_SERVER_HEADLESS = 'true'
 $proc = Start-Process -FilePath $exe -WorkingDirectory $freshHome -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $testRoot 'stdout.log') -RedirectStandardError (Join-Path $testRoot 'stderr.log')
} finally {
 foreach ($name in $names) { [Environment]::SetEnvironmentVariable($name,$saved[$name],'Process') }
}
$record = [ordered]@{archive=$archivePath;sha256=(Get-FileHash -LiteralPath $archivePath -Algorithm SHA256).Hash;root=$testRoot;exe=$exe;pid=$proc.Id;freshWindows=$false;pythonInChildPath=$false;freshSettings=$true;health=$false}
try {
 for ($i=0;$i -lt 60;$i++) {
  try { $response=Invoke-WebRequest 'http://127.0.0.1:8501/_stcore/health' -TimeoutSec 1; if ($response.StatusCode -eq 200) {$record.health=$true;break} } catch {}
  Start-Sleep -Milliseconds 500
 }
} finally {
 $record | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $testRoot 'evidence.json') -Encoding utf8
 $record | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $repo 'build\first-use-latest.json') -Encoding utf8
}
if (!$record.health) {
 Get-Process | Where-Object {$_.Path -eq $exe} | Stop-Process
 throw 'Brak odpowiedzi serwera; zobacz logi w katalogu testu.'
}
# Po teście przeglądarkowym zakończ wyłącznie procesy o ścieżce exe z evidence.json.
$record | ConvertTo-Json
