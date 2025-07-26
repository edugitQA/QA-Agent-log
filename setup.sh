#!/bin/bash

# Script de Configuração Automática do QA Log Agent
# Este script configura todo o ambiente necessário para a aula

set -e  # Para em caso de erro

echo "🚀 Iniciando configuração do QA Log Agent..."
echo "================================================"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para imprimir mensagens coloridas
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

# Verifica se Python está instalado
check_python() {
    print_status "Verificando instalação do Python..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_success "Python $PYTHON_VERSION encontrado"
        
        # Verifica se é versão 3.8+
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
            print_success "Versão do Python é compatível (3.8+)"
        else
            print_error "Python 3.8+ é necessário. Versão atual: $PYTHON_VERSION"
            exit 1
        fi
    else
        print_error "Python3 não encontrado. Por favor, instale Python 3.8+"
        exit 1
    fi
}

# Verifica se pip está instalado
check_pip() {
    print_status "Verificando instalação do pip..."
    
    if command -v pip3 &> /dev/null; then
        print_success "pip3 encontrado"
    else
        print_error "pip3 não encontrado. Instalando..."
        python3 -m ensurepip --upgrade
    fi
}

# Cria ambiente virtual
create_venv() {
    print_status "Criando ambiente virtual..."
    
    if [ -d "venv" ]; then
        print_warning "Ambiente virtual já existe. Removendo..."
        rm -rf venv
    fi
    
    python3 -m venv venv
    print_success "Ambiente virtual criado"
}

# Ativa ambiente virtual
activate_venv() {
    print_status "Ativando ambiente virtual..."
    
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        print_success "Ambiente virtual ativado"
    else
        print_error "Falha ao encontrar ambiente virtual"
        exit 1
    fi
}

# Instala dependências
install_dependencies() {
    print_status "Instalando dependências Python..."
    
    if [ -f "requirements.txt" ]; then
        pip install --upgrade pip
        pip install -r requirements.txt
        print_success "Dependências instaladas com sucesso"
    else
        print_error "Arquivo requirements.txt não encontrado"
        exit 1
    fi
}

# Configura arquivo .env
setup_env_file() {
    print_status "Configurando arquivo de ambiente..."
    
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_success "Arquivo .env criado a partir do exemplo"
            print_warning "IMPORTANTE: Configure suas chaves de API no arquivo .env"
            print_warning "Especialmente a OPENAI_API_KEY é obrigatória"
        else
            print_error "Arquivo .env.example não encontrado"
            exit 1
        fi
    else
        print_warning "Arquivo .env já existe. Mantendo configuração atual."
    fi
}

# Cria diretórios necessários
create_directories() {
    print_status "Criando diretórios necessários..."
    
    mkdir -p vectorstore
    mkdir -p output
    mkdir -p logs
    
    print_success "Diretórios criados"
}

# Testa instalação básica
test_installation() {
    print_status "Testando instalação..."
    
    # Testa imports básicos
    python3 -c "
import sys
try:
    import langchain
    import openai
    import chromadb
    import streamlit
    import pandas
    print('✅ Todas as dependências principais importadas com sucesso')
except ImportError as e:
    print(f'❌ Erro ao importar dependência: {e}')
    sys.exit(1)
"
    
    if [ $? -eq 0 ]; then
        print_success "Teste de instalação passou"
    else
        print_error "Teste de instalação falhou"
        exit 1
    fi
}

# Exibe instruções finais
show_final_instructions() {
    echo ""
    echo "================================================"
    echo -e "${GREEN}🎉 Configuração concluída com sucesso!${NC}"
    echo "================================================"
    echo ""
    echo -e "${BLUE}Próximos passos:${NC}"
    echo ""
    echo "1. Configure suas chaves de API no arquivo .env:"
    echo "   nano .env"
    echo ""
    echo "2. Para ativar o ambiente virtual:"
    echo "   source venv/bin/activate"
    echo ""
    echo "3. Para testar o agente:"
    echo "   python main.py analyze data/example.log"
    echo ""
    echo "4. Para iniciar a interface web:"
    echo "   streamlit run streamlit_app.py"
    echo ""
    echo -e "${YELLOW}IMPORTANTE:${NC}"
    echo "- Configure a OPENAI_API_KEY no arquivo .env"
    echo "- Para Slack: configure SLACK_TOKEN e SLACK_CHANNEL"
    echo "- Para Discord: configure DISCORD_WEBHOOK_URL"
    echo ""
    echo -e "${GREEN}Documentação completa: README.md${NC}"
}

# Função principal
main() {
    echo "Iniciando configuração automática..."
    echo "Este script irá:"
    echo "- Verificar Python e pip"
    echo "- Criar ambiente virtual"
    echo "- Instalar dependências"
    echo "- Configurar arquivos necessários"
    echo ""
    
    read -p "Continuar? (y/N): " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Configuração cancelada."
        exit 0
    fi
    
    check_python
    check_pip
    create_venv
    activate_venv
    install_dependencies
    setup_env_file
    create_directories
    test_installation
    show_final_instructions
}

# Executa função principal
main "$@"

