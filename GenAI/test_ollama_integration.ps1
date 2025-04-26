# PowerShell script to test Ollama integration
Write-Host "Testing Ollama integration with DeepSeek-R1..." -ForegroundColor Green

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

# Check if Ollama is running
try {
    Write-Host "Checking if Ollama is running..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -Method GET -ErrorAction Stop | Out-Null
    Write-Host "Ollama is running and available!" -ForegroundColor Green
} catch {
    Write-Host "Error connecting to Ollama service. Make sure Ollama is running at http://localhost:11434" -ForegroundColor Red
    exit 1
}

# Run the Ollama test
Write-Host "Running Ollama test..." -ForegroundColor Yellow
python test_ollama.py

# Return to the original directory
Set-Location -Path .. 