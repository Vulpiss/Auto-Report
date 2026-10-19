param(
    [string]$Archive = (Join-Path $PSScriptRoot '..\release\AutoReport-v0.2.0-Windows.zip')
)
$ErrorActionPreference = 'Stop'
$zipPath = (Resolve-Path -LiteralPath $Archive).Path
$testRoot = Join-Path ([IO.Path]::GetTempPath()) ('AutoReport-test-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $testRoot | Out-Null
Expand-Archive -LiteralPath $zipPath -DestinationPath $testRoot
$exe = Get-ChildItem -LiteralPath $testRoot -Filter AutoReport.exe -Recurse | Select-Object -First 1
if (-not $exe) { throw 'AutoReport.exe not found in archive.' }
$outputPath = Join-Path $testRoot 'results'
$savedPath = $env:PATH
try {
    $env:PATH = Join-Path $env:SystemRoot 'System32'
    $process = Start-Process -FilePath $exe.FullName -ArgumentList @('--smoke-test', ('"' + $outputPath + '"')) -WorkingDirectory $testRoot -WindowStyle Hidden -PassThru
} finally {
    $env:PATH = $savedPath
}
if (-not $process.WaitForExit(45000)) {
    if (-not $process.HasExited) { $process.Kill() }
    throw 'Test timed out after 45 seconds.'
}
if ($process.ExitCode -ne 0) { throw ('EXE failed: ' + $process.ExitCode) }
$result = Get-Content -LiteralPath (Join-Path $outputPath 'smoke-result.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$summary = Get-Content -LiteralPath (Join-Path (Split-Path $result.output) 'summary.json') -Raw -Encoding UTF8 | ConvertFrom-Json
if ($summary.kpis.total_minor -ne 125000 -or $summary.kpis.rows_cnt -ne 7 -or $summary.comparison.change_pct.total_value -ne 25) {
    throw 'Report numbers are incorrect.'
}
$cpu = Get-CimInstance Win32_Processor | Select-Object Name,NumberOfLogicalProcessors
$system = Get-CimInstance Win32_OperatingSystem | Select-Object Caption,Version,OSArchitecture,TotalVisibleMemorySize
$evidence = [pscustomobject]@{
    Result='PASS'; Version=$result.version; CPU=$cpu; OS=$system
    ArchiveSHA256=(Get-FileHash -LiteralPath $zipPath -Algorithm SHA256).Hash
    PythonInChildPath=$false; FreshWindowsVerifiedByScript=$false
    Report=$result.output
    ManualNextStep='Open AutoReport.exe and prepare a second report without help.'
}
$evidence | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $testRoot 'test-result.json') -Encoding utf8
$evidence | Format-List
Write-Host ('Evidence saved to: ' + (Join-Path $testRoot 'test-result.json'))
