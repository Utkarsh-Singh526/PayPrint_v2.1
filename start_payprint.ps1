$ErrorActionPreference = "Stop"

$Project = "C:\Users\Fixit_Expert\Desktop\PayPrint_v2.1"
$LogDir = Join-Path $Project "logs"
$BackendPython = Join-Path $Project "venv\Scripts\python.exe"
$AgentPython = Join-Path $Project "print_agent\venv\Scripts\python.exe"
$ServerDir = Join-Path $Project "server"
$CustomerDir = Join-Path $Project "frontend\PayPrint_Customer_Frontend"
$AgentDir = Join-Path $Project "print_agent"

New-Item -ItemType Directory -Path $LogDir -Force | Out-Null

if (!(Test-Path $BackendPython)) { throw "Backend Python missing: $BackendPython" }
if (!(Test-Path $AgentPython)) { throw "Agent Python missing: $AgentPython" }

# Start backend only if port 8000 is not listening.
$BackendPort = Get-NetTCPConnection -State Listen -LocalPort 8000 -ErrorAction SilentlyContinue
if (!$BackendPort) {
    Start-Process -FilePath $BackendPython `
        -ArgumentList @("-u", "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000") `
        -WorkingDirectory $ServerDir `
        -RedirectStandardOutput (Join-Path $LogDir "backend-out.log") `
        -RedirectStandardError (Join-Path $LogDir "backend-error.log") `
        -WindowStyle Hidden
}

# Wait for backend readiness.
$Ready = $false
for ($i = 0; $i -lt 30; $i++) {
    try {
        Invoke-RestMethod "http://127.0.0.1:8000/health" -TimeoutSec 2 | Out-Null
        $Ready = $true
        break
    } catch {
        Start-Sleep -Seconds 2
    }
}
if (!$Ready) { throw "Backend not healthy. Check logs\backend-error.log" }

# Start customer frontend only if port 5502 is free.
$FrontendPort = Get-NetTCPConnection -State Listen -LocalPort 5502 -ErrorAction SilentlyContinue
if (!$FrontendPort) {
    Start-Process -FilePath $BackendPython `
        -ArgumentList @("-u", "-m", "http.server", "5502", "--bind", "127.0.0.1") `
        -WorkingDirectory $CustomerDir `
        -RedirectStandardOutput (Join-Path $LogDir "customer-out.log") `
        -RedirectStandardError (Join-Path $LogDir "customer-error.log") `
        -WindowStyle Hidden
}

Start-Sleep -Seconds 2

# Detect an existing agent by its exact virtual-environment executable.
$ExistingAgent = Get-CimInstance Win32_Process | Where-Object {
    $_.ExecutablePath -and
    $_.ExecutablePath -ieq $AgentPython -and
    $_.CommandLine -match 'app\.main'
}

if ($ExistingAgent) {
    Write-Host "Print Agent already running; skipping duplicate launch." -ForegroundColor Yellow
} else {
    Start-Process -FilePath $AgentPython `
        -ArgumentList @("-u", "-m", "app.main") `
        -WorkingDirectory $AgentDir `
        -RedirectStandardOutput (Join-Path $LogDir "agent-out.log") `
        -RedirectStandardError (Join-Path $LogDir "agent-error.log") `
        -WindowStyle Hidden

    Write-Host "Print Agent launch requested."
}

Write-Host "PayPrint startup sequence finished." -ForegroundColor Green
Write-Host "Customer page: http://127.0.0.1:5502/index.html"
Write-Host "Backend health: http://127.0.0.1:8000/health"
Write-Host "Logs: $LogDir"
