param([Parameter(Mandatory=$true)][string]$DashboardExe)
$ErrorActionPreference = 'Stop'
$exe = (Resolve-Path -LiteralPath $DashboardExe).Path
Write-Host 'Uruchomienie lokalnego dashboardu. Zamknij konsolę aplikacji po zakończeniu próby.'
Start-Process -FilePath $exe -WorkingDirectory (Split-Path $exe) -WindowStyle Hidden
Write-Host 'Otwórz http://127.0.0.1:8501. Użyj protokołu docs/DASHBOARD_PILOT.md.'
