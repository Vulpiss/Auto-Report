param([Parameter(Mandatory=$true)][string]$AnalystExe)
$ErrorActionPreference = 'Stop'
$exe = (Resolve-Path -LiteralPath $AnalystExe).Path
if (Get-NetTCPConnection -State Listen -LocalPort 8501 -ErrorAction SilentlyContinue) {
    throw 'Port 8501 jest zajęty. Zakończ poprzedni dashboard i uruchom test ponownie.'
}
$record = [ordered]@{ date=(Get-Date).ToString('o'); exeSha256=(Get-FileHash -LiteralPath $exe -Algorithm SHA256).Hash; windows=[Environment]::OSVersion.VersionString; health=$false; manualResult='UNKNOWN' }
$process = Start-Process -FilePath $exe -ArgumentList @('--serve','8501') -WorkingDirectory (Split-Path $exe) -WindowStyle Hidden -PassThru
try {
    for ($attempt=0; $attempt -lt 30; $attempt++) {
        try { $r=Invoke-WebRequest 'http://127.0.0.1:8501/_stcore/health' -UseBasicParsing -TimeoutSec 2; if($r.StatusCode -eq 200){$record.health=$true; break} } catch {}
        Start-Sleep -Seconds 1
    }
    if (-not $record.health) { throw 'Serwer nie odpowiedział w czasie testu.' }
    Write-Host 'Otwórz http://127.0.0.1:8501 i sprawdź prosty tryb według START_HERE.txt. Ten test uruchamia serwer, nie okno startowe.'
    Write-Host 'Następnie wybierz tryb Zaawansowany i wykonaj zadania z ANALYST_ACCEPTANCE.md.'
    Write-Host 'Sprawdź demo, eksport PDF oraz 1 i 3 slajdy w PowerPoint. Test nie zastępuje pilota klienta.'
    $record.manualResult=Read-Host 'Wpisz wynik próby i napotkane błędy (bez danych klienta)'
} finally {
    if (-not $process.HasExited) { Stop-Process -Id $process.Id -ErrorAction SilentlyContinue }
    $report=Join-Path (Get-Location) ('analyst-check-'+(Get-Date -Format 'yyyyMMdd-HHmmss')+'.json')
    $record | ConvertTo-Json | Set-Content -LiteralPath $report -Encoding UTF8
    Write-Host "Zapisano wynik: $report"
}
