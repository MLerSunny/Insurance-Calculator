# PowerShell script to run the FastAPI backend server
Write-Host "Starting Insurance Calculator Backend API..." -ForegroundColor Green

# Navigate to the backend directory
Set-Location -Path .\backend

# Activate virtual environment if not already activated
if (-not (Test-Path env:VIRTUAL_ENV)) {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    if (Test-Path ..\.venv\Scripts\Activate.ps1) {
        & ..\.venv\Scripts\Activate.ps1
    } else {
        Write-Host "Virtual environment not found. Please create it first." -ForegroundColor Red
        exit 1
    }
}

# Run database health check
Write-Host "Checking database connection..." -ForegroundColor Yellow
python check_db.py

# Run the FastAPI application
Write-Host "Starting FastAPI server..." -ForegroundColor Green
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Return to the original directory when the server stops
Set-Location -Path .. 