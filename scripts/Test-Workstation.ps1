# Windows PowerShell 5.1+, no Python or additional modules required.
[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$Archive,
    [Parameter(Mandatory=$true)][ValidatePattern('^[0-9a-fA-F]{64}$')][string]$ExpectedZipSHA256,
    [string]$EvidenceRoot
)
$ErrorActionPreference = 'Stop'
function Get-TaskSHA256([string]$LiteralPath) {
    $taskHasher = [Security.Cryptography.SHA256]::Create()
    $taskStream = [IO.File]::OpenRead($LiteralPath)
    try {
        return ([BitConverter]::ToString($taskHasher.ComputeHash($taskStream))).Replace('-','').ToLowerInvariant()
    } finally { $taskStream.Dispose(); $taskHasher.Dispose() }
}
if (-not $EvidenceRoot) {
    $EvidenceRoot = Join-Path $env:TEMP ('AutoReport-workstation-' + [guid]::NewGuid().ToString('N'))
}
$taskRoot = [IO.Path]::GetFullPath($EvidenceRoot)
if (Test-Path -LiteralPath $taskRoot) { throw 'EvidenceRoot already exists. Choose a new directory.' }
New-Item -ItemType Directory -Path $taskRoot | Out-Null
$taskRecord = [ordered]@{
    started_at = (Get-Date).ToString('o'); result = 'FAIL'; sessions = @()
    scope = 'Owned EXE server only; two starts with isolated settings and no Python in PATH'
    clean_windows = 'UNKNOWN'; native_launcher = 'UNKNOWN'
    user_independence = 'UNKNOWN'; profile_recall_in_ui = 'UNKNOWN'
}
try {
    $taskArchive = (Resolve-Path -LiteralPath $Archive).Path
    $taskHash = Get-TaskSHA256 $taskArchive
    $taskRecord.archive_sha256 = $taskHash
    if ($taskHash -ne $ExpectedZipSHA256.ToLowerInvariant()) { throw 'ZIP SHA256 differs from the expected release.' }
    $taskOs = Get-CimInstance Win32_OperatingSystem
    $taskComputer = Get-CimInstance Win32_ComputerSystem
    $taskRecord.windows = [ordered]@{caption=$taskOs.Caption; version=$taskOs.Version; architecture=$taskOs.OSArchitecture; memory_bytes=$taskComputer.TotalPhysicalMemory}
    # The non-ASCII path and spaces are intentional portability checks.
    $taskUnpack = Join-Path $taskRoot (([char]0x015A).ToString() + 'wieza paczka ze spacjami')
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $taskZip = [IO.Compression.ZipFile]::OpenRead($taskArchive)
    try {
        $taskPrefix = [IO.Path]::GetFullPath($taskUnpack) + [IO.Path]::DirectorySeparatorChar
        foreach ($taskEntry in $taskZip.Entries) {
            $taskDestination = [IO.Path]::GetFullPath((Join-Path $taskUnpack $taskEntry.FullName))
            if (-not $taskDestination.StartsWith($taskPrefix, [StringComparison]::OrdinalIgnoreCase)) {
                throw 'ZIP contains a path outside the extraction directory.'
            }
        }
    } finally { $taskZip.Dispose() }
    [IO.Compression.ZipFile]::ExtractToDirectory($taskArchive, $taskUnpack)
    $taskPackage = Join-Path $taskUnpack 'AutoReportAnalyst'
    $taskExe = Join-Path $taskPackage 'AutoReportAnalyst.exe'
    $taskManifest = Get-Content -LiteralPath (Join-Path $taskPackage 'RELEASE.json') -Raw -Encoding UTF8 | ConvertFrom-Json
    $taskExeHash = Get-TaskSHA256 $taskExe
    if ($taskExeHash -ne $taskManifest.exe_sha256) { throw 'EXE does not match RELEASE.json.' }
    $taskRecord.exe_sha256 = $taskExeHash
    $taskProfiles = Join-Path $taskRoot 'isolated-profiles'
    $taskLocal = Join-Path $taskRoot 'isolated-user'
    $taskTemp = Join-Path $taskRoot 'temporary-files'
    foreach ($taskFolder in @($taskProfiles,$taskLocal,$taskTemp)) { New-Item -ItemType Directory -Path $taskFolder | Out-Null }
    for ($taskSession=1; $taskSession -le 2; $taskSession++) {
        $taskListener = [Net.Sockets.TcpListener]::new([Net.IPAddress]::Loopback,0)
        $taskListener.Start()
        $taskPort = $taskListener.LocalEndpoint.Port
        $taskListener.Stop()
        $taskSessionDir = Join-Path $taskRoot ('session-' + $taskSession)
        New-Item -ItemType Directory -Path $taskSessionDir | Out-Null
        $taskLog = Join-Path $taskSessionDir 'server.log'
        $taskChild = $null
        $taskSessionRecord = [ordered]@{number=$taskSession;port=$taskPort;health=$false;stopped=$false;python_in_path=$false}
        try {
            $taskChanges = @{
                PATH=($env:SystemRoot + ';' + (Join-Path $env:SystemRoot 'System32'))
                PYTHONPATH=$null; PYTHONHOME=$null; PYTHONNOUSERSITE='1'
                AUTOREPORT_PROFILE_DIR=$taskProfiles; APPDATA=$taskLocal; LOCALAPPDATA=$taskLocal
                TEMP=$taskTemp; TMP=$taskTemp
            }
            $taskSaved = @{}
            try {
                foreach ($taskName in $taskChanges.Keys) {
                    $taskSaved[$taskName] = [Environment]::GetEnvironmentVariable($taskName,'Process')
                    [Environment]::SetEnvironmentVariable($taskName,$taskChanges[$taskName],'Process')
                }
                $taskChild = Start-Process -FilePath $taskExe -ArgumentList @('--serve', $taskPort, '--log', ('"' + $taskLog + '"')) -WorkingDirectory $taskSessionDir -WindowStyle Hidden -PassThru
            } finally {
                foreach ($taskName in $taskSaved.Keys) { [Environment]::SetEnvironmentVariable($taskName,$taskSaved[$taskName],'Process') }
            }
            for ($taskAttempt=0; $taskAttempt -lt 60; $taskAttempt++) {
                if ($taskChild.HasExited) { throw ('EXE exited early. See ' + $taskLog) }
                try {
                    $taskResponse = Invoke-WebRequest ('http://127.0.0.1:' + $taskPort + '/_stcore/health') -UseBasicParsing -TimeoutSec 1
                    if ($taskResponse.StatusCode -eq 200 -and $taskResponse.Content.Trim() -eq 'ok') { $taskSessionRecord.health=$true; break }
                } catch {}
                Start-Sleep -Milliseconds 500
            }
            if (-not $taskSessionRecord.health) { throw ('Server timeout. See ' + $taskLog) }
        } finally {
            if ($null -ne $taskChild) {
                if (-not $taskChild.HasExited) { Stop-Process -Id $taskChild.Id -ErrorAction Stop }
                $taskSessionRecord.stopped = $taskChild.WaitForExit(10000)
            }
            $taskRecord.sessions += $taskSessionRecord
        }
        if (-not $taskSessionRecord.stopped) { throw 'Owned EXE did not stop.' }
    }
    $taskRecord.result = 'PASS_SERVER_RESTART'
} catch {
    $taskRecord.error = $_.Exception.Message
    throw
} finally {
    $taskRecord.finished_at = (Get-Date).ToString('o')
    $taskRecord | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $taskRoot 'evidence.json') -Encoding UTF8
    Write-Host ('Evidence: ' + (Join-Path $taskRoot 'evidence.json'))
}
$taskRecord | ConvertTo-Json -Depth 8
