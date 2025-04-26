# PowerShell script to run the test suite for the backend
Write-Host "Running Insurance Calculator Backend Tests..." -ForegroundColor Green

# Activate virtual environment if not already activated
if (-not (Test-Path env:VIRTUAL_ENV)) {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    if (Test-Path .venv\Scripts\Activate.ps1) {
        & .venv\Scripts\Activate.ps1
    } elseif (Test-Path ..\.venv\Scripts\Activate.ps1) {
        & ..\.venv\Scripts\Activate.ps1
    } else {
        Write-Host "Virtual environment not found. Please create it first." -ForegroundColor Red
        exit 1
    }
}

# Install test dependencies if needed
Write-Host "Ensuring test dependencies are installed..." -ForegroundColor Yellow
pip install pytest pytest-cov

# Run tests with coverage
Write-Host "Running tests with coverage..." -ForegroundColor Green
python -m pytest tests/ -v --cov=app --cov-report=term --cov-report=html:test-coverage

# Check the test result
if ($LASTEXITCODE -eq 0) {
    Write-Host "`nAll tests passed successfully!" -ForegroundColor Green
    Write-Host "Coverage report has been generated in the test-coverage directory" -ForegroundColor Green
} else {
    Write-Host "`nSome tests failed. Please check the test output for details." -ForegroundColor Red
}

# Return exit code from pytest
exit $LASTEXITCODE 