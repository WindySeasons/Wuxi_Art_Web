#!/usr/bin/env pwsh
if (-not (Test-Path .\.venv)) {
    Write-Host "Virtual environment not found. Please execute start.ps1 first."
    exit 1
}

Write-Host "Activating virtual environment..."
& .\.venv\Scripts\Activate.ps1

Write-Host "Launching Flask backend..."
python .\app.py
