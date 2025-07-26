#!/usr/bin/env python3
"""
Script de Teste do Ambiente QA Log Agent

Este script verifica se o ambiente está configurado corretamente
e testa as funcionalidades principais do agente.
"""

import os
import sys
import json
import traceback
from datetime import datetime
from typing import List, Dict, Tuple


class EnvironmentTester:
    """Classe para testar o ambiente do QA Log Agent."""

    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0
        self.test_results = []

    def print_header(self):
        """Imprime cabeçalho do teste."""
        print("=" * 60)
        print("🧪 TESTE DO AMBIENTE QA LOG AGENT")
        print("=" * 60)
        print(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

    def print_test(self, test_name: str, status: str, message: str = ""):
        """Imprime resultado de um teste."""
        status_icon = "✅" if status == "PASS" else "❌"
        print(f"{status_icon} {test_name}: {status}")
        if message:
            print(f"   {message}")
        print()

    def run_test(self, test_name: str, test_func) -> bool:
        """Executa um teste e registra o resultado."""
        try:
            result = test_func()
            if result:
                self.tests_passed += 1
                self.print_test(test_name, "PASS")
                self.test_results.append({"test": test_name, "status": "PASS", "error": None})
                return True
            else:
                self.tests_failed += 1
                self.print_test(test_name, "FAIL", "Teste retornou False")
                self.test_results.append({"test": test_name, "status": "FAIL", "error": "Test returned False"})
                return False
        except Exception as e:
            self.tests_failed += 1
            error_msg = f"{type(e).__name__}: {str(e)}"
            self.print_test(test_name, "FAIL", error_msg)
            self.test_results.append({"test": test_name, "status": "FAIL", "error": error_msg})
            return False

    def test_python_version(self) -> bool:
        """Testa se a versão do Python é compatível."""
        version = sys.version_info
        if version.major == 3 and version.minor >= 8:
            print(f"   Python {version.major}.{version.minor}.{version.micro}")
            return True
        return False

    def test_required_packages(self) -> bool:
        """Testa se todos os pacotes necessários estão instalados."""
        required_packages = [
            'langchain',
            'openai', 
            'chromadb',
            'streamlit',
            'pandas',
            'plotly',
            'python_dotenv',
            'tiktoken'
        ]

        missing_packages = []

        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                # Tenta nomes alternativos
                if package == 'python_dotenv':
                    try:
                        __import__('dotenv')
                    except ImportError:
                        missing_packages.append(package)
                else:
                    missing_packages.append(package)

        if missing_packages:
            print(f"   Pacotes faltando: {', '.join(missing_packages)}")
            return False

        print(f"   Todos os {len(required_packages)} pacotes necessários estão instalados")
        return True

    def test_environment_variables(self) -> bool:
        """Testa se as variáveis de ambiente estão configuradas."""
        from dotenv import load_dotenv
        load_dotenv()

        required_vars = ['OPENAI_API_KEY']
        optional_vars = ['SLACK_TOKEN', 'DISCORD_WEBHOOK_URL']

        missing_required = []
        missing_optional = []

        for var in required_vars:
            if not os.getenv(var):
                missing_required.append(var)

        for var in optional_vars:
            if not os.getenv(var):
                missing_optional.append(var)

        if missing_required:
            print(f"   Variáveis obrigatórias faltando: {', '.join(missing_required)}")
            return False

        print(f"   Variáveis obrigatórias configuradas: {', '.join(required_vars)}")
        if missing_optional:
            print(f"   Variáveis opcionais faltando: {', '.join(missing_optional)}")

        return True

    def test_file_structure(self) -> bool:
        """Testa se a estrutura de arquivos está correta."""
        required_files = [
            'main.py',
            'streamlit_app.py',
            'requirements.txt',
            '.env.example',
            'agents/log_analyzer.py',
            'utils/preprocessor.py',
            'data/example.log'
        ]

        required_dirs = [
            'agents',
            'utils', 
            'data',
            'vectorstore',
            'output'
        ]

        missing_files = []
        missing_dirs = []

        for file_path in required_files:
            if not os.path.exists(file_path):
                missing_files.append(file_path)

        for dir_path in required_dirs:
            if not os.path.exists(dir_path):
                missing_dirs.append(dir_path)

        if missing_files or missing_dirs:
            if missing_files:
                print(f"   Arquivos faltando: {', '.join(missing_files)}")
            if missing_dirs:
                print(f"   Diretórios faltando: {', '.join(missing_dirs)}")
            return False

        print(f"   Estrutura de arquivos completa")
        return True

    def test_preprocessor_import(self) -> bool:
        """Testa se o preprocessador pode ser importado."""
        sys.path.append('.')
        from utils.preprocessor import LogPreprocessor

        preprocessor = LogPreprocessor()
        print(f"   LogPreprocessor importado com sucesso")
        return True

    def test_log_analyzer_import(self) -> bool:
        """Testa se o analisador pode ser importado."""
        sys.path.append('.')
        from agents.log_analyzer import LogAnalyzerAgent

        print(f"   LogAnalyzerAgent importado com sucesso")
        return True

    def test_example_log_processing(self) -> bool:
        """Testa processamento do log de exemplo."""
        sys.path.append('.')
        from utils.preprocessor import LogPreprocessor

        if not os.path.exists('data/example.log'):
            print("   Arquivo example.log não encontrado")
            return False

        preprocessor = LogPreprocessor()
        chunks, patterns = preprocessor.process_log_file('data/example.log')

        if len(chunks) == 0:
            print("   Nenhum chunk foi processado")
            return False

        if patterns['total_errors'] == 0:
            print("   Nenhum erro foi detectado no log de exemplo")
            return False

        print(f"   Processados {len(chunks)} chunks, {patterns['total_errors']} erros detectados")
        return True

    def test_openai_connection(self) -> bool:
        """Testa conexão com OpenAI (se API key estiver configurada)."""
        from dotenv import load_dotenv
        load_dotenv()

        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("   OPENAI_API_KEY não configurada - pulando teste")
            return True

        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=api_key)
            # Inicializando o cliente sem o argumento 'proxies'

            # Teste simples de conexão
            response = client.chat.completions.create(model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5)

            print(f"   Conexão com OpenAI estabelecida com sucesso")
            return True

        except Exception as e:
            print(f"   Erro na conexão com OpenAI: {str(e)}")
            return False

    def test_chromadb_initialization(self) -> bool:
        """Testa inicialização do ChromaDB."""
        try:
            import chromadb
            from langchain.embeddings import OpenAIEmbeddings
            from langchain.vectorstores import Chroma
            from dotenv import load_dotenv

            load_dotenv()
            api_key = os.getenv('OPENAI_API_KEY')

            if not api_key:
                print("   OPENAI_API_KEY necessária para teste do ChromaDB")
                return False

            # Testa inicialização básica
            embeddings = OpenAIEmbeddings(openai_api_key=api_key)
            vectorstore = Chroma(
                persist_directory="./test_vectorstore",
                embedding_function=embeddings
            )

            # Limpa teste
            import shutil
            if os.path.exists("./test_vectorstore"):
                shutil.rmtree("./test_vectorstore")

            print(f"   ChromaDB inicializado com sucesso")
            return True

        except Exception as e:
            print(f"   Erro na inicialização do ChromaDB: {str(e)}")
            return False

    def test_streamlit_import(self) -> bool:
        """Testa se o Streamlit pode ser importado."""
        import streamlit as st
        print(f"   Streamlit importado com sucesso")
        return True

    def run_all_tests(self):
        """Executa todos os testes."""
        self.print_header()

        # Lista de testes
        tests = [
            ("Versão do Python", self.test_python_version),
            ("Pacotes Necessários", self.test_required_packages),
            ("Variáveis de Ambiente", self.test_environment_variables),
            ("Estrutura de Arquivos", self.test_file_structure),
            ("Import do Preprocessor", self.test_preprocessor_import),
            ("Import do Log Analyzer", self.test_log_analyzer_import),
            ("Processamento do Log de Exemplo", self.test_example_log_processing),
            ("Conexão OpenAI", self.test_openai_connection),
            ("Inicialização ChromaDB", self.test_chromadb_initialization),
            ("Import do Streamlit", self.test_streamlit_import)
        ]

        # Executa testes
        for test_name, test_func in tests:
            self.run_test(test_name, test_func)

        # Resumo final
        self.print_summary()

    def print_summary(self):
        """Imprime resumo dos testes."""
        total_tests = self.tests_passed + self.tests_failed
        success_rate = (self.tests_passed / total_tests) * 100 if total_tests > 0 else 0

        print("=" * 60)
        print("📊 RESUMO DOS TESTES")
        print("=" * 60)
        print(f"Total de testes: {total_tests}")
        print(f"Testes aprovados: {self.tests_passed}")
        print(f"Testes falharam: {self.tests_failed}")
        print(f"Taxa de sucesso: {success_rate:.1f}%")
        print()

        if self.tests_failed == 0:
            print("🎉 Todos os testes passaram! O ambiente está pronto para uso.")
        else:
            print("⚠️  Alguns testes falharam. Verifique as configurações acima.")
            print("💡 Consulte o README.md para instruções de configuração.")

        print()

        # Salva resultados
        self.save_test_results()

    def save_test_results(self):
        """Salva resultados dos testes em arquivo JSON."""
        try:
            os.makedirs('output', exist_ok=True)

            results = {
                'timestamp': datetime.now().isoformat(),
                'total_tests': self.tests_passed + self.tests_failed,
                'tests_passed': self.tests_passed,
                'tests_failed': self.tests_failed,
                'success_rate': (self.tests_passed / (self.tests_passed + self.tests_failed)) * 100,
                'test_details': self.test_results
            }

            with open('output/test_results.json', 'w') as f:
                json.dump(results, f, indent=2)

            print(f"📄 Resultados salvos em: output/test_results.json")

        except Exception as e:
            print(f"⚠️  Erro ao salvar resultados: {e}")


def main():
    """Função principal."""
    tester = EnvironmentTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()

