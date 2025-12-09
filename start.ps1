#!/usr/bin/env pwsh

# Job Posting Aggregator - Quick Start Guide (Windows with WSL)

Write-Host "Job Posting Aggregator - Quick Start" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Check if WSL is available
if (-not (Get-Command wsl -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: WSL is not installed or not in PATH" -ForegroundColor Red
    exit 1
}

# Check if docker is available in WSL
$dockerCheck = wsl bash -c "command -v docker" 2>$null
if (-not $dockerCheck) {
    Write-Host "ERROR: Docker is not installed in WSL" -ForegroundColor Red
    exit 1
}

# Check if docker-compose is available in WSL
$dockerComposeCheck = wsl bash -c "command -v docker-compose" 2>$null
if (-not $dockerComposeCheck) {
    Write-Host "docker-compose not found in WSL, installing..." -ForegroundColor Yellow
    wsl bash -c "sudo curl -L `"https://github.com/docker/compose/releases/latest/download/docker-compose-`$(uname -s)-`$(uname -m)`" -o /usr/local/bin/docker-compose && sudo chmod +x /usr/local/bin/docker-compose"
    Write-Host "docker-compose installed" -ForegroundColor Green
}

# Change to script directory
Set-Location $PSScriptRoot

# Convert Windows path to WSL path
$wslPath = wsl wslpath -a $PSScriptRoot

Write-Host "Building Docker images..." -ForegroundColor Yellow
wsl bash -c "cd '$wslPath' && docker-compose build"

Write-Host ""
Write-Host "Starting services..." -ForegroundColor Yellow
wsl bash -c "cd '$wslPath' && docker-compose up -d"

Write-Host ""
Start-Sleep -Seconds 3

# Check backend
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
    Write-Host "✓ Backend running at http://localhost:8000" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Backend failed to start" -ForegroundColor Red
    Write-Host "Run 'docker-compose logs backend' to see errors" -ForegroundColor Yellow
    exit 1
}

# Check frontend
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5173" -UseBasicParsing -TimeoutSec 5 -ErrorAction SilentlyContinue
    Write-Host "✓ Frontend running at http://localhost:5173" -ForegroundColor Green
} catch {
    Write-Host "⚠ Frontend may take a moment to fully initialize" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Useful endpoints:" -ForegroundColor Cyan
Write-Host "  - Frontend: http://localhost:5173"
Write-Host "  - API: http://localhost:8000"
Write-Host "  - API Docs: http://localhost:8000/docs"
Write-Host "  - Health: http://localhost:8000/health"
Write-Host ""
Write-Host "To stop: docker-compose down" -ForegroundColor Yellow
Write-Host "To view logs: docker-compose logs -f [backend|frontend]" -ForegroundColor Yellow
