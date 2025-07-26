"""
Interface Streamlit para o Agente IA de Análise de Logs de Erro - VERSÃO CORRIGIDA

Esta aplicação web permite:
- Upload de arquivos de log
- Visualização da análise em tempo real
- Exploração de logs similares
- Download de relatórios
"""

import streamlit as st
from dotenv import load_dotenv
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from io import StringIO
import os
import requests


# Imports locais
from agents.log_analyzer import LogAnalyzerAgent
from utils.preprocessor import LogPreprocessor

load_dotenv()


def send_discord_notification(results, analysis_summary=None):
    """
    Envia notificação formatada para Discord via webhook.
    
    Args:
        results: Lista com resultados da análise
        analysis_summary: Resumo opcional da análise
    """
    webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
    if not webhook_url:
        st.warning("⚠️ DISCORD_WEBHOOK_URL não configurado no .env")
        return False
    
    if not results:
        return False
    
    try:
        # Conta severidades
        severity_counts = {}
        for result in results:
            severity = result.get('severity', 'UNKNOWN')
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # Calcula confiança média
        confidence_scores = [r.get('confidence_score', 0) for r in results if r.get('confidence_score') is not None]
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        
        # Emojis para severidades
        severity_emojis = {
            'CRITICAL': '🔴',
            'HIGH': '🟠',
            'MEDIUM': '🟡',
            'LOW': '🟢',
            'UNKNOWN': '⚪'
        }
        
        # Cores para embed (hexadecimal)
        embed_color = 15158332  # Vermelho para crítico
        if severity_counts.get('CRITICAL', 0) == 0:
            if severity_counts.get('HIGH', 0) > 0:
                embed_color = 16753920  # Laranja para alto
            elif severity_counts.get('MEDIUM', 0) > 0:
                embed_color = 16776960  # Amarelo para médio
            else:
                embed_color = 5763719   # Verde para baixo
        
        # Monta embed principal
        embed = {
            "title": "🤖 QA Log Agent - Análise Concluída",
            "description": f"Análise de logs processada com **{len(results)} erros** encontrados",
            "color": embed_color,
            "timestamp": datetime.now().isoformat(),
            "fields": [
                {
                    "name": "📊 Resumo da Análise",
                    "value": f"**Total de Erros:** {len(results)}\n**Confiança Média:** {avg_confidence:.1%}",
                    "inline": True
                }
            ],
            "footer": {
                "text": "QA Log Agent - Edusync",
                "icon_url": "https://cdn.discordapp.com/attachments/123456789/robot.png"
            }
        }
        
        # Adiciona campo de severidades se houver erros
        if severity_counts:
            severity_text = ""
            for severity, count in severity_counts.items():
                emoji = severity_emojis.get(severity, '⚪')
                severity_text += f"{emoji} **{severity}**: {count}\n"
            
            embed["fields"].append({
                "name": "🎯 Distribuição por Severidade",
                "value": severity_text.strip(),
                "inline": True
            })
        
        # Adiciona top 3 erros mais críticos
        critical_errors = [r for r in results if r.get('severity') in ['CRITICAL', 'HIGH']]
        critical_errors.sort(key=lambda x: x.get('confidence_score', 0), reverse=True)
        
        if critical_errors:
            top_errors_text = ""
            for i, error in enumerate(critical_errors[:3], 1):
                severity_emoji = severity_emojis.get(error.get('severity'), '⚪')
                error_msg = str(error.get('error_message', 'Erro não especificado'))
                confidence = error.get('confidence_score', 0)
                
                # Trunca mensagem se muito longa
                if len(error_msg) > 80:
                    error_msg = error_msg[:80] + "..."
                
                top_errors_text += f"{severity_emoji} **{i}.** {error_msg}\n*Confiança: {confidence:.1%}*\n\n"
            
            embed["fields"].append({
                "name": "🚨 Top 3 Erros Prioritários",
                "value": top_errors_text.strip(),
                "inline": False
            })
        
        # Adiciona resumo personalizado se fornecido
        if analysis_summary:
            embed["fields"].append({
                "name": "📝 Resumo da Análise",
                "value": str(analysis_summary)[:1000],  # Limita tamanho
                "inline": False
            })
        
        # Monta payload para Discord
        payload = {
            "embeds": [embed],
            "username": "QA Log Agent",
            "avatar_url": "https://cdn.discordapp.com/attachments/123456789/robot.png"
        }
        
        # Envia para Discord
        response = requests.post(webhook_url, json=payload, timeout=10)
        response.raise_for_status()
        
        return True
        
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Erro ao enviar para Discord: {e}")
        return False
    except Exception as e:
        st.error(f"❌ Erro inesperado ao enviar para Discord: {e}")
        return False

# Configuração da página
st.set_page_config(
    page_title="QA Log Agent - Análise Inteligente de Logs",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado para seguir identidade visual Edusync
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: #f8fafc !important;
        background-color: #f8fafc !important;
        padding: 1.5rem !important;
        border-radius: 12px !important;
        border-left: 5px solid #3b82f6 !important;
        margin: 0.5rem 0 !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important;
        border: 1px solid #e2e8f0 !important;
        opacity: 1 !important;
    }
    
    .metric-card h3 {
        color: #1e293b !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        margin: 0 0 0.5rem 0 !important;
    }
    
    .metric-card h2 {
        color: #3b82f6 !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
        margin: 0 !important;
    }
    
    .error-card {
        background: #fef2f2 !important;
        background-color: #fef2f2 !important;
        padding: 1.5rem !important;
        border-radius: 12px !important;
        border-left: 5px solid #ef4444 !important;
        margin: 0.5rem 0 !important;
        box-shadow: 0 2px 8px rgba(239,68,68,0.1) !important;
        border: 1px solid #fecaca !important;
        opacity: 1 !important;
    }
    
    .error-card h3 {
        color: #7f1d1d !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        margin: 0 0 0.5rem 0 !important;
    }
    
    .error-card h2 {
        color: #ef4444 !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
        margin: 0 !important;
    }
    
    .success-card {
        background: #f0fdf4 !important;
        background-color: #f0fdf4 !important;
        padding: 1.5rem !important;
        border-radius: 12px !important;
        border-left: 5px solid #22c55e !important;
        margin: 0.5rem 0 !important;
        box-shadow: 0 2px 8px rgba(34,197,94,0.1) !important;
        border: 1px solid #bbf7d0 !important;
        opacity: 1 !important;
    }
    
    .success-card h3 {
        color: #14532d !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        margin: 0 0 0.5rem 0 !important;
    }
    
    .success-card h2 {
        color: #22c55e !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
        margin: 0 !important;
    }
    
    .sidebar .sidebar-content {
        background: #1e293b;
    }
    
    /* Fix para garantir que os cards não fiquem transparentes */
    .stMarkdown > div {
        opacity: 1 !important;
    }
    
    /* Adiciona transição suave */
    .metric-card, .error-card, .success-card {
        transition: all 0.3s ease !important;
    }
    
    .metric-card:hover, .error-card:hover, .success-card:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 16px rgba(0,0,0,0.15) !important;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Inicializa variáveis de sessão."""
    if 'agent' not in st.session_state:
        st.session_state.agent = None
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = []
    if 'log_content' not in st.session_state:
        st.session_state.log_content = ""


def setup_agent():
    """Configura o agente de análise."""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        st.error("🔑 OPENAI_API_KEY não configurada. Verifique as variáveis de ambiente.")
        return None
    
    try:
        agent = LogAnalyzerAgent(
            openai_api_key=api_key,
            vectorstore_path="./vectorstore",
            model_name="gpt-4o-mini"
        )
        return agent
    except Exception as e:
        st.error(f"❌ Erro ao inicializar agente: {e}")
        return None


def display_header():
    """Exibe cabeçalho da aplicação."""
    st.markdown("""
    <div class="main-header">
        <h1>🤖 QA Log Agent</h1>
        <p>Análise Inteligente de Logs de Erro com IA</p>
    </div>
    """, unsafe_allow_html=True)


def display_metrics(results):
    """Exibe métricas da análise."""
    if not results:
        return
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>📊 Total de Erros</h3>
            <h2>{}</h2>
        </div>
        """.format(len(results)), unsafe_allow_html=True)
    
    with col2:
        # CORRIGIDO: Acesso por chave de dicionário
        critical_count = sum(1 for r in results if r.get('severity') == 'CRITICAL')
        st.markdown("""
        <div class="error-card">
            <h3>🔴 Críticos</h3>
            <h2>{}</h2>
        </div>
        """.format(critical_count), unsafe_allow_html=True)
    
    with col3:
        # CORRIGIDO: Acesso por chave de dicionário
        high_count = sum(1 for r in results if r.get('severity') == 'HIGH')
        st.markdown("""
        <div class="error-card">
            <h3>🟠 Alta Prioridade</h3>
            <h2>{}</h2>
        </div>
        """.format(high_count), unsafe_allow_html=True)
    
    with col4:
        # CORRIGIDO: Acesso por chave de dicionário e tratamento de divisão por zero
        confidence_scores = [r.get('confidence_score', 0) for r in results if r.get('confidence_score') is not None]
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        st.markdown("""
        <div class="success-card">
            <h3>🎯 Confiança Média</h3>
            <h2>{:.1%}</h2>
        </div>
        """.format(avg_confidence), unsafe_allow_html=True)


def display_severity_chart(results):
    """Exibe gráfico de distribuição por severidade."""
    if not results:
        return
    
    # CORRIGIDO: Acesso por chave de dicionário
    severity_counts = {}
    for result in results:
        severity = result.get('severity', 'UNKNOWN')
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
    
    df = pd.DataFrame(list(severity_counts.items()), columns=['Severidade', 'Quantidade'])
    
    # Cores personalizadas
    color_map = {
        'CRITICAL': '#ef4444',
        'HIGH': '#f97316', 
        'MEDIUM': '#eab308',
        'LOW': '#22c55e',
        'UNKNOWN': '#6b7280'
    }
    
    fig = px.pie(df, values='Quantidade', names='Severidade',
                 title="Distribuição de Erros por Severidade",
                 color='Severidade',
                 color_discrete_map=color_map)
    
    fig.update_layout(
        font=dict(size=14),
        title_font_size=18,
        showlegend=True
    )
    
    st.plotly_chart(fig, use_container_width=True)


def display_timeline_chart(results):
    """Exibe gráfico de timeline dos erros."""
    if not results:
        return
    
    # Prepara dados para timeline
    timeline_data = []
    for result in results:
        # CORRIGIDO: Acesso por chave de dicionário e tratamento de timestamp
        timestamp = result.get('timestamp')
        if isinstance(timestamp, str):
            try:
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except:
                timestamp = datetime.now()
        elif not isinstance(timestamp, datetime):
            timestamp = datetime.now()
            
        timeline_data.append({
            'timestamp': timestamp,
            'severity': result.get('severity', 'UNKNOWN'),
            'message': str(result.get('error_message', ''))[:50] + "..."
        })
    
    df = pd.DataFrame(timeline_data)
    
    # Verifica se há dados para plotar
    if df.empty:
        st.info("📊 Não há dados suficientes para o gráfico de timeline.")
        return
    
    fig = px.scatter(df, x='timestamp', y='severity', 
                     hover_data=['message'],
                     title="Timeline de Erros",
                     color='severity',
                     color_discrete_map={
                         'CRITICAL': '#ef4444',
                         'HIGH': '#f97316',
                         'MEDIUM': '#eab308', 
                         'LOW': '#22c55e',
                         'UNKNOWN': '#6b7280'
                     })
    
    fig.update_layout(
        xaxis_title="Timestamp",
        yaxis_title="Severidade",
        font=dict(size=14),
        title_font_size=18
    )
    
    st.plotly_chart(fig, use_container_width=True)


def display_analysis_results(results):
    """Exibe resultados detalhados da análise."""
    if not results:
        st.info("📝 Nenhum resultado de análise disponível.")
        return
    
    st.subheader("📋 Resultados Detalhados")
    
    # Filtros
    col1, col2 = st.columns(2)
    with col1:
        # CORRIGIDO: Acesso por chave de dicionário
        severities = list(set(r.get('severity', 'UNKNOWN') for r in results))
        severity_filter = st.selectbox(
            "Filtrar por Severidade:",
            ["Todos"] + severities
        )
    
    with col2:
        confidence_filter = st.slider(
            "Confiança Mínima:",
            0.0, 1.0, 0.0, 0.1
        )
    
    # Aplica filtros
    filtered_results = results
    if severity_filter != "Todos":
        filtered_results = [r for r in filtered_results if r.get('severity') == severity_filter]
    
    # CORRIGIDO: Acesso por chave de dicionário
    filtered_results = [r for r in filtered_results if r.get('confidence_score', 0) >= confidence_filter]
    
    # Exibe resultados
    for i, result in enumerate(filtered_results):
        error_message = str(result.get('error_message', 'Mensagem não disponível'))
        with st.expander(f"🔍 Erro {i+1}: {error_message[:80]}..."):
            
            # Informações básicas
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Severidade", result.get('severity', 'UNKNOWN'))
            with col2:
                confidence = result.get('confidence_score', 0)
                st.metric("Confiança", f"{confidence:.1%}")
            with col3:
                # CORRIGIDO: Campo similar_logs pode não existir
                similar_count = len(result.get('similar_logs', []))
                st.metric("Logs Similares", similar_count)
            
            # Explicação
            st.subheader("💡 Explicação")
            explanation = result.get('explanation', 'Explicação não disponível.')
            st.write(explanation)
            
            # Possíveis causas
            st.subheader("🔍 Possíveis Causas")
            possible_causes = result.get('possible_causes', [])
            if isinstance(possible_causes, list):
                for j, cause in enumerate(possible_causes, 1):
                    st.write(f"{j}. {cause}")
            else:
                st.write(f"1. {possible_causes}")
            
            # Recomendações
            st.subheader("🛠️ Recomendações")
            recommendations = result.get('recommendations', [])
            if isinstance(recommendations, list):
                for j, rec in enumerate(recommendations, 1):
                    st.write(f"{j}. {rec}")
            else:
                st.write(f"1. {recommendations}")
            
            # Logs similares (se existirem)
            similar_logs = result.get('similar_logs', [])
            if similar_logs:
                st.subheader("📚 Logs Similares")
                for j, similar in enumerate(similar_logs[:3], 1):
                    if isinstance(similar, dict):
                        similarity_score = similar.get('similarity_score', 0)
                        content = similar.get('content', 'Conteúdo não disponível')
                        st.text_area(
                            f"Similar {j} (Score: {similarity_score:.3f})",
                            content[:200] + "...",
                            height=100
                        )
                    else:
                        st.text_area(
                            f"Similar {j}",
                            str(similar)[:200] + "...",
                            height=100
                        )


def main():
    """Função principal da aplicação Streamlit."""
    initialize_session_state()
    display_header()
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configurações")
        
        # Upload de arquivo
        uploaded_file = st.file_uploader(
            "📁 Upload do Arquivo de Log",
            type=['log', 'txt'],
            help="Selecione um arquivo .log ou .txt para análise"
        )
        
        # Configurações de análise
        st.subheader("🔧 Opções de Análise")
        
        model_choice = st.selectbox(
            "Modelo LLM:",
            ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo-preview"]
        )
        
        errors_only = st.checkbox(
            "Apenas Erros",
            value=True,
            help="Analisa apenas entradas de erro/crítico"
        )
        
        send_alerts = st.checkbox(
            "Enviar Alertas",
            value=False,
            help="Envia alertas para Slack/Discord"
        )
        
        # Botão de análise
        analyze_button = st.button("🚀 Iniciar Análise", type="primary")
    
    # Área principal
    if uploaded_file is not None:
        # Lê conteúdo do arquivo
        try:
            stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
            log_content = stringio.read()
            st.session_state.log_content = log_content
            
            # Mostra preview do arquivo
            with st.expander("👀 Preview do Arquivo"):
                preview_content = log_content[:1000] + "..." if len(log_content) > 1000 else log_content
                st.text_area("Conteúdo:", preview_content, height=200)
        except Exception as e:
            st.error(f"❌ Erro ao ler arquivo: {e}")
    
    # Executa análise
    if analyze_button and uploaded_file is not None:
        if not st.session_state.log_content:
            st.error("❌ Nenhum conteúdo de log encontrado. Faça upload de um arquivo válido.")
            st.stop()
            
        with st.spinner("🔄 Analisando logs... Isso pode levar alguns minutos."):
            
            # Salva arquivo temporário
            temp_file = f"temp_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            
            try:
                with open(temp_file, 'w', encoding='utf-8') as f:
                    f.write(st.session_state.log_content)
                
                # Inicializa agente
                agent = setup_agent()
                if agent is None:
                    st.stop()
                
                # Processa arquivo
                results = agent.process_log_file(temp_file)
                st.session_state.analysis_results = results
                
                # Remove arquivo temporário
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                
                if results:
                    st.success(f"✅ Análise concluída! {len(results)} erros analisados.")
                    
                    # Envia para Discord se configurado
                    if send_alerts:
                        with st.spinner("📤 Enviando notificação para Discord..."):
                            success = send_discord_notification(
                                results=results,
                                analysis_summary=f"Análise automática de logs concluída. {len(results)} erros identificados no arquivo {uploaded_file.name}."
                            )
                            if success:
                                st.success("✅ Notificação enviada para Discord com sucesso!")
                            else:
                                st.error("❌ Falha ao enviar notificação para Discord.")
                else:
                    st.warning("⚠️ Análise concluída, mas nenhum erro foi encontrado no arquivo.")
                    
                    # Envia notificação mesmo sem erros se configurado
                    if send_alerts:
                        with st.spinner("📤 Enviando notificação para Discord..."):
                            # Cria um resultado fictício para indicar que não há erros
                            no_errors_result = [{
                                'severity': 'INFO',
                                'error_message': 'Nenhum erro encontrado no arquivo de log',
                                'confidence_score': 1.0,
                                'timestamp': datetime.now()
                            }]
                            success = send_discord_notification(
                                results=no_errors_result,
                                analysis_summary=f"Análise de logs concluída sem erros encontrados no arquivo {uploaded_file.name}. ✅"
                            )
                            if success:
                                st.success("✅ Notificação enviada para Discord com sucesso!")
                
            except Exception as e:
                st.error(f"❌ Erro durante análise: {e}")
                st.exception(e)  # Para debug
                if os.path.exists(temp_file):
                    os.remove(temp_file)
    
    # Exibe resultados
    if st.session_state.analysis_results:
        results = st.session_state.analysis_results
        
        # Métricas
        display_metrics(results)
        
        # Gráficos
        col1, col2 = st.columns(2)
        with col1:
            display_severity_chart(results)
        with col2:
            display_timeline_chart(results)
        
        # Resultados detalhados
        display_analysis_results(results)
        
        # Download de relatório
        st.subheader("📥 Download do Relatório")
        
        # Prepara dados para download
        report_data = []
        for result in results:
            # CORRIGIDO: Tratamento seguro de timestamp
            timestamp = result.get('timestamp')
            if isinstance(timestamp, str):
                timestamp_str = timestamp
            elif isinstance(timestamp, datetime):
                timestamp_str = timestamp.isoformat()
            else:
                timestamp_str = datetime.now().isoformat()
            
            # CORRIGIDO: Tratamento seguro de listas
            possible_causes = result.get('possible_causes', [])
            if isinstance(possible_causes, list):
                causes_str = '; '.join(str(cause) for cause in possible_causes)
            else:
                causes_str = str(possible_causes)
            
            recommendations = result.get('recommendations', [])
            if isinstance(recommendations, list):
                recommendations_str = '; '.join(str(rec) for rec in recommendations)
            else:
                recommendations_str = str(recommendations)
            
            report_data.append({
                'timestamp': timestamp_str,
                'error_message': str(result.get('error_message', '')),
                'explanation': str(result.get('explanation', '')),
                'severity': str(result.get('severity', 'UNKNOWN')),
                'confidence_score': float(result.get('confidence_score', 0)),
                'possible_causes': causes_str,
                'recommendations': recommendations_str
            })
        
        df_report = pd.DataFrame(report_data)
        
        col1, col2 = st.columns(2)
        with col1:
            csv = df_report.to_csv(index=False)
            st.download_button(
                label="📊 Download CSV",
                data=csv,
                file_name=f"log_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        with col2:
            json_data = json.dumps(report_data, indent=2, ensure_ascii=False, default=str)
            st.download_button(
                label="📋 Download JSON",
                data=json_data,
                file_name=f"log_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    # Informações sobre o agente
    with st.expander("ℹ️ Sobre o QA Log Agent"):
        st.markdown("""
        ### 🤖 Agente IA para Análise Inteligente de Logs de Erro
        
        Este agente utiliza tecnologias avançadas de IA para automatizar a análise de logs de erro:
        
        **🔧 Tecnologias Utilizadas:**
        - **LangChain/LangGraph**: Orquestração de fluxos inteligentes
        - **OpenAI GPT**: Interpretação e análise de erros
        - **ChromaDB**: Banco vetorial para busca semântica
        - **Embeddings**: Vetorização de logs para similaridade
        
        **📊 Funcionalidades:**
        - Análise automática de logs de erro
        - Busca de padrões similares no histórico
        - Explicações claras e acionáveis
        - Sugestões de causa e resolução
        - Integração com Slack/Discord
        - Relatórios detalhados
        
        **🎯 Benefícios para QA:**
        - Redução do tempo de investigação
        - Detecção de padrões de falha
        - Suporte a profissionais juniores
        - Rastreabilidade e acurácia
        """)


if __name__ == "__main__":
    main()