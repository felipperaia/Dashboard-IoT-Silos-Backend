<#
  run_dev.ps1
  Helper Windows para desenvolvimento do backend:
  - valida ambiente Python (versão compatível)
  - detecta shadowing de stdlib (ex.: importlib.py)
  - instala dependências (exclui scikit-learn)
  - inicia uvicorn
#>
param()

function Abort([string]$msg) {
  Write-Host ""
  Write-Host "ERROR: $msg" -ForegroundColor Red
  Write-Host ""
  Exit 1
}

# Ajuste: determinar o diretório do script e garantir que todas as operações usem esse diretório
$scriptDir = Split-Path -Path $MyInvocation.MyCommand.Definition -Parent
if (-not $scriptDir) { $scriptDir = (Get-Location).ProviderPath }

# localizar venv preferencialmente dentro do backend; fallback para venv na raiz do projeto
$backendVenv = Join-Path $scriptDir ".venv"
$rootVenv = Join-Path (Split-Path $scriptDir -Parent) ".venv"
$venvToUse = $null
if (Test-Path $backendVenv) {
  $venvToUse = $backendVenv
} elseif (Test-Path $rootVenv) {
  $venvToUse = $rootVenv
}

if ($venvToUse) {
  Write-Host "Usando virtualenv em: $venvToUse"
  $activateScript = Join-Path $venvToUse "Scripts\Activate.ps1"
  if (Test-Path $activateScript) {
    Write-Host "Ativando venv: $activateScript"
    . $activateScript
  } else {
    Abort "Ativador do venv não encontrado em $activateScript"
  }
} else {
  Write-Host "Nenhum .venv encontrado automaticamente. Execute: python -m venv .venv (no backend) e ative-o antes de rodar este script."
}

Set-Location $scriptDir

Write-Host "Verificando versão do Python..."
try {
  $pyver = & python -c "import sys; print('%d.%d' % sys.version_info[:2])"
} catch {
  Abort "Python não encontrado no PATH. Instale Python 3.11 e recrie o venv."
}
if (-not $pyver) { Abort "Erro ao obter versão do Python." }

Write-Host "Python detectado: $pyver"
# interpretar versão
$parts = $pyver.Split('.')
[int]$maj = $parts[0]
[int]$min = $parts[1]

# Rejeitar ambientes problemáticos (ex.: Python 3.13+)
if ($maj -gt 3 -or ($maj -eq 3 -and $min -ge 13)) {
  Write-Host ""
  Write-Host "Atenção: Python $pyver pode ser incompatível com FastAPI/Pydantic/scikit-build neste projeto." -ForegroundColor Yellow
  Write-Host "Recomenda-se usar Python 3.11 ou 3.10 (ou crie um env conda: conda create -n silo python=3.11)" -ForegroundColor Yellow
  Write-Host "Abortando para evitar erros de import (ForwardRef._evaluate etc.)."
  Exit 1
}

Write-Host "Procurando arquivos que possam sobrescrever módulos da stdlib (ex.: importlib.py)..."
# usar $scriptDir como raiz da verificação
$root = $scriptDir
$conflicts = Get-ChildItem -Path $root -Recurse -Force -File -ErrorAction SilentlyContinue | Where-Object {
  $_.Name -match '^importlib(\.py|$)' -or $_.Name -eq 'pkgutil.py' -or $_.Name -eq 'typing.py'
}
if ($conflicts) {
  Write-Host ""
  Write-Host "Foram encontrados arquivos que podem causar shadowing da stdlib (importlib/pkt):" -ForegroundColor Yellow
  $conflicts | ForEach-Object { Write-Host " - $($_.FullName)" }
  Write-Host ""
  Write-Host "Renomeie / mova esses arquivos (ex.: importlib.py -> importlib_local.py) e tente novamente." -ForegroundColor Yellow
  Exit 1
}

Write-Host "Atualizando pip / setuptools / wheel..."
python -m pip install --upgrade pip setuptools wheel

# Criar arquivo temporário de requirements sem scikit-learn (usar caminho absoluto no backend)
$tempReq = Join-Path $scriptDir "requirements.tmp.txt"
$reqPath = Join-Path $scriptDir "requirements.txt"
if (Test-Path $reqPath) {
  Get-Content $reqPath | Where-Object { $_ -notmatch '^\s*#' -and $_ -notmatch 'scikit-learn' } | Set-Content $tempReq
  Write-Host "Instalando dependências (sem scikit-learn) a partir de $tempReq ..."
  try {
    python -m pip install -r $tempReq
  } catch {
    Write-Host "Aviso: pip install retornou erro. Verifique o log acima; você pode instalar pacotes faltantes manualmente." -ForegroundColor Yellow
  }
  Remove-Item $tempReq -ErrorAction SilentlyContinue
} else {
  Abort "requirements.txt não encontrado no diretório do backend ($scriptDir). Verifique se os arquivos foram movidos."
}

# Verificar uvicorn instalado
Write-Host "Verificando uvicorn..."
python -c "import importlib,sys; sys.exit(0 if importlib.util.find_spec('uvicorn') else 2)"
if ($LASTEXITCODE -ne 0) {
  Write-Host "uvicorn não encontrado no venv. Tentando instalar..."
  try { python -m pip install 'uvicorn[standard]==0.22.0' } catch { Abort "Falha instalando uvicorn; instale manualmente." }
}

Write-Host "Iniciando uvicorn (app.main:app)..."
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
