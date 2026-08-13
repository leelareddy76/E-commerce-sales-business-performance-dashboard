# Run precompute, start backend and Streamlit in new PowerShell windows
# Usage: Right-click -> Run with PowerShell, or from an elevated/regular PowerShell run: .\scripts\run_local.ps1

$venvPython = Join-Path -Path $PSScriptRoot -ChildPath "..\.venv\Scripts\python.exe"
$venvPython = (Resolve-Path $venvPython).Path

Write-Host "Running precompute..."
& $venvPython (Join-Path $PSScriptRoot '..\scripts\precompute.py')

Write-Host "Starting backend (uvicorn) in a new PowerShell window..."
# Limit reload to project source directories to avoid watching site-packages (which triggers frequent reloads)
Start-Process powershell -ArgumentList "-NoExit","-Command","& '$venvPython' -m uvicorn app.backend:app --reload --reload-dir app --reload-dir scripts"

Start-Sleep -Seconds 2

Write-Host "Starting Streamlit app in a new PowerShell window..."
Start-Process powershell -ArgumentList "-NoExit","-Command","& '$venvPython' -m streamlit run app/streamlit_app.py"

Write-Host "All processes started. Close the new windows to stop the services."