# 📋 Instruções de Configuração - QA Log Agent

## 🎯 Visão Geral

Este documento fornece instruções passo a passo para configurar o ambiente do QA Log Agent para a aula prática. Siga estas instruções cuidadosamente para garantir que tudo funcione corretamente durante a demonstração.

## 🔧 Pré-requisitos

### Sistema Operacional
- **Linux/macOS**: Recomendado
- **Windows**: Compatível (use WSL2 ou PowerShell)

### Software Necessário
- **Python 3.8+**: Obrigatório
- **pip**: Gerenciador de pacotes Python
- **Git**: Para controle de versão (opcional)
- **Navegador Web**: Para interface Streamlit

### Contas e APIs
- **OpenAI API Key**: Obrigatória para funcionamento do agente
- **Slack Bot Token**: Opcional para integração
- **Discord Webhook**: Opcional para notificações

## 🚀 Configuração Automática (Recomendada)

### Passo 1: Download do Projeto
```bash
# Se usando Git
git clone <repository-url>
cd qa-log-agent

# Ou extraia o arquivo ZIP fornecido
unzip qa-log-agent.zip
cd qa-log-agent
```

### Passo 2: Execução do Script de Setup
```bash
# Torna o script executável
chmod +x setup.sh

# Executa configuração automática
./setup.sh
```

O script irá:
- ✅ Verificar Python e pip
- ✅ Criar ambiente virtual
- ✅ Instalar dependências
- ✅ Configurar estrutura de arquivos
- ✅ Criar arquivo .env

### Passo 3: Configuração da API Key
```bash
# Edite o arquivo .env
nano .env

# Configure pelo menos:
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### Passo 4: Teste do Ambiente
```bash
# Ativa ambiente virtual
source venv/bin/activate

# Executa teste completo
python test_environment.py
```

## 🔧 Configuração Manual (Alternativa)

### Passo 1: Ambiente Virtual
```bash
# Cria ambiente virtual
python3 -m venv venv

# Ativa ambiente virtual
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

### Passo 2: Instalação de Dependências
```bash
# Atualiza pip
pip install --upgrade pip

# Instala dependências
pip install -r requirements.txt
```

### Passo 3: Configuração de Ambiente
```bash
# Copia arquivo de exemplo
cp .env.example .env

# Cria diretórios necessários
mkdir -p vectorstore output logs
```

### Passo 4: Configuração do .env
Edite o arquivo `.env` com suas configurações:

```env
# OBRIGATÓRIO
OPENAI_API_KEY=sk-your-openai-api-key-here

# OPCIONAL - Slack
SLACK_TOKEN=xoxb-your-slack-bot-token
SLACK_CHANNEL=#qa-alerts

# OPCIONAL - Discord  
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/your-webhook

# CONFIGURAÇÕES
LOG_DIRECTORY=./data
VECTORSTORE_PATH=./vectorstore
OUTPUT_PATH=./output
```

## 🔑 Configuração de APIs

### OpenAI API Key (Obrigatória)

1. **Acesse**: https://platform.openai.com/api-keys
2. **Crie** uma nova API key
3. **Copie** a chave (começa com `sk-`)
4. **Configure** no arquivo `.env`:
   ```env
   OPENAI_API_KEY=sk-your-actual-key-here
   ```

### Slack Integration (Opcional)

1. **Acesse**: https://api.slack.com/apps
2. **Crie** um novo app
3. **Configure** Bot Token Scopes:
   - `chat:write`
   - `channels:read`
4. **Instale** o app no workspace
5. **Copie** o Bot User OAuth Token
6. **Configure** no `.env`:
   ```env
   SLACK_TOKEN=xoxb-your-bot-token
   SLACK_CHANNEL=#qa-alerts
   ```

### Discord Webhook (Opcional)

1. **Acesse** configurações do canal Discord
2. **Crie** um webhook
3. **Copie** a URL do webhook
4. **Configure** no `.env`:
   ```env
   DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/your-webhook
   ```

## 🧪 Verificação da Instalação

### Teste Rápido
```bash
# Ativa ambiente virtual
source venv/bin/activate

# Testa análise básica
python main.py analyze data/example.log
```

### Teste Completo
```bash
# Executa todos os testes
python test_environment.py
```

### Teste da Interface Web
```bash
# Inicia Streamlit
streamlit run streamlit_app.py

# Acesse: http://localhost:8501
```

## 🐛 Solução de Problemas

### Erro: "OPENAI_API_KEY não encontrada"
```bash
# Verifique se o arquivo .env existe
ls -la .env

# Verifique o conteúdo
cat .env

# Certifique-se de que não há espaços extras
OPENAI_API_KEY=sk-key-here  # ❌ Espaço no final
OPENAI_API_KEY=sk-key-here  # ✅ Correto
```

### Erro: "ModuleNotFoundError"
```bash
# Verifique se o ambiente virtual está ativo
which python  # Deve mostrar caminho do venv

# Reinstale dependências
pip install -r requirements.txt

# Verifique instalação
pip list | grep langchain
```

### Erro: "Permission denied"
```bash
# Torna scripts executáveis
chmod +x setup.sh
chmod +x test_environment.py

# Ou execute com python diretamente
python test_environment.py
```

### Erro: "ChromaDB initialization failed"
```bash
# Limpa diretório do banco vetorial
rm -rf vectorstore

# Cria novamente
mkdir vectorstore

# Testa novamente
python test_environment.py
```

### Erro: "Streamlit command not found"
```bash
# Verifica se Streamlit está instalado
pip show streamlit

# Reinstala se necessário
pip install streamlit

# Executa diretamente
python -m streamlit run streamlit_app.py
```

## 📚 Estrutura de Arquivos Final

Após a configuração, você deve ter:

```
qa-log-agent/
├── 📄 main.py                 # Script principal
├── 📄 streamlit_app.py        # Interface web
├── 📄 requirements.txt        # Dependências
├── 📄 .env                    # Configurações (criado)
├── 📄 .env.example           # Exemplo de configuração
├── 📄 setup.sh               # Script de instalação
├── 📄 test_environment.py    # Teste do ambiente
├── 📄 README.md              # Documentação
├── 📄 SETUP_INSTRUCTIONS.md  # Este arquivo
├── 📁 venv/                  # Ambiente virtual (criado)
├── 📁 agents/
│   └── 📄 log_analyzer.py    # Agente principal
├── 📁 utils/
│   └── 📄 preprocessor.py    # Pré-processamento
├── 📁 data/
│   └── 📄 example.log        # Log de exemplo
├── 📁 vectorstore/           # Banco vetorial (criado)
├── 📁 output/                # Resultados (criado)
└── 📁 logs/                  # Logs do sistema (criado)
```

## ✅ Checklist de Verificação

Antes da aula, verifique:

- [ ] Python 3.8+ instalado
- [ ] Ambiente virtual criado e ativo
- [ ] Todas as dependências instaladas
- [ ] Arquivo .env configurado com OPENAI_API_KEY
- [ ] Teste do ambiente passou (test_environment.py)
- [ ] Análise de exemplo funciona (main.py analyze data/example.log)
- [ ] Interface Streamlit carrega (streamlit run streamlit_app.py)
- [ ] (Opcional) Integração Slack configurada
- [ ] (Opcional) Integração Discord configurada

## 🆘 Suporte Durante a Aula

### Comandos de Emergência

```bash
# Reset completo do ambiente
rm -rf venv vectorstore output
./setup.sh

# Teste rápido
python test_environment.py

# Análise de emergência (sem IA)
python main.py preprocess data/example.log
```

### Logs de Debug

```bash
# Ativa logs detalhados
export LANGCHAIN_VERBOSE=true
export LANGCHAIN_TRACING=true

# Executa com debug
python main.py analyze data/example.log --verbose
```

### Contatos de Suporte

- **Instrutor**: Disponível durante a aula
- **Documentação**: README.md
- **Logs de erro**: Salvos em `output/`

## 🎓 Próximos Passos

Após a configuração bem-sucedida:

1. **Familiarize-se** com a interface Streamlit
2. **Teste** a análise com diferentes logs
3. **Explore** as integrações disponíveis
4. **Prepare** perguntas para a aula
5. **Revise** a documentação técnica

---

**✨ Ambiente configurado com sucesso! Você está pronto para a aula prática.**

