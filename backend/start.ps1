#!/usr/bin/env pwsh
Write-Host "Setting up virtual environment and installing dependencies..."

if (-not (Test-Path .\.venv)) {
    Write-Host "Creating virtual environment (.venv)..."
    python -m venv .venv
}
else {
    Write-Host "Virtual environment already exists."
}

Write-Host "Activating virtual environment..."
& .\.venv\Scripts\Activate.ps1

Write-Host "Upgrading pip..."
python -m pip install --upgrade pip

if (Test-Path .\requirements.txt) {
    Write-Host "Installing dependencies from requirements.txt..."
    python -m pip install -r .\requirements.txt
}
else {
    Write-Host "requirements.txt not found. Installing default dependencies..."
    python -m pip install Flask
    pip freeze > requirements.txt
    Write-Host "Generated requirements.txt with current environment packages."
}

Write-Host "Environment ready. To activate later use: .\\.venv\\Scripts\\Activate.ps1"
