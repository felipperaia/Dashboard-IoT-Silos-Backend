#!/usr/bin/env bash
# Script helper (Linux / macOS)
# - atualiza pip/setuptools/wheel
# - instala dependências do requirements.txt
# - inicia uvicorn com reload
set -euo pipefail

echo "Ativando ambiente virtual (.venv) se existir..."
if [ -f ".venv/bin/activate" ]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
else
  echo "Aviso: .venv não encontrado. É recomendável criar um venv: python -m venv .venv"
fi

echo "Atualizando pip / setuptools / wheel..."
python -m pip install --upgrade pip setuptools wheel

echo "Instalando dependências do projeto (requirements.txt)..."
python -m pip install -r requirements.txt

echo "Iniciando uvicorn..."
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
