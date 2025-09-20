<#
  run_dev.ps1
  PowerShell helper para desenvolvimento no Windows:
  - Ativa venv (se existir)
  - Atualiza pip/setuptools/wheel
  - Instala requirements
  - Inicia uvicorn
#>
param()

Write-Host "Verificando virtualenv (.venv)..."
if (Test-Path -Path ".\.venv\Scripts\Activate.ps1") {
  Write-Host "Ativando .venv..."
  . .\.venv\Scripts\Activate.ps1
} else {
  Write-Host "Aviso: .venv não encontrado. Crie-o: python -m venv .venv"
}

Write-Host "Atualizando pip / setuptools / wheel..."
python -m pip install --upgrade pip setuptools wheel

Write-Host "Instalando dependências do projeto..."
python -m pip install -r requirements.txt

Write-Host "Iniciando uvicorn..."
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
