#!/usr/bin/env bash
# Sair em caso de erro
set -o errexit

echo "--- Iniciando Build ---"

# 1. Instalar dependências do Frontend e gerar build
echo "Instalando dependências do Node.js..."
pnpm install

echo "Gerando build do Frontend..."
pnpm build

# 2. Preparar diretório static do Flask
echo "Preparando arquivos estáticos para o Flask..."
mkdir -p backend/static
cp -rf dist/* backend/static/

# 3. Instalar dependências do Python
echo "Instalando dependências do Python..."
pip install -r requirements.txt

echo "--- Build Finalizado com Sucesso ---"
