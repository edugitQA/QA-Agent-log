#!/bin/bash

# Script de Reset/Limpeza do Ambiente QA Log Agent
# Use este script para limpar e resetar o ambiente em caso de problemas

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo "🔄 Script de Reset do Ambiente QA Log Agent"
echo "=========================================="
echo ""
echo "Este script irá:"
echo "- Remover ambiente virtual existente"
echo "- Limpar banco vetorial"
echo "- Limpar arquivos de output"
echo "- Manter configurações (.env)"
echo ""

read -p "Tem certeza que deseja continuar? (y/N): " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Reset cancelado."
    exit 0
fi

# Remove ambiente virtual
if [ -d "venv" ]; then
    print_status "Removendo ambiente virtual..."
    rm -rf venv
    print_success "Ambiente virtual removido"
else
    print_warning "Ambiente virtual não encontrado"
fi

# Limpa banco vetorial
if [ -d "vectorstore" ]; then
    print_status "Limpando banco vetorial..."
    rm -rf vectorstore/*
    print_success "Banco vetorial limpo"
else
    print_warning "Diretório vectorstore não encontrado"
fi

# Limpa outputs
if [ -d "output" ]; then
    print_status "Limpando arquivos de output..."
    rm -rf output/*
    print_success "Arquivos de output removidos"
else
    print_warning "Diretório output não encontrado"
fi

# Limpa logs
if [ -d "logs" ]; then
    print_status "Limpando logs do sistema..."
    rm -rf logs/*
    print_success "Logs do sistema removidos"
else
    print_warning "Diretório logs não encontrado"
fi

# Remove arquivos temporários
print_status "Removendo arquivos temporários..."
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.log" -not -path "./data/*" -delete 2>/dev/null || true
find . -name "temp_*" -delete 2>/dev/null || true
print_success "Arquivos temporários removidos"

# Recria diretórios necessários
print_status "Recriando estrutura de diretórios..."
mkdir -p vectorstore
mkdir -p output  
mkdir -p logs
print_success "Diretórios recriados"

echo ""
echo "=" * 50
print_success "Reset do ambiente concluído!"
echo "=" * 50
echo ""
echo "Próximos passos:"
echo "1. Execute: ./setup.sh"
echo "2. Configure suas APIs no .env"
echo "3. Teste: python test_environment.py"
echo ""
print_warning "Nota: Suas configurações em .env foram preservadas"

