$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$venvPython = Join-Path $projectRoot ".venv\Scripts\python.exe"
$runtimePython = Join-Path $projectRoot "runtime\python\python.exe"
$appPython = if (Test-Path -LiteralPath $venvPython) { $venvPython } else { $runtimePython }
$env:PYTHONPATH = $projectRoot
$nodeModules = Join-Path $projectRoot "frontend\node_modules"
$pidFile = Join-Path $projectRoot ".oceaneye-pids.json"

Write-Host ""
Write-Host "=== Starting OceanEye ===" -ForegroundColor Cyan

if (-not (Test-Path -LiteralPath $appPython) -or -not (Test-Path -LiteralPath $nodeModules)) {
    Write-Host "Setup is incomplete. Run setup.bat first." -ForegroundColor Red
    exit 1
}

foreach ($port in @(8000, 5173)) {
    $listener = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
    if ($listener) {
        Write-Host "Port $port is already in use. Close the program using it and try again." -ForegroundColor Red
        exit 1
    }
}

$backend = Start-Process -FilePath $appPython `
    -ArgumentList @("-m", "uvicorn", "backend.app.main:app", "--host", "127.0.0.1", "--port", "8000") `
    -WorkingDirectory $projectRoot -WindowStyle Hidden -PassThru

$frontend = Start-Process -FilePath $appPython `
    -ArgumentList @("-m", "backend.app.frontend_server") `
    -WorkingDirectory $projectRoot -WindowStyle Hidden -PassThru

@{ backend = $backend.Id; frontend = $frontend.Id } | ConvertTo-Json | Set-Content -LiteralPath $pidFile -Encoding UTF8

$ready = $false
for ($attempt = 0; $attempt -lt 30; $attempt++) {
    Start-Sleep -Milliseconds 500
    try {
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/health" -UseBasicParsing -TimeoutSec 2
        if ($response.StatusCode -eq 200) { $ready = $true; break }
    } catch { }
}

if (-not $ready) {
    Write-Host "Backend did not start within 15 seconds. Run stop.bat and try again." -ForegroundColor Red
    exit 1
}

Write-Host "OceanEye is ready: http://localhost:5173" -ForegroundColor Green
Write-Host "Data source: Mock demo data"
try {
    Start-Process "http://localhost:5173" -ErrorAction Stop
} catch {
    Write-Host "Browser could not be opened automatically. Open http://localhost:5173 manually." -ForegroundColor Yellow
}
