# ─────────────────────────────────────────────────────────────────────────────
#  AcadEval+ — One-command Dev Startup Script
#  Usage:  .\start.ps1
# ─────────────────────────────────────────────────────────────────────────────

$ErrorActionPreference = "Continue"
$Root    = Split-Path -Parent $MyInvocation.MyCommand.Path
$Backend = Join-Path $Root "backend"

Write-Host ""
Write-Host "  +--------------------------------------+" -ForegroundColor Cyan
Write-Host "  |   AcadEval+  --  Starting Dev Stack  |" -ForegroundColor Cyan
Write-Host "  +--------------------------------------+" -ForegroundColor Cyan
Write-Host ""

# ── Step 1: Docker services ───────────────────────────────────────────────────
Write-Host "  [1/5] Starting Docker services (Neo4j + Redis + GROBID)..." -ForegroundColor Yellow
try {
    docker compose -f "$Root\docker-compose.yml" up -d
    Write-Host "        [OK] Docker services up" -ForegroundColor Green
} catch {
    Write-Host "        [WARN] Docker error -- continuing..." -ForegroundColor Red
}

# Wait for Redis to be ready (Celery worker needs it)
Write-Host "  [1/5] Waiting for Redis..." -ForegroundColor Yellow
$redisReady = $false
for ($i = 0; $i -lt 10; $i++) {
    $ping = docker exec acadeval_redis redis-cli ping 2>$null
    if ($ping -match "PONG") {
        $redisReady = $true
        break
    }
    Start-Sleep -Seconds 1
}
if ($redisReady) {
    Write-Host "        [OK] Redis ready" -ForegroundColor Green
} else {
    Write-Host "        [WARN] Redis starting in background" -ForegroundColor DarkYellow
}

# ── Step 2: FastAPI backend ───────────────────────────────────────────────────
Write-Host "  [2/5] Starting FastAPI backend (port 8000)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$Backend'; if (Test-Path 'venv\Scripts\activate.ps1') { .\venv\Scripts\activate }; `$host.UI.RawUI.WindowTitle = 'AcadEval Backend'; uvicorn app.main:app --reload --port 8000"
Write-Host "        [OK] Backend window launched" -ForegroundColor Green

Start-Sleep -Seconds 2

# ── Step 3: Celery worker ─────────────────────────────────────────────────────
Write-Host "  [3/5] Starting Celery worker..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$Backend'; if (Test-Path 'venv\Scripts\activate.ps1') { .\venv\Scripts\activate }; `$host.UI.RawUI.WindowTitle = 'AcadEval Celery Worker'; celery -A app.worker worker --loglevel=info --queues=pipeline,periodic --concurrency=2"
Write-Host "        [OK] Celery worker window launched" -ForegroundColor Green

# ── Step 4: Celery beat ───────────────────────────────────────────────────────
Write-Host "  [4/5] Starting Celery beat scheduler..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$Backend'; if (Test-Path 'venv\Scripts\activate.ps1') { .\venv\Scripts\activate }; `$host.UI.RawUI.WindowTitle = 'AcadEval Celery Beat'; celery -A app.worker beat --loglevel=info"
Write-Host "        [OK] Celery beat window launched" -ForegroundColor Green

# ── Step 5: Vite frontend ─────────────────────────────────────────────────────
Write-Host "  [5/5] Starting Vite frontend (port 5173)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$Root'; `$host.UI.RawUI.WindowTitle = 'AcadEval Frontend'; npm run dev"
Write-Host "        [OK] Frontend window launched" -ForegroundColor Green

# ── Summary ───────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "  ==========================================================" -ForegroundColor Cyan
Write-Host "  All services started! URLs:" -ForegroundColor Cyan
Write-Host "    Frontend   ->  http://localhost:5173" -ForegroundColor Cyan
Write-Host "    Backend    ->  http://localhost:8000" -ForegroundColor Cyan
Write-Host "    API Docs   ->  http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "    Neo4j UI   ->  http://localhost:7474" -ForegroundColor Cyan
Write-Host "  ==========================================================" -ForegroundColor Cyan
Write-Host ""
