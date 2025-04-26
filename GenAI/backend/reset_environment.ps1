# PowerShell script to reset Python environment with compatible packages
Write-Host "Resetting Python environment with compatible package versions..." -ForegroundColor Green

# Uninstall problematic packages
Write-Host "Uninstalling conflicting packages..." -ForegroundColor Yellow
python -m pip uninstall -y langchain langchain-core langchain-community langchain-ollama langchain-text-splitters 

# Install packages from the fixed requirements file
Write-Host "Installing compatible packages..." -ForegroundColor Yellow
python -m pip install -r requirements.fixed.txt

# Display installed versions
Write-Host "Installed package versions:" -ForegroundColor Green
python -m pip list | Select-String -Pattern "langchain|ollama|tenacity|instructor"

Write-Host "Environment reset complete. You can now run 'python -m uvicorn main:app --reload'" -ForegroundColor Green 