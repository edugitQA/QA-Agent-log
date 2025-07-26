"""
Arquivo principal do Agente IA para Análise Inteligente de Logs de Erro.

Este script demonstra o uso completo do agente, incluindo:
- Configuração do ambiente
- Processamento de logs
- Análise com IA
- Integração com Slack/Discord
- Interface Streamlit
"""

import os
import sys
import json
import argparse
from datetime import datetime
from dotenv import load_dotenv

# Imports locais
from agents.log_analyzer import LogAnalyzerAgent
from utils.preprocessor import LogPreprocessor


def setup_environment():
    """
    Configura o ambiente carregando variáveis do .env
    """
    load_dotenv()
    
    # Verifica variáveis obrigatórias
    required_vars = ['OPENAI_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Variáveis de ambiente obrigatórias não encontradas: {missing_vars}")
        print("Por favor, configure o arquivo .env baseado no .env.example")
        return False
    
    print("✅ Ambiente configurado com sucesso")
    return True


def send_slack_alert(message: str, channel: str = None):
    """
    Envia alerta para o Slack.
    
    Args:
        message (str): Mensagem a ser enviada
        channel (str): Canal do Slack (opcional)
    """
    try:
        from slack_sdk import WebClient
        
        slack_token = os.getenv('SLACK_TOKEN')
        if not slack_token:
            print("⚠️ SLACK_TOKEN não configurado - pulando envio para Slack")
            return
        
        client = WebClient(token=slack_token)
        channel = channel or os.getenv('SLACK_CHANNEL', '#qa-alerts')
        
        response = client.chat_postMessage(
            channel=channel,
            text=message,
            username="QA Log Agent",
            icon_emoji=":robot_face:"
        )
        
        if response["ok"]:
            print(f"✅ Alerta enviado para Slack: {channel}")
        else:
            print(f"❌ Erro ao enviar para Slack: {response['error']}")
            
    except ImportError:
        print("⚠️ slack_sdk não instalado - pulando envio para Slack")
    except Exception as e:
        print(f"❌ Erro ao enviar alerta Slack: {e}")


def send_discord_alert(message: str):
    """
    Envia alerta para o Discord via webhook.
    
    Args:
        message (str): Mensagem a ser enviada
    """
    try:
        import requests
        
        webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
        if not webhook_url:
            print("⚠️ DISCORD_WEBHOOK_URL não configurado - pulando envio para Discord")
            return
        
        payload = {
            "content": message,
            "username": "QA Log Agent",
            "avatar_url": "https://cdn-icons-png.flaticon.com/512/4712/4712027.png"
        }
        
        response = requests.post(webhook_url, json=payload)
        
        if response.status_code == 204:
            print("✅ Alerta enviado para Discord")
        else:
            print(f"❌ Erro ao enviar para Discord: {response.status_code}")
            
    except ImportError:
        print("⚠️ requests não instalado - pulando envio para Discord")
    except Exception as e:
        print(f"❌ Erro ao enviar alerta Discord: {e}")


def format_alert_message(results):
    """
    Formata mensagem de alerta com resumo dos erros.
    
    Args:
        results: Lista de resultados da análise
        
    Returns:
        str: Mensagem formatada
    """
    if not results:
        return "🟢 Nenhum erro crítico detectado nos logs."
    
    critical_errors = [r for r in results if r.severity == 'CRITICAL']
    high_errors = [r for r in results if r.severity == 'HIGH']
    
    message = f"🚨 **Alerta de Logs de Erro - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}**\\n\\n"
    message += f"📊 **Resumo:**\\n"
    message += f"• Total de erros: {len(results)}\\n"
    message += f"• Críticos: {len(critical_errors)}\\n"
    message += f"• Alta prioridade: {len(high_errors)}\\n\\n"
    
    if critical_errors:
        message += "🔴 **Erros Críticos:**\\n"
        for i, error in enumerate(critical_errors[:3], 1):
            message += f"{i}. {error.error_message[:100]}...\\n"
        
        if len(critical_errors) > 3:
            message += f"... e mais {len(critical_errors) - 3} erros críticos\\n"
    
    message += "\\n📋 Verifique o relatório completo para mais detalhes."
    return message


def analyze_logs_command(args):
    """
    Comando para análise de logs.
    """
    print(f"🔄 Iniciando análise do arquivo: {args.log_file}")
    
    # Inicializa agente
    agent = LogAnalyzerAgent(
        openai_api_key=os.getenv('OPENAI_API_KEY'),
        vectorstore_path=args.vectorstore_path,
        model_name=args.model
    )
    
    # Processa arquivo
    results = agent.process_log_file(args.log_file)
    
    # Salva resultados
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f"{args.output_path}/analysis_{timestamp}.json"
    agent.save_analysis_results(results, output_file)
    
    # Envia alertas se configurado
    if args.send_alerts:
        alert_message = format_alert_message(results)
        send_slack_alert(alert_message)
        send_discord_alert(alert_message)
    
    # Mostra resumo
    print(f"\\n📊 Análise concluída:")
    print(f"• Arquivo processado: {args.log_file}")
    print(f"• Erros analisados: {len(results)}")
    print(f"• Resultados salvos em: {output_file}")
    
    if results:
        severities = {}
        for result in results:
            severities[result.severity] = severities.get(result.severity, 0) + 1
        
        print(f"• Distribuição por severidade:")
        for severity, count in severities.items():
            print(f"  - {severity}: {count}")


def preprocess_command(args):
    """
    Comando para pré-processamento de logs.
    """
    print(f"🔄 Pré-processando arquivo: {args.log_file}")
    
    preprocessor = LogPreprocessor()
    chunks, patterns = preprocessor.process_log_file(args.log_file, args.errors_only)
    
    # Salva chunks se solicitado
    if args.save_chunks:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        chunks_file = f"{args.output_path}/chunks_{timestamp}.json"
        
        with open(chunks_file, 'w', encoding='utf-8') as f:
            json.dump(chunks, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"✅ Chunks salvos em: {chunks_file}")
    
    # Mostra estatísticas
    print(f"\\n📊 Estatísticas do pré-processamento:")
    print(f"• Chunks criados: {len(chunks)}")
    print(f"• Total de erros: {patterns['total_errors']}")
    print(f"• Componentes afetados: {len(patterns['component_distribution'])}")
    print(f"• Palavras-chave de erro: {list(patterns['error_keywords'].keys())}")


def main():
    """
    Função principal com interface de linha de comando.
    """
    parser = argparse.ArgumentParser(
        description="Agente IA para Análise Inteligente de Logs de Erro"
    )
    
    # Argumentos globais
    parser.add_argument('--output-path', default='./output',
                       help='Diretório para salvar resultados')
    parser.add_argument('--vectorstore-path', default='./vectorstore',
                       help='Caminho para o banco vetorial')
    
    # Subcomandos
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponíveis')
    
    # Comando analyze
    analyze_parser = subparsers.add_parser('analyze', help='Analisa arquivo de log')
    analyze_parser.add_argument('log_file', help='Caminho para o arquivo de log')
    analyze_parser.add_argument('--model', default='gpt-3.5-turbo',
                               help='Modelo LLM a ser usado')
    analyze_parser.add_argument('--send-alerts', action='store_true',
                               help='Envia alertas para Slack/Discord')
    
    # Comando preprocess
    preprocess_parser = subparsers.add_parser('preprocess', 
                                            help='Pré-processa arquivo de log')
    preprocess_parser.add_argument('log_file', help='Caminho para o arquivo de log')
    preprocess_parser.add_argument('--errors-only', action='store_true',
                                  help='Processa apenas entradas de erro')
    preprocess_parser.add_argument('--save-chunks', action='store_true',
                                  help='Salva chunks processados')
    
    # Comando streamlit
    streamlit_parser = subparsers.add_parser('streamlit', 
                                           help='Inicia interface Streamlit')
    
    args = parser.parse_args()
    
    # Configura ambiente
    if not setup_environment():
        sys.exit(1)
    
    # Cria diretórios necessários
    os.makedirs(args.output_path, exist_ok=True)
    os.makedirs(args.vectorstore_path, exist_ok=True)
    
    # Executa comando
    if args.command == 'analyze':
        analyze_logs_command(args)
    elif args.command == 'preprocess':
        preprocess_command(args)
    elif args.command == 'streamlit':
        print("🚀 Iniciando interface Streamlit...")
        os.system("streamlit run streamlit_app.py")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

