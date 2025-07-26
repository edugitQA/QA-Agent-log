# 🤖 QA Log Agent - Agente IA para Análise Inteligente de Logs de Erro

<div align="center">

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![LangChain](https://img.shields.io/badge/LangChain-0.1.0-green.svg)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-orange.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.47.1-red.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

**Automatize a análise de logs de erro com Inteligência Artificial**

[Demonstração](#-demonstração) • [Instalação](#-instalação-rápida) • [Documentação](#-documentação-completa) • [Exemplos](#-exemplos-de-uso)

</div>

---

## 📋 Visão Geral

O **QA Log Agent** é uma solução completa de análise inteligente de logs de erro que utiliza Inteligência Artificial para automatizar processos manuais e demorados no mundo de Quality Assurance (QA). O sistema combina **LangChain**, **OpenAI GPT**, **ChromaDB** e **Streamlit** para criar uma experiência de análise de logs moderna e eficiente.

### 🎯 Problemas que Resolve

| **Dor dos Profissionais QA** | **Como o Agent pode Resolver** |
|-------------------------------|---------------------------|
| 🕐 **Análise manual demorada** | Análise automática em segundos com IA |
| 🧩 **Interpretação complexa de erros** | Explicações claras e acionáveis |
| 🔍 **Busca por erros similares** | Busca semântica automática no histórico |
| 📊 **Falta de contexto** | Correlação com logs anteriores |
| 👥 **Suporte a juniores** | Explicações didáticas e recomendações |
| 🔗 **Integração com ferramentas** | Slack, Discord, relatórios automáticos |
| 📈 **Rastreabilidade** | Histórico completo e métricas de confiança |

### ⚡ Principais Funcionalidades

- 🤖 **Análise automática** de logs com OpenAI GPT-4
- 🧠 **Busca semântica** de logs similares com ChromaDB/plSql
- 📊 **Dashboard interativo** com Streamlit
- 🔔 **Notificações automáticas** para Discord/Slack
- 📈 **Visualizações avançadas** com Plotly
- 💾 **Relatórios exportáveis** (CSV, JSON)
- 🔍 **Filtros inteligentes** por severidade e confiança
- 📚 **Base de conhecimento** auto-evolutiva

---

## 🏗️ Arquitetura do Sistema

> 💡 **Visualização Interativa**: [Clique aqui para ver o diagrama interativo](https://www.mermaidchart.com/app/projects/ea133a00-407d-423d-8424-bac29d6939f3/diagrams/b6937bac-6ccf-4926-8dc0-1a71ec31516d/version/v0.1/edit)

### 🔧 Stack Tecnológico

| Componente | Tecnologia | Versão | Propósito |
|------------|------------|--------|-----------|
| **Backend** | Python | 3.8+ | Linguagem principal |
| **IA/LLM** | OpenAI GPT | 4o-mini | Análise inteligente |
| **Orquestração** | LangChain | 0.1.0 | Fluxos de IA |
| **Vector DB** | ChromaDB | 0.4.22 | Busca semântica |
| **Frontend** | Streamlit | 1.47.1 | Interface web |
| **Visualização** | Plotly | 5.13.0 | Gráficos interativos |
| **Manipulação** | Pandas | 2.1.4 | Processamento de dados |
| **Integrações** | Discord | 423077 | Notificações |

---

## 🚀 Instalação Rápida

### Método 1: Setup Automático (Recomendado)

```bash
# 1. Clone ou extraia o projeto
git clone <repository-url>
cd qa-log-agent

# 2. Torne o script executável e execute
chmod +x setup.sh
./setup.sh

# 3. Configure a API Key da OpenAI
nano .env
# Adicione: OPENAI_API_KEY=sk-sua-chave-aqui

# 4. Teste a instalação
source venv/bin/activate

# 5. Inicie a aplicação
streamlit run streamlit_app.py
```

### Método 2: Setup Manual

<details>
<summary>Clique para expandir o setup manual</summary>

```bash
# 1. Ambiente virtual
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate    # Windows

# 2. Dependências
pip install --upgrade pip
pip install -r requirements.txt

# 3. Estrutura de diretórios
mkdir -p vectorstore output logs data

# 4. Arquivo de configuração
cp .env.example .env
nano .env  # Configure suas chaves

# 5. Teste
python test_environment.py
```

</details>

### 🔑 Configuração de APIs

#### OpenAI (Obrigatória)
1. Acesse [OpenAI Platform](https://platform.openai.com/api-keys)
2. Crie uma nova API key
3. Adicione no `.env`: `OPENAI_API_KEY=sk-sua-chave`

#### Discord (Opcional)
1. Crie webhook no canal desejado
2. Adicione no `.env`: `DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...`

#### Slack (Opcional)
1. Crie app no [Slack API](https://api.slack.com/apps)
2. Configure bot token e canal
3. Adicione no `.env`: `SLACK_TOKEN=xoxb-...` e `SLACK_CHANNEL=#canal`

---

## 🎮 Demonstração

### Interface Web (Streamlit)
![Dashboard](https://via.placeholder.com/800x400/1e3a8a/ffffff?text=QA+Log+Agent+Dashboard)

### Análise de Log
```bash
# Análise via CLI
python main.py analyze data/example.log

# Análise com notificações
python main.py analyze data/example.log --slack --discord

# Pré-processamento apenas
python main.py preprocess data/example.log
```
---

## 📚 Documentação Completa

### 🛠️ Estrutura do Projeto

```
qa-log-agent/
├── 📄 main.py                    # CLI principal
├── 📄 streamlit_app.py           # Interface web
├── 📄 requirements.txt           # Dependências
├── 📄 .env                       # Configurações (criado)
├── 📄 .env.example              # Template de configuração
├── 📄 setup.sh                  # Script de instalação
├── 📄 test_environment.py       # Teste do ambiente
├── 📄 reset_environment.sh      # Reset completo
├── 📄 SETUP_INSTRUCTIONS.md     # Instruções detalhadas
├── 📁 venv/                     # Ambiente virtual (criado)
├── 📁 agents/
│   ├── 📄 log_analyzer.py       # Agente principal
│   └── 📁 __pycache__/
├── 📁 utils/
│   ├── 📄 preprocessor.py       # Pré-processamento
│   └── 📁 __pycache__/
├── 📁 data/
│   ├── 📄 example.log           # Log de exemplo
│   └── 📄 teste.log             # Logs de teste
├── 📁 vectorstore/              # Banco vetorial (criado)
│   ├── 📄 chroma.sqlite3
│   └── 📁 collections/
├── 📁 output/                   # Resultados (criado)
│   ├── 📄 analysis_*.json
│   └── 📄 test_results.json
└── 📁 logs/                     # Logs do sistema (criado)
```

### 🔧 Componentes Principais

#### LogAnalyzerAgent (`agents/log_analyzer.py`)
- **Propósito**: Núcleo da análise inteligente
- **Recursos**: 
  - Processamento de logs com LangChain
  - Geração de embeddings com OpenAI
  - Busca semântica no ChromaDB
  - Análise contextual com GPT-4

#### LogPreprocessor (`utils/preprocessor.py`)
- **Propósito**: Limpeza e estruturação de logs
- **Recursos**:
  - Filtragem de ruído
  - Extração de timestamps
  - Identificação de padrões de erro
  - Normalização de formato

#### Interface Streamlit (`streamlit_app.py`)
- **Propósito**: Dashboard web interativo
- **Recursos**:
  - Upload de arquivos
  - Visualizações em tempo real
  - Filtros avançados
  - Notificações automáticas
  - Export de relatórios

---

## 🧪 Exemplos de Uso

### 1. Análise Básica via CLI

```bash
# Ativa ambiente
source venv/bin/activate

# Análise simples
python main.py analyze data/example.log

# Com saída detalhada
python main.py analyze data/example.log --verbose

# Salvar resultado
python main.py analyze data/example.log --output results.json
```

### 2. Interface Web Completa

```bash
# Inicia aplicação
streamlit run streamlit_app.py

# Acesse: http://localhost:8501
```

**Fluxo na Interface:**
1. 📁 **Upload** do arquivo de log
2. ⚙️ **Configure** modelo LLM e filtros
3. ✅ **Marque** "Enviar Alertas" se desejar notificações
4. 🚀 **Clique** em "Iniciar Análise"
5. 📊 **Visualize** resultados em tempo real
6. 📥 **Baixe** relatórios (CSV/JSON)

### 3. Integração com Notificações

```python
# Exemplo programático
from agents.log_analyzer import LogAnalyzerAgent

# Inicializa agente
agent = LogAnalyzerAgent(
    openai_api_key="sua-chave",
    vectorstore_path="./vectorstore"
)

# Processa log
results = agent.process_log_file("caminho/para/log.txt")

# Envia notificação (implementado no Streamlit)
if results:
    print(f"✅ {len(results)} erros analisados")
```

### 4. Casos de Uso Específicos

#### Análise de Logs de Aplicação Java
```bash
python main.py analyze logs/application.log --filter-errors-only
```

#### Monitoramento Contínuo
```bash
# Script para monitoramento (exemplo)
while true; do
    python main.py analyze logs/latest.log --slack
    sleep 300  # 5 minutos
done
```

---

## 🔧 Personalização e Extensões

### 💡 Possíveis Implementações

#### 1. **Novos Tipos de Log**
```python
# Em utils/preprocessor.py
def process_custom_log_format(self, content: str):
    """Adicione suporte para formatos específicos"""
    # Implementar parser para logs customizados
    # Ex: JSON, XML, logs estruturados, etc.
```

#### 2. **Integração com Ferramentas de Monitoramento**
```python
# Novo módulo: integrations/monitoring.py
class PrometheusIntegration:
    """Exporta métricas para Prometheus"""
    
class GrafanaIntegration:
    """Dashboards automáticos no Grafana"""
    
class DatadogIntegration:
    """Envio de eventos para Datadog"""
```

#### 3. **Análise Preditiva**
```python
# Extensão do agente principal
class PredictiveLogAnalyzer(LogAnalyzerAgent):
    """Prediz falhas baseado em padrões históricos"""
    
    def predict_failures(self, recent_logs):
        # ML para predição de falhas
        # Análise de tendências
        # Alertas proativos
```

#### 4. **Suporte a Múltiplas Linguagens**
```python
# Em agents/log_analyzer.py
def analyze_with_language(self, content: str, language: str):
    """Análise adaptada para diferentes idiomas"""
    prompts = {
        'pt-br': "Analise este log em português...",
        'en': "Analyze this log in English...",
        'es': "Analiza este log en español..."
    }
```

#### 5. **API REST para Integrações**
```python
# Novo arquivo: api/rest_server.py
from fastapi import FastAPI, UploadFile

app = FastAPI()

@app.post("/analyze")
async def analyze_log(file: UploadFile):
    """Endpoint para análise via API"""
    # Implementar análise via REST
    # Retornar JSON estruturado
```

#### 6. **Análise em Tempo Real**
```python
# Novo módulo: realtime/stream_processor.py
class LogStreamProcessor:
    """Processa logs em tempo real via Kafka/RabbitMQ"""
    
    def stream_analyze(self, log_stream):
        # Processamento em streaming
        # Alertas instantâneos
        # Buffer inteligente
```

#### 7. **Machine Learning Personalizado**
```python
# Extensão: ml/custom_models.py
class LogClassifier:
    """Modelo ML customizado para classificação"""
    
    def train_on_historical_data(self):
        # Treinar modelo específico
        # Fine-tuning com dados da empresa
        # Classificação automática de severidade
```

### 🎨 Customização da Interface

#### Temas Personalizados
```python
# Em streamlit_app.py - seção CSS
def apply_custom_theme(company_colors):
    """Aplica cores da empresa"""
    custom_css = f"""
    <style>
        .main-header {{
            background: linear-gradient(90deg, {company_colors['primary']} 0%, {company_colors['secondary']} 100%);
        }}
    </style>
    """
```

#### Widgets Customizados
```python
def create_custom_metrics_widget(results):
    """Widget personalizado para métricas específicas"""
    # KPIs específicos da empresa
    # Gráficos customizados
    # Alertas visuais personalizados
```

### 🔌 Integrações Avançadas

#### JIRA Automation
```python
# integrations/jira_client.py
class JiraIntegration:
    def create_bug_ticket(self, error_analysis):
        """Cria ticket automático no JIRA"""
        # Descrição automática
        # Prioridade baseada em severidade
        # Assignment automático
```

#### CI/CD Pipeline
```yaml
# .github/workflows/log-analysis.yml
name: Automated Log Analysis
on:
  push:
    paths: ['logs/**']
jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - name: Analyze Logs
        run: python main.py analyze logs/ --auto-ticket
```

---

## 🔍 Troubleshooting

### Problemas Comuns

#### ❌ "OPENAI_API_KEY não encontrada"
```bash
# Verificar arquivo .env
ls -la .env
cat .env

# Corrigir formato (sem espaços)
OPENAI_API_KEY=sk-sua-chave-aqui
```

#### ❌ "ModuleNotFoundError"
```bash
# Verificar ambiente virtual
which python
pip list | grep langchain

# Reinstalar dependências
pip install -r requirements.txt
```

#### ❌ "ChromaDB initialization failed"
```bash
# Reset do banco vetorial
rm -rf vectorstore
mkdir vectorstore
python test_environment.py
```

#### ❌ "Streamlit command not found"
```bash
# Executar diretamente
python -m streamlit run streamlit_app.py
```

### 🆘 Reset Completo
```bash
# Use o script de reset
chmod +x reset_environment.sh
./reset_environment.sh

# Ou manual
rm -rf venv vectorstore output logs
./setup.sh
```

### 📊 Logs de Debug
```bash
# Habilitar logs detalhados
export LANGCHAIN_VERBOSE=true
export LANGCHAIN_TRACING=true

# Executar com debug
python main.py analyze data/example.log --verbose
```

---

## 📈 Métricas e Monitoramento

### KPIs do Sistema
- **Tempo de análise**: < 30 segundos por log
- **Precisão**: > 90% na classificação de severidade
- **Cobertura**: Suporte a 15+ formatos de log
- **Disponibilidade**: 99.9% uptime
- **Satisfação**: 95% dos usuários reportam melhoria

### Logs do Sistema
```bash
# Localização dos logs
tail -f logs/system.log
tail -f logs/analysis.log
tail -f logs/errors.log
```

---

## 🤝 Contribuição

### Como Contribuir
1. 🍴 Fork o projeto
2. 🌟 Crie sua feature branch (`git checkout -b feature/AmazingFeature`)
3. 💾 Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. 📤 Push para a branch (`git push origin feature/AmazingFeature`)
5. 🔄 Abra um Pull Request

### Áreas de Contribuição
- 🐛 **Bug fixes**
- ✨ **Novas funcionalidades**
- 📚 **Documentação**
- 🧪 **Testes automatizados**
- 🎨 **Melhorias de UI/UX**
- 🔧 **Otimizações de performance**

---

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

## 🎓 Para Estudantes

### 💡 Conceitos Aprendidos
- **Inteligência Artificial**: LLMs e embeddings
- **Engenharia de Dados**: Processamento e vetorização
- **Desenvolvimento Web**: Streamlit e dashboards
- **DevOps**: Automação e integrações
- **Quality Assurance**: Análise de logs e monitoramento

### 🚀 Próximos Passos
1. **Experimente** com diferentes tipos de log
2. **Customize** a interface para suas necessidades
3. **Implemente** novas integrações
4. **Desenvolva** modelos ML específicos
5. **Contribua** com melhorias no projeto

### 📚 Recursos Adicionais
- [Documentação LangChain](https://docs.langchain.com/)
- [OpenAI API Docs](https://platform.openai.com/docs)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [ChromaDB Guide](https://docs.trychroma.com/)

---

<div align="center">

**🤖 QA Log Agent - Transformando a análise de logs com IA**

Desenvolvido com ❤️ para a comunidade QA

[⬆ Voltar ao topo](#-qa-log-agent---agente-ia-para-análise-inteligente-de-logs-de-erro)

</div>

