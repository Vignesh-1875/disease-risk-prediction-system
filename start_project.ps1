$ErrorActionPreference = "Stop"
$project = Split-Path -Parent $MyInvocation.MyCommand.Path
$python = Join-Path (Split-Path -Parent $project) ".venv\Scripts\python.exe"
$backend = Join-Path $project "backend"
$frontend = Join-Path $project "frontend"

if (-not (Test-Path $python)) {
    Write-Host "Python environment not found at $python" -ForegroundColor Red
    Write-Host "Install Python 3.10+ or update the python path in this script."
    Read-Host "Press Enter to close"
    exit 1
}

Write-Host "Starting Heart Disease Risk Prediction System..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$backend'; & '$python' run.py"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$project'; & '$python' -m http.server 5500 --directory '$frontend'"

$backendReady = $false
for ($attempt = 1; $attempt -le 20; $attempt++) {
    Start-Sleep -Milliseconds 500
    try {
        $response = Invoke-WebRequest -UseBasicParsing "http://127.0.0.1:5000/api/health"
        if ($response.StatusCode -eq 200) {
            $backendReady = $true
            break
        }
    } catch {
    }
}
if (-not $backendReady) {
    Write-Host "Backend did not start. Check the backend PowerShell window for the error." -ForegroundColor Red
    Read-Host "Press Enter to close"
    exit 1
}

Start-Process "http://127.0.0.1:5500"
Write-Host "Frontend: http://127.0.0.1:5500" -ForegroundColor Green
Write-Host "Backend:  http://127.0.0.1:5000/api/health" -ForegroundColor Green
Write-Host "Close the two new terminal windows to stop the project."
