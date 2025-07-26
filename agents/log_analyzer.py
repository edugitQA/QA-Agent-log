"""
Agente IA para Análise Inteligente de Logs de Erro.

Este módulo implementa o agente principal que:
- Utiliza LangChain/LangGraph para orquestração
- Gera embeddings e armazena em banco vetorial
- Realiza busca semântica de logs similares
- Interpreta erros usando LLM
- Gera explicações e sugestões de causa
"""

import os
import json
import chromadb
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

# LangChain imports
from langchain.embeddings import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Imports locais
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.preprocessor import LogPreprocessor


@dataclass
class AnalysisResult:
    """Resultado da análise de um erro de log."""
    error_message: str
    explanation: str
    possible_causes: List[str]
    similar_logs: List[Dict]
    severity: str
    recommendations: List[str]
    timestamp: datetime
    confidence_score: float


class LogAnalyzerAgent:
    """
    Agente principal para análise inteligente de logs de erro.
    """
    
    def __init__(self, 
                 openai_api_key: str,
                 vectorstore_path: str = "./vectorstore",
                 model_name: str = "gpt-3.5-turbo"):
        """
        Inicializa o agente de análise de logs.
        
        Args:
            openai_api_key (str): Chave da API OpenAI
            vectorstore_path (str): Caminho para o banco vetorial
            model_name (str): Nome do modelo LLM a ser usado
        """
        self.openai_api_key = openai_api_key
        self.vectorstore_path = vectorstore_path
        self.model_name = model_name
        
        # Inicializa componentes
        self.embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        self.llm = ChatOpenAI(
            openai_api_key=openai_api_key,
            model_name=model_name,
            temperature=0.1
        )
        self.preprocessor = LogPreprocessor()
        
        # Inicializa banco vetorial
        self._initialize_vectorstore()
        
        print(f"✅ Agente inicializado com modelo {model_name}")
    
    def _initialize_vectorstore(self):
        """Inicializa o banco vetorial ChromaDB."""
        try:
            # Cria diretório se não existir
            os.makedirs(self.vectorstore_path, exist_ok=True)
            
            # Inicializa ChromaDB
            self.vectorstore = Chroma(
                persist_directory=self.vectorstore_path,
                embedding_function=self.embeddings
            )
            print(f"✅ Banco vetorial inicializado em {self.vectorstore_path}")
        except Exception as e:
            print(f"❌ Erro ao inicializar banco vetorial: {e}")
            raise
    
    def add_logs_to_vectorstore(self, chunks: List[Dict]) -> int:
        """
        Adiciona chunks de log ao banco vetorial.
        
        Args:
            chunks (List[Dict]): Lista de chunks processados
            
        Returns:
            int: Número de chunks adicionados
        """
        try:
            texts = []
            metadatas = []
            ids = []
            
            for chunk in chunks:
                # Prepara texto para vetorização
                text = chunk['text']
                
                # Prepara metadados
                metadata = {
                    'chunk_id': chunk['chunk_id'],
                    'error_count': chunk['error_count'],
                    'components': ','.join(chunk['components']),
                    'levels': ','.join(chunk['levels']),
                    'token_count': chunk['token_count'],
                    'timestamp': datetime.now().isoformat()
                }
                
                # ID único para o chunk
                chunk_id = f"chunk_{chunk['chunk_id']}_{datetime.now().timestamp()}"
                
                texts.append(text)
                metadatas.append(metadata)
                ids.append(chunk_id)
            
            # Adiciona ao banco vetorial
            self.vectorstore.add_texts(
                texts=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            # Persiste as mudanças
            self.vectorstore.persist()
            
            print(f"✅ {len(chunks)} chunks adicionados ao banco vetorial")
            return len(chunks)
            
        except Exception as e:
            print(f"❌ Erro ao adicionar chunks ao banco vetorial: {e}")
            return 0
    
    def search_similar_logs(self, query: str, k: int = 3) -> List[Dict]:
        """
        Busca logs similares no banco vetorial.
        
        Args:
            query (str): Texto de consulta (mensagem de erro)
            k (int): Número de resultados similares
            
        Returns:
            List[Dict]: Lista de logs similares com scores
        """
        try:
            # Realiza busca semântica
            results = self.vectorstore.similarity_search_with_score(query, k=k)
            
            similar_logs = []
            for doc, score in results:
                similar_log = {
                    'content': doc.page_content,
                    'metadata': doc.metadata,
                    'similarity_score': float(score),
                    'relevance': 'high' if score < 0.3 else 'medium' if score < 0.6 else 'low'
                }
                similar_logs.append(similar_log)
            
            print(f"✅ {len(similar_logs)} logs similares encontrados")
            return similar_logs
            
        except Exception as e:
            print(f"❌ Erro na busca de logs similares: {e}")
            return []
    
    def analyze_error_with_llm(self, error_message: str, similar_logs: List[Dict]) -> Dict:
        """
        Analisa erro usando LLM com contexto de logs similares.
        
        Args:
            error_message (str): Mensagem de erro a ser analisada
            similar_logs (List[Dict]): Logs similares para contexto
            
        Returns:
            Dict: Análise detalhada do erro
        """
        try:
            # Prepara contexto com logs similares
            context = ""
            if similar_logs:
                context = "\\n\\nLogs similares encontrados no histórico:\\n"
                for i, log in enumerate(similar_logs[:3], 1):
                    context += f"{i}. {log['content'][:200]}...\\n"
            
            # Prompt para análise
            system_prompt = """Você é um especialista em análise de logs de erro e QA. 
            Sua tarefa é analisar mensagens de erro e fornecer explicações claras e acionáveis.
            
            Para cada erro, forneça:
            1. Explicação clara do que aconteceu
            2. Possíveis causas (3-5 causas mais prováveis)
            3. Nível de severidade (LOW, MEDIUM, HIGH, CRITICAL)
            4. Recomendações específicas para resolução
            5. Score de confiança da análise (0.0 a 1.0)
            
            Seja técnico mas acessível. Foque em soluções práticas."""
            
            user_prompt = f"""Analise o seguinte erro de log:
            
            ERRO: {error_message}
            {context}
            
            Forneça sua análise em formato JSON com as seguintes chaves:
            - explanation: string
            - possible_causes: array de strings
            - severity: string (LOW/MEDIUM/HIGH/CRITICAL)
            - recommendations: array de strings
            - confidence_score: number (0.0-1.0)"""
            
            # Chama o LLM
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = self.llm(messages)
            
            # Tenta fazer parse do JSON
            try:
                analysis = json.loads(response.content)
            except json.JSONDecodeError:
                # Fallback se não conseguir fazer parse
                analysis = {
                    "explanation": response.content,
                    "possible_causes": ["Análise detalhada disponível no texto acima"],
                    "severity": "MEDIUM",
                    "recommendations": ["Revisar logs completos", "Verificar configurações do sistema"],
                    "confidence_score": 0.7
                }
            
            print(f"✅ Análise LLM concluída com confiança {analysis.get('confidence_score', 0.7)}")
            return analysis
            
        except Exception as e:
            print(f"❌ Erro na análise LLM: {e}")
            return {
                "explanation": f"Erro na análise: {str(e)}",
                "possible_causes": ["Erro interno do sistema de análise"],
                "severity": "MEDIUM",
                "recommendations": ["Verificar configuração do agente"],
                "confidence_score": 0.1
            }
    
    def analyze_log_entry(self, log_entry: Dict) -> AnalysisResult:
        """
        Analisa uma entrada de log específica.
        
        Args:
            log_entry (Dict): Entrada de log processada
            
        Returns:
            AnalysisResult: Resultado completo da análise
        """
        error_message = log_entry['message']
        
        # Busca logs similares
        similar_logs = self.search_similar_logs(error_message)
        
        # Analisa com LLM
        llm_analysis = self.analyze_error_with_llm(error_message, similar_logs)
        
        # Cria resultado
        result = AnalysisResult(
            error_message=error_message,
            explanation=llm_analysis.get('explanation', 'Análise não disponível'),
            possible_causes=llm_analysis.get('possible_causes', []),
            similar_logs=similar_logs,
            severity=llm_analysis.get('severity', 'MEDIUM'),
            recommendations=llm_analysis.get('recommendations', []),
            timestamp=datetime.now(),
            confidence_score=llm_analysis.get('confidence_score', 0.5)
        )
        
        return result
    
    def process_log_file(self, file_path: str) -> List[AnalysisResult]:
        """
        Processa um arquivo de log completo.
        
        Args:
            file_path (str): Caminho para o arquivo de log
            
        Returns:
            List[AnalysisResult]: Lista de análises para cada erro
        """
        print(f"🔄 Processando arquivo de log: {file_path}")
        
        # Processa arquivo com preprocessador
        chunks, patterns = self.preprocessor.process_log_file(file_path)
        
        # Adiciona chunks ao banco vetorial
        self.add_logs_to_vectorstore(chunks)
        
        # Analisa cada entrada de erro
        results = []
        for chunk in chunks:
            for entry in chunk['entries']:
                if entry['is_error']:
                    result = self.analyze_log_entry(entry)
                    results.append(result)
        
        print(f"✅ Análise concluída: {len(results)} erros analisados")
        return results
    
    def save_analysis_results(self, results: List[AnalysisResult], output_path: str):
        """
        Salva resultados da análise em arquivo JSON.
        
        Args:
            results (List[AnalysisResult]): Lista de resultados
            output_path (str): Caminho para salvar o arquivo
        """
        try:
            # Converte resultados para dicionário
            results_dict = []
            for result in results:
                result_dict = {
                    'error_message': result.error_message,
                    'explanation': result.explanation,
                    'possible_causes': result.possible_causes,
                    'severity': result.severity,
                    'recommendations': result.recommendations,
                    'confidence_score': result.confidence_score,
                    'timestamp': result.timestamp.isoformat(),
                    'similar_logs_count': len(result.similar_logs)
                }
                results_dict.append(result_dict)
            
            # Salva arquivo
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results_dict, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Resultados salvos em {output_path}")
            
        except Exception as e:
            print(f"❌ Erro ao salvar resultados: {e}")


def main():
    """
    Função principal para teste do agente.
    """
    # Configuração
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY não encontrada nas variáveis de ambiente")
        return
    
    # Inicializa agente
    agent = LogAnalyzerAgent(
        openai_api_key=api_key,
        vectorstore_path="../vectorstore"
    )
    
    # Testa com arquivo de exemplo
    log_file = "../data/example.log"
    if os.path.exists(log_file):
        results = agent.process_log_file(log_file)
        
        # Salva resultados
        output_file = "../output/analysis_results.json"
        agent.save_analysis_results(results, output_file)
        
        # Mostra resumo
        print(f"\\n📊 Resumo da análise:")
        print(f"- Total de erros analisados: {len(results)}")
        print(f"- Severidade crítica: {sum(1 for r in results if r.severity == 'CRITICAL')}")
        print(f"- Severidade alta: {sum(1 for r in results if r.severity == 'HIGH')}")
        print(f"- Confiança média: {sum(r.confidence_score for r in results) / len(results):.2f}")
    else:
        print(f"❌ Arquivo de exemplo não encontrado: {log_file}")


if __name__ == "__main__":
    main()

