$ErrorActionPreference = "Continue"
$projectRoot = Split-Path -Parent $PSScriptRoot
$pidFile = Join-Path $projectRoot ".oceaneye-pids.json"

if (-not (Test-Path -LiteralPath $pidFile)) {
    Write-Host "No OceanEye process record was found. It may already be stopped." -ForegroundColor Yellow
    exit 0
}

$processIds = Get-Content -LiteralPath $pidFile -Raw | ConvertFrom-Json
foreach ($processId in @($processIds.backend, $processIds.frontend)) {
    if ($processId) {
        Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
        Get-CimInstance Win32_Process -Filter "ParentProcessId=$processId" -ErrorAction SilentlyContinue | ForEach-Object {
            Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
        }
    }
}
Remove-Item -LiteralPath $pidFile -Force -ErrorAction SilentlyContinue
Write-Host "OceanEye stopped. SQLite data was preserved." -ForegroundColor Green
