# Windows PowerShell equivalent of setup.sh
Set-Location $PSScriptRoot
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
pytest tests/ -q
Write-Host "`nSetup complete. Activate with:  .\.venv\Scripts\Activate.ps1"
Write-Host "Web app:                        streamlit run webapp/app.py"
