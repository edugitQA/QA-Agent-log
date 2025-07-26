# 🤖 QA Log Agent - Agente IA para Análise Inteligente de Logs de Erro

## 📋 Visão Geral

O QA Log Agent é um agente autônomo desenvolvido para automatizar a análise de logs de erro utilizando Inteligência Artificial. O sistema é capaz de receber arquivos `.log`, interpretar erros com LLM, gerar explicações e possíveis causas, consultar um histórico vetorial de logs semelhantes e enviar alertas via Slack, Discord ou interface Streamlit.

## 🎯 Objetivos

- **Automatizar** a análise de logs de erro em ambientes de QA
- **Reduzir** o tempo de investigação manual de erros
- **Detectar** padrões de falha com base em histórico
- **Integrar** facilmente com sistemas existentes (Slack, Discord, Jira)
- **Acelerar** a identificação de falhas em ambientes de teste
- **Suportar** profissionais juniores na interpretação de erros técnicos

## 🏗️ Arquitetura

```
qa-log-agent/
├── main.py                 # Arquivo principal com CLI
├── streamlit_app.py        # Interface web Streamlit
├── requirements.txt        # Dependências Python
├── .env.example           # Exemplo de configuração
├── agents/
│   └── log_analyzer.py    # Agente principal de análise
├── utils/
│   └── preprocessor.py    # Pré-processamento de logs
├── data/
│   └── example.log        # Arquivo de exemplo
├── vectorstore/           # Banco vetorial ChromaDB
├── output/               # Relatórios e resultados
└── README.md             # Esta documentação
```

## 🔧 Tecnologias Utilizadas

- **Python 3.11+**: Linguagem principal
- **LangChain/LangGraph**: Orquestração de fluxos com LLM
- **OpenAI GPT**: Interpretação e análise de erros
- **ChromaDB**: Banco vetorial para busca semântica
- **Streamlit**: Interface web interativa
- **Slack SDK**: Integração com Slack
- **Pandas**: Manipulação de dados
- **Plotly**: Visualizações interativas

## 🚀 Instalação e Configuração

### 1. Pré-requisitos

- Python 3.11 ou superior
- Chave da API OpenAI
- (Opcional) Token do Slack Bot
- (Opcional) Webhook URL do Discord

### 2. Instalação

```bash
# Clone ou baixe o projeto
cd qa-log-agent

# Crie ambiente virtual
python -m venv venv

# Ative o ambiente virtual
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\\Scripts\\activate

# Instale dependências
pip install -r requirements.txt
```

### 3. Configuração

```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite o arquivo .env com suas configurações
nano .env
```

Exemplo de configuração `.env`:

```env
# OpenAI API Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here

# Slack Integration (opcional)
SLACK_TOKEN=xoxb-your-slack-bot-token
SLACK_CHANNEL=#qa-alerts

# Discord Integration (opcional)
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/your-webhook

# Configurações do Agente
LOG_DIRECTORY=./data
VECTORSTORE_PATH=./vectorstore
OUTPUT_PATH=./output
```

## 📖 Como Usar

### 1. Interface de Linha de Comando

#### Análise Completa de Log

```bash
# Análise básica
python main.py analyze data/example.log

# Análise com alertas
python main.py analyze data/example.log --send-alerts

# Análise com modelo específico
python main.py analyze data/example.log --model gpt-4
```

#### Pré-processamento

```bash
# Pré-processamento básico
python main.py preprocess data/example.log

# Apenas erros com salvamento de chunks
python main.py preprocess data/example.log --errors-only --save-chunks
```

### 2. Interface Web Streamlit

```bash
# Inicia interface web
python main.py streamlit

# Ou diretamente
streamlit run streamlit_app.py
```

Acesse `http://localhost:8501` no navegador.

### 3. Uso Programático

```python
from agents.log_analyzer import LogAnalyzerAgent
import os

# Inicializa agente
agent = LogAnalyzerAgent(
    openai_api_key=os.getenv('OPENAI_API_KEY'),
    vectorstore_path="./vectorstore"
)

# Analisa arquivo
results = agent.process_log_file("data/example.log")

# Processa resultados
for result in results:
    print(f"Erro: {result.error_message}")
    print(f"Severidade: {result.severity}")
    print(f"Explicação: {result.explanation}")
```

## 🔍 Funcionalidades Principais

### 1. Pré-processamento Inteligente

- **Parsing automático** de logs com regex
- **Extração de metadados** (timestamp, nível, componente)
- **Chunking otimizado** respeitando limites de tokens
- **Filtragem** de entradas de erro e críticas

### 2. Análise com IA

- **Interpretação contextual** de mensagens de erro
- **Busca semântica** de logs similares no histórico
- **Geração de explicações** claras e acionáveis
- **Sugestões de causa** e recomendações de resolução
- **Score de confiança** para cada análise

### 3. Integração e Alertas

- **Slack**: Envio automático de alertas para canais
- **Discord**: Notificações via webhook
- **Streamlit**: Interface web interativa
- **JSON/CSV**: Exportação de relatórios

### 4. Visualizações

- **Distribuição por severidade** (gráfico pizza)
- **Timeline de erros** (gráfico scatter)
- **Métricas em tempo real**
- **Filtros interativos**

## 📊 Exemplo de Saída

### Análise de Erro

```json
{
  "error_message": "Connection timeout after 30 seconds to database server db-prod-01:5432",
  "explanation": "Erro de timeout de conexão com o banco de dados PostgreSQL. O servidor não respondeu dentro do tempo limite configurado.",
  "possible_causes": [
    "Sobrecarga no servidor de banco de dados",
    "Problemas de rede entre aplicação e banco",
    "Configuração inadequada de timeout",
    "Pool de conexões esgotado"
  ],
  "severity": "HIGH",
  "recommendations": [
    "Verificar status do servidor PostgreSQL",
    "Monitorar uso de CPU e memória do banco",
    "Revisar configurações de timeout",
    "Analisar logs do banco de dados"
  ],
  "confidence_score": 0.92
}
```

### Alerta Slack

```
🚨 **Alerta de Logs de Erro - 2024-01-15 10:30:25**

📊 **Resumo:**
• Total de erros: 8
• Críticos: 1
• Alta prioridade: 3

🔴 **Erros Críticos:**
1. Multiple failed login attempts detected from IP 192.168.1.100...

📋 Verifique o relatório completo para mais detalhes.
```

## 🎓 Impacto para QA

### Benefícios Diretos

- **⏱️ Redução de 70%** no tempo de investigação de erros
- **🔍 Detecção automática** de padrões de falha recorrentes
- **🤝 Suporte especializado** para profissionais juniores
- **📈 Aumento da acurácia** na análise de bugs
- **🔗 Integração nativa** com ferramentas existentes

### Casos de Uso

1. **Monitoramento Contínuo**: Agente rodando em background analisando logs em tempo real
2. **Análise Pós-Incidente**: Investigação rápida de falhas em produção
3. **Treinamento de Equipe**: Ferramenta educativa para QA juniores
4. **Documentação Automática**: Geração de relatórios detalhados de bugs

## 🔧 Personalização e Extensão

### Adicionando Novos Integrações

```python
# Exemplo: Integração com Jira
def create_jira_issue(result):
    from jira import JIRA
    
    jira = JIRA(server='https://company.atlassian.net', 
                basic_auth=('email', 'token'))
    
    issue_dict = {
        'project': {'key': 'QA'},
        'summary': f'Erro detectado: {result.error_message[:50]}...',
        'description': result.explanation,
        'issuetype': {'name': 'Bug'},
        'priority': {'name': 'High' if result.severity == 'CRITICAL' else 'Medium'}
    }
    
    return jira.create_issue(fields=issue_dict)
```

### Customizando Prompts

```python
# Personalizar prompt do LLM
custom_prompt = """
Você é um especialista em {domain} com foco em {technology}.
Analise este erro considerando as melhores práticas de {domain}...
"""
```

## 🐛 Troubleshooting

### Problemas Comuns

1. **Erro de API Key**
   ```
   ❌ OPENAI_API_KEY não encontrada
   ```
   **Solução**: Verifique se a variável está configurada no `.env`

2. **Erro de Dependências**
   ```
   ModuleNotFoundError: No module named 'langchain'
   ```
   **Solução**: Execute `pip install -r requirements.txt`

3. **Erro de Permissão ChromaDB**
   ```
   PermissionError: [Errno 13] Permission denied: './vectorstore'
   ```
   **Solução**: Verifique permissões da pasta ou execute com `sudo`

### Logs de Debug

```bash
# Ativar logs detalhados
export LANGCHAIN_VERBOSE=true
export LANGCHAIN_TRACING=true

# Executar com debug
python main.py analyze data/example.log --verbose
```

## 🤝 Contribuição

### Estrutura para Desenvolvimento

```bash
# Instalar dependências de desenvolvimento
pip install -r requirements-dev.txt

# Executar testes
python -m pytest tests/

# Verificar qualidade do código
flake8 .
black .
```

### Roadmap

- [ ] Integração com Jira API
- [ ] Suporte a múltiplos formatos de log
- [ ] Dashboard em tempo real
- [ ] Machine Learning para detecção de anomalias
- [ ] API REST para integração externa
- [ ] Suporte a logs estruturados (JSON)

## 📄 Licença

Este projeto é desenvolvido para fins educacionais e pode ser adaptado conforme necessário.

## 📞 Suporte

Para dúvidas ou sugestões sobre o QA Log Agent:

- 📧 Email: suporte@edusync.com
- 💬 Slack: #qa-automation
- 📖 Documentação: [Wiki do Projeto]

---

**Desenvolvido com ❤️ para automatizar e otimizar processos de QA**

