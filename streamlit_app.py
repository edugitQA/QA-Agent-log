"""
Interface Streamlit para o Agente IA de Análise de Logs de Erro.

Esta aplicação web permite:
- Upload de arquivos de log
- Visualização da análise em tempo real
- Exploração de logs similares
- Download de relatórios
"""

import streamlit as st
import os
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from io import StringIO

# Imports locais
from agents.log_analyzer import LogAnalyzerAgent
from utils.preprocessor import LogPreprocessor


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
        background: #f8fafc;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #3b82f6;
        margin: 0.5rem 0;
    }
    
    .error-card {
        background: #fef2f2;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ef4444;
        margin: 0.5rem 0;
    }
    
    .success-card {
        background: #f0fdf4;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #22c55e;
        margin: 0.5rem 0;
    }
    
    .sidebar .sidebar-content {
        background: #1e293b;
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
            model_name="gpt-3.5-turbo"
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
        critical_count = sum(1 for r in results if r.severity == 'CRITICAL')
        st.markdown("""
        <div class="error-card">
            <h3>🔴 Críticos</h3>
            <h2>{}</h2>
        </div>
        """.format(critical_count), unsafe_allow_html=True)
    
    with col3:
        high_count = sum(1 for r in results if r.severity == 'HIGH')
        st.markdown("""
        <div class="error-card">
            <h3>🟠 Alta Prioridade</h3>
            <h2>{}</h2>
        </div>
        """.format(high_count), unsafe_allow_html=True)
    
    with col4:
        avg_confidence = sum(r.confidence_score for r in results) / len(results)
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
    
    severity_counts = {}
    for result in results:
        severity_counts[result.severity] = severity_counts.get(result.severity, 0) + 1
    
    df = pd.DataFrame(list(severity_counts.items()), columns=['Severidade', 'Quantidade'])
    
    # Cores personalizadas
    color_map = {
        'CRITICAL': '#ef4444',
        'HIGH': '#f97316', 
        'MEDIUM': '#eab308',
        'LOW': '#22c55e'
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
        timeline_data.append({
            'timestamp': result.timestamp,
            'severity': result.severity,
            'message': result.error_message[:50] + "..."
        })
    
    df = pd.DataFrame(timeline_data)
    
    fig = px.scatter(df, x='timestamp', y='severity', 
                     hover_data=['message'],
                     title="Timeline de Erros",
                     color='severity',
                     color_discrete_map={
                         'CRITICAL': '#ef4444',
                         'HIGH': '#f97316',
                         'MEDIUM': '#eab308', 
                         'LOW': '#22c55e'
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
        severity_filter = st.selectbox(
            "Filtrar por Severidade:",
            ["Todos"] + list(set(r.severity for r in results))
        )
    
    with col2:
        confidence_filter = st.slider(
            "Confiança Mínima:",
            0.0, 1.0, 0.0, 0.1
        )
    
    # Aplica filtros
    filtered_results = results
    if severity_filter != "Todos":
        filtered_results = [r for r in filtered_results if r.severity == severity_filter]
    
    filtered_results = [r for r in filtered_results if r.confidence_score >= confidence_filter]
    
    # Exibe resultados
    for i, result in enumerate(filtered_results):
        with st.expander(f"🔍 Erro {i+1}: {result.error_message[:80]}..."):
            
            # Informações básicas
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Severidade", result.severity)
            with col2:
                st.metric("Confiança", f"{result.confidence_score:.1%}")
            with col3:
                st.metric("Logs Similares", len(result.similar_logs))
            
            # Explicação
            st.subheader("💡 Explicação")
            st.write(result.explanation)
            
            # Possíveis causas
            st.subheader("🔍 Possíveis Causas")
            for j, cause in enumerate(result.possible_causes, 1):
                st.write(f"{j}. {cause}")
            
            # Recomendações
            st.subheader("🛠️ Recomendações")
            for j, rec in enumerate(result.recommendations, 1):
                st.write(f"{j}. {rec}")
            
            # Logs similares
            if result.similar_logs:
                st.subheader("📚 Logs Similares")
                for j, similar in enumerate(result.similar_logs[:3], 1):
                    st.text_area(
                        f"Similar {j} (Score: {similar['similarity_score']:.3f})",
                        similar['content'][:200] + "...",
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
            ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo-preview"]
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
        stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
        log_content = stringio.read()
        st.session_state.log_content = log_content
        
        # Mostra preview do arquivo
        with st.expander("👀 Preview do Arquivo"):
            st.text_area("Conteúdo:", log_content[:1000] + "..." if len(log_content) > 1000 else log_content, height=200)
    
    # Executa análise
    if analyze_button and uploaded_file is not None:
        with st.spinner("🔄 Analisando logs... Isso pode levar alguns minutos."):
            
            # Salva arquivo temporário
            temp_file = f"temp_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(st.session_state.log_content)
            
            try:
                # Inicializa agente
                agent = setup_agent()
                if agent is None:
                    st.stop()
                
                # Processa arquivo
                results = agent.process_log_file(temp_file)
                st.session_state.analysis_results = results
                
                # Remove arquivo temporário
                os.remove(temp_file)
                
                st.success(f"✅ Análise concluída! {len(results)} erros analisados.")
                
            except Exception as e:
                st.error(f"❌ Erro durante análise: {e}")
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
            report_data.append({
                'timestamp': result.timestamp.isoformat(),
                'error_message': result.error_message,
                'explanation': result.explanation,
                'severity': result.severity,
                'confidence_score': result.confidence_score,
                'possible_causes': '; '.join(result.possible_causes),
                'recommendations': '; '.join(result.recommendations)
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

