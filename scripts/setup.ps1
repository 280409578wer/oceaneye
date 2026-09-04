$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$venvPython = Join-Path $projectRoot ".venv\Scripts\python.exe"
$projectPython = Join-Path $projectRoot ".python\python.exe"
$runtimePython = Join-Path $projectRoot "runtime\python\python.exe"
$appPython = $venvPython
$env:PYTHONPATH = $projectRoot

Write-Host ""
Write-Host "=== OceanEye V0.1 Setup ===" -ForegroundColor Cyan

if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "Node.js is missing. Install the LTS version from https://nodejs.org/ and run setup.bat again." -ForegroundColor Red
    exit 1
}

$pythonCommand = $null
$pythonArgs = @()
if (Test-Path -LiteralPath $runtimePython) {
    $appPython = $runtimePython
} elseif (-not (Test-Path -LiteralPath $venvPython)) {
    if (Test-Path -LiteralPath $projectPython) {
        $pythonCommand = $projectPython
    } elseif (Get-Command py -ErrorAction SilentlyContinue) {
        $pythonCommand = "py"
        $pythonArgs = @("-3")
    } elseif (Get-Command python -ErrorAction SilentlyContinue) {
        $pythonCommand = "python"
    } else {
        Write-Host "Python is missing. Install Python 3.11+ from https://www.python.org/downloads/windows/." -ForegroundColor Red
        Write-Host "Select Add python.exe to PATH, then run setup.bat again." -ForegroundColor Yellow
        exit 1
    }
}

Push-Location $projectRoot
try {
    if (-not (Test-Path -LiteralPath $venvPython)) {
        if (Test-Path -LiteralPath $runtimePython) {
            Write-Host "[1/4] Project Python runtime found and preserved."
        } else {
            Write-Host "[1/4] Creating the isolated Python environment..."
            & $pythonCommand @pythonArgs -m venv ".venv"
            $appPython = $venvPython
        }
    } else {
        Write-Host "[1/4] Existing Python environment found and preserved."
    }

    Write-Host "[2/4] Installing backend dependencies..."
    & $appPython -m pip install --disable-pip-version-check -r "backend\requirements.txt"
    if ($LASTEXITCODE -ne 0) { throw "Backend dependency installation failed." }

    Write-Host "[3/4] Installing frontend dependencies..."
    & npm install --prefix "frontend"
    if ($LASTEXITCODE -ne 0) { throw "Frontend dependency installation failed." }
    & npm run build --prefix "frontend"
    if ($LASTEXITCODE -ne 0) { throw "Frontend production build failed." }

    Write-Host "[4/4] Initializing SQLite and Mock data..."
    & $appPython -m backend.app.main
    if ($LASTEXITCODE -ne 0) { throw "Database initialization failed." }

    Write-Host ""
    Write-Host "OceanEye setup completed successfully." -ForegroundColor Green
} finally {
    Pop-Location
}
