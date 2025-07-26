"""
Agente IA para Análise Inteligente de Logs de Erro - 

Este módulo implementa o agente principal que:
- Utiliza LangChain/LangGraph para orquestração
- Gera embeddings e armazena em banco vetorial
- Realiza busca semântica de logs similares
- Interpreta erros usando LLM
- Gera explicações e sugestões de causa
"""


import os
import json
from datetime import datetime
from typing import List, Dict

# LangChain/LCEL Imports
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.chat_models import ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser

# Imports locais
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.preprocessor import LogPreprocessor


class LogAnalyzerAgent:
    """
    Agente de análise de logs com sanitização manual de dados para máxima robustez.
    """
    def __init__(self,
                 openai_api_key: str,
                 vectorstore_path: str = "./vectorstore",
                 model_name: str = "gpt-3.5-turbo"):
        
        self.openai_api_key = openai_api_key
        self.vectorstore_path = vectorstore_path
        self.model_name = model_name
        self.preprocessor = LogPreprocessor()
        
        self.embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        self.llm = ChatOpenAI(
            openai_api_key=openai_api_key,
            model_name=model_name,
            temperature=0.1,
            model_kwargs={"response_format": {"type": "json_object"}}
        )
        
        self.vectorstore = self._initialize_vectorstore()
        self.analysis_chain = self._create_analysis_chain()
        
        print(f"✅ Agente inicializado com modelo {model_name} e arquitetura de sanitização manual.")

    def _initialize_vectorstore(self) -> Chroma:
        try:
            os.makedirs(self.vectorstore_path, exist_ok=True)
            db = Chroma(
                persist_directory=self.vectorstore_path,
                embedding_function=self.embeddings
            )
            print(f"✅ Banco vetorial inicializado em {self.vectorstore_path}")
            return db
        except Exception as e:
            print(f"❌ Erro ao inicializar banco vetorial: {e}")
            raise

    def _format_docs(self, docs: List[Document]) -> str:
        if not docs:
            return "Nenhum log similar encontrado no histórico."
        return "\n\n".join(f"Log similar: {doc.page_content}" for doc in docs)

    def _create_analysis_chain(self):
        """
        Cria a cadeia de análise para retornar uma string JSON bruta.
        """
        retriever = self.vectorstore.as_retriever(search_kwargs={"k": 3})
        
        template = """Você é um especialista em análise de logs e SRE.
        Sua tarefa é analisar uma mensagem de erro, usando o contexto de logs similares, e retornar uma análise estruturada em JSON.

        CONTEXTO (Logs similares do histórico):
        {context}

        MENSAGEM DE ERRO ATUAL PARA ANÁLISE:
        {input}

        Retorne sua análise em um formato JSON contendo as chaves: "explanation", "possible_causes", "severity", "recommendations", "confidence_score".
        O valor de "possible_causes" e "recommendations" DEVE ser uma lista de strings.
        O valor de "severity" deve ser uma das seguintes opções: "LOW", "MEDIUM", "HIGH", "CRITICAL".
        O valor de "confidence_score" deve ser um número entre 0 e 1.
        """
        
        prompt = ChatPromptTemplate.from_template(template)

        chain = (
            {"context": retriever | self._format_docs, "input": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )
        return chain

    def _sanitize_llm_output(self, json_string: str) -> Dict:
        """
        Recebe a string JSON bruta do LLM e a transforma em um dicionário Python limpo e seguro.
        """
        try:
            # Remove possíveis caracteres de formatação markdown
            json_string = json_string.strip()
            if json_string.startswith('```json'):
                json_string = json_string[7:]
            if json_string.endswith('```'):
                json_string = json_string[:-3]
            json_string = json_string.strip()
            
            data = json.loads(json_string)
            
            # Sanitização robusta dos campos
            if 'possible_causes' not in data or not isinstance(data.get('possible_causes'), list):
                causes = data.get('possible_causes', 'Nenhuma causa provável encontrada.')
                if isinstance(causes, str):
                    data['possible_causes'] = [causes]
                else:
                    data['possible_causes'] = [str(causes)]

            if 'recommendations' not in data or not isinstance(data.get('recommendations'), list):
                recommendations = data.get('recommendations', 'Nenhuma recomendação disponível.')
                if isinstance(recommendations, str):
                    data['recommendations'] = [recommendations]
                else:
                    data['recommendations'] = [str(recommendations)]

            # Garantir que explanation é uma string
            data['explanation'] = str(data.get('explanation', 'Explicação não fornecida pelo modelo.'))
            
            # Garantir que severity é válido
            valid_severities = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
            severity = str(data.get('severity', 'MEDIUM')).upper()
            if severity not in valid_severities:
                severity = 'MEDIUM'
            data['severity'] = severity
            
            # Garantir que confidence_score é um número válido
            try:
                confidence = float(data.get('confidence_score', 0.5))
                if confidence < 0:
                    confidence = 0.0
                elif confidence > 1:
                    confidence = 1.0
                data['confidence_score'] = confidence
            except (ValueError, TypeError):
                data['confidence_score'] = 0.5
            
            print(f"✅ JSON sanitizado com sucesso. Severity: {data['severity']}, Confidence: {data['confidence_score']}")
            return data

        except json.JSONDecodeError as e:
            print(f"❌ Falha ao decodificar o JSON da resposta do LLM. Erro: {e}")
            print(f"Resposta bruta: {json_string}")
            return {
                "explanation": "O modelo de IA retornou uma resposta em formato JSON inválido.",
                "possible_causes": ["Erro de formatação do LLM", "Resposta malformada"],
                "severity": "MEDIUM",
                "recommendations": ["Tente novamente a análise", "Verifique a conectividade com a API"],
                "confidence_score": 0.1,
                "raw_response": json_string[:500]  # Limitar tamanho para debug
            }
        except Exception as e:
            print(f"❌ Erro inesperado ao sanitizar a saída: {e}")
            return {
                "explanation": f"Erro interno durante sanitização: {str(e)}",
                "possible_causes": ["Erro interno do sistema"],
                "severity": "MEDIUM", 
                "recommendations": ["Contacte o administrador do sistema"],
                "confidence_score": 0.0
            }

    def analyze_log_entry(self, log_entry_message: str) -> Dict:
        """
        Analisa uma entrada de log e retorna um dicionário com a análise.
        """
        try:
            print(f"🔄 Analisando erro: \"{log_entry_message[:80]}...\"")
            
            # Validação de entrada
            if not log_entry_message or not isinstance(log_entry_message, str):
                raise ValueError("Mensagem de log inválida ou vazia")
            
            # Executa a cadeia de análise
            raw_json_output = self.analysis_chain.invoke(log_entry_message)
            
            # Sanitiza a saída
            clean_analysis = self._sanitize_llm_output(raw_json_output)

            print(f"✅ Análise concluída com confiança {clean_analysis.get('confidence_score', 'N/A')}")
            return clean_analysis
            
        except Exception as e:
            print(f"❌ Erro crítico na execução da cadeia de análise: {e}")
            return {
                "explanation": f"Falha crítica ao analisar o log: {str(e)}",
                "possible_causes": [f"Erro de sistema: {type(e).__name__}"], 
                "recommendations": ["Verifique a configuração do sistema", "Tente novamente"], 
                "severity": "HIGH", 
                "confidence_score": 0.0,
                "error_details": str(e)
            }

    def add_logs_to_vectorstore(self, chunks: List[Dict]) -> int:
        """
        Adiciona chunks de log ao banco vetorial.
        """
        if not chunks:
            return 0
        
        texts = [chunk['text'] for chunk in chunks]
        metadatas = [
            {
                'chunk_id': chunk['chunk_id'],
                'error_count': chunk['error_count'],
                'components': ','.join(chunk['components']),
                'levels': ','.join(chunk['levels']),
                'token_count': chunk['token_count'],
                'timestamp': datetime.now().isoformat()
            } for chunk in chunks
        ]
        ids = [f"chunk_{chunk['chunk_id']}_{datetime.now().timestamp()}" for chunk in chunks]
        
        try:
            self.vectorstore.add_texts(texts=texts, metadatas=metadatas, ids=ids)
            self.vectorstore.persist()
            print(f"✅ {len(chunks)} chunks adicionados ao banco vetorial")
            return len(chunks)
        except Exception as e:
            print(f"❌ Erro ao adicionar chunks ao banco vetorial: {e}")
            return 0

    def process_log_file(self, file_path: str) -> List[Dict]:
        """
        Processa um arquivo de log completo.
        """
        print(f"🔄 Processando arquivo de log: {file_path}")
        
        try:
            chunks, _ = self.preprocessor.process_log_file(file_path)
            self.add_logs_to_vectorstore(chunks)
            
            results = []
            error_entries = [entry for chunk in chunks for entry in chunk['entries'] if entry['is_error']]
            
            for entry in error_entries:
                analysis = self.analyze_log_entry(entry['message'])
                analysis['error_message'] = entry['message']
                analysis['timestamp'] = datetime.now().isoformat()
                results.append(analysis)
            
            print(f"✅ Análise de arquivo concluída: {len(results)} erros analisados")
            return results
            
        except Exception as e:
            print(f"❌ Erro ao processar arquivo de log: {e}")
            return []

    def save_analysis_results(self, results: List[Dict], output_path: str):
        """
        Salva os resultados da análise em arquivo JSON.
        """
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"✅ Resultados salvos em {output_path}")
        except Exception as e:
            print(f"❌ Erro ao salvar resultados: {e}")


def main():
    """
    Função principal para teste do agente.
    """
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY não encontrada. Certifique-se de que está no seu arquivo .env")
        return
    
    agent = LogAnalyzerAgent(openai_api_key=api_key, vectorstore_path="./vectorstore")
    
    log_file = "./data/example.log"
    if os.path.exists(log_file):
        results = agent.process_log_file(log_file)
        if results:
            agent.save_analysis_results(results, "./output/analysis_results.json")
            print("\n📊 Análise concluída com sucesso.")
            
            # Debug: mostrar estrutura dos resultados
            print("\n🔍 Estrutura dos resultados:")
            for i, result in enumerate(results[:2]):  # Mostrar apenas os 2 primeiros
                print(f"Resultado {i+1}:")
                for key, value in result.items():
                    print(f"  {key}: {type(value).__name__} = {str(value)[:100]}...")
    else:
        print(f"❌ Arquivo de log de exemplo não encontrado em: {log_file}")


if __name__ == "__main__":
    main()